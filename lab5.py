import sys
from PyQt5 import QtWidgets
from PyQt5 import uic
from time import sleep
from random import randint
from threading import Event, Thread
import queue

def passData(mainWin,out):
    while True: 
        mainWin.my_event.wait()
        mainWin.my_event.clear()
        print(mainWin.title)
        if mainWin.queue.empty() and mainWin.marker.isVisible():
            print("send and dis marker",len(mainWin.input.text()))
            q.put([len(mainWin.input.text()),mainWin.daCombo.currentText(),mainWin.saCombo.currentText(),0,mainWin.is_monitor,mainWin.input.text()])
            sleep(5)
            mainWin.marker.setVisible(len(mainWin.input.text()))
        else:
            print("recieving")
            if mainWin.queue.empty() == False:
                msg = q.get()
                print(msg)
                if msg[0] == 0:
                    mainWin.marker.setVisible(1)
                    q.put([len(mainWin.input.text()),mainWin.daCombo.currentText(),mainWin.saCombo.currentText(),0,mainWin.is_monitor,mainWin.input.text()])
                    sleep(5)     
                    mainWin.marker.setVisible(len(mainWin.input.text()))
                elif msg[1] == mainWin.saCombo.currentText():
                    print(msg[5])
                    out.insertPlainText('\n')
                    out.insertPlainText(msg[5])
                    q.put([msg[0],msg[1],msg[2],1,mainWin.is_monitor,msg[5]])
                elif msg[2] == mainWin.saCombo.currentText() and msg[3] == 1:
                    mainWin.input.setText("")
                    q.put([len(mainWin.input.text()),mainWin.daCombo.currentText(),mainWin.saCombo.currentText(),0,mainWin.is_monitor,mainWin.input.text()])
                    sleep(5)
                    mainWin.marker.setVisible(len(mainWin.input.text()))
                else:
                    q.put(msg)
        mainWin.next_event.set()
class MainWindow(QtWidgets.QMainWindow):


    def __init__(self,title,is_monitor, queue, my_event,next_event):
        self.addresses = ['1b', '10b', '100b']
        self.title= title
        self.is_monitor = is_monitor
        self.my_event = my_event
        self.next_event = next_event
        self.queue  = queue
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi("mainwindow.ui",self)
        self.saCombo.addItems(self.addresses)
        self.daCombo.addItems(self.addresses)
        self.startButton.setVisible(self.is_monitor)
        self.startButton.clicked.connect(self.Start)
        #self.sendButton.clicked.connect(self.sendArray)
        self.input.textEdited.connect(self.inputChanged)
        self.setWindowTitle(self.title)
        self.marker.setVisible(self.is_monitor)
        self.thread = Thread(target=passData, args=(self,self.output))
        self.thread.start()  
        self.show()
    def Start(self):
        self.startButton.setVisible(0)
        self.my_event.set()
    def inputChanged(self,data):
        if len(data) > 1:
            self.input.setText(self.input.text()[1:])
if __name__ == "__main__":
    q = queue.Queue()
    event0 = Event()
    event1 = Event()
    event2 = Event()
    app = QtWidgets.QApplication(sys.argv)
    ex0 = MainWindow("Monitor",1,q, event0, event1)
    ex1 = MainWindow("Station A",0,q,event1,event2)
    ex2 = MainWindow("Station B",0,q, event2,event0)
    a = app.exec_()
    sys.exit(a)
                    