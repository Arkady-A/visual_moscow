#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 10:57:40 2019

@author: ark4d
"""

import data_process, visual
import cartopy.io.shapereader as shpreader
import pandas as pd
import geopandas as gpd
# dellete
from importlib import reload

def non_stationary_stores(polygons_df, lines_df, data, color_pallete):
    '''
    This function create scatter plot that shows 'Расположение 
    нестационированных точек торговли'
    
    Parameters
    ----------
    polygons_df : DataFrame
        TODO: **Add destription**
    data : pd.Dataframe
        Data that are need to be plotted.
    color_pallete : dict
        Dict of color that will be used in the plot.
    '''
    # Start of logic block
    # Here I calculate the amount of points that are in for every shap
    def calc_count_intensity(df, data):
        df.loc[:,'count']=0
        df = df.apply(
            data_process.calculation_factory(data.loc[:,'x'].copy().values, 
            data.loc[:,'y'].copy().values)
            ,axis=1) 
        gdf = gpd.GeoDataFrame(df.copy(), crs = {'init': 'epsg:4326'}, 
                               geometry=list(df.copy().geometry.values))
        gdf.geometry = gdf.geometry.to_crs("+proj=eck4 +datum=WGS84 +units=km")   
        df.loc[:,'count_area']=df.loc[:,'count']/(gdf.geometry.area)
        df.loc[:,'color_intensity']=\
        df.loc[:,'count_area']/df.loc[:,'count_area'].max() 
        return df
    # Start of logic block
    # Here I calculate the amount of points that are in for every shap
    districal_amount = polygons_df.loc[(polygons_df.admin_leve == '8') &\
                                       (polygons_df.in_region==True)]
    districal_amount = calc_count_intensity(districal_amount.copy() , data[0])
    
    cm = visual.create_cmap(color_pallete['cm'], cmap_name='WhitetRedPastel')
#    #delete that before commit
    for module in [data_process, visual]:
        reload(module)
    visual.create_plot(polygons_df, 
                       visual.count_color_shapes, 
                       [data[0]], 
                       [visual.scatter],
                       color_pallete, 
                       'Расположение нестационированных точек торговли',
                       [36.75,38,55.14,56.07],
                       'big_picture_nestat.png',
                       cm = cm,
                       dot_name = ['Нестационированные точки торговли'],
                       districts = districal_amount,
                       max_val = districal_amount.loc[:,'count'].max(),
                       sc_alpha = 0.2,
                       sc_size = 0.1,
                       do_colorbar = [True],
                       graph_info = 'Источник данных: data.mos.ru',
                       )     
    print("INFO")
    max_region = districal_amount.loc[districal_amount.loc[:,'count_area'].idxmax()]
    print("Регион с самым большим количеством нестационарных точек торговли: {}"\
          .format(max_region.loc['name']))
    print("В этом регионе {} нестационарных точек торговли".format(
            max_region.loc['count']))
    print("Регион в приближении")
    
    districal_amount_sbl = polygons_df.loc[(polygons_df.admin_leve == '8') &\
                                           (polygons_df.in_region==True)]
    

    extend = list(max_region.geometry.bounds)
    extend[1],extend[2]=extend[2],extend[1]
    
    polygons_df_sb = polygons_df.apply(data_process.split_by_location_factory(
            [max_region.geometry]),axis=1)
    lines_df_sbl = lines_df.apply(data_process.split_by_location_factory(
            [max_region.geometry]),axis=1)

    visual.create_plot(polygons_df_sb, 
                       visual.zoomed_shape, 
                       [data[0],data[1]], 
                       [visual.scatter,visual.scatter_metroes],
                       color_pallete, 
                       'Расположение нестационированных точек торговли',
                       extend,
                       'zoomed_picture_nestat.png',
                       cm = cm,
                       dot_name = ['Нестационированные точки торговли',
                                   'Входы в вестибюль метро'],
                       districts = districal_amount_sbl,
                       max_val = None,
                       lines = lines_df_sbl,
                       sc_size = 4,
                       sc_alpha = 0.4,
                       do_colorbar = [False,False],
                       graph_info = 'Источник данных: data.mos.ru'
                       )    
    
fname='moscow_data/shapes/visual_moscow_v1_planet_osm_polygon_polygons.shp'
moscow = data_process.get_moscow_shape(fname)
polygons_df = data_process.load_shapes(
        fname=fname,
        sort_function = data_process.sort_attributes)

fname='moscow_data/shapes/visual_moscow_v1_planet_osm_line_lines.shp'
lines_df = data_process.load_shapes(
        fname=fname,
        sort_function = data_process.sort_attributes)
lines_df = lines_df.apply(data_process.split_by_location_factory(moscow),
                          axis=1)


polygons_df = polygons_df.apply(data_process.split_by_location_factory(moscow),
                                axis=1)
data = data_process.load_moscow_data()

white_to_red = ['#dbd1c9','#db9a8e','#db6767','#db4848','#ff3a3a']

color_pallete = {
    'ground_in':'#585D69',
    'ground_out':'#232A34',
    'water_in':'#3E4752',
    'water_out':'#3E4752',    
    'borders_in':'#34353d',
    'borders_out':'#3B3B3B',
    'tile_out':'#1c1c1c',
    'points_in':'#2bb4ff',
    'points_out':'#2bb4ff',
    'roads_major_in':'#aba4bc',
    'roads_minor_in':'#787287',
    'roads_major_out':'#827d91',
    'roads_minor_out':'#4c4856',
    'cm':['#3d3f59','#6a8d92','#80b192','#a1e887']
}

non_stationary_stores(polygons_df=polygons_df, 
                      data = [data[0],data[1]],
                      lines_df=lines_df,
                      color_pallete=color_pallete)
#non_stationary_stores(regions, other_regions, data = data[0], 
 #                     color_pallete=color_pallete_non_stationary)
 
# 
#extend = [36.75,38,55.14,56.07]
#tiler = OSM()
#plt.figure(figsize=(10,10))
#fig = plt.gcf()
#ax = plt.axes(projection=tiler.crs)
#ax.coastlines('10m')
#
#ax.set_extent(extend)
#ax.add_geometries(moscow,ccrs.PlateCarree(),  
#              linewidth=1, alpha=0.7)