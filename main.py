from flask import Flask, render_template_string, request, jsonify, url_for
import os
import pandas as pd
import folium
from folium.plugins import HeatMapWithTime
from folium.plugins import MarkerCluster

from jinja2 import Template 
from folium.map import Layer
from werkzeug.utils import secure_filename
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
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        query = str(request.form.get('query'))
        arr_query=query.split(',')
        print(arr_query)
        fname = secure_filename(file.filename)
        file.save('static/' + fname)
        df_incidents = pd.read_csv('static/' + fname)
        df_incidents.rename(columns={"Primary Image": "Primary_Image","Century of Origin": "Century_of_Origin","Active Devotion Y = 1 ; N = 0":"Active_Devotion","Overt Political: 0=no; 1=communal; 2=Papal":"Overt_Political","Has suffering? Y=1, N=0":"Has_Suffering","Has affection? Y=1, N=0 (based on interaction of members in the shrines themselves, not towards the audience/viewer)":"Has_Affection","Not Biblical = 0 Biblical = 1; ":"Has_Biblical"},inplace=True)
        df_filtered=df_incidents.copy()
        if arr_query[0]!='':
            df_filtered=df_filtered[df_incidents['Primary_Image']==int(arr_query[0])]
        if arr_query[1]!='':
             df_filtered=df_filtered[df_incidents['Overt_Political']==int(arr_query[1])]
        if arr_query[2]!='':    
             df_filtered=df_filtered[df_incidents['Has_Biblical']==int(arr_query[2])]
        if arr_query[3]!='':      
             df_filtered=df_filtered[df_incidents['Has_Suffering']==int(arr_query[3])]
        if arr_query[4]!='':      
             df_filtered=df_filtered[df_incidents['Has_Affection']==int(arr_query[4])]
        if arr_query[5]!='':      
             df_filtered=df_filtered[df_incidents['Dedication']==int(arr_query[5])]
        if arr_query[6]!='':       
             df_filtered=df_filtered[df_incidents['Active_Devotion']==int(arr_query[6])]
        print(len(df_filtered))
        df_incidents_cp=df_incidents.copy()
        df_incidents=df_filtered.copy()
        #df_incidents = pd.read_csv('data.csv')
        #print('Dataset downloaded and read into a pandas dataframe!')
        #df_incidents.head()
        Italy_map = folium.Map(location=[41.9028, 12.4964], zoom_start=13,tiles='cartodbdark_matter')
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
        print(centuries)
        
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
        print(df_century_centers)
        #folium.TileLayer('Stamen Terrain').add_to(Italy_map)
        #folium.TileLayer('Stamen Toner').add_to(Italy_map)
        #folium.TileLayer('stamenwatercolor').add_to(Italy_map)
        #folium.TileLayer('cartodbpositron').add_to(Italy_map)
        #folium.TileLayer('cartodbdark_matter').add_to(Italy_map)
        
        
        #HeatMapWithTime(df_century_list,overlay=False,name='data',index=centuries,min_opacity=0.05,radius=20,min_speed=0.1,speed_step=0.1,max_speed=1,max_opacity=1,control=True).add_to(Italy_map)
        
        HeatMapWithTime(df_century_centers, show=True, radius=15, index=centuries, position='bottomright', name='Centers',control=True,gradient={1: 'blue',0.1:'lime'}).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_centers,name='Centers',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_list,overlay=False,name='data1',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)
        #HeatMapWithTimeAdditional(df_century_centers,overlay=False,name='data2',min_opacity=0.05,radius=20,max_opacity=1,control=True).add_to(Italy_map)

       


        
        #Adding various tiles to our map
        
        
        
        folium.LayerControl().add_to(Italy_map)
        
        Italy_map.save("Temp.html")
        
        #To always use stable v1.1.0 of github HeatMapWithTime 
        new_file= open("static/Italy.html","w+")
        F = open("Temp.html","r") 
        for i in F:
            #print(F.readline())
            if("https://rawcdn.githack.com/socib/Leaflet.TimeDimension/master/dist/leaflet.timedimension.min.js" in i):
                print(i)
                new_file.write(i.replace("https://rawcdn.githack.com/socib/Leaflet.TimeDimension/master/dist/leaflet.timedimension.min.js","https://rawcdn.githack.com/socib/Leaflet.TimeDimension/v1.1.0/dist/leaflet.timedimension.min.js"))
            else:
                new_file.write(i)
        new_file.close()
        F.close()
        # do the processing here and save the new file in static/
        fname_after_processing = "Italy.html"
        import time
        time.sleep(6) 
        return jsonify({'result_image_location': url_for('static', filename=fname_after_processing)}) 
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Title</title>
    <style>
         html {
          background-color: #333;
          font-family: Optima;
      }

      h1 {
          font-family: cursive;
      }
        body {
            display: flex;
            flex-flow: column;
            max-width: 800px;
            margin: auto;
            box-shadow: 0 0 5px 0 black;
            padding: 10px 40px;
            box-shadow: 0 0 5px 0 black;
            background: white;
        }
       
    </style>
</head>
<body>
    <h1>Church Distribution</h1>
<div>
<form enctype="multipart/form-data" method="post" name="fileinfo">
  <label>File to upload:</label>
  <input type="file" name="file" value="data.csv" required /><br>
  <input type="text" name="query" id="query" value = ',,,,,,' required />
  <label>Please Type the query here</label><br>
  <label> Query Format[Primary Image[1-9],Overt Political[0-2],Biblical[0/1],Has Suffering[0/1],Has Affection[0/1],Dedication[0/1],Active Devotion[0/1]]:</label><br>
  <input type="submit" value="Upload the file!" />
</form>
</div>
<div id="resultimg">
</div>
<div style="background-color:white;position: fixed; bottom: 50px; left: 50px; width: 300px; height: 100px;border:2px solid grey; z-index:9999; font-size:14px;">&nbsp; Top Controller Enables of Data of given query <br>&nbsp; Bottom Controller can be used to view the centers per century<br>&nbsp;Blue spots are centers;</font></div>

<script>
var form = document.forms.namedItem("fileinfo");
form.addEventListener('submit', function(ev) {
  var oData = new FormData(form);
  var oReq = new XMLHttpRequest();
  oReq.open("POST", "{{url_for('index')}}", true);
  oReq.onload = function(oEvent) {
    if (oReq.status == 200) {
       document.getElementById('resultimg').innerHTML='<iframe height="1100px" width="720px" src="'+JSON.parse(oReq.responseText).result_image_location+'"></iframe>';
    } else {
      alert("Error " + oReq.status + " occurred when trying to upload your file")
    }
  };
  console.log(form)
  oReq.send(oData);
  ev.preventDefault();
}, false);
</script>
</body>
</html>
''')


app.run(debug=True)
