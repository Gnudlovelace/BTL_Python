import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(ROOT_DIR, "image")
UI_DIR = os.path.join(ROOT_DIR, "ui")
DB_PATH = os.path.join(ROOT_DIR, "phongtro.db")

RONG, CAO = 350, 32
CHUA = "Chưa có dữ liệu"

TEN_ANH_NEN = ("background.jpg", "background.jpeg", "background.png",
               "nen.jpg", "nen.png")
DO_MO = 14
DO_TOI = 150

TEN_ANH_MAP = ("google_maps.png", "google_maps.jpg", "google_maps.svg")
CO_NUT_MAP = 34

SO_ANH_TAI_TRUOC = 5
ANH_TOI_DA_BYTE = 10_000_000
ANH_CHO = 10