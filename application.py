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
import folium 
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from get_data_API import get_data

"""
Folium in PyQt5
"""
class Folium_Map(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Wireless Measurement Project - Smart campus')
        self.window_width, self.window_height = 1600, 1200
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

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
        
        

        # Plot data on the map
        heatmap = get_data()
        HeatMap(heatmap).add_to(folium.FeatureGroup(name='Heat Map').add_to(m))
        folium.LayerControl().add_to(m)

        # save map data to data object
        data = io.BytesIO()
        m.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        layout.addWidget(webView)


#Create application widget
app = QApplication(sys.argv)
app.setStyleSheet('''
    QWidget {
        font-size: 35px;
    }
''')

#Run code & create window
MyMap = Folium_Map()
MyMap.show()

try:
    sys.exit(app.exec_())
except SystemExit:
    print('Closing Window...')