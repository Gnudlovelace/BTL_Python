import os

from PyQt5 import uic
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QLabel, QPushButton

from config import UI_DIR, RONG, CAO
from hinh_nen import NenAnhMixin
from styles import QSS_NUT_X
from widgets import ComboNhieuLuaChon


class TrangTimKiem(NenAnhMixin, QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "tim_kiem.ui"), self)

        self.o_do_dung = {
            "Điều hòa": self.checkBox_9, "Nóng lạnh": self.checkBox_6,
            "Tủ lạnh": self.checkBox_3, "Giường": self.checkBox_7,
            "Quạt": self.checkBox_4, "Bếp": self.checkBox_5,
            "Bình chữa cháy": self.checkBox_8,
        }
        self._dung_combo_quan()
        self._dung_gia_dien_tich()
        self._dung_do_dung()
        self._don_dep()
        self._ap_dung_nen()

    @staticmethod
    def _boc(cu, *phan, ngang=False):
        """Thay widget `cu` trong layout bằng một hàng gồm `phan`
        (widget hoặc chữ cố định). ngang=True: hàng rộng RONG, ô co giãn đều."""
        layout_cha = cu.parentWidget().layout()
        khung = QWidget()
        layout_cha.replaceWidget(cu, khung)   
        h = QHBoxLayout(khung)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        for p in phan:
            if isinstance(p, str):
                h.addWidget(QLabel(p))
            else:
                h.addWidget(p, 1 if ngang else 0)
        if ngang:
            khung.setFixedWidth(RONG)
        else:
            h.addStretch(1)
        return khung

    def _dung_combo_quan(self):
        ds = self.listQuanHuyen
        self.combo_quan = ComboNhieuLuaChon()
        self.combo_quan.them_cac_muc([ds.item(i).text() for i in range(ds.count())])
        self.combo_quan.setFixedSize(RONG, CAO)

        nut_x = QPushButton("✕")
        nut_x.setFixedSize(CAO, CAO)
        nut_x.setCursor(Qt.PointingHandCursor)
        nut_x.setToolTip("Bỏ chọn tất cả")
        nut_x.setStyleSheet(QSS_NUT_X)
        nut_x.clicked.connect(self.combo_quan.bo_chon_tat_ca)

        self._khung_quan = self._boc(ds, self.combo_quan, nut_x)
        ds.hide()
        self.btn_bo_chon_quan.hide()

    def _dung_gia_dien_tich(self):
        so = QRegExpValidator(QRegExp(r"^\d{0,4}([.,]\d{0,3})?$"))
        for o in (self.lineEdit_4, self.lineEdit, self.lineEdit_3):
            o.clear()
            o.setPlaceholderText("")
            o.setValidator(so)
            o.setFixedHeight(CAO)
        self.lineEdit_4.setFixedWidth(RONG)

        self._khung_gia = self._boc(self.lineEdit_4, self.lineEdit_4, "triệu đồng")
        self._trong = self._boc(self.lineEdit_3)   # chiếm chỗ ô cũ
        self._khung_dt = self._boc(self.lineEdit, "Từ:", self.lineEdit,
                                   "Đến:", self.lineEdit_3, ngang=True)

    def _dung_do_dung(self):
        """Đồ dùng xếp 3 cột, tổng rộng RONG; nút TÌM KIẾM rộng RONG."""
        grid = self.gridLayout
        cot = (RONG - 12) // 3
        o_list = list(self.o_do_dung.values())
        for o in o_list + [self.btn_tim_kiem]:
            grid.removeWidget(o)
        grid.setHorizontalSpacing(6)
        for c in range(3):
            grid.setColumnMinimumWidth(c, cot)
        grid.setColumnStretch(3, 1)  
        for i, o in enumerate(o_list):
            o.setFixedWidth(cot)
            grid.addWidget(o, i // 3, i % 3, Qt.AlignLeft)
        self.btn_tim_kiem.setFixedWidth(RONG)
        grid.addWidget(self.btn_tim_kiem, 3, 0, 1, 3, Qt.AlignLeft)

    def _don_dep(self):
        self.label_6.setText("Đồ dùng cơ bản:")
        self.lbl_goi_y_quan.hide()
        self.lbl_chat_tieu_de.setText("CHATBOT")
        self.lbl_chat_phan_hoi.setText("")
        self.lbl_chat_phan_hoi.setMinimumHeight(68)
        self.lineEdit_chat.setFixedHeight(68)
        self.btn_chat_gui.setFixedHeight(68)

    def xoa_bo_loc(self):
        """Đưa toàn bộ bộ lọc về trạng thái trống."""
        self.combo_quan.bo_chon_tat_ca()
        for o in (self.lineEdit_4, self.lineEdit, self.lineEdit_3):
            o.clear()
        for o in self.o_do_dung.values():
            o.setChecked(False)
