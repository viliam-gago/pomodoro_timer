from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
from datetime import datetime as dt
import csv
import os
import pandas as pd
import winsound
import matplotlib.pyplot as plt
from win10toast import ToastNotifier


# Window instance
class Window(QMainWindow):


    # this happens when object created - window template
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro session")
        self.setGeometry(0, 0, 400, 600)

        if 'pomodoro_log.csv' not in os.listdir():
            self.create_csv()

        # calling method setting more things for created Window object
        self.UiComponents()


    def UiComponents(self):
        #todays date - for logging into csv
        self.today = dt.now().strftime('%d_%m_%Y')

        self.time_to_add = 0

        #check what is done for today in csv file (database)
        with open('pomodoro_log.csv', 'r+') as file:
            my_dict = self.load_csv()
        self.time_total = int(my_dict[self.today]) if self.today in my_dict else 0

        #how much from a session remaining
        self.count = 0
        #timer is not running
        self.start = False

        # reset button
        reset_button = QPushButton('Reset session', self)
        reset_button.setGeometry(50, 50, 200, 50)
        reset_button.clicked.connect(self.reset_action)
        # set time button
        button = QPushButton('Set time', self)
        button.setGeometry(50, 110, 200, 50)
        button.clicked.connect(self.set_time)
        #plotting button
        plot_button = QPushButton('''Session 
history''', self)
        plot_button.setGeometry(260, 50, 90, 110)
        plot_button.clicked.connect(self.plot_history)

        # labels
        self.label = QLabel('Let\'s do it', self)
        self.label.setGeometry(50, 200, 300, 100)
        self.label.setStyleSheet("border : 3px solid black")
        self.label.setFont(QFont('Arial', 12))
        self.label.setAlignment(Qt.AlignCenter)

        self.label2 = QLabel(f'Today total: {self.convert_to_hours(self.time_total)} ', self)
        self.label2.setGeometry(50, 325, 300, 100)
        self.label2.setStyleSheet("border : 3px solid black")
        self.label2.setFont(QFont('Arial', 12))
        self.label2.setAlignment(Qt.AlignCenter)

        # start button
        start_button = QPushButton('START', self)
        start_button.setGeometry(125, 450, 150, 40)
        start_button.clicked.connect(self.start_action)
        # pause button
        pause_button = QPushButton('PAUSE', self)
        pause_button.setGeometry(125, 500, 150, 40)
        pause_button.clicked.connect(self.pause_action)

        # timer object - timer is instance of QTimer class;
        # timeout setting -> decrementing time value continuously;
        # timer.start -> sets 'step' (1000 = 1000 milisec = 1 sec)
        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)


    def create_csv(self):
        '''
        This creates new csv file for logging.
        '''
        with open('pomodoro_log.csv', 'w'):
            pass

    def load_csv(self):
        '''
        Method loads data from csv file into dict.
        '''
        with open('pomodoro_log.csv', 'r+') as file:
            r = csv.reader(file, delimiter=',')
            my_dict = {rows[0]: rows[1] for rows in r}
            return my_dict

    def update_time_worked(self, my_dict):
        '''
        Method takes dict and updates values in it. Returns updated dict.
        '''
        my_dict.setdefault(self.today, 0)
        my_dict[self.today] = int(my_dict[self.today]) + self.time_to_add

        return my_dict

    def plot_history(self):
        '''
        Method loads data from .csv file and stores them in lists. Then plot is created.
        '''
        with open('pomodoro_log.csv', 'r') as file:
            lines = file.readlines()

        days = [dt.strftime(dt.strptime(line.split(',')[0], '%d_%m_%Y'), '%d.%b %Y') for line in lines]
        time_worked = [float(line.split(',')[1]) / 3600 for line in lines]

        plt.plot(days, time_worked, 'mo-')
        plt.xlabel('Days')
        plt.ylabel('Session hours')
        plt.title('How much do I study over long run ?')
        plt.gcf().autofmt_xdate()
        yticks = [0, 1, 2, 3, 4, 5, 6]
        ax = plt.gca()
        ax.set_yticks(yticks)
        plt.grid()
        plt.show()

    def write_csv(self, my_dict):
        '''
        Method takes dictionary and writes it into .csv file.
        '''
        pd.DataFrame.from_dict(data=my_dict, orient='index').to_csv('pomodoro_log.csv', header=False)

    def convert_to_min(self, seconds):
        '''
        Method takes time in seconds, converts it into MIN:SEC format.
        '''
        return time.strftime('%M:%S', time.gmtime(seconds))

    def convert_to_hours(self, seconds):
        '''
        Method takes time in seconds, converts it into HOUR:MIN:SEC format.
        '''
        return time.strftime('%H:%M:%S', time.gmtime(seconds))

    def show_time(self):
        '''
        Method checks if timer is running. If yes, time value is decreasing continuously.

            If 0 is reached -> Completed !!! displayed into label + alarm sound played.
            (toaster object not working properly - shuts down the app when finished --> commented)

            Data from .csv file loaded into dict -> value in dict updated -> original value in .csv
            rewrited with new dict.

            Total label shows total time worked in particular day. Loads data from dict based according to todays date
            (key). Then displays time in better format.

            After these steps, timer state is changed to not running.

        If timer is running, time value in time_left label is being rewrited with updated self.count values.

        '''
        if self.start:
            self.count -= 1

            if self.count == 0:
                self.label.setText('Completed !!!')
                winsound.PlaySound('beep-07.wav', winsound.SND_NODEFAULT)
                # toaster = ToastNotifier()
                # toaster.show_toast('Sample Notification', 'Session finished !')

                my_dict = self.load_csv()
                my_dict = self.update_time_worked(my_dict)
                self.write_csv(my_dict)

                self.time_total = my_dict[self.today]
                self.time_to_add = 0
                self.label2.setText(f'Today in total: {self.convert_to_hours(self.time_total)}')

                self.start = False

        if self.start:
            secs_left = self.count
            mins_left = str(self.convert_to_min(secs_left))
            self.label.setText(mins_left)

    def set_time(self):
        '''
        Method shows input dialog window to set session time in minues. Input is in seconds, then transfered into
        desired minute format simply by *60 multiplicaton.
        '''
        self.start = False
        seconds, done = QInputDialog.getInt(self, 'Minutes', 'Enter:')

        if done:
            self.count = seconds * 60
            self.label.setText(str(self.convert_to_min(seconds * 60)))
            self.time_to_add = self.count

    def start_action(self):
        '''
        Starts countdown, if session time is not set - it does nothing.
        '''
        self.start = True

        if self.count == 0:
            self.start = False

    def pause_action(self):
        '''
        Method pauses countdown.
        '''
        self.start = False

    def reset_action(self):
        '''
        Method stops countdown, sets timer to zero and shows initial state in time label.
        '''
        self.start = False
        self.count = 0
        self.label.setText('Let\'s get it done...')


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
