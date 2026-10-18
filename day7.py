plant_data = {
    "月季": {"水分": 30, "阳光": "全日照"},
    "银杏": {"水分": 20, "阳光": "全日照"},
    "多肉": {"水分": 10, "阳光": "半日照"}
}
def check_plant(name, current_moisture):
    target = plant_data[name]["水分"]
    
    if current_moisture < target:
        print(f"⚠️ 【{name}】缺水啦！建议立刻浇水。")
    else:
        print(f"✅ 【{name}】水分充足，继续加油。")
print("--- 欢迎使用园林植物养护管家 ---")
while True:
    user_input = input("\n请输入要查询的植物（输入'退出'结束）：")
    if user_input == "退出":
        print("管家下班了，明天见！👋")
        break  
    elif user_input in plant_data:
        moisture_str = input(f"请输入【{user_input}】的当前湿度（0-100）：")
        moisture = int(moisture_str) 
        check_plant(user_input, moisture) 
    else:
        print("抱歉，数据库里没有这种植物，请重新输入。")
