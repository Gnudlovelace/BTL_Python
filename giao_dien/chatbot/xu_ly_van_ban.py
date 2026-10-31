"""Xử lý văn bản: bỏ dấu, tra địa danh -> quận / huyện."""
import re
import unicodedata

from .cau_hinh import DANH_SACH_QUAN_HUYEN
# Địa danh -> quận / huyện nằm ở đó và lân cận: xem file dia_danh.py (dễ bổ sung thêm)
from .dia_danh import DIA_DANH


def _chuan_hoa_ten(ten, danh_sach):
    """Đưa một tên bất kỳ về đúng tên trong danh sách hợp lệ (không phân biệt hoa/thường)."""
    ten = str(ten).strip().casefold()
    ten = re.sub(r"^(quận|huyện|q\.|h\.)\s*", "", ten)
    for hop_le in danh_sach:
        if hop_le.casefold() == ten:
            return hop_le
    return None


def _them_khong_trung(danh_sach, phan_tu):
    if phan_tu and phan_tu not in danh_sach:
        danh_sach.append(phan_tu)


def _bo_dau(s):
    """Chữ thường, bỏ dấu tiếng Việt: 'Bách Khoa' -> 'bach khoa'."""
    s = unicodedata.normalize("NFD", str(s).casefold().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def _mau_tu(khoa):
    """Mẫu regex khớp nguyên cụm từ (không khớp giữa một từ khác)."""
    return re.compile(r"(?<!\w)" + re.escape(khoa) + r"(?!\w)")


# Biên dịch sẵn một lần. Khóa dài xếp trước để "bệnh viện bạch mai" thắng "bạch mai".
_DIA_DANH_SAP_XEP = sorted(
    ((_mau_tu(_bo_dau(k)), v) for k, v in DIA_DANH.items()),
    key=lambda kv: len(kv[0].pattern),
    reverse=True,
)
_QUAN_KHONG_DAU = [(_mau_tu(_bo_dau(q)), q) for q in DANH_SACH_QUAN_HUYEN]


def tim_quan_huyen_trong_cau(cau):
    """Tìm các quận/huyện liên quan trong câu: địa danh (trường, bệnh viện, khu vực...)
    và tên quận/huyện nêu trực tiếp. Hiểu cả khi người dùng gõ không dấu."""
    con_lai = _bo_dau(cau)
    ket_qua = []

    for mau, ds_quan in _DIA_DANH_SAP_XEP:
        if mau.search(con_lai):
            for q in ds_quan:
                _them_khong_trung(ket_qua, q)
            con_lai = mau.sub(" ", con_lai)   # tránh khớp lặp phần đã dùng

    for mau, q in _QUAN_KHONG_DAU:
        if mau.search(con_lai):
            _them_khong_trung(ket_qua, q)
    return ket_qua
