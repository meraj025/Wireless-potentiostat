
#import random
#import serial
import numpy as np
import os,time,datetime
import sys
from PyQt4 import QtGui, QtCore
import IITB_rc
import struct
import pygatt
#import logging
#import time
from binascii import hexlify
from PIL import Image
import pyqtgraph as pg
#import pyqtgraph.exporters


import matplotlib.pyplot as plt

#from PyQt4.QtCore import QThread

#pyrcc4 -o IITB_rc.py IITB.qrc

#modify LegendItem.py line 122 and 123
#        p.setPen(fn.mkPen(0,0,0,255))
#        p.setBrush(fn.mkBrush(0,0,0,0))

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

#####################  UI file linker  ####################
from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('gui.ui')
###########################################################



#####################  Main class  ##########################
class Main(QMainWindow,Ui_MainWindow):
    
    def __init__(self,):
        super(Main, self).__init__()
        self.setupUi(self)
#        Fig = self.record_tag.clicked.connect(self.main)
#        self.dyn_plot.plotItem.showGrid(True, True, 1)
#        self.dyn_plot.setRange(xRange=[0,1],yRange=[0,10000], padding=None)

        self.quit_tag.clicked.connect(self.closeIt)
        self.start_tag.clicked.connect(self.start_reading) 
        self.stop_tag.clicked.connect(self.stop_reading) 
        self.lmp_bd_tag.clicked.connect(self.LMP91000_BD) 
        self.configure_tag.clicked.connect(self.configure)

        self.YOUR_DEVICE_NAME = "LMP91000"
        self.YOUR_DEVICE_ADDRESS = "C9:08:54:74:F4:E2"        
        self.ADDRESS_TYPE = pygatt.BLEAddressType.random#.public#pygatt.BLEAddressType.random
        self.adapter = pygatt.BGAPIBackend()
        self.adapter.start()
        self.device = self.adapter.connect(self.YOUR_DEVICE_ADDRESS, address_type=self.ADDRESS_TYPE)  #
        #    print device
#        print self.device.discover_characteristics()
        self.device.subscribe("F0001123-0451-4000-B000-000000000000",callback=self.display_data)
        self.sfreq = 10
        self.rec_time = 10000
        self.update_win_time = 0.5
        self.win_time = 50
        self.nblock = int(self.update_win_time * self.sfreq)
        self.wblock = self.win_time * self.sfreq       
#        print self.nblock
#        print self.wblock
        self.sensor_scale_buf1 = np.zeros(self.wblock)             
        self.sensor_scale_buf2 = np.ones(self.wblock)*.1             
        self.sensor_scale_buf3 = np.ones(self.wblock)*.1             
        self.sensor_scale_buf4 = np.ones(self.wblock)*.1 
            
        self.sensor_buf_time = (np.arange(0,self.wblock))/float(self.sfreq)
        
        self.sensor_scale1 = np.zeros(self.sfreq*self.rec_time)          
        self.sensor_scale2 = np.zeros(self.sfreq*self.rec_time)          
        self.sensor_scale3 = np.zeros(self.sfreq*self.rec_time)          
        self.sensor_scale4 = np.zeros(self.sfreq*self.rec_time)          

        self.scale_time = np.linspace(0,(len(self.sensor_scale1)/self.sfreq),num = len(self.sensor_scale1))                         
        
        self.recv_count = 0
        self.recv_count_plot = 0
        self.connect(self,QtCore.SIGNAL("update"), self.dynamic_plot)
#___________ Define Database creation
        self.ext = str('.txt')
        self.extf=str('.png')
        self.vref = 0
        self.res = 1
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.time_tag.setText(str(0))
#        self.timer.start(1000)



#        sub_name = self.lineEdit.text()
        #______ Check if correct Database path is available, else create
        rootdir = os.path.join(os.getcwd(), str('Database'))
        if not (os.path.exists(rootdir)):
            os.mkdir(rootdir)
#        rootdir = os.path.join(rootdir, str('Resistive_Sensor'))
#        if not (os.path.exists(rootdir)):
#            os.mkdir(rootdir)   
        
        self.folder_path = os.path.join(rootdir,str("Chemical_Sensor"))      
        if not (os.path.exists(self.folder_path)):
            os.mkdir(self.folder_path)        
        
#        self.dyn_plot.addLegend()
#        self.dyn_plot.setWindowTitle('Data plots')
#        self.dyn_plot = pg.LegendItem((0,00), (0,0))  # args are (size, position)
#        legendLabelStyle = {'color': '#FFF', 'size': '12pt', 'bold': True, 'italic': False}
        self.dyn_plot.addLegend(size=(70, 0))
#        self.dyn_plot.addLegend()
#        self.dyn_plot.setText(single_item.text, **legendLabelStyle)
        self.dyn_plot.plot(self.sensor_buf_time,self.sensor_scale_buf1, clear = True, pen='r',name='Amperometry') #A5
        
        self.dyn_plot2.addLegend(size=(70, 0))
        self.dyn_plot2.plot(self.sensor_buf_time,self.sensor_scale_buf2, clear = True, pen='b',name='A0') #A0
        self.dyn_plot2.plot(self.sensor_buf_time,self.sensor_scale_buf3, pen='g',name='A1') #A1
        self.dyn_plot2.plot(self.sensor_buf_time,self.sensor_scale_buf4, pen='k',name='A4') #A4
        
#        for item in self.dyn_plot.items:
#            for single_item in item:
#                if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
#                    single_item.setText(single_item.text, **legendLabelStyle)
#        legend.addItem(p1, "f(x) = x") 



    def updateTime(self):
#        current = QtCore.QDateTime.currentDateTime()#-self.start_time
#        self.timeEdit.setTime(self.start_time.secsTo(current))
#        print time.time()-self.start_time
        self.time_tag.setText(str(int(time.time()-self.start_time)))

    def LMP91000_BD(self):
        img = Image.open('lmp91000.png')
        img.show()




        
    def dynamic_plot(self):

        self.sensor_scale_buf1 = np.roll(self.sensor_scale_buf1,-1*self.nblock)
        self.sensor_scale_buf1[-1*self.nblock:] = self.sensor_scale1[(self.recv_count_plot-self.nblock):self.recv_count_plot]

        self.sensor_scale_buf2 = np.roll(self.sensor_scale_buf2,-1*self.nblock)
        self.sensor_scale_buf2[-1*self.nblock:] = self.sensor_scale2[(self.recv_count_plot-self.nblock):self.recv_count_plot]
        self.sensor_scale_buf3 = np.roll(self.sensor_scale_buf3,-1*self.nblock)
        self.sensor_scale_buf3[-1*self.nblock:] = self.sensor_scale3[(self.recv_count_plot-self.nblock):self.recv_count_plot]
        self.sensor_scale_buf4 = np.roll(self.sensor_scale_buf4,-1*self.nblock)
        self.sensor_scale_buf4[-1*self.nblock:] = self.sensor_scale4[(self.recv_count_plot-self.nblock):self.recv_count_plot]


#        self.dyn_plot.addLegend()
#        vline = self.dyn_plot.addLine(x=0.2, movable=True)
        
        self.dyn_plot.plot(self.sensor_buf_time,(self.sensor_scale_buf1-self.vref)/self.res, clear = True, pen='r')#,name='myPlot') #A5
        self.dyn_plot.setLabel('left','Current','A')
        self.dyn_plot.setLabel('bottom','time','s')
        
        
        self.dyn_plot2.plot(self.sensor_buf_time,(self.sensor_scale_buf2), clear = True, pen='b')#,name='myPlot') #A0
        self.dyn_plot2.plot(self.sensor_buf_time,(self.sensor_scale_buf3), pen='g')#,name='myPlot') #A1
        self.dyn_plot2.plot(self.sensor_buf_time,(self.sensor_scale_buf4), pen='k')#,name='myPlot') #A4
        self.dyn_plot2.setLabel('left','Voltage','V')
        self.dyn_plot2.setLabel('bottom','time','s')
        
                
#        legend = p1.addLegend()

#        time.sleep(1)        
#        app.processEvents()       

        
        
        
        
    def display_data(self,handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """

#        data = int(hexlify(value),16)
#        print data
#        print("Received data: %s" %hexlify(value))
        
        bytes1 = value
        val = struct.unpack('>HHHH', bytes1)
#        print val[0]
        
        
        self.sensor_scale1[self.recv_count] = val[0]*3.3/4096
        
        self.sensor_scale2[self.recv_count] = val[1]*3.3/4096
        self.sensor_scale3[self.recv_count] = val[2]*3.3/4096
        self.sensor_scale4[self.recv_count] = val[3]*3.3/4096


        if (self.recv_count > 0) and (self.recv_count % self.nblock == 0):
            self.recv_count_plot = self.recv_count          
            self.emit(QtCore.SIGNAL("update"))

        self.recv_count = self.recv_count + 1

      

                




    def configure(self):
        
        TIACN = 0        
        
        tia_fb_res = self.tia_fb_res_cb.currentIndex()
#        print tia_fb_res
        rload = self.rload_cb.currentIndex()
#        print rload
        ref_vol_src = self.ref_vol_src_cb.currentIndex()
#        print ref_vol_src
        int_zero = self.int_zero_cb.currentIndex()
#        print int_zero
        bias_pol = self.bias_pol_cb.currentIndex()
#        print bias_pol
        bias = self.bias_cb.currentIndex()
#        print bias
        fet_short = self.fet_short_cb.currentIndex()
#        print fet_short
        mode_op = self.mode_op_cb.currentIndex()
#        print mode_op
        
        if int_zero == 0: 
            self.vref = 0.66
        elif int_zero == 1: 
            self.vref = 1.65
        elif int_zero == 2: 
            self.vref = 2.21
        else: 
            self.vref = 3.3    

        if tia_fb_res == 1: 
            self.res = 2750
        elif tia_fb_res == 2: 
            self.res = 3500
        elif tia_fb_res == 3: 
            self.res = 7000
        elif tia_fb_res == 4: 
            self.res = 14000
        elif tia_fb_res == 5: 
            self.res = 35000
        elif tia_fb_res == 6: 
            self.res = 120000
        elif tia_fb_res == 7: 
            self.res = 350000
        else: 
            self.res = 1    

        if bias_pol == 0: 
            self.res = -self.res
        else: 
            self.res = self.res
        
        
        TIACN_TIA_GAIN = 4*(tia_fb_res)
        TIACN_RLOAD    = rload        

        TIACN = TIACN_TIA_GAIN + TIACN_RLOAD
 
        REFCN_REF_SOURCE = 128*(ref_vol_src)        
        REFCN_INT_Z      = 32*(int_zero)
        REFCN_BIAS_SIGN  = 16*(bias_pol)
        REFCN_BIAS       = bias

        REFCN = REFCN_REF_SOURCE + REFCN_INT_Z + REFCN_BIAS_SIGN + REFCN_BIAS
        
        MODECN_REF_SOURCE = 128*(fet_short)        
        MODECN_INT_Z      = mode_op
      
        MODECN = MODECN_REF_SOURCE + MODECN_INT_Z
        
        self.device.char_write('F0001121-0451-4000-B000-000000000000', bytearray([TIACN,REFCN,MODECN]))

    def start_reading(self):
        self.sensor_scale_buf1 = np.zeros(self.wblock)       

        self.sensor_scale_buf2 = np.zeros(self.wblock)       
        self.sensor_scale_buf3 = np.zeros(self.wblock)       
        self.sensor_scale_buf4 = np.zeros(self.wblock)       
     
        self.sensor_buf_time = (np.arange(0,self.wblock))/float(self.sfreq)
        
        self.sensor_scale1 = np.zeros(self.sfreq*self.rec_time)         
        self.sensor_scale2 = np.zeros(self.sfreq*self.rec_time)         
        self.sensor_scale3 = np.zeros(self.sfreq*self.rec_time)         
        self.sensor_scale4 = np.zeros(self.sfreq*self.rec_time)         

        self.scale_time = np.linspace(0,(len(self.sensor_scale1)/self.sfreq),num = len(self.sensor_scale1))                         
        self.recv_count = 0
        self.recv_count_plot = 0
        self.device.char_write('F0001122-0451-4000-B000-000000000000', bytearray([01]))
        
        
        self.start_time = time.time()
        self.timer.start(1000)



    def stop_reading(self): 
        self.device.char_write('F0001122-0451-4000-B000-000000000000', bytearray([00]))
                        # Taking time-stamp from Desktop for file name
        self.timer.stop()

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('__%Y-%m-%d__%H-%M-%S')

        self.file_name = str('\\') + str("Chemical_Sensor") + str('__')
        self.file_name += str(st)
      
        self.path_raw_1 = self.folder_path + self.file_name + self.ext
        self.path_fig = self.folder_path + self.file_name + self.extf
#        print self.path_fig
        dat = zip(self.scale_time[0:self.recv_count],(self.sensor_scale1[0:self.recv_count]-self.vref)/self.res,self.sensor_scale2[0:self.recv_count],self.sensor_scale3[0:self.recv_count],self.sensor_scale4[0:self.recv_count])#,self.sensor_scale5[0:self.recv_count],self.sensor_scale6[0:self.recv_count])
        np.savetxt(self.path_raw_1,dat,fmt='%.10f')
#        print 'ABCD'
        plt.clf()
        plt.subplot(211)
        
        plt.autoscale(enable=True, axis='both', tight=None)        
        plt.plot(self.scale_time[0:self.recv_count], (self.sensor_scale1[0:self.recv_count]-self.vref)/self.res, label='Channel - 1', color="red")        
        plt.xlabel('Time in Seconds')
        plt.ylabel('Signal value (A)')
        
        plt.title("CSI")
        
        plt.legend()
        plt.show()        
        
        plt.subplot(212)
        plt.autoscale(enable=True, axis='both', tight=None)        
        plt.plot(self.scale_time[0:self.recv_count], self.sensor_scale2[0:self.recv_count], label='A0', color="green")
        plt.plot(self.scale_time[0:self.recv_count], self.sensor_scale3[0:self.recv_count], label='A1', color="black")
        plt.plot(self.scale_time[0:self.recv_count], self.sensor_scale4[0:self.recv_count], label='A4', color="cyan")
#      
        plt.xlabel('Time in Seconds')
        plt.ylabel('Signal value (V)')
        
        
        plt.show()        
        

        plt.grid(True)
        plt.savefig(self.path_fig)  
     
    def closeIt(self):
        self.timer.stop()
        self.adapter.stop()        
        self.close()

       
       
######################  Default  ###########################

if __name__ == '__main__':
    app=QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
#    sys.exit(app.exec_())
############################################################
    

    