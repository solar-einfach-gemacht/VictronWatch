
<img width="1275" height="719" alt="grafik" src="https://github.com/user-attachments/assets/467c1826-ac7e-461d-9051-de3a3c7d4e00" />


# ⚡ VictronWatch


![VictronWatch Live Dashboard]

**VictronWatch** ist ein lokales, blitzschnelles Live-Dashboard für Victron-Geräte auf dem Raspberry Pi. Es liest die verschlüsselten Bluetooth-Daten (BLE) deiner Solar-Komponenten nativ aus, entschlüsselt sie lokal und stellt sie über einen schicken Webserver dar – **komplett autark, in Echtzeit und zu 100 % ohne Cloud!**

Entstanden ist dieses Projekt aus der Not heraus, dass herkömmliche ESP32-Lösungen (wie ESPHome) oft starr sind und bei komplexen Geräten (wie dem Inverter RS) mit der Entschlüsselung kämpfen. VictronWatch nutzt einen eigenen Hex-Decoder und eine dynamische Web-Oberfläche.

## ✨ Was dieses Projekt besonders macht
* **Dynamische Kommandozentrale:** Keine C++ Programmierung, kein nerviges Neu-Flashen von Mikrocontrollern. Neue Geräte werden einfach über eine Webseite per MAC-Adresse und Bindkey hinzugefügt.
* **Live-Dashboard:** Die Werte aktualisieren sich im Sekundentakt direkt im Browser, ohne dass die Seite neu laden muss (Auto-Fetch).
* **Integrierte API:** Alle Daten können über die Schnittstelle `/api/data` als sauberes JSON abgerufen werden (perfekt für Node-RED, ioBroker oder Home Assistant).
* **Lokaler Autostart:** Läuft als unsichtbarer System-Dienst (Systemd) dauerhaft im Hintergrund des Raspberry Pi.

## 🔋 Unterstützte Geräte
Aktuell ist der integrierte Decoder auf folgende Geräte abgestimmt:
* **Inverter RS Smart** (Inklusive AC-Last, Ertrag, Spannung, Strom)
* **MPPT 450/100** (und voraussichtlich die meisten anderen SmartSolar MPPT Laderegler)
* **MultiPlus** (Wird in Kürze nachgereicht!)

---

## 🚀 Installation (Idiotensicher)

Du musst kein Linux-Profi sein, um VictronWatch zu installieren. Ein einziger Befehl reicht aus!
Verbinde dich per SSH (z.B. mit MobaXterm oder PuTTY) mit deinem Raspberry Pi und füge diesen Befehl in das Terminal ein:

```bash
wget -qO- [https://raw.githubusercontent.com/solar-einfach-gemacht/VictronWatch/main/install.sh](https://raw.githubusercontent.com/solar-einfach-gemacht/VictronWatch/main/install.sh) | bash
