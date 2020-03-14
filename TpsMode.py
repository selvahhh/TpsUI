#! /usr/bin/python2

import openpyxl as xls
import os

pathXLS = os.path.join(os.getcwd(),'TPSmode.xlsx')
print pathXLS
PROJECT_NAME = 'Pixel32'
MODE_MAX_NUMNERS = 200

wb = None

def open_XLS():
    global wb
    try:
        wb = xls.load_workbook(pathXLS)
        print 'Open successfully '
        return True
    except IOError,e:
        print e.message
        return False
    
def close_XLS():
    global wb
    wb.close()
    wb = None

def read_mode(mode):
    global wb
    open_XLS()
    try:
        sheetProj = wb[PROJECT_NAME]
        for i in range(1,MODE_MAX_NUMNERS):
            if mode == sheetProj.cell(row=i,column=1).value:
                print i 
    except KeyError,e:
        print e.message
    close_XLS()

def write_mode(mode,data):
    global wb
    open_XLS()


if __name__ == "__main__":
    open_XLS()
    close_XLS()
    read_mode('ADB')
