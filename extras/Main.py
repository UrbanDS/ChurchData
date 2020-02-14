import urllib.request
import os
#import magic

import pandas as pd
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import numpy as np  # useful for many scientific computing in Python
# primary data structure library
#install -c conda-forge folium=0.5.0 --yes
import folium
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app = Flask(__name__)
page1 = 'upload'
page2='Italy.html'

@app.route('/')
def home():
    return render_template('frameset.html',src1=page1, src2="")


@app.route('/Italy.html')
def Italy():
     return render_template('Italy.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        df_incidents = pd.read_csv(request.files.get('file'))
        #df_incidents = pd.read_csv('data.csv')
        #print('Dataset downloaded and read into a pandas dataframe!')
        df_incidents.head()
        Italy_map = folium.Map(location=[41.9028, 12.4964], zoom_start=13)
        incidents = folium.map.FeatureGroup()
        #converting latitude and longitude to float values
        df_incidents.Longitude=df_incidents.Longitude.astype(float)
        df_incidents.Latitude=df_incidents.Latitude.astype(float)

        # loop through the 100 crimes and add each to the incidents feature group


        # add incidents to map of Italy
        Italy_map.add_child(incidents)
        from folium.plugins import HeatMapWithTime
        #base_map = generateBaseMap(default_zoom_start=11)
        df_century_list = []
        for century in df_incidents.Century_of_Origin.sort_values().unique():
            df_century_list.append(df_incidents.loc[df_incidents.Century_of_Origin==century,['Latitude','Longitude']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist())
            df_century_list
            centuries=[]
            centuries=df_incidents.Century_of_Origin.sort_values().unique()
            centuries=list(centuries)
            centuries
            HeatMapWithTime(df_century_list,  radius=15, index=centuries, position='topright', name='CO2 (micro-atm)',control=True).add_to(Italy_map)
            Italy_map.save("Italy.html")
        return render_template('frameset.html',src1=page1, src2=page2)
    return render_template('upload.html')
    
app.run()