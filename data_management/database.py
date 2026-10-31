import json
import sqlite3
from datetime import datetime

from config import DB_FILE, COT_DB

COT_JSON = ("do_dung_hien_co", "anh_urls")   
DINH_DANG_GIO = "%Y-%m-%d %H:%M:%S"          


def gio_hien_tai():
    return datetime.now().strftime(DINH_DANG_GIO)


def nang_cap_bang(conn):
    cot_hien_co = {r[1] for r in conn.execute("PRAGMA table_info(tro)")}
    if "anh_urls" not in cot_hien_co:        
        conn.execute("ALTER TABLE tro ADD COLUMN anh_urls TEXT")
    if "anh_url" in cot_hien_co:          
        try:
            conn.execute("ALTER TABLE tro DROP COLUMN anh_url")
        except sqlite3.OperationalError:
            pass                             
    if "thoi_gian" not in cot_hien_co:     
        conn.execute("ALTER TABLE tro ADD COLUMN thoi_gian TEXT")
    # Bản ghi cũ chưa có thời gian -> coi như vừa thêm bây giờ (được giữ thêm 7 ngày,
    # không bị xóa oan ngay lần dọn đầu tiên)
    conn.execute("UPDATE tro SET thoi_gian = ? WHERE thoi_gian IS NULL", (gio_hien_tai(),))


def setup_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tro (
                dia_chi_cu TEXT, dia_chi_moi TEXT, huyen_quan TEXT,
                gia INTEGER, dien_tich REAL,
                gia_dien INTEGER, gia_nuoc INTEGER, gia_dich_vu INTEGER,
                do_dung_hien_co TEXT, url TEXT PRIMARY KEY, anh_urls TEXT,
                thoi_gian TEXT
            )
        ''')
        nang_cap_bang(conn)
    print(f"Đã tạo xong Database '{DB_FILE}' và bảng 'tro'.")


def ham_sqlite_luu_nhieu(data_list):
    if not data_list:
        return
    bay_gio = gio_hien_tai()
    rows = [
        tuple(bay_gio if c == "thoi_gian"
              else json.dumps(d.get(c) or [], ensure_ascii=False) if c in COT_JSON
              else d.get(c)
              for c in COT_DB)
        for d in data_list
    ]
    with sqlite3.connect(DB_FILE) as conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO tro ({', '.join(COT_DB)}) "
            f"VALUES ({', '.join('?' * len(COT_DB))})", rows)
