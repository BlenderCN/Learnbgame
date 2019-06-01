#!BPY
# -*- coding: UTF-8 -*-
#
# Utilities of read/write CSV file
#
#
# 2017.09.09 Natukikazemizo
import bpy
import csv

def write(file_path, file_name, data, enc = 'utf-8'):
    """write to csv"""
    try:
        # write with UTF-8
        if enc == 'utf-8':
            with open(file_path + file_name, 'w') as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                for row_data in data:
                    writer.writerow(row_data)
        else:
            # write on arg encoding
            with open(file_path + file_name, 'w', encoding=enc) as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                for row_data in data:
                    writer.writerow(row_data)
    except FileNotFoundError as e:
        print(e)
    except csv.Error as e:
        print(e)

def read(file_path, file_name, enc = 'utf-8'):
    header = []
    data = []
    try:
        if enc == 'utf-8':
            # utf-8 CSV File
            with open(file_path + file_name, 'r') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                header = next(csv_reader)
                for row in csv_reader:
                    data.append(row)
        else:
            # read arg encoding csv file
            with open(file_path + file_name, 'r', encoding = enc) as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                header = next(csv_reader)
                for row in csv_reader:
                    data.append(row)
    except FileNotFoundError as e:
        print(e)
    except csv.Error as e:
        print(e)
    return header, data
