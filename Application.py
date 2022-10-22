# Written by Patrick Naylor
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
import sqlite3
from PyQt5.QtCore import Qt
from preferences import setup

app = QApplication([])
app.setStyle('Macintosh')

#if(not setup):

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		self.label = QLabel("Main Window")
		layout.addWidget(self.label)
		self.db = QSqlDatabase.addDatabase('QSQLITE')
		self.db.setDatabaseName('personal_data.db')

		self.model = QSqlTableModel()
		self.model.setTable('log')
		self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
		self.model.select()
		self.view = QTableView()
		self.view.setModel(self.model)
		self.view.resizeColumnsToContents()
		layout.addWidget(self.view)

		self.addButton = QPushButton('Add a Row')
		self.addButton.clicked.connect(self.addrow)
		layout.addWidget(self.addButton)
		self.setLayout(layout)

	def addrow(self):
		print(self.model.rowCount())
		ret = self.model.insertRows(self.model.rowCount(), 1)
		print(ret)




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
	w.show()








app.exec()
