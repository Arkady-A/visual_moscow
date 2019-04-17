#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 10:58:38 2019

@author: ark4d
"""
import pandas as pd
from shapely.geometry import Point
import cartopy.io.shapereader as shpreader
import numpy as np

def load_shapes(fname, sort_function=None, ):
    '''
    Loads shapes
    Parameters
    ----------
        fname : str
            Name of shape file
        sort_function : function optional
            Function that will sort data
    Returns
    -------
        If sort_function is not None then Dataframe else list 
    '''
    records = shpreader.Reader(fname).records()   
    shapes_sorted = []
    if sort_function is not None:
        for record in records:
            sort, sort_key = sort_function(record)
            if sort:
                buff = record.attributes
                buff['geometry']=record.geometry
                buff['sort_key'] = sort_key
                shapes_sorted.append(buff)
        
        return pd.DataFrame(
                {key: [dicti[key] for dicti in shapes_sorted] for key in shapes_sorted[0]})
    else:
        return list(records)

def split_by_location_factory(shapes_of_interest):
    '''
        Creates function to determine whether a polygon inside shapes_of_interest
    '''
    def split_by_Location_fn(record):
        record.loc['in_region'] = False
        for shape in shapes_of_interest:
            if record.loc['geometry'].within(shape):
                record.loc['in_region'] = True 
        return record
    return split_by_Location_fn

def sort_attributes(record):
    '''
    Sorts whether or not an data instance in interest
    Parameters
    ----------
        record : cartopy.io.shapereader.Record
            ...
    Returns
    -------
        If record in interest returns [True, key]. Key - key of interest (road, distrct)
        else returns [False, None]
    '''
    attributes_of_interest = {
        'roads_minor':{
                'highway':['unclassified',
                           'residential',
                           'living_street',
                           ]
                },
        'roads_major':{
                'highway':['motorway','trunk',
                           'primary','secondary',
                           'tertiary','road'
                           ]
                },
        'districts':{
                'admin_leve':['8','7','6']
                },
        'water':{
                'natural':['water','wetlan','glacier'],
                'waterway':['riverbank','dock'],
                'landuse':['reservoir']
                },
        }
    for key in attributes_of_interest.keys():
        for sub_key in attributes_of_interest[key]:
            try:
                if record.attributes[sub_key] in attributes_of_interest[key][sub_key]:
                    return [True,key]
            except KeyError:
                continue
    return [False, None]

        
def is_in(shape, shapes_of_interest): # subfunction for checkin whether or not a shape in shapes_of_interest
    for shape_i in shapes_of_interest:
        if shape.within(shape_i):
            return True
    return False

def load_and_process_shapes_moscow(fname):
    '''
    Loads shapes and process them
    
    Parameters 
    ----------
    fname : str
        name of '.shp' file
        
    Returns
    -------
    tuple of dictionaries
        Regions and All_regions
    '''
    records, records_mosc = shpreader.Reader(
            fname).records(),shpreader.Reader(fname).records()
    moscow = get_moscow_shape(records_mosc)
    
    regions, all_regions = split_shapes(moscow, records)
    return regions, all_regions

def load_moscow_data():
    ''' Loads data and process it.
    
    Returns
    -------
    list 
        List of dataframes.
    '''
    stationary_obj = pd.read_json('moscow_data/stationary_torg_objects.json',
                                  encoding='cp1251')
    metroes = pd.read_json('moscow_data/metro_entrance-397-2019-02-01.json', 
                         encoding='cp1251')
    metroes = metroes.rename({'Longitude_WGS84':'x',
                      'Latitude_WGS84':'y'}, axis=1)
    return_list = []
    for df in [stationary_obj]:
        adresses = []
        for i in range(0,len(df)):
            adresses.append(stationary_obj.iloc[i].geoData['coordinates'])
        return_list.append(pd.DataFrame(adresses,columns=['x','y']))
    return_list.append(metroes)
    return return_list

def get_moscow_shape(fname):
    '''This function returns shapes of moscow
    Parameters
    ----------
    shapes : shapely.geometry.multipolygon.MultiPolygon
        shapes from which moscow will be discerned
    Returns
    -------
    list of shapely.geometry.multipolygon.MultiPolygon
        moscow shapes
    '''
    shapes = shpreader.Reader(fname).records()  
    return [x.geometry for x in shapes if 'Москва' == x.attributes['name']]

def calculation_factory(x, y):
    '''Creates a function for iterating over shapes to calculate amount of points
    in it.
    
    Parameters
    ----------
    x : list
        x parameters of points
    y ; list
        y parameters of poitns
    
    Returns
    -------
    function
        Function for calculating amount of points in a region given by row of
        dataframe named 'shape'.
    
    '''
    used = []
    def calculate_points_by_region(row): 
        region = row.loc['geometry']
        count = 0
        x_l = np.delete(x,used)
        y_l = np.delete(y,used)
        for ind in range(0,len(x_l)):
            dot = Point(x_l[ind],y_l[ind])
            if region.contains(dot):
                used.append(ind)
                count+=1
        row.loc['count'] = count
        return row
    return calculate_points_by_region
