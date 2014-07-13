import Queue #, Empty
from threading import Thread
import serial
    
def _listMsgs(q):    
    try:
        while True:
            yield q.get_nowait()
    except Queue.Empty:
        raise StopIteration
                    
class mySerial():
    def __init__(self, parent=None):
        self.ser = serial.Serial("COM6", 115200)
        self.fifo = Queue.Queue()
        self._on = True
        self.th = Thread(target=self._th_read)
        self.th.start()
           
    def _th_read(self):
        while self._on:
            msg = self.ser.readline().rstrip('\n')
            self.fifo.put(msg)
#            print(msg)
    
    def readMsg(self):
        return list(_listMsgs(self.fifo))
    
    def writeMsg(self, msg):
        self.ser.write(msg + '\r')

    def stop(self):
        self.ser.close()
        self._on = False
        self.th.join()
        print("Outing!!!")
        