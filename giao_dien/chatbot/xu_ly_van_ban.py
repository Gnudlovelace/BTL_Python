import re
import unicodedata

from .cau_hinh import DANH_SACH_QUAN_HUYEN
from .dia_danh import DIA_DANH


def chuan_ten(ten, danh_sach):
    ten = str(ten).strip().casefold()
    ten = re.sub(r"^(quận|huyện|q\.|h\.)\s*", "", ten)
    for hop_le in danh_sach:
        if hop_le.casefold() == ten:
            return hop_le
    return None


def them(ds, x):
    if x and x not in ds:
        ds.append(x)


def bo_dau(s):
    s = unicodedata.normalize("NFD", str(s).casefold().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def mau_tu(khoa):
    return re.compile(r"(?<!\w)" + re.escape(khoa) + r"(?!\w)")


DS_DIA_DANH = sorted(
    ((mau_tu(bo_dau(k)), v) for k, v in DIA_DANH.items()),
    key=lambda kv: len(kv[0].pattern),
    reverse=True,
)
DS_QUAN = [(mau_tu(bo_dau(q)), q) for q in DANH_SACH_QUAN_HUYEN]


def tim_quan(cau):
    con_lai = bo_dau(cau)
    kq = []

    for mau, ds_quan in DS_DIA_DANH:
        if mau.search(con_lai):
            for q in ds_quan:
                them(kq, q)
            con_lai = mau.sub(" ", con_lai)

    for mau, q in DS_QUAN:
        if mau.search(con_lai):
            them(kq, q)
    return kq
