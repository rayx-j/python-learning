print("--- 园林植物浇水小助手 ---")
weather = input("今天是什么天气？（晴天/雨天）：")
moisture = int(input("请输入现在的土壤湿度（0-100）："))
if weather == "雨天":
    print("🌧️ 今天下雨，不需要浇水。")
elif moisture < 30:
    print("🌱 土壤太干了，快给你的植物浇水吧！")
elif moisture > 80:
    print("💧 土壤太湿了，小心烂根，今天不要浇水。")
else:
    print("✅ 湿度刚刚好，今天不用管它。")
print("--- 助手运行完毕 ---")