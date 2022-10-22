# Written by Patrick Naylor
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
import sqlite3
from PyQt5.QtCore import Qt
from preferences import setup
from datetime import date

app = QApplication([])


#if(not setup):

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
		layout.addLayout(layout1)
		layout.addLayout(layout2)
		self.setLayout(layout)


	def add_row(self):
		print(self.model.rowCount())
		ret = self.model.insertRows(self.model.rowCount(), 1)
		print(ret)

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
			(Variable TEXT, Goal TEXT)
			''')

		query.exec_('''
			CREATE TABLE IF NOT EXISTS journal
			(Date DATETIME, Entry TEXT)
			''')

		self.combobox = QComboBox()
		self.combobox.addItems(['Process Goal', 'Outcome Goal'])
		layout.addWidget(self.combobox)

		self.textbox = QLineEdit(self)
		layout.addWidget(self.textbox)

		self.button = QPushButton('Add')
		self.button.clicked.connect(self.add_column)
		layout.addWidget(self.button)

		self.doneButton = QPushButton('Done')
		self.doneButton.clicked.connect(self.close)
		layout.addWidget(self.doneButton)

		self.setLayout(layout)

	def add_column(self):
		textboxValue = self.textbox.text()
		comboboxValue = self.combobox.currentText()
		self.textbox.setText('')
		query = QSqlQuery()
		query.exec_(f'''
			ALTER TABLE log
			ADD COLUMN {textboxValue} INTEGER''')
		query = QSqlQuery()
		query.exec_(f'''
			INSERT INTO variables (Variable, Goal)
			VALUES("{textboxValue}", "{comboboxValue}")
			''')






if not setup:
	sw = SetupWindow()
	sw.show()

else:
	w = MainWindow()
	w.resize(640, 480)
	w.show()








app.exec()
