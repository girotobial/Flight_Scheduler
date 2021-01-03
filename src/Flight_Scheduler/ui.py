import os
from copy import copy as copy
from typing import Dict, List

import constant
import data
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAbstractItemView, QMainWindow, QWidget
from sqLiteManagerGUI import sqLiteDB


def waiting_effects(function):
    def new_function(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        function(self)
        QApplication.restoreOverrideCursor()
        return new_function


class MethodsMixin:
    def _translate(self, text: str) -> str:
        """Wrapper around QtCore.QCoreApplication.translate

        Parameters
        ----------
        text : str
            text to be translated

        Returns
        -------
        str
            translated text
        """
        return QtCore.QCoreApplication.translate(type(self).__name__, text)

    def _create_label(self, text: str) -> QtWidgets.QLabel:
        """Construct a label with the context applied

        Parameters
        ----------
        text : str
            Text to be applied to the label

        Returns
        -------
        QtWidgets.QLabel
            Label object
        """
        label = QtWidgets.QLabel(self)
        label.setText(self._translate(text))
        return label

    @staticmethod
    def _create_layout(
        layout: QtWidgets.QLayout, widgets: List[QtWidgets.QWidget]
    ) -> QtWidgets.QLayout:
        """Adds widgets to a layout. Not suitable for grid layouts

        Parameters
        ----------
        layout : QtWidgets.QLayout
            Layout to be constructed
        widgets : List[QtWidgets.QWidget]
            Widgets to add to the layout

        Returns
        -------
        QtWidgets.QLayout
            Supplied layout with widgets added
        """
        for widget in widgets:
            layout.addWidget(widget)
        return layout


class MainWindow(QtWidgets.QMainWindow, MethodsMixin):
    def __init__(self, database: data.Database):
        super(QMainWindow, self).__init__()
        self.db = database
        self._init_gui()

    def _init_gui(self) -> None:
        """Starts the gui"""
        self.setWindowTitle(self._translate(f"Flight Scheduler v{constant.VERSION}"))
        self.resize(1300, 800)
        self.setWindowIcon(QtGui.QIcon(constant.ICON_PATH))

        self.airports = AirportBox()
        self.airlines = AirlineBox()
        self.role_groupbox = RollGroupBox()
        self.flight_table = FlightTable(database=self.db)
        self.buttons = Buttons()

        left_panel = self._create_layout(
            layout=QtWidgets.QVBoxLayout(),
            widgets=[self.airports, self.airlines, self.role_groupbox],
        )

        right_panel = self._create_layout(
            layout=QtWidgets.QVBoxLayout(), widgets=[self.flight_table, self.buttons]
        )

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(left_panel)
        layout.addLayout(right_panel)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @property
    def roles(self) -> Dict[str, bool]:
        return {
            "pax": self.role_groupbox.pax_checkbox.isEnabled(),
            "cargo": self.role_groupbox.pax.checkbox.isEnabled(),
        }

    @property
    def departures(self) -> List[str]:
        return [
            departure for departure in self.airports.departure_textbox.text().split(",")
        ]

    @property
    def destinations(self) -> List[str]:
        return [
            destination
            for destination in self.airports.destination_textbox.text().split(",")
        ]


class AirportBox(QtWidgets.QWidget, MethodsMixin):
    def __init__(self):
        super(QWidget, self).__init__()
        self._init_gui()

    def _init_gui(self) -> None:
        """Starts the gui"""

        self.checkbox = QtWidgets.QCheckBox(self)
        self.checkbox.setText(self._translate("Specify airport details?"))
        self.checkbox.stateChanged.connect(self._checkbox_change_state)

        departure_label = self._create_label("Specify departure (ICAO):")
        destination_label = self._create_label("Specify destination (ICAO):")
        self.departure_textbox = QtWidgets.QLineEdit(self)
        self.departure_textbox.setEnabled(False)
        self.destination_textbox = QtWidgets.QLineEdit(self)
        self.destination_textbox.setEnabled(False)

        layout = self._create_layout(
            layout=QtWidgets.QVBoxLayout(),
            widgets=[
                self.checkbox,
                departure_label,
                self.departure_textbox,
                destination_label,
                self.destination_textbox,
            ],
        )
        self.setLayout(layout)

    def _checkbox_change_state(self) -> None:
        state = self.checkbox.isChecked()
        self.departure_textbox.setEnabled(state)
        self.destination_textbox.setEnabled(state)

    def _reset(self) -> None:
        self.checkbox.setChecked(False)


class AirlineBox(QtWidgets.QWidget, MethodsMixin):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.checkbox = QtWidgets.QCheckBox(self)

        self.checkbox.setText(self._translate("Specify Arilines?"))
        self.checkbox.stateChanged.connect(self._checkbox_change_state)

        label = self._create_label("Specify Airline ICAO Code(s)")
        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.setEnabled(False)

        layout = self._create_layout(
            layout=QtWidgets.QVBoxLayout(), widgets=[self.checkbox, label, self.textbox]
        )
        self.setLayout(layout)

    def _checkbox_change_state(self):
        state = self.checkbox.isChecked()
        self.textbox.setEnabled(state)


class RollGroupBox(QtWidgets.QGroupBox, MethodsMixin):
    def __init__(self):
        super(QtWidgets.QGroupBox, self).__init__()
        self._init_gui()

    def _init_gui(self):
        self.setFlat(True)
        self.setCheckable(False)
        self.setTitle(self._translate("Role"))

        self.pax_checkbox = QtWidgets.QCheckBox(self)
        self.pax_checkbox.setText(self._translate("Pax"))
        self.pax_checkbox.setChecked(True)

        self.cargo_checbox = QtWidgets.QCheckBox(self)
        self.cargo_checbox.setText(self._translate("Cargo"))
        self.cargo_checbox.setChecked(True)

        layout = self._create_layout(
            layout=QtWidgets.QVBoxLayout(),
            widgets=[self.pax_checkbox, self.cargo_checbox],
        )
        self.setLayout(layout)


class FlightTable(QtWidgets.QTableWidget, MethodsMixin):
    def __init__(self, database: data.Database):
        super(QtWidgets.QTableWidget, self).__init__()
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setRowCount(0)

        headers = constant.TABLE_HEADERS
        self.setColumnCount(len(headers))
        for i, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem()
            item.setText(self._translate(header))
            self.setHorizontalHeaderItem(i, item)


class Buttons(QtWidgets.QWidget, MethodsMixin):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.refresh_button = QtWidgets.QPushButton(self)
        self.refresh_button.setText(self._translate("Refresh"))

        self.reset_button = QtWidgets.QPushButton(self)
        self.reset_button.setText(self._translate("Reset"))

        layout = self._create_layout(
            layout=QtWidgets.QHBoxLayout(),
            widgets=[self.reset_button, self.refresh_button],
        )
        self.setLayout(layout)


class Ui_FlightScheduler(QWidget):
    def setupUi(self, FlightScheduler):
        self.checkMark = "\u2713"
        FlightScheduler.setObjectName("FlightScheduler")
        FlightScheduler.resize(1003, 800)
        self.horizontalLayout = QtWidgets.QHBoxLayout(FlightScheduler)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftPanel = QtWidgets.QVBoxLayout()
        self.leftPanel.setObjectName("leftPanel")
        self.airports = QtWidgets.QVBoxLayout()
        self.airports.setObjectName("airports")
        self.airportCheck = QtWidgets.QCheckBox(FlightScheduler)
        self.airportCheck.setObjectName("airportCheck")
        self.airports.addWidget(self.airportCheck)
        self.departureLabel = QtWidgets.QLabel(FlightScheduler)
        self.departureLabel.setObjectName("departureLabel")
        self.airports.addWidget(self.departureLabel)
        self.departureText = QtWidgets.QLineEdit(FlightScheduler)
        self.departureText.setObjectName("departureText")
        self.airports.addWidget(self.departureText)
        self.arrivalLabel = QtWidgets.QLabel(FlightScheduler)
        self.arrivalLabel.setObjectName("arrivalLabel")
        self.airports.addWidget(self.arrivalLabel)
        self.arrivalText = QtWidgets.QLineEdit(FlightScheduler)
        self.arrivalText.setObjectName("arrivalText")
        self.airports.addWidget(self.arrivalText)
        self.leftPanel.addLayout(self.airports)
        self.airlines = QtWidgets.QVBoxLayout()
        self.airlines.setObjectName("airlines")
        self.airlineCheck = QtWidgets.QCheckBox(FlightScheduler)
        self.airlineCheck.setObjectName("airlineCheck")
        self.airlines.addWidget(self.airlineCheck)
        self.airlineText = QtWidgets.QLineEdit(FlightScheduler)
        self.airlineText.setObjectName("airlineText")
        self.airlines.addWidget(self.airlineText)
        self.leftPanel.addLayout(self.airlines)
        self.aircraft = QtWidgets.QVBoxLayout()
        self.aircraft.setObjectName("aircraft")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.rollGroupBox = QtWidgets.QGroupBox(FlightScheduler)
        self.rollGroupBox.setFlat(True)
        self.rollGroupBox.setCheckable(False)
        self.rollGroupBox.setObjectName("rollGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.rollGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.paxCheckBox = QtWidgets.QCheckBox(self.rollGroupBox)
        self.paxCheckBox.setChecked(True)
        self.paxCheckBox.setObjectName("paxCheckBox")
        self.verticalLayout_2.addWidget(self.paxCheckBox)
        self.cargoCheckBox = QtWidgets.QCheckBox(self.rollGroupBox)
        self.cargoCheckBox.setChecked(True)
        self.cargoCheckBox.setObjectName("cargoCheckBox")
        self.verticalLayout_2.addWidget(self.cargoCheckBox)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout.addWidget(self.rollGroupBox)
        self.familyMenu = QtWidgets.QComboBox(FlightScheduler)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.familyMenu.sizePolicy().hasHeightForWidth())
        self.familyMenu.setSizePolicy(sizePolicy)
        self.familyMenu.setObjectName("familyMenu")
        self.familyMenu.addItem("")
        self.verticalLayout.addWidget(self.familyMenu)
        self.resetAircraft_btn = QtWidgets.QPushButton(FlightScheduler)
        self.resetAircraft_btn.setObjectName("resetAircraft_btn")
        self.verticalLayout.addWidget(self.resetAircraft_btn)
        # duration buttons
        self.durationGroupBox = QtWidgets.QGroupBox()
        self.durationGroupBox.setTitle("Duration (hours)")
        self.durationHorizontalLayout = QtWidgets.QHBoxLayout(self.durationGroupBox)
        self.anyDuration_btn = QtWidgets.QRadioButton("Any")
        self.anyDuration_btn.setChecked(True)
        self.shortDuration_btn = QtWidgets.QRadioButton("0-2")
        self.medDuration_btn = QtWidgets.QRadioButton("2-4")
        self.longDuration_btn = QtWidgets.QRadioButton("4-10")
        self.ultraLongDuration_btn = QtWidgets.QRadioButton("10+")
        self.durationHorizontalLayout.addWidget(self.anyDuration_btn)
        self.durationHorizontalLayout.addWidget(self.shortDuration_btn)
        self.durationHorizontalLayout.addWidget(self.medDuration_btn)
        self.durationHorizontalLayout.addWidget(self.longDuration_btn)
        self.durationHorizontalLayout.addWidget(self.ultraLongDuration_btn)
        self.verticalLayout.addWidget(self.durationGroupBox)
        self.currentHorizontalLayout = QtWidgets.QHBoxLayout()
        self.currentCheckBox = QtWidgets.QCheckBox()
        self.currentLabel = QtWidgets.QLabel("Departs in the next ")
        self.currentTimeEntry = QtWidgets.QLineEdit(FlightScheduler)
        self.currentTimeEntry.setEnabled(False)
        self.currentLabel2 = QtWidgets.QLabel(" minutes")
        self.currentTimeSpacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.currentHorizontalLayout.addWidget(self.currentCheckBox)
        self.currentHorizontalLayout.addWidget(self.currentLabel)
        self.currentHorizontalLayout.addWidget(self.currentTimeEntry)
        self.currentHorizontalLayout.addWidget(self.currentLabel2)
        self.currentHorizontalLayout.addItem(self.currentTimeSpacer)
        self.verticalLayout.addLayout(self.currentHorizontalLayout)

        self.eraGroupBox = QtWidgets.QGroupBox()
        self.eraGroupBox.setTitle("Era")
        self.eraHorizontalLayout = QtWidgets.QHBoxLayout(self.eraGroupBox)
        self.era1950CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era1950CheckBox.setText("50's")
        self.era1960CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era1960CheckBox.setText("60's")
        self.era1970CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era1970CheckBox.setText("70's")
        self.era1980CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era1980CheckBox.setText("80's")
        self.era1990CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era1990CheckBox.setText("90's")
        self.era2000CheckBox = QtWidgets.QCheckBox(checked=True)
        self.era2000CheckBox.setText("00's")
        self.eraModernCheckBox = QtWidgets.QCheckBox(checked=True)
        self.eraModernCheckBox.setText("2007+")
        self.eraHorizontalLayout.addWidget(self.era1950CheckBox)
        self.eraHorizontalLayout.addWidget(self.era1960CheckBox)
        self.eraHorizontalLayout.addWidget(self.era1970CheckBox)
        self.eraHorizontalLayout.addWidget(self.era1980CheckBox)
        self.eraHorizontalLayout.addWidget(self.era1990CheckBox)
        self.eraHorizontalLayout.addWidget(self.era2000CheckBox)
        self.eraHorizontalLayout.addWidget(self.eraModernCheckBox)
        self.verticalLayout.addWidget(self.eraGroupBox)

        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.resultLabel = QtWidgets.QLabel("Results:")
        self.verticalLayout.addWidget(self.resultLabel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.subTypeList = QtWidgets.QListWidget(FlightScheduler)
        self.subTypeList.setObjectName("subTypeList")
        self.horizontalLayout_2.addWidget(self.subTypeList)
        self.aircraft.addLayout(self.horizontalLayout_2)

        self.outputText = QtWidgets.QTextEdit(FlightScheduler)
        self.outputText.setObjectName("outputText")
        self.outputLegList = QtWidgets.QListWidget(FlightScheduler)
        self.outputLegList.setObjectName("outputLegs")
        self.outputLegList.setMaximumWidth(40)
        self.outputHorizontalLayout = QtWidgets.QHBoxLayout(FlightScheduler)
        self.outputHorizontalLayout.addWidget(self.outputLegList)
        self.outputHorizontalLayout.addWidget(self.outputText)
        self.aircraft.addLayout(self.outputHorizontalLayout)
        # self.aircraft.addWidget(self.outputText)

        self.leftPanel.addLayout(self.aircraft)
        self.horizontalLayout.addLayout(self.leftPanel)
        self.rightPanel = QtWidgets.QVBoxLayout()
        self.rightPanel.setObjectName("rightPanel")
        self.displayTable = QtWidgets.QTableWidget(FlightScheduler)
        self.displayTable.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.displayTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.displayTable.setObjectName("displayTable")
        self.displayTable.setColumnCount(5)
        self.displayTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.displayTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.displayTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.displayTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.displayTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.displayTable.setHorizontalHeaderItem(4, item)
        self.displayTable.horizontalHeader().setStretchLastSection(True)
        self.displayTable.verticalHeader().setVisible(False)
        self.displayTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rightPanel.addWidget(self.displayTable)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.fullRandom_btn = QtWidgets.QPushButton(FlightScheduler)
        self.fullRandom_btn.setObjectName("fullRandom_btn")
        self.horizontalLayout_3.addWidget(self.fullRandom_btn)
        # self.rndRoute_btn = QtWidgets.QPushButton(FlightScheduler)
        # self.rndRoute_btn.setObjectName("rndRoute_btn")
        self.updateTable_btn = QtWidgets.QPushButton(FlightScheduler)
        # self.horizontalLayout_3.addWidget(self.rndRoute_btn)
        self.horizontalLayout_3.addWidget(self.updateTable_btn)
        self.rightPanel.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.rightPanel)

        self.retranslateUi(FlightScheduler)
        QtCore.QMetaObject.connectSlotsByName(FlightScheduler)

    def retranslateUi(self, FlightScheduler):
        _translate = QtCore.QCoreApplication.translate
        FlightScheduler.setWindowTitle(
            _translate("FlightScheduler", "Flight Scheduler v1.7")
        )
        self.airportCheck.setText(
            _translate("FlightScheduler", "Specify airport details?")
        )
        self.departureLabel.setText(
            _translate("FlightScheduler", "Specify departure (ICAO):")
        )
        self.arrivalLabel.setText(
            _translate("FlightScheduler", "Specify arrival (ICAO):")
        )
        self.airlineCheck.setText(_translate("FlightScheduler", "Specify airlines?"))
        self.rollGroupBox.setTitle(_translate("FlightScheduler", "Role"))
        self.paxCheckBox.setText(_translate("FlightScheduler", "PAX"))
        self.cargoCheckBox.setText(_translate("FlightScheduler", "Cargo"))
        # initialize acFamilyStuff,now in seperate method
        self.familyMenu.setItemText(0, _translate("FlightScheduler", "Aircraft Family"))
        self.familyMenu.model().setData(
            self.familyMenu.model().index(0, 0),
            QtCore.QVariant(0),
            QtCore.Qt.UserRole - 1,
        )
        # done
        self.resetAircraft_btn.setText(_translate("FlightScheduler", "Reset Aircraft"))
        self.outputText.setHtml(
            _translate(
                "FlightScheduler",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>',
            )
        )
        item = self.displayTable.horizontalHeaderItem(0)
        item.setText(_translate("FlightScheduler", "Airline"))
        item = self.displayTable.horizontalHeaderItem(1)
        item.setText(_translate("FlightScheduler", "From"))
        item = self.displayTable.horizontalHeaderItem(2)
        item.setText(_translate("FlightScheduler", "To"))
        item = self.displayTable.horizontalHeaderItem(3)
        item.setText(_translate("FlightScheduler", "Aircraft"))
        # item = self.displayTable.horizontalHeaderItem(4)
        # item.setText(_translate("FlightScheduler", "Via"))
        self.fullRandom_btn.setText(_translate("FlightScheduler", "Random Flight"))
        # self.rndRoute_btn.setText(_translate("FlightScheduler", "Random Route"))
        self.updateTable_btn.setText(_translate("FlightScheduler", "Refresh Table"))

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.reset = False
        # read in aircraftFamilies mapped to subtypes
        self.fileName = os.getcwd() + "\\FlightDB.db"
        self.db = sqLiteDB(self.fileName)
        self.acSchema = self.db.pullAircraft()
        # initialize master vectors
        self.master_familyVector = {}
        self.master_subtypeVector = {}
        for family in self.acSchema[0].keys():
            self.master_familyVector[family] = False
            for subtype in self.acSchema[0][family]:
                self.master_subtypeVector[subtype] = False
        #
        self.initAircraftMenu()
        self.subTypeList.itemClicked.connect(self.subTypeClicked)
        self.familyMenu.currentTextChanged.connect(self.familyChanged)
        self.paxCheckBox.stateChanged.connect(self.paxCheckChange)
        self.cargoCheckBox.stateChanged.connect(self.cargoCheckChange)
        self.resetAircraft_btn.pressed.connect(self.resetButtonPressed)
        self.airlineText.setDisabled(True)
        self.airlineCheck.stateChanged.connect(self.airlineCheckChange)
        self.departureText.setDisabled(True)
        self.arrivalText.setDisabled(True)
        self.airportCheck.stateChanged.connect(self.airportCheckChange)
        self.anyDuration_btn.toggled.connect(self.setAnyDuration)
        self.shortDuration_btn.toggled.connect(self.setShortDuration)
        self.medDuration_btn.toggled.connect(self.setMedDuration)
        self.longDuration_btn.toggled.connect(self.setLongDuration)
        self.ultraLongDuration_btn.toggled.connect(self.setUltraDuration)
        self.fullRandom_btn.pressed.connect(self.generateFlight)
        # self.rndRoute_btn.pressed.connect(self.generateRoute)
        self.updateTable_btn.pressed.connect(self.updateTable)
        self.displayTable.setRowCount(0)
        self.displayTable.itemClicked.connect(self.generateFlightFromTable)
        self.outputLegList.itemClicked.connect(self.displayLeg)
        self.currentCheckBox.stateChanged.connect(self.currentCheckChanged)
        self.era1950CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.era1960CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.era1970CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.era1980CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.era1990CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.era2000CheckBox.stateChanged.connect(self.erasCheckChanged)
        self.eraModernCheckBox.stateChanged.connect(self.erasCheckChanged)

    def currentCheckChanged(self):
        if not self.currentCheckBox.isChecked():
            self.currentTimeEntry.setEnabled(False)
            self.db.timeFromNow = -1
        else:

            self.currentTimeEntry.setEnabled(True)

    def erasCheckChanged(self):
        eraList = [1, 1, 1, 1, 1, 1, 1]
        if not self.era1950CheckBox.isChecked():
            eraList[0] = 0
        if not self.era1960CheckBox.isChecked():
            eraList[1] = 0
        if not self.era1970CheckBox.isChecked():
            eraList[2] = 0
        if not self.era1980CheckBox.isChecked():
            eraList[3] = 0
        if not self.era1990CheckBox.isChecked():
            eraList[4] = 0
        if not self.era2000CheckBox.isChecked():
            eraList[5] = 0
        if not self.eraModernCheckBox.isChecked():
            eraList[6] = 0
        self.db.desiredEras = eraList

    #    @waiting_effects
    def updateTable(self):
        if self.currentCheckBox.isChecked():
            timeFromNow = self.sanitizeInput(self.currentTimeEntry.text())[0]
            try:
                timeFromNow = int(timeFromNow)
                self.db.timeFromNow = timeFromNow
            except Exception:
                print("User entered non-number")
                self.db.timeFromNow = -1
        if self.airlineCheck.isChecked():
            self.db.desiredAirline = self.sanitizeInput(self.airlineText.text())
        if self.airportCheck.isChecked():
            self.db.desiredOrigin = self.sanitizeInput(self.departureText.text())
            self.db.desiredDest = self.sanitizeInput(self.arrivalText.text())
        tableData = self.db.getTableDetails()
        if len(tableData) > 0 and not tableData == "NONE":
            self.displayTable.setRowCount(len(tableData))
            for i in range(0, len(tableData)):
                item0 = QTableWidgetItem(tableData[i][0])
                item0.setFlags(QtCore.Qt.ItemIsEnabled)
                self.displayTable.setItem(i, 0, item0)
                item1 = QTableWidgetItem(tableData[i][1])
                item1.setFlags(QtCore.Qt.ItemIsEnabled)
                self.displayTable.setItem(i, 1, item1)
                item2 = QTableWidgetItem(tableData[i][2])
                item2.setFlags(QtCore.Qt.ItemIsEnabled)
                self.displayTable.setItem(i, 2, item2)
                item3 = QTableWidgetItem(tableData[i][3])
                item3.setFlags(QtCore.Qt.ItemIsEnabled)
                self.displayTable.setItem(i, 3, item3)
        else:
            self.displayTable.setRowCount(0)

    #    @waiting_effects
    def generateFlightFromTable(self):
        self.outputText.setText("Thinking....")
        row = self.displayTable.row(self.displayTable.currentItem())
        airline = self.displayTable.item(row, 0).text()
        origin = self.displayTable.item(row, 1).text()
        dest = self.displayTable.item(row, 2).text()
        aircraft = self.displayTable.item(row, 3).text()
        result = self.db.getSpecificFlight(airline, origin, dest, aircraft)
        self.displayOutput(result)

    def generateFlight(self):
        self.outputText.setText("Thinking....")
        if self.currentCheckBox.isChecked():
            timeFromNow = self.sanitizeInput(self.currentTimeEntry.text())[0]
            try:
                timeFromNow = int(timeFromNow)
                self.db.timeFromNow = timeFromNow
            except Exception:
                print("User entered non-number")
                self.db.timeFromNow = -1
        if self.airlineCheck.isChecked():
            self.db.desiredAirline = self.sanitizeInput(self.airlineText.text())
        if self.airportCheck.isChecked():
            self.db.desiredOrigin = self.sanitizeInput(self.departureText.text())
            self.db.desiredDest = self.sanitizeInput(self.arrivalText.text())
        result = self.db.getRandomFlight()
        self.displayOutput(result)

    def generateRoute(self):
        self.outputText.setText("Thinking....")
        if self.currentCheckBox.isChecked():
            timeFromNow = self.sanitizeInput(self.currentTimeEntry.text())[0]
            try:
                timeFromNow = int(timeFromNow)
                self.db.timeFromNow = timeFromNow
            except Exception:
                print("User entered non-number")
                self.db.timeFromNow = -1
        if self.airlineCheck.isChecked():
            self.db.desiredAirline = self.sanitizeInput(self.airlineText.text())
        if self.airportCheck.isChecked():
            self.db.desiredOrigin = self.sanitizeInput(self.departureText.text())
            self.db.desiredDest = self.sanitizeInput(self.arrivalText.text())
        result = self.db.getRandomRoute()
        self.displayOutput(result)

    def displayLeg(self):
        row = self.outputLegList.row(self.outputLegList.currentItem())
        self.outputText.setText(self.printLeg(self.currentLegs[row]))

    def displayOutput(self, legData):
        self.outputLegList.clear()
        if len(legData) == 0:
            self.currentLegs = legData
            self.outputText.setText("No valid flights!!")
        else:
            self.currentLegs = legData[0]
            for i in range(0, len(legData[0])):
                item = QListWidgetItem("Leg " + str(i + 1))
                self.outputLegList.addItem(item)
                if legData[0][i][6] == legData[1]:
                    wantedIndex = i
            self.outputLegList.setCurrentRow(wantedIndex)
            self.outputText.setText(self.printLeg(legData[0][wantedIndex]))

    def printLeg(self, chosenLeg):
        try:
            baseString = (
                self.db.getAirlineFull(chosenLeg[1])
                + " "
                + chosenLeg[1]
                + str(chosenLeg[2])
                + ", "
                + self.getSeason(chosenLeg[3])
                + " "
                + str(chosenLeg[4])
                + "\n"
            )
            baseString += (
                str(self.db.getAircraftDetails(chosenLeg[-1])[1])
                + " "
                + chosenLeg[-3]
                + "\n"
            )
        except Exception:
            pass
        #        if chosenLeg[5] != "NULL":
        #            baseString += chosenLeg[5]+"\n"
        if chosenLeg[-2] != "NULL":
            baseString += chosenLeg[-2] + "\n"
        baseString += "Planned block time: " + self.formatTime(chosenLeg[-4]) + "\n"
        baseString += "\nDepart:\n"
        depDetails = self.db.getAirportDetails(chosenLeg[7])
        arrDetails = self.db.getAirportDetails(chosenLeg[8])
        baseString += depDetails[-1] + " (" + chosenLeg[7] + ")\n"
        locString = depDetails[3]
        if depDetails[4] != "NULL":
            locString += ", " + depDetails[4]
        baseString += locString + ", " + depDetails[-2] + "\n"
        utc = self.timeToString(chosenLeg[9])
        if chosenLeg[3] == 1:
            depLocalTime = self.timeToString(
                chosenLeg[9] + self.getTimeOffset(chosenLeg[9], depDetails[1])
            )
        else:
            depLocalTime = self.timeToString(
                chosenLeg[9] + self.getTimeOffset(chosenLeg[9], depDetails[2])
            )
        baseString += (
            self.getDayString(depLocalTime[0])
            + " "
            + depLocalTime[1]
            + " ("
            + utc[1]
            + " UTC)\n"
        )
        baseString += "\nArrive:\n" + arrDetails[-1] + " (" + chosenLeg[8] + ")\n"
        locString = arrDetails[3]
        if arrDetails[4] != "NULL":
            locString += ", " + arrDetails[4]
        baseString += locString + ", " + arrDetails[-2] + "\n"
        utc = self.timeToString(chosenLeg[10])
        if chosenLeg[3] == 1:
            arrLocalTime = self.timeToString(
                chosenLeg[10] + self.getTimeOffset(chosenLeg[10], arrDetails[1])
            )
        else:
            arrLocalTime = self.timeToString(
                chosenLeg[10] + self.getTimeOffset(chosenLeg[10], arrDetails[2])
            )
        baseString += (
            self.getDayString(arrLocalTime[0])
            + " "
            + arrLocalTime[1]
            + " ("
            + utc[1]
            + " UTC)\n"
        )
        return baseString

    def getDayString(self, dayInt):
        if dayInt == 1:
            return "Monday"
        if dayInt == 2:
            return "Tuesday"
        if dayInt == 3:
            return "Wednesday"
        if dayInt == 4:
            return "Thursday"
        if dayInt == 5:
            return "Friday"
        if dayInt == 6:
            return "Saturday"
        if dayInt == 7:
            return "Sunday"

    def timeToString(self, rawTime):
        if rawTime > 10080:
            rawTime -= 10080
        if rawTime < 1:
            rawTime += 10080
        day = rawTime // (24 * 60)
        hour = (rawTime - (day * 24 * 60)) // 60
        minute = rawTime - (day * 24 * 60) - (hour * 60)
        hourString = str(hour)
        minuteString = str(minute)
        if len(hourString) == 1:
            hourString = "0" + hourString
        if len(minuteString) == 1:
            minuteString = "0" + minuteString
        return [day + 1, hourString + ":" + minuteString]

    def getTimeOffset(self, rawTime, timezone):
        timeOffset = timezone.split(":")
        sign = timeOffset[0][0]
        hour = int(timeOffset[0][1:])
        minute = int(timeOffset[1])
        if sign == "+":
            return minute + (hour * 60)
        else:
            return -(minute + (hour * 60))

    def getSeason(self, season):
        if season == 1:
            return "Summer"
        return "Winter"

    def sendAircraft(self):
        resultArray = []
        for subType in self.current_subTypeVector.keys():
            if self.current_subTypeVector[subType] is True:
                resultArray.append(subType)
        self.db.desiredAircraft = resultArray

    def sanitizeInput(self, input):
        array = input.upper().split(",")
        array = [x.strip(" ") for x in array]
        return array

    def airportCheckChange(self):
        if self.airportCheck.isChecked():
            self.arrivalText.setEnabled(True)
            self.departureText.setEnabled(True)
            self.db.desiredOrigin = self.sanitizeInput(self.departureText.text())
            self.db.desiredDest = self.sanitizeInput(self.arrivalText.text())
        else:
            self.arrivalText.setDisabled(True)
            self.departureText.setDisabled(True)
            self.db.desiredDest = []
            self.db.desiredOrigin = []

    def airlineCheckChange(self):
        if self.airlineCheck.isChecked():
            self.airlineText.setEnabled(True)
            self.db.desiredAirline = self.sanitizeInput(self.airlineText.text())
        else:
            self.airlineText.setDisabled(True)
            self.db.desiredAirline = []

    def resetButtonPressed(self):
        # Clear table
        self.initAircraftMenu()
        self.reset = True
        self.paxCheckBox.setChecked(True)
        self.cargoCheckBox.setChecked(True)
        self.reset = False

    def formatTime(self, rawminutes):
        hours = rawminutes // 60
        minutes = int(rawminutes - (hours * 60))
        minuteString = str(minutes)
        if len(minuteString) == 1:
            minuteString = "0" + minuteString
        hourString = str(hours)
        if len(hourString) == 1:
            hourString = "0" + hourString
        return str(hourString) + ":" + str(minuteString)

    def paxCheckChange(self, state):
        for index in range(self.subTypeList.count() - 1, -1, -1):
            for typeCode in self.acSchema[1].keys():
                if (
                    self.acSchema[1][typeCode] == self.subTypeList.item(index).text()
                    and not self.acSchema[2][typeCode] == 4
                ):
                    subType = typeCode
                    if self.paxCheckBox.isChecked():
                        self.subTypeList.item(index).setForeground(
                            QtGui.QColor("green")
                        )
                        self.current_subTypeVector[subType] = True
                    else:
                        self.subTypeList.item(index).setForeground(QtGui.QColor("red"))
                        self.current_subTypeVector[subType] = False
        if not self.reset:
            self.sendAircraft()

    def cargoCheckChange(self, state):
        for index in range(self.subTypeList.count() - 1, -1, -1):
            for typeCode in self.acSchema[1].keys():
                if (
                    self.acSchema[1][typeCode] == self.subTypeList.item(index).text()
                    and self.acSchema[2][typeCode] == 4
                ):
                    subType = typeCode
                    if self.cargoCheckBox.isChecked():
                        self.subTypeList.item(index).setForeground(
                            QtGui.QColor("green")
                        )
                        self.current_subTypeVector[subType] = True
                    else:
                        self.subTypeList.item(index).setForeground(QtGui.QColor("red"))
                        self.current_subTypeVector[subType] = False
        if not self.reset:
            self.sendAircraft()

    def initAircraftMenu(self):
        # initialize acFamilyStuff
        self.current_subTypeVector = copy(self.master_subtypeVector)
        self.familyMenu.clear()
        self.subTypeList.clear()
        self.familyMenu.addItem("Aircraft Family")
        self.familyMenu.model().setData(
            self.familyMenu.model().index(0, 0),
            QtCore.QVariant(0),
            QtCore.Qt.UserRole - 1,
        )

        for aircraftFamily in sorted(self.master_familyVector.keys(), key=str.lower):
            self.familyMenu.addItem(aircraftFamily)
        self.sendAircraft()
        # REAPPLY FILTER

    def familyChanged(self, currentText):
        if not currentText == "Aircraft Family" and not currentText == "":
            self.familyMenu.setCurrentText("Aircraft Family")
            index = self.familyMenu.findText(currentText)
            if currentText.endswith(self.checkMark):
                newText = currentText[0:-2]
                self.familyMenu.setItemText(index, newText)
                subTypes = self.acSchema[0][newText]
                fullNames = []
                for subType in subTypes:
                    fullNames.append(self.acSchema[1][subType])
                    self.current_subTypeVector[subType] = False
                for index in range(self.subTypeList.count() - 1, -1, -1):
                    if self.subTypeList.item(index).text() in fullNames:
                        self.subTypeList.takeItem(index)
            else:
                self.familyMenu.setItemText(index, currentText + "\t" + self.checkMark)
                subTypes = self.acSchema[0][currentText]
                for subType in subTypes:
                    item = QListWidgetItem(self.acSchema[1][subType])
                    item.setForeground(QtGui.QColor("green"))
                    self.subTypeList.addItem(item)
                    self.current_subTypeVector[subType] = True
            # SORT SUBTYPE LIST!!!!!!!!!!!
            self.sendAircraft()

    def setAnyDuration(self):
        if self.anyDuration_btn.isChecked():
            self.db.maxDuration = -1
            self.db.minDuration = -1

    def setShortDuration(self):
        if self.shortDuration_btn.isChecked():
            self.db.maxDuration = 121
            self.db.minDuration = 0

    def setMedDuration(self):
        if self.medDuration_btn.isChecked():
            self.db.maxDuration = 241
            self.db.minDuration = 120

    def setLongDuration(self):
        if self.longDuration_btn.isChecked():
            self.db.maxDuration = 601
            self.db.minDuration = 240

    def setUltraDuration(self):
        if self.ultraLongDuration_btn.isChecked():
            self.db.minDuration = 599
            self.db.maxDuration = 1000000

    def subTypeClicked(self, item):
        for key, val in self.acSchema[1].items():
            if val == item.text():
                subType = key
        if item.foreground() == QtGui.QColor("green"):
            # #item disabled
            item.setForeground(QtGui.QColor("red"))
            self.current_subTypeVector[subType] = False
        else:
            # item enabled
            item.setForeground(QtGui.QColor("green"))
            self.current_subTypeVector[subType] = True
        # REAPPLY FILTER
        self.sendAircraft()


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication, QListWidgetItem, QTableWidgetItem

    app = QApplication(sys.argv)
    ex = Ui_FlightScheduler()
    ex.show()
    sys.exit(app.exec_())
