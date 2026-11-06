from browser import tai_trang
from database import tao_database
from guland import cao_guland
from phongtro123 import cao_phongtro123

if __name__ == "__main__":
    tao_database()

    try:
        print("=== Đang quét guland ===")
        html = tai_trang("https://guland.vn/cho-thue-phong-tro-ha-noi", so_lan_bam=4)
        print("Processing...")
        cao_guland(html)
    except Exception as e:
        print(f"Lỗi khi quét guland: {e}")

    try:
        print("\n=== Đang quét phongtro123 ===")
        cao_phongtro123("https://phongtro123.com/tinh-thanh/ha-noi", so_trang=3)
    except Exception as e:
        print(f"Lỗi khi quét phongtro123: {e}")
