from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np

def MBox(txt,mode=None):
    msg = QtWidgets.QMessageBox()
    if mode == 1:
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Hint")
    elif mode == 2:
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("Warning")
    elif mode == 3:
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Warning")
    elif mode == 4:
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setWindowTitle("Hint")
    msg.move(880,500)
    msg.setText(txt)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    retval = msg.exec_()

def ArraytoText(arr1, arr2):
    result = ""
    for i in range(len(arr1)):
        result += f"({arr1[i]},{arr2[i]}), "
    result = result[:-2]
    return result

def getLength(vertices):
    min_x = min(vertices, key=lambda p: p[0])[0]
    max_x = max(vertices, key=lambda p: p[0])[0]
    min_y = min(vertices, key=lambda p: p[1])[1]
    max_y = max(vertices, key=lambda p: p[1])[1]

    width = max_x - min_x
    height = max_y - min_y

    return [min_x, max_x, min_y, max_y,width, height]

def img2pyqt(frame,label):
    frame = np.transpose(frame, (1, 0))
    frame = frame * 256
    frame = np.round(frame).astype('uint8')
    temp = np.expand_dims(frame, axis=2)
    #print(temp.shape)
    temp = np.repeat(temp, 3, axis=2)
    temp = temp.copy()
    temp = QtGui.QImage(temp, temp.shape[1], temp.shape[0], temp.shape[1]*3, QtGui.QImage.Format_RGB888)
    return QtGui.QPixmap.fromImage(temp).scaled(label.width(), label.height())
    # aspectRatioMode= QtCore.Qt.KeepAspectRatio


