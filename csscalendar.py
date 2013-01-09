from PyQt4 import QtGui,QtCore
import calendar
from datetime import date as pydate

class CSSCalendar(QtGui.QWidget):
	currentPageChanged = QtCore.pyqtSignal(int,int)
	"""A CalendarWidget that supports CSS theming"""
	def __init__(self, *args,**kwargs):
		super().__init__(*args)
		self.__useCSS=False
		layout=QtGui.QGridLayout(self)
		self._monthBox=QtGui.QComboBox(self)
		self._monthBox.addItems(calendar.month_name[1:])
		self._goForward=QtGui.QToolButton()
		self._goBackward=QtGui.QToolButton()
		self._yearBox=QtGui.QLineEdit(self)
		self._table=QtGui.QTableWidget(6,7)
		self._table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self._table.setHorizontalHeaderLabels(calendar.day_abbr[6:]+calendar.day_abbr[:6])
		self._table.verticalHeader().hide()

		self._goForward.clicked.connect(self.nextPage)
		self._goBackward.clicked.connect(self.prevPage)
		self._goBackward.setArrowType(QtCore.Qt.LeftArrow)
		self._goForward.setArrowType(QtCore.Qt.RightArrow)
		self._monthBox.activated[int].connect(self.setMonth)

		layout.addWidget(self._goBackward,0,0)
		layout.addWidget(self._monthBox,0,1,1,3)
		layout.addWidget(self._yearBox,0,4,1,2)
		layout.addWidget(self._goForward,0,6)
		layout.addWidget(self._table,1,0,4,7)

		self.weekdayBGs=[QtGui.QBrush() for i in range(7)]
		self.weekdayFGs=[QtGui.QBrush() for i in range(7)]
		self._calendar=calendar.Calendar(6)
		self._date=None
		self.date=pydate.today()
	
	def yearShown(self):
		return int(self._yearBox.text())
	
	def monthShown(self):
		return self._monthBox.currentIndex()+1

	def prevPage(self):
		if self._date.month == 1:
			#self.currentPageChanged.emit(self._date.year-1,12)
			self.setCurrentPage(self._date.year-1,12)
		else:
			#self.currentPageChanged.emit(self._date.year,self._date.month-1)
			self.setCurrentPage(self._date.year,self._date.month-1)

	def nextPage(self):
		if self._date.month == 12:
			#self.currentPageChanged.emit(self._date.year+1,11)
			self.setCurrentPage(self._date.year+1,1)
		else:
			#self.currentPageChanged.emit(self._date.year,self._date.month+1)
			self.setCurrentPage(self._date.year,self._date.month+1)

	def setMonth(self, monthidx):
		self.currentPageChanged.emit(self._date.year,monthidx+1)
		self.date=self.date.replace(month=monthidx+1)

	def setCurrentPage(self, year, month):
		self.currentPageChanged.emit(year, month)
		self.date=self.date.replace(year=year, month=month)

	def date(self):
		return self._date
	
	def setDate(self, newdate):
		if self._date is None or newdate.month != self._date.month:
			refill=True
		self._date=newdate
		self._yearBox.setText(str(self._date.year))
		self._monthBox.setCurrentIndex(self._date.month-1)
		if refill:
			self._refillCells()
	
	date=QtCore.pyqtProperty(pydate, date, setDate)
	
	def _modifyDayItem(self, item):
		pass

	def _refillCells(self):
		monthdates=list(self._calendar.itermonthdates(self._date.year,self._date.month))
		thisday=pydate.today()
		weeks=len(monthdates)
		self._table.setRowCount(int(weeks/7))
		for i in range(weeks):
			item=QtGui.QTableWidgetItem()
			item.setText(str(monthdates[i].day))
			item.setData(QtCore.Qt.UserRole,monthdates[i])
			item.setData(QtCore.Qt.TextAlignmentRole,QtCore.Qt.AlignCenter)
			self._modifyDayItem(item)
			self._table.setItem(i/7,i%7,item)

	def useCSS(self):
		return self.__useCSS

	def setUseCSS(self, css):
		self.__useCSS=css
		if not self.__useCSS:
			transparent=QtGui.QColor()
			transparent.setAlpha(0)
			brush=QtGui.QBrush(transparent)
			col=self._table.palette().text()
			fg=QtGui.QBrush(col)
			for i in range(self._table.rowCount()):
				for j in range(7):
					self._table.item(i,j).setForeground(fg)
					self._table.item(i,j).setBackground(brush)

	def __setDayFG(self, day, fg):
		self.weekdayFGs[day-1]=fg
		for i in range(self._table.rowCount()):
			self._table.item(i,day-1).setForeground(fg)

	def __setDayFill(self, day, fill):
		self.weekdayBGs[day-1]=fill
		for i in range(self._table.rowCount()):
			self._table.item(i,day-1).setBackground(fill)

	def __dayFG(self, day):
		return self.weekdayFGs[day]

	def __dayFill(self, day):
		return self.weekdayBGs[day]

	sundayFill=QtCore.pyqtProperty("QBrush", 
		lambda self: self.__dayFill(QtCore.Qt.Sunday), 
		lambda self, fill: self.__setDayFill(QtCore.Qt.Sunday, fill))
	mondayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Monday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Monday,fill))
	tuesdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Tuesday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Tuesday,fill))
	wednesdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Wednesday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Wednesday,fill))
	thursdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Thursday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Thursday,fill))
	fridayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Friday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Friday,fill))
	saturdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Saturday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Saturday,fill))

	sundayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Sunday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Sunday,fill))
	mondayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Monday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Monday,fill))
	tuesdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Tuesday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Tuesday,fill))
	wednesdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Wednesday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Wednesday,fill))
	thursdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Thursday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Thursday,fill))
	fridayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Friday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Friday,fill))
	saturdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Saturday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Saturday,fill))
	'''
	weekNFG=QtCore.pyqtProperty("QBrush", __weekNFG, __setWeekNFG)
	weekNFill=QtCore.pyqtProperty("QBrush", __weekNFill, __setWeekNFill)
	'''
	useCSS=QtCore.pyqtProperty("bool", useCSS, setUseCSS)
