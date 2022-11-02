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
from sklearn import cluster
from sklearn import metrics

# TODO: Fix bug with empty pd.db file
# TODO: Comment code
# TODO: Finalize reate clustering model
# TODO: Work on naming/logo
# TODO: Add correlation statements to comments block

# Main window to view stats and journal. Also where users and log journal entries
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #Initialize initial layout
        self.pw = None
        self.dbw = None
        layout_super = QVBoxLayout()
        layout_header = QHBoxLayout()
        line_1 = QFrame()
        line_1.setStyleSheet("color: #ffa82e")
        line_1.setFrameShape(QFrame.HLine)
        layout_header.addWidget(line_1)
        label_journal = QLabel("Tracker")
        label_journal.setAlignment(Qt.AlignCenter)
        label_journal.setMaximumWidth(50)
        layout_header.addWidget(label_journal)
        line_2 = QFrame()
        line_2.setFrameShape(QFrame.HLine)
        line_2.setStyleSheet("color: #ffa82e")
        layout_header.addWidget(line_2)

        #Generate window with sql table data and addrow/refresh/info buttons
        layout_top = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_1top = QHBoxLayout()
        self.label_log = QLabel("Personal Log")
        self.label_log.setAlignment(Qt.AlignCenter)
        self.button_infomodel = QPushButton("i", self)
        self.button_infomodel.setFixedSize(QSize(16, 16))
        self.button_infomodel.setStyleSheet(
            "border-radius : 8; background-color: #404041"
        )
        self.button_infomodel.clicked.connect(self._tracker_popup_)
        self.refresh_model = QPushButton("Refresh")
        self.refresh_model.clicked.connect(self._refresh_model_)
        layout_1top.addWidget(self.label_log)
        layout_1top.addWidget(self.refresh_model)
        layout_1top.addWidget(self.button_infomodel)
        layout_1.addLayout(layout_1top)

        #Table reader
        self.model = QSqlTableModel()
        self.model.setTable("log")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()
        self.view = QTableView()
        self.view.setWindowTitle("Personal Log")
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()
        self.view.setMinimumWidth(360)
        layout_1.addWidget(self.view)

        layout_addrow = QHBoxLayout()
        self.button_addrow = QPushButton("Add Row")
        self.button_addrow.clicked.connect(self._add_row_)
        self.button_addrowcolumn = QPushButton("Add a Column")
        self.button_addrowcolumn.clicked.connect(self._add_column_)
        layout_addrow.addWidget(self.button_addrow)
        layout_addrow.addWidget(self.button_addrowcolumn)
        layout_1.addLayout(layout_addrow)

        #Generate panel with text progress statements.
        #Comments collected with self._progress_coments_
        layout_2 = QVBoxLayout()
        self.label_progress = QLabel("Progress Report")
        self.label_progress.setAlignment(Qt.AlignCenter)
        layout_2.addWidget(self.label_progress)
        self.layout_form1 = QFormLayout()
        self.groupbox_1 = QGroupBox()
        _variables = {"Variable": [], "GoalType": [], "Goal": []}
        self.query = QSqlQuery()

        self.query.exec_("SELECT Variable, GoalType, Goal FROM variables")
        while self.query.next():
            _variables["Variable"].append(self.query.value(0))
            _variables["GoalType"].append(self.query.value(1))
            _variables["Goal"].append(self.query.value(2))

        for idx in range(len(_variables["Variable"])):
            comment = self._progress_comments_(
                _variables["Variable"][idx],
                _variables["GoalType"][idx],
                _variables["Goal"][idx],
            )
            if _variables["GoalType"][idx] != "Reference Category":
                comment_label = QLabel(comment)
                self.layout_form1.addRow(comment_label)

        #Make comments scrollable
        self.groupbox_1.setMinimumWidth(360)
        self.groupbox_1.setLayout(self.layout_form1)
        scrollarea_1 = QScrollArea()
        scrollarea_1.setWidget(self.groupbox_1)
        scrollarea_1.setWidgetResizable(True)

        layout_2.addWidget(scrollarea_1)
        

        #Generate window with progress plots
        self.layout_3 = QVBoxLayout()
        self.label_plotprog = QLabel("Progress")
        self.label_plotprog.setAlignment(Qt.AlignCenter)
        self.layout_3.addWidget(self.label_plotprog)
        _column_num = self.model.columnCount()
        _column_names = [
            self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(_column_num)
        ]

        layout_form = QFormLayout()
        self.groupbox_2 = QGroupBox()
        self.query = QSqlQuery()

        self.query.exec_("SELECT Date FROM log;")
        self._date_values_ = []
        while self.query.next():
            self._date_values_.append(self.query.value(0))
        _ticks = [
            (tick[:-4] + tick[-2:], idx)
            for idx, tick in enumerate(self._date_values_[-100:])
            if tick[3:5] in ["01", "15"]
        ]
        _combination = list(map(list, zip(*_ticks)))
        _label_list, _tick_list = _combination

        self.query.exec_("SELECT Me, Day FROM log")
        _me_values = []
        _day_values = []
        while self.query.next():
            try:
                _me_values.append(float(self.query.value(0)))
            except:
                _me_values.append(np.nan)
            try:
                _day_values.append(float(self.query.value(1)))
            except:
                _day_values.append(np.nan)

        #Plot Me and Day data. Same for all users
        self.figure = MplCanvas(self, width=4, height=4, dpi=100)
        self.figure.p1 = self.figure.axes.plot(
            self._date_values_[-100:], _me_values[-100:], c="#557ff2"
        )
        self.figure.p2 = self.figure.axes.plot(
            self._date_values_[-100:], _day_values[-100:], c="#ffa82e"
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
        self.figure.axes.set_xticks(_tick_list, _label_list)
        self.figure.fig.tight_layout(rect=(0, 0.025, 1, 1))
        self.figure.axes.set_facecolor("#1d1e1e")
        self.figure.fig.patch.set_facecolor("#1d1e1e")
        self.figure.axes.spines["bottom"].set_color("#bfbfbf")
        self.figure.axes.spines["top"].set_color("#bfbfbf")
        self.figure.axes.spines["left"].set_color("#bfbfbf")
        self.figure.axes.spines["right"].set_color("#bfbfbf")
        self.figure.axes.tick_params(color="#bfbfbf", labelcolor="#ffffff")

        layout_form.addRow(self.figure)

       	#Plot remaining variables
        for name in _column_names[3:]:
            _mean = np.nan
            _goal_type = ""
            _target = ""
            self.query.exec_(
                f'SELECT Goal, GoalType FROM variables WHERE Variable = "{name}"'
            )
            while self.query.next():
                try:
                    _target = float(self.query.value(0))
                except:
                    _target = self.query.value(0)
                _goal_type = self.query.value(1)

            self.query.exec_(f"SELECT {name} FROM log;")
            self._y_values_ = []
            while self.query.next():
                if self.query.value(0) == "":
                    self._y_values_.append(np.nan)
                else:
                    self._y_values_.append(float(self.query.value(0)))

            self.figure = MplCanvas(self, width=4, height=4, dpi=100)

            #Plot variables that are reference goals
            if _goal_type == "Reference Goal":
                _target_values = []
                self.query.exec_(f"SELECT {_target} FROM log")
                while self.query.next():
                    try:
                        _target_values.append(float(self.query.value(0)))
                    except:
                        _target_values.append(np.nan)
                _rolling_mean = list(
                    rolling_average(np.array(_target_values) - np.array(self._y_values_))
                )
                _zero_6 = [0, 0, 0, 0, 0, 0]

                self.figure.p1 = self.figure.axes.plot(
                    self._date_values_[-100:], (_zero_6 + _rolling_mean)[-100:], c="#557ff2"
                )
                self.figure.axes.set_title(
                    f"7 day rolling difference between\n {name} and {_target}",
                    color="#ffffff",
                    fontsize="small",
                )

                #Plot variables that are not reference variables
            else:
                self.figure.p1 = self.figure.axes.plot(
                    self._date_values_[-100:], self._y_values_[-100:], c="#557ff2"
                )
                self.figure.axes.set_title(name, color="#ffffff", fontsize="small")

            if isinstance(_target, float):
                self.figure.p2 = self.figure.axes.plot(
                    [self._date_values_[-100], self._date_values_[-1]],
                    [_target, _target],
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
            self.figure.axes.set_xticks(_tick_list, _label_list)
            self.figure.fig.tight_layout(rect=(0, 0.025, 1, 1))
            self.figure.axes.set_facecolor("#1d1e1e")
            self.figure.fig.patch.set_facecolor("#1d1e1e")
            self.figure.axes.spines["bottom"].set_color("#bfbfbf")
            self.figure.axes.spines["top"].set_color("#bfbfbf")
            self.figure.axes.spines["left"].set_color("#bfbfbf")
            self.figure.axes.spines["right"].set_color("#bfbfbf")
            self.figure.axes.tick_params(color="#bfbfbf", labelcolor="#ffffff")
            self.figure.update()

            layout_form.addRow(self.figure)

        self.groupbox_2.setMinimumWidth(360)
        self.groupbox_2.setLayout(layout_form)

       	#Make plots scrollable
        scrollarea_2 = QScrollArea()
        scrollarea_2.setWidget(self.groupbox_2)
        scrollarea_2.setWidgetResizable(True)

        self.layout_3.addWidget(scrollarea_2)

        layout_top.addLayout(layout_1)
        layout_top.addLayout(layout_2)
        layout_top.addLayout(self.layout_3)

        #Divider between top and bottom layers
        layout_middle = QHBoxLayout()
        line_1 = QFrame()
        line_1.setFrameShape(QFrame.HLine)
        line_1.setStyleSheet("color: #ffa82e")
        layout_middle.addWidget(line_1)
        label_journal = QLabel("Journal")
        label_journal.setAlignment(Qt.AlignCenter)
        label_journal.setMaximumWidth(50)
        layout_middle.addWidget(label_journal)
        line_2 = QFrame()
        line_2.setFrameShape(QFrame.HLine)
        line_2.setStyleSheet("color: #ffa82e")
        layout_middle.addWidget(line_2)

        #Generae panel to add entries to specific dates in journal
        layout_bottom = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_journalheader = QHBoxLayout()
        self.dateedit_write = QDateEdit(calendarPopup=True)
        self.dateedit_write.setDateTime(QDateTime.currentDateTime())
        layout_journalheader.addWidget(self.dateedit_write)
        self.button_infojournal = QPushButton("i", self)
        self.button_infojournal.setFixedSize(QSize(16, 16))
        self.button_infojournal.setStyleSheet(
            "border-radius : 8; background-color: #404041"
        )
        self.button_infojournal.clicked.connect(self._journal_popup_)
        layout_journalheader.addWidget(self.button_infojournal)
        layout_1.addLayout(layout_journalheader)
        self.textbox_journal = QPlainTextEdit()
        layout_1.addWidget(self.textbox_journal)
        self.button_submit = QPushButton("Submit Entry")
        self.button_submit.clicked.connect(self._submit_entry_)
        layout_1.addWidget(self.button_submit)

        #Generate page that reads journal entries from specific dates
        layout_2 = QVBoxLayout()
        self.dateedit_read = QDateEdit(calendarPopup=True)
        self.dateedit_read.setDateTime(QDateTime.currentDateTime())
        layout_2.addWidget(self.dateedit_read)
        self.button_find = QPushButton("Find Entries")
        self.button_find.clicked.connect(self._find_entries_)
        layout_2.addWidget(self.button_find)
        self.layout_form3 = QFormLayout()
        self.groupbox_3 = QGroupBox()
        self.scrollarea_3 = QScrollArea()
        self.scrollarea_3.setWidget(self.groupbox_3)
        self.scrollarea_3.setWidgetResizable(True)
        layout_2.addWidget(self.scrollarea_3)

        layout_bottom.addLayout(layout_1)
        layout_bottom.addLayout(layout_2)

        layout_super.addLayout(layout_header)
        layout_super.addLayout(layout_top)
        layout_super.addLayout(layout_middle)
        layout_super.addLayout(layout_bottom)
        self.setLayout(layout_super)

    #Refresh top panel of main window
    def _refresh_model_(self):
    	#Refresh model
        self.model.select()

        #Refresh progress statements
        for widget in self.groupbox_1.children()[1:]:
            widget.setText
        self.query = QSqlQuery()
        _variables = {"Variable": [], "GoalType": [], "Goal": []}
        self.query.exec_("SELECT Variable, GoalType, Goal FROM variables")
        while self.query.next():
            _variables["Variable"].append(self.query.value(0))
            _variables["GoalType"].append(self.query.value(1))
            _variables["Goal"].append(self.query.value(2))

        _updated_comments = []
        for idx in range(1, len(_variables["Variable"])):
            comment = self._progress_comments_(
                _variables["Variable"][idx],
                _variables["GoalType"][idx],
                _variables["Goal"][idx],
            )
            _updated_comments.append(comment)

        for idx, widget in enumerate(self.groupbox_1.children()[1:]):
            widget.setText(_updated_comments[idx])

        #Refresh plots
        self.query.exec_("SELECT Date FROM log;")
        self._date_values_ = []
        while self.query.next():
            self._date_values_.append(self.query.value(0))
        _ticks = [
            (tick[:-4] + tick[-2:], idx)
            for idx, tick in enumerate(self._date_values_[-100:])
            if tick[3:5] in ["01", "15"]
        ]
        _combination = list(map(list, zip(*_ticks)))
        _label_list, _tick_list = _combination

        self.query.exec_("SELECT Me, Day FROM log")
        _me_values = []
        _day_values = []
        while self.query.next():
            try:
                _me_values.append(float(self.query.value(0)))
            except:
                _me_values.append(np.nan)
            try:
                _day_values.append(float(self.query.value(1)))
            except:
                _day_values.append(np.nan)

        self.groupbox_2.children()[1].p1[0].set_ydata(_me_values)
        self.groupbox_2.children()[1].p2[0].set_ydata(_day_values)
        self.groupbox_2.children()[1].p1[0].set_xdata(self._date_values_)
        self.groupbox_2.children()[1].p2[0].set_xdata(self._date_values_)

        self.groupbox_2.children()[1].draw()
        _column_num = self.model.columnCount()
        _column_names = [
            self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            for col in range(_column_num)
        ]
        for idx, name in enumerate(_column_names[3:]):
            mean = np.nan
            _goal_type = ""
            _target = ""
            self.query.exec_(
                f'SELECT Goal, GoalType FROM variables WHERE Variable = "{name}"'
            )
            while self.query.next():
                try:
                    _target = float(self.query.value(0))
                except:
                    _target = self.query.value(0)
                _goal_type = self.query.value(1)

            self.query.exec_(f"SELECT {name} FROM log;")
            self._y_values_ = []
            while self.query.next():
                if self.query.value(0) == "":
                    self._y_values_.append(np.nan)
                else:
                    self._y_values_.append(float(self.query.value(0)))

            self.figure = MplCanvas(self, width=4, height=4, dpi=100)

            if _goal_type == "Reference Goal":
                _target_values = []
                self.query.exec_(f"SELECT {_target} FROM log")
                while self.query.next():
                    try:
                        _target_values.append(float(self.query.value(0)))
                    except:
                        _target_values.append(np.nan)
                _rolling_mean = list(
                    rolling_average(np.array(_target_values) - np.array(self._y_values_))
                )
                zero6 = [0, 0, 0, 0, 0, 0]

                self.groupbox_2.children()[idx + 2].p1[0].set_ydata(zero6 + _rolling_mean)
                self.groupbox_2.children()[idx + 2].p1[0].set_xdata(self._date_values_)
                self.groupbox_2.children()[idx + 2].draw()
            else:
                self.groupbox_2.children()[idx + 2].p1[0].set_ydata(self._y_values_)
                self.groupbox_2.children()[idx + 2].p1[0].set_xdata(self._date_values_)
                self.groupbox_2.children()[idx + 2].draw()

    #Add new column/variable to sql table
    def _add_column_(self):
        if self.dbw is None:
            self.dbw = CreateDBWindow()
        self.dbw.show()
        self.dbw.w = Nothing()

    #Load sql inormation button window
    def _tracker_popup_(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label_popup.setText(
            """PERSONAL TRACKER:
This is where you can track your personal goals.
To add a row hit the 'Add Row' button. Once the next date is
added you can edit the empty cells by double clicking
and inputting your values."""
        )
        self.pw.show()

    #Load journal information button window
    def _journal_popup_(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label_popup.setText(
            """JOURNAL:
Journaling is a great way to keep track of your life.
STAY ON TRACK provides a journal editor where you can make entries 
to your journal. For many it's easier to regularly journal by using
a paper notebook. If you choose to use your own notebook make sure you
mark down the dates or consider transcribing your entries here.
            """
        )
        self._pw_.show()

    #Find journal entries from specific date
    def _find_entries_(self):
        _month = str(self.dateedit_read.date().month())
        if len(_month) == 1:
            _month = "0" + _month
        _day = str(self.dateedit_read.date().day())
        if len(_day) == 1:
            _day = "0" + _day
        _year = str(self.dateedit_read.date().year())
        query = QSqlQuery()
        query.exec_(
            f'''
            SELECT * FROM journal 
            WHERE Date = "{_month}-{_day}-{_year}"'''
        )
        self._entries_ = []
        self._times_ = []
        while query.next():
            self._entries_.append(query.value(1))
            self._times_.append(query.value(2))
        for (entry, time) in zip(self._entries_, self._times_):
            entry_split = entry.split("\n")
            text = [
                re.sub("(.{100})", "\\1-\n", text, 0, re.DOTALL) for text in entry_split
            ]
            text = "\n".join(text)
            label = QLabel(f"{time} - {text}")

            self.layout_form3.addRow(label)
        self.groupbox_3.setLayout(self.layout_form3)
        self.scrollarea_3.update()

    #Add new row to sql tabel with date as next in sequence
    def _add_row_(self):
        self.query.exec_(
            """SELECT Date FROM log
            ORDER BY Date DESC
            LIMIT 1"""
        )
        _prev_date = ""
        while self.query.next():
            _prev_date = self.query.value(0)
        _next_date = f"{_prev_date[:3]}{int(_prev_date[3:5]) +1}{_prev_date[5:]}"
        self.query.exec_(
            f"""INSERT INTO log (Date)
            VALUES ("{_next_date}")"""
        )
        self.model.select()

    #Submit journal entry to journal table of sql database
    def _submit_entry_(self):
        _entry = self.textbox_journal.document()
        _month = str(self.dateedit_write.date().month())
        if len(_month) == 1:
            _month = "0" + _month
        _day = str(self.dateedit_write.date().day())
        if len(_day) == 1:
            _day = "0" + _day
        _year = str(self.dateedit_write.date().year())
        _today_str = f"{_month}-{_day}-{_year}"
        _time = f"{QDateTime.currentDateTime().time().hour()}:{QDateTime.currentDateTime().time().minute()}"
        query = QSqlQuery()
        query.exec_(
            f"""
            INSERT INTO journal (Date, Entry, TimeStamp)
            VALUES("{_today_str}", "{_entry.toPlainText()}", "{_time}")
            """
        )
        self.textbox_journal.clear()

    #Generate progress comments based on target values and load random encouraging strings
    def _progress_comments_(self, name, gtype, target):
        self.query.exec_(f"SELECT {name} FROM log")
        _data_values = []
        while self.query.next():
            try:
                _data_values.append(float(self.query.value(0)))
            except ValueError:
                _data_values.append(np.nan)
        if gtype == "Process Goal":
            total_avg = np.nanmean(np.array(_data_values))
            last_seven = np.nanmean(np.array(_data_values[-7:]))
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
            last_seven = np.nanmean(np.array(_data_values[-7:]))
            prev_seven = np.nanmean(np.array(_data_values[-14:-7]))
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
            _target_values = []
            while self.query.next():
                if isinstance(self.query.value(0), float):
                    _target_values.append(self.query.value(0))
                else:
                    _target_values.append(np.nan)
            diff = abs(np.array(_target_values) - np.array(_data_values))
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

#Initial window on boot
class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dbw = None
        layout_main = QVBoxLayout()
        self.label_setup = QLabel("Setup Window")
        layout_main.addWidget(self.label_setup)
        self.button_start = QPushButton("Ready to Track Your Life?")
        self.button_start.clicked.connect(self._get_started_)
        layout_main.addWidget(self.button)
        self.setLayout(layout_main)

    #Open window to create db and 'get started'
    def _get_started_(self, checked):
        if self.dbw is None:
            self.dbw = CreateDBWindow()
        self.dbw.show()
        self.close()

#Window where users generate a database with the data they want to track
class CreateDBWindow(QWidget):
    def __init__(self):
    	#Generate initial page with combobox and information buttons
        super().__init__()
        self.layout_super = QVBoxLayout()
        self.layout_infolabel = QHBoxLayout()
        self.label_db = QLabel("Create DB Window")
        self.button_info = QPushButton("i", self)
        self.button_info.setFixedSize(QSize(16, 16))
        self.button_info.setStyleSheet("border-radius : 8; background-color: #404041")
        self.button_info.clicked.connect(self._setup_popup_)
        self.layout_infolabel.addWidget(self.label_db)
        self.layout_infolabel.addWidget(self.button_info)
        self.layout_super.addLayout(self.layout_infolabel)
        self.w = None
        self.layout_super.addWidget(self.label_db)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("personal_data.db")
        self.pw = None

        if not self.db.open():
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Critical)
            messagebox.setText("Error in Database Creation")
            _retval = messagebox.exec_()
            return False
        query = QSqlQuery()

        #Create tables
        query.exec_(
            """
            CREATE TABLE IF NOT EXISTS log
            (Date DATETIME, Me INTEGER, Day INTEGER)
            """
        )

        query.exec_(
            """
            CREATE TABLE IF NOT EXISTS variables
            (Variable TEXT, GoalType TEXT, Goal REAL, ListOrder INTEGER)
            """
        )

        query.exec_(
            """
            CREATE TABLE IF NOT EXISTS journal
            (Date DATETIME, Entry TEXT, Timestamp TEXT)
            """
        )
        self.button_add = None
        self.button_done = None
        self.combobox = QComboBox()
        self.combobox.addItems(
            ["Goal Type", "Process Goal", "Outcome Goal", "Reference Goal"]
        )
        self.layout_super.addWidget(self.combobox)

        self.checkComboBtn = QPushButton("Enter")
        self.checkComboBtn.clicked.connect(self._generate_menu_)
        self.layout_super.addWidget(self.checkComboBtn)

        self.setLayout(self.layout_super)

    #Generate selection screen based on goal type selection
    #Users add everything they want to track
    #Reference goals add an extra column to table with the data that it is being compared to
    def _generate_menu_(self):
        self.pw = None
        self._target_strings_ = {
            "Process Goal": "Target",
            "Outcome Goal": "Target",
            "Reference Goal": "Goal Category Name",
        }
        if self.button_add != None:
            self.layout_super.removeWidget(self.button_add)
            self.layout_super.removeWidget(self.button_done)
            self.layout_super.removeWidget(self.textbox_goal)
            self.layout_super.removeWidget(self.textbox_target)
            self.button_add = None
            self.button_done = None
            self.textbox_goal = None
            self.textbox_target = None
        if self.combobox.currentText() == "Goal Type":
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText("Please select a Goal Type")
            self.pw.show()
        elif self.combobox.currentText() == "Process Goal":
            self.textbox_goal = QLineEdit("Goal Name")
            self.textbox_target = QLineEdit(self._target_strings_["Process Goal"])
            self.layout_super.addWidget(self.textbox_goal)
            self.layout_super.addWidget(self.textbox_target)

            self.button_add = QPushButton("Add")
            self.button_add.clicked.connect(self._add_column_)
            self.layout_super.addWidget(self.button_add)

            self.button_done = QPushButton("Done")
            self.button_done.clicked.connect(self._done_)
            self.layout_super.addWidget(self.button_done)
        elif self.combobox.currentText() == "Outcome Goal":
            self.textbox_goal = QLineEdit("Goal Name")
            self.textbox_target = QLineEdit(self._target_strings_["Outcome Goal"])
            self.layout_super.addWidget(self.textbox_goal)
            self.layout_super.addWidget(self.textbox_target)

            self.button_add = QPushButton("Add")
            self.button_add.clicked.connect(self._add_column_)
            self.layout_super.addWidget(self.button_add)

            self.button_done = QPushButton("Done")
            self.button_done.clicked.connect(self._done_)
            self.layout_super.addWidget(self.button_done)
        else:
            self.textbox_goal = QLineEdit("Goal Name")
            self.textbox_target = QLineEdit(self._target_strings_["Reference Goal"])
            self.layout_super.addWidget(self.textbox_goal)
            self.layout_super.addWidget(self.textbox_target)

            self.button_add = QPushButton("Add")
            self.button_add.clicked.connect(self._add_column_)
            self.layout_super.addWidget(self.button_add)

            self.button_done = QPushButton("Done")
            self.button_done.clicked.connect(self._done_)
            self.layout_super.addWidget(self.button_done)
        self.setLayout(self.layout_super)

    #Finish setup
    def _done_(self):
        with open("preferences.py", "w") as f:
            f.write("setup = True")
        setup = True
        if self.w is None:
            self.w = MainWindow()
        self.w.show()
        self.close()

    #Load informational text on goal types
    def _setup_popup_(self):
        if self.pw is None:
            self.pw = Popup()
        self.pw.label_popup.setText(
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

    #Add columns with selected constraints
    #Adds variable metadata to variables table
    #Adds columns to log table
    def _add_column_(self):
        _goal_value = self.textbox_goal.text().replace(" ", "_")
        _combobox_value = self.combobox.currentText()
        _target_value = self.textbox_target.text().replace(" ", "_")
        query = QSqlQuery()
        query.exec_("SELECT ListOrder FROM variables;")
        _list_orders = []
        while query.next():
            _list_orders.append(query.value(0))
        list_order = np.max(np.array(_list_orders))
        if _goal_value in ["", "_", "Goal_Name"]:
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText("Please add Goal Name")
            self.pw.show()
            self.textbox_goal.setText("Goal Name")
            self.textbox_target.setText(self._target_strings_[_combobox_value])
        elif _target_value in ["", "_", "Target", "Goal", "Goal_Category_Name"]:
            if self.pw is None:
                self.pw = Popup()
            self.pw.label.setText(
                f"Please add {self._target_strings_[_combobox_value]} value"
            )
            self.pw.show()
            self.textbox_goal.setText("Goal Name")
        elif _combobox_value == "Reference Goal":
            query = QSqlQuery()
            query.exec_(
                f"""
                ALTER TABLE log
                ADD COLUMN {_goal_value} REAL"""
            )
            query.exec_(
                f"""
                ALTER TABLE log
                ADD COLUMN {_target_value} REAL"""
            )
            query.exec_(
                f"""
                INSERT INTO variables (Variable, GoalType, Goal)
                VALUES
                ("{_goal_value}", "{_combobox_value}", "{_target_value}", "{list_order}"),
                ("{_target_value}", "Reference Category", "")
                """
            )

            list_order += 1
            self.layout_super.removeWidget(self.button_add)
            self.layout_super.removeWidget(self.textbox_goal)
            self.layout_super.removeWidget(self.textbox_target)
            self.button_add = None
            self.textbox_goal = None
            self.textbox_target = None
        else:
            query = QSqlQuery()
            query.exec_(
                f"""
                ALTER TABLE log
                ADD COLUMN {_goal_value} REAL"""
            )
            query.exec_(
                f"""
                INSERT INTO variables (Variable, GoalType, Goal)
                VALUES
                ("{_goal_value}", "{_combobox_value}", "{_target_value}", "{list_order})
                """
            )
            list_order += 1
            self.layout_super.removeWidget(self.button_add)
            self.layout_super.removeWidget(self.textbox_goal)
            self.layout_super.removeWidget(self.textbox_target)
            self.button_add = None
            self.textbox_goal = None
            self.textbox_target = None


#Window with reports of similar days based on clustering model
#Top is plots with current and selected dates data
#Bottom is journal entries from selected dates
class ReportWindow(QWidget):
	#Initialize window
    def __init__(self):
        super().__init__()
        self._report_df_ = pd.DataFrame({})
        self._journal_ = [
            None,
        ]
        self._report_date_range_ = [
            None,
        ]
        self._current_df_ = pd.DataFrame({})
        self._current_date_range_ = [
            None,
        ]

    #Load data bassed by ReportPromptWindow
    def _load_layout_(self):
        layout_super = QVBoxLayout()
        layout_plot = QHBoxLayout()
        layout_plotheader = QHBoxLayout()
        label_data = QLabel(
            f"Tracker From {self._report_date_range_[0]} to {self._report_date_range_[-1]} and Past 7 Days"
        )
        label_data.setAlignment(Qt.AlignCenter)
        label_data.setMaximumWidth(400)
        line_1 = QFrame()
        line_1.setStyleSheet("color: #ffa82e")
        line_1.setFrameShape(QFrame.HLine)
        line_2 = QFrame()
        line_2.setStyleSheet("color: #ffa82e")
        line_2.setFrameShape(QFrame.HLine)
        layout_plotheader.addWidget(line_1)
        layout_plotheader.addWidget(label_data)
        layout_plotheader.addWidget(line_2)

        for col in self._report_df_.columns[:]:
            self.figure = MplCanvas(self, width=4, height=4, dpi=100)
            self.figure.p1 = self.figure.axes.plot(
                np.arange(1, 8), self._report_df_[col], c="#557ff2"
            )
            self.figure.p2 = self.figure.axes.plot(
                np.arange(1, 8), self._current_df_[col], c="#ffa82e"
            )
            self.figure.axes.set_title(col, color="#ffffff", fontsize="small")
            self.figure.axes.legend(
                [
                    f"{self._report_date_range_[0]} - {self._report_date_range_[-1]}",
                    f"{self._current_date_range_[0]} - {self._current_date_range_[-1]}",
                ],
                fontsize="small",
                facecolor="#1d1e1e",
                labelcolor="#ffffff",
                edgecolor="#bfbfbf",
            )
            self.figure.setMinimumWidth(300)
            self.figure.axes.tick_params(rotation=25, labelsize=8)
            self.figure.fig.tight_layout(rect=(0, 0.025, 1, 1))
            self.figure.axes.set_facecolor("#1d1e1e")
            self.figure.fig.patch.set_facecolor("#1d1e1e")
            self.figure.axes.spines["bottom"].set_color("#bfbfbf")
            self.figure.axes.spines["top"].set_color("#bfbfbf")
            self.figure.axes.spines["left"].set_color("#bfbfbf")
            self.figure.axes.spines["right"].set_color("#bfbfbf")
            self.figure.axes.tick_params(color="#bfbfbf", labelcolor="#ffffff")

            layout_plot.addWidget(self.figure)

        self.widget = QWidget()
        self.widget.setLayout(layout_plot)
        self.scroll_area1 = QScrollArea()
        self.scroll_area1.setWidget(self.widget)
        self.scroll_area1.setWidgetResizable(True)

        layout_journalheader = QHBoxLayout()
        label_journal = QLabel(
            f"Journal Entries From {self._report_date_range_[0]} to {self._report_date_range_[-1]}"
        )
        label_journal.setAlignment(Qt.AlignCenter)
        label_journal.setMaximumWidth(300)
        line_1 = QFrame()
        line_1.setStyleSheet("color: #ffa82e")
        line_1.setFrameShape(QFrame.HLine)
        line_2 = QFrame()
        line_2.setStyleSheet("color: #ffa82e")
        line_2.setFrameShape(QFrame.HLine)
        layout_journalheader.addWidget(line_1)
        layout_journalheader.addWidget(label_journal)
        layout_journalheader.addWidget(line_2)

        layout_form = QFormLayout()
        for entry in self._journal_:
            label_entry = QLabel(entry)
            layout_form.addRow(label_entry)

        self.group_box2 = QGroupBox()
        self.group_box2.setLayout(layout_form)
        self.scroll_area2 = QScrollArea()
        self.scroll_area2.setWidget(self.group_box2)
        self.scroll_area2.setWidgetResizable(True)

        layout_super.addLayout(layout_plotheader)
        layout_super.addWidget(self.scroll_area1)
        layout_super.addLayout(layout_journalheader)
        layout_super.addWidget(self.scroll_area2)

        self.setLayout(layout_super)


#Show users which date ranges are similar to past 7 days
#Prompt to open reports which will open an individual ReportWindow
class ReportPromptWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._report_dict_ = None
        self._current_dict_ = None
        self._windows_ = None
        layout_super = QVBoxLayout()
        label_start = QLabel(
            """Hey! 
            You look like you went through something similar on these days"""
        )
        layout_super.addWidget(label_start)

        for idx, ((key_report, value_report), (key, value)) in enumerate(
            zip(report_dict.items(), current_dict.items())
        ):
            self._report_date_range_ = np.arange(*key_report, dtype="datetime64[D]")
            self._report_df_ = value_report[0]
            self._current_date_range_ = np.arange(*key, dtype="datetime64[D]")
            self._current_df_ = value[0]
            self._journal_ = value_report[1]
            self.idx = idx
            button = QPushButton(
                f"{self._report_date_range_[0]} - {self._report_date_range_[-1]}"
            )
            button.clicked.connect(self._open_report_)
            layout_super.addWidget(button)

        label_end = QLabel("Click a date range to check it out!")
        layout_super.addWidget(label_end)
        self.setLayout(layout_super)

    def _open_report_(self):
        if self._windows_[self.idx] is None:
            self._windows_[self.idx] = ReportWindow()
        self._windows_[self.idx].report_df = self._report_df_
        self._windows_[self.idx].journal = self._journal_
        self._windows_[self.idx].report_date_range = self._report_date_range_
        self._windows_[self.idx].current_df = self._current_df_
        self._windows_[self.idx].current_date_range = self._current_date_range_
        self._windows_[self.idx]._load_layout_()
        self._windows_[self.idx].show()
        self.close()


#Plot widget
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.p1 = []
        self.p2 = []
        super(MplCanvas, self).__init__(self.fig)


#Popup window
class Popup(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label_popup = QLabel()
        layout.addWidget(self.label)
        self.setLayout(layout)


def rolling_average(a, n=7):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1 :] / n

#Nothing class
class Nothing:
    def __init__(self):
        self._name_ = "Nothing"

    def show(self):
        self._name_ = "Nothing2"

#Format user data into a model friendly format and remove variables without 66% of total entries
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
    df_noformat = df
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
    df["Me"] = df["Me"] / df["Me"].abs().max()
    df["Day"] = df["Day"] / df["Day"].abs().max()
    #print(drops)
    df = df.drop(drops, axis=1)
    new_cols = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    for col in df.columns:
        for key, val in new_cols.items():
            val.append(f"{col}_{key}day")
    dfs = []
    for key in new_cols.keys():
        dfs.append(df.shift(key))
    for (d, val) in zip(dfs, new_cols.values()):
        df[val] = d
    df = df.dropna(axis=0, how="any")
    dates = df["Date"]
    df = df.drop(
        [
            "Date",
            "Date_1day",
            "Date_2day",
            "Date_3day",
            "Date_4day",
            "Date_5day",
            "Date_6day",
            "Date_7day",
        ],
        axis=1,
    )
    #print(df.columns)
    return df, np.array(dates), df_noformat


#Cluster data into len/3 clusters and select the dates which are in the same group as past 7 days
def generate_clusters(df, dates):
    clusters = int(len(df.index) / 3)
    data_fit = np.array(df)[:-1, :]
    data_pred = np.array(df)[-1:, :]
    dates_fit = dates[:-1]
    date_pred = dates[-1:]
    clustering = cluster.KMeans(n_clusters=clusters)
    clustering.fit(data_fit)
    label_pred = clustering.predict(data_pred)
    # print(label_pred)
    labels = clustering.labels_
    dates_match = dates_fit[labels == label_pred[0]]

    return dates_match

#Get data dicts from dates to be passed into report window
def get_dicts(dates, df):
	df['Date_pd'] = pd.to_datetime(df['Date'])
	dates_pd = pd.to_datetime(dates)
	report_dict = {}
	for d, dpd in zip(dates, dates_pd):
		date_range = [np.array(df[df['Date_pd'] <= dpd].tail(7)['Date'])[0], d]
		date_range[0] = f'{date_range[0][-4:]}-{date_range[0][:5]}'
		date_range[1] = f'{date_range[1][-4:]}-{date_range[1][:5]}'
		query = QSqlQuery()
		query.exec_(f'SELECT * FROM journal WHERE Date = "{d}"')
		journal_entry = []
		while query.next():
			journal_entry.append(f'{query.value(0)} {query.value(2)} - {query.value(1)}')
		report_dict[(date_range[0], date_range[1])] = (df[df['Date_pd'] <= dpd].tail(7).drop(['Date_pd'], axis=1), journal_entry)

	current_dict = {}
	current_date = np.array(df['Date'])[-1]
	date_range = [np.array(df.tail(7)['Date'])[0], current_date]
	date_range[0] = f'{date_range[0][-4:]}-{date_range[0][:5]}'
	date_range[1] = f'{date_range[1][-4:]}-{date_range[1][:5]}'
	current_dict = {(date_range[0], date_range[1]): (df.tail(7), ['',])}

	return current_dict, report_dict

	    
#Strings to be selected randomly for progress report
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


#Run
if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    list_order = 0
    rpw = None
    if (setup) and (rpw is None):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("personal_data.db")
        db.close()
        db.open()
        # print(load_cluster_data().columns)
        df, dates, df_noformat = load_cluster_data()
        cluster_dates = generate_clusters(df, dates)
        report_windows = [
            None,
        ]
        current_dict, report_dict = get_dicts(cluster_dates, df_noformat)
        #print(current_dict, report_dict)
        rpw = ReportPromptWindow()
        rpw.report_dict = report_dict
        rpw.current_dict = current_dict
        rpw.windows = report_windows
        rpw.show()

    sw = None
    if not setup:
        sw = SetupWindow()
        sw.show()

    if (setup) and (sw is None):
        w = MainWindow()
        w.show()

    app.exec()
