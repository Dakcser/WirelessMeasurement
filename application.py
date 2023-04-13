import math
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import folium
import webbrowser
from requests.auth import HTTPBasicAuth
from datetime import timedelta
from fix_html import move_imageOverlay_to_back
from folium import plugins
from folium.map import Layer
from folium.plugins import HeatMapWithTime
from folium.plugins import MarkerCluster
from get_data_API import get_data
from jinja2 import Template 

sys.path.insert(1, '../')

unique_sensor_id_list = []
co2_sensors = []
audio_sensors = []

class HeatMapWithTimeAdditional(Layer):
    """
    A custom Layer class extending the Layer class for creating a time-enabled heatmap.

    This class utilizes a custom template to generate a JavaScript-based heatmap for
    visualizations, allowing customization of heatmap options such as radius, opacity,
    scaling, and gradient.
    """

    _template = Template("""
        {% macro script(this, kwargs) %}
            var {{this.get_name()}} = new TDHeatmap({{ this.data }},
                {heatmapOptions: {
                    radius: {{this.radius}},
                    minOpacity: {{this.min_opacity}},
                    maxOpacity: {{this.max_opacity}},
                    scaleRadius: {{this.scale_radius}},
                    useLocalExtrema: {{this.use_local_extrema}},
                    defaultWeight: 1,
                    {% if this.gradient %}gradient: {{ this.gradient }}{% endif %}
                }
            }).addTo({{ this._parent.get_name() }});
        {% endmacro %}
    """)

    def __init__(self, data, name=None, radius=15,
                min_opacity=0, max_opacity=0.6,
                scale_radius=False, gradient=None, use_local_extrema=False,
                overlay=True, control=True, show=True):
        """
        Initializes a HeatMapWithTimeAdditional layer with the specified settings.

        Parameters:
            data (list): Heatmap data.
            name (str, optional): Layer name.
            radius (int, optional): Heatmap radius. Default is 15.
            min_opacity (float, optional): Minimum heatmap opacity. Default is 0.
            max_opacity (float, optional): Maximum heatmap opacity. Default is 0.6.
            scale_radius (bool, optional): If True, scales the radius. Default is False.
            gradient (dict, optional): Color gradient for the heatmap.
            use_local_extrema (bool, optional): If True, uses local extrema. Default is False.
            overlay (bool, optional): If True, adds overlay. Default is True.
            control (bool, optional): If True, adds control. Default is True.
            show (bool, optional): If True, shows the heatmap. Default is True.
        """
        super(HeatMapWithTimeAdditional, self).__init__(
            name=name, overlay=overlay, control=control, show=show
        )
        self._name = 'HeatMap'
        self.data = data

        # Heatmap settings.
        self.radius = radius
        self.min_opacity = min_opacity
        self.max_opacity = max_opacity
        self.scale_radius = 'true' if scale_radius else 'false'
        self.use_local_extrema = 'true' if use_local_extrema else 'false'
        self.gradient = gradient
    
def get_unique_sensor_locations(df):
    """
    Categorizes unique sensors into CO2 and audio sensors based on the DataFrame. Updates global list audio_sensors & co2_sensors
    HOX! Don't use global variables, this function need rewrite. 

    Parameters:
        df (pd.DataFrame): Sensor data DataFrame.
    """
    #declare global variables
    global unique_sensor_id_list, co2_sensors, audio_sensors
    unique_sensor_id_list = df["ID"].unique()

    #split data based on sensor type and save to a list
    for sensor in unique_sensor_id_list:
        if (df[df["ID"]==sensor]['co2'].tail(1).values[0]) == None:
            audio_sensors.append(df[df["ID"]==sensor].tail(1).values.tolist())
        else:
            co2_sensors.append(df[df["ID"]==sensor].tail(1).values.tolist())
            
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
        timeIndexes.append((selected_data["time"].iloc[1] + i * timedelta(minutes=15)).strftime("%d/%m/%Y, %H:%M:%S")[:-3])

    #iterate through dataframe -------------------------------------
    data = [[] for _ in range(len(timeIndexes))]
    
    for _, row in selected_data.iterrows():
        #Checking for None type
        if not row[data_shown] is None:
            #Check that data isn't zero or NaN
            if (not math.isnan(row[data_shown]) and row[data_shown] != 0.0):
                data[row["period"]].append([row['coordinates'][0],row['coordinates'][1],row[data_shown]])
              
    return data, timeIndexes   
        
def main():
    # get data
    df = get_data()
    get_unique_sensor_locations(df)

    #Min-Max scale motion data
    column = "motion"
    df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())

    #Formate motion, co2, temperature and humidity data
    motion_data, motion_time = data_formating(df, "motion")
    co2_data, co2_time = data_formating(df, "co2")
    temperature_data, temperature_time = data_formating(df, "temperature")
    humidity_data, humidity_time = data_formating(df, "humidity")
    
    #Create the map
    m = folium.Map([65.059228, 25.465375], zoom_start=16.45)

    #Add campus map on top of the map
    folium.raster_layers.ImageOverlay(
                                    image="img/university_map.png",
                                    name="university map",
                                    bounds=[[65.062044, 25.462502], [65.056337, 25.471510]],
                                    opacity=1,
                                    interactive=False,
                                    cross_origin=False,
                                    zindex=-1
                                    ).add_to(m)

    ##Create data layers
    #Motion
    HeatMapWithTime(motion_data, index=motion_time, auto_play=True, max_opacity=0.9, name="Motion").add_to(m)
    #CO2
    HeatMapWithTimeAdditional(co2_data, show=False, max_opacity=0.9, name="CO2").add_to(m)
    #Temperature
    HeatMapWithTimeAdditional(temperature_data, show=False, max_opacity=0.9, name="temperature").add_to(m)
    #Humidity
    HeatMapWithTimeAdditional(humidity_data, show=False, max_opacity=0.9, name="humidity").add_to(m)
    #Sensor objects
    sensors_cluster = folium.FeatureGroup(name="sensors", show=False).add_to(m)

    #Loop trough audio sensors and add the to the map
    for sensor in audio_sensors:
        custom_icon = folium.CustomIcon("img/sound_icon.png", icon_size=(14, 14))
    
        time = sensor[0][1]
        #2023-04-03T22:09:01.169Z
        form_time = "{}.{}.{} {}:{}".format(time[8:10],time[5:7],time[0:4],time[11:13],time[14:16])
        iframe = folium.IFrame("""
                               Last measurement<br>
                               Time stamp: {}<br>
                               Temperature: {}°C<br>
                               humidity: {}%<br>
                               light: {} <br>
                               motion:  {}
                               """.format(form_time,
                                          sensor[0][2],
                                          sensor[0][3],
                                          sensor[0][4],
                                          sensor[0][5]
                                          ),
                               width=300,
                               height=150
                               )
    
        popup = folium.Popup(iframe, min_width=200, max_width=200)
        marker = folium.Marker(location=sensor[0][7], icon=custom_icon, popup=popup)
        sensors_cluster.add_child(marker)
    
    #Loop trough CO2 sensors and add the to the map
    for sensor in co2_sensors:
        custom_icon = folium.CustomIcon("img/co2_icon.png", icon_size=(14, 14))
    
        time = sensor[0][1]
        #2023-04-03T22:09:01.169Z
        form_time = "{}.{}.{} {}:{}".format(time[8:10],time[5:7],time[0:4],time[11:13],time[14:16])
        iframe = folium.IFrame("""
                               Last measurement<br>
                               Time stamp: {}<br>
                               Temperature: {}°C<br>
                               humidity: {}%<br>
                               light: {} <br>
                               motion:  {} <br>
                               CO2: {}
                               """.format(form_time,
                                          sensor[0][2],
                                          sensor[0][3],
                                          sensor[0][4],
                                          sensor[0][5],
                                          sensor[0][6]
                                          ),
                               width=300,
                               height=150
                               )
    
        popup = folium.Popup(iframe, min_width=200, max_width=200)
        marker = folium.Marker(location=sensor[0][7], icon=custom_icon, popup=popup)
        sensors_cluster.add_child(marker)

    #Add LayerControl object to map   
    folium.LayerControl().add_to(m)
    
    #Save and display the map
    m.save(outfile="index.html")

    #Move imageOverlay to z-height=-1
    move_imageOverlay_to_back()

    #Display map in Browser
    webbrowser.open("index.html")
    
if __name__ == "__main__":
    main()