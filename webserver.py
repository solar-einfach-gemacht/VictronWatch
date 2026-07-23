# -*- coding: utf-8 -*-
import json
import os
import threading
import asyncio
import struct
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bleak import BleakScanner
from victron_ble.devices import SolarCharger
from victron_ble.devices.base import Device

app = Flask(__name__)
DEVICES_FILE = 'devices.json'

# --- 1. UNSER EIGENER INVERTER RS DECODER ---
class InverterRSDecoder(Device):
    def parse_decrypted(self, decrypted: bytes):
        pass
        
    def parse(self, data):
        decrypted = self.decrypt(data)
        if len(decrypted) < 16:
            return None 
            
        spannung = struct.unpack_from('<H', decrypted, 2)[0] / 100.0
        strom = struct.unpack_from('<h', decrypted, 4)[0] / 10.0
        pv_leistung = struct.unpack_from('<H', decrypted, 6)[0]
        ertrag_heute = struct.unpack_from('<H', decrypted, 8)[0] * 10
        ac_last = struct.unpack_from('<H', decrypted, 10)[0]
        
        return {
            "spannung": spannung,
            "strom": strom,
            "pv_leistung": pv_leistung,
            "ertrag_heute": ertrag_heute,
            "ac_last": ac_last
        }

# -*- coding: utf-8 -*-
import json
import os
import threading
import asyncio
import struct
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bleak import BleakScanner
from victron_ble.devices import SolarCharger
from victron_ble.devices.base import Device

app = Flask(__name__)
DEVICES_FILE = 'devices.json'

# --- 1. UNSER EIGENER INVERTER RS DECODER ---
class InverterRSDecoder(Device):
    def parse_decrypted(self, decrypted: bytes):
        pass
        
    def parse(self, data):
        decrypted = self.decrypt(data)
        if len(decrypted) < 16:
            return None 
            
        spannung = struct.unpack_from('<H', decrypted, 2)[0] / 100.0
        strom = struct.unpack_from('<h', decrypted, 4)[0] / 10.0
        pv_leistung = struct.unpack_from('<H', decrypted, 6)[0]
        ertrag_heute = struct.unpack_from('<H', decrypted, 8)[0] * 10
        ac_last = struct.unpack_from('<H', decrypted, 10)[0]
        
        return {
            "spannung": spannung,
            "strom": strom,
            "pv_leistung": pv_leistung,
            "ertrag_heute": ertrag_heute,
            "ac_last": ac_last
        }

# --- 2. ZWISCHENSPEICHER FÜR DAS DASHBOARD ---
live_data = {}

def load_devices():
    if not os.path.exists(DEVICES_FILE):
        return []
    with open(DEVICES_FILE, 'r') as f:
        return json.load(f)

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=4)

# --- 3. BLUETOOTH HINTERGRUND-SCANNER (Das Gehirn) ---
def get_decoder(device_config):
    # Die automatische Weiche
    if device_config['type'] == 'Inverter RS':
        return InverterRSDecoder(device_config['bindkey'])
    elif device_config['type'] == 'MPPT 450/100':
        return SolarCharger(device_config['bindkey'])
    return None

async def detection_callback(device, advertisement_data):
    devices = load_devices()
    mac_upper = device.address.upper()
    
    # Prüfen, ob die gefundene MAC in unserer Liste steht
    known_device = next((d for d in devices if d['mac'].upper() == mac_upper), None)
    
    if known_device and advertisement_data.manufacturer_data and 737 in advertisement_data.manufacturer_data:
        data = advertisement_data.manufacturer_data[737]
        try:
            decoder = get_decoder(known_device)
            if decoder:
                werte = decoder.parse(data)
                
                if werte is not None:
                    # Einheitliches Format für das Dashboard basteln
                    if known_device['type'] == 'MPPT 450/100':
                        parsed = {
                            "spannung": werte.get_battery_voltage(),
                            "strom": werte.get_battery_charging_current(),
                            "pv_leistung": werte.get_solar_power(),
                            "ertrag_heute": werte.get_yield_today(),
                            "ac_last": 0, # MPPT hat keine AC-Last
                            "status": werte.get_charge_state().name
                        }
                    else: # Inverter RS
                        parsed = werte
                        parsed["status"] = "Aktiv"
                    
                    # Zusatzinfos ranhängen
                    parsed["name"] = known_device["name"]
                    parsed["type"] = known_device["type"]
                    
                    # Im globalen Speicher ablegen!
                    live_data[mac_upper] = parsed
                    
        except Exception as e:
            pass # Wenn ein Paket kaputt ist, einfach ignorieren

async def run_ble_scanner():
    scanner = BleakScanner(detection_callback)
    await scanner.start()
    while True:
        await asyncio.sleep(1)

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_ble_scanner())


# --- 4. WEB-ROUTEN ---
@app.route('/')
def index():
    # Hier laden wir jetzt das fertige HTML-Dashboard
    return render_template('index.html')

@app.route('/setup')
def setup():
    return render_template('setup.html', devices=load_devices())

@app.route('/add', methods=['POST'])
def add_device():
    name = request.form.get('name')
    device_type = request.form.get('device_type')
    mac = request.form.get('mac')
    bindkey = request.form.get('bindkey')

    if name and device_type and mac and bindkey:
        devices = load_devices()
        devices.append({
            'name': name,
            'type': device_type,
            'mac': mac.upper().strip(),
            'bindkey': bindkey.strip()
        })
        save_devices(devices)
    return redirect(url_for('setup'))

@app.route('/api/data')
def api_data():
    return jsonify(live_data)

if __name__ == '__main__':
    # Threading: Bluetooth-Scanner im Hintergrund starten
    ble_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_background_loop, args=(ble_loop,), daemon=True)
    t.start()
    
    print("Starte Webserver und Hintergrund-Scanner...")
    app.run(host='0.0.0.0', port=5000)
