import threading
from datetime import datetime
from time import sleep

import requests
from PyQt5 import QtWidgets
from clientui import Ui_MainWindow


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send)
        threading.Thread(target=self.refresh).start()  # фоновый параллельный процесс

    def send(self):
        text = self.lineEdit.text()
        username = self.lineEdit_2.text()
        password = self.lineEdit_3.text()

        try:
            response = requests.post('http://127.0.0.1:5000/login', json={
                'username': username,
                'password': password
            })
            print(response.text)  # to avoid parsing error we can output <.text> except <.json()>
            response = requests.post('http://127.0.0.1:5000/send', json={
                'username': username,
                'password': password,
                'text': text
            })
            print(response.text)
        except requests.exceptions.ConnectionError:
            print('Server is not available')
            return  # чтобы выйти из эксепшена, очищать поле не нужно, так как реквест не прошел
        except:
            print('Some error')
            return

        self.lineEdit.setText('')  # не подойдет без репэинта так как отрисовка не пройдет
        self.lineEdit.repaint()

    def refresh(self):  # нужно чтобы рефреш работал фоном, не был привязан к какому-то событию, иначе доступ пропадет к отправке новых сообщений
        last_time = 0
        while True:
            try:
                response = requests.get('http://127.0.0.1:5000/messages',
                                        params={'after': last_time})
            except:
                print('Some error')
                sleep(1)
                continue

            for message in response.json()['messages']:
                time_formatted = datetime.fromtimestamp(message['time'])
                time_formatted = time_formatted.strftime('%Y-%m-%d %H:%M:%S')
                header = message['username'] + ' in ' + str(time_formatted)
                text = message['text']
                self.textBrowser.append(header)
                self.textBrowser.append(text)
                self.textBrowser.append('')

                last_time = message['time']

            sleep(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec_()


# pyuic5 messenger.ui -o clientui.py
