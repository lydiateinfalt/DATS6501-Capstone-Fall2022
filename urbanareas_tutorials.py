# -*- coding: utf-8 -*-

# pip install gdal
# pip install geopandas
# pip install rasterio
# pip install geojson
# pip install json
# pip install GOSTRocks


import geopandas as gpd
import rasterio
import sys, os, importlib
import rasterio
import src.UrbanRaster as urban


sys.path.append("../../")

# Define input population raster
output_folder = "data/Output"
data_folder = "data"
acronym = 'pak_pd2015_'
aoi_file = os.path.join(data_folder + "/Administrative Unit Data/", "pak_adm.shp")
pop_file = os.path.join(data_folder + "/FINAL_STANDARD_1KM/", "pak_pd_2015_1km.tif")

inAOI = gpd.read_file(aoi_file)

# Shouldn't need to execute this unless you change your AOI
if not os.path.exists(pop_file):
    sys.path.append("../../../gostrocks/src")
    import GOSTRocks.rasterMisc as rMisc
    global_population = "data/ppp_2020_1km_Aggregated.tif"
    inR = rasterio.open(global_population)
    rMisc.clipRaster(inR, inAOI, pop_file)
    
inR = rasterio.open(pop_file)

# calculate urban
urban_calculator = urban.urbanGriddedPop(inR)
urban_calculator.calculateUrban

urban_extents = urban_calculator.calculateUrban(densVal=300, totalPopThresh=5000, 
                                               smooth=False, queen=False,raster_pop='data/' + acronym + 'urban.tif',
                                               verbose=True)

hd_urban_extents = urban_calculator.calculateUrban(densVal=1500, totalPopThresh=50000,
                                               smooth=True, queen=True,raster_pop ='data/' + acronym + 'hdurban.tif',
                                               verbose=True)

output_folder = "data/Output"
out_urban = os.path.join(output_folder, acronym + "urban_extents.geojson")
out_hd_urban = os.path.join(output_folder, acronym +"hd_urban_extents.geojson")

urban_extents.to_file(out_urban, driver="GeoJSON")
hd_urban_extents.to_file(out_hd_urban, driver="GeoJSON")

out_urban = os.path.join(output_folder, acronym + "urban_extents.tif")
out_hd_urban = os.path.join(output_folder, acronym +"hd_urban_extents.tif")



