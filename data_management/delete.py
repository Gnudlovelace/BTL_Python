import sqlite3
from datetime import datetime, timedelta

from config import DB_FILE
from database import FORMAT_GIO, nang_cap_bang

SO_NGAY = 7


def xoa_tro_cu():
    moc = (datetime.now() - timedelta(days=SO_NGAY)).strftime(FORMAT_GIO)
    with sqlite3.connect(DB_FILE) as conn:
        nang_cap_bang(conn)
        so_dong = conn.execute("DELETE FROM tro WHERE thoi_gian < ?", (moc,)).rowcount
    print(f"Đã xóa {so_dong} bản ghi cũ hơn {SO_NGAY} ngày.")


if __name__ == "__main__":
    xoa_tro_cu()
