from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QWidget, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

class HyperlinkLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOpenExternalLinks(True)
        # self.setParent(parent)

def create_about_dialog(title: str, body: str=None, icon: QIcon=None, contact: dict=None, source_code: str=None, extra: tuple=None, parent=None):
	"""Create a simple about dialog;
	Args:
		title (str): the dialog title.
		body (str, optional=None): the about dialog body text.
		icon (QIcon, optional=None): an icon to display at left side.
		contact (dict, optional=None): a dictionary with the contact method (discord, email) as key and the username or mail in the value.
		source_code (str, optional=None): a link to display the source code
		extra (tuple, optional=None): a tuple of extra text to display.
		parent (optional=None): the dialog parent.
	"""
	dialog = QDialog(parent=parent)
	dialog.setLayout(QGridLayout())
	dialog.setMaximumSize(0, 0)
	dialog.setWindowTitle(title)

	if not icon is None:
		icon_label = QLabel()
		icon_label.setPixmap(icon.pixmap(QSize(100, 100)))

		dialog.layout().addWidget(icon_label, 0, 0)

	if not body is None:
		body_label = HyperlinkLabel(body)
		#body_label.setWordWrap(True)
		body_label.setAlignment(Qt.AlignTop)
		body_label.setTextFormat(Qt.MarkdownText)

		body_label.setStyleSheet("font-size: 16px; margin-left: 10px;")

		dialog.layout().addWidget(body_label, 0, 1)

	if not contact is None:
		contact_widget = QWidget()
		contact_widget.setLayout(QFormLayout())
		contact_widget.layout().setSpacing(1)

		contact_me_label = QLabel("Contact me: ")
		contact_me_label.setTextFormat(Qt.MarkdownText)
		contact_me_label.setStyleSheet("font-weight: bold; font-size: 16px;")

		contact_widget.layout().addRow(contact_me_label)
		for e, (contact_method, contact_name) in enumerate(contact.items()):
			contact_method_label = QLabel(f"{contact_method}: ")
			contact_name_label = HyperlinkLabel(contact_name)

			contact_method_label.setTextFormat(Qt.MarkdownText)
			contact_name_label.setTextFormat(Qt.MarkdownText)

			contact_method_label.setStyleSheet("font-size: 16px; font-style: italic;")
			contact_name_label.setStyleSheet("font-size: 16px;")
			
			contact_widget.layout().addRow(contact_method_label, contact_name_label)

		dialog.layout().addWidget(contact_widget, 1, 0, 2, 0)

	if not source_code is None:
		source_code_label = HyperlinkLabel(source_code)
		source_code_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
		source_code_label.setTextFormat(Qt.MarkdownText)
		source_code_label.setStyleSheet("font-size: 16px;")

		dialog.layout().addWidget(source_code_label, 2, 1)

	# if not icon is None:
	# 	dialog.layout().addWidget(icon, 0, 0, 0, 1)

	# if not icon is None:
	# 	dialog.layout().addWidget(icon, 0, 0, 0, 1)

	return dialog.exec_()
