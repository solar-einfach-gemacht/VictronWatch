#!/bin/bash
echo "=========================================="
echo "⚡ Starte VictronWatch Installation... ⚡"
echo "=========================================="

# 1. System updaten und Voraussetzungen installieren
echo "[1/5] Installiere System-Updates und Abhängigkeiten..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git bluez

# 2. Projektordner erstellen und GitHub-Code herunterladen
echo "[2/5] Lade Projektdateien herunter..."
cd ~
if [ -d "VictronWatch" ]; then
    echo "Ordner VictronWatch existiert bereits. Lösche alten Code..."
    rm -rf VictronWatch
fi
# HIER SPÄTER DEINEN GITHUB-LINK EINTRAGEN:
git clone https://github.com/solar-einfach-gemacht/VictronWatch.git
cd VictronWatch

# 3. Python Sandkasten (venv) erstellen
echo "[3/5] Erstelle Python-Umgebung..."
python3 -m venv venv

# 4. Bibliotheken installieren
echo "[4/5] Installiere Bibliotheken (Flask, Bleak, Victron-BLE)..."
./venv/bin/pip install flask bleak victron-ble

# 5. Autostart (Systemd) einrichten
echo "[5/5] Richte Autostart (Systemd Service) ein..."
cat <<EOF | sudo tee /etc/systemd/system/victronwatch.service > /dev/null
[Unit]
Description=VictronWatch Webserver und Bluetooth Scanner
After=network.target bluetooth.target

[Service]
User=$USER
WorkingDirectory=$HOME/VictronWatch
ExecStart=$HOME/VictronWatch/venv/bin/python $HOME/VictronWatch/webserver.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable victronwatch.service
sudo systemctl start victronwatch.service

echo "=========================================="
echo "✅ INSTALLATION ABGESCHLOSSEN! ✅"
echo "=========================================="
echo "Dein Dashboard ist jetzt erreichbar unter:"
echo "👉 http://$(hostname -I | awk '{print $1}'):5000"
echo "👉 http://$(hostname).local:5000"
echo "=========================================="
