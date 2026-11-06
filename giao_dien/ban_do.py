import os
from functools import lru_cache
from urllib.parse import quote_plus

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPainterPath, QColor, QDesktopServices

from config import IMAGE_DIR, TEN_ANH_MAP


def ve_icon_mac_dinh():
    co = 96
    pm = QPixmap(co, co)
    pm.fill(Qt.transparent)

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)

    cx, cy, r = co / 2, co * 0.36, co * 0.30

    ghim = QPainterPath()
    ghim.addEllipse(cx - r, cy - r, 2 * r, 2 * r)

    mui = QPainterPath()
    mui.moveTo(cx - r * 0.92, cy + r * 0.45)
    mui.lineTo(cx, co * 0.93)
    mui.lineTo(cx + r * 0.92, cy + r * 0.45)
    mui.closeSubpath()

    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#ea4335"))
    painter.drawPath(ghim.united(mui))

    painter.setBrush(QColor("white"))
    painter.drawEllipse(int(cx - r * 0.42), int(cy - r * 0.42),
                        int(r * 0.84), int(r * 0.84))
    painter.end()
    return QIcon(pm)


@lru_cache(maxsize=1)
def lay_icon():
    for ten in TEN_ANH_MAP:
        path = os.path.join(IMAGE_DIR, ten)
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon
    return ve_icon_mac_dinh()


def mo_map(dia_chi):
    dia_chi = (dia_chi or "").strip()
    if "hà nội" not in dia_chi.casefold() and "ha noi" not in dia_chi.casefold():
        dia_chi += ", Hà Nội"
    url = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(dia_chi)
    QDesktopServices.openUrl(QUrl(url))