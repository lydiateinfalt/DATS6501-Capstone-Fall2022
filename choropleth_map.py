import os.path

import pandas as pd
import matplotlib.pyplot as plt #if using matplotlib
import plotly.express as px #if using plotly
import geopandas as gpd
import fnmatch
import glob
import os

admin = ['adm1', 'adm2', 'adm3']
shapefile_dir = "data/Administrative Unit Data/"
csv_dir = 'data/TI'
pakistan_iso = 'pak_admbnda'
sources = ['gpo', 'upo15']
output_dir = 'viz/cholo'
adm = ''



for file in os.listdir(shapefile_dir):
    if file.endswith('ocha_pco_gaul_20181218.shp'):
        map_df = gpd.read_file(os.path.join(shapefile_dir, file))

        #see what the map looks like
        map_df.plot(figsize=(20, 10))
        plt.show()

        adm = [ele for ele in admin if (ele in file)]

        if adm and adm[0] in admin:
            csv_files = os.listdir(csv_dir)
            admin = adm[0]
            for csv in csv_files:
                if csv.endswith("_ti.csv") and admin in csv:
                    df1 = pd.read_csv(csv_dir + "/" +csv)
                    if 'ADM3_EN' in df1.columns:
                        hover_name = 'ADM3_EN'
                        df_merged = map_df.merge(df1[['ADM3_EN', 'PERCENTAGE']],  # map_df merge to df
                                                 left_on=['ADM3_EN'], right_on=['ADM2_EN'])
                    elif 'ADM2_EN' in df1.columns:
                        hover_name = 'ADM2_EN'
                        df_merged = map_df.merge(df1[['ADM2_EN', 'PERCENTAGE']],  # map_df merge to df
                                                 left_on=['ADM2_EN'], right_on=['ADM2_EN'])
                    elif 'ADM1_EN' in df1.columns:
                        hover_name = 'ADM1_EN'
                        df_merged = map_df.merge(df1[['ADM1_EN', 'PERCENTAGE']],  # map_df merge to df
                                                 left_on=['ADM1_EN'], right_on=['ADM1_EN'])
                    else:
                        df_merged = map_df.merge(df1[['ADM0_EN', 'PERCENTAGE']],  # map_df merge to df
                                                 left_on=['ADM0_EN'], right_on=['ADM2_EN'])
                    df_merged.sort_values('PERCENTAGE', inplace=True)
                    fn = os.path.basename(csv).split('.')

                    #Create jpeg
                    fig, ax = plt.subplots(1, figsize=(10,6))
                    df_merged.plot(column='PERCENTAGE', cmap='YlOrRd', linewidth=1, ax=ax, edgecolor='0.9', legend = True)
                    plt.title(fn[0])
                    ax.axis('off')
                    fig.savefig(os.path.join(output_dir,fn[0] + '.jpg'))

                    #df_merged = pd.read_csv('data/FINAL_STANDARD_1KM/OUTPUT/pak1k_adm1_ocha_gpo_urban.csv')


                    fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                                        locations=df_merged.index, color="PERCENTAGE", hover_name=hover_name,
                                        height=500,
                                       color_continuous_scale="YlOrRd",
                                         projection="mollweide")
                    fig.update_geos(fitbounds="locations", visible=True)
                    fig.update_layout(
                        title_text= fn[0]
                    )
                    fig.update_geos(fitbounds="locations", visible=False)
                    fig.update_layout(
                        margin={"r":0,"t":30,"l":10,"b":10},
                        coloraxis_colorbar={
                            'title':'Percentage'})
                    fig.show()