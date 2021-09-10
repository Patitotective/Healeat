import random
from PyQt5.QtWidgets import QWidget, QSizePolicy, QLayout, QAction
import re
import ast
from enum import Enum, auto

OPERATORS = ("+", "-", "*", "/")
GOODLOOKING_OPERATORS = ("+", "−", "×", "÷")

GOODLOOKING_OPERATOR_TO_OPERATOR = {goodlooking_operator:operator for goodlooking_operator, operator in zip(GOODLOOKING_OPERATORS, OPERATORS)}
OPERATOR_TO_GOODLOOKING_OPERATOR = {val:key for key, val in GOODLOOKING_OPERATOR_TO_OPERATOR.items()}

class StatementTypes(Enum):
	"""Types of python expressions: variable, number or operator"""

	VARIABLE = auto()
	NUMBER = auto()
	OPERATOR = auto()
	UNKNOWN = auto()

def expression_to_goodlooking_expression(expression: str):
	result = []

	for statement, statement_type in split_expression(expression):
		value = statement
		if statement_type == StatementTypes.OPERATOR:
			value = OPERATOR_TO_GOODLOOKING_OPERATOR[statement]
		elif statement_type == StatementTypes.VARIABLE:
			value = snake_case_to_sentence_case(statement)

		result.append(value)

	return " ".join(result) 

def get_statement_type(statement: str, operators: tuple or list=OPERATORS) -> StatementTypes:
	if statement.replace(".", "").isdigit():
		return StatementTypes.NUMBER
	elif statement in operators:
		return StatementTypes.OPERATOR
	elif statement.isalpha():
		return StatementTypes.VARIABLE

	return StatementTypes.UNKNOWN

def split_expression(expression: str, include_type: bool=True, operators: tuple or list=OPERATORS) -> list:    
	expression = ''.join(expression.split()) # Remove all spaces

	operators_in_string = [f"\\{operator}" for operator in operators if operator in expression]

	if operators_in_string == []:
		return [[expression, get_statement_type(expression, operators=operators)]]

	re_expression = f"({'|'.join(operators_in_string)})"
	statements = re.split(re_expression, expression)

	result = []

	for statement in statements:
		if statement == "": continue
		
		if include_type:
			statement_type = get_statement_type(statement, operators=operators)
			result.append([statement, statement_type])
			continue

		result.append(statement)

	return result

def check_syntax(expression: str):
	if "".join(expression.split()) == "": 
		return False

	try:
		ast.parse(expression)
	except SyntaxError:
		return False
	
	return True

def create_qaction(menu, text: str, shortcut: str="", callback: callable=lambda: print("No callback"), parent=None) -> QAction:
	"""This function will create a QAction and return it"""
	action = QAction(parent) # Create a qaction in the window (self)

	action.setText(text) # Set the text of the QAction 
	action.setShortcut(shortcut) # Set the shortcut of the QAction

	menu.addAction(action) # Add the action to the menu
	
	action.triggered.connect(callback) # Connect callback to callback argument

	return action # Return QAction

def create_horizontal_line(height: int=2, stylesheet: str="background-color: #c0c0c0;"):
	line = QWidget()
	line.setFixedHeight(height)
	line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
	line.setStyleSheet(stylesheet)

	return line

def get_widgets_from_layout(layout: QLayout, widget_type: QWidget=QWidget, exact_type: bool=False) -> iter:
	for indx in range(layout.count()):
		widget = layout.itemAt(indx).widget()
		
		if not isinstance(widget, widget_type) and not exact_type:
			continue
		elif not type(widget) is widget_type and exact_type:
			continue

		yield widget

def get_widget_from_layout(layout: QLayout, widget_index: int, widget_type: QWidget=QWidget, exact_type: bool=False) -> QWidget:
	result = list(get_widgets_from_layout(layout, widget_type, exact_type))[widget_index]

	return result

def map_widgets_from_layout(layout: QLayout, map_func: callable, widget_type: QWidget=QWidget, exact_type: bool=False) -> None:
	for widget in get_widgets_from_layout(layout, widget_type, exact_type):
		map_func(widget)

	return None

def remove_elements_from_list(my_list: list, elements_to_remove: list) -> list:
	result = list(my_list)

	for ele in elements_to_remove:
		result.remove(ele)

	return result

def choose_random_from_list(my_list: list, elements_to_choose: int):
	result = []

	for _ in range(elements_to_choose):
		available_choices = remove_elements_from_list(my_list, result)

		result.append(random.choice(available_choices))

	return result

def remove_key_from_dict(my_dict: dict, key: str) -> dict:
	return {k:v for k, v in my_dict.items() if k != key}

def rename_key_from_dict(my_dict: dict, key: str, new_key: str) -> dict:
	return {new_key if k == key else k:v for k, v in my_dict.items()}

def snake_case_to_sentence_case(string: str) -> str:
	string = string.replace("_", " ")

	# Means if all the characters in the string are upper
	# Do not capitalize it
	if not any([True for i in string if i.isupper()]):
		string = string.capitalize()

	return string

def dict_max(my_dict: dict) -> float:
	num_list = []

	for i in my_dict.values():
		if isinstance(i, float) or isinstance(i, int):
			num_list.append(i)
		elif isinstance(i, dict):
			num_list.append(dict_max(i))

	return max(num_list)
