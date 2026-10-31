from PyQt5.QtCore import QThread, pyqtSignal


class ChatWorker(QThread):
    xong = pyqtSignal(dict)

    def __init__(self, chatbot, cau_hoi):
        super().__init__()
        self.chatbot, self.cau_hoi = chatbot, cau_hoi

    def run(self):
        try:
            ket_qua = self.chatbot.xu_ly_cau_hoi(self.cau_hoi)
        except Exception as e:
            ket_qua = {"status": False, "message": f"Chatbot gặp lỗi: {e}",
                       "criteria": None, "nguon": None}
        self.xong.emit(ket_qua)
