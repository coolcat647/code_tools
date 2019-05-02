# /usr/bin/env python
# -*- coding: UTF-8 -*-
import numpy as np
import os
import time
import datetime
import signal
import subprocess
import matplotlib.dates as md
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import xlwt
import atexit

fig, ax = plt.subplots(figsize=(8, 4.5))
xdata, ydata = [], []
ln, = plt.plot([], [], 'o')

N_SAMPLES = 100
N_GRIDS = 10
interval_in_ms = 1000

global start_time
start_time = datetime.datetime.now()
global xls_cnt
xls_cnt = 0

global xlsbook
xlsbook = xlwt.Workbook(encoding='utf-8')

global sheet1
sheet1 = xlsbook.add_sheet('Sheet 1')
sheet1.write(0, 0, 'Time')
sheet1.write(0, 1, 'CPU Temperature')


def shutdown_callback():
    filepath = os.path.expanduser('~')+'/cpuTemp'+start_time.strftime('%Y-%m-%d-%H-%M-%S')+'.xls'
    print('Saving all values to ' + filepath)
    global xlsbook
    xlsbook.save(filepath)


def get_cpu_temp():
    # Call command like a command line shell and get the return value
    ret_byte = subprocess.check_output(['vcgencmd', 'measure_temp'])
    # Convert byte to string value, the result is like "temp=48.5'C"
    ret_str = ret_byte.decode('utf-8')
    # Cut string from 'equal symbol' to 'degree C symbol', then convert to float
    cpu_temp = float(ret_str[ret_str.find('=')+1: ret_str.find('\'')])
    return cpu_temp
        

def init():
    # Set X axis format
    xfmt = md.DateFormatter('%M:%S')
    plt.gca().xaxis.set_major_formatter(xfmt)
    
    global xls_cnt
    xls_cnt = 0

    # Set X axis grid ticks and limitation of axis
    global start_time
    start_time = datetime.datetime.now() 
    end_time = start_time + datetime.timedelta(seconds=interval_in_ms/1000*N_SAMPLES)
    xgrid_start = start_time + datetime.timedelta(seconds=-start_time.second) + datetime.timedelta(seconds=start_time.second//10*10)
    xgrid_list = []
    for i in range(N_GRIDS):
        xgrid_list.append(md.date2num(xgrid_start + datetime.timedelta(seconds=i*N_GRIDS*interval_in_ms/1000)))
    ax.set_xticks(xgrid_list)
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(20, 100)
    
    # Turn on grid, legend, xlabel and ylabel
    plt.grid(b=None, which='major', axis='both')
    plt.legend(['Temperature in the control box'])
    plt.xlabel('Time (HH:MM)')
    plt.ylabel('Temperature (degree C)')
    return ln,

def update(frame):
    # x axis data
    now_time = datetime.datetime.now()
    # y axis data
    cpu_temp = get_cpu_temp()
    
    global xls_cnt
    xls_cnt = xls_cnt + 1
    global sheet1
    sheet1.write(xls_cnt, 0, str(now_time))
    sheet1.write(xls_cnt, 1, str(cpu_temp))
    xdata.append(now_time)
    ydata.append(cpu_temp)
    ln.set_data(xdata, ydata)
    return ln,




if __name__ == "__main__":
    atexit.register(shutdown_callback)
    ani = FuncAnimation(fig, update, init_func=init, 
                            interval=interval_in_ms, repeat=False)
    plt.show()
