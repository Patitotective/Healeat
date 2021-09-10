"""
Healeat
---
Made for Timathon's code jam

Description: Healeat is a simple way to measure your calories, watch some charts about your diet and get advices.
Team (solo): Heatlhy tim
GitHub page: https://github.com/Patitotective/Healeat

To see the nutritional sources see Prefs/nutrition.prefs

Made by Patitotective
Contact me:
	Discord: patitotective#0217
	Email: cristobalriaga@gmail.com
"""

# Libraries
import sys
import os

from PyQt5.QtWidgets import (
	QMainWindow, QWidget, 
	QSlider, QLabel, 
	QSplitter, QSpinBox, 
	QPushButton, QMessageBox, 
	QTabWidget, QGridLayout, 
	QHBoxLayout, QVBoxLayout, 
	QTabBar, QApplication, 
	QButtonGroup, QRadioButton, 
	QFormLayout, QAction, 
	QStylePainter, QStyleOptionTab, 
	QStyle, QDialog, 
	QLineEdit, QScrollArea, 
	QComboBox, QToolTip, 
	QShortcut, QDoubleSpinBox, 
	QInputDialog, QLayout)

from PyQt5.QtGui import QPixmap, QIcon, QFontDatabase, QKeySequence, QCursor, QPainter, QPalette, QColor, QFont, QFontMetricsF
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRect, QTimer

from PyQt5.QtChart import (
	QBarSet, QBarCategoryAxis, 
	QPieSeries, QStackedBarSeries, 
	QHorizontalStackedBarSeries, QChart, 
	QChartView, QLineSeries, QValueAxis)

import PREFS # https://patitotective.github.io/PREFS/
import datetime
import casestyle
from collections import defaultdict
from enum import Enum, auto

# Dependencies
import resources # .qrc file (Qt Resources)

from extra import (
	remove_key_from_dict, rename_key_from_dict, 
	snake_case_to_sentence_case, 
	dict_max, create_horizontal_line, 
	remove_elements_from_list, get_widgets_from_layout, 
	get_widget_from_layout, choose_random_from_list, 
	create_qaction, split_expression, 
	StatementTypes, OPERATORS, 
	GOODLOOKING_OPERATORS, GOODLOOKING_OPERATOR_TO_OPERATOR, 
	OPERATOR_TO_GOODLOOKING_OPERATOR, map_widgets_from_layout, 
	expression_to_goodlooking_expression, check_syntax)

from scrollarea import ScrollArea
from vertical_tab_widget import VerticalTabWidget
from about_dialog import create_about_dialog
from input_dialog import get_item_input_dialog, get_double_input_dialog, question_dialog
from instructions_dialog import create_instructions_dialog

class AdvicesTypes(Enum):

	LOW = auto()
	EXTRA = auto()
	PERFECT = auto()

class MainWindow(QMainWindow):
	def __init__(self, title: str, parent=None, verbose: bool=False) -> None:
		super().__init__(parent)
		
		self.verbose = verbose
		self.title = title
				
		self.init_window()
		self.create_menu_bar()

	def init_window(self):
		if self.verbose: print(f"Create window ({self})")
		
		# Window settings
		self.setWindowTitle(self.title)
		self.setWindowIcon(QIcon(':/Images/icon.png')) # set the icon		

		# Creating MainWidget instance and setting it as central widget
		self.main_widget = MainWidget(parent=self, verbose=self.verbose)
		self.setCentralWidget(self.main_widget)
		
		# Setting the pos and size of the window to the saved ones
		main_window_size = self.main_widget.prefs.file["state"]["main_window"]["size"]
		main_window_pos = self.main_widget.prefs.file["state"]["main_window"]["pos"]

		self.resize(main_window_size[0], main_window_size[1])
		self.move(main_window_pos[0], main_window_pos[1])

	def create_menu_bar(self):
		"""Create menu bar."""
		bar = self.menuBar() # Get the menu bar of the mainwindow
		
		## File menu ##
		file_menu = bar.addMenu('&File')

		# Create an instructions action that will open the instructions dialog
		instructions_action = create_qaction( 
			menu=file_menu, 
			text="&Instructions", 
			shortcut="Ctrl+I", 
			callback=lambda: create_instructions_dialog(parent=self, foods=self.main_widget.FOODS, meals=self.main_widget.MEALS), 
			parent=self)

		# Create a close action that will call self.close_app
		close_action = create_qaction(
			menu=file_menu, 
			text="Close", 
			shortcut="Ctrl+Q", 
			callback=self.close_app, 
			parent=self)

		## Edit menu ##
		edit_menu = bar.addMenu('&Edit') # Add a menu called edit

		# Create a settings action that will open the settings dialog
		settings_action = create_qaction( 
			menu=edit_menu, 
			text="&Settings", 
			shortcut="Ctrl+S", 
			callback=self.main_widget.settings_dialog, 
			parent=self)

		## About menu ##
		about_menu = bar.addMenu('&About') # Add a menu called about

		# Create an about action that will create an instance of AboutDialog
		about_me_action = create_qaction(
			menu=about_menu, 
			text="About &Healeat", 
			shortcut="Ctrl+H", 
			callback=lambda: create_about_dialog(
				"About Healeat", 
				body=f"""**Healeat** is nutrition tracker GUI application made using Python\\
				for the Timathon code Jam with _health_ as theme.\\
				\\
				Libraries used:\\
				- [_PyQt 5.15.4_](https://pypi.org/project/PyQt5/)\\
				- [_PyQtChart 5.15.4_](https://pypi.org/project/PyQtChart/)\\
				- [PREFS 0.2](https://patitotective.github.io/PREFS/)\\
				- [_casestyle 0.0.4_](https://github.com/zhoujin7/casestyle)
				""", 
				icon=self.windowIcon(), 
				contact={"Discord": "&nbsp;**patitotective**_#0127_", "Email": "[cristobalriaga@gmail.com](mailto:cristobalriaga@gmail.com)"}, 
				source_code="[Source code](https://github.com/Patitotective/Healeat)", 
				parent=self, 
			), 
			parent=self)

		about_qt_action = create_qaction(
			menu=about_menu, 
			text="About Q&t", 
			shortcut="Ctrl+t", 
			callback=lambda: QMessageBox.aboutQt(self), 
			parent=self)

	def close_app(self):
		# Get the geometry (pos, size) of the window and store it in the prefs file.
		main_window_geometry = self.geometry()

		main_window_pos = main_window_geometry.x(), main_window_geometry.y() - 64
		main_window_size = main_window_geometry.width(), main_window_geometry.height()

		self.main_widget.prefs.write_prefs("state/main_window/size", main_window_size)
		self.main_widget.prefs.write_prefs("state/main_window/pos", main_window_pos)

		# Close window and exit program to close all dialogs open.
		self.close()
		sys.exit()

	def closeEvent(self, event) -> None:
		"""This will be called when the windows is closed."""
		self.close_app()
		event.accept()

class MainWidget(QWidget):
	def __init__(self, parent=None, verbose=False):
		super(MainWidget, self).__init__()

		self.parent = parent
		self.verbose = verbose

		self.default_nutriton = {
			'ideal_portions': {
				'vegetables': '1.5 * weight * 3', 
				'grains': '0.7 * weight * 3', 
				'fruits': '1.5 * weight * 3', 
				'protein': '1.8 * weight * 3', 
				'dairy': '1.7 * weight * 3', 
				'oils_and_fats': '2 * weight * 3', 
				'other': '1.8 * weight * 3'
			}, 
			'ideal_meal_portions': {
				'breakfast': 'BMR / 4', 
				'lunch': 'BMR / 4', 
				'dinner': 'BMR / 4', 
				'others': 'BMR / 5'
			}
		}

		self.MEALS = ["Breakfast", "Lunch", "Dinner", "Others"]
		self.MEALS_COLORS = ["#e78f3d", "#33cea9", "#2279cd", "#d73b4f"]

		self.FOODS = ["Vegetables", "Grains", "Fruits", "Protein", "Dairy", "Oils and fats", "Other"]
		self.FOODS_COLORS = ["#99ca53", "#209fdf", "#6d5fd5", "#f6a625", "#e4e984", "#b5521a", "#e13131"]
		
		self.IDEAL_LINE_COLOR = "#43D052"

		self.widgets = {
			"init_widget": [], 
			"calories_label": [], 
			"current_user_label": [], 
			"tabs": [], 
			"meal_tabs": [], 
			"charts": {
				"bar": [], 
				"pie": [], 
			}, 
			"charts_series": {
				"bar": [], 
				"pie": [], 
			}, 
			"stats_splitter": [], 
			"advices_tab": [], 
			"calories_per_day_tab": [], 
		}

		self.HEALTH_ADVICES = (
			"Limit sugary drinks, such as: sodas, fruit juices, sweetened teas, etc. Some alternatives are water, coffee, unsweetened teas, etc.", 
			"Eat more nuts and seeds, even if you have heard they are high in fats they are really nutritious.", 
			"Avoid eating ultra-processed foods, such as: fast food, frozen meals, chips, etc.", 
			"The fish is great source of calories and healthy fats, e.g.: the salmon.", 
			"For almost everything you need to have a good quality sleep, it lets your brain rest and in general your whole body.", 
			"Stay hydrated. Hydration helps ensure that your body is functioning optimally.", 
			"Bright lights before sleep impoverishes your sleep quality.", 
			"Go exercise. Physical activity is the best thing you can do to for mental and physical health, it makes your life better.", 
			"Smoking, drinking (in excess) and drug's use kills your brain's neurons between others.", 
			"Minimize your sugar intake in general, sugar is linked to obesity, type 2 diabetes and heart disease.", 
			"Ocasionally is good to use a nutrition tracker, like this, to get an idea of your diet.")

		self.HEALTH_ADVICES_TO_DISPLAY = 3 # The number of health advices to display

		# This advices will be formated with it's corresponding ADVICE_VALUE in self.USER_ADVICES_VALUES
		self.USER_ADVICES = ("You need to eat <span style='color: #A21B97;'>more</span> {}.", 
			"Slow down. You are eating <span style='color: #BB2A19;'>extra</span> {}.", 
			"Keep it up. You are having the <span style='color: #4BCA25;'>perfect</span> rate of {}.")
		
		# Functions to format self.USER_ADVICES
		self.USER_ADVICES_VALUES = (lambda: self.get_advices(AdvicesTypes.LOW), lambda: self.get_advices(AdvicesTypes.EXTRA), lambda: self.get_advices(AdvicesTypes.PERFECT))

		self.USER_VARIABLES = ("weight", "age", "height", "BMR")
		self.GOODLOOKING_USER_VARIABLES = [snake_case_to_sentence_case(var) for var in self.USER_VARIABLES]
		self.GOODLOOKING_USER_VARIABLE_TO_USER_VARIABLE = {goodlooking_user_varible:user_variable for goodlooking_user_varible, user_variable in zip(self.GOODLOOKING_USER_VARIABLES, self.USER_VARIABLES)}
		self.USER_VARIABLE_TO_GOODLOOKING_USER_VARIABLE = {val:key for key, val in self.GOODLOOKING_USER_VARIABLE_TO_USER_VARIABLE.items()}

		self.STATEMENTS = ("Variable", "Number", "Operator")
		self.STATEMENT_TYPES = (StatementTypes.VARIABLE, StatementTypes.NUMBER, StatementTypes.OPERATOR)
		self.STATEMENT_TO_TYPE = {statement:statement_type for statement, statement_type in zip(self.STATEMENTS, self.STATEMENT_TYPES)}
		self.TYPE_TO_STATEMENT = {val:key for key, val in self.STATEMENT_TO_TYPE.items()}

		self.load_assets()
		self.init_prefs()
		self.init_window()

	@property
	def today(self) -> str:
		return datetime.datetime.now().strftime('%Y-%m-%d')

	@property
	def current_user(self) -> str:
		return self.prefs.file["current_user"]

	@property
	def sex(self) -> str:
		return self.prefs.file["users"][self.current_user]["sex"]

	@property
	def age(self) -> int:
		return self.prefs.file["users"][self.current_user]["age"]

	@property
	def weight(self) -> int:
		return self.prefs.file["users"][self.current_user]["weight"]

	@property
	def height(self) -> int:
		return self.prefs.file["users"][self.current_user]["height"]

	@property
	def activity(self) -> str:
		return self.prefs.file["users"][self.current_user]["activity"]

	@property
	def BMR(self) -> float:
		return self.prefs.file["users"][self.current_user]["BMR"]

	@property
	def user_nutrition(self) -> dict:
		if not "nutrition" in self.prefs.file["users"][self.current_user]:
			self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{casestyle.snakecase(meal):{"total": 0, **{casestyle.snakecase(food):0 for food in self.FOODS}} for meal in self.MEALS}})
		else:
			if not self.today in self.prefs.file["users"][self.current_user]["nutrition"]:
				self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{casestyle.snakecase(meal):{"total": 0, **{casestyle.snakecase(food):0 for food in self.FOODS}} for meal in self.MEALS}})

		return self.prefs.file["users"][self.current_user]["nutrition"]

	@property
	def nutrition_info(self) -> dict:
		return self.prefs.file["nutrition"]

	def load_assets(self):
		QFontDatabase.addApplicationFont(':/Fonts/Alatsi regular.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-B.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-BI.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-L.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-LI.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-M.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-MI.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-R.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-RI.ttf')
		QFontDatabase.addApplicationFont(':/Fonts/Ubuntu-Th.ttf')

	def init_prefs(self) -> None:
		"""This function inits the PREFS class to manage preferences."""
		
		# Default prefs
		prefs = {
			"current_user": "", 
			"state": {
				"settings_dialog": {
					"pos": (0, 0), 
					"size": (500, 400)
				}, 
				"main_window": {
					"pos": (500, 500), 
					"size": (10000, 10000)
				}, 
				"meal_tabs_splitters": 
				{
					e:[528, 530] for e in range(len(self.MEALS))
				}, 
				"stats_splitter": [200, 200], 
				"calories_per_day_comobox_checked": 0, 
				"selected_tab": 0, 
				"selected_meal_tab": 0, 
			}, 
			"nutrition": self.default_nutriton, 
			"users": {}, 
		}
		
		self.prefs = PREFS.PREFS(prefs, filename="Prefs/settings") # Create instance

	def init_window(self) -> None:
		"""This function will define the layout and call self.main_frame to create the main frame."""
		# Define grid
		self.setLayout(QGridLayout())

		# FONTS
		# QFontDatabase.addApplicationFont(':/impact.ttf')

		# Create frame
		self.main_frame()

	def update_calories_label(self) -> None:
		"""This function will subrtact the current calories with the daily ideal ones, 
		and display a message in the calories label.
		"""

		# Get current calories
		calories = self.prefs.file["users"][self.current_user]["nutrition"][self.today]["total"]

		# BMR stands for Basal Metabolic Rate (daily calories)
		if calories + 50 < self.BMR:
			message = "You have {} calories left."
		elif calories - 50 > self.BMR:
			message = "You are {} calories <strong>over</strong> the daily rate."
		else:
			message = "You have ate the perfect rate of calories."

		calories_left = round(self.BMR - calories, 3)

		# Update calories_label text
		self.widgets["calories_label"][-1].setText(message.format(abs(calories_left)))

	def update_splitters_sizes(self) -> None:
		"""Update the splitters size with the stored in the prefs file."""

		# Set the sizes of the stats_splitter
		self.widgets["stats_splitter"][-1].setSizes(self.prefs.file["state"]["stats_splitter"])
		
		# Iterate trough meal tabs and set splitter sizes
		for e, meal_tab in enumerate(self.widgets["meal_tabs"]):
			meal_tab.widget(0).setSizes(self.prefs.file["state"]["meal_tabs_splitters"][str(e)])

	def update(self) -> None:
		if self.current_user == "": # If no current_user means there are no users
			self.clear_user_widgets() # Clear widgets
			self.create_init_widget() # Create add user button
			return # And retturn

		self.update_tabs()
		self.update_pie_chart()
		self.update_bar_chart()
		self.update_splitters_sizes()

		self.update_calories_per_day_tab()
		self.animate_charts()
	
		self.update_advices_tab()
	
		self.update_current_user_label()		

	def update_tabs(self):
		if len(self.widgets["init_widget"]) > 0:
			self.remove_init_widget()
			self.create_tabs()
			
		# Update calories lable with the new user daily calories
		self.update_calories_label()
	
		self.widgets["stats_splitter"][-1].widget(1).setParent(None)
		self.widgets["meal_tabs"] = []

		meal_tabs = self.create_meal_tabs()

		self.widgets["stats_splitter"][-1].addWidget(meal_tabs)

	def clear_user_widgets(self):
		if len((tabs := self.widgets["tabs"])) > 0:
			tabs[-1].setParent(None)
			tabs = []

		if len((calories_label := self.widgets["calories_label"])) > 0:
			calories_label[-1].setParent(None)
			calories_label = []

		if len((current_user_label := self.widgets["current_user_label"])) > 0:
			current_user_label[-1].setParent(None)
			current_user_label = []

	def create_init_widget(self):
		"""The widgets to be displayed when there are no users.
		"""
		init_widget = QWidget()
		init_widget.setLayout(QVBoxLayout())

		healeat_sumary = QLabel(
		"""
		<body>
			<b>Healeat</b> is a nutritional tracker to measure the calories you eat on each meal <br>according to your weight, height, sex, physical activity and age.
			<hr>
			You can change the calories you eat on each meal by food using a slider (<i>Breakfast/Vegetables</i>).<br>
			<br>
			After one or two days of using <b>Healeat</b> you will be able <br>to see some charts showing you the calories you ate each day by foods or by meals.
			<hr>
			To start you will need to create a user, do it by clicking the button below.
		</body
		"""
		)

		healeat_sumary.setStyleSheet("font-size: 20px; margin-top: 50px;")

		create_user_button = QPushButton("Create user")
		create_user_button.setStyleSheet("font-size: 20px;")

		create_user_button.setFixedWidth(200)
		create_user_button.setFixedHeight(50)

		create_user_button.clicked.connect(self.create_user_on_init_widget)

		# Instructions widget
		instructions_widget = QWidget()
		instructions_widget.setLayout(QHBoxLayout())
		instructions_widget.setStyleSheet("font-style: italic; font-size: 16px;")

		instructions_label = QLabel("For more information see the")

		instructions_button = QPushButton("Instructions")
		instructions_button.clicked.connect(lambda: create_instructions_dialog(parent=self, foods=self.FOODS, meals=self.MEALS))

		instructions_widget.layout().addWidget(instructions_label, Qt.AlignLeft)
		instructions_widget.layout().addWidget(instructions_button, Qt.AlignLeft)
		instructions_widget.layout().addStretch(20)

		# Add widgets to init_widget
		init_widget.layout().addWidget(healeat_sumary)
		init_widget.layout().addWidget(create_user_button)
		init_widget.layout().addStretch(500)
		init_widget.layout().addWidget(instructions_widget, Qt.AlignBottom | Qt.AlignLeft)

		self.layout().addWidget(init_widget, 1, 0, 2, 2)

		self.widgets["init_widget"].append(init_widget)

	def remove_init_widget(self):
		self.widgets["init_widget"][-1].setParent(None)
		self.widgets["init_widget"] = []

	def create_user_on_init_widget(self):
		"""Open add_user_dialog and remove init_widget
		"""

		answer = self.add_user_dialog(parent=self)
		if answer:
			self.remove_init_widget()
			self.create_widgets()

	def get_meals_totals_by_date(self):
		result = [[] for i in self.MEALS]

		for date_count, (date, date_info) in enumerate(self.user_nutrition.items()):
			for meal, food in date_info.items():
				if meal == "total": # That meal total is equal to the sum of all MEALS
					continue

				result[self.MEALS.index(snake_case_to_sentence_case(meal))].append(food["total"]) # This food total is the sum of only one meal

		return result

	def get_foods_totals(self, date: str=None):
		"""Sum all FOODS total from every food (in a certain date).
		
		Args:
			date (str, optional=self.today): A date to search in (2021-08-22, 2021-08-23, 2021-08-24)
		"""
		if date is None:
			date = self.today

		result = defaultdict(lambda: 0)

		for meal, meal_info in self.user_nutrition[date].items():
			if meal == "total": continue

			for food, food_val in meal_info.items():
				if food == "total": continue

				result[snake_case_to_sentence_case(food)] += food_val

		return result

	def get_foods_totals_by_date(self):
		result = [[] for i in self.FOODS]

		for date_count, date in enumerate(self.get_dates()):
			for e, (food, food_total) in enumerate(self.get_foods_totals(date=date).items()):
				result[e].append(food_total)

		return result

	def get_foods_by_meal(self, meal):
		result = {}

		for food, portion_value in self.user_nutrition[self.today][casestyle.snakecase(meal)].items():

			if food == "total":	continue # this meal total is equal to the sum of all MEALS (breakfast, lunch, etc)
			
			result[food] = portion_value

		return result

	def get_ideal_meal_portions(self):
		result = {}

		BMR = self.BMR

		for meal, meal_ideal in self.nutrition_info["ideal_meal_portions"].items():
			result[meal] = eval(meal_ideal)

		return result

	def get_ideal_portions(self):
		"""This function returns a dictionary with the food and the ideal portion to it according to the current user.

		Return:
			dict: {"vegetables": 123.90, "grains": 123.90, "fruits": 123.90}
		
		"""
		result = {}

		age = self.age
		sex = self.sex
		weight = self.weight
		height = self.height
		activity = self.height
		BMR = self.BMR

		for food, food_ideal_portion in self.nutrition_info["ideal_portions"].items():

			ideal_portion_value = eval(food_ideal_portion)

			result[food] = ideal_portion_value

		return result

	def get_portions_max(self, sum_all_meals: bool=False):
		"""Sum the max value that any food slider can have.		
		"""
		result = 0
		data = self.get_ideal_portions()

		for food, food_ideal_portion in data.items():
			result += food_ideal_portion * 2

		return result * len(self.MEALS) if sum_all_meals else result

	def calculate_meal_total(self):
		meals_total_keys = []
		meals_total_values = []

		for meal, food_info in self.user_nutrition[self.today].items():
			if meal == "total":	continue # this meal total is equal to the sum of all MEALS (breakfast, lunch, etc)

			meal_total = 0
			for food_total in self.get_foods_by_meal(meal).values():
				meal_total += food_total

			meals_total_keys.append(f'users/{self.current_user}/nutrition/{self.today}/{meal}/total')
			meals_total_values.append(meal_total)

		self.prefs.write_multiple_prefs(meals_total_keys, meals_total_values)

	def calculate_day_total(self):
		"""
		Notes:
			First call calculate_meal_total to calculate the total.
		"""
		day_total = 0

		for meal, food_info in self.user_nutrition[self.today].items():
			if meal == "total":	continue # this meal total is equal to the sum of all MEALS (breakfast, lunch, etc)

			day_total += food_info["total"]

		self.prefs.write_prefs(f'users/{self.current_user}/nutrition/{self.today}/total', day_total)

	def create_meal_tabs(self):
		def on_slider_changed(value, meal, food, slider):
			self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}/{casestyle.snakecase(meal)}/{casestyle.snakecase(food)}", value)
			
			slider.setToolTip(f"{slider.value()}")

			self.calculate_meal_total()
			self.calculate_day_total()
			
			self.update_calories_label()

			start_timer()	

		def start_timer():
			"""Check if the timer is active, if it isn't, start it, if it is restart it.
			"""

			if not timer.isActive():
			    timer.start(TIME_TO_UPDATE_CHARTS)
			    return

			timer.setInterval(TIME_TO_UPDATE_CHARTS)

		def timer_timeout():
			current_meal = self.MEALS[meal_tabs.currentIndex()]

			self.update_pie_chart()
			update_meal_chart(current_meal)
			
			timer.stop()

		def create_bar_series():
			series =  QHorizontalStackedBarSeries()

			for color, (food, food_value) in zip(self.FOODS_COLORS, self.get_foods_by_meal(meal).items()):
				food_set = QBarSet(snake_case_to_sentence_case(food))
				food_set.setColor(QColor(color))

				food_set << food_value

				series.append(food_set)

			return series

		def create_meal_chart(meal):
			if self.verbose: print(f"Create {meal} chart in meal tabs")
	
			bar_series = create_bar_series()

			line_series = QLineSeries()
			line_series.setName("Ideal")

			line_series_pen = line_series.pen()
			line_series_pen.setWidth(2)
			line_series_pen.setColor(QColor(self.IDEAL_LINE_COLOR))
			line_series.setPen(line_series_pen)

			ideal_line_value = self.get_ideal_meal_portions()[casestyle.snakecase(meal)]

			line_series.append(QPoint(int(ideal_line_value), -10))
			line_series.append(QPoint(int(ideal_line_value), 10))

			chart = QChart()

			chart.addSeries(bar_series)
			chart.addSeries(line_series)

			chart.setTitle(f"Calories by food ({meal})")
			chart.setAnimationOptions(QChart.SeriesAnimations)

			axisY = QBarCategoryAxis()
			axisY.setTitleText(meal)
			axisY.setLabelsVisible(False)

			chart.addAxis(axisY, Qt.AlignLeft)
			line_series.attachAxis(axisY)
			bar_series.attachAxis(axisY)

			axisX = QValueAxis()
			axisX.setTitleText("Calories")

			chart.addAxis(axisX, Qt.AlignBottom)
			line_series.attachAxis(axisX)
			bar_series.attachAxis(axisX)
			
			current_meal_calories = self.user_nutrition[self.today][casestyle.snakecase(meal)]["total"]
			ideal_line_value = self.get_ideal_meal_portions()[casestyle.snakecase(meal)]

			axisX.setRange(0, current_meal_calories + 100 if current_meal_calories > ideal_line_value else ideal_line_value + 100)

			chart.axisX().setGridLineVisible(False)
			chart.axisY().setGridLineVisible(False)

			chart_view = QChartView(chart)
			chart_view.setRenderHint(QPainter.Antialiasing)

			return chart_view, chart, bar_series

		def update_meal_chart(meal):
			if self.verbose: print(f"Update {meal} chart in meal tabs")

			series = meal_charts_series[meal]
			series.clear()

			for color, (food, food_value) in zip(self.FOODS_COLORS, self.get_foods_by_meal(meal).items()):
				food_set = QBarSet(snake_case_to_sentence_case(food))
				food_set.setColor(QColor(color))

				food_set << food_value

				series.append(food_set)
			
			current_meal_calories = self.user_nutrition[self.today][casestyle.snakecase(meal)]["total"]
			ideal_line_value = self.get_ideal_meal_portions()[casestyle.snakecase(meal)]

			meal_charts[meal].axisX().setRange(0, current_meal_calories + 100 if current_meal_calories > ideal_line_value else ideal_line_value + 100)

		def animate_splitter(index):
			splitter = meal_tabs_splitters[index]
			sizes = splitter.sizes()
			
			sizes[1] += 10
			splitter.setSizes(sizes)

			sizes[1] -= 10
			splitter.setSizes(sizes)

		def on_tab_change(index):
			nonlocal first_time

			if first_time:
				first_time = False
				return
			
			self.prefs.write_prefs("state/selected_meal_tab", index)
			animate_splitter(index)

		def on_splitter_moved(pos, _, index):
			self.prefs.write_prefs(f"state/meal_tabs_splitters/{index}", meal_tabs_splitters[index].sizes())

		if self.verbose: print(f"Create meal tabs")

		first_time = True

		TIME_TO_UPDATE_CHARTS = 500 # Miliseconds
		timer = QTimer()
		timer.timeout.connect(timer_timeout)

		meal_tabs = VerticalTabWidget()
		meal_tabs.currentChanged.connect(on_tab_change)

		meal_charts = {}
		meal_charts_series = {}		
		meal_tabs_splitters = []

		for e, meal in enumerate(self.MEALS): # Breakfast, lunch, dinner and extra
			meal_tab = QSplitter(Qt.Horizontal)
			meal_tab.splitterMoved.connect(lambda pos, _, splitter_index=e: on_splitter_moved(pos, _, splitter_index))
			
			meal_tab_sliders = QWidget()
			meal_tab_sliders.setLayout(QFormLayout())

			for food, food_ideal_portion in zip(self.FOODS, self.get_ideal_portions().values()): # Vegetables, whole grains, fruits, etc
				slider = QSlider(Qt.Horizontal)
				slider.setFocusPolicy(Qt.StrongFocus)
				slider.setTickPosition(QSlider.NoTicks)
				
				slider.setMinimum(0)
				slider.setMaximum(int(food_ideal_portion // 2))
				
				slider.setPageStep(int(slider.maximum() // 10))
				slider.setSingleStep(int(slider.maximum() // 10))

				slider_value = self.user_nutrition[self.today][casestyle.snakecase(meal)][casestyle.snakecase(food)]
				
				slider.setValue(slider_value)
				slider.setToolTip(f"{slider_value}")

				slider.valueChanged.connect(lambda value, meal=meal, food=food, slider=slider: on_slider_changed(value, meal, food, slider))

				meal_tab_sliders.layout().addRow(food, slider)

			meal_tab.addWidget(meal_tab_sliders)
			
			meal_chart_view, meal_chart, meal_chart_series = create_meal_chart(meal)
			meal_charts_series[meal] = meal_chart_series
			meal_charts[meal] = meal_chart
			
			meal_tab.addWidget(meal_chart_view)
			meal_tab.setSizes(self.prefs.file["state"]["meal_tabs_splitters"][f"{e}"])
			meal_tabs_splitters.append(meal_tab)

			meal_tabs.addTab(meal_tab, meal)

		meal_tabs.setCurrentIndex(self.prefs.file["state"]["selected_meal_tab"])

		self.widgets["meal_tabs"].append(meal_tabs)
		return meal_tabs

	def get_advices(self, advice_type: str):
		food_data = self.get_all_foods_totals_today()
		ideal_food_data = self.get_ideal_portions()

		food_list = []

		for (food, food_value), ideal_food_value in zip(food_data.items(), ideal_food_data.values()):

			if advice_type == AdvicesTypes.LOW:
				food_difference = ideal_food_value - food_value 
			elif advice_type == AdvicesTypes.EXTRA:
				food_difference = food_value - ideal_food_value
			elif advice_type == AdvicesTypes.PERFECT:
				food_difference = abs(food_value - ideal_food_value)

			condition = food_difference > 30 if advice_type != AdvicesTypes.PERFECT else food_difference < 30
			if condition:
				food_list.append(food)


		if len(food_list) < 1: # Means if it's empty
			return False

		result = ""

		for e, food in enumerate(food_list):
			if e == len(food_list) - 2:
				result += f"{food} and "
			elif e == len(food_list) - 1:
				result += f"{food}"
			else:
				result += f"{food}, "

		return snake_case_to_sentence_case(result).lower()

	def update_advices_tab(self):
		"""This function will update the created labels on self.create_advices_tab
		"""
		if self.verbose: print("Update advices tab")
		
		advices_tab_layout = self.widgets["advices_tab"][-1].layout()

		advices_labels = list(get_widgets_from_layout(advices_tab_layout, widget_type=QLabel)) # User advice labels (depend on the user)
		
		health_advices_layout = get_widget_from_layout(advices_tab_layout, 0, QScrollArea).widget().layout()
		health_advices_labels = get_widgets_from_layout(health_advices_layout, widget_type=QLabel) # The list of QLabel widgets
		health_advices_list = choose_random_from_list(self.HEALTH_ADVICES, 3) # Health advice labels which means advices from self.HEALTH_ADVICES (not depend on the user)

		## Update health advices labels ##
		for advice_label, advice in zip(health_advices_labels, health_advices_list):						
			advice_label.setText(advice) # Choose a random advice from health_adivces


		## Update user advices labels ##
		empty = True
		for advice, advice_value, advice_label in zip(self.USER_ADVICES, self.USER_ADVICES_VALUES, advices_labels):
			advice_value = advice_value() # Call advice_value to get the value depending on the user

			if not advice_value: # If value is false means there is no advice of this kind
				advice_label.setVisible(False) # Then hide it
				continue # And try the next label
			
			advice_label.setVisible(True) # Otherwise show it
			advice_label.setText(advice.format(advice_value)) # Set the text to the value
			
			if empty: empty = False # Set it to false because there are advices to display

		if empty: # Means all labels are emtpy
			advices_labels[0].setVisible(True)
			advices_labels[0].setText("It seems there are no advices to give you yet.")		

	def create_advices_tab(self):
		"""This function creates all the needed lables to display advices, it just creates them, not the content (the labels are filled in self.update_advices_tab)

		"""
		## Create QWidget to contain all advices tab. ##
		advices_tab = QWidget()
		advices_tab.setLayout(QVBoxLayout())

		## Create widgets ##
		for _ in self.USER_ADVICES: # This loop will create advices related with the user
			advice_label = QLabel()				
			advice_label.setStyleSheet("font-weight: bold; font-size: 19px; color: #3A3A3A; font-family: Ubuntu;")

			# Position widgets into advices_tab layout
			advices_tab.layout().addWidget(advice_label)
			
		advices_tab.layout().addSpacing(10) # spacing	

		health_advices_area = QWidget()
		health_advices_area.setLayout(QFormLayout())

		health_advices_scroll = ScrollArea(health_advices_area)

		for _ in range(self.HEALTH_ADVICES_TO_DISPLAY): # This loop will create health advices (not related with the user)
			advice_label = QLabel()
			advice_label.setStyleSheet("border: none; font-weight: bold; font-size: 18px; color: #4e342e; margin-top: 5px; padding: 2px 2px 2px 2px; font-family: Ubuntu;")#" background-color: #B9B9B9;")
			advice_label.setAlignment(Qt.AlignLeft)

			# Position widgets into advices_tab layout
			health_advices_area.layout().addWidget(advice_label)
			
		advices_tab.layout().addWidget(health_advices_scroll)
		self.widgets["advices_tab"].append(advices_tab)		
		return advices_tab

	def get_all_foods_totals_today(self):
		"""Get the total of all fods of today's current user.

		Return:
			dict: {"vegetables": 124, "grains": 94, ...}
		"""
		result = defaultdict(lambda: 0)

		for meal, meal_data in self.user_nutrition[self.today].items():
			if meal == "total":
				continue
			
			for food, portion_value in meal_data.items():
				if food == "total":
					continue

				result[food] += portion_value

		return result	

	def update_pie_chart(self):
		if self.verbose: print("Update pie chart")

		chart = self.widgets["charts"]["pie"][-1]

		series = self.widgets["charts_series"]["pie"][-1]
		series.clear()

		self.create_slices_pie(series)

	def create_slices_pie(self, series):
		for color, (food, food_total) in zip(self.FOODS_COLORS, self.get_all_foods_totals_today().items()):
			_slice = series.append(food.replace("_", " ").capitalize(), food_total)
			_slice.setBrush(QColor(color))
			if food_total > 0: _slice.setLabelVisible() # Otherwise there will be a lot of labels over

		return series

	def create_pie_chart(self):
		if self.verbose: print("Create pie chart")

		series = QPieSeries()

		self.create_slices_pie(series)

		chart = QChart()
		chart.addSeries(series)
		chart.setAnimationOptions(QChart.SeriesAnimations)
		chart.setTitle("Calories by food (Today)")
		chart.legend().setVisible(False)

		chart_view = QChartView(chart)
		chart_view.setRenderHint(QPainter.Antialiasing)

		self.widgets["charts"]["pie"].append(chart)
		self.widgets["charts_series"]["pie"].append(series)

		return chart_view

	def create_calories_label(self):
		calories_label = QLabel()
		calories_label.setStyleSheet("font-size: 30px; font-family: Alatsi;")
		calories_label.setAlignment(Qt.AlignCenter)

		self.widgets["calories_label"].append(calories_label)
		self.update_calories_label()

		return calories_label

	def update_bar_chart(self):
		if self.verbose: print("Update bar chart")
	
		chart = self.widgets["charts"]["bar"][-1]

		series = self.widgets["charts_series"]["bar"][-1]
		series.clear()

		series = self.create_bar_series()

		dates = self.get_dates()
		
		axisX = QBarCategoryAxis()
		axisX.setTitleText("Date")
		axisX.append(dates)

		chart.removeAxis(chart.axisX())
		chart.addAxis(axisX, Qt.AlignBottom)
		series.attachAxis(axisX)
				
		max_calories = dict_max(self.user_nutrition) # This will find the biggest value inside all nutrition dates
		chart.axisY().setRange(0, max_calories + 100 if max_calories > self.BMR else self.BMR + 100)

	def get_dates(self):
		dates = []

		for date in self.user_nutrition.keys():
			dates.append(date)

		return dates

	def create_bar_series(self, bar_series=QStackedBarSeries()):
		def on_series_hoverd(point, state):
			if not point:
				return
					
		## Use MEALS data if calories_per_day_comobox_checked else use FOODS data ##
		if self.prefs.file["state"]["calories_per_day_comobox_checked"] == 0:
			data = self.get_meals_totals_by_date() # Data
			colors = self.MEALS_COLORS # Colors
			names_list = self.MEALS # A list for the bar set names
		elif self.prefs.file["state"]["calories_per_day_comobox_checked"] == 1:
			data = self.get_foods_totals_by_date() # Data
			colors = self.FOODS_COLORS # Colors
			names_list = self.FOODS # A list for the bar set names

		for e, (color, values_list) in enumerate(zip(colors, data)):
			_set = QBarSet(names_list[e])
			_set.setColor(QColor(color))

			for value in values_list:
				_set << value

			bar_series.append(_set)

		#bar_series.hovered.connect(on_series_hoverd)
		return bar_series

	def create_bar_chart(self):
		dates = self.get_dates()

		chart = QChart()

		bar_series = self.create_bar_series()

		## ideal line ##		
		line_series = QLineSeries()
		line_series.setName("Ideal")

		line_series_pen = line_series.pen()
		line_series_pen.setWidth(2)
		line_series_pen.setColor(QColor(self.IDEAL_LINE_COLOR))
		line_series.setPen(line_series_pen)

		line_series.append(QPoint(-100, int(self.BMR)))
		line_series.append(QPoint(100, int(self.BMR)))

		## Add series to chart ##
		chart.addSeries(bar_series)
		chart.addSeries(line_series)
		chart.setTitle("Calories along the days")
		chart.setAnimationOptions(QChart.SeriesAnimations)

		axisX = QBarCategoryAxis()
		axisX.setTitleText("Date")
		axisX.append(dates)
				
		chart.addAxis(axisX, Qt.AlignBottom)
		
		line_series.attachAxis(axisX)
		bar_series.attachAxis(axisX)

		axisX.setRange(dates[0], dates[-1])

		axisY = QValueAxis()
		axisY.setTitleText("Calories")
		chart.addAxis(axisY, Qt.AlignLeft)
		line_series.attachAxis(axisY)
		bar_series.attachAxis(axisY)

		max_calories = dict_max(self.user_nutrition) # This will find the biggest value inside all nutrition dates
		axisY.setRange(0, max_calories + 100 if max_calories > self.BMR else self.BMR + 100)

		chart_view = QChartView(chart)
		chart_view.setRenderHint(QPainter.Antialiasing)

		self.widgets["charts"]["bar"].append(chart)
		self.widgets["charts_series"]["bar"].append(bar_series)

		return chart_view

	def animate_charts(self, *args, **kwargs):
		"""
		Increase the window height by one and decrease it to the original size to animate the bar charts.
		"""		

		main_window_geometry = self.window().geometry()
		main_window_width, main_window_height = main_window_geometry.width(), main_window_geometry.height()

		self.window().resize(main_window_width, main_window_height + 1)
		self.window().resize(main_window_width, main_window_height)

	def update_calories_per_day_tab(self):
		if self.verbose: print("Create calories per day tab")
	
		"""This function removes the comboboxes that changes the way calories per day chart is displayed (the two options are "by MEALS" or "by FOODS").
			I do this because otherwise the combobxes just stop working. 
		"""
		comboboxes = self.widgets["calories_per_day_tab"][-1].layout().itemAt(0).widget()

		self.widgets["calories_per_day_tab"][-1].layout().removeWidget(comboboxes)
		comboboxes.setParent(None)
		self.widgets["calories_per_day_tab"][-1].layout().insertWidget(0, self.create_bar_chart_comboboxes())

		self.update_bar_chart()

	def create_bar_chart_comboboxes(self):
		"""This function creates two comboboxes to change the way calories per day chart is displayed (by MEALS or by foos)
		"""
		def on_combobox_change():
			index = comboboxes_group.checkedId()
			index = abs(index) - 2 # if index 0 id is -2, that's why i subtract two from index
			
			self.prefs.write_prefs("state/calories_per_day_comobox_checked", index)
			self.update_bar_chart()

		bar_chart_comboboxes = QWidget()
		bar_chart_comboboxes.setLayout(QVBoxLayout())

		comboboxes_group = QButtonGroup()
		comboboxes_group.setExclusive(True)
		comboboxes_group.idToggled.connect(on_combobox_change)

		by_meals_radiobutton = QRadioButton("By meals")
		by_food_radiobutton = QRadioButton("By foods")
		by_food_radiobutton.setStyleSheet("margin: 0px 0px 0px 0px;")

		if (calories_per_day_comobox_checked := self.prefs.file["state"]["calories_per_day_comobox_checked"]) == 0:
			by_meals_radiobutton.setChecked(True)
		elif calories_per_day_comobox_checked == 1:
			by_food_radiobutton.setChecked(True)

		comboboxes_group.addButton(by_meals_radiobutton)
		comboboxes_group.addButton(by_food_radiobutton)

		bar_chart_comboboxes.layout().addWidget(by_meals_radiobutton)	
		bar_chart_comboboxes.layout().addWidget(by_food_radiobutton)

		return bar_chart_comboboxes

	def create_calories_per_day_tab(self):
		if self.verbose: print("Create calories per day tab")

		## calories_per_day_tab Widget ##
		calories_per_day_tab = QWidget()
		calories_per_day_tab.setLayout(QVBoxLayout())

		## Bar chart ##
		bar_chart = self.create_bar_chart() 

		## Position widgets on calories_per_day_tab ##
		calories_per_day_tab.layout().addWidget(self.create_bar_chart_comboboxes())
		calories_per_day_tab.layout().addWidget(bar_chart)

		self.widgets["calories_per_day_tab"].append(calories_per_day_tab)

		return calories_per_day_tab

	def create_widgets(self):
		"""Create all widgets."""
		self.create_current_user_label()	
		self.create_tabs()

		self.update()

	def create_tabs(self):
		def on_tab_change(index):
			nonlocal first_time

			if first_time:
				first_time = False
				return

			self.prefs.write_prefs("state/selected_tab", index)

			if index == 0:
				self.update_pie_chart()
			elif index == 1:
				self.update_calories_per_day_tab()
			elif index == 2:
				self.update_advices_tab()

			self.animate_charts()
	
		def on_splitter_moved(pos, index):
			self.prefs.write_prefs(f"state/stats_splitter", stats_splitter.sizes())

		def next_tab():
			tabs.setCurrentIndex((tabs.currentIndex() + 1) % tabs.count())

		first_time = True

		tabs = QTabWidget()
		tabs.currentChanged.connect(on_tab_change)

		tabs_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), tabs)
		tabs_shortcut.activated.connect(next_tab)

		## Splitter ##
		stats_splitter = QSplitter(Qt.Vertical)
		stats_splitter.splitterMoved.connect(on_splitter_moved)
		
		first_splitter_area = QWidget()
		first_splitter_area.setLayout(QVBoxLayout())

		second_splitter_area = QWidget()
		second_splitter_area.setLayout(QVBoxLayout())

		## Charts ##
		calories_per_day_tab = self.create_calories_per_day_tab()
		pie_chart = self.create_pie_chart()

		## Nutrition ##
		calories_label = self.create_calories_label()
		nutrition_tabs = self.create_meal_tabs()

		## Advices ##
		advices_tab = self.create_advices_tab()

		## Position ##
		first_splitter_area.layout().addWidget(calories_label)
		first_splitter_area.layout().addWidget(pie_chart)
		second_splitter_area.layout().addWidget(nutrition_tabs)

		# Position splitters
		stats_splitter.addWidget(first_splitter_area)
		stats_splitter.addWidget(second_splitter_area)
		stats_splitter.setSizes(self.prefs.file["state"]["stats_splitter"])
		
		## Add tabs to tabs widget ##
		tabs.addTab(stats_splitter, "Main")
		tabs.addTab(calories_per_day_tab, "Calories per day")
		tabs.addTab(advices_tab, "Advices")		

		tabs.setCurrentIndex(self.prefs.file["state"]["selected_tab"])

		## Position tabs in main widget ##
		self.layout().addWidget(tabs, 2, 0, 1, 0)

		## Add elements to self.widgets dictionary##
		self.widgets["stats_splitter"].append(stats_splitter)
		self.widgets["tabs"].append(tabs)

	def create_current_user_label(self):
		current_user_label = QLabel(self.current_user)
		current_user_label.setStyleSheet("font-size: 30px; margin-right: 10px;")
		current_user_label.setAlignment(Qt.AlignRight)

		self.layout().addWidget(current_user_label, 1, 1)
		self.widgets["current_user_label"].append(current_user_label)

	def update_current_user_label(self):
		current_user_label = self.widgets["current_user_label"][-1]

		current_user_label.setText(self.current_user)

	def main_frame(self):
		logo = QLabel()
		logo.setStyleSheet("margin-bottom: 10px;")
		logo.setAlignment(Qt.AlignCenter)

		pixmap = QPixmap(":/Images/logo.png")
		logo.setPixmap(pixmap)

		self.layout().addWidget(logo, 0, 0, 2, 0, Qt.AlignTop)

		if self.prefs.file["users"] == {}:			
			self.create_init_widget()
			return

		self.create_widgets()

	def add_user_dialog(self, 
		default_username="Tim", 
		default_sex='Male', 
		default_weight=70, 
		default_height=170, 
		default_age=25, 
		default_activity="Rarely", 
		editing=False, 
		parent=None
		):

		def save_config():
			if user_input.text() in self.prefs.file["users"] and not editing:

				warning = question_dialog(
					"Already existent username", 
					"That username already exists, do you want to overwrite it?", 
					buttons=(
						(QPushButton(dialog.style().standardIcon(QStyle.SP_DialogYesButton), "Yes"), 1), 
						(QPushButton(dialog.style().standardIcon(QStyle.SP_DialogNoButton), "No"), 0), 
						), 
					icon=QMessageBox.Warning, 
					parent=dialog)
				
				if not warning:
					return
		
			username = user_input.text()

			sex_id = abs(sex_group.checkedId()) - 2
			sex = sex_list[sex_id]
			
			age = age_spinbox.value()
			weight = weight_spinbox.value()
			height = height_spinbox.value()
			activity = activity_combobox.currentText()

			if not default_username == username and editing:
				self.prefs.write_prefs("users", rename_key_from_dict(self.prefs.file["users"], default_username, username))
				self.prefs.write_prefs("current_user", username)

			if self.current_user == "": self.prefs.write_prefs(f"current_user", username)
			
			self.prefs.write_prefs(f"users/{username}/sex", sex)
			self.prefs.write_prefs(f"users/{username}/age", age)
			self.prefs.write_prefs(f"users/{username}/weight", weight)
			self.prefs.write_prefs(f"users/{username}/height", height)
			self.prefs.write_prefs(f"users/{username}/activity", activity)

			if sex == "Male":
				BMR = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
			elif sex == "Female":
				BMR = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

			if activity == "None":
				BMR *= 1.2
			elif activity == "Rarely":
				BMR *= 1.375
			elif activity == "Moderate":
				BMR *= 1.55
			elif activity == "Often":
				BMR *= 1.725

			BMR = round(BMR, 3)

			self.prefs.write_prefs(f"users/{username}/BMR", BMR)

			dialog.accept()

		dialog = QDialog(parent=parent) # Creating dialog
		dialog.setMaximumSize(1, 1)
		
		dialog.setWindowTitle("Settings") # Setting dialog title

		dialog.setWindowModality(Qt.ApplicationModal) # True blocks its parent window
		dialog.setLayout(QFormLayout())

		## User ##
		user_input = QLineEdit(default_username)

		## Sex RadioButtons ##
		sex_list = ["Male", "Female"]
		sex_group = QButtonGroup()
		sex_box = QHBoxLayout()
		
		for e, sex in enumerate(sex_list):
			sex_radio_button = QRadioButton(sex)

			if not default_sex is None:
				if sex == default_sex:
					sex_radio_button.setChecked(True)

			sex_group.addButton(sex_radio_button)
			sex_box.addWidget(sex_radio_button)

		## Weight and height ##
		weight_spinbox = QSpinBox(suffix=" kg")
		height_spinbox = QSpinBox(suffix=" cm")

		weight_spinbox.setMaximum(300)
		weight_spinbox.setMinimum(1)
		weight_spinbox.setValue(default_weight)

		height_spinbox.setMaximum(300)
		height_spinbox.setMinimum(1)
		height_spinbox.setValue(default_height)


		## Age spinbox ##
		age_spinbox = QSpinBox(suffix=" years")

		age_spinbox.setMaximum(150)
		age_spinbox.setMinimum(1)
		age_spinbox.setValue(default_age)

		## Activity Combobox ##
		activity_list = ["Often", "Moderate", "Rarely", "None"]
		activity_combobox = QComboBox()
		activity_combobox.addItems(activity_list)
		activity_combobox.setCurrentIndex(activity_list.index(default_activity))

		## Ok button ##
		ok_button = QPushButton("Ok")
		ok_button.clicked.connect(save_config)

		## Position widgets ##
		#dialog.layout().addRow(label)

		dialog.layout().addRow("Username: ", user_input)
		dialog.layout().addRow("Sex: ", sex_box)
		dialog.layout().addRow("Weight: ", weight_spinbox)
		dialog.layout().addRow("Height: ", height_spinbox)
		dialog.layout().addRow("Age: ", age_spinbox)
		dialog.layout().addRow("Physical activity: ", activity_combobox)

		dialog.layout().addRow(ok_button)

		return dialog.exec_()

	def create_ideal_portion_settings_tab(self, parent=None):
		def add_or_remove_dialog(food_layout: QLayout, food: str):
			answer = question_dialog(
				"Add or remove", 
				"Add a statement at the end or remove the last statement.", 
				parent=nutrition_tab, 				
			)

			# If none of the below conditions are true, means cancel

			if answer == 1: # Means remove
				if food_layout.count() <= 1:
					QMessageBox.warning(nutrition_tab, "Nothing to remove", "There are no more statements to remove.")
					return

				last_widget = get_widget_from_layout(food_layout, -2) # -2 because -1 it's add_remove button itself
				last_widget.setParent(None)

				statement = split_expression(self.prefs.file["nutrition"]["ideal_portions"][food], include_type=False)

				if check_syntax(self.prefs.file["nutrition"]["ideal_portions"][food]): 
					self.prefs.write_prefs(f"nutrition/ideal_portions_cache/{food}", self.prefs.file["nutrition"]["ideal_portions"][food])
				else:	
					print(f'invalid syntax {self.prefs.file["nutrition"]["ideal_portions"][food]}')

				self.prefs.write_prefs(f"nutrition/ideal_portions/{food}", "".join(statement[:-1]))

			elif answer == 2: # Means add
				statement, ok = get_item_input_dialog(self.STATEMENTS, "Choose an statement.", parent=nutrition_tab)
				
				if not ok:
					return

				statement_type = self.STATEMENT_TO_TYPE[statement]
				
				if statement_type == StatementTypes.NUMBER:
					statement, statement_ok = get_double_input_dialog("Enter a value", parent=nutrition_tab)
				
				elif statement_type == StatementTypes.VARIABLE:
					statement, statement_ok = get_item_input_dialog(self.USER_VARIABLES, "Choose a variable", parent=nutrition_tab)
				
				elif statement_type == StatementTypes.OPERATOR:
					statement, statement_ok = get_item_input_dialog(GOODLOOKING_OPERATORS, "Choose an operator", parent=nutrition_tab)
				else:
					raise TypeError(f"Unknown type {statement}")

				if not statement_ok:
					return
				
				food_layout.insertWidget(food_layout.count() - 1, create_statement_button(str(statement), -1, food))
				
				if check_syntax(self.prefs.file["nutrition"]["ideal_portions"][food]): 
					self.prefs.write_prefs(f"nutrition/ideal_portions_cache/{food}", self.prefs.file["nutrition"]["ideal_portions"][food])

				self.prefs.write_prefs(f"nutrition/ideal_portions/{food}", f"{self.prefs.file['nutrition']['ideal_portions'][food]}{statement}")

		def number_dialog(statement_indx, food, button: QPushButton, title: str="Choose a number", value: float=0,):
			ideal = self.prefs.file["nutrition"]["ideal_portions"][casestyle.snakecase(food)]
			value = float(split_expression(ideal, include_type=False)[statement_indx])

			number, ok = get_double_input_dialog(title, value=value)
			#number, ok = QInputDialog.getDouble(nutrition_tab, title, label, value, minValue, maxValue, decimals, flags, step)

			if not ok:
				return

			ideal = split_expression(ideal, include_type=False)
			ideal[statement_indx] = number
			ideal = "".join(map(str, ideal))

			self.prefs.write_prefs(f"nutrition/ideal_portions/{casestyle.snakecase(food)}", ideal)			
			button.setText(str(number))

		def items_dialog(statement_indx, food, button: QPushButton, items: list, title: str="Choose an item"):
			ideal = self.prefs.file["nutrition"]["ideal_portions"][casestyle.snakecase(food)]
			value = split_expression(ideal, include_type=False)[statement_indx]

			if value in OPERATORS:
				value = OPERATOR_TO_GOODLOOKING_OPERATOR[value]

			if value in self.USER_VARIABLES:
				value = self.USER_VARIABLE_TO_GOODLOOKING_USER_VARIABLE[value]

			item, ok = get_item_input_dialog(items, title, parent=nutrition_tab, current_index=items.index(value))
			#item, ok = QInputDialog.getItem(nutrition_tab, title, label, items, current=items.index(value))

			if not ok:
				return
			
			if item in GOODLOOKING_OPERATORS:
				item = GOODLOOKING_OPERATOR_TO_OPERATOR[item]
			elif item in self.GOODLOOKING_USER_VARIABLES:
				item = self.GOODLOOKING_USER_VARIABLE_TO_USER_VARIABLE[item]

			ideal = split_expression(ideal, include_type=False)
			ideal[statement_indx] = item
			ideal = "".join(map(str, ideal))

			self.prefs.write_prefs(f"nutrition/ideal_portions/{casestyle.snakecase(food)}", ideal)

			if item in OPERATORS:
				item = OPERATOR_TO_GOODLOOKING_OPERATOR[item]
			elif item in self.USER_VARIABLES:
				item = self.USER_VARIABLE_TO_GOODLOOKING_USER_VARIABLE[item]

			button.setText(str(item))

		def create_statement_button(statement: str, statement_indx: int, food: str):
			statement_button = QPushButton(statement)
			statement_button.setStyleSheet("font-family: Ubuntu; font-size: 15px; padding: 1px 2px 1px 2px; margin: 0px 0px 0px 0px;")
			
			if statement_type == StatementTypes.NUMBER:
				statement_button.clicked.connect(
					lambda ignore, statement_indx=statement_indx, food=food, button=statement_button: 
						number_dialog(statement_indx, food, button, title="Enter a value")
				)					
			
			elif statement_type == StatementTypes.VARIABLE:
				statement_button.clicked.connect(
					lambda ignore, statement_indx=statement_indx, food=food, button=statement_button: 
						items_dialog(statement_indx, food, button, self.GOODLOOKING_USER_VARIABLES, title="Choose a variable")
				)					
			
			elif statement_type == StatementTypes.OPERATOR:
				statement_button.clicked.connect(
					lambda ignore, statement_indx=statement_indx, food=food, button=statement_button: 
						items_dialog(statement_indx, food, button, GOODLOOKING_OPERATORS, title="Choose an operator")
				)
			
			else:
				raise TypeError(f"Unknown type {statement} at {statement_indx} on {food}")

			return statement_button	

		def reset_ideal_portions():
			self.prefs.write_prefs("nutrition/ideal_portions", self.default_nutriton["ideal_portions"])
			parent.accept()
			self.settings_dialog(default_tab=0) # Reopen to update users			

		## NUTRITION TAB ##
		nutrition_tab = QWidget()
		nutrition_tab.setLayout(QFormLayout())

		for food, food_ideal_portion in self.nutrition_info["ideal_portions"].items():
			food_line = QWidget()
			food_line.setLayout(QHBoxLayout())

			food_ideal_portion = expression_to_goodlooking_expression(food_ideal_portion)
			food_ideal_portion = split_expression(food_ideal_portion, operators=GOODLOOKING_OPERATORS)
			for statement_indx, (statement, statement_type) in enumerate(food_ideal_portion):
				if statement in OPERATORS:
					statement = OPERATOR_TO_GOODLOOKING_OPERATOR[statement]

				statement_button = create_statement_button(statement, statement_indx, food)

				food_line.layout().addWidget(statement_button)

			icon = QIcon(":/Images/plus_minus_icon.png")#nutrition_tab.style().standardIcon(QStyle.SP_FileDialogInfoView)
			icon_size = min(icon.availableSizes())

			extra_btn = QPushButton(icon=icon)
			extra_btn.setFixedSize(icon_size.width(), icon_size.height())
			extra_btn.clicked.connect(lambda ignore, food_layout=food_line.layout(), food=food: add_or_remove_dialog(food_layout, food))
			
			food_line.layout().addWidget(extra_btn)

			nutrition_tab.layout().addRow(snake_case_to_sentence_case(food), food_line)

		reset_button = QPushButton("Reset")
		reset_button.clicked.connect(reset_ideal_portions)

		nutrition_tab.layout().addRow(reset_button)

		nutrition_tab_scroll = ScrollArea(nutrition_tab)

		return nutrition_tab_scroll

	def create_users_settings_tab(self, parent=None):
		def create_user():
			self.add_user_dialog(parent=self)
			
			parent.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users
	
		def remove_user(user):
			warning = question_dialog(
				f"Remove user", 
				f"Are you sure you want to remove {user} user?\nThis action cannot be undone.", 
				buttons=(
					(QPushButton(parent.style().standardIcon(QStyle.SP_DialogNoButton), "No"), 0), 					
					(QPushButton(parent.style().standardIcon(QStyle.SP_DialogYesButton), "Yes"), 2), 
					), 
				icon=QMessageBox.Warning, 
				parent=parent)
		

			if not warning: # Means no
				return

			users_with_user_removed = remove_key_from_dict(self.prefs.file["users"], user)

			self.prefs.write_prefs(f"users", users_with_user_removed)
			
			if len(self.prefs.file["users"]) >= 1:
				select_user( list(self.prefs.file["users"])[0] )
			else:
				self.prefs.write_prefs("current_user", "")
				
				parent.accept() # Close the dialog
				self.settings_dialog(default_tab=1) # Reopen to update users

		def edit_user(user):
			user_info = self.prefs.file["users"][user]
			self.add_user_dialog(
				default_username=user, 
				default_sex=user_info["sex"], 
				default_height=user_info["height"], 
				default_weight=user_info["weight"], 
				default_age=user_info["age"], 
				default_activity=user_info["activity"], 
				editing=True)
			
			parent.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users
		
		def select_user(user):
			self.prefs.write_prefs("current_user", user)
			
			parent.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users
		
		users_tab = QWidget()
		users_tab.setLayout(QGridLayout())

		### Existent users ####
		users_scrollarea = QScrollArea()
		users_widget = QWidget()
		users_grid = QGridLayout()

		for e, (user, user_info) in enumerate(self.prefs.file["users"].items()):
			user_label = QLabel(user)
			user_label.setStyleSheet("font-size: 15px")

			edit_user_button = QPushButton("Edit")
			remove_user_button = QPushButton("Remove")

			edit_user_button.clicked.connect(lambda *args, user=user: edit_user(user))
			remove_user_button.clicked.connect(lambda *args, user=user: remove_user(user))
			
			if user != self.current_user:
				select_user_button = QPushButton("Select")
				select_user_button.clicked.connect(lambda *args, user=user: select_user(user))
				
			else:
				select_user_button = QLabel("Selected")
				select_user_button.setEnabled(False)

			users_grid.addWidget(select_user_button, e, 1)


			users_grid.addWidget(user_label, e, 0)
			users_grid.addWidget(edit_user_button, e, 2)
			users_grid.addWidget(remove_user_button, e, 3)

		users_widget.setLayout(users_grid)

		users_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		users_scrollarea.setWidgetResizable(True)
		users_scrollarea.setWidget(users_widget)

		users_tab.layout().addWidget(users_scrollarea, 0, 0)

		add_user_button = QPushButton("Add user")
		add_user_button.clicked.connect(create_user)

		users_tab.layout().addWidget(add_user_button, 1, 0)	

		return users_tab	

	def settings_dialog(self, default_tab=0):
		def save_dialog_geometry(*args, **kwargs):
			dialog_geometry = dialog.geometry()
			dialog_pos = dialog_geometry.x(), dialog_geometry.y() - 64

			dialog_size = dialog_geometry.width(), dialog_geometry.height()

			self.prefs.write_prefs("state/settings_dialog/pos", dialog_pos)
			self.prefs.write_prefs("state/settings_dialog/size", dialog_size)

		def check_food_ideal_portions_expressions(event):
			for food, food_ideal in self.prefs.file["nutrition"]["ideal_portions"].items():
				if not check_syntax(food_ideal):
					answer = question_dialog("Invalid expression", 
						f"<i>{snake_case_to_sentence_case(food)} = {expression_to_goodlooking_expression(food_ideal)}</i> is a wrong expression, please fix it before continue.", 
						buttons=(
							(QPushButton(dialog.style().standardIcon(QStyle.SP_DialogOkButton), "Ok"), 1), 
							(QPushButton(dialog.style().standardIcon(QStyle.SP_DialogDiscardButton), "Reverse changes"), 0), 
						), 
						icon=QMessageBox.Critical, 
						parent=dialog)

					if answer == 1: # Means Reverse changes
						self.prefs.write_prefs(f"nutrition/ideal_portions/{food}", self.prefs.file["nutrition"]["ideal_portions_cache"][food])
						return True

					if not event is None:
						event.ignore()

					return False

			return True

		def close_event(event=None):
			if not self.current_user == "":
				if not "nutrition" in self.prefs.file["users"][self.current_user]:
					self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{casestyle.snakecase(meal):{"total": 0, **{casestyle.snakecase(food):0 for food in self.FOODS}} for meal in self.MEALS}})
				else:
					if not self.today in self.user_nutrition:
						self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{casestyle.snakecase(meal):{"total": 0, **{casestyle.snakecase(food):0 for food in self.FOODS}} for meal in self.MEALS}})

			save_dialog_geometry()

			check_syntax_answer = check_food_ideal_portions_expressions(event)
			if not check_syntax_answer:
				return

			self.update()
			dialog.accept()

		def reject():
			close_event()
		
		def next_tab():
			tabs.setCurrentIndex((tabs.currentIndex() + 1) % tabs.count())

		dialog = QDialog(self)
		dialog.setFixedSize(400, 470)
		
		dialog_size = self.prefs.file["state"]["settings_dialog"]["size"]
		dialog_pos = self.prefs.file["state"]["settings_dialog"]["pos"]

		dialog.resize(dialog_size[0], dialog_size[1])
		dialog.move(dialog_pos[0], dialog_pos[1])

		dialog.setLayout(QVBoxLayout())
		dialog.setWindowTitle("Settings")

		dialog.closeEvent = close_event
		dialog.reject = reject
		dialog.accepted.connect(save_dialog_geometry)

		## TABS ##
		tabs = QTabWidget()

		tabs_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), tabs)
		tabs_shortcut.activated.connect(next_tab)

		## NUTRITION TAB ##
		nutrition_tab = self.create_ideal_portion_settings_tab(dialog)
		
		## USERS TAB ##
		users_tab = self.create_users_settings_tab(dialog)

		## ADD TABS ##
		tabs.addTab(nutrition_tab, "Ideal Portions")
		tabs.addTab(users_tab, "Users")
		tabs.setCurrentIndex(default_tab)

		dialog.layout().addWidget(tabs)

		return dialog.exec_()

def init_app():
	app = QApplication(sys.argv)
	
	mainwindow = MainWindow("Healeat", verbose=True)
	mainwindow.show()
	sys.exit(app.exec_())

def main():
	init_app()

if __name__ == '__main__':
	main()
