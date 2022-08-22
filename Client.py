import asyncio
import socket
import sys
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import pyqtSignal

from db import Database


class Client:
    def __init__(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.socket.setblocking(True)
        self.username = ""

    def setup(self):
        try:
            database = Database()
            self.socket.connect(('localhost', 8080))
            check = False
            username = ""
            while not check:
                username = input(f'Enter username (should not be in db): ')
                check = database.isValidUsername(username)
            if check:
                self.username = username
                database.addUser(self.username)
            database.closeDatabase()
        except ConnectionRefusedError:
            print(f'Server should be opened!')
            return

    def sendText(self, data=None, socketSent=None):
        self.socket.send(data.encode('utf-8'))

    def listen(self):
        while True:
            try:
                data = self.socket.recv(4096)
                if data:
                    yield data
            except BlockingIOError as error:
                print(error)


class Ui_Chat(object):
    def setupUi(self, Chat):
        Chat.setObjectName("Chat")
        Chat.resize(252, 350)
        Chat.setMinimumSize(QtCore.QSize(252, 350))
        Chat.setMaximumSize(QtCore.QSize(252, 350))
        self.centralwidget = QtWidgets.QWidget(Chat)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 251, 351))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.username = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.username.setFont(font)
        self.username.setAlignment(QtCore.Qt.AlignCenter)
        self.username.setObjectName("username")
        self.verticalLayout.addWidget(self.username)
        self.messageView = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget)
        self.messageView.setEnabled(True)
        self.messageView.setReadOnly(True)
        self.messageView.setObjectName("messageView")
        self.verticalLayout.addWidget(self.messageView)
        self.messageEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.messageEdit.setObjectName("messageEdit")
        self.verticalLayout.addWidget(self.messageEdit)
        self.sendButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.sendButton.setObjectName("sendButton")
        self.verticalLayout.addWidget(self.sendButton)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 1)
        Chat.setCentralWidget(self.centralwidget)

        self.retranslateUi(Chat)
        QtCore.QMetaObject.connectSlotsByName(Chat)

    def retranslateUi(self, Chat):
        _translate = QtCore.QCoreApplication.translate
        Chat.setWindowTitle(_translate("Chat", "Chat"))
        self.username.setText(_translate("Chat", "USER"))
        self.sendButton.setText(_translate("Chat", "Send"))


class ChatWindow(QMainWindow):
    render = pyqtSignal(str)

    def __init__(self):
        # Chat client
        self.client = Client()
        self.client.setup()

        # UI
        super(ChatWindow, self).__init__()
        self.ui = Ui_Chat()
        self.ui.setupUi(self)
        self.ui.username.setText(self.client.username)
        self.ui.sendButton.clicked.connect(self.send)

        # Letting a thread dedicated to listening to messages from
        # other sockets send a signal to render freshly arrived message
        self.render.connect(self.ui.messageView.appendPlainText)
        self.t = threading.Thread(target=self.receive)
        self.t.start()

    def send(self):
        message = self.ui.messageEdit.toPlainText()
        username = self.client.username
        history = self.ui.messageView

        self.client.sendText(f"{username}|{message}")
        history.appendPlainText(f"{username}: {message}")

    def receive(self):
        for data in self.client.listen():
            [username, message] = data.decode("utf-8").split("|")
            self.render.emit(f"{username}: {message}")


def main():
    app = QApplication([])

    chat = ChatWindow()
    chat.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
