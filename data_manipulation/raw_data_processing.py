#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program used to parse the XML dataset file and convert it into a csv
"""

import xml.etree.ElementTree as ET
import os
import pandas as pd
import numpy as np

def xml_sensors_converter(sensors_xml):
    """
    Reads the xml inputs and creates a new DataFrame with the aggregated accelerometer, gyroscope and magnetometer sensor data.

    Parameters:
        sensors_xml (str): The path to the xml file containing sensor accelerometer, gyroscope, magnetometer and wifi data

    Returns:
        df (DataFrame): DataFrame containing the sensors data (Accelerometer, Gyro, Magnetomter) from the raw xml input file
    """
    tree = ET.parse(sensors_xml)
    root = tree.getroot()
    time = []
    full_timestamps_list = []

    # If no elements in file,
    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    for element in root:
        time.append(element.attrib['st'])
    times_list = list(dict.fromkeys(time))

    # # Take the first and last timestamp from the xml file and replace the last ":" with "." in order
    # # to be accepted as input for date_range
    # start_time = ".".join(root[0].attrib['st'].rsplit(":", 1))
    # end_time = ".".join(root[0].attrib['st'].rsplit(":", 1))
    # # Create a fixed frequency DatetimeIndex (10ms frequence)
    # datetimes_indexes = pd.date_range(start_time, end_time, freq="10L")
    # # Take the hour:min:sec:ms and eplace the "." with ":" in the DatetimeIndexes
    # full_timestamps_list = datetimes_indexes.map(lambda t: str(t).split(" ")[1][:-4].replace(".", ":"))

    # We calculate the diffference between first and last values of timestamps
    hours_init, min_init, sec_init, ms_init = times_list[0].split(':')
    hours_end, min_end, sec_end, ms_end = times_list[-1].split(':')
    # The data is taken each 10 ms, so for the ms we must multiply by 10
    time_init = int(hours_init) * 60 * 60 * 1000 + \
                int(min_init) * 60 * 1000 + \
                int(sec_init)  * 1000 + \
                int(ms_init) * 10
    time_end = int(hours_end) * 60 * 60 * 1000 + \
               int(min_end) * 60 * 1000 + \
               int(sec_end)  * 1000 + \
               int(ms_end) * 10
    milisec_range = time_end - time_init
    # We've calculated the total number of ms between the first and last timestamp, but the values are taken
    # each 10 ms, so we must divide the number of total ms with 10, so instead of 10:05:10:100, 10:05:10:101,
    # we will have 10:05:10:10(0), 10:05:10:11(0)
    ms_range_with_interval = milisec_range // 10

    for ms in range(ms_range_with_interval+1):
        curr_miliseconds = time_init + ms * 10
        hour = str(curr_miliseconds//3600000)
        minute = f"{curr_miliseconds%3600000//60000:02d}"
        second = f"{curr_miliseconds%3600000%60000//1000:02d}"
        milisecond = f"{curr_miliseconds%3600000%60000%1000//10:02d}"
        full_timestamps_list.append(':'.join((hour, minute, second, milisecond)))

    df = pd.DataFrame(np.nan, index=full_timestamps_list, columns=['ax',
                                                                   'ay',
                                                                   'az',
                                                                   'gx',
                                                                   'gy',
                                                                   'gz',
                                                                   'mx',
                                                                   'my',
                                                                   'mz',
                                                                   'a_total',
                                                                   'g_total',
                                                                   'm_total'])


    for element in root:
        attributes = element.attrib
        sensor = ''
        if element.tag in ['a', 'g', 'm']:
            sensor = element.tag
            # if not df.at[attributes['st'], f'{sensor}x'] == np.NaN:
            df.at[attributes['st'], f'{sensor}x'] = float(attributes['x'])
            df.at[attributes['st'], f'{sensor}y'] = float(attributes['y'])
            df.at[attributes['st'], f'{sensor}z'] = float(attributes['z'])
            df.at[attributes['st'], f'{sensor}_total'] = np.sqrt(float(attributes['x'])**2+
                                                                 float(attributes['y'])**2+
                                                                 float(attributes['z'])**2)


    df=df.interpolate(method='linear')
    print(df)
    # df.to_csv("sensor_data.csv")
    return df


def sensor_and_position_generator(sensors_df, ground_truth_xml):
    """
    Reads the xml ground truth inputs and outputs a dataframe containing the sensor data and the ground truth

    Parameters:
        sensors_csv (str): The path to the xml file containing sensor accelerometer, gyroscope, magnetometer and wifi data
        ground_truth_xml (str): The path to the xml file containing the ground truth location with latitude and longitude
    """
    tree = ET.parse(ground_truth_xml)
    root = tree.getroot()
    time = []

    # If no elements in file,
    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    for element in root:
        time.append(element.attrib['time'][:11])
    times_list = list(dict.fromkeys(time))

    sensors_df['lat'] = np.NaN
    sensors_df['lng'] = np.NaN

    for time in times_list:
        sensors_df.at[time, 'lat'] = float(attributes['x'])



if __name__ == "__main__":
    sensor_readings_xml_path = 'data/PrecisLoc/Scenario_1/1/Sensor_readings_11-05-07.xml'
    ground_truth_xml_path = 'data/PrecisLoc/Scenario_1/1/ground_truth_11-05-07.xml'
    sensor_readings_csv_path = 'sensor_data.csv'

    df_sensor_readings = xml_sensors_converter(sensor_readings_xml_path)
    sensor_and_position_generator(df_sensor_readings, ground_truth_xml_path)

