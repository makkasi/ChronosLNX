#!/usr/bin/env python

# icon.py
#http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttable-model/
#http://www.commandprompt.com/community/pyqt/book1
#http://doc.qt.nokia.com/latest/qstandarditemmodel.html
import os
import sys
import ephem
from PyQt4 import QtGui,QtCore
import geolocationwidget ## from example, but modified a little
import datetimetz #from Zim source code

from astro import *
from astrowidgets import *
from eventplanner import *
from chronostext import *
import chronosconfig

class ChronosLNX(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.timer = QtCore.QTimer(self)
		self.now = datetimetz.now()
		self.make_tray_icon()
		self.setGeometry(400, 400, 840, 400)
		self.setWindowTitle('ChronosLNX')
		self.setWindowIcon(CLNXConfig.main_icons['logo'])
		self.mainLayout=QtGui.QHBoxLayout(self)
		self.leftLayout=QtGui.QVBoxLayout()
		self.rightLayout=QtGui.QVBoxLayout()
		self.add_widgets()
		self.mainLayout.addLayout(self.leftLayout)
		self.mainLayout.addLayout(self.rightLayout)
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
		self.timer.start(1000)

	def add_widgets(self):
		##left pane
		self.calendar=AstroCalendar(self)
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.make_calendar_menu()
		self.leftLayout.addWidget(self.calendar)
		
		settingsButton=QtGui.QPushButton("Settings",self)
		settingsButton.clicked.connect(self.show_settings)
		self.leftLayout.addWidget(settingsButton)

		helpButton=QtGui.QPushButton("Help",self)
		helpButton.clicked.connect(self.show_about)
		self.leftLayout.addWidget(helpButton)

		aboutButton=QtGui.QPushButton("About",self)
		aboutButton.clicked.connect(self.show_about)
		self.leftLayout.addWidget(aboutButton)
		
		##right pane
		dayinfo=QtGui.QHBoxLayout()
		self.todayPicture=QtGui.QLabel()
		self.todayOther=QtGui.QLabel()
		dayinfo.addWidget(self.todayPicture)
		dayinfo.addWidget(self.todayOther)

		self.hoursToday=PlanetaryHoursList(self)
		self.hoursToday.setIcons(CLNXConfig.main_icons)

		self.moonToday=MoonCycleList(self)
		self.moonToday.setIcons(CLNXConfig.moon_icons)

		self.signsToday=SignsForDayList(self)
		self.signsToday.setIcons(CLNXConfig.main_icons)

		self.eventsToday=EventsList(self)

		dayData=QtGui.QTabWidget()
		self.prepare_hours_for_today()
		self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)
		self.signsToday.get_constellations(self.now)

		model=DayEventsModel()
		model.setSourceModel(CLNXConfig.schedule)
		model.setDate(self.now.date())
		self.eventsToday.tree.setModel(model)

		dayData.addTab(self.hoursToday,"Planetary Hours")
		dayData.addTab(self.moonToday,"Moon Cycles")
		dayData.addTab(self.signsToday,"Today's Signs")
		dayData.addTab(self.eventsToday,"Today's Events")

		self.rightLayout.addLayout(dayinfo)
		self.rightLayout.addWidget(dayData)
		self.update()

##time related

	def update_hours(self):
		self.hoursToday.clear()
		self.signsToday.clear()
		self.prepare_hours_for_today()
		self.eventsToday.tree.model().setDate(self.now.date())
		self.signsToday.get_constellations(self.now)

	def update_moon_cycle(self):
		if ephem.localtime(ephem.next_new_moon(self.now)).timetuple().tm_yday == self.now.timetuple().tm_yday:
			self.moonToday.clear()
			self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)

	def prepare_hours_for_today(self):
		self.pday = get_planet_day(int(self.now.strftime('%w')))
		self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
		if self.now < self.sunrise:
			self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now-timedelta(days=1), CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
			self.hoursToday.prepareHours(self.now-timedelta(days=1), CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
			self.pday = get_planet_day(int(self.now.strftime('%w'))-1)
		else:
			self.hoursToday.prepareHours(self.now, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidgetitem.html#setIcon
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidget.html


	#def check_alarm(self):
		#look through proxy model
		#if checkState == unchecked:
		#	skip

		#if self.now.date() == entry.toPyDate():
			#set date trigger satisfied

		#elif day == "Everyday":
			#set date trigger satisfied

		#elif day == "Weekends" and check weekend:
			#set date trigger satisfied

		#elif day == "Weekday" and check weekday:
			#set date trigger satisfied

		#elif self.pday == entry's pday:
			#set date trigger satisfied

		#if self.phour == entry's phour:
			#set date trigger satisfied
		
		#if all conditions met:
			#trigger function
			#disable until conditions met for hour

##datepicking related
#http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot/

	def get_info_for_date(self, date):
		info_dialog=QtGui.QDialog()
		info_dialog.setFixedSize(400,400)
		info_dialog.setWindowTitle("Info for %s" %(date.strftime("%m/%d/%Y")))
		hbox=QtGui.QHBoxLayout(info_dialog)

		hoursToday=PlanetaryHoursList(info_dialog)
		hoursToday.setIcons(CLNXConfig.main_icons)
		
		moonToday=MoonCycleList(info_dialog)
		moonToday.setIcons(CLNXConfig.moon_icons)

		signsToday=SignsForDayList(info_dialog)
		signsToday.setIcons(CLNXConfig.main_icons)

		eventsToday=EventsList(info_dialog)
		model=DayEventsModel()
		model.setSourceModel(CLNXConfig.schedule)
		model.setDate(date)
		eventsToday.tree.setModel(model)

		dayData=QtGui.QTabWidget(info_dialog)

		hoursToday.prepareHours(date,CLNXConfig.current_latitude,CLNXConfig.current_longitude,CLNXConfig.current_elevation)
		moonToday.get_moon_cycle(date)
		moonToday.highlight_cycle_phase(date)
		signsToday.get_constellations(date)

		dayData.addTab(hoursToday,"Planetary Hours")
		dayData.addTab(moonToday,"Moon Cycles")
		dayData.addTab(signsToday,"Signs For This Day")
		dayData.addTab(eventsToday,"Events for This Day")
		hbox.addWidget(dayData)
		info_dialog.exec_()

	def make_calendar_menu(self):
		self.calendar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.connect(self.calendar,QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.get_cal_menu)
		#self.calendar.setContextMenu(self.menu)

	def copy_to_clipboard(self, option,date):
		if option == "All":
			text=prepare_all(date, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
		elif option == "Moon":
			text=prepare_moon_cycle(date)
		elif option == "Signs":
			text=prepare_sign_info(date)
		elif option == "Hours":
			text=prepare_planetary_info(date, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
		elif option == "Events":
			text=prepare_events(date, CLNXConfig.schedule)
		app.clipboard().setText(text)

#KGlobal::locale::Warning your global KLocale is being recreated with a valid main component instead of a fake component, this usually means you tried to call i18n related functions before your main component was created. You should not do that since it most likely will not work
#X Error: RenderBadPicture (invalid Picture parameter) 174
#Extension:    153 (RENDER)
#Minor opcode: 8 (RenderComposite)
#Resource id:  0x3800836
#weird bug related to opening file dialog on linux through this, but it's harmless

	def print_to_file(self, option,date):
		if option == "All":
			text=prepare_all(date, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
		elif option == "Moon Cycle":
			text=prepare_moon_cycle(date)
		elif option == "Planetary Signs":
			text=prepare_sign_info(date)
		elif option == "Planetary Hours":
			text=prepare_planetary_info(date, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
		elif option == "Events":
			text=prepare_events(date, CLNXConfig.schedule)
		filename=QtGui.QFileDialog.getSaveFileName(parent=self,caption="Saving %s for %s" %(option, date.strftime("%m/%d/%Y")),filter="*.txt")
		if filename is not None and filename != "":
			f=open(filename,"w")
			f.write(text)
			QtGui.QMessageBox.information(self,"Saved", "%s has the %s you saved." %(filename, option))

	def get_cal_menu(self, qpoint):
		table=self.calendar.findChild(QtGui.QTableView)
		idx=table.indexAt(qpoint)
		mdl=table.model()
		if idx.column() > 0 and idx.row() > 0:
			month=self.calendar.monthShown()
			year=self.calendar.yearShown()
			day=mdl.data(idx,0).toPyObject()
			if idx.row() is 1 and day > 7:
				date=datetime(year=year,month=month-1,day=day).replace(tzinfo=LocalTimezone())
			elif idx.row() is 6 and day < 24:
				date=datetime(year=year,month=month+1,day=day).replace(tzinfo=LocalTimezone())
			else:
				date=datetime(year=year,month=month,day=day).replace(tzinfo=LocalTimezone())
			#self.calendar.setGridVisible(True)
			menu=QtGui.QMenu()
			infoitem=menu.addAction("Info for %s" %(date.strftime("%m/%d/%Y")))
			infoitem.triggered.connect(lambda: self.get_info_for_date(date))

			copymenu=menu.addMenu("Copy")
			copyall=copymenu.addAction("All")
			copydate=copymenu.addAction("Date")
			copyplanetdata=copymenu.addAction("Planetary Hours")
			copymoonphasedata=copymenu.addAction("Moon Phases")
			copysignsdata=copymenu.addAction("Signs for this date")
			copyeventdata=copymenu.addAction("Events")

			copyall.triggered.connect(lambda: self.copy_to_clipboard("All",date))
			copydate.triggered.connect(lambda: app.clipboard().setText(date.strftime("%m/%d/%Y")))
			copyplanetdata.triggered.connect(lambda: self.copy_to_clipboard("Planetary Hours",date))
			copymoonphasedata.triggered.connect(lambda: self.copy_to_clipboard("Moon Cycle",date))
			copysignsdata.triggered.connect(lambda: self.copy_to_clipboard("Planetary Signs",date))
			copyeventdata.triggered.connect(lambda: self.copy_to_clipboard("Events", date))

			savemenu=menu.addMenu("Save to File")
			saveall=savemenu.addAction("All")
			saveplanetdata=savemenu.addAction("Planetary Hours")
			savemoonphasedata=savemenu.addAction("Moon Phases")
			savesignsdata=savemenu.addAction("Signs for this date")
			saveeventdata=savemenu.addAction("Events")

			saveall.triggered.connect(lambda: self.print_to_file("All",date))
			saveplanetdata.triggered.connect(lambda: self.print_to_file("Planetary Hours",date))
			savemoonphasedata.triggered.connect(lambda: self.print_to_file("Moon Cycle",date))
			savesignsdata.triggered.connect(lambda: self.print_to_file("Planetary Signs",date))
			saveeventdata.triggered.connect(lambda: self.print_to_file("Events",date))

			menu.exec_(self.calendar.mapToGlobal(qpoint))
		#http://www.qtcentre.org/archive/index.php/t-42524.html?s=ef30fdd9697c337a1d588ce9d26f47d8

##config related

	def settings_reset(self,dialog):
		CLNXConfig.reset_settings()
		dialog.location_widget.setLatitude(CLNXConfig.current_latitude)
		dialog.location_widget.setLongitude(CLNXConfig.current_longitude)
		dialog.location_widget.setElevation(CLNXConfig.current_elevation)
		dialog.appearance_icons.setCurrentIndex(dialog.appearance_icons.findText(CLNXConfig.current_theme))

	def settings_change(self,dialog):
		lat=float(dialog.location_widget.latitude)
		lng=float(dialog.location_widget.longitude)
		elv=float(dialog.location_widget.elevation)
		thm=str(dialog.appearance_icons.currentText())
		CLNXConfig.current_latitude=lat
		CLNXConfig.current_longitude=lng
		CLNXConfig.current_elevation=elv
		CLNXConfig.current_theme=thm
		CLNXConfig.prepare_icons()
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.hoursToday.setIcons(CLNXConfig.main_icons)
		self.moonToday.setIcons(CLNXConfig.moon_icons)
		self.signsToday.setIcons(CLNXConfig.main_icons)
		self.update_hours()
		self.moonToday.clear()
		self.moonToday.get_moon_cycle(self.now)
		#eventually load DB of events

	def settings_write(self,dialog):
		self.settings_change(dialog)
		CLNXConfig.save_settings()
		CLNXConfig.save_schedule()
		dialog.close()
		#eventually save DB of events

	def show_settings(self):
		settings_dialog=QtGui.QDialog(self)
		settings_dialog.setWindowTitle("Settings")
		tabs=QtGui.QTabWidget(settings_dialog)
		settings_dialog.setFixedSize(400,400)
		
		location_page=QtGui.QFrame()
		appearance_page=QtGui.QFrame()
		events_page=QtGui.QFrame()
		tabs.addTab(location_page,"Location")
		tabs.addTab(appearance_page,"Appearance")
		tabs.addTab(events_page,"Events")
		
		settings_dialog.location_widget = geolocationwidget.GeoLocationWidget(location_page)
		settings_dialog.location_widget.setLatitude(CLNXConfig.current_latitude)
		settings_dialog.location_widget.setLongitude(CLNXConfig.current_longitude)
		settings_dialog.location_widget.setElevation(CLNXConfig.current_elevation)
		
		layout=QtGui.QVBoxLayout(settings_dialog)
		layout.addWidget(tabs)
		
		grid=QtGui.QGridLayout(appearance_page)
		appearance_label=QtGui.QLabel("Icon theme")
		settings_dialog.appearance_icons=QtGui.QComboBox()
		settings_dialog.appearance_icons.addItem("None")
		for theme in CLNXConfig.get_available_themes():
			icon=QtGui.QIcon(CLNXConfig.grab_icon_path(theme,"misc","chronoslnx"))
			settings_dialog.appearance_icons.addItem(icon,theme)
		settings_dialog.appearance_icons.setCurrentIndex(settings_dialog.appearance_icons.findText(CLNXConfig.current_theme))
		grid.addWidget(appearance_label,0,0)
		grid.addWidget(settings_dialog.appearance_icons,0,1)
		
		buttonbox=QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
		resetbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Reset)
		okbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
		applybutton=buttonbox.addButton(QtGui.QDialogButtonBox.Apply)
		cancelbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
		
		resetbutton.clicked.connect(lambda: self.settings_reset(settings_dialog))
		okbutton.clicked.connect(lambda: self.settings_write(settings_dialog))
		applybutton.clicked.connect(lambda: self.settings_change(settings_dialog))
		cancelbutton.clicked.connect(settings_dialog.close)
		layout.addWidget(buttonbox)
		
		settings_dialog.eventplanner=EventsList(events_page)
		a_vbox=QtGui.QVBoxLayout(events_page)
		a_vbox.addWidget(settings_dialog.eventplanner)
		settings_dialog.eventplanner.tree.setModel(CLNXConfig.schedule)
		
		#tooltips.set_tip(settings_window.lat_box, "Negative indicates south.\nMust be between -90 and 90 inclusive.")
		#tooltips.set_tip(settings_window.lon_box,"Negative indicates west.\nMust be between -180 and 180 inclusive.")
		#tooltips.set_tip(settings_window.elv_box,"Negative indicates below sea level.\nMust be between -418 and 8850 inclusive, in meters.")

		settings_dialog.open()

## systray
#http://stackoverflow.com/questions/893984/pyqt-show-menu-in-a-system-tray-application
#http://www.itfingers.com/Question/758256/pyqt4-minimize-to-tray

	def make_tray_icon(self):
		  self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(CLNXConfig.main_icons['logo']), app)
		  #self.trayIcon = QtGui.QSystemTrayIcon(app)
		  menu = QtGui.QMenu()
		  quitAction = QtGui.QAction(self.tr("&Quit"), self)
		  QtCore.QObject.connect(quitAction, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("quit()"))
		  menu.addAction("&Show",self.show)
		  menu.addAction("&Settings",self.show_settings)
		  menu.addAction(quitAction)
		  self.trayIcon.setContextMenu(menu)
		  traySignal = "activated(QSystemTrayIcon::ActivationReason)"
		  QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)
		  self.trayIcon.show()

	def _ChronosLNX__icon_activated(self,reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick:
			if(self.isHidden()):
				self.show()
			else:
				self.hide()

	def closeEvent(self, event):
		self.hide()
		event.ignore()

##misc
#http://www.saltycrane.com/blog/2008/01/python-variable-scope-notes/

	def show_about(self):
		QtGui.QMessageBox.about (self, "About ChronosLNX", "<center><big><b>ChronosLNX 0.2</b></big><br />\
A simple tool for checking planetary hours and moon phases.<br />\
(C) ShadowKyogre 2011<br /><a href=\"http://shadowkyogre.github.com/ChronosLNX/\">ChronosLNX Homepage</a></center>")

	def update(self):
		self.now = datetimetz.now()
		if self.now > self.next_sunrise:
			self.update_hours()
			self.update_moon_cycle()
		self.phour = self.hoursToday.grab_nearest_hour(self.now)
		planets_string = "This is the day of %s, the hour of %s" %(self.pday, self.phour)
		moon_phase=grab_moon_phase(self.now)
		sign_string="The sign of the month is %s" %(calculate_sign(self.now))
		if CLNXConfig.current_theme == "None":
			sysicon=QtGui.QIcon(CLNXConfig.grab_icon_path("DarkGlyphs","misc","chronoslnx"))
		else:
			sysicon=CLNXConfig.main_icons[str(self.phour)]
		self.trayIcon.setToolTip("%s - %s\n%s\n%s\n%s" %(self.now.strftime("%Y/%m/%d"), self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		self.trayIcon.setIcon(sysicon)
		self.todayPicture.setPixmap(CLNXConfig.main_icons[str(self.phour)].pixmap(64,64))
		self.todayOther.setText("%s\n%s\n%s\n%s" %(self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))

app = QtGui.QApplication(sys.argv)
CLNXConfig = chronosconfig.ChronosLNXConfig()
chronoslnx = ChronosLNX()
chronoslnx.show()
sys.exit(app.exec_())