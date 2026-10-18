def check_watering(plant, moisture):
    print(f"正在检查植物：【{plant}】")
    
    if moisture < 10:
        print("  -> 警告：土壤太干，需要浇水！🌱")
    else:
        print("  -> 状态良好，暂不浇水。✅")
    
    print("-" * 20) # 打印一条分割线
print("--- 智能浇水系统启动 ---")
check_watering("月季", 15)
check_watering("银杏", 60)
check_watering("多肉", 25)
print("--- 检查结束 ---")