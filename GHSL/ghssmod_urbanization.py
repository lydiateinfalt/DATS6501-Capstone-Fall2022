#Author: Lydia Teinfalt
#Last updated date: 06/05/2023
##Data downloaded from https://ghsl.jrc.ec.europa.eu/download.php?ds=pop

import geopandas as gpd
import pandas as pd
import os
import rasterio
import GOSTRocks.rasterMisc as rMisc
from rasterio import features
import numpy as  np
from xrspatial import zonal_stats
import rioxarray


smod_vals = [10, 11, 12, 13, 21, 22, 23, 30]
#years = ["2000", "1995", "1990", "1985", "1980"]
years = ["2010"]
#read input files
iso3 = 'PAK'
shortnm = 'adm0'
adm0 = ''
homedir = os.getcwd()


for year in years:
    ghssmod_file = year + "_" + "GHS" + "_" + iso3 + "_" + "SMOD" + '.tif'
    shape_file = "pak_admbnda_adm0_ocha_pco_gaul_20181218.shp"
    aoi_pop = year + "_" + "GHS" + "_" + iso3 + "_" + "POP" + '.tif'
    outdir = os.path.join(homedir, year)

    def urban_cal(year, adm, inA, smod_file, pop_file, inRaster):
        final = pd.Series(dtype=float)
        stats = {}
        shape_areas =[]
        inRaster = os.path.join(outdir, inRaster)
        xpop = rioxarray.open_rasterio(inRaster).squeeze()
        inA_mw = gpd.read_file(inA)
        #smod_pop = rioxarray.open_rasterio(out_name).squeeze()
        inA_mw = gpd.read_file(inA)

        adm_en = adm.upper() + "_EN"
        adm_code = adm.upper() + "_PCODE"
        inA_out = inA_mw.to_crs(xpop.rio.crs)
        df_zones = inA_out[["Shape_Area", adm_code, adm_en]]
        geom = inA_out[['geometry', "Shape_Area"]].values.tolist()

        for val in smod_vals:
            cur_smod = (smod_file == val).astype(int)
            #smod = (smod_file == val)*pop_file
            cur_pop = pop_file * cur_smod
            total_curpop = cur_pop.sum()
            perUrban = (total_curpop.sum() / total_pop * 100)

            out_name = year + "_" + iso3 + "_" + str(val)+ "_smod_pop.tif"

            with rasterio.open(out_name, 'w', **out_meta) as out_urban:
                out_urban.write(cur_pop)

            # Zonal Statistics, reference: https://carpentries-incubator.github.io/geospatial-python/10-zonal-statistics/index.html
            smod_pop = rioxarray.open_rasterio(out_name).squeeze()

            fields_rasterized = features.rasterize(geom, out_shape=smod_pop.shape, transform=smod_pop.rio.transform())
            fields_rasterized_xarr = smod_pop.copy()
            fields_rasterized_xarr.data = fields_rasterized

            results= zonal_stats(fields_rasterized_xarr, smod_pop, stats_funcs=['sum'])
            #res = rMisc.zonalStats(inA, out_name, minVal=0)
            #res = pd.DataFrame(res, columns=["%s_%s_%s" % (x, year + "_" + adm, val) for x in ['SUM', 'MIN', 'MAX', 'MEAN']])
            #res = pd.DataFrame(res, columns=["%s_%s_%s" % (x, year + "_" + adm, val) for x in ['SUM']])
            df1 = [df_zones,results]
            df_zones['Shape_Area'] = df_zones['Shape_Area'].astype(np.float32)
            #results['zone'] = results['zone'].astype(np.float64)
            print(df_zones.dtypes)
            print(results.dtypes)
            results = results.rename(columns={'sum': 'sum_'+ str(val) } )
            final =pd.merge(df_zones, results, how="left", left_on='Shape_Area', right_on='zone')
            df_zones = final
            df_zones = df_zones.rename(columns={'zone': 'zone_' + str(val)})
            df_zones = df_zones[df_zones.columns.drop(list(df_zones.filter(regex='zone')))]
            print(final)

            #try:
            #    final = final.join(stat)
            #except:
            #    final = stat
        final_stats = pd.DataFrame(stats)
        final_df = [df_zones, final_stats]
        final = pd.concat(final_df, axis = 1)

        output_file = os.path.join(outdir, year + "_" + iso3 + "_" + adm + ".csv")

        final.to_csv(os.path.join(output_file))


    def find_country_shapefile(year):
        shape_files = os.listdir()
        adm0 = ""
        for files in shape_files:
            if (files.endswith(".shp")) & ("adm0" in files):
                adm0 = files
                break
        return adm0

    def find_global_file_location(year, type):
        tif_files = os.listdir()
        global_file = ''
        for f in tif_files:
            if type == 'SMOD':
                if (f.endswith(".tif")) & ('SMOD' in f) & (year in f) & ('GLOBE' in f):
                    global_file = f
            elif (f.endswith(".tif")) & ('POP' in f) & (year in f) & ('GLOBE' in f):
                    global_file = f
        return global_file

    os.chdir(year)
    os.chdir('admin units')
    adm0 = find_country_shapefile(str(year))
    inAOI = gpd.read_file(adm0)
    os.chdir('..')
    if not os.path.exists(ghssmod_file):
        global_smod = find_global_file_location(year, 'SMOD')
        global_smod = os.path.join(outdir, global_smod)
        inR = rasterio.open(global_smod)
        inAOI = inAOI.to_crs(inR.crs)
        rMisc.clipRaster(inR, inAOI, ghssmod_file)

    if (not os.path.exists(aoi_pop)) & (adm0 != ''):
        global_pop = find_global_file_location(year, 'POP')
        global_pop = os.path.join(outdir, global_pop)
        inR = rasterio.open(global_pop)
        inAOI = inAOI.to_crs(inR.crs)
        rMisc.clipRaster(rasterio.open(global_pop), inAOI, aoi_pop)

    SMOD = rasterio.open(ghssmod_file).read()
    inPop = rasterio.open(aoi_pop)
    inP = rasterio.open(aoi_pop)
    if inAOI.crs != inPop.crs:
        inAOI = inAOI.to_crs(inPop.crs)

    out_meta = inPop.meta
    inPop = inPop.read()
    inPop = inPop * (inPop > 0)
    total_pop = inPop.sum()

    os.chdir('admin units')
    shape_files = os.listdir()
    adm = []
    for file in shape_files:
        if file.endswith(".shp"):
            if "adm0" in file:
                shortnm = 'adm0'
            elif "adm1" in file:
                shortnm = 'adm1'
            elif "adm2" in file:
                shortnm = 'adm2'
            elif "adm3" in file:
                shortnm = 'adm3'

            inA = gpd.read_file(file)
            if inA.crs != inP.crs:
                inA = inAOI.to_crs(inP.crs)
            urban_cal(year, shortnm, file, SMOD, inPop, ghssmod_file)
    os.chdir(homedir)