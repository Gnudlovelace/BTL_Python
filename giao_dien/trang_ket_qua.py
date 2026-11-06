import json
import os
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from anh_phong import DialogXemAnh, doc_ds_anh, lay_kho
from ban_do import lay_icon, mo_map
from config import UI_DIR, CHUA, CO_NUT_MAP, SO_ANH_TAI_TRUOC
from hinh_nen import NenAnhMixin
from styles import QSS_CARD

QSS_NUT_SX = """
QPushButton { background-color: #3a3a3a; color: #e0e0e0;
              border: 1px solid #555; border-radius: 5px; padding: 7px 14px; }
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:checked { background-color: #00bcd4; color: black;
                      border-color: #00bcd4; font-weight: bold; }
"""

QSS_NUT_MAP = """
QPushButton { background: transparent; border: none; }
QPushButton:hover { background-color: rgba(255,255,255,40); border-radius: 6px; }
"""

QSS_NUT_ANH = """
QPushButton { background-color: #3a3a3a; color: #e0e0e0;
              border: 1px solid #555; border-radius: 6px; padding: 0 12px; }
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:disabled { color: #777; border-color: #3a3a3a; }
"""

QSS_KHONG_CO = "QLabel { color: #bbb; font-size: 14px; padding: 30px; }"


def dinh_dang(gia_tri, mau="{:,}"):
    return mau.format(gia_tri) if gia_tri is not None else CHUA


def tinh_ngay_dang(thoi_gian):
    try:
        gio_dang = datetime.strptime(thoi_gian, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return CHUA
    so_ngay = (datetime.now() - gio_dang).days
    return "hôm nay" if so_ngay <= 0 else f"{so_ngay} ngày trước"


class TrangKetQua(NenAnhMixin, QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "ket_qua.ui"), self)
        self.lay_ds = self.verticalLayout_2
        self.ap_nen()

        self.ds = []
        self.nut_tang = self.tao_nut_sx("Tăng dần")
        self.nut_giam = self.tao_nut_sx("Giảm dần")

        for i, w in enumerate((QLabel("Sắp xếp theo giá:"), self.nut_tang, self.nut_giam)):
            self.horizontalLayout.insertWidget(2 + i, w)

        self.nut_tang.clicked.connect(lambda: self.chon_sx(self.nut_tang))
        self.nut_giam.clicked.connect(lambda: self.chon_sx(self.nut_giam))

    @staticmethod
    def tao_nut_sx(chu):
        nut = QPushButton(chu)
        nut.setCheckable(True)
        nut.setCursor(Qt.PointingHandCursor)
        nut.setStyleSheet(QSS_NUT_SX)
        return nut

    def chon_sx(self, nut):
        khac = self.nut_giam if nut is self.nut_tang else self.nut_tang
        khac.setChecked(False)
        self.ve_lai()

    @staticmethod
    def tao_nut_map(dia_chi):
        nut = QPushButton()
        nut.setIcon(lay_icon())
        nut.setIconSize(QSize(CO_NUT_MAP - 8, CO_NUT_MAP - 8))
        nut.setFixedSize(CO_NUT_MAP, CO_NUT_MAP)
        nut.setFlat(True)
        nut.setStyleSheet(QSS_NUT_MAP)

        if dia_chi:
            nut.setCursor(Qt.PointingHandCursor)
            nut.setToolTip("Xem trên Google Maps: " + dia_chi)
            nut.clicked.connect(lambda _=False, d=dia_chi: mo_map(d))
        else:
            nut.setEnabled(False)
            nut.setToolTip("Phòng này chưa có địa chỉ")
        return nut

    def tao_nut_anh(self, ds_anh, url):
        nut = QPushButton("Xem ảnh")
        nut.setFixedHeight(CO_NUT_MAP)
        nut.setStyleSheet(QSS_NUT_ANH)

        if ds_anh:
            nut.setCursor(Qt.PointingHandCursor)
            nut.setToolTip(f"Xem {len(ds_anh)} ảnh phòng")
            nut.clicked.connect(
                lambda _=False, a=ds_anh, r=url: DialogXemAnh(a, r, self).exec_())
        else:
            nut.setEnabled(False)
            nut.setToolTip("Phòng này chưa có ảnh")
        return nut

    def tao_card(self, phong, stt):
        card = QFrame()
        card.setObjectName("cardPhong")
        card.setStyleSheet(QSS_CARD)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)

        try:
            do_dung = ", ".join(json.loads(phong["do_dung_hien_co"] or "[]"))
        except (json.JSONDecodeError, TypeError):
            do_dung = phong["do_dung_hien_co"]

        url = phong["url"] or ""
        cac_dong = [
            (f"PHÒNG {stt}", "tieuDeCard"),
            (f"Địa chỉ cũ: {phong['dia_chi_cu'] or CHUA}", ""),
            (f"Địa chỉ mới: {phong['dia_chi_moi'] or CHUA}", ""),
            (f"Quận / huyện: {phong['huyen_quan'] or CHUA}", ""),
            (f"Giá: {dinh_dang(phong['gia'], '{:,} VNĐ/tháng')}", "giaCard"),
            (f"Diện tích: {dinh_dang(phong['dien_tich'], '{} m²')}", ""),
            (f"Giá điện: {dinh_dang(phong['gia_dien'], '{:,} VNĐ/kWh')}", ""),
            (f"Giá nước: {dinh_dang(phong['gia_nuoc'], '{:,} VNĐ')}", ""),
            (f"Giá dịch vụ: {dinh_dang(phong['gia_dich_vu'], '{:,} VNĐ')}", ""),
            (f"Đồ dùng hiện có: {do_dung or CHUA}", ""),
            (f'<a href="{url}">URL: {url}</a>' if url else f"URL: {CHUA}", "urlCard"),
            (f"Thời gian đăng: {tinh_ngay_dang(phong.get('thoi_gian'))}", ""),
        ]

        for text, ten_obj in cac_dong:
            nhan = QLabel(text)
            nhan.setWordWrap(True)
            if ten_obj:
                nhan.setObjectName(ten_obj)
            if ten_obj == "urlCard":
                nhan.setOpenExternalLinks(True)
                nhan.setTextInteractionFlags(Qt.TextBrowserInteraction)
            layout.addWidget(nhan)

        dia_chi = (phong["dia_chi_moi"] or phong["dia_chi_cu"] or "").strip()

        hang_nut = QHBoxLayout()
        hang_nut.setContentsMargins(0, 0, 0, 0)
        hang_nut.addWidget(self.tao_nut_map(dia_chi))
        hang_nut.addWidget(self.tao_nut_anh(doc_ds_anh(phong), url))
        hang_nut.addStretch()
        layout.addLayout(hang_nut)
        return card

    def hien_thi_ket_qua(self, ds):
        self.ds = ds
        self.nut_tang.setChecked(False)
        self.nut_giam.setChecked(False)
        self.ve_lai()

    def sap_xep_gia(self, ds):
        co_gia = [p for p in ds if p["gia"] is not None]
        thieu_gia = [p for p in ds if p["gia"] is None]
        co_gia.sort(key=lambda p: p["gia"], reverse=self.nut_giam.isChecked())
        return co_gia + thieu_gia

    def ve_lai(self):
        ds = list(self.ds)
        if self.nut_tang.isChecked() or self.nut_giam.isChecked():
            ds = self.sap_xep_gia(ds)

        lay = self.lay_ds
        while lay.count():
            w = lay.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

        if ds:
            for i, phong in enumerate(ds, 1):
                lay.addWidget(self.tao_card(phong, i))
            for phong in ds[:SO_ANH_TAI_TRUOC]:
                ds_anh = doc_ds_anh(phong)
                if ds_anh:
                    lay_kho().tai_anh(ds_anh[0], phong.get("url"))
        else:
            nhan = QLabel("Không tìm thấy phòng phù hợp với điều kiện tìm kiếm.")
            nhan.setWordWrap(True)
            nhan.setAlignment(Qt.AlignCenter)
            nhan.setStyleSheet(QSS_KHONG_CO)
            lay.addWidget(nhan)

        lay.addStretch()