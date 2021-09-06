from PyQt5.QtWidgets import QDialog, QLabel, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

def create_instructions_dialog(title: str="Instructions"):
	dialog = QDialog()
	dialog.setLayout(QVBoxLayout())

	tabs = QTabWidget()

	## Start tab ##
	start_tab = QWidget()
	start_tab.setLayout(QVBoxLayout())

	start_tab_label = QLabel(
	"""Welcome to **Healeat**!\\
	**Healeat** is a nutritional tracker _GUI_ application to manage your diet.\\
	\\
	First of all start creating a new user, there you will need to set an username, \\
	your sex, age, weight, height and your physical activity. It will calculate \\
	your daily calories rate.
	\\
	
	"""
	)
	
	start_tab_label.setTextFormat(Qt.MarkdownText)

	start_tab.layout().addWidget(start_tab_label)

	## Calories per day tab ##

	## Advices tab ##

	## Settings ##

	tabs.addTab(start_tab, "Start")

	dialog.layout().addWidget(tabs)

	return dialog.exec_()