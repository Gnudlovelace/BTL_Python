import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

DANH_SACH_QUAN_HUYEN = [
    "Ba Đình", "Bắc Từ Liêm", "Cầu Giấy", "Hà Đông", "Hai Bà Trưng",
    "Hoàn Kiếm", "Hoàng Mai", "Long Biên", "Nam Từ Liêm", "Tây Hồ",
    "Thanh Xuân", "Đống Đa", "Chương Mỹ", "Gia Lâm", "Hoài Đức",
    "Mê Linh", "Phú Xuyên", "Quốc Oai", "Sóc Sơn", "Thạch Thất",
    "Thanh Trì", "Thường Tín", "Đan Phượng", "Đông Anh",
]

DANH_SACH_DO_DUNG = [
    "Điều hòa", "Nóng lạnh", "Tủ lạnh", "Quạt", "Giường", "Bếp",
    "Bình chữa cháy",
]

NGUONG_RE = 3_500_000
NGUONG_RONG = 40
NGUONG_NHO = 30
NGUONG_VUA_RONG = 40
NGUONG_VUA_NHO = 30

TU_KHOA_MO_HO = [
    (["rẻ", "giá rẻ", "bình dân", "tiết kiệm", "sinh viên"],
     "gia_max", NGUONG_RE, "rẻ"),
    (["vừa", "vừa phải", "khá vừa", "rộng vừa", "nhỏ vừa"],
     "dien_tich_min", NGUONG_VUA_NHO, "vừa"),
    (["vừa", "vừa phải", "khá vừa", "rộng vừa", "nhỏ vừa"],
     "dien_tich_max", NGUONG_VUA_RONG, "vừa"),
    (["rộng", "rộng rãi", "thoáng"],
     "dien_tich_min", NGUONG_RONG, "rộng"),
    (["nhỏ", "nhỏ gọn"],
     "dien_tich_max", NGUONG_NHO, "nhỏ"),
]

TU_KHOA_DO_DUNG = {
    "điều hòa": "Điều hòa",
    "điều hoà": "Điều hòa",
    "nóng lạnh": "Nóng lạnh",
    "bình nóng lạnh": "Nóng lạnh",
    "tủ lạnh": "Tủ lạnh",
    "quạt": "Quạt",
    "giường": "Giường",
    "bếp": "Bếp",
    "bình chữa cháy": "Bình chữa cháy",
    "chữa cháy": "Bình chữa cháy",
    "pccc": "Bình chữa cháy",
}
