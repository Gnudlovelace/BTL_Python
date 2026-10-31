import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Danh sách quận / huyện hợp lệ (khớp với danh sách trong giao diện)
DANH_SACH_QUAN_HUYEN = [
    "Ba Đình", "Bắc Từ Liêm", "Cầu Giấy", "Hà Đông", "Hai Bà Trưng",
    "Hoàn Kiếm", "Hoàng Mai", "Long Biên", "Nam Từ Liêm", "Tây Hồ",
    "Thanh Xuân", "Đống Đa", "Chương Mỹ", "Gia Lâm", "Hoài Đức",
    "Mê Linh", "Phú Xuyên", "Quốc Oai", "Sóc Sơn", "Thạch Thất",
    "Thanh Trì", "Thường Tín", "Đan Phượng", "Đông Anh",
]

# Danh sách đồ dùng hợp lệ (khớp với các checkbox trong giao diện)
DANH_SACH_DO_DUNG = [
    "Điều hòa", "Nóng lạnh", "Tủ lạnh", "Quạt", "Giường", "Bếp",
    "Bình chữa cháy",
]


# ---------------------------------------------------------------------------
# Từ mô tả mơ hồ -> giá trị bộ lọc cụ thể.
# Chỉnh các con số ở đây để thay đổi "rẻ" là bao nhiêu, "rộng" là bao nhiêu...
# ---------------------------------------------------------------------------
NGUONG_RE = 3_500_000        # "rẻ"   -> giá tối đa 3,5 triệu
NGUONG_RONG = 40             # "rộng" -> diện tích tối thiểu 40 m²
NGUONG_NHO = 20              # "nhỏ"  -> diện tích tối đa 20 m²

# (danh sách từ khóa, trường, giá trị, mô tả hiển thị)
TU_KHOA_MO_HO = [
    (["rẻ", "giá rẻ", "bình dân", "tiết kiệm", "sinh viên"],
     "gia_max", NGUONG_RE, "rẻ"),
    (["rộng", "rộng rãi", "thoáng"],
     "dien_tich_min", NGUONG_RONG, "rộng"),
    (["nhỏ", "nhỏ gọn"],
     "dien_tich_max", NGUONG_NHO, "nhỏ"),
]

# Từ khóa -> tên đồ dùng (fallback)
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
