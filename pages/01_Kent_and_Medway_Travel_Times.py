# Page for exploring why K&M is exceptional

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import seaborn as sbn
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools
import time
from PIL import Image

# file with geography for proposed sites
sites_filename = 'KM_Sites_Geog.csv'

# lsoa shapefile
shape_filename = 'Lower_Layer_Super_Output_Areas_December_2011_Generalised_Clipped__Boundaries_in_England_and_Wales.zip'

# file with lsoa codes for ICS of interest - create dataframe
ics_filename = 'KM_LSOA.csv'
ics_lsoa = pd.read_csv(ics_filename)

# axis title for site plot
axis_title = 'Kent by LSOA with proposed cardiac surgery sites'

# activity data
activity_data_filename = "Cardiac valves_national v0.2.csv"
activity_data_minimal_filename = "activity_data_minimal.csv"

# routino data for ics
ics_routino_filename = "results_km_all_sites.csv"

# national providers for this service
national_provider_filename = 'valve_providers.csv'

# mapping file for CCG mergers (will need updating)
ccg_mapping_filename = 'CCG_mapping.csv'

# File for population density and mean travel times and distances by CCG
ccg_gdf_travel = 'ccg_gdf_travel.csv'
#gdf = gpd.read_file('valve_ccg_gdf.csv', GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO", dtype=np.float64)

@st.cache(suppress_st_warning=True)
def read_site_geographic_data(sites_filename):
    #st.write("Cache miss: read_site_geographic_data ran")
    df = pd.read_csv(sites_filename)
    new_prov_gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude_1m, df.Latitude_1m))
    new_prov_gdf = new_prov_gdf.set_crs(epsg=4326)
    new_prov_gdf = new_prov_gdf.to_crs(epsg=27700)
    return new_prov_gdf

def import_minimal_activity_data(activity_data_minimal_filename):
    # import minimal activity data **4 fields**
    df_activity = pd.read_csv(activity_data_minimal_filename)
    return df_activity

@st.cache(suppress_st_warning=True)
def read_ccg_geo_pop_data(ccg_gdf_travel):
    #st.write("Cache miss: read_site_geographic_data ran")
    gdf = gpd.read_file(ccg_gdf_travel, 
                        GEOM_POSSIBLE_NAMES="geometry",
                        KEEP_GEOM_COLUMNS="NO", 
                        dtype=np.float64)
    gdf['Population'] = gdf['Population'].astype(float)
    gdf['Population_density'] = gdf['Population_density'].astype(float)
    gdf['Activity_count'] = gdf['Activity_count'].astype(float)
    gdf['Travel_distance_km'] = gdf['Travel_distance_km'].astype(float)
    gdf['Travel_time'] = gdf['Travel_time'].astype(float)
    return gdf

#@st.cache(suppress_st_warning=True)
# causes problems if cached, OK if not
def plot_proposed_sites1(prov_gdf, ics_gdf,axis_title):
    #st.write("Cache miss: plot_proposed_sites1 ran")
    fig, ax = plt.subplots(figsize=(5, 10)) # Make max dimensions 10x10 inch
    # Plot travel times for each LSOA
    ics_gdf.plot(ax=ax, # Set which axes to use for plot (only one here)
            #column='Travel_time', # Column to apply colour
            # antialiased=False, # Avoids artifact boundry lines
            edgecolor='gray', # Make LSOA boundry same colour as area
            linewidth=0.5,# Use linewidth=0 to hide boarder lines
            vmin=-100, # Manual scale min (remove to make automatic)
            vmax=200, # Manual scale max (remove to make automatic)
            #cmap='inferno_r', # Coloour map to use
            # Adjust size of colourmap key, and add label
            #legend_kwds={'shrink':0.5, 'label':'Travel time (mins)'},
            # Set to display legend
            #legend=True,
            # Set transparancy (to help reveal basemap)
            alpha = 0.70)

    # Plot location of hospitals
    prov_gdf.plot(ax=ax, edgecolor='k', facecolor='gold', markersize=200,marker='*')
    # Add labels
    for x, y, label in zip(
        prov_gdf.geometry.x, prov_gdf.geometry.y, prov_gdf.Provider_Site_Name):
            ax.annotate(label, xy=(x, y), xytext=(8, 8), textcoords="offset points",
                        backgroundcolor="y", fontsize=8)

    # Add base map (note that we specifiy the same CRS as we are using)
    # Use manual zoom to adjust level of detail of base map
    # ctx.add_basemap(ax,source=ctx.providers.OpenStreetMap.Mapnik,zoom=10, crs='epsg:27700')

    ax.set_axis_off() # Turn on/off axis line numbers
    ax.set_title(axis_title, fontsize=20)
    # Adjust for printing
    ax.margins(0.05)
    #ax.apply_aspect()
    #plt.subplots_adjust(left=0.01, right=1.0, bottom=0.0, top=1.0)
    # Save figure
    #plt.savefig('map.jpg', dpi=300)
    #return plt.show()
    return fig, ax

gdf = read_ccg_geo_pop_data(ccg_gdf_travel)

st.title('Kent and Medway travel times')

st.write("We assess the likely impact of new site(s) on travel "+
         "times for Kent and Medway patients. The sites considered "+
         "are the seven in the area with an existing adult critical "+
         "care unit.")


kent_prov = Image.open(os.getcwd()+'/output/kent_prov.png')
st.image(kent_prov)

kent_kde = Image.open(os.getcwd()+'/output/km_current_kde.png')
st.write('The current travel times for Kent and Medway patients are as '+
         'follows, with 98.7% of patients with travel times greater than the '+
         ' national median time of 27 minutes')
st.image(kent_kde)

kent_map = Image.open(os.getcwd()+'/output/km_current_map.png')
st.write('The current travel times are distributed geographically as '+
          'follows, with almost all patients travelling to the 2 London '+
          'sites shown')
st.image(kent_map)

kent_threshold_map = Image.open(os.getcwd()+'/output/km_current_threshold_map.png')
st.write('We see only small area close to London currently sees travel times '+
         'less than the national median')
st.image(kent_threshold_map)

