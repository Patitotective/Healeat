"""
Made for Timathon code jam

Description: Diet is a simple GUI app that asks for your diet and says you what you're missing. 
Team (solo): Heatlhy tim

To see the nutritional sources see Prefs/nutrition.prefs

Made by Patitotective
Contact me:
	Discord: patitotective#0217
	Mail: cristobalriaga@gmail.com
"""

# Libraries
import sys
import os

# PyQt5
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
	QComboBox, QToolTip)

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QIcon, QFontDatabase, QKeySequence
from PyQt5.QtGui import QCursor, QPainter, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint

from PyQt5.QtChart import (
	QBarSet, QBarCategoryAxis, 
	QPieSeries, QStackedBarSeries, 
	QHorizontalStackedBarSeries, QChart, 
	QChartView, QLineSeries, QValueAxis)

import PREFS # https://patitotective.github.io/PREFS/
import datetime
import itertools
import time

# Dependencies

class MainWindow(QMainWindow):
	def __init__(self, title, parent=None):
		super().__init__(parent)
		
		self.title = title
		
		# self.setWindowIcon(QtGui.QIcon(':/icon.png'))
		
		self.window()
		self.create_menu_bar()

	def window(self):
		# Window settings
		self.setWindowTitle(self.title)
		#self.setMinimumSize(1200, 500)

		# creating MainWidget widget and setting it as central
		self.main_widget = MainWidget(parent=self)
		
		main_window_size = self.main_widget.prefs.file["state"]["main_window"]["size"]
		main_window_pos = self.main_widget.prefs.file["state"]["main_window"]["pos"]

		self.resize(main_window_size[0], main_window_size[1])
		self.move(main_window_pos[0], main_window_pos[1])

		self.setCentralWidget(self.main_widget)

	def create_menu_bar(self):
		# filling up a menu bar
		bar = self.menuBar()
		
		file_menu = bar.addMenu('&File')
	
		settings_action = self.create_qaction(
			menu=file_menu, 
			text="Settings", 
			shortcut="Ctrl+S", 
			callback=self.main_widget.settings_dialog)

		close_action = self.create_qaction(
			menu=file_menu, 
			text="Close", 
			shortcut="Ctrl+Q", 
			callback=self.close_app)

		# Edit menu
		edit_menu = bar.addMenu('&Edit')


		# About menu
		about_menu = bar.addMenu('&About')

		about_me_action = self.create_qaction(
			menu=about_menu, 
			text="About diet", 
			shortcut="Ctrl+d", 
			callback=self.main_widget.create_about_me_dialog)

	def create_qaction(self, menu, text: str, shortcut: str="", callback: callable=lambda: print("No callback")):
		action = QAction(self)

		if shortcut != "": # If the shortcut isn't empty
			mnemo = shortcut.split("+")[1] # Split by + and get the key (a, b, c)
			
			shortcut_text = text.replace(mnemo, f"&{mnemo}", 1) # Underline the shortut letter 

		action.setText(shortcut_text)
		action.setShortcut(shortcut)

		menu.addAction(action)
		
		action.triggered.connect(callback)

		return action

	def close_app(self):
		main_window_geometry = self.geometry()

		main_window_pos = main_window_geometry.x(), main_window_geometry.y() - 64
		main_window_size = main_window_geometry.width(), main_window_geometry.height()

		self.main_widget.prefs.write_prefs("state/main_window/size", main_window_size)
		self.main_widget.prefs.write_prefs("state/main_window/pos", main_window_pos)

		self.close()
		sys.exit()

	def closeEvent(self, event):
		self.close_app()
		event.accept()


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super(MainWidget, self).__init__()

		self.parent = parent
		# self.portions = ["Huge portion", "Big portion", "Medium portion", "Small portion", "Tiny portion", "No portion"]

		self.meals = ["Breakfast", "Lunch", "Dinner", "Others"]
		self.meals_colors = ["#e78f3d", "#33cea9", "#2279cd", "#d73b4f"]


		self.foods = ["Vegetables", "Grains", "Fruits", "Protein", "Dairy", "Oils and fats", "Other"]
		self.foods_colors = ["#99ca53", "#209fdf", "#6d5fd5", "#f6a625", "#e4e984", "#b5521a", "#e13131"]
		self.ideal_line_color = "#43D052"

		self.widgets = {
			"create_user_button": [], 
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
		}

		self.advices_list = ("You need to eat more {}.", "You are eating extra {}.", "You are eating the perfect rate of {}.")
		self.advices_values = (lambda: self.get_advices("low"), lambda: self.get_advices("extra"), lambda: self.get_advices("perfect"))

		self.init_prefs()
		self.create_window()

	@property
	def today(self):
		return datetime.datetime.now().strftime('%Y-%m-%d')

	@property
	def current_user(self):
		return self.prefs.file["current_user"]

	@property
	def gender(self):
		return self.prefs.file["users"][self.current_user]["gender"]

	@property
	def age(self):
		return self.prefs.file["users"][self.current_user]["age"]

	@property
	def weight(self):
		return self.prefs.file["users"][self.current_user]["weight"]

	@property
	def height(self):
		return self.prefs.file["users"][self.current_user]["height"]

	@property
	def activity(self):
		return self.prefs.file["users"][self.current_user]["activity"]

	@property
	def BMR(self):
		return self.prefs.file["users"][self.current_user]["BMR"]

	@property
	def user_nutrition(self):
		if not "nutrition" in self.prefs.file["users"][self.current_user]:
			self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{to_snake_case(meal):{"total": 0, **{to_snake_case(food):0 for food in self.foods}} for meal in self.meals}})

		return self.prefs.file["users"][self.current_user]["nutrition"]


	@property
	def nutrition_info(self):
		return self.prefs.file["nutrition"]

	def init_prefs(self):	
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
					e:[528, 530] for e in range(len(self.meals))
				}, 
				"stats_splitter": [200, 200], 
				"calories_per_day_comobox_checked": 0, 

			}, 
			"tabs": {
				"selected_tab": 0, 
				"selected_meal_tab": 0, 
			}, 
			"nutrition": PREFS.read_prefs_file("Prefs/nutrition"), 
			"users": {}, 
		}
		
		self.prefs = PREFS.PREFS(prefs, filename="Prefs/settings")

		if self.current_user == "": return

	def create_window(self):
		##### Creating window
		self.app = QApplication(sys.argv)

		# Setting grid
		self.setLayout(QGridLayout())

		# FONTS
		# QFontDatabase.addApplicationFont(':/impact.ttf')

		# First frame
		self.main_frame()

	def update_calories(self):
		calories = self.prefs.file["users"][self.current_user]["nutrition"][self.today]["total"] 

		if calories + 30 < self.BMR:
			message = "You have {} calories left."
		elif calories - 30 > self.BMR:
			message = "You are {} calories <strong>over</strong> the daily rate."
		else:
			message = "You have ate the perfect rate of calories."

		calories_left = round(self.BMR - calories, 3)

		self.widgets["calories_label"][-1].setText(message.format(abs(calories_left)))

	def update_splitters(self):
		self.widgets["stats_splitter"][-1].setSizes(self.prefs.file["state"]["stats_splitter"])
		
		for e, meal_tab in enumerate(self.widgets["meal_tabs"]):
			meal_tab.widget(0).setSizes(self.prefs.file["state"]["meal_tabs_splitters"][str(e)])

	def update(self):
		if not self.update_tabs(): # update_tabs returns False means that there is no 'current_user' so all stats should be cleaned.
			return False

		self.update_current_user_label()
		self.update_bar_chart()
		self.update_pie_chart()
		self.update_advices_tab()
		self.update_splitters()

	def update_tabs(self):
		if self.current_user == "":
			self.clear_user_widgets()
			self.create_add_user_button()
			return False

		if len((create_user_button := self.widgets["create_user_button"])) > 0:
			create_user_button[-1].setParent(None)
			create_user_button = []
			self.create_stats()
			return
			
		# Update calories lable with the new user daily calories
		self.update_calories()
	
		self.widgets["stats_splitter"][-1].widget(1).setParent(None)
		self.widgets["meal_tabs"] = []

		meal_tabs = self.create_meal_tabs()

		self.widgets["stats_splitter"][-1].addWidget(meal_tabs)

		return True

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

	def create_add_user_button(self):
		create_user_button = QPushButton("Create user")
		create_user_button.setFixedHeight(50)
		create_user_button.clicked.connect(self.add_user_dialog_and_hide_button)

		self.layout().addWidget(create_user_button, 2, 0, 1, 0)
		self.widgets["create_user_button"].append(create_user_button)

	def add_user_dialog_and_hide_button(self):
		accepted_rejected = self.add_user_dialog()

		if accepted_rejected == True:
			self.widgets["create_user_button"][-1].setParent(None)
			self.widgets["create_user_button"] = []
			self.create_tabs()

	def get_meals_totals_by_date(self):
		result = [[] for i in self.meals]

		for date_count, (date, date_info) in enumerate(self.user_nutrition.items()):
			for meal, food in date_info.items():
				if meal == "total": # That meal total is equal to the sum of all meals
					continue

				result[self.meals.index(snake_case_to_text(meal))].append(food["total"]) # This food total is the sum of only one meal

		return result

	def get_foods_totals(self, date: str=None):
		"""Sum all foods total from every food (in a certain date).
		
		Args:
			date (str, optional=self.today): A date to search in (2021-08-22, 2021-08-23, 2021-08-24)
		"""
		if date is None:
			date = self.today

		result = {food:0 for food in self.foods}

		for meal, meal_info in self.user_nutrition[date].items():
			if meal == "total": continue

			for food, food_val in meal_info.items():
				if food == "total": continue

				result[snake_case_to_text(food)] += food_val

		return result

	def get_foods_totals_by_date(self):
		result = [[] for i in self.foods]

		for date_count, date in enumerate(self.get_dates()):
			for e, (food, food_total) in enumerate(self.get_foods_totals(date=date).items()):
				result[e].append(food_total)

		return result

	def get_foods_by_meal(self, meal):
		result = {}

		for food, portion_value in self.user_nutrition[self.today][to_snake_case(meal)].items():

			if food == "total":	continue # this meal total is equal to the sum of all meals (breakfast, lunch, etc)
			
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
		gender = self.gender
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
			result += eval(self.nutrition_info["portion_max"].format(food_ideal_portion))

		return result * len(self.meals) if sum_all_meals else result

	def calculate_meal_total(self):
		meals_total_keys = []
		meals_total_values = []

		for meal, food_info in self.user_nutrition[self.today].items():
			if meal == "total":	continue # this meal total is equal to the sum of all meals (breakfast, lunch, etc)

			meal_total = 0
			for food_total in self.get_foods_by_meal(meal).values():
				meal_total += food_total

			meals_total_keys.append(f'users/{self.current_user}/nutrition/{self.today}/{meal}/total')
			meals_total_values.append(meal_total)

		self.prefs.write_multiple_prefs(meals_total_keys, meals_total_values)

	def calculate_day_total(self):
		"""First call calculate_meal_total to calculate the total.
		"""
		day_total = 0

		for meal, food_info in self.user_nutrition[self.today].items():
			if meal == "total":	continue # this meal total is equal to the sum of all meals (breakfast, lunch, etc)

			day_total += food_info["total"]

		self.prefs.write_prefs(f'users/{self.current_user}/nutrition/{self.today}/total', day_total)

	def create_meal_tabs(self):
		def on_slider_changed(value, meal, food, slider):			
			nonlocal sleep_time

			sleep_time = time.time() - sleep_time

			self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}/{to_snake_case(meal)}/{to_snake_case(food)}", value)
			
			# slider_pos = slider.mapToGlobal(QPoint(0, 0))

			self.calculate_meal_total()
			self.calculate_day_total()
			
			self.update_calories()

			self.update_pie_chart()
			update_meal_chart(meal)

			sleep_time = time.time()
		
		def create_bar_series():
			series =  QHorizontalStackedBarSeries()

			for color, (food, food_value) in zip(self.foods_colors, self.get_foods_by_meal(meal).items()):
				food_set = QBarSet(snake_case_to_text(food))
				food_set.setColor(QColor(color))

				food_set << food_value

				series.append(food_set)

			return series

		def create_meal_chart(meal):
			bar_series = create_bar_series()

			line_series = QLineSeries()
			line_series.setName("Ideal")

			line_series_pen = line_series.pen()
			line_series_pen.setWidth(2)
			line_series_pen.setColor(QColor(self.ideal_line_color))
			line_series.setPen(line_series_pen)

			ideal_line_value = self.get_ideal_meal_portions()[to_snake_case(meal)]

			line_series.append(QPoint(int(ideal_line_value), -10))
			line_series.append(QPoint(int(ideal_line_value), 10))

			chart = QChart()

			chart.addSeries(bar_series)
			chart.addSeries(line_series)

			chart.setTitle(f"Calories by food ({meal})")
			chart.setAnimationOptions(QChart.SeriesAnimations)

			axis = QBarCategoryAxis()
			#axis.setTitleText("Date")
			#axis.append([f"<strong>{meal}</strong>"])

			axisY = QBarCategoryAxis()
			axisY.append([f"<strong>{meal}</strong>"])
			
			chart.addAxis(axisY, Qt.AlignLeft)
			line_series.attachAxis(axisY)
			bar_series.attachAxis(axisY)

			#axisY.setRange(dates[0], dates[-1])

			axisX = QValueAxis()
			axisX.setTitleText("Calories")

			chart.addAxis(axisX, Qt.AlignBottom)
			line_series.attachAxis(axisX)
			bar_series.attachAxis(axisX)
			axisX.setRange(0, self.get_portions_max())					

			chart.axisX().setGridLineVisible(False)
			chart.axisY().setGridLineVisible(False)

			chart_view = QChartView(chart)
			chart_view.setRenderHint(QPainter.Antialiasing)

			return chart_view, bar_series

		def update_meal_chart(meal):
			series = meal_charts_series[meal]
			series.clear()

			for color, (food, food_value) in zip(self.foods_colors, self.get_foods_by_meal(meal).items()):
				food_set = QBarSet(snake_case_to_text(food))
				food_set.setColor(QColor(color))

				food_set << food_value

				series.append(food_set)

		def on_tab_change(index):
			nonlocal first_time

			if first_time:
				first_time = False
				return
			
			self.prefs.write_prefs("tabs/selected_meal_tab", index)
			#self.animate_charts()
			#update_meal_chart(meal)

		def on_splitter_moved(pos, _, index):
			self.prefs.write_prefs(f"state/meal_tabs_splitters/{index}", meal_tabs_splitters[index].sizes())

		first_time = True
		sleep_time = time.time() 

		meal_tabs = VerticalTabWidget()
		meal_tabs.currentChanged.connect(on_tab_change)

		meal_charts_series = {}
		meal_tabs_splitters = []

		for e, meal in enumerate(self.meals): # Breakfast, lunch, dinner and extra
			meal_tab = QSplitter(Qt.Horizontal)
			meal_tab.splitterMoved.connect(lambda pos, _, splitter_index=e: on_splitter_moved(pos, _, splitter_index))
			
			meal_tab_sliders = QWidget()
			meal_tab_sliders.setLayout(QFormLayout())

			for food, food_ideal_portion in zip(self.foods, self.get_ideal_portions().values()): # Vegetables, whole grains, fruits, etc
				slider = QSlider(Qt.Horizontal)
				slider.setFocusPolicy(Qt.StrongFocus)
				slider.setTickPosition(QSlider.NoTicks)
				
				slider_max = eval(self.nutrition_info["portion_max"].format(food_ideal_portion))

				slider.setMinimum(0)
				slider.setMaximum(int(slider_max))
				
				slider.setPageStep(int(slider_max // 5))
				slider.setSingleStep(int(slider_max // 5))

				slider_value = self.user_nutrition[self.today][to_snake_case(meal)][to_snake_case(food)]
				
				slider.setValue(slider_value)
				slider.valueChanged.connect(lambda value, meal=meal, food=food, slider=slider: on_slider_changed(value, meal, food, slider))

				meal_tab_sliders.layout().addRow(food, slider)

			meal_tab.addWidget(meal_tab_sliders)
			
			meal_chart, meal_chart_series = create_meal_chart(meal)
			meal_charts_series[meal] = meal_chart_series
			
			meal_tab.addWidget(meal_chart)
			meal_tab.setSizes(self.prefs.file["state"]["meal_tabs_splitters"][f"{e}"])
			meal_tabs_splitters.append(meal_tab)

			meal_tabs.addTab(meal_tab, meal)

		meal_tabs.setCurrentIndex(self.prefs.file["tabs"]["selected_meal_tab"])

		self.update_calories()
		self.update_bar_chart()
		self.update_pie_chart()

		self.widgets["meal_tabs"].append(meal_tabs)
		return meal_tabs

	def get_advices(self, kind: str):
		food_data = self.get_all_foods_totals_today()
		ideal_food_data = self.get_ideal_portions()

		food_list = []

		for (food, food_value), ideal_food_value in zip(food_data.items(), ideal_food_data.values()):
			#print(food, food_value, ideal_food_value)

			if kind == "low":
				food_difference = ideal_food_value - food_value 
			elif kind == "extra":
				food_difference = food_value - ideal_food_value
			elif kind == "perfect":
				food_difference = abs(food_value - ideal_food_value)

			condition = food_difference > 10 if kind != "perfect" else food_difference < 10
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

		return snake_case_to_text(result)

	def update_advices_tab(self):
		advices_list = self.advices_list
		advices_values = self.advices_values
		advices_tab_layout = self.widgets["advices_tab"][-1].layout()

		advices_labels_list = [advices_tab_layout.itemAt(indx).widget() for indx in range(advices_tab_layout.count())]

		## Update widgets ##
		not_empty_count = 0
		for advice, advice_value, advice_label in zip(advices_list, advices_values, advices_labels_list):
			advice_value = advice_value()

			if not advice_value:
				advice_label.setText("")
			else:
				advice_label.setText(advice.format(advice_value))
				not_empty_count += 1

		if not_empty_count == 0: # Means all labels are emtpy
			advices_tab_layout.itemAt(0).setText("It seems there are no advices to give you yet.")
			#self.widgets["advices_labels_list"][0].setAlignment(Qt.AlignTop)
			#self.widgets["advices_labels_list"][0].setStyleSheet("font-weight: bold; font-size: 16px;")

	def create_advices_tab(self):
		## Create QWidget to contain all advices tab. ##
		advices_tab = QWidget()
		advices_tab.setLayout(QFormLayout())

		advices_list = self.advices_list
		advices_values = self.advices_values

		## Create widgets ##
		not_empty_count = 0
		for advice, advice_value in zip(advices_list, advices_values):
			advice_value = advice_value()
			advice_label = QLabel()
			advice_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #3A3A3A;")

			if not advice_value:
				advice_label.setText("")
			else:
				advice_label.setText(advice.format(advice_value))
				not_empty_count += 1

			#advice_label.setStyleSheet("padding: 0px 0px 0px 0px;")

			# Position widgets into advices_tab layout
			advices_tab.layout().addRow(advice_label)

			## Add widgets to self.widgets dictionary ##

		if not_empty_count == 0: # Means all labels are emtpy
			advices_tab.layout().itemAt(0).setText("It seems there are no advices to give you yet.")

		self.widgets["advices_tab"].append(advices_tab)		
		return advices_tab

	def get_all_foods_totals_today(self):
		"""Get the total of all fods of today's current user.

		Return:
			dict: {"vegetables": 124, "grains": 94, ...}
		"""
		result = {}

		for meal, meal_data in self.user_nutrition[self.today].items():
			if meal == "total":
				continue
			
			for food, portion_value in meal_data.items():
				if food == "total":
					continue

				if not food in result:
					result[food] = 0

				result[food] += portion_value

		return result		

	def update_pie_chart(self):
		chart = self.widgets["charts"]["pie"][-1]

		series = self.widgets["charts_series"]["pie"][-1]
		series.clear()

		self.create_slices_pie(series)

	def create_slices_pie(self, series):
		for color, (food, food_total) in zip(self.foods_colors, self.get_all_foods_totals_today().items()):
			_slice = series.append(food.replace("_", " ").capitalize(), food_total)
			_slice.setBrush(QColor(color))
			if food_total > 0: _slice.setLabelVisible() # Otherwise there will be a lot of labels over

		return series

	def create_pie_chart(self):
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
		calories_label.setStyleSheet("font-size: 30px;")
		calories_label.setAlignment(QtCore.Qt.AlignCenter)

		self.widgets["calories_label"].append(calories_label)
		self.update_calories()

		return calories_label

	def update_bar_chart(self):
		chart = self.widgets["charts"]["bar"][-1]

		series = self.widgets["charts_series"]["bar"][-1]
		series.clear()

		dates = self.get_dates()

		self.create_bar_series(series)
		
		axis = QBarCategoryAxis()
		axis.setTitleText("Date")
		axis.append(dates)

		chart.setAxisX(axis, series)

		max_calories = dict_max(self.user_nutrition) # This will find the biggest value inside all nutrition dates
		chart.axisY().setRange(0, max_calories + 500 if max_calories > self.BMR else self.BMR + 500)

	def get_dates(self):
		dates = []

		for date in self.user_nutrition.keys():
			dates.append(date)

		return dates

	def create_bar_series(self, bar_series=QStackedBarSeries()):
		def on_series_hoverd(point, state):
			if not point:
				return
					
		## Use meals data if calories_per_day_comobox_checked else use foods data ##
		if self.prefs.file["state"]["calories_per_day_comobox_checked"] == 0:
			data = self.get_meals_totals_by_date() # Data
			colors = self.meals_colors # Colors
			names_list = self.meals # A list for the bar set names
		elif self.prefs.file["state"]["calories_per_day_comobox_checked"] == 1:
			data = self.get_foods_totals_by_date() # Data
			colors = self.foods_colors # Colors
			names_list = self.foods # A list for the bar set names

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
		line_series_pen.setColor(QColor(self.ideal_line_color))
		line_series.setPen(line_series_pen)

		line_series.append(QPoint(-1, int(self.BMR)))
		line_series.append(QPoint(10, int(self.BMR)))

		## Add series to chart ##
		chart.addSeries(bar_series)
		chart.addSeries(line_series)
		chart.setTitle("Calories along the days")
		chart.setAnimationOptions(QChart.SeriesAnimations)

		axisX = QBarCategoryAxis()
		axisX.setTitleText("Date")
		axisX.append(dates)
		
		#chart.createDefaultAxes()
		
		chart.addAxis(axisX, Qt.AlignBottom)
		
		line_series.attachAxis(axisX)
		bar_series.attachAxis(axisX)

		axisX.setRange(dates[0], dates[-1])

		axisY = QValueAxis()
		chart.addAxis(axisY, Qt.AlignLeft)
		line_series.attachAxis(axisY)
		bar_series.attachAxis(axisY)

		max_calories = dict_max(self.user_nutrition) # This will find the biggest value inside all nutrition dates
		axisY.setRange(0, max_calories + 500 if max_calories > self.BMR else self.BMR + 500)

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

	def create_calories_per_day_tab(self):
		def on_combobox_change():
			index = comboboxes_group.checkedId()
			index = abs(index) - 2 # if index 0 id is -2, that's why i subtract two from index
			
			print(index)

			self.prefs.write_prefs("state/calories_per_day_comobox_checked", index)

			self.update_bar_chart()

		## calories_per_day_tab Widget ##
		calories_per_day_tab = QWidget()
		calories_per_day_tab.setLayout(QVBoxLayout())

		## By meals, by food comboboxes ##
		comboboxes_widget = QWidget()
		comboboxes_widget.setLayout(QVBoxLayout())

		comboboxes_group = QButtonGroup()
		comboboxes_group.idToggled.connect(on_combobox_change)
		comboboxes_group.setExclusive(True)

		by_meals_radiobutton = QRadioButton("By meals")
		by_food_radiobutton = QRadioButton("By foods")
		by_food_radiobutton.setStyleSheet("margin: 0px 0px 0px 0px;")

		comboboxes_widget.layout().addWidget(by_meals_radiobutton)	
		comboboxes_widget.layout().addWidget(by_food_radiobutton)

		if (calories_per_day_comobox_checked := self.prefs.file["state"]["calories_per_day_comobox_checked"]) == 0:
			by_meals_radiobutton.setChecked(True)
			#by_meals_radiobutton.setChecked(True)
		elif calories_per_day_comobox_checked == 1:
			by_food_radiobutton.setChecked(True)
			#by_meals_radiobutton.setChecked(True)

		comboboxes_group.addButton(by_meals_radiobutton)
		comboboxes_group.addButton(by_food_radiobutton)

		## Bar chart ##
		bar_chart = self.create_bar_chart() 

		## Position widgets on calories_per_day_tab ##
		calories_per_day_tab.layout().addWidget(comboboxes_widget)
		calories_per_day_tab.layout().addWidget(bar_chart)

		return calories_per_day_tab

	def create_tabs(self):
		def on_tab_change(index):
			nonlocal first_time

			if first_time:
				first_time = False
				return

			self.prefs.write_prefs("tabs/selected_tab", index)
			if index == 1:
				self.update_bar_chart()
				self.animate_charts()
			elif index == 2:
				self.update_advices_tab()
	
		def on_splitter_moved(pos, index):
			self.prefs.write_prefs(f"state/stats_splitter", stats_splitter.sizes())

		first_time = True

		tabs = QTabWidget()
		tabs.currentChanged.connect(on_tab_change)

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
		tabs.addTab(stats_splitter, "Stats")
		tabs.addTab(calories_per_day_tab, "Calories per day")
		tabs.addTab(advices_tab, "Advices")		

		tabs.setCurrentIndex(self.prefs.file["tabs"]["selected_tab"])

		## Position tabs in main widget ##
		self.layout().addWidget(tabs, 2, 0, 1, 0)

		## Add elements to self.widgets dictionary##
		self.widgets["stats_splitter"].append(stats_splitter)
		self.widgets["tabs"].append(tabs)

	def create_current_user_label(self):
		current_user_label = QLabel(self.current_user)
		current_user_label.setStyleSheet("font-size: 30px; margin-right: 10px;")
		current_user_label.setAlignment(QtCore.Qt.AlignRight)

		self.layout().addWidget(current_user_label, 1, 1)
		self.widgets["current_user_label"].append(current_user_label)

	def update_current_user_label(self):
		current_user_label = self.widgets["current_user_label"][-1]

		current_user_label.setText(self.current_user)

	def main_frame(self):
		logo = QLabel("<strong>Diet</strong>")
		logo.setStyleSheet("font-size: 50px;")
		logo.setAlignment(QtCore.Qt.AlignCenter)

		self.layout().addWidget(logo, 0, 0, 2, 0)

		if self.prefs.file["users"] == {}:			
			self.create_add_user_button()
			return

		self.create_current_user_label()
		self.create_tabs()

	def create_warning(self, window, message: str, title: str):
		warning = QMessageBox.question(window, 
			title, 
			message, 
			QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
				
		return True if warning == QMessageBox.Yes else False

	def add_user_dialog(self, 
		default_username="Tim", 
		default_gender=None, 
		default_weight=70, 
		default_height=170, 
		default_age=25, 
		default_activity="Rarely", 
		editing=False):

		def save_config():
			if user_input.text() in self.prefs.file["users"] and not editing:
				warning = self.create_warning(dialog,   
					message="That username already exists, do you want to overwrite it?", 
					title="Already existent username", 
				)
				
				if not warning:
					return
		
			username = user_input.text()

			gender_id = abs(gender_group.checkedId()) - 2
			gender = gender_list[gender_id]
			
			age = age_spinbox.value()
			weight = weight_spinbox.value()
			height = height_spinbox.value()
			activity = activity_combobox.currentText()

			if not default_username == username and editing:
				self.prefs.write_prefs("users", rename_key_from_dict(self.prefs.file["users"], default_username, username))
				self.prefs.write_prefs("current_user", username)

			if self.current_user == "": self.prefs.write_prefs(f"current_user", username)
			
			self.prefs.write_prefs(f"users/{username}/gender", gender)
			self.prefs.write_prefs(f"users/{username}/age", age)
			self.prefs.write_prefs(f"users/{username}/weight", weight)
			self.prefs.write_prefs(f"users/{username}/height", height)
			self.prefs.write_prefs(f"users/{username}/activity", activity)

			if gender == "Male":
				BMR = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
			elif gender == "Female":
				BMR = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
			elif gender == "Non-binary":
				BMR = 267.9775 + (11.322 * weight) + (3.9485 * height) - (5.0035 * age)

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

		dialog = QDialog() # Creating dialog
		dialog.setMaximumSize(1, 1)
		
		dialog.setWindowTitle("Settings") # Setting dialog title

		dialog.setWindowModality(Qt.ApplicationModal) # True blocks its parent window
		dialog.setLayout(QFormLayout())

		## User ##
		user_input = QLineEdit(default_username)

		## Gender RadioButtons ##
		gender_list = ["Male", "Female", "Non-binary"]
		gender_group = QButtonGroup()
		gender_box = QHBoxLayout()
		
		for e, gender in enumerate(gender_list):
			gender_radiobutton = QRadioButton(gender)

			if not default_gender is None:
				if gender == default_gender:
					gender_radiobutton.setChecked(True)

			gender_group.addButton(gender_radiobutton)
			gender_box.addWidget(gender_radiobutton)

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

		## OK button ##
		ok_button = QPushButton("OK")
		ok_button.clicked.connect(save_config)

		## Position widgets ##
		#dialog.layout().addRow(label)

		dialog.layout().addRow("Username: ", user_input)
		dialog.layout().addRow("Gender: ", gender_box)
		dialog.layout().addRow("Weight: ", weight_spinbox)
		dialog.layout().addRow("Height: ", height_spinbox)
		dialog.layout().addRow("Age: ", age_spinbox)
		dialog.layout().addRow("Physical activity: ", activity_combobox)

		dialog.layout().addRow(ok_button)

		return dialog.exec_()

	def settings_dialog(self, default_tab=0):
		def create_user():
			self.add_user_dialog()
			
			dialog.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users
	
		def remove_user(user):
			warning = self.create_warning(dialog,   
				message=f"Are you sure you want to remove {user}?\nThis action cannot be undone.", 
				title=f"Remove {user}?", 
			)
				
			if not warning:
				return

			users_with_user_removed = remove_key_from_dict(self.prefs.file["users"], user)

			self.prefs.write_prefs(f"users", users_with_user_removed)
			
			if len(self.prefs.file["users"]) >= 1:
				select_user( list(self.prefs.file["users"])[0] )
			else:
				self.prefs.write_prefs("current_user", "")
				
				dialog.accept() # Close the dialog
				self.settings_dialog(default_tab=1) # Reopen to update users

		def edit_user(user):
			user_info = self.prefs.file["users"][user]
			self.add_user_dialog(
				default_username=user, 
				default_gender=user_info["gender"], 
				default_height=user_info["height"], 
				default_weight=user_info["weight"], 
				default_age=user_info["age"], 
				default_activity=user_info["activity"], 
				editing=True)
			
			dialog.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users
		
		def select_user(user):
			self.prefs.write_prefs("current_user", user)
			
			dialog.accept() # Close the dialog

			self.settings_dialog(default_tab=1) # Reopen to update users

		def save_dialog_geometry(*args, **kwargs):
			dialog_geometry = dialog.geometry()
			dialog_pos = dialog_geometry.x(), dialog_geometry.y() - 64

			dialog_size = dialog_geometry.width(), dialog_geometry.height()

			self.prefs.write_prefs("state/settings_dialog/pos", dialog_pos)
			self.prefs.write_prefs("state/settings_dialog/size", dialog_size)

		def close_event(*args, **kwargs):
			if not "nutrition" in self.prefs.file["users"][self.current_user]:
				self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{to_snake_case(meal):{"total": 0, **{to_snake_case(food):0 for food in self.foods}} for meal in self.meals}})
			else:
				if not self.today in self.user_nutrition:
					self.prefs.write_prefs(f"users/{self.current_user}/nutrition/{self.today}", {"total": 0, **{to_snake_case(meal):{"total": 0, **{to_snake_case(food):0 for food in self.foods}} for meal in self.meals}})

			save_dialog_geometry()
			self.update()
		
		def reject_event(*args, **kwargs):
			save_dialog_geometry()
			self.update()

		dialog = QDialog()
		dialog.setMinimumSize(500, 400)
		
		dialog_size = self.prefs.file["state"]["settings_dialog"]["size"]
		dialog_pos = self.prefs.file["state"]["settings_dialog"]["pos"]

		dialog.resize(dialog_size[0], dialog_size[1])
		dialog.move(dialog_pos[0], dialog_pos[1])

		dialog.setLayout(QVBoxLayout())
		dialog.setWindowTitle("Settings")

		dialog.closeEvent = close_event
		dialog.rejected.connect(close_event)
		dialog.accepted.connect(save_dialog_geometry)

		## TABS ##
		tabs = QTabWidget()
		
		## NUTRITION TAB ##
		nutrition_tab = QWidget()
		nutrition_tab.setLayout(QFormLayout())

		for food, food_ideal_portion in self.nutrition_info["ideal_portions"].items():
			food_line_edit = QLineEdit(food_ideal_portion)
			
			nutrition_tab.layout().addRow(snake_case_to_text(food), food_line_edit)

		## USERS TAB ##
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

		create_user_button = QPushButton("Add user")
		create_user_button.clicked.connect(create_user)

		users_tab.layout().addWidget(create_user_button, 1, 0)

		## ADD TABS ##
		tabs.addTab(nutrition_tab, "Ideal Portions")
		tabs.addTab(users_tab, "Users")
		tabs.setCurrentIndex(default_tab)

		dialog.layout().addWidget(tabs)

		return dialog.exec_()

	def create_checkbox(self, 
		text: str, 
		stylesheet: str="", 
		checked: bool=True, 
		callback: callable=lambda x: print(f"No callback function {x}"), 
		tooltip: str=None):
		
		checkbox = QCheckBox(text)
		checkbox.setStyleSheet(stylesheet)
		checkbox.setChecked(checked)
		
		if not tooltip is None:
			checkbox.setToolTip(tooltip)

		checkbox.toggled.connect(callback)

		return checkbox

	def create_button(self, text: str, stylesheet: str="", callback: callable=lambda x: print(f"No callback function"), tooltip: str=None):
		button = QPushButton(text)
		button.setStyleSheet(stylesheet)
		button.clicked.connect(callback)

		if not tooltip is None:
			button.setToolTip(tooltip)

		return button

	def create_spinbox(self, 
		prefix: str="", 
		suffix: str="", 
		stylesheet: str="", 
		minium: int=0, 
		maximum: int=10000, 
		value: int=0, 
		callback: callable=lambda x: print(x), 
		tooltip: str=None):
		
		spinbox = QSpinBox()
		
		spinbox.setMinimum(minium)
		spinbox.setMaximum(maximum)
		
		spinbox.setPrefix(prefix)
		spinbox.setSuffix(suffix)

		spinbox.setValue(value)
		spinbox.setStyleSheet(stylesheet)

		if not tooltip is None:
			spinbox.setToolTip(tooltip)

		spinbox.valueChanged.connect(callback)

		return spinbox

	def create_about_me_dialog(self):
		######## SET UP DIALOG ########
		dialog = QDialog() # Creating dialog
		
		dialog.setWindowTitle("About diet") # Setting dialog title
		#dialog.setStyleSheet("background: #81dbe8; color: black") # Setting dialog styling
		dialog.setWindowModality(True) # False blocks its parent window
		dialog.setLayout(QGridLayout())

		## Adding widgets ##
		about_label = QLabel("Diet is a simple GUI app for the Timathon code jam, written in Python using PyQt5.<br/><br/>Contact me: <br/>&nbsp;&nbsp;&nbsp;&nbsp;Discord: patitotective#0127<br/>&nbsp;&nbsp;&nbsp;&nbsp;Mail: <a href='mailto:cristobalriaga@gmail.com' style='color: #FF5794'>cristobalriaga@gmail.com</a>", dialog)
		about_label.setOpenExternalLinks(True)

		about_prefs_label = QLabel("<strong>Diet </strong> uses <a href='https://patitotective.github.io/PREFS' style='color: #FF5794'>PREFS python library</a> to store the settings.")

		about_prefs_label.setStyleSheet("margin: 5px 0px 0px 0px;")
		about_prefs_label.setOpenExternalLinks(True)

		source_code_link = QLabel("<a href='https://github.com/Patitotective/password_generator_gui' style='color: #FF5794'>Source code</a>", dialog)
		source_code_link.setOpenExternalLinks(True)

		dialog.layout().addWidget(about_label, 0, 0, 1, 1)
		dialog.layout().addWidget(about_prefs_label, 1, 0, 1, 1)
		dialog.layout().addWidget(QLabel(), 2, 0, 1, 1)
		dialog.layout().addWidget(source_code_link, 3, 1)
		dialog.layout().addWidget(QLabel("v0.1"), 3, 0)

		self.about_me_dialog = dialog

		dialog.exec_()


class TabBar(QTabBar):
	def tabSizeHint(self, index):
		s = QTabBar.tabSizeHint(self, index)
		s.transpose()
		return s

	def paintEvent(self, event):
		painter = QStylePainter(self)
		opt = QStyleOptionTab()

		for i in range(self.count()):
			self.initStyleOption(opt, i)
			painter.drawControl(QStyle.CE_TabBarTabShape, opt)
			painter.save()

			s = opt.rect.size()
			s.transpose()
			r = QtCore.QRect(QtCore.QPoint(), s)
			r.moveCenter(opt.rect.center())
			opt.rect = r

			c = self.tabRect(i).center()
			painter.translate(c)
			painter.rotate(90)
			painter.translate(-c)
			painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
			painter.restore()


class VerticalTabWidget(QTabWidget):
	def __init__(self, *args, **kwargs):
		QTabWidget.__init__(self, *args, **kwargs)
		self.setTabBar(TabBar())
		self.setTabPosition(QTabWidget.West)


def remove_key_from_dict(my_dict: dict, key: str) -> dict:
	return {k:v for k, v in my_dict.items() if k != key}

def rename_key_from_dict(my_dict: dict, key: str, new_key: str) -> dict:
	return {new_key if k == key else k:v for k, v in my_dict.items()}

def to_snake_case(string: str) -> str:
	return string.replace(" ", "_").lower()

def snake_case_to_text(string: str) -> str:
	return string.replace("_", " ").capitalize()

def dict_max(my_dict: dict) -> float:
	num_list = []

	for i in my_dict.values():
		if isinstance(i, float) or isinstance(i, int):
			num_list.append(i)
		elif isinstance(i, dict):
			num_list.append(dict_max(i))

	return max(num_list)

def init_app():
	app = QApplication(sys.argv)
	
	mainwindow = MainWindow("Diet")
	mainwindow.show()
	sys.exit(app.exec_())

def main():
	init_app()

if __name__ == '__main__':
	main()
