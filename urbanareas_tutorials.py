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
global_acronym = 'pak'
#pop_data_dir = ['FINAL_STANDARD', 'FINAL_STANDARD_1KM']
pop_data_dir = ['FINAL_STANDARD_1KM']
#pop_data_src = ['gpo', 'upo15']
pop_data_src = ['gpo']
shape_fn_keys = ['adm2_ocha']

def element_in_common(l1, l2):
    '''
    Function that takes two lists and returns same (or True) if they have at least one.
    '''
    m = len(l1)
    n = len(l2)
    index = -99
    for i in range (0, m):
        if l1[i] in l2:
            index = i
    return index


def urban_areas(acronym, aoi, pop):
    # Define input population raster
    aoi_file = aoi
    pop_file = pop
    ur_acro = pop.split('.')
    if "_1KM" in ur_acro[0]:
        acronym = acronym + "1k"

    shape_fn = os.path.basename(aoi)
    index = element_in_common(shape_fn_keys, shape_fn)
    if index < 0:
        return
    if index >= 0:
        aoi_acro = shape_fn_keys[index]

    output_folder = os.path.join(os.path.dirname(pop), 'OUTPUT')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pop_fn= os.path.basename(pop)
    pop_fn = pop_fn.rstrip()
    pop_index = element_in_common(pop_data_src, pop_fn)
    if pop_index >= 0:
        pop_acro = pop_data_src[pop_index]
    if pop_index < 0:
        return

    urban_common_fn = acronym + '_' + aoi_acro + '_' + pop_acro + "_urban"
    hd_urban_common_fn = acronym +'_' + aoi_acro + '_' + pop_acro + "_hd_urban"

    print("Processing " + aoi_file)
    inAOI = gpd.read_file(aoi_file)

    # Shouldn't need to execute this unless you change your AOI
    if not os.path.exists(pop_file):
        sys.path.append("../../../gostrocks/src")
        import GOSTRocks.rasterMisc as rMisc
        global_population = "data/ppp_2020_1km_Aggregated.tif"
        inR = rasterio.open(global_population)
        rMisc.clipRaster(inR, inAOI, pop_file)

    print("Processing " + pop_file)
    inR = rasterio.open(pop_file)

    # calculate urban
    urban_calculator = urban.urbanGriddedPop(inR)
    urban_calculator.calculateUrban


    urban_extents = urban_calculator.calculateUrban(densVal=300, totalPopThresh=5000,
                                                   smooth=False, queen=False,raster_pop= ur_acro[0] + '_urban.tif',
                                                   verbose=True)

    hd_urban_extents = urban_calculator.calculateUrban(densVal=1500, totalPopThresh=50000,
                                                   smooth=True, queen=True,raster_pop = ur_acro[0] + '_hdurban.tif',
                                                   verbose=True)


    out_urban = os.path.join(output_folder, urban_common_fn + ".geojson")
    out_hd_urban = os.path.join(output_folder, hd_urban_common_fn +".geojson")
    urban_extents.to_file(out_urban, driver="GeoJSON")
    hd_urban_extents.to_file(out_hd_urban, driver="GeoJSON")

    #Create shape files
    out_urban_shp = os.path.join(output_folder, urban_common_fn + ".shp")
    out_hd_urban_shp = os.path.join(output_folder, hd_urban_common_fn + ".shp")

    urban_extents.to_file(out_urban_shp)
    hd_urban_extents.to_file(out_hd_urban_shp)

    out_urban_csv = os.path.join(output_folder, urban_common_fn + ".csv")
    out_hd_urban_csv = os.path.join(output_folder, hd_urban_common_fn + ".csv")

    urban_extents.to_csv(out_urban_csv)
    hd_urban_extents.to_csv(out_hd_urban_csv)


#Compile a list of administrative unit shapes
data_dir = 'data'
admin_shapes_dir = 'Administrative Unit Data'
os.chdir(data_dir)
os.chdir(admin_shapes_dir)
pak_admin_shapes = []
for file in os.listdir():
     if os.path.isfile(file) and file.startswith("pak_admbnda_") and file.endswith(".shp"):
         pak_admin_shapes.append(os.path.join(os.getcwd(), file))



pop_filenames = []
os.chdir("..")
for dir in pop_data_dir:
    os.chdir(dir)
    current_dir = os.getcwd()
    filename = os.listdir(current_dir)

    for file in filename:
        if os.path.isfile(file) and file.startswith(global_acronym) and (file.endswith("gpo.tif") or file.endswith("upo15.tif")):
            pop_filenames.append(os.path.join(current_dir, file))
    os.chdir("..")

print("list of administrative shape files")
print(pak_admin_shapes)

print("list of population files")
print(pop_filenames)


for i in pop_filenames:
    for j in pak_admin_shapes:
        urban_areas(global_acronym, j, i)










