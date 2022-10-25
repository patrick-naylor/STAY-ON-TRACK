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
import random

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
		self.label = QLabel('Progress Report')
		layout2.addWidget(self.label)
		formLayout = QFormLayout()
		groupBox = QGroupBox()
		variables = {'Variable': [], 'GoalType': [], 'Goal': []}
		self.query = QSqlQuery()

		self.query.exec_('SELECT Variable, GoalType, Goal FROM variables')
		while self.query.next():
			variables['Variable'].append(self.query.value(0))
			variables['GoalType'].append(self.query.value(1))
			variables['Goal'].append(self.query.value(2))

		for idx in range(len(variables['Variable'])):
			comment = self.progress_comments(variables['Variable'][idx], variables['GoalType'][idx], variables['Goal'][idx])
			comment_label = QLabel(comment)
			formLayout.addRow(comment_label)

		groupBox.setLayout(formLayout)
		scrollarea = QScrollArea()
		scrollarea.setWidget(groupBox)
		scrollarea.setWidgetResizable(True)

		layout2.addWidget(scrollarea)


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
				if isinstance(self.query.value(0), str):
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
			self.figure.axes.plot(self.date_values, self.y_values, c = '#557ff2')

			if(~np.isnan(target)):
				self.figure.axes.plot([self.date_values[0], self.date_values[-1]], [target, target], c='#ffa82e')
				self.figure.axes.legend([name, 'Target Value'], fontsize='small', facecolor='#1d1e1e', labelcolor='#ffffff', edgecolor='#bfbfbf')
			if(~np.isnan(mean)):
				self.figure.axes.plot([self.date_values[0], self.date_values[-1]], [mean, mean], c='#6bcf7e')
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
		self.query.exec_(f'SELECT {name} FROM log')
		data_values = []
		while self.query.next():
			try:
				data_values.append(float(self.query.value(0)))
			except ValueError:
				data_values.append(np.nan)
		if gtype == 'Process Goal':
			total_avg = np.nanmean(np.array(data_values))
			last_seven = np.nanmean(np.array(data_values[-7:]))
			total_diff = abs(float(target) - total_avg)
			seven_diff = abs(float(target) - last_seven)

			if total_diff > seven_diff:
				closer_or_further = 'closer to'
				percent_num = (total_diff - seven_diff)/seven_diff
				percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
				rand_str = random.choice(random_improve_strings)
			elif total_diff < seven_diff:
				closer_or_further = 'further from'
				percent_num = (seven_diff - total_diff)/total_diff
				percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
				rand_str = random.choice(random_disimprove_strings)
			else:
				rand_str = random.choice(random_generic_strings)
				return f'''<font color="white">over your last seven entries your average </font><font color="#557ff2">{name}<br>
has been equal to your overall average<br>
</font><font color="#f5f398">{rand_str}</font>'''
				
			return f'''<font color="white">Over your last seven entries your average </font><font color="#557ff2">{name}</font><font color="white"><br>
have been {percent}{closer_or_further} your target of </font><font color="#557ff2">{str(target)}</font><font color="white"><br>
than your overall average.<br>
</font><font color="#f5f398">{rand_str}</font>'''

		elif gtype == 'Outcome Goal':
			last_seven = np.nanmean(np.array(data_values[-7:]))
			prev_seven = np.nanmean(np.array(data_values[-14:-7]))
			last_seven_diff = abs(float(target)-last_seven)
			prev_seven_diff = abs(float(target)-prev_seven)

			if last_seven_diff > prev_seven_diff:
				closer_or_further = 'further from'
				percent_num = round(last_seven_diff - prev_seven_diff, 2)
				percent = f'</font><font color="#ffa82e">{str(percent_num)} </font><font color="white">'
				rand_str = random.choice(random_disimprove_strings)

			elif last_seven_diff < prev_seven_diff:
				closer_or_further = 'closer to'
				percent_num = round(prev_seven_diff - last_seven_diff, 2)
				percent = f'</font><font color="#ffa82e">{str(percent_num)} </font><font color="white">'
				rand_str = random.choice(random_improve_strings)
			else:
				rand_str = random.choice(random_generic_strings)
				return f'''<font color="white">Over your last seven days you hav not made<br> 
any progress towards your goal of </font><font color="#557ff2">{target}</font><font color="white"><br>
</font><font color="#f5f398">{rand_str}</font>'''

			return f'''<font color="white">Over your last seven entries your progress towards your<br> 
</font><font color="#557ff2">{name}</font><font color="white"> goal is {percent}{closer_or_further} your goal of </font><font color="#557ff2">{target}</font><font color="white"><br> 
then after your previous seven.<br>
</font><font color="#f5f398">{rand_str}</font>'''
		elif gtype == 'Reference Goal':
			self.query.exec_(f'SELECT {str(target)} FROM log')
			target_values = []
			while self.query.next():
				if isinstance(self.query.value(0), float):
					target_values.append(self.query.value(0))
				else:
					target_values.append(np.nan)
			diff = abs(np.array(target_values) - np.array(data_values))
			total_diff = np.nanmean(diff)
			seven_diff = np.nanmean(diff[-7:])
			if total_diff > seven_diff:
				closer_or_further = 'closer to'
				percent_num = (total_diff - seven_diff)/seven_diff
				percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
				rand_str = random.choice(random_improve_strings)
			elif total_diff < seven_diff:
				closer_or_further = 'further from'
				percent_num = (seven_diff - total_diff)/total_diff
				percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
				rand_str = random.choice(random_disimprove_strings)
			else:
				rand_str = random.choice(random_generic_strings)
				return f'''<font color="white">Over your last seven entries your </font><font color="#557ff2">{name}</font><font color="white"> is no<br> 
closer to your </font><font color="#557ff2">{target}</font><font color="white"> than your overall average<br>
</font><font color="#f5f398">{rand_str}</font>'''

			return f'''<font color="white">Over your last seven entries your </font><font color="#557ff2">{name}</font><font color="white"> is<br> 
{percent} {closer_or_further} </font><font color="#557ff2">{target}</font><font color="white"> than your overall average<br>
</font><font color="#f5f398">{rand_str}</font>'''







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
		self.layout = QVBoxLayout()
		self.label = QLabel("Create DB Window")
		self.w = None
		self.layout.addWidget(self.label)
		self.db = QSqlDatabase.addDatabase('QSQLITE')
		self.db.setDatabaseName('personal_data.db')
		self.pw = None

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
		self.button = None
		self.doneButton = None
		self.combobox = QComboBox()
		self.combobox.addItems(['Goal Type', 'Process Goal', 'Outcome Goal', 'Reference Goal'])
		self.layout.addWidget(self.combobox)

		self.checkComboBtn = QPushButton('Enter')
		self.checkComboBtn.clicked.connect(self.generate_menu)
		self.layout.addWidget(self.checkComboBtn)

		self.setLayout(self.layout)

	def generate_menu(self):
		self.pw = None
		self.target_strings = {'Process Goal': 'Target', 'Outcome Goal': 'Goal', 'Reference Goal': 'Goal Category Name'}
		if(self.button != None):
			self.layout.removeWidget(self.button)
			self.layout.removeWidget(self.doneButton)
			self.layout.removeWidget(self.goalText)
			self.layout.removeWidget(self.targetText)
			self.button = None
			self.doneButton = None
			self.goalText = None
			self.targetText = None
		if self.combobox.currentText() == 'Goal Type':
			if self.pw is None:
				self.pw = ErrorPopup()
			self.pw.label.setText('Please select a Goal Type')
			self.pw.show()
		elif self.combobox.currentText() == 'Process Goal':
			self.goalText = QLineEdit('Goal Name')
			self.targetText = QLineEdit(self.target_strings['Process Goal'])
			self.layout.addWidget(self.goalText)
			self.layout.addWidget(self.targetText)

			self.button = QPushButton('Add')
			self.button.clicked.connect(self.add_column)
			self.layout.addWidget(self.button)

			self.doneButton = QPushButton('Done')
			self.doneButton.clicked.connect(self.done)
			self.layout.addWidget(self.doneButton)
		elif self.combobox.currentText() == 'Outcome Goal':
			self.goalText = QLineEdit('Goal Name')
			self.targetText = QLineEdit(self.target_strings['Outcome Goal'])
			self.layout.addWidget(self.goalText)
			self.layout.addWidget(self.targetText)

			self.button = QPushButton('Add')
			self.button.clicked.connect(self.add_column)
			self.layout.addWidget(self.button)

			self.doneButton = QPushButton('Done')
			self.doneButton.clicked.connect(self.done)
			self.layout.addWidget(self.doneButton)
		else:
			self.goalText = QLineEdit('Goal Name')
			self.targetText = QLineEdit(self.target_strings['Reference Goal'])
			self.layout.addWidget(self.goalText)
			self.layout.addWidget(self.targetText)

			self.button = QPushButton('Add')
			self.button.clicked.connect(self.add_column)
			self.layout.addWidget(self.button)

			self.doneButton = QPushButton('Done')
			self.doneButton.clicked.connect(self.done)
			self.layout.addWidget(self.doneButton)
		self.setLayout(self.layout)



	def done(self):
		with open('preferences.py', 'w') as f:
			f.write('setup = True')
		setup = True
		if self.w is None:
			self.w = MainWindow()
		self.w.show()
		self.close()

	def add_column(self):
		goalValue = self.goalText.text().replace(' ', '_')
		comboboxValue = self.combobox.currentText()
		targetValue = self.targetText.text().replace(' ', '_')
		if(goalValue in ['', '_', 'Goal_Name']):
			if self.pw is None:
				self.pw = ErrorPopup()
			self.pw.label.setText('Please add Goal Name')
			self.pw.show()
			self.goalText.setText('Goal Name')
			self.targetText.setText(self.target_strings[comboboxValue])
		elif(targetValue in ['', '_', 'Target', 'Goal', 'Goal_Category_Name']):
			if self.pw is None:
				self.pw = ErrorPopup()
			self.pw.label.setText(f'Please add {self.target_strings[comboboxValue]} value')
			self.pw.show()
			self.goalText.setText('Goal Name')
		elif(comboboxValue == 'Reference Goal'):
			query = QSqlQuery()
			query.exec_(f'''
				ALTER TABLE log
				ADD COLUMN {goalValue} REAL''')
			query.exec_(f'''
				ALTER TABLE log
				ADD COLUMN {targetValue} REAL''')
			query.exec_(f'''
				INSERT INTO variables (Variable, GoalType, Goal)
				VALUES
				("{goalValue}", "{comboboxValue}", "{targetValue}"),
				("{targetValue}", "Reference Category", "")
				''')
			self.layout.removeWidget(self.button)
			self.layout.removeWidget(self.goalText)
			self.layout.removeWidget(self.targetText)
			self.button = None
			self.goalText = None
			self.targetText = None
		else:
			query = QSqlQuery()
			query.exec_(f'''
				ALTER TABLE log
				ADD COLUMN {goalValue} REAL''')
			query.exec_(f'''
				INSERT INTO variables (Variable, GoalType, Goal)
				VALUES
				("{goalValue}", "{comboboxValue}", "{targetValue}")
				''')
			self.layout.removeWidget(self.button)
			self.layout.removeWidget(self.goalText)
			self.layout.removeWidget(self.targetText)
			self.button = None
			self.goalText = None
			self.targetText = None

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class ErrorPopup(QWidget):
	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		self.label = QLabel()
		layout.addWidget(self.label)
		self.setLayout(layout)


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

random_generic_strings = ['Great Work!', 'Effort is Progress', 'You\'re doing this! Push yourself!', 
'"Believe you can and you\'re halfway there." - Theodore Roosevelt', '']

random_improve_strings = ['You\'re making great progress towards your goal!', 'Don\'t let your success slow you down!',
'You\'re crushing it!', 'You\'re progress is impressve, keep it up!']

random_disimprove_strings = ['Don\'t let this discourage you, you\'re doing great!', 'One step back won\'t ruin you\'re progress', 
'Don\'t focus on you\'re past failures. Focus on you\'re future successes']

random_reached_goal_string = []

if not setup:
	sw = SetupWindow()
	sw.show()

if ((setup) and (sw is None)):
	w = MainWindow()
	w.show()

app.exec()
