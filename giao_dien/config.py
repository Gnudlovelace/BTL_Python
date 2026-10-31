import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
IMAGE_DIR = os.path.join(ROOT_DIR, "image")
UI_DIR = os.path.join(ROOT_DIR, "ui")
DB_PATH = os.path.join(ROOT_DIR, "phongtro.db")


RONG, CAO = 350, 32          
CHUA = "Chưa có dữ liệu"


# Ảnh nền 
TEN_ANH_NEN = ("background.jpg", "background.jpeg", "background.png",
               "nen.jpg", "nen.png")
DO_MO = 14      # bán kính làm mờ (tính trên ảnh rộng 1000px)
DO_TOI = 150    # 0-255: lớp đen phủ lên ảnh


# Ảnh nút bản đồ 
TEN_ANH_MAP = ("google_maps.png", "google_maps.jpg", "google_maps.svg")
KICH_THUOC_NUT_MAP = 34

# Ảnh phòng:
SO_ANH_TAI_SAN = 5            
ANH_TOI_DA_BYTE = 10_000_000  
ANH_THOI_GIAN_CHO = 10       
