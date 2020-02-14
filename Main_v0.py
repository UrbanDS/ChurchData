from flask import Flask, render_template_string, request, jsonify, url_for
import os
import pandas as pd
import folium
from folium.plugins import HeatMapWithTime
from werkzeug.utils import secure_filename
if not os.path.isdir("/static"):  # just for this example
    os.makedirs("/static")

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save('static/' + fname)
        df_incidents = pd.read_csv('static/' + fname)
        #df_incidents = pd.read_csv('data.csv')
        #print('Dataset downloaded and read into a pandas dataframe!')
        #df_incidents.head()
        Italy_map = folium.Map(location=[41.9028, 12.4964], zoom_start=13)
        incidents = folium.map.FeatureGroup()
        #converting latitude and longitude to float values
        df_incidents.Longitude=df_incidents.Longitude.astype(float)
        df_incidents.Latitude=df_incidents.Latitude.astype(float)
        # loop through the 100 crimes and add each to the incidents feature group
        # add incidents to map of Italy
        Italy_map.add_child(incidents)
        #base_map = generateBaseMap(default_zoom_start=11)
        df_century_list = []
        for century in df_incidents.Century_of_Origin.sort_values().unique():
            df_century_list.append(df_incidents.loc[df_incidents.Century_of_Origin==century,['Latitude','Longitude']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist())
            #df_century_list
            centuries=[]
            centuries=df_incidents.Century_of_Origin.sort_values().unique()
            centuries=list(centuries)
            #centuries
            
        Italy_map.add_child(HeatMapWithTime(df_century_list,  radius=15, index=centuries, position='topright', name='CO2 (micro-atm)',control=True))
        Italy_map.add_child(folium.LayerControl())
        Italy_map.save("static/Italy.html")
        # do the processing here and save the new file in static/
        fname_after_processing = "Italy.html"
        return jsonify({'result_image_location': url_for('static', filename=fname_after_processing)}) 
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>title</title>
</head>
<body>
<div>
<form enctype="multipart/form-data" method="post" name="fileinfo">
  <label>Some user provided information</label>
  <input type="text" name="some_info" size="12" maxlength="32" /><br />
  <label>File to upload:</label>
  <input type="file" name="file" required />
  <input type="submit" value="Upload the file!" />
</form>
</div>
<div id="resultimg">
</div>
<script>
var form = document.forms.namedItem("fileinfo");
form.addEventListener('submit', function(ev) {
  var oData = new FormData(form);
  var oReq = new XMLHttpRequest();
  oReq.open("POST", "{{url_for('index')}}", true);
  oReq.onload = function(oEvent) {
    if (oReq.status == 200) {
       document.getElementById('resultimg').innerHTML='<iframe height="700" width="1500" src="'+JSON.parse(oReq.responseText).result_image_location+'"></iframe>';
    } else {
      alert("Error " + oReq.status + " occurred when trying to upload your file")
    }
  };
  oReq.send(oData);
  ev.preventDefault();
}, false);
</script>
</body>
</html>
''')


app.run(debug=True)
