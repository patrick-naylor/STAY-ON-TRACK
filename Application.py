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
from matplotlib.widgets import Slider

#TODO: Put progress statements for each goal in scrollable box inbetween sql view
#and charts
#TODO: Move Journal to bottom half. Split in half vertically between create entry
#box and journal recall page
#TODO: Add information to setup page
#TODO: Add information to main page
#TODO: Create clustering model and launch notification system
#TODO: Work on styling/naming/logo

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
		layout2.addWidget(self.label)


		self.model2 = QSqlTableModel()
		self.model2.setTable('Variables')
		self.model2.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.model2.select()
		self.view2 = QTableView()
		self.view2.setWindowTitle('Personal Log')
		self.view2.setModel(self.model2)
		self.view2.resizeColumnsToContents()
		layout2.addWidget(self.view2)


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
		ticks = [(tick[:-4] + tick[-2:], idx) for idx, tick in enumerate(self.date_values) if tick[3:5] in ['01', '15']]
		combination = list(map(list, zip(*ticks)))
		label_list, tick_list = combination

		for name in columnNames[1:]:
			target = np.nan
			mean = np.nan
			self.query.exec_(f'SELECT Goal FROM variables WHERE Variable = "{name}"')
			while self.query.next():
				if isinstance(self.query.value(0), str):p
					target = np.nan
				else:
					target = float(self.query.value(0))

			self.query.exec_(f'SELECT {name} FROM log;')
			self.y_values = []
			while self.query.next():
				if(self.query.value(0) == ''):
					self.y_values.append(np.nan)
				else:
					self.y_values.append(float(self.query.value(0)))

			self.query.exec_(f'SELECT GoalType FROM variables WHERE GoalType = "Process Goal" AND "Goal" = "" And Variable = "{name}"')
			while self.query.next():
				if(self.query.value(0) == ''):
					mean = np.nan
				else:
					mean = np.nanmean(np.array(self.y_values[-7:]))


			self.figure = MplCanvas(self, width=4, height=4, dpi=100)
			self.figure.axes.plot(self.date_values, self.y_values)
			if(~np.isnan(target)):
				self.figure.axes.plot([self.date_values[0], self.date_values[-1]], [target, target], c='orange')
				self.figure.axes.legend([name, 'Target Value'], fontsize='small', facecolor='#1d1e1e', labelcolor='#ffffff', edgecolor='#bfbfbf')
			if(~np.isnan(mean)):
				self.figure.axes.plot([self.date_values[0], self.date_values[-1]], [mean, mean], c='limegreen')
				self.figure.axes.legend([name, f'Previous 7 {name} Mean'], fontsize='small', facecolor='#1d1e1e', labelcolor='#ffffff', edgecolor='#bfbfbf')
			self.figure.setMinimumHeight(280)
			self.figure.axes.set_title(name, color='#ffffff')
			self.figure.axes.tick_params(rotation=25, labelsize=8)
			self.figure.axes.set_xticks(tick_list, label_list)
			self.figure.fig.tight_layout(rect=(0, .025, 1, 1))
			self.figure.axes.set_facecolor('#1d1e1e')
			self.figure.fig.patch.set_facecolor('#1d1e1e')
			self.figure.axes.spines['bottom'].set_color('#bfbfbf')
			self.figure.axes.spines['top'].set_color('#bfbfbf')
			self.figure.axes.spines['left'].set_color('#bfbfbf')
			self.figure.axes.spines['right'].set_color('#bfbfbf')
			self.figure.axes.tick_params(color='#bfbfbf', labelcolor='#ffffff')


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

	def progress_comments(self, name, gtype, target):
		if ((gtype == 'Process Goal') and (target == '')):
			string = f'''Over your last 7 days youre average {name}(s) have been {amount} {high_or_low} overall average 
			{rand_str}'''
		elif ((gtype == 'Process Goal') and (isinstance(target, float))):
			string = f'''Over your last 7 days youre average {name}(s) have been {amount} {high_or_low} than your target 
			{rand_str}'''
		elif gtype == 'Process Goal':
			string = f'''Over the last 7 days your {name} has been {percent}% of your target category {target}
			{rand_str}'''
		elif ((gtype == 'Outcome Goal') and (isinstance(target, float))):
			string = f'''Over the last 7 days your progress towards your {name} goal has {high_or_low} by {percent}%
			{outcom_rand_str}'''
		else:
			string = f'''Over your last 7 days youre average {name}(s) have been {amount} {high_or_low} overall average 
			{rand_str}'''







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
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

## Junk	layout2 = QVBoxLayout()
#		self.today = date.today()
#		self.today_str = self.today.strftime('%m-%d-%Y')
#		self.dateLabel = QLabel(self.today_str)
#		layout2.addWidget(self.dateLabel)
#		self.journalBox = QPlainTextEdit()
#		layout2.addWidget(self.journalBox)
#		self.submitButton = QPushButton('Submit Entry')
#		self.submitButton.clicked.connect(self.submit_entry)
#		layout2.addWidget(self.submitButton)

random_strings = ['']

if not setup:
	sw = SetupWindow()
	sw.show()

if ((setup) and (sw is None)):
	w = MainWindow()
	w.show()

app.exec()
