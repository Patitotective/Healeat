from PyQt5.QtWidgets import QTabBar, QTabWidget, QStylePainter, QStyleOptionTab, QStyle
from PyQt5.QtCore import QRect, QPoint

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
			r = QRect(QPoint(), s)
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
