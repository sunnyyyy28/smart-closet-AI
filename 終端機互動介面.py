import random
from database import (
    init_db,
    add_cloth_item,
    get_all_clothes,
    get_color_counts,
)


def recommend_outfit(temp, occasion, wardrobe):
    """
    依氣溫與場合篩選衣物，回傳推薦組合字典：
    {"top": dict | None, "bottom": dict | None, "outer": dict | None}
    """
    try:
        temp_val = float(temp)
    except (ValueError, TypeError):
        temp_val = 22.0

    occasion_clean = str(occasion).strip()

    if occasion_clean == "運動":
        if temp_val >= 25:
            target_seasons = ["夏"]
            need_outer = False
        elif temp_val >= 18:
            target_seasons = ["春", "夏", "秋"]
            need_outer = False
        else:
            target_seasons = ["秋", "冬"]
            need_outer = True
    elif occasion_clean in ["正裝", "上班"]:
        if temp_val >= 28:
            target_seasons = ["夏", "春"]
            need_outer = False
        elif temp_val >= 19:
            target_seasons = ["春", "秋"]
            need_outer = True
        else:
            target_seasons = ["冬", "秋"]
            need_outer = True
    else:
        if temp_val >= 27:
            target_seasons = ["夏"]
            need_outer = False
        elif temp_val >= 21:
            target_seasons = ["春", "夏"]
            need_outer = False
        elif temp_val >= 16:
            target_seasons = ["秋", "春"]
            need_outer = True
        else:
            target_seasons = ["冬", "秋"]
            need_outer = True

    def pick_by_type(item_type):
        matched = [
            item for item in wardrobe
            if item.get("type") == item_type
            and item.get("season") in target_seasons
            and item.get("occasion") == occasion_clean
        ]
        if not matched:
            matched = [
                item for item in wardrobe
                if item.get("type") == item_type
                and item.get("season") in target_seasons
            ]
        if not matched:
            matched = [item for item in wardrobe if item.get("type") == item_type]

        return random.choice(matched) if matched else None

    return {
        "top": pick_by_type("上衣"),
        "bottom": pick_by_type("下著"),
        "outer": pick_by_type("外套") if need_outer else None,
    }


def format_outfit_summary(result):
    parts = []
    for key, label in [("top", "上衣"), ("bottom", "下著"), ("outer", "外套")]:
        item = result.get(key)
        if item:
            parts.append(f"{item.get('color', '')}色{item.get('sub_type', '')}")
        elif key != "outer":
            parts.append(f"無合適{label}")
    return " + ".join(parts) if parts else "目前衣櫃沒有可搭配的衣物"


def main():
    init_db(seed_if_empty=True)

    while True:
        print("\n" + "=" * 50)
        print("💡 救救穿搭黑洞！告別「衣」問三不知的自動化專屬造型系統 💡")
        print("=" * 50)
        print("1. ➕ 新增衣物到衣櫃 (手動標籤)")
        print("2. ✨ 幫我搭配今日穿搭 (演算法推薦)")
        print("3. 📊 查看我的衣櫃色彩分析 (圓餅圖)")
        print("4. ❌ 離開系統")
        print("-" * 50)

        choice = input("👉 請輸入數字選擇功能 (1-4): ").strip()

        if choice == "1":
            add_clothes_ui()
        elif choice == "2":
            recommend_outfit_ui()
        elif choice == "3":
            show_chart_ui()
        elif choice == "4":
            print("👋 感謝使用自動化專屬造型系統，系統已關閉。")
            break
        else:
            print("⚠️ 輸入錯誤！請輸入 1 到 4 的數字喔！")


def add_clothes_ui():
    print("\n--- [➕ 新增衣物到衣櫃 ➕] ---")
    print("衣物種類清單：1.上衣 2.下著 3.外套 4.飾品")
    c_type = input("請輸入種類編號 (1-4): ").strip()

    clothes = input("請輸入衣物細分種類 (T恤、短袖、打底衫、襯衫、毛衣、套裝、外套、短褲、短裙、長褲、長裙、飾品): ").strip()
    color = input("請輸入衣物顏色 (例如：黑、白、紅、藍): ").strip()
    season = input("請輸入適合季節 (春、夏、秋、冬): ").strip()
    occasion = input("請輸入適合場合 (休閒、正裝、運動、上學、上班、逛街、旅遊): ").strip()
    img = input("請輸入圖片檔名（可先留空直接按 Enter）: ").strip()

    new_id = add_cloth_item(c_type, clothes, color, season, occasion, img)
    print(f"\n✅ 已存入資料庫（編號 #{new_id}）：【{season}季 - {occasion}場合】的【{color}色{clothes}】")


def recommend_outfit_ui():
    print("\n--- [✨ 今日穿搭推薦 ✨] ---")

    use_api = input("需要自動抓取今天的天氣嗎？(輸入 Y 自動抓取，輸入 N 手動輸入氣溫): ").strip().upper()
    if use_api == "Y":
        print("☁️ 正在連線氣象局抓取天氣...")
        current_temp = 22
    else:
        current_temp = input("請手動輸入現在氣溫 (例如: 22): ").strip()

    occasion = input("請問今天要去什麼場合？(休閒、正裝、運動、上學、上班、逛街、旅遊): ").strip()

    print(f"\n⏳ 正在為您計算【氣溫 {current_temp}度】+【{occasion}場合】的最佳穿搭...")

    wardrobe = get_all_clothes()
    result = recommend_outfit(current_temp, occasion, wardrobe)
    summary = format_outfit_summary(result)

    print(f"\n🎉 搭配完成！為您推薦：{summary}")


def show_chart_ui():
    print("\n--- [📊 衣櫃色彩分析 📊] ---")
    counts = get_color_counts()
    if not counts:
        print("目前衣櫃裡還沒有衣物喔！")
        return

    total = sum(counts.values())
    print(f"目前衣櫃共有 {total} 件衣物，顏色分布如下：")
    for color, cnt in counts.items():
        pct = (cnt / total) * 100
        print(f"  - {color}色：{cnt} 件 ({pct:.1f}%)")


if __name__ == "__main__":
    main()
