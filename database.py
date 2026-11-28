import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "wardrobe.db"

TYPE_MAP = {
    "1": "上衣",
    "2": "下著",
    "3": "外套",
    "4": "飾品",
}

SEED_WARDROBE = [
    ("上衣", "T恤", "白", "夏", "休閒", "white_t.jpg"),
    ("上衣", "短袖", "藍", "夏", "運動", "blue_sport_tee.jpg"),
    ("上衣", "襯衫", "淺藍", "春", "上班", "blue_shirt.jpg"),
    ("上衣", "打底衫", "黑", "秋", "逛街", "black_base.jpg"),
    ("上衣", "毛衣", "米白", "冬", "上學", "cream_sweater.jpg"),
    ("下著", "短褲", "牛仔藍", "夏", "休閒", "denim_shorts.jpg"),
    ("下著", "短褲", "黑", "夏", "運動", "sport_shorts.jpg"),
    ("下著", "長褲", "黑", "秋", "上班", "black_pants.jpg"),
    ("下著", "長裙", "卡其", "春", "逛街", "khaki_skirt.jpg"),
    ("下著", "長褲", "深灰", "冬", "上學", "gray_pants.jpg"),
    ("外套", "外套", "卡其", "秋", "休閒", "khaki_coat.jpg"),
    ("外套", "外套", "黑", "冬", "上班", "black_coat.jpg"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed_if_empty=True):
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wardrobe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                sub_type TEXT NOT NULL,
                color TEXT NOT NULL,
                season TEXT NOT NULL,
                occasion TEXT NOT NULL,
                img TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        if seed_if_empty:
            count = conn.execute("SELECT COUNT(*) AS cnt FROM wardrobe").fetchone()["cnt"]
            if count == 0:
                conn.executemany(
                    """
                    INSERT INTO wardrobe (type, sub_type, color, season, occasion, img)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    SEED_WARDROBE,
                )
        conn.commit()


def normalize_type(c_type):
    val = str(c_type).strip()
    return TYPE_MAP.get(val, val)


def add_cloth_item(c_type, sub_type, color, season, occasion, img=""):
    cloth_type = normalize_type(c_type)
    clean_sub = str(sub_type).strip()
    clean_color = str(color).strip()
    clean_season = str(season).strip()
    clean_occasion = str(occasion).strip()
    clean_img = str(img).strip()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO wardrobe (type, sub_type, color, season, occasion, img)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cloth_type, clean_sub, clean_color, clean_season, clean_occasion, clean_img),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_clothes():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, type, sub_type, color, season, occasion, img
            FROM wardrobe
            ORDER BY id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_color_counts():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT color, COUNT(*) AS total
            FROM wardrobe
            GROUP BY color
            ORDER BY total DESC
            """
        ).fetchall()
        return {row["color"]: row["total"] for row in rows}
