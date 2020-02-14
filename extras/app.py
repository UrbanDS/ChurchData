from flask import Flask, render_template, jsonify
import pandas as pd 
import folium 
app = Flask(__name__)
@app.route('/')
def foo():
    return render_template("index.html")
 
@app.route('/get_word')
def languages():
    '''Return data in json format'''
    df_incidents = pd.read_csv('data.csv')
    print('Dataset downloaded and read into a pandas dataframe!')
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
        #df_century_list
        centuries=[]
        centuries=df_incidents.Century_of_Origin.sort_values().unique()
        centuries=list(centuries)
        centuries
        HeatMapWithTime(df_century_list,  radius=15, index=centuries, position='topright', name='CO2 (micro-atm)',control=True).add_to(Italy_map)
        Italy_map.save("Italy.html")
        #lst = ["Python", 'HTML', 'JavaScript', 'CSS']
    #words = {}
    #words['choice'] = random.choice(lst)
    return jsonify(Italy_map)
 
if __name__ == '__main__':
    app.run(debug=True)