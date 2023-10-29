#Author: Lydia Teinfalt
#Last updated date: 06/05/2023
##Data downloaded from https://ghsl.jrc.ec.europa.eu/download.php?ds=pop

import geopandas as gpd
import pandas as pd
import rasterio
import os
import rasterio
import GOSTRocks.rasterMisc as rMisc
from rasterio import features
import numpy as  np
from xrspatial import zonal_stats
import xarray as xr
import rioxarray


#years = ["1975", "1980", "1985", "1990", "1995", "2000","2005","2010","2015","2020"]
years = ["2010"]
#read input files
homedir = os.getcwd()
all_csv_files = []
combined_adm0 = pd.DataFrame()
combined_adm1 = pd.DataFrame()
combined_adm2 = pd.DataFrame()
combined_adm3 = pd.DataFrame()
adm_files = ["PAK_ADM0.csv", "PAK_ADM1.csv", "PAK_ADM2.csv","PAK_ADM3.csv"]
combined_files = [combined_adm0,combined_adm1,combined_adm2,combined_adm3]

def summarize_data(files):
    print("current csv files")
    print(files)

    for f in files:
        df = pd.read_csv(f)
        if 'adm0' in f:
            combined_adm0 = combined_adm0.append
        combined_df = combined_df.append(df)
    print(combined_df)


for year in years:
    os.chdir(year)
    all_files = os.listdir()

    for file in all_files:
        if os.path.isfile(file) and len(file)>= 4 and file[-4:] == ".csv":
            df = pd.read_csv(file)
            df['year'] = year
            if 'PAK_adm0' in file:
                combined_adm0 = combined_adm0.append(df)
            if 'PAK_adm1' in file:
                combined_adm1 = combined_adm1.append(df)
            if 'PAK_adm2' in file:
                #combined_adm2 = pd.concat([combined_adm2, df])
                combined_adm2 = combined_adm2.append(df)
            if 'PAK_adm3' in file:
                #combined_adm3 = pd.concat([combined_adm3, df])
                combined_adm3 = combined_adm3.append(df)
    os.chdir("..")
    #combined_adm0 = combined_adm0[['Shape_Area', 'year', 'ADM0_PCODE', 'ADM0_EN','sum_10', 'sum_10']]

combined_adm0.to_csv("PAK_ADM0.csv")
combined_adm1.to_csv("PAK_ADM1.csv")
combined_adm2.to_csv("PAK_ADM2.csv")
combined_adm3.to_csv("PAK_ADM3.csv")
writer = pd.ExcelWriter('PAK_TREND_GHSSMOD.xlsx')

for k in adm_files:
    df = pd.read_csv(k)
    df['total'] = df[['sum_10', 'sum_11', 'sum_12', 'sum_13', 'sum_21','sum_22', 'sum_23', 'sum_30']].values.sum(axis=1)
    df['perc_10'] = (df['sum_10']/df['total'])
    df['perc_11'] = (df['sum_11'] / df['total'])
    df['perc_12'] = (df['sum_12'] / df['total'])
    df['perc_13'] = (df['sum_13'] / df['total'])
    df['perc_21'] = (df['sum_21'] / df['total'])
    df['perc_22'] = (df['sum_22'] / df['total'])
    df['perc_23'] = (df['sum_23'] / df['total'])
    df['perc_30'] = (df['sum_30'] / df['total'])
    df['perc_total'] = df[['perc_10', 'perc_11', 'perc_12', 'perc_13', 'perc_21', 'perc_22', 'perc_23','perc_30']].values.sum(axis=1)
    df.iloc[:,2:].to_csv(k)
    df.to_excel(writer, sheet_name=k)
writer.save()





