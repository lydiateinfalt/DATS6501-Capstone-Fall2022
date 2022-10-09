# -*- coding: utf-8 -*-
"""GOST_Urban_Viz.ipynb
"""

import geopandas as gpd
import geojson
import matplotlib.pyplot as plt
import folium
import sys
from folium import GeoJson


urban_extent = gpd.read_file("data/Output/punjab_pak1kurban_extents.geojson")

print(urban_extent.crs)
print(urban_extent['geometry'][2])
urban_extent = urban_extent.to_crs(epsg=4326)
print(urban_extent.crs)
print(urban_extent.head())
urban_extent.plot(figsize=(6, 6))
plt.grid()
plt.show()

map = folium.Map(location=[25.894302, 68.524715], zoom_start=7,tiles='CartoDB Dark_Matter')

for _, r in urban_extent.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['ID']).add_to(geo_j)
    geo_j.add_to(map)


sindh_tehsil =r"data/Punjab.geojson"
file = open(sindh_tehsil, encoding="utf8")
text = file.read()
# GeoJson(text).add_to(map)
map.save('punjab_urban_map.html')

hd_urban = gpd.read_file("data/Output/punjab_pak1khd_urban_extents.geojson")
print(hd_urban.crs)
hd_urban.head()
hd_urban = hd_urban.to_crs(epsg=4326)
hd_urban.plot(figsize=(6, 6))
plt.grid()
plt.show()

hd_urban.head()

hd_urban_map = folium.Map(location=[25.894302, 68.524715],zoom_start=7, tiles='CartoDB Dark_Matter')
for _, r in hd_urban.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'red'})
    folium.Popup(r['ID']).add_to(geo_j)
    geo_j.add_to(hd_urban_map)

# GeoJson(text).add_to(hd_urban_map)
hd_urban_map.save('punjab_hd_urban_map.html')