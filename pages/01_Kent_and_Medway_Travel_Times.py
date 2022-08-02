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

gdf = read_ccg_geo_pop_data(ccg_gdf_travel)

# plot inetractive map of CCGs showing travel times and pop dens etc as tooltip



st.title('Kent and Medway travel times')
st.write('Add details of the exceptionality of this CCG in terms of '+
         'long travel times for the geographic and demographic features. '+
         'Use analysis in Travel_time_pop_density.ipynb to show K&M is an '+
         'exception to the (negative) rank correlation of population density '+
         'and median travel time.')


