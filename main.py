#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: wangt@njust.edu.cn
Last edited: 2019.7.30
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox, QDialog, QFileDialog
from PyQt5.QtCore import Qt,pyqtSlot, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor

from ui_main import Ui_Dialog
from shpreader import *

CUR_VERSION = 'V2019.0730'


class MainDlg(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle("SHPViewer - " + CUR_VERSION)

        windowFlag  = Qt.Dialog
        windowFlag |= Qt.WindowMinimizeButtonHint
        windowFlag |= Qt.WindowMaximizeButtonHint
        windowFlag |= Qt.WindowCloseButtonHint 
        self.setWindowFlags(windowFlag)

        self.shps = []
        self.colors = [
            QColor(0,255,0),
            QColor(0,0,255),
            QColor(0,255,255),
            QColor(128,128,255),
        ]

        self.leftMouseDown = False
        self.mouseDownPos = None
        self.orig = QPointF(0,0)
        self.ratio = 10.0
    
    @pyqtSlot()
    def on_btn_clear_clicked(self):
        self.shps = []
        self.repaint()

    @pyqtSlot()
    def on_btn_open_file_clicked(self):
        filename,ok = QFileDialog.getOpenFileName(self,
                                r'选择shp文件', r'', "shp file (*.shp)")

        if not ok:
            return

        shp = read_shp(filename)
        if not shp:
            QMessageBox.information(self, "SHPViewer", "invalid shp file!")
            return

        shp['color'] = self.colors[ len(self.shps) % len(self.colors) ]

        # init orig and ratio when first shp loaded
        if not self.shps:
            bbox = shp['boudingbox']
            rect = self.rect()

            ratiox = rect.width()/(bbox['xmax']-bbox['xmin'])
            ratioy = rect.height()/(bbox['ymax']-bbox['ymin'])

            self.ratio = min(ratiox,ratioy)*0.9

            self.orig.setX((bbox['xmax']+bbox['xmin'])*self.ratio/2 - self.width()/2)
            self.orig.setY((bbox['ymax']+bbox['ymin'])*self.ratio/2 - self.height()/2)

        self.shps.append(shp)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        for shp in self.shps:
            painter.setPen(QPen( shp['color'] ))
            draw_shp(painter, self.rect(), shp, self.orig, self.ratio)

    # def closeEvent(self, event):
    #     if QMessageBox.Yes == QMessageBox.question(self, "SHPViewer", "确认退出?",
    #                                                QMessageBox.Yes | QMessageBox.No,
    #                                                QMessageBox.Yes):
    #         self.accept()
    #     else:
    #         event.ignore()

    def mousePressEvent(self, event):
        pt = event.pos()
        self.leftMouseDown = True
        self.mouseDownPos = pt

    def mouseReleaseEvent(self, event):
        self.leftMouseDown = False
        
    def mouseMoveEvent(self, event):
        if not self.leftMouseDown:
            return

        pt = event.pos()
        moved = pt - self.mouseDownPos
        self.mouseDownPos = pt
        
        # reverse y
        moved.setY(-moved.y())
        self.orig -= moved

        self.repaint()

    def wheelEvent(self, event):
        mousepos = event.pos()
        rect = self.rect()
        delta = event.angleDelta().y()

        mapx = (mousepos.x() + self.orig.x())/self.ratio
        mapy = (rect.bottom() - mousepos.y() + self.orig.y() )/self.ratio

        if delta > 0:
            self.ratio *= 1.5     
        elif delta < 0:
            self.ratio *= 0.6
            if self.ratio < 1:
                self.ratio = 1.0

        mapx *= self.ratio
        mapy *= self.ratio

        self.orig.setX(mapx - mousepos.x())
        self.orig.setY(mapy - rect.bottom() + mousepos.y())

        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_dlg = MainDlg()
    main_dlg.show()
    sys.exit(app.exec_())
