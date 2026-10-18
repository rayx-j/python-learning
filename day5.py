print("---园林植物数据库查询系统---")
plant_data={
    "月季":{"水分":"喜湿润","阳光":"全日照"},
    "银杏":{"水分":"耐旱","阳光":"全日照"},
    "多肉":{"水分":"少浇水","阳光":"半日照"}
}
for plant_name,info in plant_data.items():
    print(f"\n正在查询：{plant_name}")
    water_need=info["水分"]
    sunlight_need=info["阳光"]
    print(f"  -> 水分需求：{water_need}")
    print(f"  -> 阳光需求：{sunlight_need}")
print("\n查询完毕！")