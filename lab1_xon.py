import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit,QTextEdit
from PyQt5.QtWidgets import QPushButton,QComboBox,QRadioButton
from PyQt5.QtCore import QSize 
import serial
from serial import SerialException
import threading


def read_from_port(widget, label,serial_com,xonLabel, sendButton):
	recieve_counter = 0
	while True:
		if serial_com.is_open and serial_com.port != 'COM':
                        try:
                            output = serial_com.read(serial_com.inWaiting())
                            if len(output) > 0 :
                                if  serial_com.xonxoff == False:
                                        xonLabel.setText("")
                                        if output != b'11h' and output != b'12h':
                                            recieve_counter += len(output)
                                            widget.insertPlainText(str(output))
                                            widget.insertPlainText("\n")
                                            label.setText("R: " + str(recieve_counter))
                                            xonLabel.setText("")
                                        elif output == b'11h':
                                            xonLabel.setText("XOFF from reciever")
                                            sendButton.setEnabled(False)
                                        elif output == b'12h':
                                            sendButton.setEnabled(True)
                                            xonLabel.setText("XON from reciever")
                                   

                        except Exception:
                            print("have exception")
			

   

class MainWindow(QMainWindow):
    def __init__(self, serial_com):

        QMainWindow.__init__(self)	
        self.setMaximumSize(QSize(400, 500))  
        self.setMinimumSize(QSize(400, 500))      
        self.setWindowTitle("COM")

        self.transmit_counter = 0
        self.serial_com = serial_com

        self.fromLabel = QLabel(self)
        self.fromLabel.setText('From:')
        self.fromLabel.move(20, 390)

        self.line = QTextEdit(self)
        self.line.move(20, 0)
        self.line.resize(355, 120)       

        self.pybutton = QPushButton('Send', self)
        self.pybutton.clicked.connect(self.clickMethod)
        self.pybutton.resize(355,32)
        self.pybutton.move(20, 120)
        self.pybutton.setEnabled(False)
     
        self.recieveLabel = QLabel(self)
        self.recieveLabel.setText("R: 0")
        self.recieveLabel.move(20, 320)

        self.transmitLabel = QLabel(self)
        self.transmitLabel.setText("T: 0")
        self.transmitLabel.move(20, 340)

        self.errorLabel = QLabel(self)
        self.errorLabel.setText("")
        self.errorLabel.move(20, 300)

        self.xonLabel = QLabel(self)
        self.xonLabel.setText("XOFF on reciever")
        self.xonLabel.move(200, 370)
        
        self.output = QTextEdit(self)
        self.output.move(20, 200)
        self.output.setReadOnly(True)
        self.output.resize(355, 100)

        self.comInput = QComboBox(self)
        self.comInput.move(20, 430)
        self.comInput.addItems(["---","COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"])
        self.comInput.currentIndexChanged.connect(self.selectionChangeInput)

        self.comState = QComboBox(self)
        self.comState.move(150, 430)
        self.comState.addItems(["Close port","Open port"])
        self.comState.currentIndexChanged.connect(self.selectionChangeState)
	
        self.inboxLabel = QLabel(self)
        self.inboxLabel.setText('All inboxes:')
        self.inboxLabel.move(20, 170)
        
        self.xon =  QPushButton("send XON",self)
        self.xon.clicked.connect(self.xonEnable)
        self.xon.move(20, 370)
 	
    def clickMethod(self):
        if self.serial_com.is_open:
                self.xonLabel.setText("")
                self.errorLabel.setText("")
                self.transmit_counter += len(self.line.toPlainText())
                self.transmitLabel.setText("T: " + str(self.transmit_counter))
                self.serial_com.write(self.line.toPlainText().encode('UTF-8'))
                self.line.clear()
        else:
                self.errorLabel.setText("Port is closed")

    def xonEnable(self):
        self.errorLabel.setText("")
        if self.serial_com.is_open and self.serial_com.port != 'COM' and self.xon.text() == 'send XON':
            self.serial_com.write(b"12h")
            self.xon.setText("send XOFF")
        elif self.serial_com.is_open and self.serial_com.port != 'COM' and self.xon.text() == 'send XOFF':
            self.serial_com.write(b"11h")
            self.xon.setText("send XON")

    def selectionChangeInput(self):
        self.errorLabel.setText("")
        if self.serial_com.is_open:
                self.serial_com.close()
                self.serial_com.port = 'COM'
        if self.comInput.currentText() == '---':
                self.errorLabel.setText("Select port")
                return

        self.serial_com.port = 'COM' + self.comInput.currentText()[3]
        if self.comState.currentText() == "Open port":
                try:
                        self.serial_com.open()
                except SerialException as error:
                        self.errorLabel.setText("Can't open this port")


    def selectionChangeState(self):

        self.errorLabel.setText("")
        if self.comState.currentText() == "Close port" and self.serial_com.is_open:
                self.serial_com.close()
                self.serial_com.port = 'COM'
        elif self.comState.currentText() == "Open port" and self.serial_com.is_open == False:	
                try:
                       self.serial_com.port = 'COM' + self.comInput.currentText()[3]
                       self.serial_com.open()

                except Exception:
                        self.errorLabel.setText("Can't open this port")
                        self.serial_com.port = 'COM'
                except SerialException as error:
                        self.errorLabel.setText("Can't open this port")
        elif self.comState.currentText() == "Open port" and self.serial_com.is_open == True:
                        self.errorLabel.setText("Can't open this port")
	  
if __name__ == "__main__":


    serial_com = serial.Serial()
    serial_com.baudrate = 9600
    serial_com.parity = serial.PARITY_NONE
    serial_com.stopbits = serial.STOPBITS_ONE
    serial_com.xonxoff = False


    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow(serial_com)


    thread = threading.Thread(target=read_from_port, args = (mainWin.output,mainWin.recieveLabel, serial_com, mainWin.xonLabel, mainWin.pybutton))    
    mainWin.show()
    thread.start()
  
    sys.exit( app.exec_() ) 
