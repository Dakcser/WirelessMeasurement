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

from datetime import datetime, timedelta
import math


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
    
    # Set the API endpoint and request maximum of 15000 datapoints from the last 12 hours
    now = datetime.now() - timedelta(days=1)
    halfDayAgo = now - timedelta(days=1)
    now = str(now.isoformat())
    halfDayAgo = str(halfDayAgo.isoformat())
    url = f'https://query-api.rahtiapp.fi/events?from={halfDayAgo}Z&to={now}Z&limit=33000'

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

def data_formating(df, data_shown):
    
    print(f"Formating data for {data_shown} map")
    selected_data = df[["coordinates", data_shown, "time"]]
    
    #Convert ISO-8601 time format to pandas DateTime format 
    selected_data.time = pd.to_datetime(selected_data.time, format="%Y-%m-%dT%H:%M:%S.%fZ")
    
    #Add new column 'period' to dataframe, every row gets group number based on 15min clusters
    new = selected_data.groupby(pd.Grouper(key='time', freq='15Min'),as_index=False).apply(lambda x: x['time'])
    selected_data['period'] = new.index.get_level_values(0)
    
    #create time indexes for HeatMapWithTime ----------------------
    timeIndexes = []
    
    #get last period in dataframe
    for i in range(selected_data['period'].iloc[-1] + 1):

        #Add multiples of 15min to first timestamp based on period value
        timeIndexes.append((selected_data["time"].iloc[1] + i * timedelta(minutes=15)).strftime("%m/%d/%Y, %H:%M:%S")[:-3])

    #iterate through dataframe -------------------------------------
    data = [[] for _ in range(len(timeIndexes))]
    
    for _, row in selected_data.iterrows():
        #Checking for None type
        if not row[data_shown] is None:
            #Check that data isn't zero or NaN
            if (not math.isnan(row[data_shown]) and row[data_shown] != 0.0):
                
                data[row["period"]].append([row['coordinates'][0],row['coordinates'][1],row[data_shown]])
              
    return data, timeIndexes
