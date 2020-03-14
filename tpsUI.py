'''
File Name:  tpsUI.py
Author:     xingming.he
Version:    V0.1
Date:       2019.7.22
Description: function: Create UI, write and read info from TPS
            function: Get device id and reg address from led position
            function: Get led position from device id and reg address
            Interface: TpsControl
'''


#! /usr/bin/python2
#-*- coding:utf-8 -*- 

import wx
import sys
from TpsControl import SerialTPS
from TpsControl import *
from time import sleep
import os

REG_ADDRESS_OFFSET = 0
WIDTH_REG_ADDRESS_START  = 64
PHASE_REG_DEVIDE_POINT = 512

PIXEL_LED_NUMBERS = 32
LED_NUMBER  = 12    #TPS channel,Must be even number
PWM_MAX = 1023
PHASE_START = 0
Unit_ID_List = [DEVICE_ID_000,DEVICE_ID_001,DEVICE_ID_010]
DELAY_TIME = 500
LED_POSITION_MIN_ID_000 = 20
LED_POSITION_MAX_ID_000 = 31
LED_POSITION_MIN_ID_010 = 4
LED_POSITION_MAX_ID_010 = 15
LED_POSITION_ID_001_LEFT = [0,13,14,15,16,29,30,31]


COLOR_START_VALUE = 'FFFFF4'  #16777204 Light
START_VALUE = 16777215
COLOR_END_VALUE = 'FFFF37'    #16777015 Heavy
END_VALUE = 16777015

class Frame(wx.Frame,SerialTPS):
    def __init__(self):
        SerialTPS.__init__(self,"COM4")     #Default port COM4
        #print "Frame__init__"
        wx.Frame.__init__(self, None, -1, 'TPS_UI',size=(700, 600))
        self.SetMaxSize((700,600))
        self.SetMinSize((700,600))
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour((0x28,0x28,0xff))

        image_file = os.path.join(os.getcwd(),'Logo.jpg' )
        logoBitmap = wx.Bitmap(image_file,type=wx.BITMAP_TYPE_ANY)
        logoImage = logoBitmap.ConvertToImage()
        bmp = wx.Bitmap(logoImage.Scale(100,90))
        self.bitmap = wx.StaticBitmap(panel, -1, bmp, pos=(580, 10))

        fontTps = wx.Font(12,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        self.labelInit = wx.StaticText(panel, wx.ID_ANY, "Init:", size=(50, 20),pos=(70,10))
        self.labelInit.SetFont(fontTps)
        self.labelInit.SetForegroundColour('green')
        #self.labelInit.SetBackgroundColour('blue')
        
        self.labelDeviceId = wx.StaticText(panel, wx.ID_ANY, "Deviceid:", size=(50, 20),pos=(70,30))
        self.labelDeviceId.SetFont(fontTps)
        self.labelDeviceId.SetForegroundColour('green')
        #self.labelDeviceId.SetBackgroundColour('blue')
        
        self.labelRegaddr = wx.StaticText(panel, wx.ID_ANY, "Regaddr:", size=(50, 20),pos=(70,50))
        self.labelRegaddr.SetFont(fontTps)
        self.labelRegaddr.SetForegroundColour('green')
        #self.labelRegaddr.SetBackgroundColour('blue')
        
        self.labelData = wx.StaticText(panel, wx.ID_ANY, "Data:", size=(50, 20),pos=(70,70))
        self.labelData.SetFont(fontTps)
        self.labelData.SetForegroundColour('green')
        #self.labelData.SetBackgroundColour('blue')
        

        self.delayCount = 0
        self.delayTime = wx.Timer(self)
        self.timeMsgType = None
        self.Bind(wx.EVT_TIMER, self.mode_display, self.delayTime)
        
        self.InitList=['Write Command of 1 Byte','Write Command of 2 Byte',
                     'Write Command of 3 Byte','Write Command of 4 Byte',
                     'Write Command of 12 Byte','Write Command of 16 Byte',
                     'Write Command of 32 Byte','Read Command of 1 Byte',
                     'Read Command of 2 Byte','Read Command of 3 Byte',
                     'Read Command of 4 Byte','Read Command of 12 Byte',
                     'Read Command of 16 Byte','Read Command of 32 Byte',]
        self.InitDic={'Write Command of 1 Byte':WRITE_CMD_ONE_BYTE,'Write Command of 2 Byte':WRITE_CMD_TWO_BYTE,
                    'Write Command of 3 Byte':WRITE_CMD_THREE_BYTE,'Write Command of 4 Byte':WRITE_CMD_FOUR_BYTE,
                    'Write Command of 12 Byte':WRITE_CMD_TWELVE_BYTE,'Write Command of 16 Byte':WRITE_CMD_SIXTEEN_BYTE,
                    'Write Command of 32 Byte':WRITE_CMD_THIRTYTWO_BYTE,'Read Command of 1 Byte':READ_CMD_ONE_BYTE,
                    'Read Command of 2 Byte':READ_CMD_TWO_BYTE,'Read Command of 3 Byte':READ_CMD_THREE_BYTE,
                    'Read Command of 4 Byte':READ_CMD_FOUR_BYTE,'Read Command of 12 Byte':READ_CMD_TWELVE_BYTE,
                    'Read Command of 16 Byte':READ_CMD_SIXTEEN_BYTE,'Read Command of 32 Byte':READ_CMD_THIRTYTWO_BYTE,}
        
        self.IintBox=wx.ComboBox(panel,-1,value=self.InitList[0],pos=(140,10),size=(150,20),choices=self.InitList,style=wx.CB_SORT)
        self.IintBox.SetEditable(False)
        self.IintBox.Bind(wx.EVT_COMBOBOX,self.select_Iint)

        self.UnitList=['Unit_000','Unit_001','Unit_010']
        self.UnitDic={'Unit_000':DEVICE_ID_000,'Unit_001':DEVICE_ID_001,'Unit_010':DEVICE_ID_010}
        self.DeviceIDBox=wx.ComboBox(panel,-1,value=self.UnitList[0],pos=(140,30),size=(150,20),choices=self.UnitList,style=wx.CB_SORT)
        self.DeviceIDBox.SetEditable(False)
        self.DeviceIDBox.Bind(wx.EVT_COMBOBOX,self.select_DeviceID)

        self.RegaddrList=['MPHASE01L','LPHASE01H','DPHASE01L','SLEWRATE','OVLMT','PARLED','DEFWIDTH02_01','SYSCFG','CMWTAP','PWMTICK','ADCID','SOFTSYNC',
                          'I2CTICK','I2CSLA','I2CRLEN','I2CADR','I2CCTRL','I2CDAT','I2CSTAT','I2CBMON','ADC1'
                          ,'ADC2','FAULTL','FAULTH','CERRCNT','ICID']
        self.RegaddrDic={'MPHASE01L':MPHASE01L_ADDR,'LPHASE01H':LPHASE01H_ADDR,'DPHASE01L':DPHASE01L_ADDR,
                         'SLEWRATE':SLEWRATE_ADDR,'OVLMT':OVLMT_ADDR,'PARLED':PARLED_ADDR,
                         'DEFWIDTH02_01':DEFWIDTH02_01_ADDR,'SYSCFG':SYSCFG_ADDR,'CMWTAP':CMWTAP_ADDR,
                         'PWMTICK':PWMTICK_ADDR,'ADCID':ADCID_ADDR,'SOFTSYNC':SOFTSYNC_ADDR,
                         'I2CTICK':I2CTICK_ADDR,'I2CSLA':I2CSLA_ADDR,'I2CRLEN':I2CRLEN_ADDR,
                         'I2CADR':I2CADR_ADDR,'I2CCTRL':I2CCTRL_ADDR,'I2CDAT':I2CDAT_ADDR,
                         'I2CSTAT':I2CSTAT_ADDR,'I2CBMON':I2CBMON_ADDR,'ADC1':ADC1_ADDR,
                         'ADC2':ADC2_ADDR,'FAULTL':FAULTL_ADDR,'FAULTH':FAULTH_ADDR,
                         'CERRCNT':CERRCNT_ADDR,'ICID':ICID_ADDR}
        self.RegaddrBox=wx.ComboBox(panel,-1,value=self.RegaddrList[0],pos=(140,50),size=(150,20),choices=self.RegaddrList,style=wx.CB_SORT)
        self.RegaddrBox.SetEditable(False)
        self.RegaddrBox.Bind(wx.EVT_COMBOBOX,self.select_Regaddr)
        
        #self.lmmtext = wx.TextCtrl(panel, wx.ID_ANY,pos=(80,10), size =(50,20), value="",style = wx.TE_RICH)
        #self.deviceidtext = wx.TextCtrl(panel, wx.ID_ANY,pos=(80,30), size =(50,20), value="",style = wx.TE_RICH)
        #self.regaddrtext = wx.TextCtrl(panel, wx.ID_ANY,pos=(140,50), size =(50,20), value="",style = wx.TE_RICH)
        self.datatext = wx.TextCtrl(panel, wx.ID_ANY,pos=(140,70), size =(150,40), value="",style=wx.TE_MULTILINE)
        #self.text.Bind(wx.EVT_LEFT_UP, self.leftUP)

        fontPixel = wx.Font(9,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        self.labelOpticMode = wx.StaticText(panel, wx.ID_ANY, "Optic Mode:", size=(80, 20),pos=(300,10))
        self.labelOpticMode.SetFont(fontPixel)
        self.labelOpticMode.SetForegroundColour('yellow')
        
        self.labelAngleLeft = wx.StaticText(panel, wx.ID_ANY, "Angle Left:", size=(80, 20),pos=(300,30))
        self.labelAngleLeft.SetFont(fontPixel)
        self.labelAngleLeft.SetForegroundColour('yellow')
        
        self.labelAngleRight = wx.StaticText(panel, wx.ID_ANY, "Angle Right:", size=(80, 20),pos=(300,50))
        self.labelAngleRight.SetFont(fontPixel)
        self.labelAngleRight.SetForegroundColour('yellow')
        
        self.OpticModeList=['contry_L','town_L','motorway LB_L','high beam_L','motorway HB_L','contry_R','town_R','motorway LB_R','high beam_R','motorway HB_R','test']
        self.OpticModeBox=wx.ComboBox(panel,-1,value=self.OpticModeList[0],pos=(380,10),size=(150,20),choices=self.OpticModeList,style=wx.CB_SORT)
        self.OpticModeBox.SetEditable(False)
        self.OpticModeBox.Bind(wx.EVT_COMBOBOX,self.set_OpticMode)
        self.OpticModeLeftAngleList = ['0','-0.7','-2.3','-3.9','-5.4','-7.0','+2.4','+3.9','+5.5','+7.0','+8.5']
        self.OpticModeLeftBox=wx.ComboBox(panel,-1,value=self.OpticModeLeftAngleList[0],pos=(380,30),size=(150,20),choices=self.OpticModeLeftAngleList,style=wx.CB_SORT)
        self.OpticModeLeftBox.SetEditable(False)
        self.OpticModeRightAngleList = ['0','-1.4','-2.9','-4.5','-6.0','-7.6','+1.7','+3.3','+4.9','+6.4','+7.9',]
        self.OpticModeRightBox=wx.ComboBox(panel,-1,value=self.OpticModeRightAngleList[0],pos=(380,50),size=(150,20),choices=self.OpticModeRightAngleList,style=wx.CB_SORT)
        self.OpticModeRightBox.SetEditable(False)

        self.LeftOrRightList = ['Left','Right']
        fontLRradioBox = wx.Font(12,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        self.LeftOrRightRadioBox = wx.RadioBox(panel,-1,"Left or Right",pos=(380,75),size=(100, 20),choices=self.LeftOrRightList,majorDimension=3,style=wx.RA_SPECIFY_COLS)
        self.LeftOrRightRadioBox.SetFont(fontPixel)
        self.LeftOrRightRadioBox.SetForegroundColour('red')
        
        '''
        self.writeButton = wx.Button(panel, -1, "Write", pos=(400,230),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.write_info, self.writeButton)  
        self.writeButton.SetDefault()

        self.readButton = wx.Button(panel, -1, "Read", pos=(400,250),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.read_info, self.readButton)  
        self.readButton.SetDefault()
        '''

        self.initButton = wx.Button(panel, -1, "Init", pos=(580,210),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.init_all, self.initButton)  
        self.initButton.SetDefault()

        self.comtext = wx.TextCtrl(panel, wx.ID_ANY,pos=(580,150), size =(50,20), value="COM4",style = wx.TE_RICH)
        self.baudratetext = wx.TextCtrl(panel, wx.ID_ANY,pos=(630,150), size =(50,20), value="500000",style = wx.TE_RICH)
        
        self.openPortButton = wx.Button(panel, -1, "Open Port", pos=(580,170),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.open_port, self.openPortButton)  
        self.openPortButton.SetDefault()
        
        self.closePortButton = wx.Button(panel, -1, "Close Port", pos=(580,190),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.close_port, self.closePortButton)  
        self.closePortButton.SetDefault()

        self.slider = []
        for i in range(LED_NUMBER):
            if i<(LED_NUMBER/2):
                self.slider.append(wx.Slider(panel,i,1,1,100,pos=(70+i*50,150),size=(1,100),style=wx.SL_RIGHT|wx.SL_LABELS|wx.SL_INVERSE))#创建滑块控件
            else:
                self.slider.append(wx.Slider(panel,i,1,1,100,pos=(70+(i-LED_NUMBER/2)*50,250),size=(1,100),style=wx.SL_RIGHT|wx.SL_LABELS|wx.SL_INVERSE))#创建滑块控件
        self.Bind(wx.EVT_SCROLL,self.set_LEDx_width)

        self.sliderDimming = wx.Slider(panel,LED_NUMBER,100,1,100,pos=(80,380),size=(200,10),style=wx.SL_LABELS)#Dimming for All units

        self.ledMatrixText = []
        for i in range(PIXEL_LED_NUMBERS):
            if i<(PIXEL_LED_NUMBERS/2):
                #self.ledMatrixText.append(wx.TextCtrl(panel,i,pos=(40 + i*30,450), size =(30,20), value='100',style = wx.TE_RICH | wx.TE_PROCESS_ENTER))
                self.ledMatrixText.append(wx.TextCtrl(panel,i,pos=(40 + i*30,470), size =(30,20), value='100',style = wx.TE_RICH | wx.TE_PROCESS_ENTER))
            else:
                #self.ledMatrixText.append(wx.TextCtrl(panel,i,pos=(40 + (i-PIXEL_LED_NUMBERS/2)*30,470), size =(30,20), value='100',style = wx.TE_RICH | wx.TE_PROCESS_ENTER))
                self.ledMatrixText.append(wx.TextCtrl(panel,i,pos=(40 + (i-PIXEL_LED_NUMBERS/2)*30,450), size =(30,20), value='100',style = wx.TE_RICH | wx.TE_PROCESS_ENTER))
            self.ledMatrixText[i].SetBackgroundColour("#"+COLOR_END_VALUE)
            self.Bind(wx.EVT_TEXT_ENTER,self.set_led_matrix_width,self.ledMatrixText[i])

        fontCopyright = wx.Font(10, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.labelCopyrightName = wx.StaticText(panel, wx.ID_ANY, "Application Name: Tps_UI", size=(300, 20), pos=(500, 500))
        self.labelCopyrightName.SetFont(fontCopyright)
        self.labelCopyrightName.SetForegroundColour('white')

        self.labelCopyrightDevLan = wx.StaticText(panel, wx.ID_ANY, "Develop language: Python 2.7", size=(300, 20),
                                              pos=(500, 520))
        self.labelCopyrightDevLan.SetFont(fontCopyright)
        self.labelCopyrightDevLan.SetForegroundColour('white')

        self.labelCopyrightOS = wx.StaticText(panel, wx.ID_ANY, "Author: Xingming He", size=(300, 20),
                                              pos=(500, 540))
        self.labelCopyrightOS.SetFont(fontCopyright)
        self.labelCopyrightOS.SetForegroundColour('white')


        wx.StaticText(panel, wx.ID_ANY, "Speed:", size=(60, 20),pos=(580,340))
        self.sppedtext = wx.TextCtrl(panel, wx.ID_ANY,pos=(640,340), size =(40,20), value='500',style = wx.TE_RICH )
        
        wx.StaticText(panel, wx.ID_ANY, "DimLevel:", size=(60, 20),pos=(580,360))
        self.dimLeveltext = wx.TextCtrl(panel, wx.ID_ANY,pos=(640,360), size =(40,20), value='100',style = wx.TE_RICH | wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER,self.get_LEDx_width,self.dimLeveltext)
        
        self.L2RButton = wx.Button(panel, -1, "L2R", pos=(580,380),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.mode_L2R, self.L2RButton)  
        self.L2RButton.SetDefault()

        self.R2LButton = wx.Button(panel, -1, "R2L", pos=(580,400),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.mode_R2L, self.R2LButton)  
        self.R2LButton.SetDefault()

        self.one232Button = wx.Button(panel, -1, "1to32", pos=(580,420),size =(100,20))  
        self.Bind(wx.EVT_BUTTON, self.mode_1to32_circle, self.one232Button)  
        self.one232Button.SetDefault()

        
        #self.resetuartButton = wx.Button(panel, -1, "Rest UART", pos=(300,70),size =(100,20))  
        #self.Bind(wx.EVT_BUTTON, self.init_uart, self.resetuartButton)  
        #self.resetuartButton.SetDefault()

        #self.setsyscfgButton = wx.Button(panel, -1, "Set SYS", pos=(300,90),size =(100,20))  
        #self.Bind(wx.EVT_BUTTON, self.init_tps, self.setsyscfgButton)  
        #self.setsyscfgButton.SetDefault()

    def set_OpticMode(self,event):
        opticMode =  self.OpticModeBox.GetValue()
        if opticMode == self.OpticModeList[0]: #Contry left
            #print opticMode
            opticModeAngle = self.OpticModeLeftBox.GetValue()
            if opticModeAngle == self.OpticModeLeftAngleList[0]: #0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,11.1,13.0,15.2,16.4,14.0,0,0,0,0.00,0.00,19.2,20.7,22.3,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[1]: #-0.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,11.1,13.0,15.2,14.0,0,0,0,0.00,0.00,22.3,19.2,20.7,22.3,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[2]: #-2.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,11.1,13.0,14.0,0,0,0,0.00,0.00,26.0,22.3,19.2,20.7,20.7,17.7,15.2,13.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[3]: #-3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,11.1,13.0,0,0,0,0.00,0.00,35.2,26.0,22.3,19.2,20.7,17.7,15.2,13.0,11.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[4]: #-5.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,11.1,0.00,0,0,0,0.00,35.2,35.2,26.0,22.3,19.2,17.7,15.2,13.0,11.1,9.40]
            elif opticModeAngle == self.OpticModeLeftAngleList[5]:#-7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35.2,35.2,30.3,24.1,20.7,17.7,15.2,13,11.1,9.4,8]
            elif opticModeAngle == self.OpticModeLeftAngleList[6]:#+2.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9.4,11.1,13,15.2,14,0,0,0,0,0,2.5,20.7,22.3,30.3,24.1,20.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[7]:#+3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8.0,9.4,11.1,13,14,0,0,0,0,0,2.5,5.2,22.3,30.3,30.3,24.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[8]:#+5.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6.8,8.0,9.4,11.1,13,0,0,0,0,0,2.5,5.2,7.4,30.3,32.7,30.3]
            elif opticModeAngle == self.OpticModeLeftAngleList[9]:#7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5.7,6.8,8.0,9.4,11.1,0,0,0,0,0,2.5,5.2,7.4,6.2,32.7,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[10]:
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4.8,5.7,6.8,8.0,9.4,0,0,0,0,0,2.5,5.2,7.4,6.2,5.2,32.7]
                
        elif opticMode == self.OpticModeList[1]: #town left
            opticModeAngle = self.OpticModeLeftBox.GetValue()
            if opticModeAngle == self.OpticModeLeftAngleList[0]: #0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,19.2,20.7,22.3,17.7,15.2,13.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[1]:#-0.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,22.3,19.2,20.7,17.7,15.2,13.0,11.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[2]:#-2.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,26.0,22.3,19.2,17.7,15.2,13.0,11.1,9.40]
            elif opticModeAngle == self.OpticModeLeftAngleList[3]:#-3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,26.0,26.0,22.3,17.7,15.2,13.0,11.1,9.40,8.00]
            elif opticModeAngle == self.OpticModeLeftAngleList[4]:#-5.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,26.0,26.0,26.0,17.7,15.2,13.0,11.1,9.40,8.00,6.80]
            elif opticModeAngle == self.OpticModeLeftAngleList[5]:#-7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,26.0,26.0,26.0,17.7,15.2,13.0,11.1,9.40,8.00,6.80,5.70]
            elif opticModeAngle == self.OpticModeLeftAngleList[6]:#+2.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.5,20.7,22.3,26,17.7,15.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[7]:#3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.5,5.2,22.3,26,26,17.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[8]:#+5.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.5,5.2,7.4,26,26,26]
            elif opticModeAngle == self.OpticModeLeftAngleList[9]:#+7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.5,5.2,7.4,6.2,26,26]
            elif opticModeAngle == self.OpticModeLeftAngleList[10]:#8.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.5,5.2,7.4,6.2,5.2,26]

        elif opticMode == self.OpticModeList[2]:#motorWay LB Left
            opticModeAngle = self.OpticModeLeftBox.GetValue()
            if opticModeAngle == self.OpticModeLeftAngleList[0]: #0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,35.2,35.2,30.3,32.7,28.1,24.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[1]:#-0.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,35.2,35.2,35.2,30.3,28.1,24.1,20.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[2]:#-2.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,35.2,35.2,35.2,32.7,28.1,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[3]:#-3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,47.6,35.2,35.2,32.7,28.1,24.1,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[4]:#-5.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,47.6,47.6,35.2,32.7,28.1,24.1,20.7,17.7,15.2,13.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[5]:#-7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,47.6,47.6,32.7,28.1,24.1,20.7,17.7,15.2,13.0,11.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[6]:#+2.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,0,0,0,0,0,3.30,35.2,30.3,38.0,32.7,28.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[7]:#+3.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,0,0,0,0,0,3.30,6.80,30.3,38.0,35.2,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[8]:#+5.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,0,0,0,0,0,3.30,6.80,9.40,38.0,35.2,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[9]:#+7.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,0,0,0,0,0,3.30,6.80,9.40,8.00,35.2,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[10]:#+8.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,0,0,0,0,0,3.30,6.80,9.40,8.00,6.80,32.7]
        
        elif opticMode == self.OpticModeList[3]:#high beam Left
            opticModeAngle = self.OpticModeLeftBox.GetValue()
            if opticModeAngle == self.OpticModeLeftAngleList[0]: #0
                dutycycleList=[24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[1]:#-0.7
                dutycycleList=[28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[2]:#-2.3
                dutycycleList=[32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,44.1,38.0,32.7,28.1,24.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,44.1,38.0,32.7,28.1,24.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[3]:#-3.9
                dutycycleList=[38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,69.0,59.5,44.1,32.7,28.1,24.1,20.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,69.0,59.5,44.1,32.7,28.1,24.1,20.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[4]:#-5.4
                dutycycleList=[44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[5]:#-7.0
                dutycycleList=[51.2,59.5,69.0,100,100,100,69.0,55.2,59.5,69.0,59.5,44.1,28.1,20.7,17.7,15.2,51.2,59.5,69.0,100,100,100,69.0,55.2,59.5,69.0,59.5,44.1,28.1,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[6]:#+2.4
                dutycycleList=[20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[7]:#+3.9
                dutycycleList=[17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[8]:#+5.5
                dutycycleList=[15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,59.5,69.0,69.0,100,100,100,69.0,55.2,15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,59.5,69.0,69.0,100,100,100,69.0,55.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[9]:#7.0
                dutycycleList=[13.0,15.2,17.7,20.7,24.1,28.1,32.7,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,13.0,15.2,17.7,20.7,24.1,28.1,32.7,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[10]:
                dutycycleList=[11.1,13.0,15.2,17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,11.1,13.0,15.2,17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0]
       
        elif opticMode == self.OpticModeList[4]: #Motorway HB Left
            opticModeAngle = self.OpticModeLeftBox.GetValue()
            if opticModeAngle == self.OpticModeLeftAngleList[0]:#0
                dutycycleList=[24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[1]:#-0.7
                dutycycleList=[28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[2]:#-2.3
                dutycycleList=[32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1,24.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,32.7,28.1,24.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[3]:#-3.9
                dutycycleList=[38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,69.0,59.5,44.1,32.7,28.1,24.1,20.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,69.0,59.5,44.1,32.7,28.1,24.1,20.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[4]:#-5.4
                dutycycleList=[44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,44.1,51.2,59.5,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeLeftAngleList[5]:#-7.0
                dutycycleList=[51.2,59.5,69.0,100,100,100,69.0,55.2,59.5,69.0,59.5,44.1,28.1,20.7,17.7,15.2,51.2,59.5,69.0,100,100,100,69.0,55.2,59.5,69.0,59.5,44.1,28.1,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[6]:#+2.4
                dutycycleList=[20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,38.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[7]:#+3.9
                dutycycleList=[17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,44.1]
            elif opticModeAngle == self.OpticModeLeftAngleList[8]:#+5.5
                dutycycleList=[15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2,15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,55.2]
            elif opticModeAngle == self.OpticModeLeftAngleList[9]:#+7.0
                dutycycleList=[13.0,15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0,13.0,15.2,17.7,20.7,24.1,28.1,32.7,38.0,44.1,51.2,59.5,69.0,100,100,100,69.0]
            elif opticModeAngle == self.OpticModeLeftAngleList[10]:#+8.5
                dutycycleList=[11.1,13.0,15.2,17.7,20.7,24.1,28.1,32.7,44.1,59.5,69.0,59.5,69.0,100,100,100,11.1,13.0,15.2,17.7,20.7,24.1,28.1,32.7,44.1,59.5,69.0,59.5,69.0,100,100,100]
            
        elif opticMode == self.OpticModeList[5]:#Contry Right
            opticModeAngle = self.OpticModeRightBox.GetValue()
            if opticModeAngle == self.OpticModeRightAngleList[0]:#0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,19.2,20.7,22.3,22.3,19.2,16.4,14.0,12.0,10.2]
            elif opticModeAngle == self.OpticModeRightAngleList[1]:#-1.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,22.3,19.2,20.7,22.3,19.2,16.4,14.0,12.0,10.2,8.70]
            elif opticModeAngle == self.OpticModeRightAngleList[2]:#-2.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,26.0,22.3,19.2,20.7,19.2,16.4,14.0,12.0,10.2,8.70,7.40]
            elif opticModeAngle == self.OpticModeRightAngleList[3]:#-4.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,35.2,26.0,22.3,19.2,19.2,16.4,14.0,12.0,10.2,8.70,7.40,6.20]
            elif opticModeAngle == self.OpticModeRightAngleList[4]:#-6.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,35.2,35.2,24.1,22.3,19.2,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20]
            elif opticModeAngle == self.OpticModeRightAngleList[5]:#-7.6
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35.2,35.2,24.1,22.3,19.2,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20,4.40]
            elif opticModeAngle == self.OpticModeRightAngleList[6]:#+1.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,20.7,22.3,24.1,22.3,19.2,16.4,14.0,12.0]
            elif opticModeAngle == self.OpticModeRightAngleList[7]:#+3.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,22.3,30.3,24.1,22.3,19.2,16.4,14.0]
            elif opticModeAngle == self.OpticModeRightAngleList[8]:#+4.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,30.3,32.7,24.1,22.3,19.2,16.4]
            elif opticModeAngle == self.OpticModeRightAngleList[9]:#+6.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,6.20,32.7,32.7,24.1,22.3,19.2]
            elif opticModeAngle == self.OpticModeRightAngleList[10]:#+7.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,6.20,5.20,32.7,35.2,24.1,22.3]
           
        elif opticMode == self.OpticModeList[6]:#town Right
            opticModeAngle = self.OpticModeRightBox.GetValue()
            if opticModeAngle == self.OpticModeRightAngleList[0]:#0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,0.00,19.2,20.7,17.7,16.4,14.0,12.0,10.2,8.70,7.40]
            elif opticModeAngle == OpticModeRightAngleList[1]:#-1.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,22.3,19.2,17.7,16.4,14.0,12.0,10.2,8.70,7.40,6.20]
            elif opticModeAngle == self.OpticModeRightAngleList[2]:#-2.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,22.3,22.3,17.7,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20]
            elif opticModeAngle == self.OpticModeRightAngleList[3]:#-4.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,22.3,26.0,17.7,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20,4.40]
            elif opticModeAngle == self.OpticModeRightAngleList[4]:#-6.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,22.3,26.0,17.7,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20,4.40,3.70]
            elif opticModeAngle == self.OpticModeRightAngleList[5]:#-7.6
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,22.3,26.0,17.7,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20,4.40,3.70,3.00]
            elif opticModeAngle == self.OpticModeRightAngleList[6]:#+1.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,20.7,22.3,17.7,16.4,14.0,12.0,10.2,8.70]
            elif opticModeAngle == self.OpticModeRightAngleList[7]:#+3.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,22.3,26.0,17.7,16.4,14.0,12.0,10.2]
            elif opticModeAngle == self.OpticModeRightAngleList[8]:#+4.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,22.3,26.0,17.7,16.4,14.0,12.0]
            elif opticModeAngle == self.OpticModeRightAngleList[9]:#+6.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,6.20,22.3,26.0,17.7,16.4,14.0]
            elif opticModeAngle == self.OpticModeRightAngleList[10]:#+7.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2.50,5.20,7.40,6.20,5.20,22.3,26.0,17.7,16.4]
            
        elif opticMode == self.OpticModeList[7]:#motorway LB Right
            opticModeAngle = self.OpticModeRightBox.GetValue()
            if opticModeAngle == self.OpticModeRightAngleList[0]:#0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,0.00,35.2,35.2,30.3,30.3,26.0,22.3,19.2,16.4,14.0]
            elif opticModeAngle == self.OpticModeRightAngleList[1]:#-1.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,0.00,35.2,35.2,32.7,30.3,26.0,22.3,19.2,16.4,14.0,12.0]
            elif opticModeAngle == self.OpticModeRightAngleList[2]:#-2.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,0.00,35.2,35.2,32.7,30.3,26.0,22.3,19.2,16.4,14.0,12.0,10.2]
            elif opticModeAngle == self.OpticModeRightAngleList[3]:#-4.5
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.00,40.9,35.2,32.7,30.3,26.0,22.3,19.2,16.4,14.0,12.0,10.2,8.70]
            elif opticModeAngle == self.OpticModeRightAngleList[4]:#-6.0
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,40.9,47.6,32.7,30.3,26.0,22.3,19.2,16.4,14.0,12.0,10.2,8.70,7.40]
            elif opticModeAngle == self.OpticModeRightAngleList[5]:#-7.6
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,47.6,32.7,30.3,26.0,22.3,19.2,16.4,14.0,12.0,10.2,8.70,7.40,6.20]
            elif opticModeAngle == self.OpticModeRightAngleList[6]:#+1.7
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3.30,35.2,30.3,32.7,30.3,26.0,22.3,19.2,16.4]
            elif opticModeAngle == self.OpticModeRightAngleList[7]:#+3.3
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3.30,6.80,30.3,38.0,32.7,30.3,26.0,22.3,19.2]
            elif opticModeAngle == self.OpticModeRightAngleList[8]:#+4.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3.30,6.80,9.40,38.0,35.2,32.7,30.3,26.0,22.3]
            elif opticModeAngle == self.OpticModeRightAngleList[9]:#+6.4
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3.30,6.80,9.40,8.00,35.2,32.7,30.3,28.1,26.0]
            elif opticModeAngle == self.OpticModeRightAngleList[10]:#+7.9
                dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3.30,6.80,9.40,8.00,6.80,32.7,30.3,28.1,26.0]
            
        elif opticMode == self.OpticModeList[8]:#high beam Right
            opticModeAngle = self.OpticModeRightBox.GetValue()
            if opticModeAngle == self.OpticModeRightAngleList[0]:#0
                dutycycleList=[32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1]
            elif opticModeAngle == self.OpticModeRightAngleList[1]:#-1.4
                dutycycleList=[38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7]
            elif opticModeAngle == self.OpticModeRightAngleList[2]:#-2.9
                dutycycleList=[44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,17.7,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeRightAngleList[3]:#-4.5
                dutycycleList=[55.2,69.0,100,100,100,69.0,69.0,59.5,44.1,38.0,32.7,28.1,24.1,20.7,17.7,15.2,55.2,69.0,100,100,100,69.0,69.0,59.5,44.1,38.0,32.7,28.1,24.1,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeRightAngleList[4]:#-6.0
                dutycycleList=[69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,32.7,28.1,24.1,20.7,17.7,15.2,13.0,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,32.7,28.1,24.1,20.7,17.7,15.2,13.0]
            elif opticModeAngle == self.OpticModeRightAngleList[5]:#-7.6
                dutycycleList=[100,100,100,69.0,59.5,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,15.2,13.0,11.1,100,100,100,69.0,59.5,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,15.2,13.0,11.1]
            elif opticModeAngle == self.OpticModeRightAngleList[6]:#+1.7
                dutycycleList=[28.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,28.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1]
            elif opticModeAngle == self.OpticModeRightAngleList[7]:#+3.3
                dutycycleList=[24.1,28.1,32.7,38.0,44.1,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,24.1,28.1,32.7,38.0,44.1,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7]
            elif opticModeAngle == self.OpticModeRightAngleList[8]:#+4.9
                dutycycleList=[20.7,24.1,28.1,32.7,44.1,59.5,69.0,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,20.7,24.1,28.1,32.7,44.1,59.5,69.0,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0]
            elif opticModeAngle == self.OpticModeRightAngleList[9]:#+6.4
                dutycycleList=[17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1]
            elif opticModeAngle == self.OpticModeRightAngleList[10]:#+7.9
                dutycycleList=[15.2,17.7,20.7,28.1,44.1,59.5,69.0,59.5,55.2,69.0,100,100,100,69.0,59.5,51.2,15.2,17.7,20.7,28.1,44.1,59.5,69.0,59.5,55.2,69.0,100,100,100,69.0,59.5,51.2]
            
        elif opticMode == self.OpticModeList[9]:#motorway HB Right
            opticModeAngle = self.OpticModeRightBox.GetValue()
            if opticModeAngle == self.OpticModeRightAngleList[0]:#0
                dutycycleList=[32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1]
            elif opticModeAngle == self.OpticModeRightAngleList[1]:#-1.4
                dutycycleList=[38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7]
            elif opticModeAngle == self.OpticModeRightAngleList[2]:#-2.9
                dutycycleList=[44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,17.7,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,24.1,20.7,17.7]
            elif opticModeAngle == self.OpticModeRightAngleList[3]:#-4.5
                dutycycleList=[55.2,69.0,100,100,100,69.0,69.0,59.5,44.1,38.0,32.7,28.1,24.1,20.7,17.7,15.2,55.2,69.0,100,100,100,69.0,69.0,59.5,44.1,38.0,32.7,28.1,24.1,20.7,17.7,15.2]
            elif opticModeAngle == self.OpticModeRightAngleList[4]:#-6.0
                dutycycleList=[69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,32.7,28.1,24.1,20.7,17.7,15.2,13.0,69.0,100,100,100,69.0,59.5,69.0,59.5,44.1,32.7,28.1,24.1,20.7,17.7,15.2,13.0]
            elif opticModeAngle == self.OpticModeRightAngleList[5]:#-7.6
                dutycycleList=[100,100,100,69.0,59.5,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,15.2,13.0,11.1,100,100,100,69.0,59.5,59.5,69.0,59.5,44.1,28.1,24.1,20.7,17.7,15.2,13.0,11.1]
            elif opticModeAngle == self.OpticModeRightAngleList[6]:#+1.7
                dutycycleList=[28.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1,28.1,32.7,38.0,44.1,55.2,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,28.1]
            elif opticModeAngle == self.OpticModeRightAngleList[7]:#+3.3
                dutycycleList=[24.1,28.1,32.7,38.0,44.1,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7,24.1,28.1,32.7,38.0,44.1,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,32.7]
            elif opticModeAngle == self.OpticModeRightAngleList[8]:#+4.9
                dutycycleList=[20.7,24.1,28.1,32.7,44.1,59.5,69.0,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0,20.7,24.1,28.1,32.7,44.1,59.5,69.0,69.0,100,100,100,69.0,59.5,51.2,44.1,38.0]
            elif opticModeAngle == self.OpticModeRightAngleList[9]:#+6.4
                dutycycleList=[17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1,17.7,20.7,24.1,28.1,44.1,59.5,69.0,59.5,69.0,100,100,100,69.0,59.5,51.2,44.1]
            elif opticModeAngle == self.OpticModeRightAngleList[10]:#+7.9
                dutycycleList=[15.2,17.7,20.7,28.1,44.1,59.5,69.0,59.5,55.2,69.0,100,100,100,69.0,59.5,51.2,15.2,17.7,20.7,28.1,44.1,59.5,69.0,59.5,55.2,69.0,100,100,100,69.0,59.5,51.2]

        elif opticMode == self.OpticModeList[10]:#test       
            dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35.2,35.2,24.1,22.3,19.2,16.4,14.0,12.0,10.2,8.70,7.40,6.20,5.20]
        else:
            dutycycleList=dutycycleList=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range(PIXEL_LED_NUMBERS):
            width = int(PWM_MAX*dutycycleList[i]/100)
            widthH = int(width/256)
            widthL = int((float(width)/256 - widthH)*256)
            

            ledPos = self.ledMatrix_i_2_ledPosUnit(i)[0]
            if width<PHASE_REG_DEVIDE_POINT:
                phase = (int(PHASE_REG_DEVIDE_POINT/12))*(ledPos+1)
                #phase = (11 - ledPos)*10
            else:
                phase = 0
            phaseH = int(phase/256)
            phaseL = int((float(phase)/256 - phaseH)*256)
            
            deviceid = self.ledMatrix_i_2_ledPosUnit(i)[1]
            regaddr = WIDTH_REG_ADDRESS_START + ledPos*4 + 2
            init = WRITE_CMD_TWO_BYTE
            data = [widthL, widthH]
            #data = [phaseL,phaseH,widthL,widthH]
            self.ledMatrixText[i].SetValue(str(int(dutycycleList[i])))
            self.set_led_matrix_color(i,2*int(dutycycleList[i]))               #Yellow means lighting
            self.set_write_info(init,deviceid,regaddr,data)
        
    def ledMatrix_i_2_ledPosUnit(self,ledMatrixPos):      #Led matrix from 0 to 31, get LED postion for tps of unitid.
        #print self.LeftOrRightRadioBox.GetSelection()
        if self.LeftOrRightRadioBox.GetSelection()== 0: #Left
            if ledMatrixPos>=1 and ledMatrixPos<=12: #deviceid = DEVICE_ID_010,LED matrix from 1(11) to 12(0)
                deviceid = DEVICE_ID_010
                unitLedPos = 12 - ledMatrixPos
            elif ledMatrixPos>=17 and ledMatrixPos<=28: #deviceid =DEVICE_ID_000,LED matrix from 17(0) to 28(11)
                deviceid = DEVICE_ID_000
                unitLedPos = ledMatrixPos - 17
            elif ledMatrixPos in LED_POSITION_ID_001_LEFT: ##deviceid =DEVICE_ID_001,LED matrix 0,13,14,15(7,4,5,6),16,29,30,31(8,11,10,9)
                deviceid = DEVICE_ID_001
                if ledMatrixPos==16:
                    unitLedPos = 7
                elif ledMatrixPos==0:
                    unitLedPos = 8
                else:
                    if ledMatrixPos<29:
                        unitLedPos = 24 - ledMatrixPos
                    else:
                        unitLedPos = 33 + (ledMatrixPos-29)*2 - ledMatrixPos
            else:
                deviceid = False
                unitLedPos = False
                print 'Wrong input position for ledMatrix i of device 010'
        elif self.LeftOrRightRadioBox.GetSelection()== 1: #Right
            if ledMatrixPos>=0 and ledMatrixPos<=11: #deviceid = DEVICE_ID_010,LED matrix from 0(11) to 11(0)
                deviceid = DEVICE_ID_010
                unitLedPos = 11 - ledMatrixPos
            elif ledMatrixPos>=16 and ledMatrixPos<=27: #deviceid =DEVICE_ID_000,LED matrix from 16(0) to 27(11)
                deviceid = DEVICE_ID_000
                unitLedPos = ledMatrixPos + 16
            elif ledMatrixPos>=12 and ledMatrixPos<=15: #deviceid =DEVICE_ID_001,LED matrix from 12(4) to 15(7)
                deviceid = DEVICE_ID_001
                unitLedPos = 23 - ledMatrixPos
            elif ledMatrixPos>=28 and ledMatrixPos<=31: #deviceid =DEVICE_ID_001,LED matrix from 28(11) to 31(8)
                deviceid = DEVICE_ID_001
                unitLedPos = 32 + (ledMatrixPos-28)*2 - ledMatrixPos
            else:
                deviceid = False
                unitLedPos = False
                print 'Wrong input position for ledMatrix i of device 010'

        ''' 
        if ledMatrixPos>=LED_POSITION_MIN_ID_000 and ledMatrixPos<=LED_POSITION_MAX_ID_000: #deviceid = DEVICE_ID_000,LED matrix from 20(11) to 31(0)
            deviceid = DEVICE_ID_000
            unitLedPos = LED_POSITION_MAX_ID_000 - ledMatrixPos
        elif ledMatrixPos>=LED_POSITION_MIN_ID_010 and ledMatrixPos<=LED_POSITION_MAX_ID_010: #deviceid =DEVICE_ID_010,LED matrix from 4(0) to 15(11)
            deviceid = DEVICE_ID_010
            unitLedPos = ledMatrixPos - LED_POSITION_MIN_ID_010
        elif ledMatrixPos in LED_POSITION_ID_001: ##deviceid =DEVICE_ID_001,LED matrix 19,18,17,16(4,5,6,7),0,1,2,3(8,9,10,11)
            deviceid = DEVICE_ID_001
            if ledMatrixPos>=16:
                unitLedPos = 23 - ledMatrixPos
            else:
                unitLedPos = ledMatrixPos + 8
        else:
            unitLedPos = False
        '''
            
        #print deviceid
        #print unitLedPos
        return unitLedPos,deviceid

    def ledPosUnit_2_ledMatrix_i(self,unitid,unitLedPos):    #Get LedMatrix postion from led postion of unitid of tps
        if self.LeftOrRightRadioBox.GetSelection()== 0: #Left
            if unitid == DEVICE_ID_010:
                if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 11(1) to 0(12)
                    ledMatrixPos = 12- unitLedPos
                else:
                    ledMatrixPos = False
                    print 'Wrong input unitLedPos of device 000'
            elif unitid == DEVICE_ID_000:
                if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 0(17) to 11(28)
                    ledMatrixPos = unitLedPos + 17
                else:
                    ledMatrixPos = False
                    print 'Wrong input unitLedPos of device 010'
            elif unitid == DEVICE_ID_001:
                if unitLedPos>=4 and unitLedPos<=11: #uinit_i 7,4,5,6(0,13,14,15),8,11,10,9(16,29,30,31)
                    if unitLedPos==7:
                        ledMatrixPos = 16
                    elif unitLedPos==8:
                        ledMatrixPos = 0
                    else:
                        if unitLedPos<9:
                            ledMatrixPos = 33 + (unitLedPos-4)*2 - unitLedPos
                        else:
                            ledMatrixPos = 24 - unitLedPos
                else:
                    ledMatrixPos = False
                    print 'Wrong input unitLedPos of device 001'
            else:
                ledMatrixPos = False
        elif self.LeftOrRightRadioBox.GetSelection()== 1: #Right
            if unitid == DEVICE_ID_010:
                if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 11(0) to 0(11)
                    ledMatrixPos = 11- unitLedPos
                else:
                    ledMatrixPos = False
                    print 'Wrong input unitLedPos of device 000'
            elif unitid == DEVICE_ID_000:
                if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 0(16) to 11(27)
                    ledMatrixPos = unitLedPos + 16
                else:
                    ledMatrixPos = False
                    print 'Wrong input unitLedPos of device 010'
            elif unitid == DEVICE_ID_001:
                if unitLedPos>=4 and unitLedPos<=11: #uinit_i from 4(12) to 7(15)
                    if unitLedPos<=7:
                        ledMatrixPos = 32 + (unitLedPos-4)*2 - unitLedPos
                    else:                           #uinit_i from 8(31) to 11(28)
                        ledMatrixPos = 23 - unitLedPos
            else:
                ledMatrixPos = False



        '''   
        if unitid == DEVICE_ID_000:
            if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 0(20) to 11(31)
                ledMatrixPos = unitLedPos + 20
            else:
                ledMatrixPos = False
                print 'Wrong input unitLedPos of device 000'
        elif unitid == DEVICE_ID_010:
            if unitLedPos>=0 and unitLedPos<=11: #uinit_i from 0(4) to 11(15)
                ledMatrixPos = unitLedPos + 4
            else:
                ledMatrixPos = False
                print 'Wrong input unitLedPos of device 010'
        elif unitid == DEVICE_ID_001:
            if unitLedPos>=4 and unitLedPos<=11: #uinit_i 4,5,6,7(19,18,17,16),8,9,10,11(0,1,2,3)
                if unitLedPos>=8:
                    ledMatrixPos = unitLedPos - 8
                else:
                    ledMatrixPos = 23 - unitLedPos
            else:
                ledMatrixPos = False
                print 'Wrong input unitLedPos of device 001'
        else:
            ledMatrixPos = False
        '''
        #print ledMatrixPos
        return ledMatrixPos


    
    def set_led_matrix_color(self,ledMatrixPos,colorValueSet):
        ledMatrixPos = int(ledMatrixPos)
        colorValue = START_VALUE - colorValueSet
        colorValue = str(hex(colorValue))
        colorValue = colorValue.replace('0x','')
        self.ledMatrixText[ledMatrixPos].SetBackgroundColour("#"+colorValue)

    def set_led_matrix_width(self,event):
        ledMatrixPos = event.GetId()
        colorValueSet = int(self.ledMatrixText[ledMatrixPos].GetValue())
        #print colorValueSet
        colorValue = START_VALUE - 2*colorValueSet
        colorValue = str(hex(colorValue))
        colorValue = colorValue.replace('0x','')
        self.ledMatrixText[ledMatrixPos].SetBackgroundColour("#"+colorValue)
        ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
        deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
        #print ledPos
        #print deviceid
        dutycycle = colorValueSet
        width = int(PWM_MAX*dutycycle/100)
        widthH = int(width/256)
        widthL = int((float(width)/256 - widthH)*256)
        if width<PHASE_REG_DEVIDE_POINT:
            phase = (int(PHASE_REG_DEVIDE_POINT/12))*(ledPos+1)
        else:
            phase = 0
        phaseH = int(phase/256)
        phaseL = int((float(phase)/256 - phaseH)*256)
        regaddr = WIDTH_REG_ADDRESS_START + ledPos*4 + REG_ADDRESS_OFFSET
        init = WRITE_CMD_FOUR_BYTE
        data = [phaseL,phaseH,widthL,widthH]
        self.set_write_info(init,deviceid,regaddr,data)

    def mode_display(self,event):
        if self.timeMsgType == '1to32Circle':
            #data = [0,0]
            width = 0
            init = WRITE_CMD_FOUR_BYTE
            i = self.delayCount
            if i>15:
                ledMatrixPos = 47 - i
            else:
                ledMatrixPos = i
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            if width<PHASE_REG_DEVIDE_POINT:
                phase = (int(PHASE_REG_DEVIDE_POINT/12))*(ledPos+1)
            else:
                phase = 0
            phaseH = int(phase/256)
            phaseL = int((float(phase)/256 - phaseH)*256)
            data = [phaseL,phaseH,0,0]
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = WIDTH_REG_ADDRESS_START + ledPos*4 + REG_ADDRESS_OFFSET
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            self.set_write_info(init,deviceid,regaddr,data)
            self.delayCount += 1
            #print self.delayCount
            if i == PIXEL_LED_NUMBERS - 1:
                self.timeMsgType = None
                self.delayTime.Stop()
        else:
            #data = [0,0]
            width = 0
            init = WRITE_CMD_FOUR_BYTE
            i = self.delayCount
            ledMatrixPos = i
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            if width<PHASE_REG_DEVIDE_POINT:
                phase = (int(PHASE_REG_DEVIDE_POINT/12))*(ledPos+1)
            else:
                phase = 0
            phaseH = int(phase/256)
            phaseL = int((float(phase)/256 - phaseH)*256)
            data = [phaseL,phaseH,0,0]
            
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = WIDTH_REG_ADDRESS_START + ledPos*4 + REG_ADDRESS_OFFSET
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            self.set_write_info(init,deviceid,regaddr,data)
            
            ledMatrixPos = i + 16
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            if width<PHASE_REG_DEVIDE_POINT:
                phase = (int(PHASE_REG_DEVIDE_POINT/12))*(ledPos+1)
            else:
                phase = 0
            phaseH = int(phase/256)
            phaseL = int((float(phase)/256 - phaseH)*256)
            data = [phaseL,phaseH,0,0]
            
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = WIDTH_REG_ADDRESS_START + ledPos*4 + REG_ADDRESS_OFFSET
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            self.set_write_info(init,deviceid,regaddr,data)
            if self.timeMsgType == 'L2R':
                self.delayCount += 1
                #print self.delayCount
                if i == PIXEL_LED_NUMBERS/2 - 1:
                    self.timeMsgType = None
                    self.delayTime.Stop()
            elif self.timeMsgType == 'R2L':
                self.delayCount -= 1
                #print self.delayCount
                if i == 0:
                    self.timeMsgType = None
                    self.delayTime.Stop()
            else:                               #No event for this message type
                self.timeMsgType = None
                self.delayTime.Stop()
            
    def mode_1to32_circle(self,event):
        speed = int(self.sppedtext.GetValue())
        self.set_TPS_width(100)         # all lighting
        self.delayTime.Start(speed,False)
        self.delayCount= 0
        self.timeMsgType = '1to32Circle'
        
    def mode_L2R(self,event):
        speed = int(self.sppedtext.GetValue())
        self.set_TPS_width(100)         # all lighting
        self.delayTime.Start(speed,False)
        self.delayCount= 0
        self.timeMsgType = 'L2R'
        '''
        #self.set_TPS_width(100)         # all lighting
        data = [0,0]
        init = WRITE_CMD_TWO_BYTE
        for i in range(PIXEL_LED_NUMBERS/2):
            ledMatrixPos = i
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = 64 + ledPos*4 + 2
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            #self.set_write_info(init,deviceid,regaddr,data)
            ledMatrixPos = i + 16
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = 64 + ledPos*4 + 2
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            #self.set_write_info(init,deviceid,regaddr,data)
            #sleep(DELAY_TIME)
        '''  


    def mode_R2L(self,event):
        speed = int(self.sppedtext.GetValue())
        self.set_TPS_width(100)         # all lighting
        self.delayTime.Start(speed,False)
        self.delayCount= 15
        self.timeMsgType = 'R2L'
        '''
        self.set_TPS_width(100)         # all lighting
        data = [0,0]
        init = WRITE_CMD_TWO_BYTE
        for i in range(15,-1,-1):
            ledMatrixPos = i
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = 64 + ledPos*4 + 2
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            self.set_write_info(init,deviceid,regaddr,data)
            ledMatrixPos = i + 16
            ledPos = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[0]
            deviceid = self.ledMatrix_i_2_ledPosUnit(ledMatrixPos)[1]
            regaddr = 64 + ledPos*4 + 2
            self.ledMatrixText[ledMatrixPos].SetValue('0')
            self.set_led_matrix_color(ledMatrixPos,0)               #White means no lighting
            self.set_write_info(init,deviceid,regaddr,data)
            sleep(DELAY_TIME)
        '''
    def get_LEDx_width(self,event):
        width = int(self.dimLeveltext.GetValue()) #Need to complete wrong type value situation
        self.set_TPS_width(width)
        
        
    def set_LEDx_width(self,event):
        #sleep(0.1)
        LED_i = event.GetId()
        if LED_i == LED_NUMBER:                     #Dim to same level for all LEDs in each unit
            dutycycle = self.sliderDimming.GetValue()
            width = int(PWM_MAX*dutycycle/100)
            widthH = int(width/256)
            widthL = int((float(width)/256 - widthH)*256)
            for i in range(len(self.UnitList)):
                deviceidKey = self.UnitList[i]
                deviceid = self.UnitDic[deviceidKey]
                j = 0
                for j in range(LED_NUMBER):
                    if deviceid == DEVICE_ID_001:
                        if j<4:
                            continue
                    if width<PHASE_REG_DEVIDE_POINT:
                        phase = (int(PHASE_REG_DEVIDE_POINT/12))*(j+1)
                    else:
                        phase = 0
                    phaseH = int(phase/256)
                    phaseL = int((float(phase)/256 - phaseH)*256)
                    regaddr = WIDTH_REG_ADDRESS_START + j*4 + REG_ADDRESS_OFFSET
                    init = WRITE_CMD_FOUR_BYTE
                    data = [phaseL,phaseH,widthL,widthH]
                    ledMatrixPos = self.ledPosUnit_2_ledMatrix_i(deviceid,j)
                    self.ledMatrixText[ledMatrixPos].SetValue(str(dutycycle))
                    self.set_led_matrix_color(ledMatrixPos,dutycycle*2)
                    self.set_write_info(init,deviceid,regaddr,data)
                
        else:                                       #Dim individually for single LED of specific unit
            dutycycle = self.slider[LED_i].GetValue()
            width = int(PWM_MAX*dutycycle/100)
            widthH = int(width/256)
            widthL = int((float(width)/256 - widthH)*256)
            if width<PHASE_REG_DEVIDE_POINT:
                phase = (int(PHASE_REG_DEVIDE_POINT/12))*(LED_i+1)
            else:
                phase = 0
            phaseH = int(phase/256)
            phaseL = int((float(phase)/256 - phaseH)*256)
            regaddr = WIDTH_REG_ADDRESS_START + LED_i*4 + REG_ADDRESS_OFFSET
            init = WRITE_CMD_FOUR_BYTE
        
            key =  self.DeviceIDBox.GetValue()
            value = self.UnitDic[key]
            deviceid = int(value)
            data = [phaseL,phaseH,widthL,widthH]
            ledMatrixPos = self.ledPosUnit_2_ledMatrix_i(deviceid,LED_i)
            self.ledMatrixText[ledMatrixPos].SetValue(str(dutycycle))
            self.set_led_matrix_color(ledMatrixPos,dutycycle*2)
            self.set_write_info(init,deviceid,regaddr,data)
        
            
    def select_Iint(self,event):     #set init byte
        key =  self.IintBox.GetValue()
        #value = '%2x'%self.InitDic[key]
        value = self.InitDic[key]
        lmm = int(value)
        index = self.InitList.index(key)
        if index<4:
            number = index + 1
        elif index>=7 and index<11:
            number = index - 6
        else:
            if index == 4 or index == 11:
                number = 12
            elif index == 5 or index == 12:
                number = 16
            else:
                number = 32
        #print number
        key =  self.DeviceIDBox.GetValue()
        value = self.UnitDic[key]
        deviceid = int(value)

        key =  self.RegaddrBox.GetValue()
        value = self.RegaddrDic[key]
        regaddr = int(value)
        if index<7: # Write command
            if regaddr == DPHASE01L_ADDR:
                lmm = WRITE_CMD_TWO_BYTE
                phase = self.datatext.GetValue()
                if phase == '':
                    print 'No valid data'
                else:
                    phase = int(self.datatext.GetValue())
                    phaseH = int(phase/256)
                    phaseL = int((float(phase)/256 - phaseH)*256)
                    data = [phaseL,phaseH]
                    for i in range(LED_NUMBER):
                        regaddr = 64+i*4
                        self.set_write_info(lmm,deviceid,regaddr,data)
            else:
                key =  self.IintBox.GetValue()
                value = self.InitDic[key]
                lmm = int(value)
                data = self.parse_data(self.datatext.GetValue())
                self.set_write_info(lmm,deviceid,regaddr,data)
        else: # Read command
            dataRx = self.get_read_info(lmm,deviceid,regaddr,number)
            self.datatext.SetValue(dataRx)
            #print dataRx
            
        return value

    def select_DeviceID(self,event):
        key =  self.DeviceIDBox.GetValue()
        value = '%2x'%self.UnitDic[key]
        #print value
        return value

    def select_Regaddr(self,event):
        key =  self.RegaddrBox.GetValue()
        value = '%2x'%self.RegaddrDic[key]
        #print value
        return value
    
    def write_info(self, event):
        try:
            key =  self.DeviceIDBox.GetValue()
            value = self.UnitDic[key]
            deviceid = int(value)
            key =  self.RegaddrBox.GetValue()
            value = self.RegaddrDic[key]
            regaddr = int(value)
            
            if regaddr == DPHASE01L_ADDR:
                lmm = WRITE_CMD_TWO_BYTE
                phase = int(self.datatext.GetValue())
                phaseH = int(phase/256)
                phaseL = int((float(phase)/256 - phaseH)*256)
                data = [phaseL,phaseH]
                for i in range(LED_NUMBER):
                    regaddr = 64+i*4
                    self.set_write_info(lmm,deviceid,regaddr,data)
            else:
                key =  self.IintBox.GetValue()
                value = self.InitDic[key]
                lmm = int(value)
                data = self.parse_data(self.datatext.GetValue())
                self.set_write_info(lmm,deviceid,regaddr,data)

        except Exception as e:
            print e.message

    def read_info(self,event):
        try:
            #lmm = int(self.lmmtext.GetValue())
            key =  self.IintBox.GetValue()
            value = self.InitDic[key]
            lmm = int(value)
            #print self.lmmtext.GetValue()
            
            key =  self.DeviceIDBox.GetValue()
            value = self.UnitDic[key]
            deviceid = int(value)
            #deviceid = int(self.deviceidtext.GetValue())

            key =  self.RegaddrBox.GetValue()
            value = self.RegaddrDic[key]
            regaddr = int(value)
            #regaddr = int(self.regaddrtext.GetValue())
            #print self.regaddrtext.GetValue()
            number = int(self.datatext.GetValue())
            #print data
            dataRx = self.get_read_info(lmm,deviceid,regaddr,number)
            print dataRx
        except Exception as e:
            print e.message

    def close_port(self,event):
        port = self.comtext.GetValue()
        try:
            if len(port)>2:
                if(port[0:3]) != "COM":
                    self.comtext.SetValue("COM")
            else:
                port = int(self.comtext.GetValue())
                port = "COM" + str(port)   
                print port
            self.serObj.port = port
            self.serial_close()
        except Exception as e:
            print e.message
        

    def open_port(self,event):
        port = self.comtext.GetValue()
        baudrate = self.baudratetext.GetValue()
        try:
            if len(port)>2:
                if(port[0:3]) != "COM":
                    self.comtext.SetValue("COM")
            else:
                port = int(self.comtext.GetValue())
                port = "COM" + str(port)   
                print port
            self.serObj.port = port
            self.serObj.baudrate = int(baudrate)
            self.serial_open()
        except Exception as e:
            print e.message

    def init_uart(self,event):
        self.serObj.baudrate = 50000
        self.serial_open()
        self.init_uart_reset()
        
    def init_tps(self,event):
        self.serObj.baudrate = 500000
        self.serial_open()
        self.init_tps_sys()

    def init_all(self,event):
        self.serObj.baudrate = 50000
        self.serial_open()
        self.init_uart_reset()
        self.serObj.baudrate = 500000
        self.serial_open()
        self.init_tps_sys()
        self.set_TPS_width(100)         # Init dutycycle
        
    def set_TPS_width(self,dutycycle):
        width = int(PWM_MAX*dutycycle/100)
        widthH = int(width/256)
        widthL = int((float(width)/256 - widthH)*256)
        for i in range(len(self.UnitList)):
            deviceidKey = self.UnitList[i]
            deviceid = self.UnitDic[deviceidKey]
            j = 0
            for j in range(LED_NUMBER):
                if deviceid == DEVICE_ID_001:
                        if j<4:
                            continue
                if width<PHASE_REG_DEVIDE_POINT:
                    phase = (int(PHASE_REG_DEVIDE_POINT/12))*(j+1)
                else:
                    phase = 0
                phaseH = int(phase/256)
                phaseL = int((float(phase)/256 - phaseH)*256)
                regaddr = WIDTH_REG_ADDRESS_START + j*4 + REG_ADDRESS_OFFSET
                init = WRITE_CMD_FOUR_BYTE
                data = [phaseL,phaseH,widthL,widthH]
                if j == LED_NUMBER - 1 and deviceid == DEVICE_ID_010: # solve issue of Channel for LED3_1 to LED3_12 no enough output
                    data = [0,0]
                ledMatrixPos = self.ledPosUnit_2_ledMatrix_i(deviceid,j)
                self.ledMatrixText[ledMatrixPos].SetValue(str(dutycycle))
                self.set_led_matrix_color(ledMatrixPos,2*dutycycle)               #Yellow means lighting
                self.set_write_info(init,deviceid,regaddr,data)
                
                    
    
    def parse_data(self,data):
        #data = self.datatext.GetValue()
        countlist=[]
        length = len(data)
        if length == 0:
            count = 0
        else:
            count = 1     #one number at least
                
        index = 0
        pos = 0
        for c in data:
            if c.isspace():
                count += 1
                pos = index + data[index:length].find(c)
                countlist.append(pos)
                index = pos+1
        if count == 1:
            countlist.append(1) #No space
        #print ('count is %d'%(count))
        #print ('pos is %d'%(pos))
        #print countlist
        datainfo = []
        for i in range(count):
            if i == 0:
                datainfo.append(data[0:countlist[i]])
            elif i <count - 1:
                datainfo.append(data[countlist[i-1]:countlist[i]])
            else:
                datainfo.append(data[countlist[i-1]:(len(data))])
        #print datainfo
        return datainfo
        

    def leftUP(self,event):
        print(self.text.GetStringSelection())


class App(wx.App):
    def __init__(self,redirect=True,filename=None):
        print "App__init__"
        wx.App.__init__(self,redirect,filename)

    def OnInit(self):
        print "OnInit"
        self.frame=Frame(parent=None,id=-1,title='Startup')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        print >>sys.stderr,"A pretend error message"
        return True

    def OnExit(self):

        print "OnExit"





if __name__ == '__main__':
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()
