from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPolygonF

class Zawor:
    def __init__(self, x, y, rozmiar=20):
        self.x = x
        self.y = y
        self.rozmiar = rozmiar
        self.czy_otwarty = False
        self.kolor_zamkniety = QColor("#555")
        self.kolor_otwarty = QColor("#00FF00")

    def ustaw_stan(self, czy_plynie):
        self.czy_otwarty = czy_plynie

    def draw(self, painter):
        painter.save()

        if self.czy_otwarty:
            painter.setBrush(self.kolor_otwarty)
            painter.setPen(QColor("lime")) 
        else:
            painter.setBrush(self.kolor_zamkniety)
            painter.setPen(Qt.black)

        cx, cy = self.x, self.y
        r = self.rozmiar / 2
        
        p1 = QPolygonF([
            QPointF(cx - r, cy - r/2),
            QPointF(cx - r, cy + r/2),
            QPointF(cx, cy)
        ])
        
        p2 = QPolygonF([
            QPointF(cx + r, cy - r/2),
            QPointF(cx + r, cy + r/2),
            QPointF(cx, cy)
        ])
        
        painter.drawPolygon(p1)
        painter.drawPolygon(p2)
        
        painter.setBrush(Qt.black if not self.czy_otwarty else Qt.white)
        painter.drawEllipse(QPointF(cx, cy), 4, 4)
        
        painter.restore()
