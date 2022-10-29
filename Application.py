# Written by Patrick Naylor
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QSize
from preferences import setup
from datetime import date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import random
import re
import pandas as pd

# TODO: Fix bug with empty pd.db file
# TODO: Clean code
# TODO: Comment code
# TODO: Generate sample data with much larger sample size
# TODO: Create clustering model and launch notification system
# TODO: Work on naming/logo
# TODO: Add correlation statements to comments block


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.pw = None
        self.dbw = None
        superLayout = QVBoxLayout()
        layoutHeader = QHBoxLayout()
        line1 = QFrame()
        line1.setStyleSheet("color: #ffa82e")
        line1.setFrameShape(QFrame.HLine)
        layoutHeader.addWidget(line1)
        journalLabel = QLabel("Tracker")
        journalLabel.setAlignment(Qt.AlignCenter)
        journalLabel.setMaximumWidth(50)
        layoutHeader.addWidget(journalLabel)
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color: #ffa82e")
        layoutHeader.addWidget(line2)

        layoutTop = QHBoxLayout()
        layout1 = QVBoxLayout()
        layout1_top = QHBoxLayout()
        self.label = QLabel("Personal Log")
        self.label.setAlignment(Qt.AlignCenter)
        self.infoButtonModel = QPushButton("i", self)
        self.infoButtonModel.setFixedSize(QSize(16, 16))
        self.infoButtonModel.setStyleSheet(
            "border-radius : 8; background-color: #404041"
        )
        self.infoButtonModel.clicked.connect(self.tracker_popup)
        self.refreshModel = QPushButton("Refresh")
        self.refreshModel.clicked.connect(self.refresh_model)
        layout1_top.addWidget(self.label)
        layout1_top.addWidget(self.refreshModel)
        layout1_top.addWidget(self.infoButtonModel)
        layout1.addLayout(layout1_top)

        self.model = QSqlTableModel()
        self.model.setTable("log")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()
        self.view = QTableView()
        self.view.setWindowTitle("Personal Log")
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()
        self.view.setMinimumWidth(360)
        layout1.addWidget(self.view)

        layoutAddRow = QHBoxLayout()
        self.addButton = QPushButton("Add Row")
        self.addButton.clicked.connect(self.add_row)
        self.addColumn = QPushButton("Add a Column")
        self.addColumn.clicked.connect(self.add_column)
        layoutAddRow.addWidget(self.addButton)
        layoutAddRow.addWidget(self.addColumn)
        layout1.addLayout(layoutAddRow)

        layout2 = QVBoxLayout()
        self.label = QLabel("Progress Report")
        self.label.setAlignment(Qt.AlignCenter)
        layout2.addWidget(self.label)
        self.formLayout1 = QFormLayout()
        self.groupBox = QGroupBox()
        variables = {"Variable": [], "GoalType": [], "Goal": []}
        self.query = QSqlQuery()

        self.query.exec_("SELECT Variable, GoalType, Goal FROM variables")
        while self.query.next():
            variables["Variable"].append(self.query.value(0))
            variables["GoalType"].append(self.query.value(1))
            variables["Goal"].append(self.query.value(2))

        print(variables["Variable"])
        for idx in range(len(variables["Variable"])):
            comment = self.progress_comments(
                variables["Variable"][idx],
                variables["GoalType"][idx],
                variables["Goal"][idx],
            )
            if variables["GoalType"][idx] != "Reference Category":
                comment_label = QLabel(comment)
                self.formLayout1.addRow(comment_label)

        self.groupBox.setMinimumWidth(360)
        self.groupBox.setLayout(self.formLayout1)
        scrollarea = QScrollArea()
        scrollarea.setWidget(self.groupBox)
        scrollarea.setWidgetResizable(True)

        layout2.addWidget(scrollarea)

        self.layout3 = QVBoxLayout()
        self.plotProg = QLabel("Progress")
        self.plotProg.setAlignment(Qt.AlignCenter)
        self.layout3.addWidget(self.plotProg)
        columnNum = self.model.columnCount()
        columnNames = [
            self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(columnNum)
        ]

        formLayout = QFormLayout()
        self.groupBox2 = QGroupBox()
        self.query = QSqlQuery()

        self.query.exec_("SELECT Date FROM log;")
        self.date_values = []
        while self.query.next():
            self.date_values.append(self.query.value(0))
        ticks = [
            (tick[:-4] + tick[-2:], idx)
            for idx, tick in enumerate(self.date_values)
            if tick[3:5] in ["01", "15"]
        ]
        combination = list(map(list, zip(*ticks)))
        label_list, tick_list = combination

        self.query.exec_("SELECT Me, Day FROM log")
        me_values = []
        day_values = []
        while self.query.next():
            try:
                me_values.append(float(self.query.value(0)))
            except:
                me_values.append(np.nan)
            try:
                day_values.append(float(self.query.value(1)))
            except:
                day_values.append(np.nan)

        self.figure = MplCanvas(self, width=4, height=4, dpi=100)
        self.figure.p1 = self.figure.axes.plot(self.date_values, me_values, c="#557ff2")
        self.figure.p2 = self.figure.axes.plot(
            self.date_values, day_values, c="#ffa82e"
        )
        self.figure.axes.set_title("Me and Day", color="#ffffff", fontsize="small")
        self.figure.axes.legend(
            ["Me", "Day"],
            fontsize="small",
            facecolor="#1d1e1e",
            labelcolor="#ffffff",
            edgecolor="#bfbfbf",
        )
        self.figure.setMinimumHeight(280)
        self.figure.axes.tick_params(rotation=25, labelsize=8)
        self.figure.axes.set_xticks(tick_list, label_list)
        self.figure.fig.tight_layout(rect=(0, 0.025, 1, 1))
        self.figure.axes.set_facecolor("#1d1e1e")
        self.figure.fig.patch.set_facecolor("#1d1e1e")
        self.figure.axes.spines["bottom"].set_color("#bfbfbf")
        self.figure.axes.spines["top"].set_color("#bfbfbf")
        self.figure.axes.spines["left"].set_color("#bfbfbf")
        self.figure.axes.spines["right"].set_color("#bfbfbf")
        self.figure.axes.tick_params(color="#bfbfbf", labelcolor="#ffffff")

        formLayout.addRow(self.figure)

        for name in columnNames[3:]:
            mean = np.nan
            Gtype = ""
            target = ""
            self.query.exec_(
                f'SELECT Goal, GoalType FROM variables WHERE Variable = "{name}"'
            )
            while self.query.next():
                try:
                    target = float(self.query.value(0))
                except:
                    target = self.query.value(0)
                Gtype = self.query.value(1)

            self.query.exec_(f"SELECT {name} FROM log;")
            self.y_values = []
            while self.query.next():
                if self.query.value(0) == "":
                    self.y_values.append(np.nan)
                else:
                    self.y_values.append(float(self.query.value(0)))

            self.figure = MplCanvas(self, width=4, height=4, dpi=100)

            if Gtype == "Reference Goal":
                target_values = []
                self.query.exec_(f"SELECT {target} FROM log")
                while self.query.next():
                    try:
                        target_values.append(float(self.query.value(0)))
                    except:
                        target_values.append(np.nan)
                rolling_mean = list(
                    rolling_average(np.array(target_values) - np.array(self.y_values))
                )
                zero6 = [0, 0, 0, 0, 0, 0]

                self.figure.p1 = self.figure.axes.plot(
                    self.date_values, zero6 + rolling_mean, c="#557ff2"
                )
                self.figure.axes.set_title(
                    f"7 day rolling difference between\n {name} and {target}",
                    color="#ffffff",
                    fontsize="small",
                )

            else:
                self.figure.p1 = self.figure.axes.plot(
                    self.date_values, self.y_values, c="#557ff2"
                )
                self.figure.axes.set_title(name, color="#ffffff", fontsize="small")

            if isinstance(target, float):
                self.figure.p2 = self.figure.axes.plot(
                    [self.date_values[0], self.date_values[-1]],
                    [target, target],
                    c="#ffa82e",
                )
                self.figure.axes.legend(
                    [name, "Target Value"],
                    fontsize="small",
                    facecolor="#1d1e1e",
                    labelcolor="#ffffff",
                    edgecolor="#bfbfbf",
                )

            self.figure.setMinimumHeight(280)
            self.figure.axes.tick_params(rotation=25, labelsize=8)
            self.figure.axes.set_xticks(tick_list, label_list)
            self.figure.fig.tight_layout(rect=(0, 0.025, 1, 1))
            self.figure.axes.set_facecolor("#1d1e1e")
            self.figure.fig.patch.set_facecolor("#1d1e1e")
            self.figure.axes.spines["bottom"].set_color("#bfbfbf")
            self.figure.axes.spines["top"].set_color("#bfbfbf")
            self.figure.axes.spines["left"].set_color("#bfbfbf")
            self.figure.axes.spines["right"].set_color("#bfbfbf")
            self.figure.axes.tick_params(color="#bfbfbf", labelcolor="#ffffff")
            self.figure.update()

            formLayout.addRow(self.figure)

        self.groupBox2.setMinimumWidth(360)
        self.groupBox2.setLayout(formLayout)

        scrollarea = QScrollArea()
        scrollarea.setWidget(self.groupBox2)
        scrollarea.setWidgetResizable(True)

        self.layout3.addWidget(scrollarea)

        layoutTop.addLayout(layout1)
        layoutTop.addLayout(layout2)
        layoutTop.addLayout(self.layout3)

        layoutMiddle = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("color: #ffa82e")
        layoutMiddle.addWidget(line1)
        journalLabel = QLabel("Journal")
        journalLabel.setAlignment(Qt.AlignCenter)
        journalLabel.setMaximumWidth(50)
        layoutMiddle.addWidget(journalLabel)
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("color: #ffa82e")
        layoutMiddle.addWidget(line2)

        layoutBottom = QHBoxLayout()
        layout1 = QVBoxLayout()
        journalHeader = QHBoxLayout()
        self.dateeditWrite = QDateEdit(calendarPopup=True)
        self.dateeditWrite.setDateTime(QDateTime.currentDateTime())
        journalHeader.addWidget(self.dateeditWrite)
        self.infoButtonJournal = QPushButton("i", self)
        self.infoButtonJournal.setFixedSize(QSize(16, 16))
        self.infoButtonJournal.setStyleSheet(
            "border-radius : 8; background-color: #404041"
        )
        self.infoButtonJournal.clicked.connect(self.journal_popup)
        journalHeader.addWidget(self.infoButtonJournal)
        layout1.addLayout(journalHeader)
        self.journalBox = QPlainTextEdit()
        layout1.addWidget(self.journalBox)
        self.submitButton = QPushButton("Submit Entry")
        self.submitButton.clicked.connect(self.submit_entry)
        layout1.addWidget(self.submitButton)

        layout2 = QVBoxLayout()
        self.dateedit = QDateEdit(calendarPopup=True)
        self.dateedit.setDateTime(QDateTime.currentDateTime())
        layout2.addWidget(self.dateedit)
        self.findButton = QPushButton("Find Entries")
        self.findButton.clicked.connect(self.find_entries)
        layout2.addWidget(self.findButton)
        self.formLayout3 = QFormLayout()
        self.groupBox3 = QGroupBox()
        self.scrollarea3 = QScrollArea()
        self.scrollarea3.setWidget(self.groupBox3)
        self.scrollarea3.setWidgetResizable(True)
        layout2.addWidget(self.scrollarea3)

        layoutBottom.addLayout(layout1)
        layoutBottom.addLayout(layout2)

        superLayout.addLayout(layoutHeader)
        superLayout.addLayout(layoutTop)
        superLayout.addLayout(layoutMiddle)
        superLayout.addLayout(layoutBottom)
        self.setLayout(superLayout)

    def refresh_model(self):
        self.model.select()
        for widget in self.groupBox.children()[1:]:
            widget.setText
        self.query = QSqlQuery()
        variables = {"Variable": [], "GoalType": [], "Goal": []}
        self.query.exec_("SELECT Variable, GoalType, Goal FROM variables")
        while self.query.next():
            variables["Variable"].append(self.query.value(0))
            variables["GoalType"].append(self.query.value(1))
            variables["Goal"].append(self.query.value(2))

        updated_comments = []
        for idx in range(1, len(variables["Variable"])):
            comment = self.progress_comments(
                variables["Variable"][idx],
                variables["GoalType"][idx],
                variables["Goal"][idx],
            )
            updated_comments.append(comment)

        for idx, widget in enumerate(self.groupBox.children()[1:]):
            widget.setText(updated_comments[idx])

        self.query.exec_("SELECT Date FROM log;")
        self.date_values = []
        while self.query.next():
            self.date_values.append(self.query.value(0))
        ticks = [
            (tick[:-4] + tick[-2:], idx)
            for idx, tick in enumerate(self.date_values)
            if tick[3:5] in ["01", "15"]
        ]
        combination = list(map(list, zip(*ticks)))
        label_list, tick_list = combination

        self.query.exec_("SELECT Me, Day FROM log")
        me_values = []
        day_values = []
        while self.query.next():
            try:
                me_values.append(float(self.query.value(0)))
            except:
                me_values.append(np.nan)
            try:
                day_values.append(float(self.query.value(1)))
            except:
                day_values.append(np.nan)

        self.groupBox2.children()[1].p1[0].set_ydata(me_values)
        self.groupBox2.children()[1].p2[0].set_ydata(day_values)
        self.groupBox2.children()[1].p1[0].set_xdata(self.date_values)
        self.groupBox2.children()[1].p2[0].set_xdata(self.date_values)

        self.groupBox2.children()[1].draw()
        columnNum = self.model.columnCount()
        columnNames = [
            self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(columnNum)
        ]
        for idx, name in enumerate(columnNames[3:]):
            mean = np.nan
            Gtype = ""
            target = ""
            self.query.exec_(
                f'SELECT Goal, GoalType FROM variables WHERE Variable = "{name}"'
            )
            while self.query.next():
                try:
                    target = float(self.query.value(0))
                except:
                    target = self.query.value(0)
                Gtype = self.query.value(1)

            self.query.exec_(f"SELECT {name} FROM log;")
            self.y_values = []
            while self.query.next():
                if self.query.value(0) == "":
                    self.y_values.append(np.nan)
                else:
                    self.y_values.append(float(self.query.value(0)))

            self.figure = MplCanvas(self, width=4, height=4, dpi=100)

            if Gtype == "Reference Goal":
                target_values = []
                self.query.exec_(f"SELECT {target} FROM log")
                while self.query.next():
                    try:
                        target_values.append(float(self.query.value(0)))
                    except:
                        target_values.append(np.nan)
                rolling_mean = list(
                    rolling_average(np.array(target_values) - np.array(self.y_values))
                )
                zero6 = [0, 0, 0, 0, 0, 0]

                self.groupBox2.children()[idx + 2].p1[0].set_ydata(zero6 + rolling_mean)
                self.groupBox2.children()[idx + 2].p1[0].set_xdata(self.date_values)
                self.groupBox2.children()[idx + 2].draw()
            else:
                self.groupBox2.children()[idx + 2].p1[0].set_ydata(self.y_values)
                self.groupBox2.children()[idx + 2].p1[0].set_xdata(self.date_values)
                self.groupBox2.children()[idx + 2].draw()

    def add_column(self):
        if self.dbw is None:
            self.dbw = CreateDBWindow()
        self.dbw.show()
        self.dbw.w = Nothing()

    def tracker_popup(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label.setText(
            """PERSONAL TRACKER:
This is where you can track your personal goals.
To add a row hit the 'Add Row' button. Once the next date is
added you can edit the empty cells by double clicking
and inputting your values."""
        )
        self.pw.show()

    def journal_popup(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label.setText(
            """JOURNAL:
Journaling is a great way to keep track of your life.
STAY ON TRACK provides a journal editor where you can make entries 
to your journal. For many it's easier to regularly journal by using
a paper notebook. If you choose to use your own notebook make sure you
mark down the dates or consider transcribing your entries here.
			"""
        )
        self.pw.show()

    def find_entries(self):
        month = str(self.dateedit.date().month())
        if len(month) == 1:
            month = "0" + month
        day = str(self.dateedit.date().day())
        if len(day) == 1:
            day = "0" + day
        year = str(self.dateedit.date().year())
        query = QSqlQuery()
        query.exec_(
            f'''
			SELECT * FROM journal 
			WHERE Date = "{month}-{day}-{year}"'''
        )
        self.entries = []
        self.times = []
        while query.next():
            self.entries.append(query.value(1))
            self.times.append(query.value(2))
        for (entry, time) in zip(self.entries, self.times):
            entry_split = entry.split("\n")
            text = [
                re.sub("(.{100})", "\\1-\n", text, 0, re.DOTALL) for text in entry_split
            ]
            text = "\n".join(text)
            label = QLabel(f"{time} - {text}")

            self.formLayout3.addRow(label)
        self.groupBox3.setLayout(self.formLayout3)
        self.scrollarea3.update()

    def add_row(self):
        self.query.exec_(
            """SELECT Date FROM log
			ORDER BY Date DESC
			LIMIT 1"""
        )
        prev_date = ""
        while self.query.next():
            prev_date = self.query.value(0)
        next_date = f"{prev_date[:3]}{int(prev_date[3:5]) +1}{prev_date[5:]}"
        print(next_date)
        self.query.exec_(
            f"""INSERT INTO log (Date)
			VALUES ("{next_date}")"""
        )
        self.model.select()

    def submit_entry(self):
        entry = self.journalBox.document()
        month = str(self.dateeditWrite.date().month())
        if len(month) == 1:
            month = "0" + month
        day = str(self.dateeditWrite.date().day())
        if len(day) == 1:
            day = "0" + day
        year = str(self.dateeditWrite.date().year())
        today_str = f"{month}-{day}-{year}"
        time = f"{QDateTime.currentDateTime().time().hour()}:{QDateTime.currentDateTime().time().minute()}"
        query = QSqlQuery()
        query.exec_(
            f"""
			INSERT INTO journal (Date, Entry, TimeStamp)
			VALUES("{today_str}", "{entry.toPlainText()}", "{time}")
			"""
        )
        self.journalBox.clear()

    def progress_comments(self, name, gtype, target):
        self.query.exec_(f"SELECT {name} FROM log")
        data_values = []
        while self.query.next():
            try:
                data_values.append(float(self.query.value(0)))
            except ValueError:
                data_values.append(np.nan)
        if gtype == "Process Goal":
            total_avg = np.nanmean(np.array(data_values))
            last_seven = np.nanmean(np.array(data_values[-7:]))
            total_diff = abs(float(target) - total_avg)
            seven_diff = abs(float(target) - last_seven)

            if total_diff > seven_diff:
                closer_or_further = "closer to"
                percent_num = (total_diff - seven_diff) / seven_diff
                percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
                rand_str = random.choice(random_improve_strings)
            elif total_diff < seven_diff:
                closer_or_further = "further from"
                percent_num = (seven_diff - total_diff) / total_diff
                percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
                rand_str = random.choice(random_disimprove_strings)
            else:
                rand_str = random.choice(random_generic_strings)
                return f"""<font color="white">over your last seven entries your average </font><font color="#557ff2">{name}<br>
has been equal to your overall average<br>
</font><font color="#f5f398">{rand_str}</font>"""

            return f"""<font color="white">Over your last seven entries your average </font><font color="#557ff2">{name}</font><font color="white"><br>
have been {percent}{closer_or_further} your target of </font><font color="#557ff2">{str(target)}</font><font color="white"><br>
than your overall average.<br>
</font><font color="#f5f398">{rand_str}</font>"""

        elif gtype == "Outcome Goal":
            last_seven = np.nanmean(np.array(data_values[-7:]))
            prev_seven = np.nanmean(np.array(data_values[-14:-7]))
            last_seven_diff = abs(float(target) - last_seven)
            prev_seven_diff = abs(float(target) - prev_seven)

            if last_seven_diff > prev_seven_diff:
                closer_or_further = "further from"
                percent_num = round(last_seven_diff - prev_seven_diff, 2)
                percent = f'</font><font color="#ffa82e">{str(percent_num)} </font><font color="white">'
                rand_str = random.choice(random_disimprove_strings)

            elif last_seven_diff < prev_seven_diff:
                closer_or_further = "closer to"
                percent_num = round(prev_seven_diff - last_seven_diff, 2)
                percent = f'</font><font color="#ffa82e">{str(percent_num)} </font><font color="white">'
                rand_str = random.choice(random_improve_strings)
            else:
                rand_str = random.choice(random_generic_strings)
                return f"""<font color="white">Over your last seven days you hav not made<br> 
any progress towards your goal of </font><font color="#557ff2">{target}</font><font color="white"><br>
</font><font color="#f5f398">{rand_str}</font>"""

            return f"""<font color="white">Over your last seven entries your progress towards your<br> 
</font><font color="#557ff2">{name}</font><font color="white"> goal is {percent}{closer_or_further} your goal of </font><font color="#557ff2">{target}</font><font color="white"><br> 
then after your previous seven.<br>
</font><font color="#f5f398">{rand_str}</font>"""
        elif gtype == "Reference Goal":
            self.query.exec_(f"SELECT {str(target)} FROM log")
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
                closer_or_further = "closer to"
                percent_num = (total_diff - seven_diff) / seven_diff
                percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
                rand_str = random.choice(random_improve_strings)
            elif total_diff < seven_diff:
                closer_or_further = "further from"
                percent_num = (seven_diff - total_diff) / total_diff
                percent = f'</font><font color="#ffa82e">{str(round(percent_num * 100, 2))}% </font><font color="white">'
                rand_str = random.choice(random_disimprove_strings)
            else:
                rand_str = random.choice(random_generic_strings)
                return f"""<font color="white">Over your last seven entries your </font><font color="#557ff2">{name}</font><font color="white"> is no<br> 
closer to your </font><font color="#557ff2">{target}</font><font color="white"> than your overall average<br>
</font><font color="#f5f398">{rand_str}</font>"""

            return f"""<font color="white">Over your last seven entries your </font><font color="#557ff2">{name}</font><font color="white"> is<br> 
{percent} {closer_or_further} </font><font color="#557ff2">{target}</font><font color="white"> than your overall average<br>
</font><font color="#f5f398">{rand_str}</font>"""
        else:
            return ""


class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dbw = None
        layout = QVBoxLayout()
        self.label = QLabel("Setup Window")
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
        self.infoLabelLayout = QHBoxLayout()
        self.label = QLabel("Create DB Window")
        self.infoButton = QPushButton("i", self)
        self.infoButton.setFixedSize(QSize(16, 16))
        self.infoButton.setStyleSheet("border-radius : 8; background-color: #404041")
        self.infoButton.clicked.connect(self.setup_popup)
        self.infoLabelLayout.addWidget(self.label)
        self.infoLabelLayout.addWidget(self.infoButton)
        self.layout.addLayout(self.infoLabelLayout)
        self.w = None
        self.layout.addWidget(self.label)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("personal_data.db")
        self.pw = None

        if not self.db.open():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error in Database Creation")
            retval = msg.exec_()
            return False
        query = QSqlQuery()

        query.exec_(
            """
			CREATE TABLE IF NOT EXISTS log
			(Date DATETIME, Me INTEGER, Day INTEGER)
			"""
        )

        query.exec_(
            """
			CREATE TABLE IF NOT EXISTS variables
			(Variable TEXT, GoalType TEXT, Goal REAL)
			"""
        )

        query.exec_(
            """
			CREATE TABLE IF NOT EXISTS journal
			(Date DATETIME, Entry TEXT, Timestamp TEXT)
			"""
        )
        self.button = None
        self.doneButton = None
        self.combobox = QComboBox()
        self.combobox.addItems(
            ["Goal Type", "Process Goal", "Outcome Goal", "Reference Goal"]
        )
        self.layout.addWidget(self.combobox)

        self.checkComboBtn = QPushButton("Enter")
        self.checkComboBtn.clicked.connect(self.generate_menu)
        self.layout.addWidget(self.checkComboBtn)

        self.setLayout(self.layout)

    def generate_menu(self):
        self.pw = None
        self.target_strings = {
            "Process Goal": "Target",
            "Outcome Goal": "Target",
            "Reference Goal": "Goal Category Name",
        }
        if self.button != None:
            self.layout.removeWidget(self.button)
            self.layout.removeWidget(self.doneButton)
            self.layout.removeWidget(self.goalText)
            self.layout.removeWidget(self.targetText)
            self.button = None
            self.doneButton = None
            self.goalText = None
            self.targetText = None
        if self.combobox.currentText() == "Goal Type":
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText("Please select a Goal Type")
            self.pw.show()
        elif self.combobox.currentText() == "Process Goal":
            self.goalText = QLineEdit("Goal Name")
            self.targetText = QLineEdit(self.target_strings["Process Goal"])
            self.layout.addWidget(self.goalText)
            self.layout.addWidget(self.targetText)

            self.button = QPushButton("Add")
            self.button.clicked.connect(self.add_column)
            self.layout.addWidget(self.button)

            self.doneButton = QPushButton("Done")
            self.doneButton.clicked.connect(self.done)
            self.layout.addWidget(self.doneButton)
        elif self.combobox.currentText() == "Outcome Goal":
            self.goalText = QLineEdit("Goal Name")
            self.targetText = QLineEdit(self.target_strings["Outcome Goal"])
            self.layout.addWidget(self.goalText)
            self.layout.addWidget(self.targetText)

            self.button = QPushButton("Add")
            self.button.clicked.connect(self.add_column)
            self.layout.addWidget(self.button)

            self.doneButton = QPushButton("Done")
            self.doneButton.clicked.connect(self.done)
            self.layout.addWidget(self.doneButton)
        else:
            self.goalText = QLineEdit("Goal Name")
            self.targetText = QLineEdit(self.target_strings["Reference Goal"])
            self.layout.addWidget(self.goalText)
            self.layout.addWidget(self.targetText)

            self.button = QPushButton("Add")
            self.button.clicked.connect(self.add_column)
            self.layout.addWidget(self.button)

            self.doneButton = QPushButton("Done")
            self.doneButton.clicked.connect(self.done)
            self.layout.addWidget(self.doneButton)
        self.setLayout(self.layout)

    def done(self):
        with open("preferences.py", "w") as f:
            f.write("setup = True")
        setup = True
        if self.w is None:
            self.w = MainWindow()
        self.w.show()
        self.close()

    def setup_popup(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label.setText(
            """SETUP:
In order to track your life you need to add the categories you want
to track. STAY ON TRACK supports three different types of goals.

Process Goals: Goals where you intend to maintain a daily target
example: I want to do 30 push ups a day. Here your "Goal Name"
would be push ups and your "Target" would be 30.

Outcome Goals: Goals where you have a target you want to reach over
time.
example: I want to be able to run a marathon. Here you would track how
many miles you run each day. The "Goal Name" would be named miles and the
"Target" would be 26.2

Reference Goals: Goals that change every day.
example: I want to complete all of my daily work tasks. For this you 
would track your tasks and tasks completed each day. The "Goal Name" would
be tasks completed and the "Goal Category Name" would be tasks
"""
        )
        self.pw.show()

    def add_column(self):
        goalValue = self.goalText.text().replace(" ", "_")
        comboboxValue = self.combobox.currentText()
        targetValue = self.targetText.text().replace(" ", "_")
        if goalValue in ["", "_", "Goal_Name"]:
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText("Please add Goal Name")
            self.pw.show()
            self.goalText.setText("Goal Name")
            self.targetText.setText(self.target_strings[comboboxValue])
        elif targetValue in ["", "_", "Target", "Goal", "Goal_Category_Name"]:
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText(
                f"Please add {self.target_strings[comboboxValue]} value"
            )
            self.pw.show()
            self.goalText.setText("Goal Name")
        elif comboboxValue == "Reference Goal":
            query = QSqlQuery()
            query.exec_(
                f"""
				ALTER TABLE log
				ADD COLUMN {goalValue} REAL"""
            )
            query.exec_(
                f"""
				ALTER TABLE log
				ADD COLUMN {targetValue} REAL"""
            )
            query.exec_(
                f"""
				INSERT INTO variables (Variable, GoalType, Goal)
				VALUES
				("{goalValue}", "{comboboxValue}", "{targetValue}"),
				("{targetValue}", "Reference Category", "")
				"""
            )
            self.layout.removeWidget(self.button)
            self.layout.removeWidget(self.goalText)
            self.layout.removeWidget(self.targetText)
            self.button = None
            self.goalText = None
            self.targetText = None
        else:
            query = QSqlQuery()
            query.exec_(
                f"""
				ALTER TABLE log
				ADD COLUMN {goalValue} REAL"""
            )
            query.exec_(
                f"""
				INSERT INTO variables (Variable, GoalType, Goal)
				VALUES
				("{goalValue}", "{comboboxValue}", "{targetValue}")
				"""
            )
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
        self.p1 = []
        self.p2 = []
        super(MplCanvas, self).__init__(self.fig)


class Popup(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel()
        layout.addWidget(self.label)
        self.setLayout(layout)


def rolling_average(a, n=7):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1 :] / n


class Nothing:
    def __init__(self):
        self.name = "Nothing"

    def show(self):
        self.name = "Nothing2"


def load_cluster_data():
    query = QSqlQuery()
    query.exec_(
        """SELECT Variable, GoalType, Goal FROM variables
    	ORDER BY ListOrder"""
    )
    variables = ["Date", "Me", "Day"]
    types = [
        "",
        "",
        "",
    ]
    targets = [
        "",
        "",
        "",
    ]

    data_dict = {}
    while query.next():
        variables.append(query.value(0))
        types.append(query.value(1))
        targets.append(query.value(2))
    print(variables)
    var_dict = {"var": variables, "gtype": types, "target": targets}
    # print(var_dict)
    var_df = pd.DataFrame.from_dict(var_dict)

    for var in variables:
        data_dict[var] = []
    query.exec_("SELECT * FROM log")
    while query.next():
        for idx, key in enumerate(data_dict.keys()):
            if key != "Date":
                try:
                    data_dict[key].append(float(query.value(idx)))
                except:
                    data_dict[key].append(np.nan)
            else:
                data_dict[key].append(query.value(idx))

    df = pd.DataFrame.from_dict(data_dict)
    # print(df)
    for col in df.columns:
        data = var_df[var_df["var"] == col]
        gtype = np.array(data["gtype"])[0]
        if gtype == "Outcome Goal":
            df[col] = df[col].interpolate(method="linear", limit_areg="inside")

        elif col != "Date":
            mean = df[col].mean()
            m1 = df[col].shift().notna()
            m2 = df[col].shift(-1).notna()
            m3 = df[col].isna()
            df.loc[m1 & m2 & m3, col] = mean

    date_len = np.shape(df["Date"])[0]
    one_thirds_date = date_len - (float(date_len) * (2 / 3))
    drops = []
    for (gtype, col, target) in zip(types, variables, targets):
        if gtype == "Process Goal":
            df[col] = df[col] / df[col].abs().max()
        if gtype == "Outcome Goal":
            df[col] = np.diff(df[col], prepend=[0])
            df[col] = df[col] / df[col].abs().max()
        if gtype == "Reference Goal":
            df[col] = df[col] / df[target]
        elif gtype == "Reference Category":
            drops.append(col)
        elif df[col].isna().sum() > one_thirds_date:
            drops.append(col)
    drops.append("Date")
    df.reset_index(inplace=True)
    df["Me"] = df["Me"] / df["Me"].abs().max()
    df["Day"] = df["Day"] / df["Day"].abs().max()
    print(df)
    df = df.drop(drops, axis=1)
    df = df.dropna(axis=0, how="any")

    return df


random_generic_strings = [
    "Great Work!",
    "Effort is Progress",
    "You're doing this! Push yourself!",
    '"Believe you can and you\'re halfway there." - Theodore Roosevelt',
    "",
]

random_improve_strings = [
    "You're making great progress towards your goal!",
    "Don't let your success slow you down!",
    "You're crushing it!",
    "You're progress is impressve, keep it up!",
]

random_disimprove_strings = [
    "Don't let this discourage you, you're doing great!",
    "One step back won't ruin you're progress",
    "Don't focus on you're past failures. Focus on you're future successes",
]

random_reached_goal_string = []

if __name__ == "__main__":
    app = QApplication([])
    if setup:
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("personal_data.db")
        db.close()
        db.open()
        cluster_df = load_cluster_data()
        print(cluster_df)
    app.setStyle("Fusion")
    sw = None
    if not setup:
        sw = SetupWindow()
        sw.show()

    if (setup) and (sw is None):
        w = MainWindow()
        w.show()

    app.exec()
