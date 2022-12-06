import pandas as pd
import os
from arcgis.gis import GIS
from arcgis.geometry import Polygon, Geometry, Point, Polyline
from arcgis.geocoding import geocode
import arcpy




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

    print("Count of Population")
    print(df['Pop'].count())



    if 'ADM3_EN' in df.columns:
        df1 = df.groupby(['ADM3_EN', 'ADM2_EN', 'ADM1_EN']).sum()
        df2 = df.groupby(['ADM3_EN', 'ADM2_EN', 'ADM1_EN']).count()
    elif 'ADM2_EN' in df.columns:
        df1 = df.groupby(['ADM2_EN', 'ADM1_EN']).sum()
        df1 = df.groupby(['ADM2_EN', 'ADM1_EN']).count()
    else:
        df1 = df.groupby(['ADM1_EN']).sum()
        df2 = df.groupby(['ADM1_EN']).count()
    print(df1)
    print(df2)

def read_shape_file(shape):
    shape_file = gpd.read_file(shape)
    filenm = shape.split('.')
    shape_file.to_csv(filenm[0] + '.csv')



data_dir = 'data'
pop_data_dir = 'FINAL_STANDARD'
output_dir = 'ESRI_OUTPUT'

os.chdir(data_dir)
os.chdir(pop_data_dir)
os.chdir(output_dir)
files = os.listdir(os.getcwd())
for file in files:
    if file.endswith('.shp'):
        read_shape_file(file)
    if file.endswith('.csv'):
        eda(file)

#for i in os.listdir(os.getcwd()):
    # if os.path.isfile(i):
    #     df = gpd.read_file(i)
    #     eda(df)








