'''
File Name:  tpsControl.py
Author:     xingming.he
Version:    V0.1
Date:       2019.7.22
Description: function: read and write data to TPS    
'''

#! /usr/bin/python2
import abc
import serial
import time
import os
import sys


CONSOLE_PORT    =           "COM5"
CRC_POLYNOM = 0xA001
CRC_PRESET  = 0x0000
WRITE_CMD_ONE_BYTE = 0x87
WRITE_CMD_TWO_BYTE = 0x99
WRITE_CMD_THREE_BYTE = 0x1E
WRITE_CMD_FOUR_BYTE = 0xAA
WRITE_CMD_TWELVE_BYTE = 0x2D
WRITE_CMD_SIXTEEN_BYTE = 0x33
WRITE_CMD_THIRTYTWO_BYTE = 0xB4

READ_CMD_ONE_BYTE = 0x4B
READ_CMD_TWO_BYTE = 0xCC
READ_CMD_THREE_BYTE = 0xD2
READ_CMD_FOUR_BYTE = 0x55
READ_CMD_TWELVE_BYTE = 0xE1
READ_CMD_SIXTEEN_BYTE = 0x66
READ_CMD_THIRTYTWO_BYTE = 0x78

DEVICE_ID_000 = 0x20 #32
DEVICE_ID_001 = 0x61 #97
DEVICE_ID_010 = 0xE2 #226
DEVICE_ID_100 = 0x64

BRODCAST_WRITE_ID = 0xBF

MPHASE01L_ADDR = 0x00
LPHASE01H_ADDR = 0x20
DPHASE01L_ADDR = 0x40
SLEWRATE_ADDR = 0x70
OVLMT_ADDR = 0x71
PARLED_ADDR = 0x72
DEFWIDTH02_01_ADDR = 0x73
SYSCFG_ADDR = 0x80
CMWTAP_ADDR = 0x81
PWMTICK_ADDR = 0x82
ADCID_ADDR = 0x83
SOFTSYNC_ADDR = 0x84
I2CTICK_ADDR = 0x90
I2CSLA_ADDR = 0x91
I2CRLEN_ADDR = 0x92
I2CADR_ADDR = 0x93
I2CCTRL_ADDR = 0x94
I2CDAT_ADDR = 0x95
I2CSTAT_ADDR = 0x96
I2CBMON_ADDR = 0x97
ADC1_ADDR = 0xA0
ADC2_ADDR = 0xA1
FAULTL_ADDR = 0xB0
FAULTH_ADDR = 0xB1
CERRCNT_ADDR = 0xB2
ICID_ADDR = 0xFF


#SYSCFG_ADDR = 0x80
SYSCFG_CONFIG = 0x84 #SEPTR =1, I2CEN =0, ACKEN=0,PSON=0,CMWEN=0,SYNCOEN=1,SYNCPEN=0,PWR=0


def calc_crc16_test(packet):
        length = len(packet)
        crc = CRC_PRESET
        for i in range(length):
            crc ^= packet[i]
            for j in range(8):
                if crc & 0x01:
                    crc= (crc>>1)^CRC_POLYNOM
                else:
                    crc = (crc >> 1)^0
        print hex(crc)
        return crc

class SerialTPS():
    #define globals
    serObj = serial.Serial()
    tpsFound = False
    
    def __init__(self,port = CONSOLE_PORT,baudrate = 500000):
        #self.writeInfo = [0x8D,0x0B0,0x55,0x05]
        #[141, 176, 85, 5]
        self.writeInfo = []
        self.readInfo = []
        #define the serial object to handle the rs232 communication
        self.serObj = serial.Serial()
        #use the default settings of feig
        self.serObj.baudrate = baudrate 
        self.serObj.timeout = 100
        self.serObj.parity=serial.PARITY_NONE
        self.serObj.port = port #Try the default COM Port
        #try:
            #self.serObj.open()
            #self.tpsFound= True
        #except:
            #self.tpsFound = False
        
        #if not self.tpsFound:
            #time.sleep(1.0)
            #self.serObj.close()
            #print "no port"

    def get_read_info(self,lmm,deviceid,regaddr,number):
        if len(self.readInfo):
            del self.readInfo
            self.readInfo = []
        try:
            self.readInfo.append(int(lmm))
            self.readInfo.append(int(deviceid))
            self.readInfo.append(int(regaddr))
            crc = self.calc_crc16(self.readInfo)
            #print self.readInfo
            #print hex(crc)
            self.readInfo.append(crc & 0xFF)
            self.readInfo.append((crc & 0xFF00) >> 8)
            #print self.readInfo
            self.serObj.write(self.readInfo) 
            resp = self.serObj.read(number + 2) #plus CRCL and CRCH
            #print "read info is "
            dataRx = self.hexShow(resp)
            #print dataRx
            return dataRx
            #print bytearray(resp)
            #if(self.is_crc_valid(resp)):
                #return resp
            #else:
                #return False
        except Exception as e:
            print e.message
            
        
    def set_write_info(self,lmm,deviceid,regaddr,data):
        if len(self.writeInfo):
            del self.writeInfo
            self.writeInfo = []
        try:
            self.writeInfo.append(int(lmm))
            self.writeInfo.append(int(deviceid))
            self.writeInfo.append(int(regaddr))
            if type(data) == int:
                self.writeInfo.append(int(data))
            else:
                for i in range(len(data)):
                    self.writeInfo.append(int(data[i]))
            crc = self.calc_crc16(self.writeInfo)
            self.writeInfo.append(crc & 0xFF)
            self.writeInfo.append((crc & 0xFF00) >> 8)
            #print "write info is "
            #print self.writeInfo
            self.serObj.write(self.writeInfo)
        except Exception as e:
            print "wrong in setWriteInfo " + e.message
            
    def hexShow(self,argv):  
        result = ''  
        hLen = len(argv)  
        for i in xrange(hLen):  
            hvol = ord(argv[i])  
            hhex = '%02x'%hvol  
            result += hhex+' '  
        #print 'hexShow:',result
        return result
        
    def calc_crc16(self,packet):
        length = len(packet)
        crc = CRC_PRESET
        for i in range(length):
            crc ^= packet[i]
            for j in range(8):
                if crc & 0x01:
                    crc= (crc>>1)^CRC_POLYNOM
                else:
                    crc = (crc >> 1)^0
        #print hex(crc)
        return crc
    
    def crc_16_ibm(self,packet):
        length = len(packet)
        crc = CRC_PRESET
        while length>0:
            crc ^= packet[len(packet) - length];
            for i in range(8):
                if crc & 0x01:
                    crc= (crc>>1)^CRC_POLYNOM
                else:
                    crc = (crc >> 1)^0
            length = length - 1
        #print hex(crc)
        return crc;


    def is_crc_valid(self,packet):
        try:
            #Calculate the CRC based on bytes received
            length = len(packet) - 2
            crc_calc = self.calc_crc16(packet[0:(length-1)]);
            crc_lsb = (crc_calc & 0x00FF);
            crc_msb = ((crc_calc >> 8) & 0x00FF);
            #Perform the bit reversal within each byte
            crc_msb = self.reverse_byte(crc_msb);
            crc_lsb = self.reverse_byte(crc_lsb);
            #Do they match?
            if((packet[length] == crc_lsb) and (packet[length+1] == crc_msb)):
                return True;
            else:
                return False;
        except Exception as e:
            print "wrong in is_crc_valid " + e.message

    def reverse_byte(self,byte):
        #First, swap the nibbles
        byte = (((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4));
        #Then, swap bit pairs
        byte = (((byte & 0xCC) >> 2) | ((byte & 0x33) << 2));
        #Finally, swap adjacent bits
        byte = (((byte & 0xAA) >> 1) | ((byte & 0x55) << 1));
        #We should now be reversed (bit 0 <--> bit 7, bit 1 <--> bit 6, etc.)
        print hex(byte)
        return byte;

    def serial_close(self):
        try:
            if self.serObj.isOpen():
                #print self.serObj.isOpen()
                self.serObj.close()
            else:
                pass
        except Exception as e:
            print e.message

    def serial_open(self):
        try:
            if not self.serObj.isOpen():
                #print self.serObj.isOpen()
                self.serObj.open()
            else:
                pass
        except Exception as e:
            print e.message

    def init_uart_reset(self):
        self.serObj.write([0x00])         #Holding RX of TPS low


    def init_tps_sys(self):
        self.set_write_info(WRITE_CMD_ONE_BYTE,BRODCAST_WRITE_ID,SYSCFG_ADDR,SYSCFG_CONFIG)
        #time.sleep(1.0)
        self.get_read_info(READ_CMD_ONE_BYTE,DEVICE_ID_000,SYSCFG_ADDR,1)
    
            

if __name__ == "__main__":
        serread = SerialTPS(CONSOLE_PORT,9600)
        serread.serial_open()
        serread.serObj.write(0x0F)
        resp = serread.serObj.read(2)
        print resp
        serread.serial_close()
