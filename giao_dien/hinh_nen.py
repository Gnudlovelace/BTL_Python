import os
import re
from functools import lru_cache

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsBlurEffect

from config import IMAGE_DIR, TEN_ANH_NEN, DO_MO, DO_TOI
from styles import QSS_NEN


@lru_cache(maxsize=1)
def lay_anh_nen_mo():
    for ten in TEN_ANH_NEN:
        pm = QPixmap(os.path.join(IMAGE_DIR, ten))
        if not pm.isNull():
            return lam_mo(pm)
    return None


def lam_mo(pm):
    ban_kinh = max(DO_MO * pm.width() / 1000.0, 1.0)
    item = QGraphicsPixmapItem(pm)
    hieu_ung = QGraphicsBlurEffect()
    hieu_ung.setBlurRadius(ban_kinh)
    hieu_ung.setBlurHints(QGraphicsBlurEffect.QualityHint)
    item.setGraphicsEffect(hieu_ung)
    scene = QGraphicsScene()
    scene.addItem(item)

    anh = QImage(pm.size(), QImage.Format_ARGB32_Premultiplied)
    anh.fill(Qt.transparent)
    painter = QPainter(anh)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    scene.render(painter, QRectF(anh.rect()), QRectF(pm.rect()))
    painter.end()

    le = min(int(ban_kinh * 2), anh.width() // 4, anh.height() // 4)  # bỏ viền nhạt
    return QPixmap.fromImage(
        anh.copy(le, le, anh.width() - 2 * le, anh.height() - 2 * le)
    )


class NenAnhMixin:
    def _ap_dung_nen(self):
        ss = re.sub(r"(QWidget\s*\{\s*background-color:\s*)#2b2b2b",
                    r"\1transparent", self.styleSheet(), count=1)
        self.setStyleSheet(ss + QSS_NEN)

    def paintEvent(self, event):
        painter = QPainter(self)
        pm = lay_anh_nen_mo()
        if pm is None:
            painter.fillRect(self.rect(), QColor("#2b2b2b"))
            return
        cache = getattr(self, "_nen_cache", None)
        if cache is None or cache[0] != self.size():
            cache = (self.size(), pm.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation))
            self._nen_cache = cache
        anh = cache[1]
        painter.drawPixmap(0, 0, anh,
                           (anh.width() - self.width()) // 2,
                           (anh.height() - self.height()) // 2,
                           self.width(), self.height())
        painter.fillRect(self.rect(), QColor(0, 0, 0, DO_TOI))
