import pandas as pd
import geopandas as gpd
import src.novelUrbanization as novel
import os
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import product
import numpy as np
import scipy.stats as ss


method = 'DB'
#pak_provinces = ['Khyber Pakhtunkhwa', 'Punjab', 'Sindh', 'Balochistan', 'Federal Capital Territory']
pak_provinces = ['Khyber Pakhtunkhwa', 'Punjab', 'Sindh', 'Balochistan', 'Federal Capital Territory']
data_dir = 'data'
pop_data_dir = ['FINAL_STANDARD', 'FINAL_STANDARD_1KM']
output_dir = 'ESRI_OUTPUT'
ti_dir = 'TI'

def eda(csv):
    if csv.endswith('.csv'):
        print("Filename: " + csv)
        df = pd.read_csv(csv)
    print(df.head())
    print(df.tail())
    print('Length of dataframe')
    print(len(df))

    print(df.describe())
    print('Top 5 Most Populous')
    print(df.sort_values(by=['Pop'], ascending = False).head(5))
    print(df.sort_values(by=['Pop'], ascending=False).head(5))

    print("Sum of Population")
    print(df['Pop'].sum())

    if 'ADM3_EN' in df.columns:
        df1 = df.groupby(['ADM3_EN', 'ADM2_EN', 'ADM1_EN']).sum()
    elif 'ADM2_EN' in df.columns:
        df1 = df.groupby(['ADM2_EN', 'ADM1_EN']).sum()
    elif 'ADM1_EN' in df.columns:
        df1 = df.groupby(['ADM1_EN']).sum()
    else:
        df1 = df.groupby(['ADM0_EN']).sum()
    fn = os.path.basename(csv).split('.')
    df1.to_csv(fn[0] + '_sum.csv')

def summarize(path_ti_files,adm_level):
    ti_path = os.path.join(data_dir, path_ti_files)
    if adm_level == 1:
        df_province = pd.DataFrame()
        for f in os.listdir(ti_path):
            csv = os.path.basename(f)
            if csv.endswith('ti.csv'):
                print('TI filename: ' + csv)
                df1 = pd.read_csv(os.path.join(ti_path, csv))
                df2=df1[['ADM1_EN', 'Pop', 'PERCENTAGE']]
                if df_province.empty:
                    df_province= df2
                else:
                    df_province = pd.concat([df_province, df2], axis=1)
        df_province.to_csv(os.path.join(ti_path, 'provinces.csv'))



    if adm_level > 1:
        for item in pak_provinces:
            df_district = pd.DataFrame()
            print('Province: ' + item)
            for f in os.listdir(ti_path):
                csv = os.path.basename(f)
                if csv.endswith('ti.csv'):
                    print('TI filename: ' + csv)
                    df1 = pd.read_csv(os.path.join(ti_path,csv))
                    df2 = df1[df1['ADM1_EN'] == item]
                    df3 = df2[['ADM3_EN','ADM2_EN','Pop', 'PERCENTAGE']]
                    if df_district.empty:
                        df_district = df3
                    else: df_district = pd.concat([df_district, df3], axis = 1)
            df_district.to_csv(item + '.csv')


def read_shape_file(shape):
    shape_file = gpd.read_file(shape)
    filenm = shape.split('.')
    shape_file.to_csv(filenm[0] + '.csv')


if method == 'DOU':
    os.chdir(data_dir)
    os.chdir(pop_data_dir)
    os.chdir(output_dir)
    files = os.listdir(os.getcwd())
    for file in files:
        if file.endswith('.shp'):
            read_shape_file(file)
        if file.endswith('.csv'):
            eda(file)

if method == 'DB':
    data_dir = os.path.join('dartboard', 'Delineations')
    pop_data_dir = os.path.join('dartboard', 'Sources')
    output_dir = os.path.join('dartboard','Output')
    pop_data_src = ['pak1k_gpo.tif', 'pak1k_upo15.tif']
    admin = os.path.join('data', 'Administrative Unit Data', 'pak_admbnda_adm1_ocha_pco_gaul_20181218.shp')
    for src in pop_data_src:
        print('pop data = ' + src)
        if 'gpo' in src:
            folder = 'gpo'
            in_folder = os.path.join(data_dir, folder)
            print(in_folder)
            db_urban = novel.calc_pp_urban(in_folder, src, admin, output_dir, '')
            df1 = db_urban[['ADM1_EN', 'pak1k_gpo', 'pak1k_gpod3b3000_ur', 'pak1k_gpod3b3000_cc', 'pak1k_gpod3b3000_co','pak_gpo','pak_gpod10b3000_ur', 'pak_gpod10b3000_cc', 'pak_gpod10b3000_co']]
            df1.to_csv('dartboard/Output/db_pak_adm1_gpo_1k_250m.csv')
        if 'upo' in src:
            folder = 'upo15'
            in_folder = os.path.join(data_dir, folder)
            print(in_folder)
            db_urban = novel.calc_pp_urban(in_folder, src, admin, output_dir, '')
            df1 = db_urban[['ADM1_EN', 'pak1k_upo15', 'pak1k_upo15d3b3000_ur', 'pak1k_upo15d3b3000_cc', 'pak1k_upo15d3b3000_co','pak_upo15', 'pak_upo15d10b3000_ur', 'pak_upo15d10b3000_cc', 'pak_upo15d10b3000_co']]
            df1.to_csv('dartboard/Output/db_pak_adm1_upo15_1k_250m.csv')


if method == 'EDA':
    eda("data/FINAL_STANDARD_1KM/ESRI_OUTPUT/pak1k_gpo1_ocha_adm1_hd_urban.csv")

if method == 'ZONAL':
    summarize(ti_dir,1)

if method == 'COMBINE_CSV':
    writer = pd.ExcelWriter('dou_districts.xlsx')  # Arbitrary output name
    csv_files = os.listdir('.')
    for files in csv_files:
        if files.endswith('.csv'):
            df = pd.read_csv(files)
            df.to_excel(writer, sheet_name=os.path.splitext(files)[0])
    writer.save()


if method == 'CORR':
    df = pd.read_excel('pak_national_urban.xlsx')
    print('Dataframe columns:' + df.columns)
    df_cat = pd.DataFrame(data=df.dtypes, columns=['a']).reset_index()
    cat_var = list(df_cat['index'].loc[df_cat['a'] == 'object'])
    df_cat = df[cat_var]
    print(df_cat.head())
    cat_var1 = ('source', 'resolution', 'method')
    cat_var2 = ('source', 'resolution', 'method')
    cat_var_prod = list(product(cat_var1, cat_var2, repeat=1))
    result = []
    for i in cat_var_prod:
        if i[0] != i[1]:
            result.append((i[0], i[1], list(ss.chi2_contingency(pd.crosstab(df_cat[i[0]], df_cat[i[1]])))[1]))
    chi_test_output = pd.DataFrame(result, columns=['var1', '‘var2','coeff'])
    ## Using pivot function to convert the above DataFrame into a crosstab
    print(chi_test_output.pivot(index='var1', columns='var2', values ='coeff'))









