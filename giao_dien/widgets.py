from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QComboBox, QStylePainter, QStyle, QStyleOptionComboBox


class ComboNhieuLuaChon(QComboBox):
    def __init__(self):
        super().__init__()
        self.setModel(QStandardItemModel(self))
        self.setMaxVisibleItems(8)
        self.setCurrentIndex(-1)
        self.model().itemChanged.connect(self.cap_nhat)
        self.view().viewport().installEventFilter(self)

    def them_cac_muc(self, ds):
        for ten in ds:
            item = QStandardItem(ten)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            self.model().appendRow(item)
        self.setCurrentIndex(-1)

    def cac_item(self):
        return [self.model().item(i) for i in range(self.model().rowCount())]

    def da_chon(self):
        return [it.text() for it in self.cac_item() if it.checkState() == Qt.Checked]

    def dat_da_chon(self, ds):
        tap = {t.casefold() for t in ds}
        self.model().blockSignals(True)
        for it in self.cac_item():
            co_chon = it.text().casefold() in tap
            it.setCheckState(Qt.Checked if co_chon else Qt.Unchecked)
        self.model().blockSignals(False)
        self.cap_nhat()

    def bo_chon_tat_ca(self):
        self.dat_da_chon([])

    def cap_nhat(self, *_):
        self.model().blockSignals(True)
        for it in self.cac_item():
            if it.checkState() == Qt.Checked:
                it.setBackground(QBrush(QColor("#00bcd4")))
                it.setForeground(QBrush(QColor("#000000")))
            else:
                it.setData(None, Qt.BackgroundRole)
                it.setData(None, Qt.ForegroundRole)
        self.model().blockSignals(False)
        self.setToolTip(", ".join(self.da_chon()))
        self.update()

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        text = ", ".join(self.da_chon()) or "Tất cả quận / huyện"
        opt.currentText = self.fontMetrics().elidedText(
            text, Qt.ElideRight, max(self.width() - 40, 10))
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)

    def eventFilter(self, obj, event):
        if obj is self.view().viewport() and event.type() == event.MouseButtonRelease:
            index = self.view().indexAt(event.pos())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                da_tick = item.checkState() == Qt.Checked
                item.setCheckState(Qt.Unchecked if da_tick else Qt.Checked)
            return True
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        event.ignore()