import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa="", kolor_cieczy=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        
        self.kolor_cieczy = kolor_cieczy

        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0
        
        self.ma_filtr = False
        self.postep_filtracji = 0.0
        
        self.ma_grzalke = False
        self.temperatura = 20.0
        
        self.proces_zakonczony = False 

    def reset_procesu(self):
        self.proces_zakonczony = False
        self.postep_filtracji = 0.0
        self.temperatura = 20.0

    def zmien_kolor(self, nowy_kolor):
        self.kolor_cieczy = nowy_kolor

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1
        
    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.kolor_cieczy)
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

        if self.ma_filtr:
            if (self.czy_pelny() and not self.proces_zakonczony):
                painter.setPen(QPen(Qt.yellow, 3, Qt.SolidLine))
            else:
                painter.setPen(QPen(QColor(200, 200, 200, 100), 1, Qt.DotLine))

            for i in range(1, 5):
                y_pos = self.y + (self.height / 5) * i
                painter.drawLine(int(self.x), int(y_pos), int(self.x + self.width), int(y_pos))
            
            if self.aktualna_ilosc > 5:
                painter.setPen(Qt.yellow)
                status = "Filtrowanie..." if self.postep_filtracji < 100 else "GOTOWE"
                painter.drawText(int(self.x + 5), int(self.y + 20), f"{status}")

        if self.ma_grzalke:
            pen_grzalka = QPen(QColor("#FF4500"), 3)
            
            if (self.temperatura < 90 and self.czy_pelny() and not self.proces_zakonczony):
                pen_grzalka.setColor(Qt.red)
                pen_grzalka.setWidth(4)
            else:
                pen_grzalka.setColor(Qt.gray)
                pen_grzalka.setWidth(3)

            painter.setPen(pen_grzalka)
            path = QPainterPath()
            start_y = self.y + self.height - 20
            path.moveTo(self.x + 10, start_y)
            for i in range(1, 10):
                x_pos = self.x + 10 + (self.width - 20) * (i/9)
                y_offset = -10 if i % 2 == 0 else 0
                path.lineTo(x_pos, start_y + y_offset)
            painter.drawPath(path)

            painter.setPen(Qt.white)
            painter.drawText(int(self.x + self.width + 10), int(self.y + self.height/2), f"{self.temperatura:.1f}°C")