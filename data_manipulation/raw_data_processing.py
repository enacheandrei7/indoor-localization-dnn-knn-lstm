#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program used to parse the XML dataset file and convert it into a csv
"""

import xml.etree.ElementTree as ET
import os
import glob
import pandas as pd
import numpy as np

pd.set_option('display.float_format', '{:.15f}'.format)
# pd.set_option("display.max_columns", None)


def calculate_ms_interval(times_list):
    """
    Helper method used to calculate the number of ms between the first and the last timestamp.

    Parameters:
        times_list (list): list containing strings on format hh:mm:ss:msms from the xml raw file

    Returns:
        full_timestamps_list (list): List containing all the timestamps between the first and the last registered value in format hh:mm:ss:msms
    """
    full_timestamps_list = []

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
    return full_timestamps_list

def xml_imu_sensors_converter(sensors_xml):
    """
    Reads the xml inputs and creates a new DataFrame with the aggregated accelerometer, gyroscope and magnetometer sensor data.

    Parameters:
        sensors_xml (str): The path to the xml file containing sensor accelerometer, gyroscope, magnetometer and wifi data

    Returns:
        df (DataFrame): DataFrame containing the sensors data (Accelerometer, Gyro, Magnetomter) from the raw xml input file
    """
    tree = ET.parse(sensors_xml)
    root = tree.getroot()
    xml_timestamps = []
    full_timestamps_list = []

    # If no elements in file,
    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    for element in root:
        xml_timestamps.append(element.attrib['st'])
    times_list = list(dict.fromkeys(xml_timestamps))

    # # Take the first and last timestamp from the xml file and replace the last ":" with "." in order
    # # to be accepted as input for date_range
    # start_time = ".".join(root[0].attrib['st'].rsplit(":", 1))
    # end_time = ".".join(root[-1].attrib['st'].rsplit(":", 1))
    # # Create a fixed frequency DatetimeIndex (10ms frequence)
    # datetimes_indexes = pd.date_range(start_time, end_time, freq="10L")
    # # Take the hour:min:sec:ms and eplace the "." with ":" in the DatetimeIndexes
    # full_timestamps_list = datetimes_indexes.map(lambda t: str(t).split(" ")[1][:-4].replace(".", ":"))

    full_timestamps_list = calculate_ms_interval(times_list)

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
    # print(df)
    # df.to_csv("data/Processed/sensor_data.csv")
    return df

def imu_sensor_and_position_generator(sensors_df, ground_truth_xml):
    """
    Reads the xml ground truth inputs and outputs a dataframe containing the sensor data and the ground truth

    Parameters:
        sensors_df (DataFrame): DataFrame containing accelerometer, gyroscope and magnetometer data
        ground_truth_xml (str): The path to the xml file containing the ground truth location with latitude and longitude
    """
    tree = ET.parse(ground_truth_xml)
    root = tree.getroot()
    first_loc_timestamp = root[0].attrib['time'][:11]
    last_loc_timestamp = root[-1].attrib['time'][:11]
    sens_and_loc_df = sensors_df

    # If no elements in file,
    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    sens_and_loc_df['lat'] = np.NaN
    sens_and_loc_df['long'] = np.NaN

    for element in root:
        # the time format for ground_truth has 3 values at ms, not 2 like in the sensor data, so we keep only the first 11 chars (hh:mm:ss:msms)
        timestamp = element.attrib['time'][:11]
        sens_and_loc_df.at[timestamp, 'lat'] = float(element.attrib['lat'])
        sens_and_loc_df.at[timestamp, 'long'] = float(element.attrib['long'])

    sens_and_loc_df = sens_and_loc_df[sens_and_loc_df.index >= first_loc_timestamp]
    sens_and_loc_df = sens_and_loc_df[sens_and_loc_df.index <= last_loc_timestamp]

    # Interpolate the data in order to fill all the lat and long
    sens_and_loc_df = sens_and_loc_df.interpolate(method='linear')
    # print(sens_and_loc_df)
    # sens_and_loc_df.to_csv('data/Processed/sensor_and_location.csv')
    return sens_and_loc_df

def xml_wifi_converter(sensors_xml):
    """
    Wifi data parser, reads the xml inputs and creates a new DataFrame with the Wifi data.

    Parameters:
        sensors_xml (str): The path to the xml file containing sensor accelerometer, gyroscope, magnetometer and wifi data

    Returns:
        wifi_df (DataFrame): DataFrame containing the wifi data from the raw xml input file. It has all the timestamps between the first and last wifi reading, at 10ms intervals, even though many rows are empty as the wifi data was taken at about 1000 ms
    """
    tree = ET.parse(sensors_xml)
    root = tree.getroot()
    xml_timestamps = []
    times_list = []
    full_timestamps_list = []
    xml_raw_ap_ids_list = []
    ap_ids_list = []

    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    for element in root:
        if element.tag == 'wr':
            xml_timestamps.append(element.attrib['st'])
            for wifi_subtag in element:
                xml_raw_ap_ids_list.append(wifi_subtag.attrib['b'])

    # List with the unique wifi timestamps
    times_list = list(dict.fromkeys(xml_timestamps))
    # List with the AP (Access Points) individual ids
    ap_ids_list = list(dict.fromkeys(xml_raw_ap_ids_list))
    # List with all the timestamps between the first and the last ones from the APs, with 10ms interval
    full_timestamps_list = calculate_ms_interval(times_list)

    wifi_df = pd.DataFrame(None, index=full_timestamps_list, columns=ap_ids_list)

    for element in root:
        if element.tag == 'wr':
            wr_attributes = element.attrib
            for wifi_subtag in element:
                wifi_df.at[wr_attributes['st'], wifi_subtag.attrib['b']] = float(wifi_subtag.attrib['s'])

    return wifi_df

def wifi_and_position_generator(wifi_df, ground_truth_xml):
    """
    Reads the xml ground truth inputs and outputs a dataframe containing the wifi data and the ground truth

    Parameters:
        wifi_df (DataFrame): DataFrame containing wifi data
        ground_truth_xml (str): The path to the xml file containing the ground truth location with latitude and longitude
    Returns:
        wifi_and_loc_df (DataFrame): DataFrame containing only the wifi values and their corresponding locations
    """
    tree = ET.parse(ground_truth_xml)
    root = tree.getroot()
    first_loc_timestamp = root[0].attrib['time'][:11]
    last_loc_timestamp = root[-1].attrib['time'][:11]
    wifi_and_loc_df = wifi_df

    # If no elements in file,
    if root.__len__() < 1:
        print('Xml file has no sensor values')
        exit(-1)

    wifi_and_loc_df['lat'] = np.NaN
    wifi_and_loc_df['long'] = np.NaN

    for element in root:
        # the time format for ground_truth has 3 values at ms, not 2 like in the sensor data, so we keep only the first 11 chars (hh:mm:ss:msms)
        timestamp = element.attrib['time'][:11]
        wifi_and_loc_df.at[timestamp, 'lat'] = float(element.attrib['lat'])
        wifi_and_loc_df.at[timestamp, 'long'] = float(element.attrib['long'])

    # Removing rows that were before the first position and after the last (As a test, this could be removed in the future to see if extrapolation works for backward or if having more interpolated info works in our advantag)
    wifi_and_loc_df = wifi_and_loc_df[wifi_and_loc_df.index >= first_loc_timestamp]
    wifi_and_loc_df = wifi_and_loc_df[wifi_and_loc_df.index <= last_loc_timestamp]

    wifi_and_loc_df.loc[:, 'lat'].interpolate(inplace=True)
    wifi_and_loc_df.loc[:, 'long'].interpolate(inplace=True)

    wifi_and_loc_df.dropna(thresh=3, inplace=True)

    return wifi_and_loc_df

def wifi_and_sensors_combiner(sensor_df, wifi_df):
    pass

if __name__ == "__main__":
    # All data folders
    sc_1_precisloc_data_folder = 'data/PrecisLoc/Scenario_1/'
    output_folder = 'data/Processed/'
    # Data files for easier testing
    sensor_readings_xml_path = 'data/PrecisLoc/Scenario_1/1/Sensor_readings_11-05-07.xml'
    ground_truth_xml_path = 'data/PrecisLoc/Scenario_1/1/ground_truth_11-05-07.xml'
    # sensor_readings_csv_path = 'sensor_data.csv'
    ground_truts_files_list = []
    raw_sensor_data_files_list = []

    for filename in glob.glob(f"{sc_1_precisloc_data_folder}**/ground*"):
        ground_truts_files_list.append(filename)

    for filename in glob.glob(f"{sc_1_precisloc_data_folder}**/Sensor*"):
        raw_sensor_data_files_list.append(filename)

    data_file_paths = zip(ground_truts_files_list, raw_sensor_data_files_list)

    for idx, data in enumerate(data_file_paths):
        # IMU sensors
        df_sensor_readings = xml_imu_sensors_converter(sensor_readings_xml_path)
        # df_sensor_readings.to_csv(f"{output_folder}sensor_data_{idx+1}.csv")
        df_sensor_and_pos = imu_sensor_and_position_generator(df_sensor_readings, ground_truth_xml_path)
        df_sensor_and_pos.to_csv(f"{output_folder}sensor_data_and_location_{idx+1}.csv")

        # Wifi data
        df_wifi = xml_wifi_converter(sensor_readings_xml_path)
        df_wifi_and_pos = wifi_and_position_generator(df_wifi, ground_truth_xml_path)
        df_wifi_and_pos.to_csv(f"{output_folder}wifi_data_and_location_{idx+1}.csv")

        print(f'File {idx+1} converted')

