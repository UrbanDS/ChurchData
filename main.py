from flask import Flask, render_template_string, request, jsonify, url_for, render_template, send_from_directory,redirect
import os
import pandas as pd
import folium
from folium.plugins import HeatMapWithTime
from folium.plugins import MarkerCluster
import time

from jinja2 import Template 
from folium.map import Layer
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))

#Class to have single controller for all layers
class HeatMapWithTimeAdditional(Layer):
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
                 overlay=False, control=True, show=True):
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
                 #self.gradient = gradient
                 
if not os.path.isdir("./static"):  # just for this example
    os.makedirs("./static")

app = Flask(__name__)

@app.route('/map', methods=['GET'])
def mymap():
    token = request.args.get("token")
    # print("=== token", token)
    filename = "static/Italy" + token + ".html"

    if token == 'init' or not os.path.exists(filename):
        filename = "static/Italyinit.html"
    # print("=== filename", filename)

    html = ''
    with open(filename, 'r') as f:
        html = f.read()
    if token != 'init' and os.path.exists(filename):
        os.remove(filename)
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    Primary_Image = ''
    Political = ''
    Biblical0 = ''
    Suffering0 = ''
    Affection0 = ''
    Dedication0 = ''
    Devotion0 = ''

    if request.method == 'POST':
        query = str(request.form.get('query'))
        arr_query = query.split(',')
        # print(query)
        try:
            file = request.files['file']
            fname = secure_filename(file.filename)
            file.save('static/' + fname)
            # print("=== file saved: ", fname)
        except:
            fname = 'data_new.csv'
            # print("=== filename:", fname)
        df_incidents = pd.read_csv('static/' + fname)
        df_incidents.rename(columns={"Primary Image": "Primary_Image","Century of Origin": "Century_of_Origin","Active Devotion Y = 1 ; N = 0":"Active_Devotion","Overt Political: 0=no; 1=communal; 2=Papal":"Overt_Political","Has suffering? Y=1, N=0":"Has_Suffering","Has affection? Y=1, N=0 (based on interaction of members in the shrines themselves, not towards the audience/viewer)":"Has_Affection","Not Biblical = 0 Biblical = 1; ":"Has_Biblical"},inplace=True)
        # print("df_incidents===", df_incidents)

        df_filtered=df_incidents.copy()
        if arr_query[0]!='':
            Primary_Image = arr_query[0]
            df_filtered=df_filtered[df_filtered['Primary_Image']==int(arr_query[0])]
        if arr_query[1]!='':
            Political = arr_query[1]
            df_filtered=df_filtered[df_filtered['Overt_Political']==int(arr_query[1])]
        if arr_query[2]!='':
            Biblical0 = arr_query[2]
            df_filtered=df_filtered[df_filtered['Has_Biblical']==int(arr_query[2])]
        if arr_query[3]!='':
            Suffering0 = arr_query[3]
            df_filtered=df_filtered[df_filtered['Has_Suffering']==int(arr_query[3])]
        if arr_query[4]!='':
            Affection0 = arr_query[4]
            df_filtered=df_filtered[df_filtered['Has_Affection']==int(arr_query[4])]
        if arr_query[5]!='':
            Dedication0 = arr_query[5]
            df_filtered=df_filtered[df_filtered['Dedication']==int(arr_query[5])]
        if arr_query[6]!='':
            Devotion0 = arr_query[6]
            df_filtered=df_filtered[df_filtered['Active_Devotion']==int(arr_query[6])]

        df_incidents_cp=df_incidents.copy()

        # print("length: ", len(df_filtered))
        # print(df_filtered.head())
        df_incidents=df_filtered.copy()
        #df_incidents = pd.read_csv('data.csv')
        #print('Dataset downloaded and read into a pandas dataframe!')
        #df_incidents.head()
        Italy_map = folium.Map(location=[41.9028, 12.4964], zoom_start=13,tiles='cartodbpositron')
        fg = folium.map.FeatureGroup()
        #converting latitude and longitude to float values
        df_incidents.Longitude=df_incidents.Longitude.astype(float)
        df_incidents.Latitude=df_incidents.Latitude.astype(float)
        # loop through the 100 crimes and add each to the incidents feature group
        # add incidents to map of Italy


        #base_map = generateBaseMap(default_zoom_start=11)
        df_century_list = []
        for century in df_incidents.Century_of_Origin.sort_values().unique():
            df_century_list.append(df_incidents.loc[df_incidents.Century_of_Origin==century,['Latitude','Longitude']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist())
        df_century_list


        centuries=[]
        centuries=df_incidents.Century_of_Origin.sort_values().unique()
        centuries=list(centuries)
        # print("centuries", centuries)

        HeatMapWithTime(df_century_list,  show=True,radius=15, index=centuries, position='topright', name='Query Output',control=True).add_to(Italy_map)
        #HeatMapWithTime(df_century_list, radius=5, gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(Italy_map)
        #HeatMapWithTime(df_century_list,  radius=15, index=centuries, position='bottomright', name='Century_Of_Origin',control=True).add_to(Italy_map)

        #Identifying centers of churchs in each century

        df_century_centers=[]
        sumx=0
        sumy=0
        meanx=0
        meany=0
        for century in df_century_list:
            for loc in century:
                sumx=sumx+loc[0]
                sumy=sumy+loc[1]
                #print(len(century))
                meanx=round(sumx/len(century),6)
                meany=round(sumy/len(century),6)
            df_century_centers.append([[meanx,meany]])
            sumx=0
            sumy=0
            meanx=0
            meany=0
        # print("df_century_centers", df_century_centers)
        #folium.TileLayer('Stamen Terrain').add_to(Italy_map)
        #folium.TileLayer('Stamen Toner').add_to(Italy_map)
        #folium.TileLayer('stamenwatercolor').add_to(Italy_map)
        #folium.TileLayer('cartodbpositron').add_to(Italy_map)
        #folium.TileLayer('cartodbdark_matter').add_to(Italy_map)


        #HeatMapWithTime(df_century_list,overlay=False,name='data',index=centuries,min_opacity=0.05,radius=20,min_speed=0.1,speed_step=0.1,max_speed=1,max_opacity=1,control=True).add_to(Italy_map)

        # HeatMapWithTime(df_century_centers, show=True, radius=15, index=centuries, position='bottomright', name='Centers',control=True,gradient={1: 'blue',0.1:'lime'}).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_centers,name='Centers',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_list,overlay=False,name='data1',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_centers,overlay=False,name='data2',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)


        #Adding various tiles to our map
        # folium.LayerControl().add_to(Italy_map)

        Italy_map.save("Temp.html")

        #To always use stable v1.1.0 of github HeatMapWithTime
        token = str(int(time.time()))
        new_filename = "static/Italy" + token + ".html"
        new_file= open(new_filename, "w")
        F = open("Temp.html","r")
        for i in F:
            #print(F.readline())
            if("https://rawcdn.githack.com/socib/Leaflet.TimeDimension/master/dist/leaflet.timedimension.min.js" in i):
                # print(i)
                new_file.write(i.replace("https://rawcdn.githack.com/socib/Leaflet.TimeDimension/master/dist/leaflet.timedimension.min.js","https://rawcdn.githack.com/socib/Leaflet.TimeDimension/v1.1.0/dist/leaflet.timedimension.min.js"))
            else:
                new_file.write(i)
        new_file.close()
        F.close()
        # do the processing here and save the new file in static/
        fname_after_processing = "Italy.html"
        time.sleep(3)
        return jsonify({'result_image_location': token})

    return render_template('index.html')


app.run(debug=True)