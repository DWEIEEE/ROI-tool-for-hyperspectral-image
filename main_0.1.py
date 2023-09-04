from PyQt5 import QtWidgets, QtCore, QtGui
from GUI import Ui_MainWindow
from tool import MBox, ArraytoText, img2pyqt, getLength
import qtawesome as qta
import numpy as np
import scipy.io
import h5py as h5
import sys
import os
import cv2

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setIcon()
        self.setInfo(pre=True)
        self.ui.pushButton_3.clicked.connect(lambda: self.add_folder('in'))
        self.ui.pushButton_10.clicked.connect(lambda: self.add_folder('out'))
        self.ui.pushButton_4.clicked.connect(self.left)
        self.ui.pushButton_5.clicked.connect(self.right)
        self.ui.pushButton_6.clicked.connect(self.Rectangle)
        self.ui.pushButton_7.clicked.connect(self.Polygon)
        self.ui.pushButton_8.clicked.connect(self.Delete)
        self.ui.comboBox.activated.connect(self.bandChange)
        self.ui.checkBox.stateChanged.connect(self.saveMAT)
        self.ui.checkBox_2.stateChanged.connect(self.saveH5)
        self.ui.checkBox_3.stateChanged.connect(self.fixed_ROI)
        self.ui.checkBox_4.stateChanged.connect(self.baseMAP)
        self.ui.spinBox.valueChanged.connect(self.spinChange1)
        self.ui.spinBox_2.valueChanged.connect(self.spinChange2)
        self.ui.spinBox_3.valueChanged.connect(self.spinChange3)
        self.ui.spinBox_4.valueChanged.connect(self.spinChange4)
        self.ui.pushButton.clicked.connect(self.apply)
        self.ui.pushButton_2.clicked.connect(self.cancel)
        self.checkin = self.checkout = self.H5 = self.MAT = False
        self.ui.checkBox_3.setEnabled(False) #unable

    def Rectangle(self):
        self.ui.label.mode = 'Rectangle'
        self.ui.label.update()
        self.ui.pushButton_6.setChecked(True)
        self.ui.pushButton_7.setChecked(False)
        
    def Polygon(self):
        self.ui.label.mode = 'Polygon'
        self.ui.label.update()
        self.ui.pushButton_6.setChecked(False)
        self.ui.pushButton_7.setChecked(True)


    def add_folder(self,mode):
        if mode == 'in':
            self.checkin = False
            self.folderPath = QtWidgets.QFileDialog.getExistingDirectory()
            if self.folderPath == '':
                return
            self.ui.lineEdit.setText(self.folderPath)
            self.checkfolder()
        elif mode == 'out':
            self.checkout = False
            self.outPath = QtWidgets.QFileDialog.getExistingDirectory()
            if self.outPath == '':
                return
            self.ui.lineEdit_2.setText(self.outPath)
            self.checkout = True
        else:
            print('select Folder Error ...')
            return

    def checkfolder(self):
        notice = False
        self.filenames = os.listdir(self.folderPath)
        self.file_count = len(self.filenames)
        if self.file_count == 0:
            MBox('No .mat files found in the folder.',3)
            return
        for index, file in enumerate(self.filenames):
            _, extension = os.path.splitext(file)
            extension = extension.lower()
            if extension != ".mat":
                self.file_count -= 1
                del self.filenames[index]
                notice = True
        if self.file_count == 0:
            MBox('No .mat files found in the folder.',3)
            return
        if notice == True:
            MBox('Notice, Only .mat files supported in folder,\nNon-.mat files filtered out from the folder',1)
        self.checkin = True
        self.inNum = self.bandNum = 1
        self.setSec()

    def setSec(self):
        self.ui.label_5.setText(f"( {self.inNum} / {self.file_count} )")
        self.ui.label_4.setText(f"{self.filenames[self.inNum-1]}")
        self.load_file()
        self.info_1 = f"<b>{self.info_t1}</b>  {self.file_count} pcs"
        self.info_2 = f"<b>{self.info_t2}</b>  {self.w} * {self.h} * {self.band}"
        self.info_3 = f"<b>{self.info_t3}</b>  {round(self.maxValue,5)}  ({self.maxcol},{self.maxrow})"
        self.info_4 = f"<b>{self.info_t4}</b>  {round(self.minValue,5)}  ({self.mincol},{self.minrow})"
        self.info_5 = f"<b>{self.info_t5}</b>  {self.nan}"
        self.info_6 = f"<b>{self.info_t6}</b>  {self.geNum} item"
        self.setInfo()
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems([str(x) for x in range(1, (self.band+1))])

        try:
            self.ui.comboBox.setCurrentIndex(self.bandNum-1)
        except:
            self.ui.comboBox.setCurrentIndex(self.band-1)

        self.ui.pushButton_6.setEnabled(True)
        self.ui.pushButton_7.setEnabled(True)
        self.ui.pushButton_8.setEnabled(True)
        #self.ui.pushButton_9.setEnabled(True)
        if self.ui.pushButton_6.isChecked() == False and self.ui.pushButton_7.isChecked() == False:
            self.ui.pushButton_6.setChecked(True)
            self.ui.pushButton_7.setChecked(False)
            self.ui.label.mode = 'Rectangle'

    def load_file(self):
        temp = h5.File(os.path.join(self.folderPath,self.filenames[self.inNum-1]),'r')
        self.img = np.array(temp[list(temp.keys())[0]])
        self.band = self.img.shape[0]
        self.w = self.img.shape[1]
        self.h = self.img.shape[2]
        self.maxValue = np.nanmax(self.img[self.bandNum-1])
        self.minValue = np.nanmin(self.img[self.bandNum-1])
        max_index = np.nanargmax(self.img[self.bandNum-1])
        self.maxrow, self.maxcol = np.unravel_index(max_index, self.img[self.bandNum-1].shape)
        min_index = np.nanargmin(self.img[self.bandNum-1])
        self.minrow, self.mincol = np.unravel_index(min_index, self.img[self.bandNum-1].shape)
        temp_nan = np.where(np.isnan(self.img[self.bandNum-1]))
        try:
            self.nan = ArraytoText(temp_nan[0],temp_nan[1])
        except:
            self.nan = "None"
        self.geNum = 0
        self.ui.label.setPixmap(img2pyqt(self.img[self.bandNum-1],self.ui.label))

    def apply(self):
        if self.checkin != True:
            MBox('Please load your data first.',3)
            return
        if self.checkout != True:
            MBox('Please choose your output\'s folder.',3)
            return
        if len(self.ui.label.polygons) == 0 and len(self.ui.label.rectangles) == 0:
            MBox('You don\'t draw any ROI, please re-check.',3)
            return
        if self.MAT == False and self.H5 == False:
            MBox('Please choose any type output format.',3)
            return
        self.output_perpare()
        self.geNum = 0

        for polygon in self.ui.label.polygons:
            vertices = []
            for i in range(polygon.size()):
                point = polygon.point(i)
                vertices.append((point.x(), point.y()))
            vertices = [(x // 2, y // 2) for x, y in vertices]
            print(vertices)
            vertices = np.array(vertices)

            newimg = self.roimg.copy()
            mask = np.zeros(self.roimg[:,:,0].shape, dtype=np.uint8)
            cv2.fillPoly(mask,[vertices],1)
            for i in range(self.band):
                newimg[:,:,i] = newimg[:,:,i] * mask
            if self.ui.checkBox_4.isChecked():
                vertical_info = getLength(vertices)
                back = np.zeros([self.spin_value3,self.spin_value4,self.band], dtype=np.float64)
                offset_x = (self.spin_value3 - vertical_info[4]) // 2
                offset_y = (self.spin_value4 - vertical_info[5]) // 2
                back[offset_y:offset_y+vertical_info[5], offset_x:offset_x+vertical_info[4], :] = newimg[vertical_info[2]:vertical_info[3],vertical_info[0]:vertical_info[1],:]
                newimg = self.checknan(back)
            else:
                newimg = self.checknan(newimg)
            self.geNum += 1
            if self.MAT == True:
                scipy.io.savemat(f'{self.outPath}/mat/{self.filenames[self.inNum-1][:-10]}Leaf{self.geNum}.mat', {'data': newimg})
            if self.H5 == True:
                filename = f'{self.outPath}/h5/{self.filenames[self.inNum-1][:-10]}Leaf{self.geNum}.h5'
                try:
                    with h5.File(filename, 'w') as hf:
                        hf.create_dataset('data', data=newimg)
                except:
                    os.remove(filename)
                    with h5.File(filename, 'w') as hf:
                        hf.create_dataset('data', data=newimg)

        for rectangle in self.ui.label.rectangles:
            x1 = int(rectangle.x()//2)
            y1 = int(rectangle.y()//2)
            w = int(rectangle.width()//2)
            h = int(rectangle.height()//2)
            x2 = x1 + w
            y2 = y1 + h
            roi = self.roimg[y1:y2, x1:x2, :]
            if self.ui.checkBox_4.isChecked():
                back = np.zeros([self.spin_value3,self.spin_value4,self.band], dtype=np.float64)
                offset_x = (self.spin_value3 - w) // 2
                offset_y = (self.spin_value4 - h) // 2
                back[offset_y:offset_y+h, offset_x:offset_x+w, :] = roi
                back = self.checknan(back)
            else:
                back = self.checknan(roi)
            self.geNum += 1
            if self.MAT == True:
                scipy.io.savemat(f'{self.outPath}/mat/{self.filenames[self.inNum-1][:-10]}Leaf{self.geNum}.mat', {'data': back})
            if self.H5 == True:
                filename = f'{self.outPath}/h5/{self.filenames[self.inNum-1][:-10]}Leaf{self.geNum}.h5'
                try:
                    with h5.File(filename, 'w') as hf:
                        hf.create_dataset('data', data=back)
                except:
                    os.remove(filename)
                    with h5.File(filename, 'w') as hf:
                        hf.create_dataset('data', data=back)

        self.info_6 = f"<b>{self.info_t6}</b>  {self.geNum} item"
        MBox('Successful',1)
        self.setInfo()

    def output_perpare(self):
        if self.MAT ==  True:
            if not os.path.isdir(os.path.join(self.outPath,'mat')):
                os.mkdir(os.path.join(self.outPath,'mat'))
        if self.H5 ==  True:
            if not os.path.isdir(os.path.join(self.outPath,'h5')):
                os.mkdir(os.path.join(self.outPath,'h5'))
        self.roimg = self.img.transpose(2, 1, 0)

    def checknan(self,img):
        for i in range(self.band):
            temp_nan = np.where(np.isnan(img[:,:,i]))
            for k in range(len(temp_nan[0])):
                img[int(temp_nan[0][k]), int(temp_nan[1][k]),i] = 0
        return img

    def Delete(self):
        print('delete')
        try:
            if self.ui.label.mode == 'Polygon':
                self.ui.label.polygons.pop()
                self.ui.label.polygontypelist.pop()
                self.ui.label.update()

            if self.ui.label.mode == 'Rectangle':
                self.ui.label.rectangles.pop()
                self.ui.label.update()
        except:
            pass

    def DeleteALL(self):
        try:
            self.ui.label.polygons.clear()
            self.ui.label.polygontypelist.clear()
            self.ui.label.update()
        except:
            pass
        try:
            self.ui.label.rectangles.clear()
            self.ui.label.update()
        except:
            pass

    def bandChange(self):
        self.bandNum = int(self.ui.comboBox.currentText())
        self.setSec()

    def left(self):
        try:
            if self.inNum == 1:
                return
            self.inNum -= 1
            self.DeleteALL()
            self.setSec()
        except:
            pass

    def right(self):
        try:
            if self.inNum == self.file_count:
                return
            self.inNum += 1
            self.DeleteALL()
            self.setSec()
        except:
            pass

    def saveMAT(self):
        if self.ui.checkBox.isChecked():
            self.MAT = True
            return
        self.MAT = False

    def saveH5(self):
        if self.ui.checkBox_2.isChecked():
            self.H5 = True
            return
        self.H5 = False

    def fixed_ROI(self):
        if self.ui.checkBox_3.isChecked():
            self.ui.spinBox.setEnabled(True)
            self.ui.spinBox_2.setEnabled(True)
            return
        self.ui.spinBox.setEnabled(False)
        self.ui.spinBox_2.setEnabled(False)

    def baseMAP(self):
        if self.ui.checkBox_4.isChecked():
            self.ui.spinBox_3.setEnabled(True)
            self.ui.spinBox_4.setEnabled(True)
            return
        self.ui.spinBox_3.setEnabled(False)
        self.ui.spinBox_4.setEnabled(False)

    def spinChange1(self):
        self.spin_value1 = self.ui.spinBox.value()

    def spinChange2(self):
        self.spin_value2 = self.ui.spinBox_2.value()

    def spinChange3(self):
        self.spin_value3 = self.ui.spinBox_3.value()

    def spinChange4(self):
        self.spin_value4 = self.ui.spinBox_4.value()

    def cancel(self):
        print('Application Exit ... ')
        sys.exit()

    def setInfo(self,pre=False):
        if pre == True:
            self.ui.label_5.setText("( 0 / 0 )")
            self.info_t1 = self.ui.label_8.text()
            self.info_t2 = self.ui.label_9.text()
            self.info_t3 = self.ui.label_10.text()
            self.info_t4 = self.ui.label_11.text()
            self.info_t5 = self.ui.label_12.text()
            self.info_t6 = self.ui.label_13.text()
            self.info_1 = f"<b>{self.info_t1}</b>"
            self.info_2 = f"<b>{self.info_t2}</b>"
            self.info_3 = f"<b>{self.info_t3}</b>"
            self.info_4 = f"<b>{self.info_t4}</b>"
            self.info_5 = f"<b>{self.info_t5}</b>"
            self.info_6 = f"<b>{self.info_t6}</b>"
        self.ui.label_8.setText(self.info_1)
        self.ui.label_9.setText(self.info_2)
        self.ui.label_10.setText(self.info_3)
        self.ui.label_11.setText(self.info_4)
        self.ui.label_12.setText(self.info_5)
        self.ui.label_13.setText(self.info_6)

    def setIcon(self):
        self.ui.spinBox.setRange(0,1920)
        self.ui.spinBox_2.setRange(0,1080)
        self.ui.spinBox_3.setRange(0,1920)
        self.ui.spinBox_4.setRange(0,1080)
        self.spin_value1 = self.spin_value2 = self.spin_value3 = self.spin_value4 = 0
        self.ui.spinBox.setEnabled(False)
        self.ui.spinBox_2.setEnabled(False)
        self.ui.spinBox_3.setEnabled(False)
        self.ui.spinBox_4.setEnabled(False)

        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
        self.ui.pushButton_9.setEnabled(False)

        folder_icon = qta.icon('mdi.folder-outline', color='black')
        poly_icon = qta.icon('mdi.vector-polyline-edit', color='black')
        tangle_icon = qta.icon('mdi.vector-square', color='black')
        delete_icon = qta.icon('mdi.delete-empty-outline', color='black')
        send_icon = qta.icon('mdi.check-box-multiple-outline', color='black')
        left_icon = qta.icon('mdi.arrow-left-thick', color='black')
        right_icon = qta.icon('mdi.arrow-right-thick', color='black')
        self.ui.pushButton_3.setIcon(QtGui.QIcon(folder_icon))
        self.ui.pushButton_3.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_10.setIcon(QtGui.QIcon(folder_icon))
        self.ui.pushButton_10.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_4.setIcon(QtGui.QIcon(left_icon))
        self.ui.pushButton_4.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_5.setIcon(QtGui.QIcon(right_icon))
        self.ui.pushButton_5.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_6.setIcon(QtGui.QIcon(tangle_icon))
        self.ui.pushButton_6.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_6.setCheckable(True)
        self.ui.pushButton_7.setIcon(QtGui.QIcon(poly_icon))
        self.ui.pushButton_7.setIconSize(QtCore.QSize(25,25))
        self.ui.pushButton_7.setCheckable(True)
        self.ui.pushButton_8.setIcon(QtGui.QIcon(delete_icon))
        self.ui.pushButton_8.setIconSize(QtCore.QSize(28,28))
        self.ui.pushButton_9.setIcon(QtGui.QIcon(send_icon))
        self.ui.pushButton_9.setIconSize(QtCore.QSize(25,25))
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())