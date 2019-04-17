#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 10:59:15 2019

@author: ark4d
"""
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np
from cartopy.io.img_tiles import OSM
import cartopy.crs as ccrs
import pylab


def standart_visual(ax, regions, color_pallete, flags, **kargs):
    '''
    Show all regions
    Parameters
    ----------
        ax : geoaxes
            axes in which the data needs to be represented
        regions : dataframe
            having [sort_key, in_region, geometry] in columns
        color_pallete : dictionary
            color pallete (see source)
        flags : list of bool
            [ground, water, roads_major, roads_minor]
    Raises
    ------
        KeyError - if lines_df not provided
    '''
    #TODO: groundinner
    #ground_outer
    if flags[1]: ax.add_geometries(
        regions.loc[(regions.sort_key == 'districts') &\
                    (regions.in_region==False)].geometry,
        ccrs.PlateCarree(),
        edgecolor=color_pallete['borders_out'],
        linewidth=0.4,
        alpha=1,
        zorder=kargs['zorder']['ground_out'],
        color = color_pallete['ground_out'])
    #Water inner
    if flags[2]: ax.add_geometries(
        regions.loc[(regions.sort_key == 'water') &\
                    (regions.in_region==True)].geometry,
        ccrs.PlateCarree(),
        linewidth=0.4,
        alpha=1,
        zorder=kargs['zorder']['water_in'],
        color = color_pallete['water_in'])
    #Water outer
    if flags[3]: ax.add_geometries(
        regions.loc[(regions.sort_key == 'water') &\
                    (regions.in_region==False)].geometry,
        ccrs.PlateCarree(),
        linewidth=0.4,
        alpha=1,
        zorder=kargs['zorder']['water_out'],
        color = color_pallete['water_out'])
    try:
        if True in flags[4:8]:
            #road major in 
            lines_df = kargs['lines']
            if flags[4]: ax.add_geometries(
                lines_df.loc[(lines_df.sort_key == 'roads_major') &\
                            (lines_df.in_region==True)].geometry,
                ccrs.PlateCarree(),
                facecolor='none',
                linewidth=1,
                zorder=kargs['zorder']['roads_major_in'],
                edgecolor = color_pallete['roads_major_in'])
            #road minor in
            if flags[5]: ax.add_geometries(
                lines_df.loc[(lines_df.sort_key == 'roads_minor') &\
                            (lines_df.in_region==True)].geometry,
                ccrs.PlateCarree(),
                facecolor='none',
                linewidth=1,
                zorder=kargs['zorder']['roads_minor_in'],
                edgecolor = color_pallete['roads_minor_in'])
            #road major out
            if flags[6]: ax.add_geometries(
                lines_df.loc[(lines_df.sort_key == 'roads_major') &\
                            (lines_df.in_region==False)].geometry,
                ccrs.PlateCarree(),
                facecolor='none',
                linewidth=1,
                zorder=kargs['zorder']['roads_major_out'],
                edgecolor = color_pallete['roads_major_out'])
            #road minor out
            if flags[7]: ax.add_geometries(
                lines_df.loc[(lines_df.sort_key == 'roads_minor') &\
                            (lines_df.in_region==False)].geometry,
                ccrs.PlateCarree(),
                facecolor='none',
                linewidth=1,
                zorder=kargs['zorder']['roads_minor_out'],
                edgecolor = color_pallete['roads_minor_out'])
    except KeyError as keyer:
        print(keyer)
        raise KeyError(keyer, 
                       'Error might occur due the lack of lines_df in the kargs.')
        
    
def count_color_shapes(ax, regions, color_pallete, **kargs):
    '''
    Creates inner ground with color that represent count of datapoints in region
    Parameters
    ----------
        ax : geoaxes
        regions : dataframe
            shapes (passed to standart_visual)
        color_pallete : dict {for what:hexcolor}
            see source
    Keyword arguments
    -----------------
    districts : dataframe
        dataframe having [color_intensity(0 to 1), geometry]
        
    '''
    cm = kargs['cm']
    districts_df = kargs['districts']
    for index, row in districts_df.iterrows():

        ax.add_geometries([row.geometry],
                          ccrs.PlateCarree(),
                          edgecolor=color_pallete['borders_in'],
                          linewidth=0.4,
                          alpha=1,
                          zorder=kargs['zorder']['ground_in'],
                          color = cm(row.color_intensity))
    standart_visual(ax,regions,color_pallete,
                    flags=[False,True,True,True,False,False,False,False]
                    ,**kargs)
    
        
def zoomed_shape(ax, regions, color_pallete, **kargs):
    '''
    Function to draw shape 
    '''
    districts_df = kargs['districts']
    ax.add_geometries(districts_df.geometry,
                  ccrs.PlateCarree(),
                  edgecolor=color_pallete['borders_in'],
                  linewidth=0.4,
                  alpha=1,
                  zorder=kargs['zorder']['ground_in'],
                  color = color_pallete['ground_in'])
    standart_visual(ax,regions,color_pallete,
                    flags=[False,True,True,True,True,True,True,True]
                    ,**kargs)


def scatter(ax, data, color_pallete, **kargs):
    '''
    Creates points on axes and a colorbar
    Parameters
    ---------
        ax : geoaxes
            axes in which points will be visialized
        data : DataFrame
            having [x,y] in columns
        color_pallete : dict {for what:hexcolor}
            see source
    Keyword arguments
    -----------------
        do_colorbar : bool required
            If true then will show colorbar on axes
    '''
    ax.scatter(data.loc[:,'x'],data.loc[:,'y'], transform = ccrs.PlateCarree(),
               color = color_pallete['points_in'],
               s=kargs['sc_size'], alpha=kargs['sc_alpha'], zorder=30, )
    
    if kargs['do_colorbar'][kargs['ind']]==True:
        im = ax.imshow([[1,1,1,1],[2,2,2,2]], interpolation='nearest', 
                       cmap=kargs['cm'],vmin=0, vmax=1)
        N = kargs['max_val']
        rnd = -(len(str(int(N/2)))-1)
        print(N,rnd,[0,int(round(N/2,rnd)),int(round(N,rnd))])
        cax = kargs['fig'].add_axes([0.75, 0.20, 0.02, 0.2])
        cbar = kargs['fig'].colorbar(im, cax=cax, ticks=[0,0.5,1])
        cax.yaxis.set_ticks_position('left')
        yticks = cbar.ax.set_yticklabels(
                [0,str(int(round(N/2,rnd))),int(round(N,rnd))])  
        cbar.ax.tick_params(axis="y",labelsize=9)
        for tick in yticks:
            tick.set_color(color_pallete['points_in'])
        
    return [pylab.Line2D([0],[0],linewidth=0,
                         marker="o"
                         ,color=color_pallete['points_in'], alpha=1.0,),
            kargs['dot_name'][kargs['ind']]]
    
def scatter_metroes(ax, data, color_pallete, **kargs):
    '''
        Shows metro on axes
    '''
    ax.scatter(data.loc[:,'x'],data.loc[:,'y'], transform = ccrs.PlateCarree(),
               color = 'red',
               marker='$M$',
               s=30, linewidths=0.1, alpha=1, zorder=115, )
            
    return [pylab.Line2D([0],[0],linewidth=0,
                         marker="$M$"
                         ,color='red', alpha=1.0,),
            kargs['dot_name'][kargs['ind']]]
    
    
def hex_to_rgb(hex_s):
    '''Convert hex color to rgb
    Parameters
    -----------
    hex_s : str
        hex string
    
    Returns
    -------
    list of int
        [Red, Green, Blue]
    '''
    hex_s = hex_s.lstrip('#')
    return [int(hex_s[int(indx*2):int(indx*2+2)],16) for indx in range(0,3)]

def create_cmap(hexset, cmap_name):
    '''Creates gradient cmap by given hex values
    Parameters
    ----------
    hexset : list of str
        colors in hex value
    cmap_name : str
        name for new cmap
    
    Returns
    -------
    matplotlib.colors.LinearSegmentedColormap
        cmap 
    '''
    color = [[],[],[]]
    for hex_v in hexset:
        rgb_list = hex_to_rgb(hex_v)
        for indx, c in enumerate(rgb_list):
            color[indx].append(c)
    cdict = {'red':[],'green':[],'blue':[]} # see mpl docs
    for cind, val in enumerate(np.linspace(0, 1, len(color[0]))):
        for ind, key in enumerate(cdict):
            cdict[key].append([val, color[ind][cind]/255, 
                              color[ind][cind]/255])
    return LinearSegmentedColormap(cmap_name, segmentdata=cdict, N=256)

def create_plot(polygons_df, shape_func, datas, data_plot_funcs, 
                 color_pallete, title, extend, sav_figname, **kargs):
    '''
    Creates plot
    
    Parameters
    ----------
    shapes_in : list of shapely.geometry.multipolygon.MultiPolygon
        Shapes that represent region of interest.
    shapes_out : list of shapely.geometry.multipolygon.MultiPolygon
        All shaps or not in region of interest shapes.
    shape_func : function
        Function that determines how to represent shapes in regions 
        of interest. Parameters: ax, shapes_in, color_pallette, **kargs
    datas : list of obj pd.DataFrame
        Data that needs to be plotted on the plot
    data_plot_funcs : function
        Function that determines how to represent data at plot.
        Parameters: ax, data, color_palleter, **kargs
    color_pallette : dict
        Dictionary of colors
    title : str
        Title of plot
    extend : list of float
        Extend of map
    sav_figname : str
        Name of file in which the plot will be saved
    Keyword argumnets
    -----------------
        A bunch of ^^
        graph_info : str
            Infromation about data sources
    Returns
    -------
    '''
    zorders = {
            'legends':100,
            'ground_in':5,
            'ground_out':20,
            'water_out':15,
            'water_in':1,
            'roads_major_out':22,
            'roads_minor_out':21,
            'roads_major_in':7,
            'roads_minor_in':6,
            'first_layer_top':25,
            'first_layer':20,
            'first_layer_bottom':15,
            'second_layer_top':10,
            'second_layer':5,
            'second_layer_bottom':1,
            }
    tiler = OSM()
    plt.figure(figsize=(10,10))
    fig = plt.gcf()
    ax = plt.axes(projection=tiler.crs)
    ax.coastlines('10m')
    ax.set_extent(extend)

    shape_func(ax, polygons_df, color_pallete, 
               zorder = zorders, tiler=tiler, **kargs)
    legend_lines_list = []
    legend_text_list = []
    for indx, record in enumerate(list(zip(datas, data_plot_funcs))):
        legend_line, legend_text = record[1](ax, record[0], color_pallete, 
                                         fig = fig, ind = indx, **kargs )
        legend_lines_list.append(legend_line)
        legend_text_list.append(legend_text)
    ax.legend(legend_lines_list,legend_text_list,loc=4).set_zorder(
            zorders['legends'])
    if 'graph_info' in kargs and len(kargs['graph_info'])>0: 
        props = dict(boxstyle='round', facecolor='gray', alpha=0.5)
        ax.text(0.02,0.98,kargs['graph_info'],fontsize=7,
                horizontalalignment = 'left',
                verticalalignment = 'top',
                bbox=props,
                transform = ax.transAxes, color='White', zorder=1000)
    ax.text(0.001,
            0.001,
            '© OpenStreetMap contributors',
            fontsize=8,
            horizontalalignment = 'left',
            verticalalignment = 'bottom',
            transform = ax.transAxes, color='White', zorder=1000)
  
        
    plt.savefig(sav_figname)
    return ax
    plt.close()

# This code can be used to test create_cmap function
#hex_s='dbd1c9'
#mcm = create_cmap(['#dbd1c9','#db9a8e','#db6767','#db4848','#ff3a3a'])
#
#plt.figure()
#
#plt.scatter(np.random.random(100),np.random.random(100),c=np.random.random(100),cmap=mcm)
#plt.colorbar()
#plt.show()
#
#rgba = mcm(np.linspace(0, 1, 256))
#fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
#col = ['r', 'g', 'b']
#for xx in [0.25, 0.5, 0.75]:
#    ax.axvline(xx, color='0.7', linestyle='--')
#for i in range(3):
#    ax.plot(np.arange(256)/256, rgba[:, i], color=col[i])
#ax.set_xlabel('index')
#ax.set_ylabel('RGB')