from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen

class PanelSterowania(QWidget):
    sygnal_zmien_predkosc = pyqtSignal(int)
    sygnal_steruj_z1 = pyqtSignal()
    sygnal_reset = pyqtSignal()
    sygnal_steruj_z4 = pyqtSignal()
    
    sygnal_napelnij_z2 = pyqtSignal()
    sygnal_napelnij_z3 = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(20, 580, 480, 190)
        
        self.lbl_panel = QLabel("PANEL STEROWANIA", self)
        self.lbl_panel.setGeometry(20, 10, 200, 20)
        self.lbl_panel.setStyleSheet("color: #ddd; font-weight: bold; font-size: 14px; background: transparent;")

        self.lbl_monitor_filtr = QLabel("Filtracja (Z2): 0%", self)
        self.lbl_monitor_filtr.setGeometry(20, 40, 200, 20)
        self.lbl_monitor_filtr.setStyleSheet("color: #ffff00; font-weight: bold; background: transparent;")

        self.lbl_monitor_temp = QLabel("Temp. (Z3): 20.0°C", self)
        self.lbl_monitor_temp.setGeometry(20, 65, 200, 20)
        self.lbl_monitor_temp.setStyleSheet("color: #ff4500; font-weight: bold; background: transparent;")

        self.lbl_monitor_woda = QLabel("Odbiorca: 0 L", self)
        self.lbl_monitor_woda.setGeometry(20, 90, 200, 20)
        self.lbl_monitor_woda.setStyleSheet("color: #00FF00; font-weight: bold; background: transparent;")

        self.lbl_suwak = QLabel("Szybkość przepływu:", self)
        self.lbl_suwak.setGeometry(250, 20, 150, 20)
        self.lbl_suwak.setStyleSheet("color: white; background: transparent;")

        self.suwak = QSlider(Qt.Horizontal, self)
        self.suwak.setGeometry(250, 45, 180, 20)
        self.suwak.setMinimum(1)
        self.suwak.setMaximum(20)
        self.suwak.setValue(10)
        self.suwak.valueChanged.connect(self.obsluga_suwaka)
        self.suwak.setStyleSheet("""
            QSlider::groove:horizontal { height: 8px; background: #555; border-radius: 4px; }
            QSlider::handle:horizontal { background: #3498db; width: 16px; margin: -4px 0; border-radius: 8px; }
        """)

        self.lbl_wartosc_suwaka = QLabel("1.0x", self)
        self.lbl_wartosc_suwaka.setGeometry(440, 20, 40, 20)
        self.lbl_wartosc_suwaka.setStyleSheet("color: #3498db; font-weight: bold; background: transparent;")

        btn_y = 120 
        
        self.btn_z1 = QPushButton("Otwórz Z1", self)
        self.btn_z1.setGeometry(20, btn_y, 100, 35)
        self.btn_z1.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_z1.clicked.connect(self.sygnal_steruj_z1.emit) 
        
        self.btn_reset = QPushButton("Reset", self)
        self.btn_reset.setGeometry(130, btn_y, 100, 35)
        self.btn_reset.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_reset.clicked.connect(self.sygnal_reset.emit)

        self.btn_z4 = QPushButton("Opróżnij Z4", self)
        self.btn_z4.setGeometry(240, btn_y, 100, 35)
        self.styl_z4_aktywny = "background-color: #e67e22; color: white; font-weight: bold; border-radius: 5px;"
        self.styl_z4_nieaktywny = "background-color: #555; color: #aaa; font-weight: bold; border-radius: 5px;"
        self.btn_z4.setStyleSheet(self.styl_z4_nieaktywny)
        self.btn_z4.setEnabled(False)
        self.btn_z4.clicked.connect(self.sygnal_steruj_z4.emit)

        btn_y_dol = 160

        self.btn_napelnij_z2 = QPushButton("Napełnij Z2 (100%)", self)
        self.btn_napelnij_z2.setGeometry(20, btn_y_dol, 110, 30)
        self.btn_napelnij_z2.setStyleSheet("background-color: #663399; color: white; border-radius: 5px; font-size: 11px;")
        self.btn_napelnij_z2.clicked.connect(self.sygnal_napelnij_z2.emit)

        self.btn_napelnij_z3 = QPushButton("Napełnij Z3 (100%)", self)
        self.btn_napelnij_z3.setGeometry(140, btn_y_dol, 110, 30)
        self.btn_napelnij_z3.setStyleSheet("background-color: #663399; color: white; border-radius: 5px; font-size: 11px;")
        self.btn_napelnij_z3.clicked.connect(self.sygnal_napelnij_z3.emit)


    def obsluga_suwaka(self, wartosc):
        predkosc = wartosc / 10.0
        self.lbl_wartosc_suwaka.setText(f"{predkosc:.1f}x")
        self.sygnal_zmien_predkosc.emit(wartosc)

    def aktualizuj_monitory(self, postep_filtracji, temperatura, ilosc_wody):
        self.lbl_monitor_filtr.setText(f"Filtracja (Z2): {int(postep_filtracji)}%")
        self.lbl_monitor_temp.setText(f"Temp. (Z3): {temperatura:.1f}°C")
        self.lbl_monitor_woda.setText(f"Odbiorca: {int(ilosc_wody)} L")

    def ustaw_stan_przycisku_z1(self, czy_otwarty):
        if czy_otwarty:
            self.btn_z1.setText("Zamknij Z1")
            self.btn_z1.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; border-radius: 5px;")
        else:
            self.btn_z1.setText("Otwórz Z1")
            self.btn_z1.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px;")

    def aktualizuj_dostepnosc_z4(self, czy_dostepny):
        if czy_dostepny:
            self.btn_z4.setEnabled(True)
            self.btn_z4.setStyleSheet(self.styl_z4_aktywny)
        else:
            self.btn_z4.setEnabled(False)
            self.btn_z4.setStyleSheet(self.styl_z4_nieaktywny)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#333"))
        p.setPen(QPen(QColor("#555"), 3))
        p.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)