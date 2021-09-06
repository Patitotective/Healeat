from PyQt5.QtWidgets import QLabel, QWidget,  QScrollBar, QScrollArea
from PyQt5.QtCore import Qt, QCoreApplication, QEvent

class ScrollArea(QScrollArea):
	def __init__(self, main_widget, parent=None):
		super().__init__()
		
		self.main_widget = main_widget

		self.horizontalScrollBar().setSingleStep(5)
		self.setWidget(main_widget)
		self.setWidgetResizable(True)
		self.set_stylesheet()

		main_widget.installEventFilter(self)

	def set_stylesheet(self):
		self.setStyleSheet(
		"""
		 /* --------------------------------------- QScrollBar  -----------------------------------*/
		 QScrollBar
		 {
		     height: 15px;
		     margin: 3px 15px 3px 15px;
		     border: 1px transparent #2A2929;
		     border-radius: 4px;
		     background-color: #C4C4C4;    /* #2A2929; */
		 }

		 QScrollBar::handle
		 {
		     background-color: #807E7E;      /* #605F5F; */
		     min-width: 5px;
		     border-radius: 4px;
		 }

		QScrollBar::handle:hover
		{
			background-color: #605F5F;
		}

		QScrollBar::add-line
		{
			margin: 0px 3px 0px 3px;
			border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
			width: 10px;
			height: 10px;
			subcontrol-position: right;
			subcontrol-origin: margin;
		}

		QScrollBar::sub-line
		{
			margin: 0px 3px 0px 3px;
			border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
			height: 10px;
			width: 10px;
			subcontrol-position: left;
			subcontrol-origin: margin;
		}

		QScrollBar::add-line:hover,QScrollBar::add-line:on
		{
			border-image: url(:/qss_icons/rc/right_arrow.png);
			height: 10px;
			width: 10px;
			subcontrol-position: right;
			subcontrol-origin: margin;
		}


		QScrollBar::sub-line:hover, QScrollBar::sub-line:on
		{
			border-image: url(:/qss_icons/rc/left_arrow.png);
			height: 10px;
			width: 10px;
			subcontrol-position: left;
			subcontrol-origin: margin;
		}

		QScrollBar::up-arrow, QScrollBar::down-arrow
		{
			background: none;
		}


		QScrollBar::add-page, QScrollBar::sub-page
		{
			background: none;
		}
		""")

	def eventFilter(self, obj, event):
		try: # Without try and except raises three errors when begin run code
			if self.main_widget is obj and event.type() == QEvent.Wheel:
				QCoreApplication.sendEvent(self.horizontalScrollBar(), event)
			return super().eventFilter(obj, event)
		except:
			return True

