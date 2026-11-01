import network
import time
import urequests
import json
from machine import Pin, ADC

sensor = ADC(Pin(36))
sensor.atten(ADC.ATTN_11DB)

# 👇 新增：设置板载蓝色小灯（GPIO 2） 👇
led = Pin(2, Pin.OUT)
led.value(0) # 默认关灯

WIFI_SSID = "你的WiFi名字"
WIFI_PASS = "你的WiFi密码"
SERVER_URL = "http://rayx360.pythonanywhere.com/check_moisture"
PLANT_NAME = "笔尖茉莉"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('正在连接WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(15):
            if wlan.isconnected(): break
            time.sleep(1)
            print('.', end='')
    print('\nWiFi连接成功!' if wlan.isconnected() else '\nWiFi连接超时！')
    return wlan.isconnected()

connect_wifi()
print("硬件启动...")

while True:
    raw_value = sensor.read()
    dry_val = 2500
    wet_val = 1000
    moisture = int((dry_val - raw_value) / (dry_val - wet_val) * 100)
    if moisture > 100: moisture = 100
    if moisture < 0: moisture = 0

    try:
        # 发送数据，并接收云端的指令
        response = urequests.post(
            SERVER_URL,
            data=json.dumps({"name": PLANT_NAME, "current_moisture": moisture}),
            headers={'Content-Type': 'application/json'}
        )
        # 👇 新增：解析云端返回的 JSON 数据 👇
        result = response.json()
        response.close()
        
        # 👇 新增：如果云端说开灯，就开灯；说关灯，就关灯 👇
        if result.get("led_status") == "on":
            if led.value() == 0:
                print("💡 收到云端指令：开灯！")
                led.value(1)
        else:
            if led.value() == 1:
                print("🌑 收到云端指令：关灯！")
                led.value(0)

        print(f"湿度: {moisture}% | 发送成功！")
    except Exception as e:
        print("网络波动，等会重试:", e)

    time.sleep(5) # 为了快速测试，改成5秒发一次