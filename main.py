import os
import sys


import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QPoint

class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)

        self.setWindowTitle('Отображение карты')
        self.setFixedSize(650, 600)

        self.ln = 37.530887
        self.lt = 55.703118
        self.spn = [0.0021, 0.0021]

        self.left = self.ln - self.spn[0]
        self.right = self.ln + self.spn[0]
        self.top = self.lt - self.spn[1]
        self.bottom = self.lt + self.spn[1]

        self.idx = 0
        self.l = 'map'
        self.mark = None

        self.img_pos_x = 25
        self.img_pos_y = 71

        self.searchBtn.clicked.connect(self.search)
        self.resetBtn.clicked.connect(self.reset)
        self.checkBox.stateChanged.connect(self.chanchAddress)

        self.getImage()
        self.loadImage()

    def getImage(self):

        params = {
            'll': f'{str(self.ln)},{str(self.lt)}',
            'spn': f'{str(self.spn[0])},{str(self.spn[1])}',
            'l': f'{self.l}',
        }

        if self.mark:
            params['pt'] = f'{self.mark[0]},{self.mark[1]}',

        map_request = f"http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_request, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def loadImage(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            if self.spn[0] <= 1:
                self.spn[0] += 0.002
                self.spn[1] += 0.002

        if event.key() == Qt.Key.Key_PageDown:
            if self.spn[0] > 0.002:

                self.spn[0] -= 0.002
                self.spn[1] -= 0.002
        if event.key() == Qt.Key.Key_Up:
            self.lt += 0.001
        if event.key() == Qt.Key.Key_Down:
            self.lt -= 0.001
        if event.key() == Qt.Key.Key_Left:
            self.ln -= 0.001
        if event.key() == Qt.Key.Key_Right:
            self.ln += 0.001

        if event.key() == Qt.Key.Key_F1:
            self.l = 'map'
        if event.key() == Qt.Key.Key_F2:
            self.l = 'sat'
        if event.key() == Qt.Key.Key_F3:
            self.l = 'skl'

        self.spn[0] = round(self.spn[0], 6)
        self.spn[1] = round(self.spn[1], 6)

        self.loadImage()

    def mouseMoveEvent(self, event):
        # print(f"Move Координаты: {event.x()}, {event.y()}")
        pass

    def mousePressEvent(self, event):
        # print(f"Press Координаты: {event.x()}, {event.y()}")
        x, y = event.x() - self.img_pos_x, event.y() - self.img_pos_y
        print(x, y)
        lt = (self.bottom - self.top) / 450 * y
        ln = (self.right - self.left) / 600 * x

        # lt = ln = 0


        print(f'left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom}')
        print(f'ln: {self.ln}, lt: {self.lt}')
        print(f'Сдвиг ln: {ln}, Сдвиг lt: {lt}')
        print('--------------------------------------------------------------------------------')

        mark_ln = self.ln - (self.right - self.left) / 2 + ln
        mark_lt = self.lt

        self.left = self.ln - self.spn[0]
        self.right = self.ln + self.spn[0]
        self.top = self.lt - self.spn[1]
        self.bottom = self.lt + self.spn[1]

        self.mark = [mark_ln, mark_lt]

        self.loadImage()


    def search(self):
        print('search')

        params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': self.searchInput.text(),
            'format': 'json',
        }

        geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_request, params=params)
        print(response.url)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.toponym_address = toponym_address
        if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
            toponym_post = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        else:
            toponym_post = ""
        self.toponym_post = toponym_post

        if self.checkBox.isChecked():
            self.fullAddress.setText(toponym_post + ', ' + toponym_address)
        else:
            self.fullAddress.setText(toponym_address)
        toponym_coodrinates = toponym["Point"]["pos"]

        print(f'toponym_coodrinates: {toponym_coodrinates}')
        coods = list(map(float, toponym_coodrinates.split(' ')))

        self.ln = coods[0]
        self.lt = coods[1]
        self.mark = [self.ln, self.lt]

        self.left = self.ln - self.spn[0]
        self.right = self.ln + self.spn[0]
        self.top = self.lt - self.spn[1]
        self.bottom = self.lt + self.spn[1]

        self.loadImage()

    def chanchAddress(self):
        if self.fullAddress.text() == '':
            return
        if self.checkBox.isChecked():
            self.fullAddress.setText(self.toponym_post + ', ' + self.toponym_address)
        else:
            self.fullAddress.setText(self.toponym_address)

    def reset(self):
        print('reset')

        self.searchInput.setText('')
        self.fullAddress.setText('')
        self.mark = None

        self.loadImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
