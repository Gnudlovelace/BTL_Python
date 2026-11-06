import os

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(ROOT_DIR, "phongtro.db")

load_dotenv(os.path.join(ROOT_DIR, ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.5-flash"

COT_DB = [
    "dia_chi_cu", "dia_chi_moi", "huyen_quan", "gia", "dien_tich",
    "gia_dien", "gia_nuoc", "gia_dich_vu", "do_dung_hien_co",
    "url", "anh_urls", "thoi_gian",
]
