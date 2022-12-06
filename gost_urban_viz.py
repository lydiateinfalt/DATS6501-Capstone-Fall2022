# -*- coding: utf-8 -*-
"""GOST_Urban_Viz.ipynb
"""

import geopandas as gpd
import geojson
import matplotlib.pyplot as plt
import folium
import fiona


urban_extent = gpd.read_file("dartboard/Delineations/pak1k_gpod3b3000_ur.tif")
urban_extent = urban_extent.to_crs(epsg=4326)
urban_extent.plot(aspect='equal', figsize=(12, 12))
plt.grid()
plt.show()

map = folium.Map(location=[33.72, 73.06], zoom_start=5,tiles='CartoDB Dark_Matter')

#
for _, r in urban_extent.iterrows():
     sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
     geo_j = sim_geo.to_json()
     geo_j = folium.GeoJson(data=geo_j,
                            style_function=lambda x: {'fillColor': 'orange'})
     folium.Popup(r['ID']).add_to(geo_j)
     geo_j.add_to(map)

map.save('pak_gpo_urban_areas.html')

hd_urban = gpd.read_file("dartboard/Delineations/gpo/pak_gpod10b3000_co.tif")
print(hd_urban.crs)
hd_urban.plot(aspect=1)
hd_urban = hd_urban.to_crs(epsg=4326)
hd_urban.plot(aspect = 'equal', figsize=(12, 12))
plt.grid()
plt.show()


hd_urban_map = folium.Map(location=[33.72, 73.06],zoom_start=5, tiles='CartoDB Dark_Matter')
for _, r in hd_urban.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'red'})
    folium.Popup(r['ID']).add_to(geo_j)
    geo_j.add_to(hd_urban_map)

# GeoJson(text).add_to(hd_urban_map)
hd_urban_map.save('pak_gpo_cities.html')