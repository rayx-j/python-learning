import network
import time
import urequests  # 1. 修改这里，换成刚刚安装的 urequests
import json
from machine import Pin, ADC

# 2. 设置传感器
sensor = ADC(Pin(36))
sensor.atten(ADC.ATTN_11DB)

# 3. 你的 Wi-Fi 信息（一定要改成你手机开的热点！）
WIFI_SSID = "荣耀X50"
WIFI_PASS = "12345678"

# 4. 云端的接口地址
SERVER_URL = "http://rayx360.pythonanywhere.com/check_moisture"
PLANT_NAME = "笔尖茉莉"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('正在连接WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    print('\nWiFi连接成功! IP:', wlan.ifconfig()[0])

connect_wifi()
print("硬件启动，开始监测土壤...")

while True:
    raw_value = sensor.read()
    dry_val = 2500
    wet_val = 1000
    moisture = int((dry_val - raw_value) / (dry_val - wet_val) * 100)
    
    if moisture > 100: moisture = 100
    if moisture < 0: moisture = 0

    print(f"原始值: {raw_value} | 换算真实湿度: {moisture}%")

    try:
        print("正在发送数据到云端...")
        # 5. 使用 urequests.post 发送请求
        response = urequests.post(
            SERVER_URL,
            data=json.dumps({"name": PLANT_NAME, "current_moisture": moisture}),
            headers={'Content-Type': 'application/json'}
        )
        print("云端回复成功！状态码:", response.status_code)
        response.close() # 6. 记得关闭连接，释放内存
    except Exception as e:
        print("发送失败，请检查网络或云端服务器:", e)

    print("等待 10 秒进入下一次检测...\n")
    time.sleep(10)