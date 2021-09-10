from PyQt5.QtWidgets import QDialog, QLabel, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from scrollarea import ScrollArea

SOURCES = (
	"https://www.who.int/news-room/fact-sheets/detail/healthy-diet", 
	"https://wholegrainscouncil.org/sites/default/files/atoms/files/WG_HowMuch.pdf", 
	"https://www.health.harvard.edu/blog/how-much-protein-do-you-need-every-day-201506188096", 
	"https://www.health.harvard.edu/blog/dairy-health-food-or-health-risk-2019012515849", 
	"https://healthfully.com/how-much-oil-should-you-eat-12681816.html", 
	"https://www.bodybuilding.com/fun/fats_calculator.htm", 
	"https://www.nia.nih.gov/health/usda-food-patterns", 
	"https://www.nia.nih.gov/health/know-your-food-groups", 
	"https://www.healthline.com/nutrition/27-health-and-nutrition-tips", 
)

def create_instructions_dialog(ignore=None, title: str="Instructions", meals=(), foods=(), parent=None):
	"""
	Notes:
		&#8203; character is (an emtpy character) used because <hr> tag cannot have a tag after it.
	"""
	dialog = QDialog(parent)
	dialog.setLayout(QVBoxLayout())
	dialog.setWindowTitle(title)

	tabs = QTabWidget()

	## Start tab ##
	start_tab_label = QLabel(
	f"""Welcome to <b>Healeat</b>!<br>
	<b>Healeat</b> is a nutritional tracker <i>GUI</i> application to manage your diet.
	<hr>
	Start doing the following steps:<br>
	1. Create a new user.<br>
	2. Start filling up meals calories. (<i>see calories tab for more info.</i>)
	"""
	)

	start_tab_label.setAlignment(Qt.AlignTop)

	start_tab = ScrollArea(start_tab_label)

	## Calories tab ##

	calories_label = QLabel(
	f"""<b><i>Calories sliders</i></b>
	<hr>
	&#8203;The calories sliders are located in the Main tab, there are sliders for each food on each meal.<br>
	&#8203;<b>Ideal portion: </b> the ideal portion of each food is located on the middle of the slider.
	&#8203;<br>You can modify the ideal portion for each specific portion in the nutrition tab on settings (<i>see settings tab.</i>).
	"""
	)

	calories_label.setAlignment(Qt.AlignTop)
	#calories_label.setWordWrap(True)

	calories_tab = ScrollArea(calories_label)

	## Calories per day tab ##

	## Advices tab ##

	## Settings tab ##
	settings_label = QLabel(
	f"""<b><i>Open settings</i></b>
	<hr>
	To open the settings dialog, press <i>Ctrl+S</i> (after closing this dialog) or go to the menu bar, click Edit and Settings.<br>
	<br>
	<b><i>Ideal portions</b></i>
	<hr>
	You will be able to modify the ideal portion for each food <br>
	by adding, removing or changing each statement on the expression.<br>
	<i>Expressions could be like: </i><br>
	<i>1.7 × Weight × 3.0</i><br>
	<i>Height × Age</i><br>

	<span style='font-size: 13px; font-style: italic;'>The ideal portions affect all users.</span><br>
	
	<b><i>Users</i></b>
	<hr>
	Add, remove or edit users. Each user will have it's own data, this way you can manage multiple diets.<br>

	""")

	settings_label.setAlignment(Qt.AlignTop)

	settings_tab = ScrollArea(settings_label)	
	## Sources tab ##
	sources_label = QLabel(
	f"""<b><i>Sources</i></b>
	<hr>
	&#8203;{''.join((f'<a href="{source}">{source}</a><br>' for source in SOURCES))}
	""")

	sources_label.setOpenExternalLinks(True)
	sources_label.setAlignment(Qt.AlignTop)

	source_tab = ScrollArea(sources_label)

	## Glossary tab ##
	glossary_label = QLabel(
	f"""<b><i>BMR</b></i>
	<hr>
	Basal metabolic rate is the number of calories your body needs to accomplish its most basic (basal) life-sustaining functions.<br>
	<br>
	<b><i>Foods</i></b>
	<hr>
	Foods are refered to:<br>
	&#8203;{''.join((f'- <i>{food}</i><br>' for food in foods))}
	<br>
	<b><i>Meals</i></b>
	<hr>
	Meals are refered to:<br>
	&#8203;{''.join((f'- <i>{meal}</i><br>' for meal in meals))}	
	""")

	glossary_label.setAlignment(Qt.AlignTop)

	glossary_tab = ScrollArea(glossary_label)	

	## Add tabs to tab widget ##

	tabs.addTab(start_tab, "Start")
	tabs.addTab(calories_tab, "Calories")
	tabs.addTab(settings_tab, "Settings")
	tabs.addTab(glossary_tab, "Glossary")
	tabs.addTab(source_tab, "Sources")

	## Warning label ##
	warning_label = QLabel("<b><span style='color: #ff2b2b;'>WARNING</span>: DO NOT GUIDE YOUR DIET ONTO THIS UNOFICIAL NUTRITIONAL TRACKER, PLEASE CONSULT YOUR DOCTOR.</b>")

	dialog.resize(warning_label.width(), 400)

	dialog.layout().addWidget(tabs)
	dialog.layout().addWidget(warning_label)

	return dialog.exec_()