import sqlite3

from PyQt5.QtWidgets import QStackedWidget, QMessageBox

from chat_worker import ChatWorker
from chatbot import ChatbotManager
from config import DB_PATH
from loc_du_lieu import doc_so, hop_dieu_kien
from trang_ket_qua import TrangKetQua
from trang_tim_kiem import TrangTimKiem


class AppTro(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.trang_tk = TrangTimKiem()
        self.trang_kq = TrangKetQua()
        self.chatbot = ChatbotManager()
        self.worker = None

        self.addWidget(self.trang_tk)
        self.addWidget(self.trang_kq)

        self.trang_tk.btn_tim_kiem.clicked.connect(self.tim_kiem)
        self.trang_tk.btn_chat_gui.clicked.connect(self.gui_chat)
        self.trang_tk.lineEdit_chat.returnPressed.connect(self.gui_chat)
        self.trang_kq.btn_quay_lai.clicked.connect(lambda: self.setCurrentIndex(0))

        self.resize(900, 700)
        self.setWindowTitle("Hệ thống đề xuất phòng trọ")

    def gui_chat(self):
        tk = self.trang_tk
        cau_hoi = tk.lineEdit_chat.text().strip()
        if not cau_hoi or (self.worker and self.worker.isRunning()):
            return

        tk.btn_chat_gui.setEnabled(False)
        tk.lbl_chat_phan_hoi.setText("Đang phân tích yêu cầu...")
        self.worker = ChatWorker(self.chatbot, cau_hoi)
        self.worker.xong.connect(self.nhan_chat)
        self.worker.start()

    def nhan_chat(self, kq):
        tk = self.trang_tk
        tk.btn_chat_gui.setEnabled(True)
        tk.lbl_chat_phan_hoi.setText(kq["message"])

        tc = kq.get("criteria")
        if kq.get("status") and tc:
            self.dien_bo_loc(tc)
            tk.lineEdit_chat.clear()

    def dien_bo_loc(self, tc):
        tk = self.trang_tk
        co_tieu_chi = (
            tc["quan_huyen"] or tc["do_dung"]
            or tc["gia_max"] is not None
            or tc["dien_tich_min"] is not None
            or tc["dien_tich_max"] is not None
        )
        if not co_tieu_chi:
            return

        tk.xoa_bo_loc()
        if tc["quan_huyen"]:
            tk.combo_quan.dat_da_chon(tc["quan_huyen"])
        if tc["gia_max"] is not None:
            tk.lineEdit_4.setText(f"{tc['gia_max'] / 1_000_000:g}")
        if tc["dien_tich_min"] is not None:
            tk.lineEdit.setText(f"{tc['dien_tich_min']:g}")
        if tc["dien_tich_max"] is not None:
            tk.lineEdit_3.setText(f"{tc['dien_tich_max']:g}")
        for ten in tc["do_dung"]:
            if ten in tk.o_do_dung:
                tk.o_do_dung[ten].setChecked(True)

    def tim_kiem(self):
        tk = self.trang_tk
        gia = doc_so(tk.lineEdit_4.text())
        gia_max = round(gia * 1_000_000) if gia is not None else None
        quan = [q.casefold() for q in tk.combo_quan.da_chon()]
        dt_min = doc_so(tk.lineEdit.text())
        dt_max = doc_so(tk.lineEdit_3.text())
        do_dung = [ten for ten, o in tk.o_do_dung.items() if o.isChecked()]

        if dt_min is not None and dt_max is not None and dt_max < dt_min:
            QMessageBox.warning(
                self, "Diện tích không hợp lệ",
                f"Diện tích tối đa ({dt_max:g} m²) không được nhỏ hơn "
                f"diện tích tối thiểu ({dt_min:g} m²).\nVui lòng nhập lại.")
            tk.lineEdit_3.setFocus()
            tk.lineEdit_3.selectAll()
            return

        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            dong = conn.execute("SELECT * FROM tro").fetchall()

        kq = [p for p in map(dict, dong)
              if hop_dieu_kien(p, gia_max, quan, dt_min, dt_max, do_dung)]
        self.trang_kq.hien_thi_ket_qua(kq)
        self.setCurrentIndex(1)