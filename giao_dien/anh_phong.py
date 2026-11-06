import json
import urllib.request
from urllib.parse import urlsplit

from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QPainter, QPixmap
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy, QVBoxLayout)

from config import ANH_TOI_DA_BYTE, ANH_CHO

QSS_NUT = """
QPushButton { background-color: rgba(60, 60, 60, 230); color: #fff; font-size: 22px;
              font-weight: bold; border: 1px solid #666; border-radius: 6px; }
QPushButton:hover { background-color: #00bcd4; color: black; }
QPushButton:disabled { color: #555; border-color: #333; }
"""


class TinHieu(QObject):
    xong = pyqtSignal(str, bytes)


class TacVuTai(QRunnable):
    def __init__(self, url, ref, tin_hieu):
        super().__init__()
        self.url, self.ref, self.tin_hieu = url, ref, tin_hieu

    def run(self):
        data = b""
        try:
            goc = urlsplit(self.ref or self.url)
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"{goc.scheme}://{goc.netloc}/",
            })
            with urllib.request.urlopen(req, timeout=ANH_CHO) as r:
                data = r.read(ANH_TOI_DA_BYTE + 1)
            if len(data) > ANH_TOI_DA_BYTE:
                data = b""
        except Exception:
            data = b""
        self.tin_hieu.xong.emit(self.url, data)


class KhoAnh(QObject):
    san_sang = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cache = {}
        self.dang_tai = set()
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(3)
        self.tin_hieu = TinHieu()
        self.tin_hieu.xong.connect(self.nhan_anh)

    def lay_anh(self, url):
        return self.cache.get(url)

    def tai_anh(self, url, ref=None):
        if not url or url in self.cache or url in self.dang_tai:
            return
        self.dang_tai.add(url)
        self.pool.start(TacVuTai(url, ref, self.tin_hieu))

    def nhan_anh(self, url, data):
        self.cache[url] = data
        self.dang_tai.discard(url)
        self.san_sang.emit(url)


_kho = None


def lay_kho():
    global _kho
    if _kho is None:
        _kho = KhoAnh()
    return _kho


def doc_ds_anh(phong):
    try:
        ds = json.loads(phong.get("anh_urls") or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(ds, list):
        return []
    return [u.strip() for u in ds if isinstance(u, str) and u.strip()]


class LabelAnh(QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        self.pm = None
        self.cache = (None, None)

    def dat_anh(self, pm):
        self.pm = pm
        self.cache = (None, None)
        self.update()

    def paintEvent(self, event):
        if self.pm is None:
            super().paintEvent(event)
            return

        if self.cache[0] != self.size():
            self.cache = (self.size(), self.pm.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        anh = self.cache[1]
        painter = QPainter(self)
        painter.drawPixmap(
            (self.width() - anh.width()) // 2,
            (self.height() - anh.height()) // 2,
            anh,
        )


class DialogXemAnh(QDialog):
    def __init__(self, ds_url, ref=None, parent=None):
        super().__init__(parent)
        self.ds = list(ds_url)
        self.vi_tri = 0
        self.ref = ref

        self.setWindowTitle("Ảnh phòng")
        self.resize(820, 580)
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }"
                           "QLabel { color: #e0e0e0; }")

        self.lbl = LabelAnh("Đang tải ảnh...")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.lbl.setMinimumSize(640, 400)

        self.nut_trai = QPushButton("<")
        self.nut_phai = QPushButton(">")
        co_nhieu = len(self.ds) > 1
        for nut in (self.nut_trai, self.nut_phai):
            nut.setFixedSize(44, 80)
            nut.setCursor(Qt.PointingHandCursor)
            nut.setFocusPolicy(Qt.NoFocus)
            nut.setStyleSheet(QSS_NUT)
            nut.setVisible(co_nhieu)
        self.nut_trai.clicked.connect(lambda: self.chuyen_anh(-1))
        self.nut_phai.clicked.connect(lambda: self.chuyen_anh(+1))

        hang_anh = QHBoxLayout()
        hang_anh.addWidget(self.nut_trai)
        hang_anh.addWidget(self.lbl, 1)
        hang_anh.addWidget(self.nut_phai)

        self.lbl_dem = QLabel("")
        self.lbl_dem.setAlignment(Qt.AlignCenter)
        nut_mo = QPushButton("Mở bằng trình duyệt")
        nut_mo.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url_hien)))
        nut_dong = QPushButton("Đóng")
        nut_dong.clicked.connect(self.accept)

        hang_duoi = QHBoxLayout()
        hang_duoi.addWidget(self.lbl_dem, 1)
        hang_duoi.addWidget(nut_mo)
        hang_duoi.addWidget(nut_dong)

        bo_cuc = QVBoxLayout(self)
        bo_cuc.addLayout(hang_anh, 1)
        bo_cuc.addLayout(hang_duoi)

        kho = lay_kho()
        kho.san_sang.connect(self.khi_xong)
        self.finished.connect(lambda *_: kho.san_sang.disconnect(self.khi_xong))
        self.hien_anh()

    @property
    def url_hien(self):
        return self.ds[self.vi_tri]

    def chuyen_anh(self, buoc):
        if len(self.ds) > 1:
            self.vi_tri = (self.vi_tri + buoc) % len(self.ds)
            self.hien_anh()

    def hien_anh(self):
        kho = lay_kho()
        self.lbl_dem.setText(f"{self.vi_tri + 1} / {len(self.ds)}")

        url = self.url_hien
        data = kho.lay_anh(url)

        if data is None:
            self.lbl.dat_anh(None)
            self.lbl.setText("Đang tải ảnh...")
            kho.tai_anh(url, self.ref)
        else:
            pm = QPixmap()
            if data and pm.loadFromData(data):
                self.lbl.setText("")
                self.lbl.dat_anh(pm)
                print(f"[anh_phong] ảnh gốc {pm.width()}x{pm.height()} px, "
                      f"khung hiển thị {self.lbl.width()}x{self.lbl.height()} px")
            else:
                self.lbl.dat_anh(None)
                self.lbl.setText("Không tải được ảnh này.\n"
                                 "Bạn có thể bấm \"Mở bằng trình duyệt\".")

        if len(self.ds) > 1:
            kho.tai_anh(self.ds[(self.vi_tri + 1) % len(self.ds)], self.ref)
            kho.tai_anh(self.ds[(self.vi_tri - 1) % len(self.ds)], self.ref)

    def khi_xong(self, url):
        if url == self.url_hien:
            self.hien_anh()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.chuyen_anh(-1)
        elif event.key() == Qt.Key_Right:
            self.chuyen_anh(+1)
        else:
            super().keyPressEvent(event)