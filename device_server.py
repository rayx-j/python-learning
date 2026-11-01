from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = '/home/rayx360/my_website/garden.db'

# 👇 新增：全局变量，记录灯的状态 👇
led_state = "off" 

@app.route('/')
def index():
    return send_from_directory('/home/rayx360/my_website', 'index.html')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            min_moisture INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_name TEXT NOT NULL,
            moisture INTEGER,
            record_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/add_plant', methods=['POST'])
def add_plant():
    data = request.json
    name = data.get('name')
    min_moisture = data.get('min_moisture')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO plants (name, min_moisture) VALUES (?, ?)', (name, min_moisture))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_plants', methods=['GET'])
def get_plants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants')
    rows = cursor.fetchall()
    
    plants_list = []
    for row in rows:
        plant_name = row[1]
        cursor.execute('SELECT moisture FROM history WHERE plant_name = ? ORDER BY id DESC LIMIT 1', (plant_name,))
        latest = cursor.fetchone()
        latest_moisture = latest[0] if latest else "--"
        
        plants_list.append({
            "id": row[0], 
            "name": plant_name, 
            "min_moisture": row[2],
            "latest_moisture": latest_moisture
        })
    conn.close()
    return jsonify(plants_list)

@app.route('/check_moisture', methods=['POST'])
def check_moisture():
    data = request.json
    name = data.get('name')
    current_moisture = data.get('current_moisture')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT min_moisture FROM plants WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    if result is None:
        conn.close()
        return jsonify({"status": "error", "message": "没找到该植物"})
    
    min_required = result[0]
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO history (plant_name, moisture, record_time) VALUES (?, ?, ?)', (name, current_moisture, current_time))
    
    cursor.execute('''
        DELETE FROM history 
        WHERE plant_name = ? AND id NOT IN (
            SELECT id FROM history WHERE plant_name = ? ORDER BY id DESC LIMIT 50
        )
    ''', (name, name))
    
    conn.commit()
    conn.close()

    status_str = "warning" if current_moisture < min_required else "ok"
    
    # 👇 核心改变：把灯的状态一起返回给 ESP32 👇
    return jsonify({
        "status": status_str, 
        "message": "缺水" if status_str == "warning" else "正常",
        "led_status": led_state
    })

@app.route('/get_history', methods=['GET'])
def get_history():
    plant_name = request.args.get('name')
    if not plant_name:
        return jsonify([])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT moisture FROM history WHERE plant_name = ? ORDER BY id DESC LIMIT 50', (plant_name,))
    rows = cursor.fetchall()
    conn.close()
    
    history_data = [row[0] for row in rows]
    history_data.reverse()
    return jsonify(history_data)

@app.route('/delete_plant', methods=['POST'])
def delete_plant():
    data = request.json
    name = data.get('name')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM plants WHERE name = ?', (name,))
    cursor.execute('DELETE FROM history WHERE plant_name = ?', (name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# 👇 新增：接收前端开灯/关灯指令的接口 👇
@app.route('/led_on', methods=['POST'])
def turn_on():
    global led_state
    led_state = "on"
    print("🟢 收到前端指令：开灯")
    return jsonify({"status": "success"})

@app.route('/led_off', methods=['POST'])
def turn_off():
    global led_state
    led_state = "off"
    print("🔴 收到前端指令：关灯")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)