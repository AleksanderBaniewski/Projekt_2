from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QColor, QPen
from zbiorniki import Zbiornik

class Budynek(Zbiornik):
    def __init__(self, x, y, nazwa="Budynek"):
        super().__init__(x, y, nazwa=nazwa, kolor_cieczy=QColor("gray"))
        self.width = 110
        self.height = 90

    def dodaj_ciecz(self, ilosc):
        self.aktualna_ilosc += ilosc

    def czy_pusty(self):
        return True 

    def draw(self, painter):
        painter.setBrush(QColor("#444"))
        painter.setPen(QPen(Qt.black, 1))
        komin_x = int(self.x + self.width - 35)
        komin_y = int(self.y - 25)
        painter.drawRect(komin_x, komin_y, 20, 25)

        painter.setBrush(QColor("gray"))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        painter.setBrush(QColor("yellow"))
        painter.setPen(QPen(Qt.black, 1))
        margin_x, margin_y, gap = 20, 15, 30
        okno_w, okno_h = 20, 20
        
        coords = [
            (0, 0), (gap, 0),
            (0, gap), (gap, gap)
        ]
        for dx, dy in coords:
            painter.drawRect(int(self.x + margin_x + dx), int(self.y + margin_y + dy), okno_w, okno_h)

        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y + self.height + 5), int(self.width), 20, Qt.AlignCenter, self.nazwa)
        
        painter.setPen(QColor("#00FF00"))
        painter.drawText(int(self.x), int(self.y + self.height + 25), int(self.width), 20, Qt.AlignCenter, f"Pobrano: {int(self.aktualna_ilosc)}")

    def punkt_gora_srodek(self):
        return (self.x + self.width - 25, self.y - 25)