import sys
import io
import numpy as np
from requests.auth import HTTPBasicAuth

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import time
from folium import plugins
from folium.plugins import HeatMap
from folium.plugins import HeatMapWithTime
import folium 

from get_data_API import get_data

def main():

    m = folium.Map([65.059228, 25.465375], zoom_start=16.45)

    folium.raster_layers.ImageOverlay(
                                    image="./img/university_map_sub_2Mb.png",
                                    name="university map",
                                    bounds=[[65.062044, 25.462502], [65.056337, 25.471510]],
                                    opacity=1,
                                    interactive=False,
                                    cross_origin=False,
                                    zindex=1
                                    ).add_to(m)



    # get data
    df = get_data()


    motion_data = df[["coordinates", "motion", "time"]]
    data = []
    timestamps = []

    for _, row in motion_data.iterrows():
        #check for nan in data
        if np.isnan(row['motion']):
            continue
            
        data.append([row['coordinates'][0],row['coordinates'][1],row['motion']])
        timestamps.append(row['time'])

    #HeatMap(data[:500]).add_to(folium.FeatureGroup(name='Heat Map').add_to(m))
    HeatMapWithTime(data[:500]).add_to(m)
    folium.LayerControl().add_to(m)


    m.save(outfile="index.html")

    webbrowser.open("index.html")


if __name__ == "__main__":
    main()
