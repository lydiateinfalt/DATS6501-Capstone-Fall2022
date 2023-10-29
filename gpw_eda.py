import os
import geopandas as gpd
import rasterio
import GOSTRocks.rasterMisc as rMisc
import src.UrbanRaster as urban
import src.urban_helper as helper
import rioxarray
from rasterio import features
from xrspatial.zonal import stats
import numpy as np
import pandas as pd



#Gridded Population of the World (GPW), v4 https://sedac.ciesin.columbia.edu/data/collection/gpw-v4
adm0 = "Administrative Unit Data/pak_admbnda_adm0_ocha_pco_gaul_20181218.shp"
adm1 = "Administrative Unit Data/pak_admbnda_adm1_ocha_pco_gaul_20181218.shp"
adm2 = "Administrative Unit Data/pak_admbnda_adm2_ocha_pco_gaul_20181218.shp"
adm3 = "Administrative Unit Data/pak_admbnda_adm3_ocha_pco_gaul_20181218.shp"
adm_shapes = [adm0, adm1, adm2, adm3]
adm_dict = {"Administrative Unit Data/pak_admbnda_adm0_ocha_pco_gaul_20181218.shp": 'ADM0',
            "Administrative Unit Data/pak_admbnda_adm1_ocha_pco_gaul_20181218.shp":'ADM1',
            "Administrative Unit Data/pak_admbnda_adm2_ocha_pco_gaul_20181218.shp": 'ADM2',
            "Administrative Unit Data/pak_admbnda_adm3_ocha_pco_gaul_20181218.shp": 'ADM3'}
inAOI = gpd.read_file(adm0)
output_dir = "gpw/output"
aoi_pop = os.path.join(output_dir, "2015_PAK_GPW_POP.tif")
iso3 = 'pak'

if not os.path.exists(aoi_pop):
    global_pop = "gpw/gpw_v4_population_count_adjusted_to_2015_unwpp_country_totals_rev11_2015_30_sec.tif"
    inR = rasterio.open(global_pop)
    inAOI = inAOI.to_crs(inR.crs)
    rMisc.clipRaster(rasterio.open(global_pop), inAOI, aoi_pop)

def total_pop_calc(aoi_raster, aoi_vector):
    inP = rasterio.open(aoi_raster)
    if aoi_vector.crs != inP.crs:
        aoi_vector = aoi_vector.to_crs(inP)
    out_meta = inP.meta
    inP = inP.read()
    inP = inP * (inP > 0)
    total_pop = inP.sum()
    print(total_pop)
    return total_pop

total_pop = total_pop_calc(aoi_pop, inAOI)
print("Total Population for adm0= " + str(total_pop))

# calculate urban
inPop = rasterio.open(aoi_pop)
urban_calculator = urban.urbanGriddedPop(inPop)
urban_calculator.calculateUrban

file_nm = "2015_pak_gpw"
urban_raster = os.path.join(output_dir, file_nm + "_urban.tif")

if not os.path.exists(urban_raster):
    urban_extents = urban_calculator.calculateUrban(densVal=300, totalPopThresh=5000,
                                                smooth=False, queen=False,raster_pop= urban_raster ,verbose=True)
    out_urban = os.path.join(output_dir, file_nm + "_urban.geojson")
    urban_extents.to_file(out_urban, driver="GeoJSON")
    out_urban_csv = os.path.join(output_dir, file_nm + ".csv")
    urban_extents.to_csv(out_urban_csv)

hd_urban_raster = os.path.join(output_dir, file_nm + "_hdurban.tif")
if not os.path.exists(hd_urban_raster):
    hd_urban_extents = urban_calculator.calculateUrban(densVal=1500, totalPopThresh=50000,
                                                   smooth=True, queen=True,raster_pop = hd_urban_raster,verbose=True)
    out_hd_urban = os.path.join(output_dir, file_nm + "_hdurban.geojson")
    hd_urban_extents.to_file(out_hd_urban, driver="GeoJSON")
    out_hd_urban_csv = os.path.join(output_dir, file_nm + ".csv")
    hd_urban_extents.to_csv(out_hd_urban_csv)

urban_total_pop = total_pop_calc(urban_raster, inAOI)
hd_urban_total_pop= total_pop_calc(hd_urban_raster, inAOI)
print("Total Population for urban raster= " + urban_total_pop.astype(str))
print("Total Population for hd urban raster= " + hd_urban_total_pop.astype(str))

#Requires rasterizing of shape files
def zonal_stats_calc(inRasters, inShapes):
    final = pd.DataFrame()
    for vector in inShapes:
        adm = adm_dict[vector]
        adm_en = adm.upper() + "_EN"
        adm_code = adm.upper() + "_PCODE"
        inA_out = gpd.read_file(vector)
        df_zones = inA_out[["Shape_Area", adm_code, adm_en]]
        shape = gpd.read_file(vector)

        for raster in inRasters:
            raster = rioxarray.open_rasterio(raster).squeeze()
            shape_utm = shape.to_crs(raster.rio.crs)
            geom = shape_utm[['geometry', "Shape_Area"]].values.tolist()
            fields_rasterized = features.rasterize(geom, out_shape=raster.shape, transform=raster.rio.transform())
            fields_rasterized_xarr = raster.copy()
            fields_rasterized_xarr.data = fields_rasterized

            results = stats(fields_rasterized_xarr, raster, stats_funcs=['sum'])

            df_zones = df_zones.copy()
            df_zones['Shape_Area'] = df_zones['Shape_Area'].astype(np.float32)
            df_zones = pd.merge(df_zones, results, how="left", left_on='Shape_Area', right_on='zone')
            df_zones = df_zones[df_zones.columns.drop(list(df_zones.filter(regex='zone')))]

            if ('sum_x' in df_zones.columns) or ('sum_y' in df_zones.columns):
                df_zones.rename(columns={'sum_x': 'urban_sum', 'sum_y':'hd_urban_sum'}, inplace=True)
        output_filenm = os.path.join(output_dir, 'pak_2015_gpw_' + adm +'.csv')
        df_zones.to_csv(output_filenm)

rasters = [urban_raster, hd_urban_raster]
zonal_stats_calc(rasters, adm_shapes)

def calculate_urban:

    xx = helper.urban_country(iso3, output_folder, inD, pop_files,
                              final_folder="FINAL_STANDARD_1KM", ghspop_suffix="1k")
    adm2_res = os.path.join(xx.final_folder, "URBAN_ADMIN2_STATS_COMPILED.csv")
    ea_res = os.path.join(xx.final_folder, "URBAN_COMMUNE_STATS_COMPILED.csv")
    print(f"{iso3} ***1k Extracting Global Layers")
    xx.extract_layers(global_landcover, global_ghspop, global_ghspop_1k, global_ghbuilt, ghsl_vrt, ghs_smod)
    print(f"{iso3} ***1k Downloading and processing elevation")
    xx.process_dem(global_dem=global_dem_1k)
    print(f"{iso3} ***1k Standardizing rasters")
    xx.standardize_rasters(include_ghsl_h20)
    print(f"{iso3} ***1k Calculating Urban")
    xx.calculate_urban()
    print(f"{iso3} ***1k Calculating Zonal admin2")
    if not os.path.exists(admin2_1k_stats):
        zonal_adm2 = xx.pop_zonal_admin(inD2)
        zonal_adm2.to_csv(admin2_1k_stats)
        tPrint(f"{iso3} ***1k Calculating Zonal communes")
        if os.path.exists(ea_file):
            inEA = gpd.read_file(ea_file)
            zonal_ea = xx.pop_zonal_admin(inEA)
            zonal_ea.to_csv(commune_1k_stats)
    if evaluate:
        tPrint(f"{iso3} ***1k Evaluating Data")
        xx.evaluateOutput(admin2_1k_stats, commune_1k_stats)










