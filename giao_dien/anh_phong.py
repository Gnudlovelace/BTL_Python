import json
import urllib.request
from urllib.parse import urlsplit

from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QPainter, QPixmap
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from config import ANH_TOI_DA_BYTE, ANH_THOI_GIAN_CHO


class _TinHieu(QObject):
    xong = pyqtSignal(str, bytes)   


class _TacVuTai(QRunnable):
    def __init__(self, url, referer, tin_hieu):
        super().__init__()
        self.url, self.referer, self.tin_hieu = url, referer, tin_hieu

    def run(self):
        du_lieu = b""
        try:
            goc = urlsplit(self.referer or self.url)
            req = urllib.request.Request(self.url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": f"{goc.scheme}://{goc.netloc}/",
            })
            with urllib.request.urlopen(req, timeout=ANH_THOI_GIAN_CHO) as r:
                du_lieu = r.read(ANH_TOI_DA_BYTE + 1)
            if len(du_lieu) > ANH_TOI_DA_BYTE:
                du_lieu = b""
        except Exception:
            du_lieu = b""
        self.tin_hieu.xong.emit(self.url, du_lieu)


class KhoAnh(QObject):
    """Tải ảnh nền + cache trong bộ nhớ."""
    san_sang = pyqtSignal(str)       # url vừa tải xong 

    def __init__(self):
        super().__init__()
        self._cache = {}             # url 
        self._dang_tai = set()
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(3)
        self._tin_hieu = _TinHieu()
        self._tin_hieu.xong.connect(self._nhan)

    def lay(self, url):
        """bytes nếu đã có, b"" nếu tải lỗi, None nếu chưa tải."""
        return self._cache.get(url)

    def tai(self, url, referer=None):
        if not url or url in self._cache or url in self._dang_tai:
            return
        self._dang_tai.add(url)
        self._pool.start(_TacVuTai(url, referer, self._tin_hieu))

    def _nhan(self, url, du_lieu):
        self._cache[url] = du_lieu
        self._dang_tai.discard(url)
        self.san_sang.emit(url)


_kho = None


def kho_anh():
    global _kho
    if _kho is None:
        _kho = KhoAnh()
    return _kho


def doc_danh_sach_anh(p):
    """Danh sách link ảnh của một phòng (dict lấy từ DB). Trả về [] nếu chưa có."""
    try:
        ds = json.loads(p.get("anh_urls") or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(ds, list):
        return []
    return [u.strip() for u in ds if isinstance(u, str) and u.strip()]


class LabelAnh(QLabel):
    """Nhãn tự vẽ ảnh vừa khít kích thước hiện tại (giữ tỉ lệ), vẽ lại mỗi khi đổi cỡ.
    Vẽ trong paintEvent nên luôn đúng cỡ thật, kể cả khi ảnh có sẵn trước lúc cửa sổ hiện ra."""

    def __init__(self, *args):
        super().__init__(*args)
        self._pm = None
        self._cache = (None, None)       # (kích thước, ảnh đã co giãn)

    def dat_anh(self, pm):
        self._pm = pm
        self._cache = (None, None)
        self.update()

    def paintEvent(self, event):
        if self._pm is None:
            super().paintEvent(event)    # không có ảnh 
            return
        if self._cache[0] != self.size():
            self._cache = (self.size(), self._pm.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        anh = self._cache[1]
        painter = QPainter(self)
        painter.drawPixmap((self.width() - anh.width()) // 2,
                           (self.height() - anh.height()) // 2, anh)


QSS_MUI_TEN = """
QPushButton { background-color: rgba(60, 60, 60, 230); color: #fff; font-size: 22px;
              font-weight: bold; border: 1px solid #666; border-radius: 6px; }
QPushButton:hover { background-color: #00bcd4; color: black; }
QPushButton:disabled { color: #555; border-color: #333; }
"""


class DialogXemAnh(QDialog):
    """Xem toàn bộ ảnh của một phòng, chuyển ảnh bằng nút < > hoặc phím mũi tên."""

    def __init__(self, danh_sach_url, referer=None, parent=None):
        super().__init__(parent)
        self.ds = list(danh_sach_url)
        self.vi_tri = 0
        self.referer = referer
        self.setWindowTitle("Ảnh phòng")
        self.resize(820, 580)
        self.setStyleSheet("QDialog { background-color: #1e1e1e; }"
                           "QLabel { color: #e0e0e0; }")

        self.lbl = LabelAnh("Đang tải ảnh...")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.lbl.setMinimumSize(640, 400)   # khung ảnh 

        self.nut_trai = QPushButton("<")
        self.nut_phai = QPushButton(">")
        for nut in (self.nut_trai, self.nut_phai):
            nut.setFixedSize(44, 80)
            nut.setCursor(Qt.PointingHandCursor)
            nut.setFocusPolicy(Qt.NoFocus)
            nut.setStyleSheet(QSS_MUI_TEN)
        self.nut_trai.clicked.connect(lambda: self._chuyen(-1))
        self.nut_phai.clicked.connect(lambda: self._chuyen(+1))
        co_nhieu = len(self.ds) > 1
        self.nut_trai.setVisible(co_nhieu)
        self.nut_phai.setVisible(co_nhieu)

        hang_anh = QHBoxLayout()
        hang_anh.addWidget(self.nut_trai)
        hang_anh.addWidget(self.lbl, 1)
        hang_anh.addWidget(self.nut_phai)

        self.lbl_dem = QLabel("")
        self.lbl_dem.setAlignment(Qt.AlignCenter)
        nut_mo = QPushButton("Mở bằng trình duyệt")
        nut_mo.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.ds[self.vi_tri])))
        nut_dong = QPushButton("Đóng")
        nut_dong.clicked.connect(self.accept)
        hang_duoi = QHBoxLayout()
        hang_duoi.addWidget(self.lbl_dem, 1)
        hang_duoi.addWidget(nut_mo)
        hang_duoi.addWidget(nut_dong)

        bo_cuc = QVBoxLayout(self)
        bo_cuc.addLayout(hang_anh, 1)
        bo_cuc.addLayout(hang_duoi)

        kho = kho_anh()
        kho.san_sang.connect(self._khi_tai_xong)
        self.finished.connect(lambda *_: kho.san_sang.disconnect(self._khi_tai_xong))
        self._hien_thi()

    @property
    def url_hien_tai(self):
        return self.ds[self.vi_tri]

    def _chuyen(self, buoc):
        if len(self.ds) > 1:
            self.vi_tri = (self.vi_tri + buoc) % len(self.ds)   # hết ảnh thì vòng lại
            self._hien_thi()

    def _hien_thi(self):
        kho = kho_anh()
        self.lbl_dem.setText(f"{self.vi_tri + 1} / {len(self.ds)}")
        url = self.url_hien_tai
        du_lieu = kho.lay(url)
        if du_lieu is None:                  # chưa tải 
            self.lbl.dat_anh(None)
            self.lbl.setText("Đang tải ảnh...")
            kho.tai(url, self.referer)
        else:
            pm = QPixmap()
            if du_lieu and pm.loadFromData(du_lieu):
                self.lbl.setText("")
                self.lbl.dat_anh(pm)
                # In kích thước để dễ kiểm tra 
                print(f"[anh_phong] ảnh gốc {pm.width()}x{pm.height()} px, "
                      f"khung hiển thị {self.lbl.width()}x{self.lbl.height()} px")
            else:
                self.lbl.dat_anh(None)
                self.lbl.setText("Không tải được ảnh này.\n"
                                 "Bạn có thể bấm \"Mở bằng trình duyệt\".")
        # tải sẵn ảnh 
        if len(self.ds) > 1:
            kho.tai(self.ds[(self.vi_tri + 1) % len(self.ds)], self.referer)
            kho.tai(self.ds[(self.vi_tri - 1) % len(self.ds)], self.referer)

    def _khi_tai_xong(self, url):
        if url == self.url_hien_tai:
            self._hien_thi()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self._chuyen(-1)
        elif event.key() == Qt.Key_Right:
            self._chuyen(+1)
        else:
            super().keyPressEvent(event)
