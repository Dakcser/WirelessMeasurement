import numpy as np
import requests
import json
import apikey
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt

import folium
from folium import plugins
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import time
from folium import plugins
from folium.plugins import HeatMap

def get_data():

    #smart campus api key
    headers = {
        'Content-type': 'application/json', 
        'Authorization': f'{apikey.APIKEY}',
    }

    # Set the API endpoint and request all devices
    url = 'https://query-api.rahtiapp.fi/events'
    

    # Send the API request
    response = requests.get(url, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Print the sensor data
        sensor_data = response.iter_lines()
        print(sensor_data)
    else:
        print("Error: API request failed with status code", response.status_code)
        
    devices = []
    devicesInFloorOne = []

    #loop through all devices API gave
        
    for line in response.iter_lines(decode_unicode=True):
        #print(line)
        devices.append(json.loads(line))

    device_id_list = [device["deveui"] for device in devices[0]]

    ## Remove duplicates
    device_id_list = list(dict.fromkeys(device_id_list))
    print("Amount of unique devices: ", len(device_id_list))


    # API with sensor values uses IDs with lower cases and dashes,
    # while the API with location data uses them with upper cases and without dashes

    # Form a dictionary for ID mapping
    idDict = {}
    for id in device_id_list:
        tempId = id.replace("-", '').upper()
        idDict[id] = tempId

    print(device_id_list[0])
    print(idDict[device_id_list[0]])

    # Set the API endpoint and request all devices
    url = 'https://smartcampus.oulu.fi/manage/api/devices/listAll'
    old_sensor_data = []

    # Send the API request
    response = requests.get(url)

    # Check the response status code
    if response.status_code == 200:
        print("200")
    else:
        print("Error: API request failed with status code", response.status_code)
        
    for line in response.iter_lines(decode_unicode=True):
        old_sensor_data.append(json.loads(line))

    old_sensor_locations = []
    for line in old_sensor_data[0]:
        print(line)
        try:
            old_sensor_locations.append((line["deviceId"], line['location']['coordinates']))
        except TypeError:
            continue

    get_id = []
    for device in devices[0]:
        if device['motion'] != None:
            get_id.append(device)

    heatmap = []

    for motion in get_id:
        for sensor in old_sensor_locations:
            if sensor[0] == idDict[motion['deveui']]:
                #print("Found")
                heatmap.append([sensor[1][0], sensor[1][1], motion['motion']])
                break

    return heatmap
