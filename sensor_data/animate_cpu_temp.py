# /usr/bin/env python
# -*- coding: UTF-8 -*-
import numpy as np
import os
import sys
import time
import datetime
import signal
import subprocess
import matplotlib.dates as md
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.pylab import *
import pandas as pd
import xlwt
from argparse import ArgumentParser
import atexit
import psutil

import random

# For graphic
fig = plt.figure(figsize=(12, 10))
ax2 = subplot2grid((2,1), (0,0))
ax1 = subplot2grid((2,1), (1,0))
# fig, ax1 = plt.subplots(1,2,figsize=(8, 4.5))

xdata, ydata = [], []
cpu_data = []
data_line, = ax1.plot([], [], '-')
danger_line, = ax1.plot([], [], 'r--')
cpu_monitor_line, = ax2.plot([], [], '-', color='C1')
temp_word = ax1.text([], [], '', fontsize=48, color='b')

# Custom Parameters
N_SAMPLES = 100
N_GRIDS = 10
interval_in_ms = 1000

# For data recording
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
sheet1.write(0, 2, 'CPU Usage (%)')

global is_saved
is_saved = False

def shutdown_callback(signal=None, frame=None):
    global is_saved
    if not is_saved:
        is_saved = True
        plt.close()
        filepath = os.path.expanduser('~')+'/cpuTemp'+start_time.strftime('%Y-%m-%d-%H-%M-%S')+'.xls'
        if len(xdata) > 0:
            print('Saving all values to ' + filepath)
            global xlsbook
            xlsbook.save(filepath)
        else:
            print('Close program without saving data.')
        sys.exit(0)


def get_cpu_temp():
    # Call command like a command line shell and get the return value
    ret_byte = subprocess.check_output(['vcgencmd', 'measure_temp'])
    # Convert byte to string value, the result is like "temp=48.5'C"
    ret_str = ret_byte.decode('utf-8')
    # Cut string from 'equal symbol' to 'degree C symbol', then convert to float
    cpu_temp = float(ret_str[ret_str.find('=')+1: ret_str.find('\'')])
    return cpu_temp
        

def update_grid(start_time):
    end_time = start_time + datetime.timedelta(seconds=interval_in_ms/1000*N_SAMPLES)
    xgrid_start = start_time + datetime.timedelta(seconds=-start_time.second) + datetime.timedelta(seconds=start_time.second//10*10)
    xgrid_list = []
    for i in range(N_GRIDS):
        xgrid_list.append(md.date2num(xgrid_start + datetime.timedelta(seconds=i*N_GRIDS*interval_in_ms/1000)))
    ax1.set_xticks(xgrid_list)
    ax1.set_xlim(start_time, end_time)
    ax2.set_xticks(xgrid_list)
    ax2.set_xlim(start_time, end_time)
    
    
def get_cpu_usage():
    # tmp = str(os.popen("top -n1|awk '/Cpu\(s\):/ {print $2}'").readline().strip())
    tmp = psutil.cpu_percent()
    return(float(tmp))

def init():
    # Set X axis format
    xfmt = md.DateFormatter('%M:%S')
    ax1.xaxis.set_major_formatter(xfmt)
    ax2.xaxis.set_major_formatter(xfmt)
    
    global xls_cnt
    xls_cnt = 0

    # Set X axis grid ticks and limitation of axis
    global start_time
    start_time = datetime.datetime.now() 
    update_grid(start_time=start_time)
    ax1.set_ylim(20, 100)
    ax2.set_ylim(0, 100)

    # danger line
    xlim = ax1.get_xlim()
    danger_line.set_data(xlim, [85, 85])

    # Turn on grid, legend, xlabel and ylabel
    ax1.grid(b=None, which='major', axis='both')
    ax1.legend(['CPU Temperature', 'Official max operational temp'], loc='upper right')
    ax1.set_xlabel('Time (MM:SS)', fontsize=20)
    ax1.set_ylabel('Temperature (' + u"\u2103" +')', fontsize=20)
    ax2.grid(b=None, which='major', axis='both')
    ax2.legend(['CPU Usage'])
    # ax2.set_xlabel('Time (MM:SS)')
    ax2.set_ylabel('CPU Usage (%)', fontsize=20)
    
    return data_line, danger_line, cpu_monitor_line, temp_word


def update(frame):
    now_time = datetime.datetime.now()      # x axis data
    # cpu_temp = get_cpu_temp()               # y axis data
    # cpu_usage = get_cpu_usage()
    cpu_temp = random.uniform(20, 100)
    cpu_usage = random.uniform(20, 100)
    
    # Write data to xls sheet
    global xls_cnt
    xls_cnt = xls_cnt + 1
    global sheet1
    sheet1.write(xls_cnt, 0, str(now_time))
    sheet1.write(xls_cnt, 1, str(cpu_temp))
    sheet1.write(xls_cnt, 2, str(cpu_usage))

    # danger line
    xlim = ax1.get_xlim()
    danger_line.set_data(xlim, [85, 85])

    # Append data to graph list
    xdata.append(now_time)
    ydata.append(cpu_temp)
    cpu_data.append(cpu_usage)

    data_line.set_data(xdata, ydata)
    cpu_monitor_line.set_data(xdata, cpu_data)
    
    temp_word.set_position([md.date2num(md.num2date(xlim[1]) - datetime.timedelta(seconds=15)), 50])
    temp_word.set_text('{:.2f}'.format(cpu_temp) + u"\u2103")

    print(now_time.strftime('%Y-%m-%d %H:%M:%S'), ' CPU Temp:',str(cpu_temp), '(\'C) CPU Usage:', str(cpu_usage), '(%)')
    
    if len(xdata) > N_SAMPLES*0.8:
        update_grid(xdata[1])
        xdata.pop(0)
        ydata.pop(0)
        cpu_data.pop(0)
    return data_line, danger_line, cpu_monitor_line, temp_word



if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_callback)

    parser = ArgumentParser()
    parser.add_argument('--plot', '-p', type=str, help='Plot animation: ture or false', default='true')
    parser.add_argument('--freq', '-f', type=float, help='Sampling frequency in (ms)', default=interval_in_ms)
    args = parser.parse_args()
    if args.freq >= 500:
        interval_in_ms = args.freq

    if args.plot.lower() == 'false':
        while True:
            now_time = datetime.datetime.now()      # x axis data
            cpu_temp = get_cpu_temp()               # y axis data
            cpu_usage = get_cpu_usage()

            # Write data to xls sheet
            global xls_cnt
            xls_cnt = xls_cnt + 1
            global sheet1
            sheet1.write(xls_cnt, 0, str(now_time))
            sheet1.write(xls_cnt, 1, str(cpu_temp))
            sheet1.write(xls_cnt, 2, str(cpu_usage))
            
            xdata.append(now_time)
            ydata.append(cpu_temp)
            cpu_data.append(cpu_usage)
            # print(now_time.strftime('%Y-%m-%d %H:%M:%S'), ' CPU Temp:',str(cpu_temp))
            print(now_time.strftime('%Y-%m-%d %H:%M:%S'), ' CPU Temp:',str(cpu_temp), '(\'C) CPU Usage:', str(cpu_usage), '(%)')
    
            time.sleep(interval_in_ms/1000)
            
    elif args.plot.lower() == 'true':
        atexit.register(shutdown_callback)
        ani = FuncAnimation(fig, update, init_func=init, 
                            interval=interval_in_ms, repeat=False)
        plt.show()
