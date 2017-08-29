import sys
import os
import serial
import threading
import binascii 
import serial.tools.list_ports
from PyQt5 import uic,QtGui
from PyQt5.QtWidgets import QApplication , QMainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

qtCreatorFile = resource_path("SerialGUI.ui")
# qtCreatorFile = "./SerialGUI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QMainWindow, Ui_MainWindow):
    ser = serial.Serial()
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)

    def port_open(self):
        self.ser.port = self.comPort.currentText()
        self.ser.baudrate = int(self.comBaud.currentText())
        self.ser.bytesize = int(self.comByteSize.currentText()) 
        self.ser.stopbits = int(self.comStopBit.currentText())
        self.ser.parity = self.comParity.currentText()
        self.ser.timeout = 0.5
        self.ser.open()
        if(self.ser.isOpen()):
            self.pushButtonOpen.setEnabled(False)
            self.labelShowState.setText("打开成功")
            self.t1 = threading.Thread(target=self.receive_data)
            self.t1.setDaemon(True)
            self.t1.start()
        else:
            self.labelShowState.setText("打开失败")

    def port_close(self):
        self.ser.close()
        if(self.ser.isOpen()):
            self.labelShowState.setText("关闭失败")
        else:
            self.pushButtonOpen.setEnabled(True)
            self.labelShowState.setText("关闭成功")

    def send_data(self):
        if(self.ser.isOpen()):
            if(self.checkBoxSendHex.isChecked()):
                 self.ser.write(binascii.a2b_hex(self.sendTextBrowser.toPlainText()))
            else:
                self.ser.write(self.sendTextBrowser.toPlainText().encode('utf-8'))
            self.labelShowState.setText("发送成功")
    #       self.ser.flushOutput()
        else:
            self.labelShowState.setText("发送失败")

    def receive_data(self):
        print("The receive_data threading is start")
        res_data = '' 
        num = 0
        while (self.ser.isOpen()):
            size = self.ser.inWaiting()
            if size:
                res_data = self.ser.readall()
                if(self.checkBoxShowHex.isChecked()):
                    self.receiveTextBrowser.append(binascii.b2a_hex(res_data).decode())
                else:
                    # self.receiveTextBrowser.append(res_data.decode())
                    self.receiveTextBrowser.insertPlainText(res_data.decode())
                self.receiveTextBrowser.moveCursor(QtGui.QTextCursor.End)
                #self.ser.flushInput()               
                num +=1
                self.labelShowState.setText("接收："+str(num))

    def clean_data(self):
        self.receiveTextBrowser.setText("")
        self.labelShowState.setText("接收清空")

    def port_cheak(self):
        Com_List=[]
        port_list = list(serial.tools.list_ports.comports())
        self.comPort.clear()
        for port in port_list:
            Com_List.append(port[0])
            self.comPort.addItem(port[0])
        if(len(Com_List) == 0):
            self.labelShowState.setText("没串口")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
