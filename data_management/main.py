from browser import ham_chung_tai_trang
from database import setup_database
from guland import ham_rieng_scraping_guland
from phongtro123 import ham_scrape_phongtro123_bam_card

if __name__ == "__main__":
    setup_database()

    try:
        print("=== Đang quét guland ===")
        html = ham_chung_tai_trang("https://guland.vn/cho-thue-phong-tro-ha-noi", so_lan_bam=4)
        print("Processing...")
        ham_rieng_scraping_guland(html)
    except Exception as e:
        print(f"Lỗi khi quét guland: {e}")

    try:
        print("\n=== Đang quét phongtro123 ===")
        ham_scrape_phongtro123_bam_card("https://phongtro123.com/tinh-thanh/ha-noi", so_trang=3)
    except Exception as e:
        print(f"Lỗi khi quét phongtro123: {e}")
