from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math

class MyLabel(QLabel):
    def __init__(self, parent=None, mode=None):
        super().__init__(parent)
        self.pen = QPen(Qt.red, 4, Qt.SolidLine)
        self.pen2 = QPen(Qt.green, 4, Qt.SolidLine)
        self.pen3 = QPen(Qt.blue, 4, Qt.SolidLine)
        self.pen4 = QPen(Qt.yellow, 4, Qt.SolidLine)
        self.start_pos = None
        self.end_pos = None
        self.rectstart_pos = QPoint()
        self.rectend_pos = QPoint()
        self.firstclick = True
        self.rectfirstclick = True
        self.linefirstclick = True
        self.linestart_pos = None
        self.lineend_pos = None
        self.lines = [] #list for drawing polygon line
        self.polygons = [] #list for done polygon
        self.rectangles = [] #list for rectangles
        self.linelist = [] #list for line
        self.mode = mode
        self.linetype = 'A to B'
        self.linetypelist = [] #list for each line type
        self.polygontype ='IN' 
        self.polygontypelist = []
        self.isActive = False
        self.start_x =0
        self.start_y= 0
        self.end_x = 0
        self.end_y = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #print("mousePressEvent")
            if self.mode == 'Polygon':
                self.lines.append(event.pos())
                if self.firstclick:
                    self.start_pos = event.pos()
                    self.polygontypelist.append(self.polygontype)
                    self.firstclick = False
                    self.setMouseTracking(True)
                else:
                    self.end_pos = event.pos()
                    self.start_pos = event.pos()
            elif self.mode == 'Rectangle':
                if self.rectfirstclick:
                    self.isActive = True
                    self.rectstart_pos = event.pos()
                    self.rectfirstclick = False
                    self.setMouseTracking(True)
                else:
                    self.rectend_pos = event.pos()
                    self.rectfirstclick = True
                    self.rectangles.append(QtCore.QRect(self.rectstart_pos, self.rectend_pos))
            self.update()

        elif event.button() == Qt.RightButton:
            if self.mode == 'Polygon' and len(self.lines) > 2:
                polygon = QtGui.QPolygon(self.lines)
                self.polygons.append(polygon)
                self.firstclick = True
                self.lines.clear()
            
            elif self.mode =='Rectangle'and not self.rectfirstclick:
                self.rectstart_pos = None
                self.rectfirstclick = True

            self.update()

    def mouseMoveEvent(self, event):
        if self.mode == 'Polygon':
            self.end_pos = event.pos()

        elif self.mode == 'Rectangle':
            self.rectend_pos = event.pos()
    
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        self.painter = QPainter(self)

        if self.mode == 'Polygon':
            self.painter.setPen(self.pen)
            if self.start_pos and self.end_pos and not self.firstclick:
                self.painter.drawLine(self.start_pos, self.end_pos)

        elif self.mode == 'Rectangle':
            self.painter.setPen(self.pen3)
            if not self.rectfirstclick:
                rect = QtCore.QRect(self.rectstart_pos, self.rectend_pos)
                self.painter.drawRect(rect)

        for i in range(1, len(self.lines)):
            self.painter.setPen(self.pen)
            self.painter.drawLine(self.lines[i], self.lines[i - 1])
            
        self.polycount = 1
        for poly in self.polygons:
            first_point = poly.point(0)
            second_point = poly.point(1)
            inout = QtCore.QLineF(first_point, second_point)
            xcenter = 0
            ycenter = 0
            for i in range(len(poly)):
                xcenter = poly.point(i).x() + xcenter
                ycenter = poly.point(i).y() + ycenter
            xcenter = xcenter//len(poly)
            ycenter = ycenter//len(poly)
            movex = (xcenter-first_point.x()-inout.dx()/2)/2
            movey = (ycenter-first_point.y()-inout.dy()/2)/2
            x = first_point.x()+inout.dx()/2 - movex
            y = first_point.y()+inout.dy()/2 - movey
            xcenter = xcenter-movex
            ycenter = ycenter-movey
            self.painter.setPen(self.pen)
            #self.painter.drawLine(xcenter, ycenter,x, y)
            self.painter.drawPolygon(poly)
                
            self.painter.setPen(QColor('#ff00ff'))
            font = QFont('Helvetica',16)
            font.setBold(True)
            self.painter.setFont(font)
            self.painter.drawText(first_point.x(),first_point.y()-5,'pologon'+str(self.polycount))
            self.polycount = self.polycount+1

        self.rectcount = 1
        for rectangle in self.rectangles:
            x1 = rectangle.x()
            y1 = rectangle.y()
            x2 = rectangle.x() + rectangle.width()
            y2 = rectangle.y() + rectangle.height()
            self.painter.setOpacity(1)
            self.painter.setPen(QColor('#ff00ff'))
            font = QFont('Helvetica',16)
            font.setBold(True)
            self.painter.setFont(font)
            self.painter.drawText(min(x1, x2),min(y1, y2) - 5,'rectangle'+str(self.rectcount))
            self.painter.setPen(self.pen3)
            self.painter.setOpacity(0.5)
            brush = QBrush(QColor(0, 0, 255))
            self.painter.setBrush(brush)
            self.painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            self.rectcount = self.rectcount+1
        self.painter.end()

