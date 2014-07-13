import sys

from PyQt4.QtCore import QTimer, SIGNAL
from PyQt4.QtGui import QApplication, QDialog, QHBoxLayout, QVBoxLayout, QTabWidget, \
                            QWidget, QCheckBox, QLabel, QTextBrowser
import mySerial

SLOT = 5.0    # width of graph
REFRESH = 0.1 # graph refresh time interval 

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AppForm(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('myGUI')
        self.resize(600, 400)
        self.tNow = 0
        self.data = [[], [], [], []]
        self.create_main_frame()
        self.ser = mySerial.mySerial()
        print('Start!!!\r\n')
            
    def closeEvent(self, event):
        self.ser.stop()
            
    def on_chkLED(self):
        if self.chkLED.checkState():
            s = "Button ON"
            self.timer.start(1000 * REFRESH) 
            self.ser.writeMsg("a1")
        else:
            s = 'Button OFF'
            self.timer.stop()
            self.ser.writeMsg("a0")
        self.labButton.setText(s)
     
    def timer_tick(self):
        l = self.ser.readMsg()
        for i in l:
#            self.memo.append(i)
            d = i.split()
            if d[0] == 't':
                self.data[0] += [int(d[1])/1000.0]
                self.data[1] += [int(d[2])]
                self.data[2] += [int(d[3])]
                self.data[3] += [int(d[4])]
        if len(l):
            self.tNow = self.data[0][-1]
        else:
            self.tNow += REFRESH
        n = 0
        for i in self.data[0]:
            if i > self.tNow - SLOT:
                break
            else:
                n += 1
        self.data[0] = self.data[0][n:]
        self.data[1] = self.data[1][n:]
        self.data[2] = self.data[2][n:]
        self.data[3] = self.data[3][n:]
        self.draw_graph()
    
    def draw_graph(self):
        self.axes.clear()
        self.axes.grid(True)
        self.axes.set_title("ADXL345")
        self.axes.set_xlim([self.tNow-SLOT, self.tNow])
        self.axes.set_xlabel("time (s)")
        self.axes.set_ylim([-600, 600])
        self.axes.set_ylabel("Aceleration (G)")
        self.axes.plot(self.data[0], self.data[1])
        self.axes.plot(self.data[0], self.data[2])
        self.axes.plot(self.data[0], self.data[3])
        self.canvas.draw()
                       
    def create_main_frame(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_tick)

        self.horizontalLayout = QHBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "t1")
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "t2")
        self.horizontalLayout.addWidget(self.tabs)
                
        self.chkLED = QCheckBox("LED", self.tab1)
        self.chkLED.setChecked(False)
        self.connect(self.chkLED, SIGNAL('stateChanged(int)'), self.on_chkLED)
                
        self.labButton = QLabel("Button OFF", self.tab1)
        
        self.memo = QTextBrowser(self.tab1)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.chkLED)
        vbox.addWidget(self.labButton)
        vbox.addWidget(self.memo)
        self.tab1.setLayout(vbox)
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        
        self.draw_graph()
        
        hbox = QVBoxLayout()
        hbox.addWidget(self.canvas)
        self.tab2.setLayout(hbox)        

        self.tabs.setCurrentIndex(1)
                
def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    