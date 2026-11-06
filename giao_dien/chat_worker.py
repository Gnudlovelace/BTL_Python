from PyQt5.QtCore import QThread, pyqtSignal


class ChatWorker(QThread):
    xong = pyqtSignal(dict)

    def __init__(self, chatbot, cau_hoi):
        super().__init__()
        self.chatbot, self.cau_hoi = chatbot, cau_hoi

    def run(self):
        try:
            kq = self.chatbot.xu_ly(self.cau_hoi)
        except Exception as e:
            kq = {
                "status": False,
                "message": f"Chatbot gặp lỗi: {e}",
                "criteria": None,
                "nguon": None,
            }
        self.xong.emit(kq)