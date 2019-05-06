#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import numpy as np
from collections import OrderedDict
import csv
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime
def Average(lst): 
    return sum(lst) / len(lst) 

def convertdate(dstring):
    dstring = str(dstring)
    if dstring.find('.') != -1:
        return datetime.datetime.strptime(dstring, '%Y-%m-%d %H:%M:%S.%f')
    else:
        return datetime.datetime.strptime(dstring, '%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    # read file
    # file = r'~/Downloads/temp_press_current2019-04-17-08-41-42.xls'
    file = r'~/Downloads/cpuTemp2019-05-06-15-20-42.xls'
    

    df = pd.read_excel(file)
    # extract data by column
    temperature_list = df['CPU Temperature']
    freq_list = df['CPU Frequency']/1000000
    # p2 = (df['Current2'])*12
    # p1 = abs(df['Current1'])*48

    timestamp_list = df['Time']
    time_inhour = []
    for timestamp in timestamp_list:
        time_inhour.append(convertdate(timestamp))
    print(time_inhour[0], time_inhour[-1])


    # avg_time_list = []
    # for i in range(len(timestamp_list)):
    #     if i % 360 == 0:
    #         avg_time_list.append(timestamp_list[i])
    #         avg_val_list.append(Average(p1[i:i+360]))
    # print(avg_time_list)


    fig = plt.figure(figsize=(10, 6)) 
    ax1 = fig.add_subplot(111, label="1")
    ax2 = fig.add_subplot(111, label="2", frame_on=False)
    ax1.plot(time_inhour, temperature_list)
    # plt.plot(avg_time_list, avg_val_list, 'o-')
    ax1.grid(b=None, which='major', axis='both')
    xfmt = md.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(xfmt)
    # plt.gca().set_xlim(datetime.datetime.strptime('2018-10-03 10:30:00', '%Y-%m-%d %H:%M:%S'), datetime.datetime.strptime('2018-10-03 15:30:00', '%Y-%m-%d %H:%M:%S'))
    ax1.set_xlabel('Time (HH:MM)')
    ax1.set_ylabel('Power comsumption(Watt)')
    # plt.legend(['Power of Rpi3 & sensors'])
    # plt.ylim([0, 20])
    # # plt.ylim([20, 60])

    ax2.scatter(time_inhour, freq_list, color="C1")
    ax2.yaxis.set_label_position('right') 
    ax2.tick_params(axis='y', colors="C1")
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    plt.show()

