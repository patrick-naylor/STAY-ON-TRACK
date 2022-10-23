# Written by Patrick Naylor
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
import sqlite3
from PyQt5.QtCore import Qt
from preferences import setup
from datetime import date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

sw = None
app = QApplication([])


class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		layout = QHBoxLayout()
		layout1 = QVBoxLayout()
		self.label = QLabel("Personal Log")
		layout1.addWidget(self.label)
		self.db = QSqlDatabase.addDatabase('QSQLITE')
		self.db.setDatabaseName('personal_data.db')

		self.model = QSqlTableModel()
		self.model.setTable('log')
		self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.model.select()
		self.view = QTableView()
		self.view.setWindowTitle('Personal Log')
		self.view.setModel(self.model)
		self.view.resizeColumnsToContents()
		layout1.addWidget(self.view)

		self.addButton = QPushButton('Add a Row')
		self.addButton.clicked.connect(self.add_row)
		layout1.addWidget(self.addButton)


		layout2 = QVBoxLayout()
		self.today = date.today()
		self.today_str = self.today.strftime('%m-%d-%Y')
		self.dateLabel = QLabel(self.today_str)
		layout2.addWidget(self.dateLabel)
		self.journalBox = QPlainTextEdit()
		layout2.addWidget(self.journalBox)
		self.submitButton = QPushButton('Submit Entry')
		self.submitButton.clicked.connect(self.submit_entry)
		layout2.addWidget(self.submitButton)


		self.layout3 = QVBoxLayout()
		self.plotProg = QLabel('Progress')
		self.layout3.addWidget(self.plotProg)
		columnNum = self.model.columnCount()
		columnNames = [self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole) for col in range(columnNum)]

		formLayout = QFormLayout()
		groupBox = QGroupBox()

		self.query = QSqlQuery()
		self.query.exec_('SELECT Date FROM log;')
		self.date_values = []
		while self.query.next():
			self.date_values.append(self.query.value(0))

		for name in columnNames[1:]:
			self.query.exec_(f'SELECT {name} FROM log;')
			self.y_values = []
			while self.query.next():
				#print(type(self.query.value(0)))
				if(self.query.value(0) == ''):
					self.y_values.append(np.nan)
				else:
					self.y_values.append(float(self.query.value(0)))
			self.figure = MplCanvas(self, width=4, height=4, dpi=100)
			self.figure.axes.plot(self.date_values, self.y_values)
			self.figure.setMinimumHeight(280)
			self.figure.axes.set_title(name)
			formLayout.addRow(self.figure)

		groupBox.setLayout(formLayout)

		scrollarea = QScrollArea()
		scrollarea.setWidget(groupBox)
		scrollarea.setWidgetResizable(True)

		self.layout3.addWidget(scrollarea)

		layout.addLayout(layout1)
		layout.addLayout(layout2)
		layout.addLayout(self.layout3)
		self.setLayout(layout)



	def add_row(self):
		ret = self.model.insertRows(self.model.rowCount(), 1)

	def submit_entry(self):
		entry = self.journalBox.document()
		query = QSqlQuery()
		query.exec_(f'''
			INSERT INTO journal (Date, Entry)
			VALUES("{self.today_str}", "{entry.toPlainText()}")
			''')
		self.journalBox.clear()





class SetupWindow(QWidget):

	def __init__(self):
		super().__init__()
		self.dbw = None
		layout = QVBoxLayout()
		self.label = QLabel('Setup Window')
		layout.addWidget(self.label)
		self.button = QPushButton("Ready to Track Your Life?")
		self.button.clicked.connect(self.get_started)
		layout.addWidget(self.button)
		self.setLayout(layout)

	def get_started(self, checked):
		if self.dbw is None:
			self.dbw = CreateDBWindow()
		self.dbw.show()
		self.close()

class CreateDBWindow(QWidget):

	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		self.label = QLabel("Create DB Window")
		self.w = None
		layout.addWidget(self.label)
		self.db = QSqlDatabase.addDatabase('QSQLITE')
		self.db.setDatabaseName('personal_data.db')

		if not self.db.open():
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText('Error in Database Creation')
			retval = msg.exec_()
			return False
		query = QSqlQuery()

		query.exec_('''
			CREATE TABLE IF NOT EXISTS log
			(Date DATETIME, Me INTEGER, Day INTEGER)
			''')

		query.exec_('''
			CREATE TABLE IF NOT EXISTS variables
			(Variable TEXT, GoalType TEXT, Goal REAL)
			''')

		query.exec_('''
			CREATE TABLE IF NOT EXISTS journal
			(Date DATETIME, Entry TEXT)
			''')

		self.combobox = QComboBox()
		self.combobox.addItems(['Process Goal', 'Outcome Goal'])
		layout.addWidget(self.combobox)

		self.textbox = QLineEdit(self)
		self.textbox.setText('Goal Name')
		layout.addWidget(self.textbox)

		self.textbox2 = QLineEdit(self)
		self.textbox2.setText('Target')
		layout.addWidget(self.textbox2)

		self.button = QPushButton('Add')
		self.button.clicked.connect(self.add_column)
		layout.addWidget(self.button)

		self.doneButton = QPushButton('Done')
		self.doneButton.clicked.connect(self.done)
		layout.addWidget(self.doneButton)

		self.setLayout(layout)

	def done(self):
		with open('preferences.py', 'w') as f:
			f.write('setup = True')
		setup = True
		if self.w is None:
			self.w = MainWindow()
		self.w.show()
		self.close()

	def add_column(self):
		textboxValue = self.textbox.text().replace(' ', '_')
		comboboxValue = self.combobox.currentText()
		textbox2Value = self.textbox2.text().replace(' ', '_')
		self.textbox.setText('')
		self.textbox2.setText('')
		query = QSqlQuery()
		query.exec_(f'''
			ALTER TABLE log
			ADD COLUMN {textboxValue} REAL''')
		query = QSqlQuery()
		query.exec_(f'''
			INSERT INTO variables (Variable, GoalType, Goal)
			VALUES("{textboxValue}", "{comboboxValue}", "{textbox2Value}")
			''')

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

if not setup:
	sw = SetupWindow()
	sw.show()

if ((setup) and (sw is None)):
	w = MainWindow()
	w.show()

app.exec()
