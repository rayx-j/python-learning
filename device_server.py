from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# 初始化数据库（如果数据库文件不存在，就会自动创建）
def init_db():
    conn = sqlite3.connect('garden.db') # 创建/连接 garden.db 文件
    cursor = conn.cursor()
    # 创建一个表，用来存植物名字和它需要的最低湿度
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            min_moisture INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db() # 启动时先建表

# 1. 添加植物（带习性）
@app.route('/add_plant', methods=['POST'])
def add_plant():
    data = request.json
    name = data.get('name')
    min_moisture = data.get('min_moisture')
    
    conn = sqlite3.connect('garden.db')
    cursor = conn.cursor()
    # 把数据插进表里
    cursor.execute('INSERT INTO plants (name, min_moisture) VALUES (?, ?)', (name, min_moisture))
    conn.commit()
    conn.close()
    
    print(f"💾 已将 {name} (最低湿度:{min_moisture}%) 存入数据库")
    return jsonify({"status": "success"})

# 2. 获取所有植物
@app.route('/get_plants', methods=['GET'])
def get_plants():
    conn = sqlite3.connect('garden.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants')
    rows = cursor.fetchall() # 拿到所有行
    conn.close()
    
    # 把数据库查出来的数据，转换成前端喜欢的字典列表格式
    plants_list = []
    for row in rows:
        plants_list.append({"id": row[0], "name": row[1], "min_moisture": row[2]})
    
    return jsonify(plants_list)
# 4. 真正的删除接口（从 SQLite 数据库里抹掉）
@app.route('/delete_plant', methods=['POST'])
def delete_plant():
    data = request.json
    name = data.get('name')
    
    conn = sqlite3.connect('garden.db')
    cursor = conn.cursor()
    # SQL 命令：从 plants 表里删除名字等于 name 的那一行
    cursor.execute('DELETE FROM plants WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    
    print(f"🗑️ 数据库已彻底删除植物：{name}")
    return jsonify({"status": "success"})
# 3. 接收传感器数据并进行判断的接口
@app.route('/check_moisture', methods=['POST'])
def check_moisture():
    data = request.json
    name = data.get('name')
    current_moisture = data.get('current_moisture')
    
    conn = sqlite3.connect('garden.db')
    cursor = conn.cursor()
    # 去数据库里查一下，这种植物要求的最低湿度是多少
    cursor.execute('SELECT min_moisture FROM plants WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return jsonify({"status": "error", "message": "数据库里没找到这种植物"})
    
    min_required = result[0] # 提取出最低湿度要求
    
    # 核心逻辑：如果当前湿度 < 设定的最低湿度，就报警！
    if current_moisture < min_required:
        print(f"🚨 警报！{name} 湿度不足！当前:{current_moisture}%，需要:{min_required}%")
        return jsonify({
            "status": "warning", 
            "message": f"⚠️ 湿度不足！建议立刻浇水。(当前:{current_moisture}%, 需求:{min_required}%)"
        })
    else:
        print(f"✅ {name} 湿度正常。")
        return jsonify({
            "status": "ok", 
            "message": f"✅ 湿度正常，植物很健康。(当前:{current_moisture}%)"
        })
if __name__ == '__main__':
    import os
    # 让云端平台自己分配端口，如果没有就默认用 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)