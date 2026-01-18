import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from zbiorniki import Zbiornik
from rury import Rura
from panel_sterowania import PanelSterowania
from zawory import Zawor
from budynek import Budynek

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oczyszczanie wody")
        self.setFixedSize(700, 780)
        self.setStyleSheet("background-color: #222;")
        
        self.kolor_zielony = QColor("green")
        self.kolor_granatowy = QColor("navy")
        self.kolor_jasnoniebieski = QColor("lightskyblue")

        self.z1 = Zbiornik(50, 50, nazwa="Z1 (Źródło)", kolor_cieczy=self.kolor_zielony)
        self.z1.aktualna_ilosc = 100.0
        self.z1.aktualizuj_poziom()

        self.z2 = Zbiornik(220, 225, nazwa="Z2 (Filtr)", kolor_cieczy=self.kolor_zielony)
        self.z2.ma_filtr = True
        
        self.z3 = Zbiornik(390, 400, nazwa="Z3 (Grzałka)", kolor_cieczy=self.kolor_zielony)
        self.z3.ma_grzalke = True
        
        self.z4 = Zbiornik(560, 575, nazwa="Z4 (Bufor)", kolor_cieczy=self.kolor_zielony)
        
        self.b = Budynek(520, 80, nazwa="Dom (Odbiorca)")
        
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4, self.b]

        p_start1 = self.z1.punkt_dol_srodek()
        p_koniec1 = self.z2.punkt_gora_srodek()
        mid_y1 = (p_start1[1] + p_koniec1[1]) / 2
        self.rura1 = Rura([p_start1, (p_start1[0], mid_y1), (p_koniec1[0], mid_y1), p_koniec1])

        p_start2 = self.z2.punkt_dol_srodek()
        p_koniec2 = self.z3.punkt_gora_srodek()
        mid_y2 = (p_start2[1] + p_koniec2[1]) / 2
        self.rura2 = Rura([p_start2, (p_start2[0], mid_y2), (p_koniec2[0], mid_y2), p_koniec2])
        
        p_start3 = self.z3.punkt_dol_srodek()
        p_koniec3 = self.z4.punkt_gora_srodek()
        mid_y3 = (p_start3[1] + p_koniec3[1]) / 2
        self.rura3 = Rura([p_start3, (p_start3[0], mid_y3), (p_koniec3[0], mid_y3), p_koniec3])

        p_start4 = self.z4.punkt_dol_srodek()
        p_koniec4 = self.b.punkt_gora_srodek()
        
        self.rura4 = Rura([
            p_start4,
            (p_start4[0], p_start4[1] + 20),
            (660, p_start4[1] + 20),
            (660, p_koniec4[1] - 10),
            (p_koniec4[0], p_koniec4[1] - 10),
            p_koniec4
        ])

        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4]

        self.zawor1 = Zawor(p_start1[0], p_start1[1] + 15)
        self.zawor2 = Zawor(p_start2[0], p_start2[1] + 15)
        self.zawor3 = Zawor(p_start3[0], p_start3[1] + 15)
        self.zawor4 = Zawor(p_start4[0], p_start4[1] + 15)

        self.zawory = [self.zawor1, self.zawor2, self.zawor3, self.zawor4]

        self.flow_speed = 1.0
        self.zawor_glowny_otwarty = False
        self.czy_oprozniac_z4 = False

        self.panel = PanelSterowania(self)
        
        self.panel.sygnal_zmien_predkosc.connect(self.zmien_predkosc)
        self.panel.sygnal_steruj_z1.connect(self.steruj_kranu)
        self.panel.sygnal_reset.connect(self.reset_symulacji)
        self.panel.sygnal_steruj_z4.connect(self.aktywuj_oproznianie_z4)
        
        self.panel.sygnal_napelnij_z2.connect(self.napelnij_z2_max)
        self.panel.sygnal_napelnij_z3.connect(self.napelnij_z3_max)

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)
        self.timer.start(20)

    def napelnij_z2_max(self):
        self.z2.aktualna_ilosc = 100.0
        self.z2.aktualizuj_poziom()
        
        self.z2.zmien_kolor(self.kolor_zielony)
        
        self.z2.postep_filtracji = 0
        self.z2.proces_zakonczony = False
        
        self.update()

    def napelnij_z3_max(self):
        self.z3.aktualna_ilosc = 100.0
        self.z3.aktualizuj_poziom()
        
        self.z3.zmien_kolor(self.kolor_granatowy)
        self.z3.temperatura = 20.0
        self.z3.proces_zakonczony = False
        
        self.update()

    def zmien_predkosc(self, wartosc):
        self.flow_speed = wartosc / 10.0

    def aktywuj_oproznianie_z4(self):
        self.czy_oprozniac_z4 = True
        self.panel.aktualizuj_dostepnosc_z4(False)

    def steruj_kranu(self):
        self.zawor_glowny_otwarty = not self.zawor_glowny_otwarty
        self.panel.ustaw_stan_przycisku_z1(self.zawor_glowny_otwarty)

    def reset_symulacji(self):
        self.zawor_glowny_otwarty = False
        self.czy_oprozniac_z4 = False
        
        self.panel.ustaw_stan_przycisku_z1(False)
        self.panel.aktualizuj_dostepnosc_z4(False)

        for z in self.zbiorniki:
            if isinstance(z, Budynek):
                z.calkowita_woda = 0.0
            z.aktualna_ilosc = 0.0
            z.aktualizuj_poziom()
            z.reset_procesu()

        self.z1.aktualna_ilosc = 100.0
        self.z1.aktualizuj_poziom()
        self.z1.zmien_kolor(self.kolor_zielony)

        for r in self.rury:
            r.ustaw_przeplyw(False)
        self.update()

    def logika_przeplywu(self):
        self.z1.aktualna_ilosc = 100.0
        self.z1.aktualizuj_poziom()

        if self.z2.czy_pusty(): self.z2.reset_procesu()
        if self.z3.czy_pusty(): self.z3.reset_procesu()

        self.panel.aktualizuj_monitory(self.z2.postep_filtracji, self.z3.temperatura)
        
        mozna_wcisnac_oproznianie = self.z4.czy_pelny() and not self.czy_oprozniac_z4
        self.panel.aktualizuj_dostepnosc_z4(mozna_wcisnac_oproznianie)

        trwa_filtracja = False
        if self.z2.czy_pelny() and not self.z2.proces_zakonczony:
            trwa_filtracja = True
            self.z2.postep_filtracji += 0.8
            if self.z2.postep_filtracji >= 100:
                self.z2.postep_filtracji = 100
                self.z2.proces_zakonczony = True
                self.z2.zmien_kolor(self.kolor_granatowy)

        trwa_grzanie = False
        if self.z3.czy_pelny() and not self.z3.proces_zakonczony:
            trwa_grzanie = True
            if self.z3.temperatura < 90:
                self.z3.temperatura += 0.4
            else:
                self.z3.temperatura = 90
                self.z3.proces_zakonczony = True
                self.z3.zmien_kolor(self.kolor_jasnoniebieski)

        plynie_1 = False
        mozna_lac_do_z2 = (not self.z2.czy_pelny() and not trwa_filtracja and not self.z2.proces_zakonczony)
        if self.zawor_glowny_otwarty and mozna_lac_do_z2:
            self.z2.dodaj_ciecz(self.flow_speed)
            if not self.z2.proces_zakonczony:
                self.z2.zmien_kolor(self.z1.kolor_cieczy)
            plynie_1 = True
            self.rura1.ustaw_kolor_cieczy(self.z1.kolor_cieczy)
        self.rura1.ustaw_przeplyw(plynie_1)
        self.zawor1.ustaw_stan(plynie_1)

        plynie_2 = False
        z2_gotowy = self.z2.proces_zakonczony and self.z2.aktualna_ilosc > 0
        mozna_lac_do_z3 = (not self.z3.czy_pelny() and not trwa_grzanie and not self.z3.proces_zakonczony)
        if z2_gotowy and mozna_lac_do_z3:
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            if not self.z3.proces_zakonczony:
                self.z3.zmien_kolor(self.z2.kolor_cieczy)
            self.z3.dodaj_ciecz(ilosc)
            plynie_2 = True
            self.rura2.ustaw_kolor_cieczy(self.z2.kolor_cieczy)
        self.rura2.ustaw_przeplyw(plynie_2)
        self.zawor2.ustaw_stan(plynie_2)

        plynie_3 = False
        z3_gotowy = self.z3.proces_zakonczony and self.z3.aktualna_ilosc > 0
        mozna_dolewac = self.z4.czy_pusty() or (self.rura3.czy_plynie and not self.z4.czy_pelny())

        if z3_gotowy and mozna_dolewac:
            ilosc = self.z3.usun_ciecz(self.flow_speed)
            self.z4.zmien_kolor(self.z3.kolor_cieczy)
            self.z4.dodaj_ciecz(ilosc)
            plynie_3 = True
            self.rura3.ustaw_kolor_cieczy(self.z3.kolor_cieczy)
        
        self.rura3.ustaw_przeplyw(plynie_3)
        self.zawor3.ustaw_stan(plynie_3)
        
        plynie_4 = False
        if self.czy_oprozniac_z4:
            if self.z4.aktualna_ilosc > 0:
                ilosc = self.z4.usun_ciecz(self.flow_speed * 1.5)
                self.b.dodaj_ciecz(ilosc)
                plynie_4 = True
                self.rura4.ustaw_kolor_cieczy(self.z4.kolor_cieczy)
            else:
                self.czy_oprozniac_z4 = False
        
        self.rura4.ustaw_przeplyw(plynie_4)
        self.zawor4.ustaw_stan(plynie_4)

        self.update()

    def rysuj_strumien(self, painter, x_start, y_start, zbiornik_docelowy, kolor):
        painter.setPen(QPen(kolor, 6, Qt.SolidLine, Qt.RoundCap))

        if isinstance(zbiornik_docelowy, Budynek):
            y_koniec = y_start + 30
        else:
            calkowita_wysokosc_zbiornika = zbiornik_docelowy.height
            
            obecny_poziom_wody = zbiornik_docelowy.height * zbiornik_docelowy.poziom
            
            gora_zbiornika_y = zbiornik_docelowy.y

            odleglosc_do_tafli = calkowita_wysokosc_zbiornika - obecny_poziom_wody
            y_tafli = gora_zbiornika_y + odleglosc_do_tafli
            
            y_koniec = y_tafli

            if y_koniec < y_start:
                y_koniec = y_start
            
        painter.drawLine(int(x_start), int(y_start), int(x_start), int(y_koniec))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        for r in self.rury: r.draw(p)
        if self.rura1.czy_plynie:
            self.rysuj_strumien(p, self.rura1.punkty[-1].x(), self.rura1.punkty[-1].y(), self.z2, self.rura1.kolor_cieczy)
        if self.rura2.czy_plynie:
            self.rysuj_strumien(p, self.rura2.punkty[-1].x(), self.rura2.punkty[-1].y(), self.z3, self.rura2.kolor_cieczy)
        if self.rura3.czy_plynie:
            self.rysuj_strumien(p, self.rura3.punkty[-1].x(), self.rura3.punkty[-1].y(), self.z4, self.rura3.kolor_cieczy)
        if self.rura4.czy_plynie:
             self.rysuj_strumien(p, self.rura4.punkty[-1].x(), self.rura4.punkty[-1].y(), self.b, self.rura4.kolor_cieczy)

        for z in self.zbiorniki: z.draw(p)
        for v in self.zawory: v.draw(p)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())