import network
import time
import urequests
import json
from machine import Pin, ADC, deepsleep

# 设置传感器和灯
sensor = ADC(Pin(36))
sensor.atten(ADC.ATTN_11DB)
led = Pin(2, Pin.OUT)
led.value(0) 

WIFI_SSID = "荣耀X50" # 记得改
WIFI_PASS = "12345678" # 记得改
SERVER_URL = "http://rayx360.pythonanywhere.com/check_moisture"
PLANT_NAME = "笔尖茉莉"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('正在连接WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(10): # 最多等10秒，防止死机
            if wlan.isconnected(): break
            time.sleep(1)
            print('.', end='')
    return wlan.isconnected()

print("硬件唤醒...")

if connect_wifi():
    # 1. 读取真实湿度
    raw_value = sensor.read()
    dry_val = 2500
    wet_val = 1000
    moisture = int((dry_val - raw_value) / (dry_val - wet_val) * 100)
    if moisture > 100: moisture = 100
    if moisture < 0: moisture = 0

    print(f"当前湿度: {moisture}%")

    # 2. 边缘计算：如果湿度低于40%，自动开启“水泵”（蓝灯亮5秒）
    if moisture < 40:
        print("🚨 湿度低于40%，正在自动浇水（亮灯模拟）...")
        led.value(1)
        time.sleep(5) # 模拟浇水5秒
        led.value(0)
    else:
        print("水分充足，不用浇水。")

    # 3. 把数据发给云端
    try:
        response = urequests.post(
            SERVER_URL,
            data=json.dumps({"name": PLANT_NAME, "current_moisture": moisture}),
            headers={'Content-Type': 'application/json'}
        )
        print("云端回复:", response.status_code)
        response.close()
    except Exception as e:
        print("发送失败:", e)

else:
    print("WiFi连接失败，跳过本次发送。")

# 4. 核心魔法：进入深度睡眠！
print("进入深度睡眠 10 秒...")
time.sleep(1) # 给串口打印留一点时间
# 这里的时间单位是微秒，10 * 1000000 = 10秒
# 以后如果是 12 小时，就改成 12 * 60 * 60 * 1000000
deepsleep(10 * 1000000) 