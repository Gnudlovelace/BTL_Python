import os
from functools import lru_cache
from urllib.parse import quote_plus

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPainterPath, QColor, QDesktopServices

from config import IMAGE_DIR, TEN_ANH_MAP


@lru_cache(maxsize=1)
def lay_icon_map():
    for ten in TEN_ANH_MAP:
        duong_dan = os.path.join(IMAGE_DIR, ten)
        if os.path.exists(duong_dan):
            icon = QIcon(duong_dan)
            if not icon.isNull():
                return icon

    s = 96
    pm = QPixmap(s, s)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    cx, r = s / 2, s * 0.30
    cy = s * 0.36
    ghim = QPainterPath()
    ghim.addEllipse(cx - r, cy - r, 2 * r, 2 * r)
    mui = QPainterPath()
    mui.moveTo(cx - r * 0.92, cy + r * 0.45)
    mui.lineTo(cx, s * 0.93)
    mui.lineTo(cx + r * 0.92, cy + r * 0.45)
    mui.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#ea4335"))
    p.drawPath(ghim.united(mui))
    p.setBrush(QColor("white"))
    p.drawEllipse(int(cx - r * 0.42), int(cy - r * 0.42),
                  int(r * 0.84), int(r * 0.84))
    p.end()
    return QIcon(pm)


def mo_google_map(dia_chi):
    dia_chi = (dia_chi or "").strip()
    if "hà nội" not in dia_chi.casefold() and "ha noi" not in dia_chi.casefold():
        dia_chi += ", Hà Nội"
    url = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(dia_chi)
    QDesktopServices.openUrl(QUrl(url))
