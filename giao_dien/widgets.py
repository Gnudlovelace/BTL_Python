from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QComboBox, QStylePainter, QStyle, QStyleOptionComboBox


class ComboNhieuLuaChon(QComboBox):
    """Combo tick nhiều mục: bấm đầu ô để mở/thu gọn, giữ giá trị đã chọn.
    Không chọn mục nào = tất cả."""

    def __init__(self):
        super().__init__()
        self.setModel(QStandardItemModel(self))
        self.setMaxVisibleItems(8)
        self.setCurrentIndex(-1)
        self.model().itemChanged.connect(self._cap_nhat)
        self.view().viewport().installEventFilter(self)  # tick mà không đóng

    def them_cac_muc(self, ds):
        for ten in ds:
            item = QStandardItem(ten)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            self.model().appendRow(item)
        self.setCurrentIndex(-1)

    def _cac_item(self):
        return [self.model().item(i) for i in range(self.model().rowCount())]

    def da_chon(self):
        return [i.text() for i in self._cac_item()
                if i.checkState() == Qt.Checked]

    def dat_da_chon(self, ds):
        tap = {t.casefold() for t in ds}
        self.model().blockSignals(True)
        for i in self._cac_item():
            i.setCheckState(Qt.Checked if i.text().casefold() in tap
                            else Qt.Unchecked)
        self.model().blockSignals(False)
        self._cap_nhat()

    def bo_chon_tat_ca(self):
        self.dat_da_chon([])

    def _cap_nhat(self, *_):
        self.model().blockSignals(True)
        for i in self._cac_item():   # mục đã chọn tô xanh
            if i.checkState() == Qt.Checked:
                i.setBackground(QBrush(QColor("#00bcd4")))
                i.setForeground(QBrush(QColor("#000000")))
            else:
                i.setData(None, Qt.BackgroundRole)
                i.setData(None, Qt.ForegroundRole)
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
                item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked
                                   else Qt.Checked)
            return True
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        event.ignore()  
