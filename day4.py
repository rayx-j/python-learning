print("--- 园林植物批量巡检系统 ---")
plants = ["月季", "银杏", "多肉", "桂花"]
for plant in plants:
    print(f"正在检查：{plant}")
    if plant == "多肉":
        print("  -> 多肉耐旱，少浇水。")
    elif plant == "月季":
        print("  -> 月季喜湿润，检查土壤，干透了就浇透。")
    else:
        print("  -> 普通植物，保持土壤微湿即可。")
    print("------------------------")
    print("浇水时间：", plant)
print("巡检完毕！")