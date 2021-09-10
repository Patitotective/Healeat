from PyQt5.QtWidgets import QDialog, QPushButton, QComboBox, QGridLayout, QStyle, QDoubleSpinBox, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from enum import Enum, auto

def question_dialog(
      title: str, 
      text: str, 
      icon: QIcon=QMessageBox.Question, 
      parent: QWidget=None, 
      buttons: tuple=None
   ):

   def close_event(event=None):
      """done(0) if reject is false, and set it ture.
      This will avoid infinite recursio
      """
      nonlocal rejected

      if not rejected:
         rejected = True
         msg_box.done(0)

      rejected = False

   msg_box = QMessageBox(icon, title, text, parent=parent)
   rejected = False

   if buttons is None:
      buttons = (
         (QPushButton(msg_box.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel"), 0),
         (QPushButton(QIcon("Images/minus_icon.png"), "Remove"), 2),         
         (QPushButton(QIcon("Images/plus_icon.png"), "Add"), 3),
      )

   for button, button_role in buttons:
      msg_box.addButton(button, button_role)

   msg_box.closeEvent = close_event
   msg_box.rejected.connect(close_event)

   return msg_box.exec_()

def get_item_input_dialog(items: list or tuple, title: str, current_index: int=0, parent: QWidget=None):
   dialog = QDialog(parent)
   dialog.setWindowTitle(title)
   dialog.setMaximumHeight(0)
   dialog.setMaximumWidth(0)

   dialog.setLayout(QGridLayout())

   combobox = QComboBox()
   combobox.addItems(items)
   combobox.setCurrentIndex(current_index)

   ok_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_DialogApplyButton), "OK")
   ok_btn.clicked.connect(lambda: dialog.done(1))

   cancel_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel")
   cancel_btn.clicked.connect(lambda: dialog.done(0))

   # remove_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_MessageBoxCritical), "Remove")
   # remove_btn.clicked.connect(lambda: dialog.done(2))

   dialog.layout().addWidget(combobox, 0, 0, 1, 0)
   dialog.layout().addWidget(ok_btn, 1, 2)
   dialog.layout().addWidget(cancel_btn, 1, 1)
   # dialog.layout().addWidget(remove_btn, 1, 0)

   return_value = dialog.exec_()
   value = combobox.currentText()
   # return item, ok/cancel
   return value, return_value

def get_double_input_dialog(title: str, value: float=0, minValue: float=0, maxValue: float=10000, decimals: int=1, step: float=0.1, parent: QWidget=None):
   dialog = QDialog(parent)
   dialog.setWindowTitle(title)   
   dialog.setMaximumHeight(0)
   dialog.setMaximumWidth(0)

   dialog.setLayout(QGridLayout())

   double_spinbox = QDoubleSpinBox()
   double_spinbox.setValue(value)
   double_spinbox.setMinimum(minValue)
   double_spinbox.setMaximum(maxValue)
   double_spinbox.setDecimals(decimals)
   double_spinbox.setSingleStep(step)

   ok_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_DialogApplyButton), "OK")
   ok_btn.clicked.connect(lambda: dialog.done(1))

   cancel_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel")
   cancel_btn.clicked.connect(lambda: dialog.done(0))

   # remove_btn = QPushButton(dialog.style().standardIcon(QStyle.SP_MessageBoxCritical), "Remove")
   # remove_btn.clicked.connect(lambda: dialog.done(2))

   dialog.layout().addWidget(double_spinbox, 0, 0, 1, 0)
   dialog.layout().addWidget(ok_btn, 1, 2)
   dialog.layout().addWidget(cancel_btn, 1, 1)
   # dialog.layout().addWidget(remove_btn, 1, 0)

   return_value = dialog.exec_()
   value = double_spinbox.value()
   #return value, ok/cancel
   return round(value, 1), return_value
