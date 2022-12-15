# Author: Lim Hong Yong
# UI config

import os.path
import sys
import traceback

import mysql.connector
import pandas as pd
import json
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, \
    QWidget, QFileDialog, QGridLayout, QDialog, QMessageBox, QMainWindow, \
    QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.uic import loadUi
from urllib.request import urlopen

# Timer Dependency
from PyQt5.QtCore import QTimer, QTime

# Audio Dependencies
from PyQt5.QtCore import QUrl
from PyQt5 import QtMultimedia
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSoundEffect

parameters = {
    "question": [],
    "difficulty": [],
    "answer1": [],
    "answer2": [],
    "answer3": [],
    "answer4": [],
    "correct": [],
    "score": [],
    "index": []
}

data_to_be_synced = {
    "filename": [],
    "last_score": [],
    "user_email": [],
    "uid": [],
    "achievements": []
}

widgets = {
    "empty_space": [],
    "empty_space_2": [],
    "spacer": [],
    "spacer2": [],
    "logos": [],
    "buttons": [],
    "score": [],
    "question": [],
    "answer1": [],
    "answer2": [],
    "answer3": [],
    "answer4": [],
    "message": [],
    "message2": [],
    "leaderboard_button": [],
    "leaderboard_table": [],
    "settings_button": [],
    "instructions_button": [],
    "instructions_panel": [],
    "import_csv_button": [],
    "information": [],
    "return": [],
    "play_music": [],
    "volume_increase": [],
    "volume_decrease": [],
    "mute": [],
    "volume_indicator": [],
    "test_clicker": [],
    "bgm_status": [],
    "timer": [],
    "logout": []
}

# default question loaded from DB on start *******
db_default = mysql.connector.connect(host="localhost", user="root", passwd="(y>sgWevvxs>Qt%y", database="gamiccount")
cursor = db_default.cursor()
sql = "select * from question_formatted;"
cursor.execute(sql)
info_rows = cursor.fetchall()
cursor.close()

df = pd.DataFrame(info_rows)
df.rename(columns={0: 'category', 1: 'question_type', 2: 'difficulty',
                   3: 'question', 4: 'correct_answer',
                   5: 'incorrect_answer_0', 6: 'incorrect_answer_1',
                   7: 'incorrect_answer_2', 8: 'incorrect_answers'}, inplace=True)

cols = ["incorrect_answer_0", "incorrect_answer_1",
        "incorrect_answer_2"]

df["incorrect_answers"] = df[cols].values.tolist()

hasUserImported = False


def preload_data(index):  # prepares new question data
    # category = df["category"][index]
    difficulty = df["difficulty"][index]
    question = df["question"][index]
    correct = df["correct_answer"][index]
    incorrect = df["incorrect_answers"][index]

    # For check in terminal
    print(question)
    print("Difficulty: " + difficulty)
    print("Answer:" + correct)

    parameters["question"].append(question)
    parameters["correct"].append(correct)
    parameters["difficulty"].append(difficulty)

    # incorrect var contains 'list' data type, hence correct must be converted into a list also
    all_ans = incorrect + [correct]
    random.shuffle(all_ans)
    print(all_ans)  # print all_ans for unit testing

    # appends shuffled choices into dictionary
    parameters["answer1"].append(all_ans[0])
    parameters["answer2"].append(all_ans[1])
    parameters["answer3"].append(all_ans[2])
    parameters["answer4"].append(all_ans[3])


# initialise GUI app
app = QApplication(sys.argv)
# initialise grid layout
grid = QGridLayout()

# windows settings
window = QWidget()
window.setWindowTitle("Gami-ccount: Gamified System for Accounting Learning")
window.setWindowIcon(QtGui.QIcon("gami-ccount_icon.png"))
window.setFixedWidth(1000)
window.setFixedHeight(900)
window.move(20, 20)
window.setStyleSheet("background:'black';")


# Function for image resize to x and y px ratio
def resize_image(src, x, y):
    pixmap = QtGui.QPixmap(src)
    # Automatically resizes to max size available
    pixmap_scaled = pixmap.scaled(x, y, QtCore.Qt.KeepAspectRatio)
    return pixmap_scaled


# function for creating button widgets
def create_answer_buttons(answer, l_margin, r_margin):
    btn = QPushButton(answer)
    btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn.setFixedWidth(475)
    btn.setStyleSheet(
        "*{margin-left:" + str(l_margin) + "px;" +
        " margin-right:" + str(r_margin) + "px;" +
        '''
        border: 4px solid'#7FFF00';
        border-radius: 12px;
        font-family: 'Arial';     
        font-size: 16px;
        color: 'white';
        padding: 50px 0;
        margin-top: 5px;}
        *:hover{
            background:'green';
            font-weight: bold;
            color: 'yellow';
        }
        '''
    )
    btn.clicked.connect(lambda x: is_correct(btn))
    return btn


def create_start_buttons(placeholder_text):
    btn = QPushButton(placeholder_text)
    btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    # btn.setFixedWidth(300)
    btn.setStyleSheet(
        '''
        *{  
            font: 'Georgia';
            border: 1px solid 'GREEN';
            border-radius: 12px;
            font-size: 30px;
            color: 'white';
            padding: 5px ;
            margin: 0px 300px;
            }
        *:hover{
                background:'green';
                color:'yellow';
                font-weight:800;
                font-size: 30px;   
            }
        '''
    )

    if placeholder_text == "Leaderboard":
        btn.clicked.connect(leaderboard)
    elif placeholder_text == "Settings":
        btn.clicked.connect(settings)
    elif placeholder_text == "Log Out":
        btn.clicked.connect(logout)
    elif placeholder_text == "Instructions":
        btn.clicked.connect(instructions)
    elif placeholder_text == "Import Questions":
        btn.clicked.connect(import_stuff)
    else:
        pass  # do nothing
    return btn


def logout():
    print("User Logged Out")
    clear_widgets()
    clear_parameters()
    player.stop()
    sys.exit()
    pass


def create_settings_buttons(placeholder_text):
    btn = QPushButton(placeholder_text)
    btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn.setStyleSheet(
        '''        
        *{  
            font: 'Georgia';
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
            border-radius: 12px;
            font-size: 30px;
            color: 'white';
            padding: 10px;
            margin: 0px 25px;
            }
        *:hover{
                color:'black';
                font-weight:900;
                font-size: 30px;   
            }
        '''
    )

    if placeholder_text == "TEST AUDIO":
        btn.setStyleSheet(
            '''        
            *{  
                font: 'Georgia';
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
                border-radius: 12px;
                font-size: 30px;
                color: 'white';
                padding: 10px;
                margin-top: 100px;
                margin-left: 25px;
                margin-right: 25px;
                }
            *:hover{
                    color:'black';
                    font-weight:900;
                    font-size: 30px;   
                }
            '''
        )
        btn.clicked.connect(play_bgm)
    elif placeholder_text == "VOLUME UP":
        btn.clicked.connect(vol_up)
    elif placeholder_text == "VOLUME DOWN":
        btn.clicked.connect(vol_down)
    elif placeholder_text == "MUTE":
        btn.clicked.connect(vol_mute)
    elif placeholder_text == "BACK TO MENU":
        btn.clicked.connect(return_to_menu)
    else:
        pass  # do nothing
    return btn


def import_stuff():
    try:
        import tkinter as tk
        from tkinter.filedialog import askopenfilename
        global hasUserImported

        data_to_be_synced = {
            "filename": []
        }

        tk.Tk().withdraw()
        fn = askopenfilename(title="Gami-ccount Import Question Wizard", filetypes=(("CSV Files", "*.csv"),))
        data_to_be_synced["filename"].append(fn)  # save file path to local dict
        print("Added into dict:")
        print(data_to_be_synced["filename"][-1])
        # widgets["information"][-1].setText("Question is now User-Defined!")  # change info text in menu

        db = mysql.connector.connect(host="localhost", user="root", passwd="(y>sgWevvxs>Qt%y", database="gamiccount")
        user_imported_data = pd.read_csv(data_to_be_synced["filename"][-1])
        user_imported_data.head()
        db_cursor = db.cursor()

        try:
            if db.is_connected():

                query = "DROP TABLE user_imported_converted;"
                db_cursor.execute(query)
                query = "DROP TABLE user_imported;"
                db_cursor.execute(query)

                import_query = """
                create table user_imported (
                    category char(2) not null,
                    question_type varchar(16) not null,
                    difficulty char(12) not null,
                    question tinytext not null,
                    correct_answer tinytext not null,
                    incorrect_answer_0 tinytext not null,
                    incorrect_answer_1 tinytext not null,
                    incorrect_answer_2 tinytext not null
                );
                """
                db_cursor.execute(import_query)
                print("Initial Table Creation Successful.")
                for i, row in user_imported_data.iterrows():
                    sql = "INSERT INTO gamiccount.user_imported VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
                    db_cursor.execute(sql, tuple(row))

                print("Initial Data Added into Initial Table.")

                convert_import_query = """
                CREATE TABLE user_imported_converted(
                    category char(2) not null,
                    question_type varchar(16) not null,
                    difficulty char(12) not null,
                    question tinytext not null,
                    correct_answer tinytext not null,
                    incorrect_answer_0 tinytext not null,
                    incorrect_answer_1 tinytext not null,
                    incorrect_answer_2 tinytext not null,
                    incorrect_answers json default null
                );
                """
                db_cursor.execute(convert_import_query)
                print("Second Table Creation Successful.")

                insert_into_convert_import_query = """
                INSERT INTO gamiccount.user_imported_converted 
                (category, question_type, difficulty, question,correct_answer, incorrect_answer_0,
                 incorrect_answer_1,incorrect_answer_2)
                SELECT category, question_type, difficulty, question, 
                correct_answer,incorrect_answer_0, incorrect_answer_1,incorrect_answer_2
                FROM gamiccount.user_imported;     
                """
                db_cursor.execute(insert_into_convert_import_query)
                print("Data Added into Second Table.")

        except error as e:
            print("Error during connection to DB", e)

        query = "select * from user_imported_converted;"
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()

        df_user = pd.DataFrame(rows)

        # renames each column in the Dataframe
        df_user.rename(columns={0: 'category', 1: 'question_type', 2: 'difficulty',
                                3: 'question', 4: 'correct_answer',
                                5: 'incorrect_answer_0', 6: 'incorrect_answer_1',
                                7: 'incorrect_answer_2', 8: 'incorrect_answers'}, inplace=True)

        df_user_cols = ["incorrect_answer_0", "incorrect_answer_1",
                        "incorrect_answer_2"]

        df_user["incorrect_answers"] = df_user[df_user_cols].values.tolist()

        df.drop(df.index, inplace=True)

        # to replace default dataframe with values of imported dataframe
        df["category"] = df_user["category"]
        df["question_type"] = df_user["question_type"]
        df["difficulty"] = df_user["difficulty"]
        df["question"] = df_user["question"]
        df["correct_answer"] = df_user["correct_answer"]
        df["incorrect_answer_0"] = df_user["incorrect_answer_0"]
        df["incorrect_answer_1"] = df_user["incorrect_answer_1"]
        df["incorrect_answer_2"] = df_user["incorrect_answer_2"]
        df["incorrect_answers"] = df_user["incorrect_answers"]

        widgets["information"][-1].setStyleSheet("color: 'green'; font-size: 20px; margin-top: 0px 300px; ")
        hasUserImported = True
        widgets["information"][-1].setText("Custom Questions in place!")  # change info text in menu

    except:
        hasUserImported = False
        widgets["information"][-1].setText("File format invalid! Try Again.")  # change info text in menu


def settings():  # audio settings
    clear_widgets()

    btn_play = create_settings_buttons("TEST AUDIO")
    widgets["play_music"].append(btn_play)

    btn_vol_down = create_settings_buttons("VOLUME DOWN")
    widgets["volume_decrease"].append(btn_vol_down)

    btn_vol_up = create_settings_buttons("VOLUME UP")
    widgets["volume_increase"].append(btn_vol_up)

    btn_mute = create_settings_buttons("MUTE")
    widgets["mute"].append(btn_mute)

    btn_exit = create_settings_buttons("BACK TO MENU")
    widgets["return"].append(btn_exit)

    current_vol = QLabel()
    current_vol.setText("Volume: " + str(round(int(player.volume() * 100))))
    current_vol.setAlignment(QtCore.Qt.AlignCenter)
    current_vol.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 25px;
        color: '#32CD32';
        padding: 150px;
        '''
    )
    widgets["volume_indicator"].append(current_vol)

    bgm_status = QLabel()
    bgm_status.setText("BGM Unmuted.")
    bgm_status.setAlignment(QtCore.Qt.AlignCenter)
    bgm_status.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 25px;
        color: '#32CD32';
        padding: 150px;
        '''
    )
    widgets["bgm_status"].append(bgm_status)

    grid.addWidget(widgets["play_music"][-1], 0, 0, 1, 2)
    grid.addWidget(widgets["volume_increase"][-1], 1, 0, 1, 2)
    grid.addWidget(widgets["mute"][-1], 2, 0, 1, 2)
    grid.addWidget(widgets["volume_decrease"][-1], 3, 0, 1, 2)
    grid.addWidget(widgets["volume_indicator"][-1], 4, 0, 1, 2)
    grid.addWidget(widgets["bgm_status"][-1], 5, 0, 1, 2)
    grid.addWidget(widgets["return"][-1], 6, 0, 1, 2)


sfx_player = QMediaPlayer()
player = QSoundEffect()


def play_bgm(mode):
    if mode == "ingame":
        sound_file = 'bgm.wav'
    elif mode == "menu":
        sound_file = 'menu_bgm.wav'
    else:
        sound_file = 'bgm.wav'
    player.setSource(QtCore.QUrl.fromLocalFile(sound_file))
    player.setLoopCount(QSoundEffect.Infinite)
    player.play()


def play_click_sound():
    filepath = "mixkit-select-click-1109.wav"
    fullfp = os.path.join(os.getcwd(), filepath)
    url = QUrl.fromLocalFile(fullfp)
    content = QMediaContent(url)
    sfx_player.setMedia(content)
    sfx_player.play()


def play_defeat_sound():
    sound_file = "game_over.wav"
    player.setSource(QtCore.QUrl.fromLocalFile(sound_file))
    player.setLoopCount(1)
    player.play()


def play_win_sound():
    sound_file = "victory.wav"
    player.setSource(QtCore.QUrl.fromLocalFile(sound_file))
    player.setLoopCount(1)
    player.play()


def vol_up():
    current_vol = player.volume()
    player.setVolume(current_vol + 0.1)  # increases vol by 5 everytime function called'
    if player.volume() == 1.0:
        widgets["volume_indicator"][-1].setText("Volume Maxed Out!")
    else:
        widgets["volume_indicator"][-1].setText("Volume: " + str(round(int(player.volume() * 100))))
    print("Current Volume: ", str(round(int(player.volume() * 100))))


def vol_down():
    current_vol = player.volume()
    player.setVolume(current_vol - 0.1)  # decreases vol by 5 everytime function called
    if player.volume() <= 0:
        widgets["volume_indicator"][-1].setText("Volume Cannot Go Lower!")
    else:
        widgets["volume_indicator"][-1].setText("Volume: " + str(round(int(player.volume() * 100))))
    print("Current Volume: ", str(round(int(player.volume() * 100))))


def vol_mute():
    player.setMuted(not player.isMuted())
    if player.isMuted():
        widgets["bgm_status"][-1].setText("BGM Muted.")
        print("BGM Muted.")
    else:
        widgets["bgm_status"][-1].setText("BGM Unmuted.")
        print("BGM Unmuted.")


def leaderboard():
    clear_widgets()

    logo = QLabel()
    logo.setPixmap(QtGui.QPixmap("leaderboard_logo_reformatted.png"))
    logo.setAlignment(QtCore.Qt.AlignCenter)
    widgets["logos"].append(logo)

    spacer = QLabel("")
    spacer.setStyleSheet(
        '''
            background: 'black';
        ''')
    spacer.setMinimumHeight(900)
    spacer.setMinimumWidth(175)
    widgets["spacer"].append(spacer)

    leaderboard = QTableWidget()
    leaderboard.setColumnCount(4)  # display UID, email, total score, achievements
    leaderboard.setColumnWidth(0, 250)  # UID column
    leaderboard.setColumnWidth(1, 120)  # Email Column
    leaderboard.setColumnWidth(2, 70)  # Score column
    leaderboard.setColumnWidth(3, 500)  # Achievements column
    leaderboard.setStyleSheet("""
    background: 'white';
    color: 'black';
    border: 1px solid red;
    """)
    leaderboard.setHorizontalHeaderLabels(["UID", "User Email", "Score", "Achievements"])
    leaderboard.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # disable editing of table content
    leaderboard.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)  # disable width change
    widgets["leaderboard_table"].append(leaderboard)

    spacer_right = QLabel("")
    spacer_right.setStyleSheet(
        '''
            background: 'black';
        ''')
    spacer_right.setMinimumHeight(900)
    spacer_right.setMinimumWidth(175)
    widgets["spacer2"].append(spacer_right)

    btn_return = QPushButton("RETURN TO MENU")
    btn_return.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn_return.setMinimumWidth(200)
    btn_return.setStyleSheet(
        '''        
        *{  
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
            font-size: 17px;
            font-weight: bold;
            color: 'white';
            border-radius: 5px;
            padding-top: 10px;
            padding-bottom: 10px;
            }
        *:hover{
                background:'white';
                color:'black';
                font-weight: bold;
                font-size: 17px;   
            }
        '''
    )
    btn_return.clicked.connect(return_to_menu)
    widgets["return"].append(btn_return)

    # reading leaderboard data from db
    db = mysql.connector.connect(host="localhost", user="root", passwd="(y>sgWevvxs>Qt%y",
                                 database="gamiccount")
    cursor = db.cursor()
    sql = """
        SELECT UID, USER_EMAIL, SUM(HIGH_SCORE), ACHIEVEMENTS
        FROM USER_DATA
        GROUP BY UID
        ORDER BY SUM(HIGH_SCORE) DESC;
    """
    cursor.execute(sql)
    results = cursor.fetchall()

    for row_number, row_data in enumerate(results):
        leaderboard.insertRow(row_number)
        for column_number, data in enumerate(row_data):
            leaderboard.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    cursor.close()
    leaderboard.setRowCount(row_number)

    # place widgets on grid
    grid.addWidget(widgets["spacer"][-1], 0, 0, 2, 1)
    grid.addWidget(widgets["logos"][-1], 0, 1, 1, 1)
    grid.addWidget(widgets["return"][-1], 2, 1, 1, 1)
    grid.addWidget(widgets["leaderboard_table"][-1], 1, 1, 1, 1)
    grid.addWidget(widgets["spacer2"][-1], 0, 2, 2, 1)


def instructions():
    clear_widgets()
    logo = QLabel()
    logo.setPixmap(resize_image("main-logo.png", 500, 300))
    logo.setAlignment(QtCore.Qt.AlignCenter)
    logo.setStyleSheet('''
            margin-top: 25px;
            margin-bottom: 5px;
    ''')
    widgets["logos"].append(logo)

    with open("instructions.txt", 'r') as f:
        f_text = f.read()

    text = QLabel(f_text)  # Prints Question randomly from dictionary
    text.setAlignment(QtCore.Qt.AlignJustify)
    text.setWordWrap(True)
    text.setStyleSheet(
        '''
        font-family: 'Arial';
        background: 'black';
        border: 5px solid 'purple';
        font-size:  15px;
        color: 'yellow';
        margin-top: 10px;
        margin-bottom: 10px;
        margin-left: 30px;
        margin-right: 30px;
        padding: 10px;
        '''
    )
    widgets["instructions_panel"].append(text)

    btn_return = QPushButton("Return to Menu")
    btn_return.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn_return.setStyleSheet(
        '''        
        *{  
            background-color: 'white';
            font-size: 15px;
            color: 'black';
            border-radius: 12px;
            margin-right: 300px;
            margin-left: 300px;
            padding-top: 10px;
            padding-bottom: 10px;
            }
        *:hover{
                background:'green';
                color:'yellow';
                font-weight: bold;
                font-size: 17px;   
            }
        '''
    )
    btn_return.clicked.connect(return_to_menu)
    widgets["return"].append(btn_return)

    # place widgets on grid
    grid.addWidget(widgets["logos"][-1], 1, 0, 1, 2)
    grid.addWidget(widgets["instructions_panel"][-1], 2, 0, 1, 2)
    grid.addWidget(widgets["return"][-1], 3, 0, 1, 2)


def is_correct(btn):
    play_click_sound()

    if btn.text() == parameters["correct"][-1]:
        print(btn.text() + " is correct!")

        temp_score = parameters["score"][-1]
        parameters["score"].pop()
        parameters["score"].append(temp_score + 10)  # adds 10 score everytime answered correctly
        parameters["index"].pop()  # removes from list old question index to generate subsequent random question index
        parameters["index"].append(random.randint(0, (len(df) - 1)))
        preload_data(parameters["index"][-1])  # engine resumes (reset all data, generate new question)
        widgets["score"][-1].setText("Score: " + str(parameters["score"][-1]))

        # widget contents change
        widgets["question"][0].setText(parameters["question"][-1])
        # widgets["difficulty"][0].setText(parameters["difficulty"][-1])
        widgets["answer1"][0].setText(parameters["answer1"][-1])
        widgets["answer2"][0].setText(parameters["answer2"][-1])
        widgets["answer3"][0].setText(parameters["answer3"][-1])
        widgets["answer4"][0].setText(parameters["answer4"][-1])

        global time
        time.setHMS(0, 0, 30)
        widgets["timer"][-1].setText(time.toString("hh:mm:ss"))

        # wins the round if score is 100
        if parameters["score"][-1] == 100:
            clear_widgets()
            win_game()

    else:  # wrong answer chosen.
        clear_widgets()
        defeat_screen()


def calculo():
    global time  # tells compiler we are using the global var as local var
    time = time.addSecs(-1)
    if widgets["timer"] != []:
        if time < QtCore.QTime(0, 0, 1):
            timer0.stop()
            widgets["timer"][-1].setText("Time's up!")
            clear_widgets()
            defeat_screen()
        else:
            widgets["timer"][-1].setText(time.toString("hh:mm:ss"))


time = QtCore.QTime(0, 0, 30)
timer0 = QtCore.QTimer()
timer0.setInterval(1000)  # 1000 milisec/ 1 sec per interval
timer0.timeout.connect(calculo)
timer0.start()


# Function to clear widgets from global dictionary, vital to avoid UI truncates and abnormalities!
def clear_widgets():
    try:
        for widget in widgets:
            if widgets[widget] != []:  # if not an empty dict, hide/ remove current widget from window
                widgets[widget][-1].hide()

            for i in range(0,
                           len(widgets[widget])):  # depending on how many widget objects are in the dict, remove them
                widgets[widget].pop()
    except:
        import traceback
        traceback.print_exc()


def clear_parameters():
    for param in parameters:
        if parameters[param] != []:
            for i in range(0, len(parameters[param])):
                parameters[param].pop()

    # after clearing parameters, re-populate the 2 vital parameters
    parameters["index"].append(random.randint(0, (len(df) - 1)))
    parameters["score"].append(0)  # resets score to 0 once restarted


def start_game():
    clear_widgets()
    clear_parameters()
    preload_data(parameters["index"][-1])
    data_to_be_synced["achievements"].append("None")
    global time
    time.setHMS(0, 0, 30)
    frame2()  # stionstion screen


def menu():
    if player.isPlaying():
        pass
    else:
        play_bgm("menu")

    global hasUserImported
    if hasUserImported:
        widgets["information"][-1].setText("Custom Questions in place!")

    logo = QLabel()  # logo display
    logo.setPixmap(resize_image("main-logo.png", 500, 300))
    logo.setAlignment(QtCore.Qt.AlignCenter)
    logo.setStyleSheet('''
            margin-top: 25px;
            margin-bottom: 5px;
    ''')
    widgets["logos"].append(logo)

    information_message = QLabel()
    information_message.setText("Default Questions in place.")
    information_message.setAlignment(QtCore.Qt.AlignCenter)
    information_message.setStyleSheet("color: 'red'; font-size: 20px; margin-top: 0px 300px; ")
    widgets["information"].append(information_message)

    # Start Button config
    btn_start = QPushButton("Launch Gami-ccount")
    btn_start.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn_start.setStyleSheet(
        '''        
        *{  
            font: 'Georgia';
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
            border-radius: 12px;
            font-size: 30px;
            color: 'white';
            padding: 5px ;
            margin: 0px 300px;
            }
        *:hover{
                color:'black';
                font-weight:900;
                font-size: 30px;   
            }
        '''
    )
    btn_start.clicked.connect(start_game)
    widgets["buttons"].append(btn_start)
    # ==========OTHER BUTTONS=================
    btn_leaderboard = create_start_buttons("Leaderboard")
    widgets["leaderboard_button"].append(btn_leaderboard)

    btn_settings = create_start_buttons("Settings")
    widgets["settings_button"].append(btn_settings)

    btn_instructions = create_start_buttons("Instructions")
    widgets["instructions_button"].append(btn_instructions)

    btn_import_questions_frame = create_start_buttons("Import Questions")
    widgets["import_csv_button"].append(btn_import_questions_frame)

    btn_logout = create_start_buttons("Log Out")
    widgets["logout"].append(btn_logout)

    # empty/placeholder space in bottom
    empty_space = QPushButton("")
    empty_space.setStyleSheet(
        '''
            background-color: 'green';
            margin-bottom: 50px;
        ''')
    empty_space.setMinimumHeight(50)
    empty_space2 = QPushButton("")
    empty_space2.setStyleSheet(
        '''
            background: 'green';
            margin-top: 50px;
        ''')
    empty_space2.setMinimumHeight(50)
    widgets["empty_space"].append(empty_space)
    widgets["empty_space_2"].append(empty_space2)

    # widget placement on screen
    grid.addWidget(widgets["empty_space"][-1], 0, 0, 1, 2)
    grid.addWidget(widgets["logos"][-1], 1, 0, 1, 2)
    grid.addWidget(widgets["buttons"][-1], 2, 0, 1, 2)
    grid.addWidget(widgets["information"][-1], 3, 0, 1, 2)
    grid.addWidget(widgets["import_csv_button"][-1], 4, 0, 1, 2)
    grid.addWidget(widgets["leaderboard_button"][-1], 5, 0, 1, 2)
    grid.addWidget(widgets["settings_button"][-1], 6, 0, 1, 2)
    grid.addWidget(widgets["instructions_button"][-1], 7, 0, 1, 2)
    grid.addWidget(widgets["logout"][-1], 8, 0, 1, 2)
    grid.addWidget(widgets["empty_space_2"][-1], 9, 0, 1, 2)


def return_to_menu():
    clear_widgets()
    clear_parameters()
    menu()


def frame2():
    play_bgm("ingame")

    # ************Score placement***************
    score = QLabel("Score: " + str(parameters["score"][-1]))
    score.setAlignment(QtCore.Qt.AlignRight)
    score.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 25px;
        color: '#32CD32';
        padding: 1px;
        margin: 5px;
        '''
    )
    widgets["score"].append(score)

    # ************Difficulty Placement******************
    # difficulty = QLabel("Difficulty: " + str(parameters["difficulty"][-1]))
    # difficulty.setAlignment(QtCore.Qt.AlignCenter)
    # difficulty.setStyleSheet(
    #     '''
    #     font-family: 'Georgia';
    #     font-size: 15px;
    #     color: '#32CD32';
    #     '''
    # )
    # widgets["difficulty"].append(difficulty)

    # ************Question placement***************
    question = QLabel(parameters["question"][-1])  # Prints Question randomly from dictionary
    question.setAlignment(QtCore.Qt.AlignCenter)
    question.setWordWrap(True)
    question.setStyleSheet(
        '''
        font-family: 'Georgia';
        background: 'white';
        border: 1px solid 'White';
        font-size:  25px;
        color: 'black';
        margin-top: 10px;
        margin-bottom: 10px;
        margin-left: 30px;
        margin-right: 30px;
        padding: 25px;
        '''
    )
    widgets["question"].append(question)

    # **************Logo Placement***************
    logo_bottom = QLabel()
    logo_bottom.setPixmap(resize_image("logo_bottom_formatted.png", 300, 300))
    logo_bottom.setAlignment(QtCore.Qt.AlignCenter)
    logo_bottom.setStyleSheet("margin-top: 25px; margin-bottom: 30px;")
    widgets["logos"].append(logo_bottom)

    # ***************Button Creation**************
    btn1 = create_answer_buttons(parameters["answer1"][-1], 0, 0)
    btn2 = create_answer_buttons(parameters["answer2"][-1], 0, 0)
    btn3 = create_answer_buttons(parameters["answer3"][-1], 0, 0)
    btn4 = create_answer_buttons(parameters["answer4"][-1], 0, 0)

    widgets["answer1"].append(btn1)
    widgets["answer2"].append(btn2)
    widgets["answer3"].append(btn3)
    widgets["answer4"].append(btn4)

    # ***********return to main menu button**************
    btn_return = QPushButton("Return to Menu")
    btn_return.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    btn_return.setStyleSheet(
        '''        
        *{  
            background-color: 'white';
            font-size: 15px;
            color: 'black';
            margin-right: 300px;
            margin-left: 20px;
            padding-top: 10px;
            padding-bottom: 10px;
            }
        *:hover{
                background:'green';
                color:'yellow';
                font-weight: bold;
                font-size: 17px;   
            }
        '''
    )
    btn_return.clicked.connect(save_temp_score)
    widgets["return"].append(btn_return)

    timerlbl = QLabel("START!")
    timerlbl.setAlignment(QtCore.Qt.AlignCenter)
    timerlbl.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 25px;
        color: '#32CD32';
        '''
    )
    widgets["timer"].append(timerlbl)

    # place widgets on grid
    grid.addWidget(widgets["return"][-1], 0, 0)
    grid.addWidget(widgets["score"][-1], 0, 1)
    grid.addWidget(widgets["question"][-1], 1, 0, 1, 2)
    grid.addWidget(widgets["answer1"][-1], 2, 0)
    grid.addWidget(widgets["answer2"][-1], 3, 0)
    grid.addWidget(widgets["answer3"][-1], 2, 1)
    grid.addWidget(widgets["answer4"][-1], 3, 1)
    grid.addWidget(widgets["timer"][-1], 4, 0, 1, 2)


def save_temp_score():  # to save high score later in DB
    data_to_be_synced["last_score"].append(parameters["score"][-1])

    with open("log.txt", 'r') as filestream_1:
        for line in filestream_1:
            user_array = line.split(",")
            uid = user_array[0]
            email = user_array[1]

    data_to_be_synced["uid"].append(uid)
    data_to_be_synced["user_email"].append(email)
    print("UID: ", data_to_be_synced["uid"][-1])
    print("Email: ", data_to_be_synced["user_email"][-1])
    print("Round High Score: ", data_to_be_synced["last_score"][-1])

    # save into DB
    db = mysql.connector.connect(host="localhost", user="root", passwd="(y>sgWevvxs>Qt%y", database="gamiccount")
    db_cursor = db.cursor()

    try:
        if db.is_connected():
            string1 = (
                data_to_be_synced["uid"][-1], data_to_be_synced["user_email"][-1],
                data_to_be_synced["last_score"][-1], data_to_be_synced["achievements"][-1])
            save_score_sql = """
                INSERT INTO gamiccount.user_data (uid, user_email, high_score, achievements)
                VALUES (%s,%s,%s,%s);
                """
            db_cursor.execute(save_score_sql, string1)
            db.commit()
            print("User data saved in DB.")

    except:
        import traceback
        traceback.print_exc()

    db_cursor.close()
    player.stop()
    return_to_menu()


def win_game():
    play_win_sound()
    # congratulations widget
    message = QLabel("You did good!\nYou are a natural accountant!\nYour Score Is:")
    message.setAlignment(QtCore.Qt.AlignCenter)
    message.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 25px;
        color: 'white';
        margin: 50px 0px;
        '''
    )
    widgets["message"].append(message)

    # score widget placement
    score = QLabel(str(parameters["score"][-1]))
    score.setStyleSheet(
        '''
        font-family: 'Georgia';
        font-size: 150px;
        color: 'White';
        margin-top:0px;
        margin-bottom: 25px; 
        '''
    )
    widgets["score"].append(score)

    # bid goodbye widget placement
    bye_message = QLabel("You are a cut above average!")
    bye_message.setAlignment(QtCore.Qt.AlignCenter)
    bye_message.setStyleSheet(
        "font-family: 'Georgia'; font-size: 20px; color: 'white'; margin: 5pxpx 100px;"
    )
    bye_message.setWordWrap(True)
    widgets["message2"].append(bye_message)

    # Retry button widget
    retry_btn = QPushButton('MAIN MENU')
    retry_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    retry_btn.clicked.connect(save_temp_score)
    retry_btn.setStyleSheet(
        '''*{
            text-family: Garamond;
            padding: 25px 0px;
            background: '#BC006C';
            color: 'white';
            font-family: 'Georgia';
            font-size: 35px;
            border-radius: 30px;
            margin: 0px 325px;
        }
        *:hover{
                background: QLinearGradient(x1:0, y1:0,
                                            x2:1, y2:0,
                                            stop: 0 #ea9714,
                                            stop: 1 #9ed228);
                font-size: 40px;
                color: 'black';
        }'''
    )
    widgets["buttons"].append(retry_btn)

    # Bottom Logo widget
    logo_bottom = QLabel()
    logo_bottom.setPixmap(resize_image("logo_bottom_formatted.png", 300, 300))
    logo_bottom.setAlignment(QtCore.Qt.AlignCenter)
    logo_bottom.setStyleSheet("margin-top: 30px; margin-bottom: 30px;")
    widgets["logos"].append(logo_bottom)

    # place widgets on the grid
    grid.addWidget(widgets["message"][-1], 2, 0)
    grid.addWidget(widgets["score"][-1], 2, 1)
    grid.addWidget(widgets["message2"][-1], 3, 0, 1, 2)
    grid.addWidget(widgets["buttons"][-1], 4, 0, 1, 2)
    grid.addWidget(widgets["logos"][-1], 5, 0, 1, 2)


def defeat_screen():
    try:
        # consolation message
        play_defeat_sound()
        message = QLabel("Yikes, that was awful.\nFinal score is:")
        message.setWordWrap(True)
        message.setAlignment(QtCore.Qt.AlignRight)
        message.setStyleSheet(
            "font-family: 'Georgia'; font-size: 35px; color: 'white'; margin: 130px 0px; padding:0px;"
        )
        widgets["message"].append(message)

        # score widget placement
        score = QLabel(str(parameters["score"][-1]))
        score.setAlignment(QtCore.Qt.AlignLeft)
        score.setStyleSheet("font-size: 250px; color: white; margin: 0px 0px;")
        widgets["score"].append(score)
        data_to_be_synced["last_score"].append(parameters["score"][-1])

        # Retry button widget
        retry_btn = QPushButton("STUDY MORE\n" + "and" + "\nTRY AGAIN!")
        retry_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        retry_btn.clicked.connect(save_temp_score)
        retry_btn.setStyleSheet(
            '''        
            *{  
                font: 'Georgia';
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
                border-radius: 30px;
                font-size: 25px;
                color: 'white';
                padding: 25px ;
                margin: 0px 300px;
                }
            *:hover{
                    color:'black';
                    font-weight:bold;
                    font-size: 28px;   
                }
            '''
        )

        widgets["buttons"].append(retry_btn)

        # Bottom Logo widget
        logo_bottom = QLabel()
        logo_bottom.setPixmap(resize_image("logo_bottom_formatted.png", 300, 300))
        logo_bottom.setAlignment(QtCore.Qt.AlignCenter)
        logo_bottom.setStyleSheet("margin-top: 30px; margin-bottom: 30px;")
        widgets["logos"].append(logo_bottom)

        # place widgets on the grid
        grid.addWidget(widgets["message"][-1], 1, 0)
        grid.addWidget(widgets["score"][-1], 1, 1)
        grid.addWidget(widgets["buttons"][-1], 2, 0, 1, 2)
        grid.addWidget(widgets["logos"][-1], 3, 0, 1, 2)
    except:
        import traceback
        traceback.print_exc()


# *********Unit Tests***********
menu()
# ***********************
window.setLayout(grid)
window.show()
sys.exit(app.exec_())  # terminate app
