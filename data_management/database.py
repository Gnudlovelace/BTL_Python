import json
import sqlite3
from datetime import datetime

from config import DB_FILE, COT_DB

COT_JSON = ("do_dung_hien_co", "anh_urls")
FORMAT_GIO = "%Y-%m-%d %H:%M:%S"


def lay_gio():
    return datetime.now().strftime(FORMAT_GIO)


def nang_cap_bang(conn):
    cot_cu = {r[1] for r in conn.execute("PRAGMA table_info(tro)")}

    if "anh_urls" not in cot_cu:
        conn.execute("ALTER TABLE tro ADD COLUMN anh_urls TEXT")

    if "anh_url" in cot_cu:
        try:
            conn.execute("ALTER TABLE tro DROP COLUMN anh_url")
        except sqlite3.OperationalError:
            pass

    if "thoi_gian" not in cot_cu:
        conn.execute("ALTER TABLE tro ADD COLUMN thoi_gian TEXT")

    conn.execute("UPDATE tro SET thoi_gian = ? WHERE thoi_gian IS NULL", (lay_gio(),))


def tao_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tro (
                dia_chi_cu TEXT, dia_chi_moi TEXT, huyen_quan TEXT,
                gia INTEGER, dien_tich REAL,
                gia_dien INTEGER, gia_nuoc INTEGER, gia_dich_vu INTEGER,
                do_dung_hien_co TEXT, url TEXT PRIMARY KEY, anh_urls TEXT,
                thoi_gian TEXT
            )
            """
        )
        nang_cap_bang(conn)
    print(f"Đã tạo xong Database '{DB_FILE}' và bảng 'tro'.")


def luu_tro(ds_tro):
    if not ds_tro:
        return

    gio = lay_gio()
    dong = []
    for tro in ds_tro:
        gia_tri = []
        for cot in COT_DB:
            if cot == "thoi_gian":
                gia_tri.append(gio)
            elif cot in COT_JSON:
                gia_tri.append(json.dumps(tro.get(cot) or [], ensure_ascii=False))
            else:
                gia_tri.append(tro.get(cot))
        dong.append(tuple(gia_tri))

    with sqlite3.connect(DB_FILE) as conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO tro ({', '.join(COT_DB)}) "
            f"VALUES ({', '.join('?' * len(COT_DB))})",
            dong,
        )
