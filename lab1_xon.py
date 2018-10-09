import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit,QTextEdit
from PyQt5.QtWidgets import QPushButton,QComboBox,QRadioButton
from PyQt5.QtCore import QSize 
import serial
from serial import SerialException
import threading


def read_from_port(widget, label,serial_com,xonLabel, sendButton, addressMyDist):
	recieve_counter = 0
	while True:
		if serial_com.is_open and serial_com.port != 'COM':
                        try:
                            output = serial_com.read(serial_com.inWaiting())
                            if len(output) > 0 :
                                if  serial_com.xonxoff == False:
                                        xonLabel.setText("")
                                        for i in output:
                                            print(i)
                                        if output != b'@' and output != b'#' and chr(output[0]) == "a" and addressMyDist[0] == chr(output[1]) and addressMyDist[1] ==  chr(output[2]):
                                            recieve_counter += len(output)
                                            output = bytearray(output)
                                            print("output[3]", output[3])
                                            range_number = list(range(4, output[3] + 4))
                                            for i in range_number:
                                                if output[i] == 27:
                                                    #output = output[:i] + output[i+1:]
                                                    output[i+1] -= 8
                                                    #range_number.pop()
                                                else:
                                                    widget.insertPlainText(chr(output[i]))
                                                
                                            widget.insertPlainText("\n")
                                            label.setText("R: " + str(recieve_counter))
                                            xonLabel.setText("")
                                        elif output == b'@':
                                            xonLabel.setText("XOFF from reciever")
                                            sendButton.setEnabled(False)
                                        elif output == b'#':
                                            sendButton.setEnabled(True)
                                            xonLabel.setText("XON from reciever")
                                   

                        except Exception as e:
                            print("have exception")
                            print(e)
			

   

class MainWindow(QMainWindow):
    def __init__(self, serial_com):

        QMainWindow.__init__(self)	
        self.setMaximumSize(QSize(400, 600))  
        self.setMinimumSize(QSize(400, 600))      
        self.setWindowTitle("COM")
        
        self.addressMyDist = ["1", "0"]
        self.transmit_counter = 0
        self.serial_com = serial_com

        self.fromLabel = QLabel(self)
        self.fromLabel.setText('From:')
        self.fromLabel.move(20, 400)

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
        self.recieveLabel.move(20, 300)

        self.transmitLabel = QLabel(self)
        self.transmitLabel.setText("T: 0")
        self.transmitLabel.move(20, 340)

        self.setDestAddressLabel = QLabel(self)
        self.setDestAddressLabel.setText("Destination address: ")
        self.setDestAddressLabel.move (60,300)
        
        self.setDestAddress = QComboBox(self)
        self.setDestAddress.move(200, 300)
        self.setDestAddress.addItems(["0","1","2", "3", "4", "5", "6", "7", "8", "9", "A", "B"])
        self.setDestAddress.currentIndexChanged.connect(self.selectionChangeDestAddress)

        self.setMyAddressLabel = QLabel(self)
        self.setMyAddressLabel.setText("My address: ")
        self.setMyAddressLabel.move (60,340)
        
        self.setMyAddress = QComboBox(self)
        self.setMyAddress.move(200, 340)
        self.setMyAddress.addItems(["1","0","2", "3", "4", "5", "6", "7", "8", "9", "A", "B"])
        self.setMyAddress.currentIndexChanged.connect(self.selectionChangeMyAddress)
                
        self.errorLabel = QLabel(self)
        self.errorLabel.setText("")
        self.errorLabel.move(20, 460)
        self.errorLabel.setStyleSheet('color: red')

        self.xonLabel = QLabel(self)
        self.xonLabel.setText("XOFF on reciever")
        self.xonLabel.move(150, 370)
        
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

        self.debugState = QTextEdit(self)
        self.debugState.move(20, 490)
        self.debugState.setReadOnly(True)
        self.debugState.resize(355, 70)
        
    def clickMethod(self):
        if self.serial_com.is_open:
                self.xonLabel.setText("")
                self.errorLabel.setText("")
                if len(self.line.toPlainText()) < 255:
                        transmit_data = bytearray(self.line.toPlainText(), 'utf-8')
                        range_number = list(range(len(transmit_data)))
                        for i in range_number:
                            if transmit_data[i] == ord('#') or transmit_data[i] == ord('@'):
                                transmit_data.insert(i, 27)
                                transmit_data[i+1] += 8
                                range_number.insert(len(range_number), len(range_number))
                                
                        self.line.clear()                        
                        self.transmit_counter += len(transmit_data) + 6 
                        self.transmitLabel.setText("T: " + str(self.transmit_counter))
                        send_total = bytearray("a", 'utf-8') + bytearray(self.addressMyDist[1], 'utf-8') + bytearray(self.addressMyDist[0], 'utf-8') + bytearray([len(transmit_data)]) + transmit_data + bytearray(self.addressMyDist[0], 'utf-8') + bytearray([255])
                        self.serial_com.write(send_total)
                        for i in send_total:
                               self.debugState.insertPlainText(str(hex(i))) 
                        self.debugState.insertPlainText("\n") 
                        #self.line.clear()
                else:
                        self.errorLabel.setText("Max size for sending")
        else:
                self.errorLabel.setText("Port is closed")

    def xonEnable(self):
        self.errorLabel.setText("")
        if self.serial_com.is_open and self.serial_com.port != 'COM' and self.xon.text() == 'send XON':
            self.serial_com.write(b"#")
            self.xon.setText("send XOFF")
        elif self.serial_com.is_open and self.serial_com.port != 'COM' and self.xon.text() == 'send XOFF':
            self.serial_com.write(b"@")
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

    def selectionChangeDestAddress(self):
            if self.addressMyDist[0] != self.setDestAddress.currentText():
                    self.errorLabel.setText("")
                    self.addressMyDist[1] = self.setDestAddress.currentText()
            else:
                    self.errorLabel.setText("Cant't set address")

    def selectionChangeMyAddress(self):
            if self.addressMyDist[1] != self.setMyAddress.currentText():
                    self.errorLabel.setText("")
                    self.addressMyDist[0] = self.setMyAddress.currentText()
            else:
                    self.errorLabel.setText("Can't set address")
            return
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


    thread = threading.Thread(target=read_from_port, args = (mainWin.output,mainWin.recieveLabel, serial_com, mainWin.xonLabel, mainWin.pybutton,
                                                             mainWin.addressMyDist))    
    mainWin.show()
    thread.start()
  
    sys.exit( app.exec_() ) 
