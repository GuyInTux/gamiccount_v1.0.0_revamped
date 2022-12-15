import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
import pyrebase

firebaseConfig = {'apiKey': "AIzaSyDnCFmS_VKGI-tyXeVMfx1PnXJE3bSb7KY",
                  'authDomain': "gami-ccount-v1.firebaseapp.com",
                  'databaseURL': "https://gami-ccount-v1.firebaseapp.com",
                  'projectId': "gami-ccount-v1",
                  'storageBucket': "gami-ccount-v1.appspot.com",
                  'messagingSenderId': "1051580956547",
                  'appId': "1:1051580956547:web:4941dc82047b03e459c0b6",
                  'measurementId': "G-E9XSYPS080"}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.btn_login.clicked.connect(self.log_user_in)
        self.btn_login.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_login.setStyleSheet('''
        *{  
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
                font-family: Georgia;
                color: 'white';
                font-weight: bold;
                border-radius: 18px;
            }
        *:hover{
                background:'white';
                color:'black';
                font-weight:1200;  
            }
        ''')
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)  # masks PW
        self.btn_signup.clicked.connect(self.gotocreate)
        self.btn_signup.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_signup.setStyleSheet('''
        *{  
                background:rgb(0, 170, 0);
                font-weight: bold;
                color:'yellow';
                border-radius: 10px;
            }
        *:hover{
                background:'yellow';
                color:rgb(0, 170, 0);
                font-weight:bold;  
            }
        ''')
        self.lbl_invalid_login.setVisible(False)
        self.lbl_login_success.setVisible(False)

    def log_user_in(self):
        email = self.emailfield.text()
        pw = self.passwordfield.text()
        try:
            auth.sign_in_with_email_and_password(email, pw)
            uid = auth.sign_in_with_email_and_password(email, pw)['localId']

            with open("log.txt", 'w') as file: #temporary processing storing current UID accessing the system
                file.write(f"{uid},{email}")
                file.close()
            print(f"User {uid} with email {email} logged in!")

            self.lbl_login_success.setVisible(True)
            self.closelauncher_and_access()
            # self.close()
            # self.hide()  # hides 1st window
            #
            # import tester2
            # launch = tester2.menu()
            # widget.addWidget(launch)
            # widget.setCurrentIndex(widget.currentIndex() + 1)

        except:
            self.lbl_login_success.setVisible(False)
            self.lbl_invalid_login.setVisible(True)

    def gotocreate(self):
        createacc = Signup()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def closelauncher_and_access(self):
        self.close()
        import tester2
        self.Open = tester2.menu()
        self.Open.show()

class Signup(QDialog):
    def __init__(self):
        super(Signup, self).__init__()
        loadUi("signup.ui", self)
        self.btn_createaccount.clicked.connect(self.create_account_function)
        self.btn_createaccount.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_createaccount.setStyleSheet('''
        *{ 
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(61,217,245), stop:1 rgba(240, 53, 218));
                color: 'white';
                font-weight: 1200;
                border-radius: 18px;

            }
        *:hover{           
                background:'white';
                color:'black';
                font-weight:1200;
                border-radius: 18px;  
            }
        ''')
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lbl_invalid_msg.setVisible(False)
        self.btn_back.clicked.connect(self.gotologin)
        self.btn_back.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_back.setStyleSheet('''
        *{  
                background:rgb(0, 170, 0);
                font-weight: bold;
                color:'yellow';
                border-radius: 10px;
            }
        *:hover{
                background:'yellow';
                color:rgb(0, 170, 0);
                font-weight:bold;  
            }
        ''')

    def gotologin(self):
        gologin = Login()
        widget.addWidget(gologin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def create_account_function(self):
        email = self.emailfield.text()
        if self.passwordfield.text() == self.confirmpasswordfield.text():
            pw = self.passwordfield.text()
            try:
                auth.create_user_with_email_and_password(email, pw)
                print("Account bound to " + email + " created!")
                login_inst = Login()
                widget.addWidget(login_inst)
                widget.setCurrentIndex(widget.currentIndex() + 1)
                self.lbl_invalid_msg.setVisible(False)
            except:
                self.lbl_invalid_msg.setVisible(True)


app = QApplication(sys.argv)
main_window = Login()  # instance of login class

widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setWindowTitle("Gami-ccount: Gamified System for Accounting Learning")
widget.setWindowIcon(QtGui.QIcon("gami-ccount_icon.png"))
widget.setFixedWidth(600)
widget.setFixedHeight(700)
widget.move(20, 20)
widget.show()
sys.exit(app.exec_())
