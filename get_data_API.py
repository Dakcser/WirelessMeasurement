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



def get_sensor_locations():
    
        # ------ Old API ------------
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
        
    #Dictionary with key and coordinates
    sensor_list = {}
    for sensor in old_sensor_data[0]:

        #Check for Nones in data
        if sensor['location'] == None:
            continue

        #without hyphens; ex. A81758FFFE046433
        old_id = sensor['deviceId']
        #with hyphens; ex. A8-17-58-FF-FE-04-64-33
        new_id = '-'.join(old_id[i:i+2] for i in range(0, len(old_id), 2))

        #Create dictionary {key new_id : value coordinates}
        sensor_list[new_id] = sensor['location']['coordinates']
        
    return sensor_list

def get_data():
    
    sensor_list = get_sensor_locations()
    
    #smart campus api key
    headers = {
        'Content-type': 'application/json', 
        'Authorization': f'{apikey.APIKEY}',
    }
    
    # Set the API endpoint and request 15000 datapoints
    url = 'https://query-api.rahtiapp.fi/events?limit=15000'

    # Send the API request
    response = requests.get(url, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Print the sensor data
        sensor_data = response.iter_lines()
    else:
        print("Error: API request failed with status code", response.status_code)
        
    #Create list out of response
    resp = []
    for line in response.iter_lines(decode_unicode=True):
        resp.append(json.loads(line))
    
    #Create dataframe
    df = pd.DataFrame(columns=['ID','time','temperature','humidity','light','motion','co2', 'coordinates'])
    
    #iterate trough response list
    for measurement in resp[0]:

        #add row to dataframe
        df.loc[len(df.index)]=[measurement['deveui'],       #id
                               measurement['time'],         #timestamp
                               measurement['temperature'],  #temperature
                               measurement['humidity'],     #humidity
                               measurement['light'],        #illuminance
                               measurement['motion'],       #motion
                               measurement['co2'],          #CO2
                               sensor_list[measurement['deveui'].upper()] #coordinates[lat, lng]
                              ]

    return df
