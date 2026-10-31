import json
import os
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from anh_phong import DialogXemAnh, doc_danh_sach_anh, kho_anh
from ban_do import lay_icon_map, mo_google_map
from config import UI_DIR, CHUA, KICH_THUOC_NUT_MAP, SO_ANH_TAI_SAN
from hinh_nen import NenAnhMixin
from styles import QSS_CARD


def dinh_dang(v, mau="{:,}"):
    return mau.format(v) if v is not None else CHUA


def thoi_gian_dang(thoi_gian):
    try:
        so_ngay = (datetime.now() - datetime.strptime(thoi_gian, "%Y-%m-%d %H:%M:%S")).days
    except (TypeError, ValueError):
        return CHUA
    if (so_ngay<=0):
        return "hôm nay"
    else:
        return f"{so_ngay} ngày trước"


class TrangKetQua(NenAnhMixin, QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "ket_qua.ui"), self)
        self.danh_sach_layout = self.verticalLayout_2   
        self._ap_dung_nen()

        # Nút sắp xếp theo giá
        self.ds = [] 
        self.nut_tang = self._tao_nut_sap_xep("Tăng dần")
        self.nut_giam = self._tao_nut_sap_xep("Giảm dần")
        for i, w in enumerate((QLabel("Sắp xếp theo giá:"),
                               self.nut_tang, self.nut_giam)):
            self.horizontalLayout.insertWidget(2 + i, w)  
        self.nut_tang.clicked.connect(lambda: self._chon_sap_xep(self.nut_tang))
        self.nut_giam.clicked.connect(lambda: self._chon_sap_xep(self.nut_giam))

    @staticmethod
    def _tao_nut_sap_xep(chu):
        nut = QPushButton(chu)
        nut.setCheckable(True)
        nut.setCursor(Qt.PointingHandCursor)
        nut.setStyleSheet("""
            QPushButton { background-color: #3a3a3a; color: #e0e0e0;
                          border: 1px solid #555; border-radius: 5px;
                          padding: 7px 14px; }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:checked { background-color: #00bcd4; color: black;
                                  border-color: #00bcd4; font-weight: bold; }
        """)
        return nut

    def _chon_sap_xep(self, nut):
        """Chỉ một nút được bật; bấm lại nút đang bật = về thứ tự mặc định."""
        khac = self.nut_giam if nut is self.nut_tang else self.nut_tang
        khac.setChecked(False)
        self.ve_lai()

    def tao_card(self, p, stt):
        card = QFrame()
        card.setObjectName("cardPhong")
        card.setStyleSheet(QSS_CARD)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)

        try:
            do_dung = ", ".join(json.loads(p["do_dung_hien_co"] or "[]"))
        except (json.JSONDecodeError, TypeError):
            do_dung = p["do_dung_hien_co"]

        url = p["url"] or ""
        dong = [
            (f"PHÒNG {stt}", "tieuDeCard"),
            (f"Địa chỉ cũ: {p['dia_chi_cu'] or CHUA}", ""),
            (f"Địa chỉ mới: {p['dia_chi_moi'] or CHUA}", ""),
            (f"Quận / huyện: {p['huyen_quan'] or CHUA}", ""),
            (f"Giá: {dinh_dang(p['gia'], '{:,} VNĐ/tháng')}", "giaCard"),
            (f"Diện tích: {dinh_dang(p['dien_tich'], '{} m²')}", ""),
            (f"Giá điện: {dinh_dang(p['gia_dien'], '{:,} VNĐ/kWh')}", ""),
            (f"Giá nước: {dinh_dang(p['gia_nuoc'], '{:,} VNĐ')}", ""),
            (f"Giá dịch vụ: {dinh_dang(p['gia_dich_vu'], '{:,} VNĐ')}", ""),
            (f"Đồ dùng hiện có: {do_dung or CHUA}", ""),
            (f'<a href="{url}">URL: {url}</a>' if url else f"URL: {CHUA}", "urlCard"),
            (f"Thời gian đăng: {thoi_gian_dang(p.get('thoi_gian'))}", ""),
        ]
        for text, ten in dong:
            lb = QLabel(text)
            lb.setWordWrap(True)
            if ten:
                lb.setObjectName(ten)
            if ten == "urlCard":
                lb.setOpenExternalLinks(True)
                lb.setTextInteractionFlags(Qt.TextBrowserInteraction)
            layout.addWidget(lb)

        #ban do
        dia_chi = (p["dia_chi_moi"] or p["dia_chi_cu"] or "").strip()
        nut_map = QPushButton()
        nut_map.setIcon(lay_icon_map())
        nut_map.setIconSize(QSize(KICH_THUOC_NUT_MAP - 8, KICH_THUOC_NUT_MAP - 8))
        nut_map.setFixedSize(KICH_THUOC_NUT_MAP, KICH_THUOC_NUT_MAP)
        nut_map.setFlat(True)
        nut_map.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            "QPushButton:hover { background-color: rgba(255,255,255,40);"
            " border-radius: 6px; }")
        if dia_chi:
            nut_map.setCursor(Qt.PointingHandCursor)
            nut_map.setToolTip("Xem trên Google Maps: " + dia_chi)
            nut_map.clicked.connect(lambda _=False, d=dia_chi: mo_google_map(d))
        else:
            nut_map.setEnabled(False)
            nut_map.setToolTip("Phòng này chưa có địa chỉ")

        # Nút xem ảnh: 
        anh_urls = doc_danh_sach_anh(p)
        nut_anh = QPushButton("Xem ảnh")
        nut_anh.setFixedHeight(KICH_THUOC_NUT_MAP)
        nut_anh.setStyleSheet(
            "QPushButton { background-color: #3a3a3a; color: #e0e0e0;"
            " border: 1px solid #555; border-radius: 6px; padding: 0 12px; }"
            "QPushButton:hover { background-color: #4a4a4a; }"
            "QPushButton:disabled { color: #777; border-color: #3a3a3a; }")
        if anh_urls:
            nut_anh.setCursor(Qt.PointingHandCursor)
            nut_anh.setToolTip(f"Xem {len(anh_urls)} ảnh phòng")
            nut_anh.clicked.connect(
                lambda _=False, a=anh_urls, r=url: DialogXemAnh(a, r, self).exec_())
        else:
            nut_anh.setEnabled(False)
            nut_anh.setToolTip("Phòng này chưa có ảnh")

        hang_nut = QHBoxLayout()
        hang_nut.setContentsMargins(0, 0, 0, 0)
        hang_nut.addWidget(nut_map)
        hang_nut.addWidget(nut_anh)
        hang_nut.addStretch()
        layout.addLayout(hang_nut)
        return card

    def hien_thi_ket_qua(self, ds):
        """Nhận kết quả tìm kiếm mới: bỏ sắp xếp cũ và vẽ lại."""
        self.ds = ds
        self.nut_tang.setChecked(False)
        self.nut_giam.setChecked(False)
        self.ve_lai()

    def ve_lai(self):
        ds = list(self.ds)
        if self.nut_tang.isChecked() or self.nut_giam.isChecked():
            co_gia = [p for p in ds if p["gia"] is not None]
            thieu = [p for p in ds if p["gia"] is None]   # chưa có giá -> cuối
            ds = sorted(co_gia, key=lambda p: p["gia"],
                        reverse=self.nut_giam.isChecked()) + thieu

        lay = self.danh_sach_layout
        while lay.count():                      # xóa kết quả cũ
            w = lay.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        if ds:
            for i, p in enumerate(ds, 1):
                lay.addWidget(self.tao_card(p, i))
            for p in ds[:SO_ANH_TAI_SAN]:       
                ds_anh = doc_danh_sach_anh(p)
                if ds_anh:
                    kho_anh().tai(ds_anh[0], p.get("url"))
        else:
            khong_co = QLabel("Không tìm thấy phòng phù hợp với điều kiện tìm kiếm.")
            khong_co.setWordWrap(True)
            khong_co.setAlignment(Qt.AlignCenter)
            khong_co.setStyleSheet(
                "QLabel { color: #bbb; font-size: 14px; padding: 30px; }")
            lay.addWidget(khong_co)
        lay.addStretch()
