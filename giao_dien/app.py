import sqlite3

from PyQt5.QtWidgets import QStackedWidget, QMessageBox

from chat_worker import ChatWorker
from chatbot import ChatbotManager
from config import DB_PATH
from loc_du_lieu import lay_so, phong_phu_hop
from trang_ket_qua import TrangKetQua
from trang_tim_kiem import TrangTimKiem


class AppTro(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.trang_1 = TrangTimKiem()
        self.trang_2 = TrangKetQua()
        self.chatbot = ChatbotManager()
        self.chat_worker = None

        self.addWidget(self.trang_1)
        self.addWidget(self.trang_2)

        self.trang_1.btn_tim_kiem.clicked.connect(self.tim_kiem)
        self.trang_1.btn_chat_gui.clicked.connect(self.gui_chat)
        self.trang_1.lineEdit_chat.returnPressed.connect(self.gui_chat)
        self.trang_2.btn_quay_lai.clicked.connect(lambda: self.setCurrentIndex(0))

        self.resize(900, 700)
        self.setWindowTitle("Hệ thống đề xuất phòng trọ")

    # ---- chatbot
    def gui_chat(self):
        t = self.trang_1
        cau_hoi = t.lineEdit_chat.text().strip()
        if not cau_hoi or (self.chat_worker and self.chat_worker.isRunning()):
            return
        t.btn_chat_gui.setEnabled(False)
        t.lbl_chat_phan_hoi.setText("Đang phân tích yêu cầu...")
        self.chat_worker = ChatWorker(self.chatbot, cau_hoi)
        self.chat_worker.xong.connect(self.nhan_phan_hoi_chat)
        self.chat_worker.start()

    def nhan_phan_hoi_chat(self, ket_qua):
        t = self.trang_1
        t.btn_chat_gui.setEnabled(True)
        t.lbl_chat_phan_hoi.setText(ket_qua["message"])
        tieu_chi = ket_qua.get("criteria")
        if ket_qua.get("status") and tieu_chi:
            self.ap_dung_tieu_chi(tieu_chi)
            t.lineEdit_chat.clear()

    def ap_dung_tieu_chi(self, tc):
        """Điền dữ kiện chatbot trích xuất vào bộ lọc.
        Mỗi yêu cầu mới thay thế hoàn toàn bộ lọc cũ (không chồng chất)."""
        t = self.trang_1
        if not (tc["quan_huyen"] or tc["do_dung"] or tc["gia_max"] is not None
                or tc["dien_tich_min"] is not None
                or tc["dien_tich_max"] is not None):
            return   # giữ nguyên bộ lọc hiện tại
        t.xoa_bo_loc()
        if tc["quan_huyen"]:
            t.combo_quan.dat_da_chon(tc["quan_huyen"])
        if tc["gia_max"] is not None:                    # đồng -> triệu
            t.lineEdit_4.setText(f"{tc['gia_max'] / 1_000_000:g}")
        if tc["dien_tich_min"] is not None:
            t.lineEdit.setText(f"{tc['dien_tich_min']:g}")
        if tc["dien_tich_max"] is not None:
            t.lineEdit_3.setText(f"{tc['dien_tich_max']:g}")
        for ten in tc["do_dung"]:
            if ten in t.o_do_dung:
                t.o_do_dung[ten].setChecked(True)

    # ---- tìm kiếm
    def tim_kiem(self):
        t = self.trang_1
        gia = lay_so(t.lineEdit_4.text())               # ô giá tính bằng triệu
        gia_max = round(gia * 1_000_000) if gia is not None else None
        quan = [q.casefold() for q in t.combo_quan.da_chon()]
        dt_min, dt_max = lay_so(t.lineEdit.text()), lay_so(t.lineEdit_3.text())
        do_dung = [ten for ten, o in t.o_do_dung.items() if o.isChecked()]

        # diện tích max < diện tích min
        if dt_min is not None and dt_max is not None and dt_max < dt_min:
            QMessageBox.warning(
                self, "Diện tích không hợp lệ",
                f"Diện tích tối đa ({dt_max:g} m²) không được nhỏ hơn "
                f"diện tích tối thiểu ({dt_min:g} m²).\nVui lòng nhập lại.")
            t.lineEdit_3.setFocus()
            t.lineEdit_3.selectAll()
            return

        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM tro").fetchall()

        ket_qua = [p for p in map(dict, rows)
                   if phong_phu_hop(p, gia_max, quan, dt_min, dt_max, do_dung)]
        self.trang_2.hien_thi_ket_qua(ket_qua)
        self.setCurrentIndex(1)
