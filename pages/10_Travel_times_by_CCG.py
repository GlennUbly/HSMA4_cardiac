# V1.2 sidebar (done), and multiple pages
# V1.3 columns for side by side comparison - see side-by-side page
##############################################################################
#
#                  Package imports and initial data sources
#
##############################################################################

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import seaborn as sbn
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import stats
import itertools
import time
from PIL import Image
from bokeh.plotting import ColumnDataSource, figure, output_file, show, output_notebook
from bokeh.models import LinearInterpolator

# for time test
start_full = time.time()

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

#shapefile available at https://data.cambridgeshireinsight.org.uk/dataset/output-areas

##############################################################################
#
#               Functions showing lines 54 to 509
#
##############################################################################

@st.cache_data()
def read_site_geographic_data(sites_filename):
    #st.write("Cache miss: read_site_geographic_data ran")
    df = pd.read_csv(sites_filename)
    new_prov_gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude_1m, df.Latitude_1m))
    new_prov_gdf = new_prov_gdf.set_crs(epsg=4326)
    new_prov_gdf = new_prov_gdf.to_crs(epsg=27700)
    return new_prov_gdf

@st.cache_data()
def filter_lsoa_to_ics(shape_filename,ics_lsoa_filename,left_on,right_on):
    #st.write("Cache miss: filter_lsoa_to_ics ran")
    lsoa_gdf = gpd.read_file(shape_filename)
    ics_lsoa = pd.read_csv(ics_lsoa_filename)
    ics_lsoa_gdf = lsoa_gdf[lsoa_gdf[left_on].isin(list(ics_lsoa[right_on]))]
    ics_lsoa_gdf = ics_lsoa_gdf.to_crs(epsg=27700)
    return ics_lsoa_gdf

#@st.cache_data()
# causes problems if cached, OK if not
def plot_proposed_sites1(prov_gdf, ics_gdf,axis_title):
    #st.write("Cache miss: plot_proposed_sites1 ran")
    fig, ax = plt.subplots(figsize=(10, 8)) # Make max dimensions 10x10 inch
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
    ax.set_title(axis_title, fontsize=12)
    # Adjust for printing
    ax.margins(0.05)
    #ax.apply_aspect()
    #plt.subplots_adjust(left=0.01, right=1.0, bottom=0.0, top=1.0)
    # Save figure
    #plt.savefig('map.jpg', dpi=300)
    #return plt.show()
    return fig, ax

#@st.cache_data()
def import_minimal_activity_data(activity_data_minimal_filename):
    # import minimal activity data **4 fields**
    df_activity = pd.read_csv(activity_data_minimal_filename)
    return df_activity


# confirmed used, consider caching - minimal time so no need
#@st.cache_data()
def create_ics_df(df_activity, ics_routino_filename, prov_gdf):
    # filter to ICS data
    df_ics = df_activity[df_activity['Patient_LSOA'].isin(list(ics_lsoa['yr2011_LSOA']))]
    df_ics = df_ics[['Der_Provider_Site_Code',
                     'Patient_LSOA',
                     'Travel_distance_km',
                     'Travel_time']]
    # add routino information to ICS df
    df_ics_routino = pd.read_csv(ics_routino_filename )
    df_ics_routino['to_postcode'] = df_ics_routino['to_postcode'].str.strip()
    df_ics = pd.merge(df_ics,
                prov_gdf[['Provider_Site_Code','Postcode_Trim']],
                how = 'left',
                left_on = 'Der_Provider_Site_Code',
                right_on = 'Provider_Site_Code'
                )
    return df_ics

# function to create DataFrame of measures for times and distances for a configuration of provider sites

# ics_routino_filename is the name of the  .csv of the full Routino output, all LSOA to all provider sites considered

# df_ics is a DataFrame of actual activity, with patient LSOA (from) and provider site postcode (to) locations
# df_ics is a slice of the original activity filtered on patient ICS
# df_ics can be created from the function create_ics_df which selects according to the LSOA in the Routino output
# df_ics = create_ics_df(df_valve, ics_routino_filename, prov_gdf)  # ACTUALS (left part of merge)

# df_activity is a DataFrame of actual activity nationally
# df_activity comes from import_activity_data(activity_data_filename)

# d_prov is a dictionary with keys the provider site codes, and values the provider site postcodes
# d_prov can be created with function get_provider_postcode_dict
# d_prov = prov_gdf.set_index('Provider_Site_Code')['Postcode_Trim'].to_dict()

# prov_gdf (GeoDataFrame) is the input for get_provider_postcode_dict and is taken from the provider site list (sites_filename)
# prov_gdf = read_site_geographic_data(sites_filename)

# new_prov_list is a list of provider codes (strings), enter manually or from some iteration

# confirmed used, but only in get_summary_table - maybe update that?
# can remove loop and use df_actuals_augmented

# Not to cache as used many times on different arguments
def test_sites_quick(df_actuals_augmented, df_activity, d_prov, prov_gdf, new_prov_list):
    df_test = df_actuals_augmented.copy()
    # create lists of values for the given new_prov_list from which we find the minimum time an distance
    new_sites_only = ['time_'+prov for prov in new_prov_list]
    df_test['Time_new_sites_min'] = df_test[new_sites_only].min(axis=1)
    df_test['Distance_new_sites_min'] = df_test[new_sites_only].min(axis=1)
    new_prov_time_list = ['time_'+a for a in new_prov_list]
    new_prov_time_list.append('Time_original')
    df_test['Time_min'] = df_test[new_prov_time_list].min(axis=1)
    df_test['Distance_min'] = df_test[new_prov_time_list].min(axis=1)
    # derive national median and mean travel time
    nat_median_time = df_activity['Travel_time'].median()
    nat_mean_time = df_activity['Travel_time'].mean()
    # Compare travel times of current service vs. test_prov list
    # Assumption: patients will go to provider with shortest travel time
    # Number of spells with travel time < actuals
    sum_reduced = sum(df_test['Time_new_sites_min'] < df_test['Time_original'])
    # Proportion of spells with travel time < actuals
    prop_reduced = sum(df_test['Time_new_sites_min'] < df_test['Time_original']) / df_test['Time_new_sites_min'].count()
    # Number of spells with (new) travel time < national median
    sum_reduced_natl_med = sum(df_test['Time_min'] < nat_median_time)
    # Proportion of spells with (new) travel time < national median
    prop_reduced_natl_med = sum(df_test['Time_min'] < nat_median_time) / df_test['Time_min'].count()
    # Original mean time
    original_time_mean = df_test['Time_original'].mean()
    # Original mean time
    original_time_median = df_test['Time_original'].median()
    # Travel time mean for this configuration
    test_time_mean = df_test['Time_min'].mean()
    # Travel time median for this configuration
    test_time_median = df_test['Time_min'].median()
    # Travel time maximum for this configuration
    test_time_maximum = df_test['Time_min'].max()
    # Travel time variance for this configuration
    test_time_var = df_test['Time_min'].var()
    # Travel time standard deviation for this configuration
    test_time_std = df_test['Time_min'].std()
    # Total travel time reduction
    total_time_reduction = (
       (df_test['Time_original'] - df_test['Time_min'])
       [df_test['Time_new_sites_min'] < df_test['Time_original']].sum())
    # Time reduction per spell
    time_reduction_per_spell = total_time_reduction/df_test['Time_new_sites_min'].count()
    # Total travel distance reduction (over 70 months), value in km travelled
    total_dist_reduction = (df_test['Distance_original'] - df_test['Distance_min'])[df_test['Time_min'] < df_test['Time_original']].sum()

    df_to_add = pd.DataFrame({"Added_providers": [','.join(new_prov_list)],
                              "Number_spells_reduced_time": [sum_reduced],
                              "Proportion_spells_reduced_time": [prop_reduced],
                              "Number_spells_under_natl_median": [sum_reduced_natl_med],
                              "Proportion_spells_under_natl_median": [prop_reduced_natl_med],
                              "Original_mean_time": [original_time_mean],
                              "Original_median_time": [original_time_median],
                              "New_mean_time": [test_time_mean],
                              "New_median_time": [test_time_median],
                              "New_maximum_time": [test_time_maximum],
                              "New_time_variance": [test_time_var],
                              "New_time_sd": [test_time_std],
                              "Total_time_reduction": [total_time_reduction],
                              "Time_reduction_per_spell": [time_reduction_per_spell],
                              "Total_distance_reduction": [total_dist_reduction]
                             })
    df_to_add.set_index("Added_providers", inplace=True)

    return df_to_add


# function to add in Routino data to the LSOA GeoDataFrame for a list of sites
# Inputs are: LSOA GeoDataFrame, Routino data, provider site gdf, Site list
# maybe improve speed with filename for lsoa_gdf ?

# confirmed used, but mostly in functions that have been updated
# Also used in the lsoa_to_all_gdf calculation - maybe update that?

@st.cache_data()
def gdf_add_site_list(ics_routino_filename, shape_filename, _prov_gdf, test_prov_list) :
    #st.write("Cache miss: gdf_add_site_list ran")
    lsoa_gdf = gpd.read_file(shape_filename)
    lsoa_gdf = lsoa_gdf.to_crs(epsg=27700)
    df_ics_routino = pd.read_csv(ics_routino_filename)
    prov_dict = dict(zip(prov_gdf.Provider_Site_Code, prov_gdf.Postcode_Trim))
    gdf_test = lsoa_gdf.copy()

    for test_prov in test_prov_list :
        right = df_ics_routino[df_ics_routino['to_postcode']==prov_dict[test_prov]][['from_postcode','to_postcode','time_min','distance_km']]
        gdf_test = pd.merge(left=gdf_test,
                            right=right,
                            left_on='lsoa11cd', # not 'yr2011_LSOA'
                            right_on='from_postcode'
                           )
        gdf_test = gdf_test.drop(['from_postcode', 'to_postcode'], axis=1)
        gdf_test = gdf_test.rename(columns={'time_min':'time_'+test_prov,
                                            'distance_km':'distance_'+test_prov})
    return gdf_test


def plot_times_impact_quick(lsoa_to_all_gdf, current_providers, new_provider_list, prov_gdf, threshold, save_output) :
    current_list = ['time_'+a for a in current_providers]
    test_prov_list = ['time_'+prov for prov in new_provider_list]
    gdf = lsoa_to_all_gdf.copy()
    gdf['new_min_time'] = gdf[current_list+test_prov_list].min(axis=1)
    gdf['Time_change'] = gdf['new_min_time'] - gdf[current_list].min(axis=1)
    sites = [site_dict2[code] for code in new_provider_list]
    # plot LSOA chloropleth with provider sites marked
    fig, ax = plt.subplots(figsize=(10,6))
    plt.title('Impact on travel times with the addition of sites\n '+
              '\n'.join(sites),
              fontsize=16)
    ax.set_axis_off()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.1)
    gdf.plot(ax=ax,
             column='Time_change',
             legend=True,
             cax=cax
             )
    test_prov_gdf = prov_gdf[prov_gdf['Provider_Site_Code'].isin(current_providers+new_provider_list)]
    test_prov_gdf.plot(ax=ax,
                       edgecolor='r',
                       facecolor='silver',
                       markersize=200,
                       marker='*')
    if save_output :
        if not os.path.exists(os.getcwd()+'/output/time_impact_maps'):
            os.makedirs(os.getcwd()+'/output/time_impact_maps')
        plt.savefig(os.getcwd()+'/output/time_impact_maps/'+'-'.join(new_provider_list)+'.png')
    else :
        pass
    return fig, ax

def plot_time_impact_threshold_quick(lsoa_to_all_gdf, current_providers, new_provider_list, prov_gdf, threshold, save_output) :
    current_list = ['time_'+a for a in current_sites]
    test_prov_list = ['time_'+prov for prov in new_provider_list]
    sites = [site_dict2[code] for code in new_provider_list]
    gdf = lsoa_to_all_gdf.copy()
    gdf['new_min_time'] = gdf[current_list+test_prov_list].min(axis=1)
    gdf['current_min_time'] = gdf[current_list].min(axis=1)
    gdf['Orig_<_nat'] = np.where(gdf[current_list].min(axis=1) <= threshold , True , False)
    gdf['New_<_nat'] = np.where(gdf[test_prov_list].min(axis=1) <= threshold , True , False)
    gdf['Compare_with_national'] = np.where(gdf['Orig_<_nat'],
                                              'Remains <= national median',
                                              np.where(gdf['New_<_nat'],
                                                      'Change to <= national median',
                                                      'Remains > national median')
                                              )
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax,
              column='Compare_with_national',
              legend=True)
    ax.set_axis_off()
    ax.set_title('Impact on travel time compared to national median for site\n '+
                  '\n'.join(sites),
                  fontsize=16)
    test_prov_gdf = prov_gdf[prov_gdf['Provider_Site_Code'].isin(current_sites+new_provider_list)]
    test_prov_gdf.plot(ax=ax,
                        edgecolor='r',
                        facecolor='silver',
                        markersize=200,
                        marker='*')
    if save_output :
        if not os.path.exists(os.getcwd()+'/output/compare_nat_med_maps'):
            os.makedirs(os.getcwd()+'/output/compare_nat_med_maps')
        plt.savefig(os.getcwd()+'/output/compare_nat_med_maps/'+'-'.join(new_provider_list)+'.png')
    else :
        pass
    return fig, ax

# get_site_pairs function
# input proposed_sites as a list output from:
# df = pd.read_csv(sites_filename)
# full_list = df['Provider_Site_Code'].tolist()
# proposed_sites = [site for site in full_list and not site in current_sites]
def get_site_pairs(proposed_sites) :
    pairs = list(itertools.product(*[proposed_sites,proposed_sites]))
    pairs_mixed = [list(i) for i in pairs if list(i)[0] != list(i)[1]]
    pairs_sorted = [sorted(i) for i in pairs_mixed]
    pairs_as_set_of_tuples = {tuple(i) for i in pairs_sorted}
    pairs_list_as_tuples = list(pairs_as_set_of_tuples)
    pairs_list = [list(i) for i in pairs_list_as_tuples]
    return pairs_list


#############################################################################
#
#                  Create summary DataFrame for results
#
#############################################################################

# maybe revise to use only quick functions?
#test_sites_quick(df_actuals_augmented, df_activity, d_prov, prov_gdf, new_prov_list)
@st.cache_data()
def get_summary_table(_prov_gdf,
                      current_sites,
                      df_activity,
                      d_prov,
                      site_pairs,
                      save_output) :
    #st.write("Cache miss: get_summary_table ran")
    df_results = pd.DataFrame()
    df_results["Added_providers"] = []
    df_results["Number_spells_reduced_time"] = []
    df_results["Proportion_spells_reduced_time"] = []
    df_results["Number_spells_under_natl_median"] = []
    df_results["Proportion_spells_under_natl_median"] = []
    df_results["Original_mean_time"] = []
    df_results["Original_median_time"] = []
    df_results["New_mean_time"] = []
    df_results["New_median_time"] = []
    df_results["New_time_variance"] = []
    df_results["New_time_sd"] = []
    df_results["Total_time_reduction"] = []
    df_results["Time_reduction_per_spell"] = []
    df_results["Total_distance_reduction"] = []
    df_results.set_index("Added_providers", inplace=True)

    new_provider_list = prov_gdf['Provider_Site_Code'].to_list()
    for site in current_sites :
        new_provider_list.remove(site)
    for pair in site_pairs :
        df_to_add = test_sites_quick(df_actuals_augmented,
                                     df_activity,
                                     d_prov,
                                     prov_gdf,
                                     pair)
        df_results = df_results.append(df_to_add)
    for site in new_provider_list :
        df_to_add = test_sites_quick(df_actuals_augmented,
                                     df_activity,
                                     d_prov,
                                     prov_gdf,
                                     [site])
        df_results = df_results.append(df_to_add)
    if save_output :
        if not os.path.exists(os.getcwd()+'/output'):
            os.makedirs(os.getcwd()+'/output')
        df_results.to_csv(os.getcwd()+'/output/'+'results_summary.csv')
    else :
        pass
    df_results["Number_spells_reduced_time"] = df_results["Number_spells_reduced_time"].astype(int)
    return df_results

#############################################################################
#
#       Create augmented actuals table with times to each proposed site
#
#############################################################################

def get_actuals_augmented(df_ics,
                          ics_routino_filename,
                          test_prov_list) :
    df_test = df_ics.copy()
    df_ics_routino = pd.read_csv(ics_routino_filename )
    for test_prov in test_prov_list :
        right = df_ics_routino[df_ics_routino['to_postcode']==d_prov[test_prov]][['from_postcode','to_postcode','time_min','distance_km']]
        df_test = pd.merge(left=df_test,
                           right=right,
                           left_on='Patient_LSOA',
                           right_on='from_postcode'
                          )
        df_test = df_test.drop(['from_postcode', 'to_postcode'], axis=1)
        df_test = df_test.rename(columns={'time_min':'time_'+test_prov,
                                          'distance_km':'distance_'+test_prov,
                                          'Travel_distance_km':'Distance_original',
                                          'Travel_time':'Time_original'})
    return df_test

#############################################################################
#
#            Create travel times plot for comparison to actuals
#
#############################################################################

# take df_actuals_augmented and find mew mins for each record
def kde_plot_quick(df_actuals_augmented, test_prov_list, threshold, save_output) :
    df_test = df_actuals_augmented.copy()
    new_sites_only = ['time_'+prov for prov in test_prov_list]
    new_sites_only_dist = ['distance_'+prov for prov in test_prov_list]
    df_test['Time_new_sites_min'] = df_test[new_sites_only].min(axis=1)
    df_test['Distance_new_sites_min'] = df_test[new_sites_only_dist].min(axis=1)

    new_prov_time_list = ['time_'+a for a in test_prov_list]
    new_prov_time_list.append('Time_original')
    df_test['Time_new_config_min'] = df_test[new_prov_time_list].min(axis=1)
    df_test['Distance_new_config_min'] = df_test[new_prov_time_list].min(axis=1)

    filename_site = ','.join(test_prov_list)+'.csv'
    sites = [site_dict2[code] for code in test_prov_list]

    fig, ax = plt.subplots(figsize=(10,6))
    sbn.kdeplot(ax=ax,
            data=df_test['Time_original'],
            clip = (0,125),
            fill=True,
            legend= True)
    plt.axvline(x=df_test['Time_original'].median(),
                linewidth=2,
                color='cornflowerblue')

    sbn.kdeplot(ax=ax,
            data=df_test['Time_new_config_min'],
            clip = (0,125),
            fill=True,
            alpha=0.5,
            legend=True).set(title='Travel times with additional site at:\n '+
                             '\n'.join(sites))
    plt.axvline(x=df_test['Time_new_config_min'].median(),
                linewidth=2,
                color='orange')
    plt.axvline(x=threshold,
                linewidth=2,
                color='g')

    ax.set_xlabel('Travel time (mins)')
    plt.legend(('Current travel times',
                'Median current travel time',
                'Travel times with additional sites',
                'Median with additional sites',
                'National median travel time'),
               loc='upper right',fontsize=8)
    if save_output :
        if not os.path.exists(os.getcwd()+'/output/kde_plots_mult'):
            os.makedirs(os.getcwd()+'/output/kde_plots_mult')
        plt.savefig(os.getcwd()+'/output/kde_plots_mult/'+
                    '-'.join(test_prov_list)+'.png')
    else :
        pass
    return fig, ax

# Write results to a .csv
#if not os.path.exists(os.getcwd()+'/output'):
#    os.makedirs(os.getcwd()+'/output')
#df_results.to_csv(os.getcwd()+'/output/'+'KM_results_1_or_2_sites.csv')

#############################################################################
#
#                     Create map for new travel times
#
#############################################################################

#current_providers = ['RJ122','RJZ01']
#new_provider_list = ['RVV09','RWF03'] # for example
# prov_gdf defined above
def plot_new_prov_times_quick(lsoa_to_all_gdf, current_providers, new_provider_list, save_file) :
    current_list = ['time_'+a for a in current_providers]
    test_prov_list = ['time_'+prov for prov in new_provider_list]
    gdf = lsoa_to_all_gdf.copy()
    gdf['new_min_time'] = gdf[current_list+test_prov_list].min(axis=1)
    sites = [site_dict2[code] for code in new_provider_list]

    fig, ax = plt.subplots(figsize=(10,6))
    plt.title('Travel times with the addition of sites:\n '+
              '\n'.join(sites),
              fontsize=16)
    ax.set_axis_off()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.1)
    gdf.plot(ax=ax,
             column='new_min_time',
             legend=True,
             cax=cax
            )
    test_prov_gdf = prov_gdf[prov_gdf['Provider_Site_Code'].isin(current_providers+new_provider_list)]
    test_prov_gdf.plot(ax=ax,
                       edgecolor='r',
                       facecolor='silver',
                       markersize=200,
                       marker='*')
    if save_file :
        if not os.path.exists(os.getcwd()+'/output/time_plots'):
            os.makedirs(os.getcwd()+'/output/time_plots')
        plt.savefig(os.getcwd()+'/output/time_plots/'+'-'.join(new_provider_list)+'.png')
    else :
        pass
    return fig, ax


#############################################################################
#
#                   Get national activity time map by CCG
#
#############################################################################

@st.cache_data()
def get_national_time_map(ccg_mapping_filename, activity_data_minimal_filename) :
    #st.write("Cache miss: get_national_time_map ran")
    df_ccg = pd.read_csv(ccg_mapping_filename, encoding = 'unicode_escape')
    df_activity = import_minimal_activity_data(activity_data_minimal_filename)
    # df_activity = pd.read_csv(activity_data_filename, parse_dates = ['Admission_Date'])
    # df_activity.set_index("APCS_Ident", inplace = True)
    # df_activity['Der_Activity_Month'] = df_activity['Der_Activity_Month'].astype(str)
    # df_activity['Admission_Method'] = df_activity['Admission_Method'].astype(str)
    # df_activity['Activity_count'] = 1
    df_activity = pd.merge(df_activity,
                            df_ccg,
                            on = 'Pt_CCG_Code',
                            how = 'left'
                            ).set_index(df_activity.index)
    df_activity['CCG_Code_2122'] = df_activity['CCG_Code_2122'].combine_first(df_activity['Pt_CCG_Code'])
    df_activity['CCG_2122'] = df_activity['CCG_2122'].combine_first(df_activity['Pt_CCG'])
    ccg_gdf = gpd.read_file('zip://./Clinical_Commissioning_Groups_(April_2021)_EN_BUC.zip')
    ccg_gdf = ccg_gdf.rename({'CCG21NM': 'Pt_CCG',
                              'Shape__Are': 'CCG_Area_sq_km'},
                             axis='columns'
                             )
    ccg_gdf['CCG_Area_sq_km'] *= 10**-6
    df_ccg_pop = pd.read_csv("ccg_pop.csv", encoding = 'unicode_escape')
    df_ccg_pop = df_ccg_pop.rename({'CCG Name': 'Pt_CCG',
                                    'STP21 Name': 'Pt_ICS',
                                    'NHSER21 Name': 'Pt_Region',
                                    'All Ages': 'Population'},
                                   axis='columns')
    df_ccg_pop['Population'] = df_ccg_pop['Population'].str.replace(',', '').astype(float)
    ccg_gdf = pd.merge(ccg_gdf, df_ccg_pop, on = 'Pt_CCG', how = 'left').set_index(ccg_gdf.index)
    ccg_gdf['Population_density'] = ccg_gdf['Population'] / ccg_gdf['CCG_Area_sq_km']
    ccg_gdf['CCG_2122'] = ccg_gdf['Pt_CCG'].str.upper()
    df = df_activity[['CCG_2122',
                      'Travel_distance_km',
                      'Travel_time']
                     ].groupby('CCG_2122').agg({'Travel_distance_km':'mean',
                                                'Travel_time':'mean'}
                                                ).reset_index()

    df['CCG_2122_lower'] = df['CCG_2122'].str.lower()
    df = pd.merge(df,
                  ccg_gdf[['Pt_CCG',
                           'CCG_2122',
                           'Pt_Region',
                           'Population',
                           'Population_density',
                           'geometry']],
                  on = 'CCG_2122',
                  how = 'left'
                  )
    df = df.drop(['CCG_2122_lower'], axis=1)
    nat_act_gdf = gpd.GeoDataFrame(df, geometry='geometry')
    return nat_act_gdf

# Exclude providers with < 10 procedures over this time
# And create national point gdf of these sites
@st.cache_data()
def get_national_providers(national_provider_filename, activity_data_minimal_filename) :
    #st.write("Cache miss: get_national_providers ran")
    nat_prov_df = pd.read_csv(national_provider_filename)
    nat_prov_gdf = gpd.GeoDataFrame(nat_prov_df,
                                    geometry=gpd.points_from_xy(nat_prov_df.Longitude_1m, nat_prov_df.Latitude_1m)
                                    )
    nat_prov_gdf = nat_prov_gdf.set_crs(epsg=4326)
    nat_prov_gdf = nat_prov_gdf.to_crs(epsg=27700)
    df_activity = import_minimal_activity_data(activity_data_minimal_filename)

    df_act_by_prov = df_activity[['Der_Provider_Site_Code']].groupby('Der_Provider_Site_Code').agg({'Der_Provider_Site_Code':'count', })
    df_act_by_prov = df_act_by_prov.rename(columns={"Der_Provider_Site_Code": "count_site"})
    df_act_by_prov = df_act_by_prov[df_act_by_prov['count_site']>10]
    nat_prov10_gdf = pd.merge(nat_prov_gdf,
                              df_act_by_prov,
                              left_on='Provider_Site_Code',
                              right_on='Der_Provider_Site_Code'
                              )
    #nat_prov10_gdf = nat_prov10_gdf[nat_prov10_gdf['Activity_count']>10].sort_values('Activity_count', ascending=False)
    return nat_prov10_gdf




#############################################################################
#
#                  Set variables and values to use
#
#############################################################################

df = pd.read_csv(sites_filename)
full_list = df['Provider_Site_Code'].tolist()
current_sites = ['RJ122','RJZ01']
proposed_sites = list(set(full_list) - set(current_sites))
prov_gdf = read_site_geographic_data(sites_filename)
d_prov = prov_gdf.set_index('Provider_Site_Code')['Postcode_Trim'].to_dict()
#df_activity = import_activity_data(activity_data_filename)
df_activity = import_minimal_activity_data(activity_data_minimal_filename)
df_ics = create_ics_df(df_activity, ics_routino_filename, prov_gdf)
df_ics = create_ics_df(df_activity, ics_routino_filename, prov_gdf)
site_pairs = get_site_pairs(proposed_sites)
lsoa_to_all_gdf = gdf_add_site_list(ics_routino_filename, shape_filename, prov_gdf, full_list)
threshold = df_activity['Travel_time'].median() # national median time
nat_act_gdf = get_national_time_map(ccg_mapping_filename, activity_data_minimal_filename)
nat_prov10_gdf = get_national_providers(national_provider_filename, activity_data_minimal_filename)
df_actuals_augmented = get_actuals_augmented(df_ics,ics_routino_filename,full_list)
save_output = False
km_prov_gdf = read_site_geographic_data(sites_filename)
km_lsoa_gdf = filter_lsoa_to_ics(shape_filename,
                                 ics_filename,
                                 'lsoa11cd',
                                 'yr2011_LSOA')

site_dict = dict(zip(km_prov_gdf['Provider_Site_Name'], km_prov_gdf['Provider_Site_Code']))
site_dict2 = dict(zip(km_prov_gdf['Provider_Site_Code'], km_prov_gdf['Provider_Site_Name']))
site_list = list(km_prov_gdf['Provider_Site_Name'])
current_site_names = [site_dict2[site] for site in current_sites]
site_list = list(set(site_list) - set(current_site_names))
df_results = get_summary_table(prov_gdf,
                               current_sites,
                               df_activity,
                               d_prov,
                               site_pairs,
                               save_output)

nat_act_gdf['Travel_time_rank_asc'] = nat_act_gdf['Travel_time'].rank(ascending=True)
nat_act_gdf['Pop_density_rank'] = nat_act_gdf['Population_density'].rank(ascending=False)


#############################################################################
#############################################################################
###
###
###                           Streamlit content
###
###
#############################################################################
#############################################################################


#############################################################################
#
#                  Initial introductory text and national map
#
#############################################################################

st.title("Travel Times For Cardiac Valve Surgery in Kent and Medway")
st.markdown("#### A comparison of possible configurations of sites offering "+
            "this service, looking at the potential impact on travel times "+
            "and distances")

st.markdown("We first look at a sample of our data - all elective cardiac "+
            "valve surgery for patients throughout England between 2016/17 "+
            "and 2021/22. Based on an OPCS procedure code list (see ref), we "+
            "identify 71,073 spells. ")
#st.write(df_activity.head())

#st.dataframe(nat_act_gdf)
st.write("Nationally, based on Routino data, we see a mean travel time of "+
         f"{df_activity['Travel_time'].mean():.0f} minutes "+
         f"and a median of {df_activity['Travel_time'].median():.0f} minutes.")
st.dataframe(df_activity.describe([0, 0.25, 0.5, 0.75, 0.95]))


#st.write("Add in detail about the range and distribution of travel times, "+
#         "activity levels, providers to include...")

st.markdown("We map the travel times based on Routino data for the patient "+
            "home LSOA and the provider site postcode, showing the mean "+
            "travel time for each CCG")


if not os.path.exists('output') :
    os.mkdir('output')
if not os.path.exists(os.getcwd()+'/output/nat_map_ccg.png') :
    fig, ax = plt.subplots(figsize=(8, 8))
    # Plot CCG by mean travel time
    nat_act_gdf.plot(ax=ax,
                      column='Travel_time',
                      edgecolor='face',
                      linewidth=0.0,
                      vmin=0,
                      vmax=110,
                      cmap='inferno_r',
                      legend_kwds={'shrink':0.8, 'label':'Travel time (mins)'},
                      legend=True,
                      alpha = 0.70)
    # Plot location of hospitals
    nat_prov10_gdf.plot(ax=ax,
                    edgecolor='k',
                    facecolor='w',
                    markersize=200,
                    marker='*')
    ax.set_axis_off() # Turn of axis line numbers
    ax.set_title('Cardiac Valve Surgery\nMean Travel Time by CCG')
    ax.margins(0)
    ax.apply_aspect()
    plt.subplots_adjust(left=0.01, right=1.0, bottom=0.0, top=1.0)
    plt.savefig(os.getcwd()+'/output/nat_map_ccg.png')
    st.pyplot(fig)
else :
    nat_map_ccg = Image.open(os.getcwd()+'/output/nat_map_ccg.png')
    st.image(nat_map_ccg)

st.write("Looking at travel times by CCG, we note a negative "+
         "correlation between population density and mean travel time. "+
         "")

with st.expander("Ranked travel time and population density by CCG",
                 expanded=False) :
    st.dataframe(nat_act_gdf[['CCG_2122',
                              'Travel_time',
                              'Travel_time_rank_asc',
                              'Pop_density_rank',
                              'Population_density',
                              'Population'
                              ]])

# chart to show correlations
df = nat_act_gdf[['CCG_2122',
                  'Travel_time',
                  'Travel_time_rank_asc',
                  'Pop_density_rank',
                  'Population_density',
                  'Population'
                  ]]

size_mapper=LinearInterpolator(
    x=[df.Population.min(),df.Population.max()],
    y=[5,20]
    )

source = ColumnDataSource(data=dict(
    x=df['Population_density'],
    y=df['Travel_time'],
    desc1=df['CCG_2122'],
    desc2=df['Population'],
    ))

TOOLTIPS = [
    ("CCG", "@desc1"),
    ("Population density", "@x{0}"),
    ("Mean travel time", "@y{0}"),
    ("Population", "@desc2")
    ]

fig = figure(width=600,
             height=600,
             tooltips=TOOLTIPS,
             title="Population density against travel time by CCG")

fig.circle('x',
           'y',
           size={'field':'desc2','transform': size_mapper},
           source=source)
fig.xaxis.axis_label = 'Population density (per sq km)'
fig.yaxis.axis_label = 'Mean travel time (mins)'
st.bokeh_chart(fig, use_container_width=True)


a = stats.spearmanr(nat_act_gdf['Travel_time'],nat_act_gdf['Population_density'])

st.write("We calculate Spearman's rank correlation coefficient to show "+
         "the negative correaltion between CCG mean travel time and "+
         "population density as:")
st.latex(r'''
         \rho =
         ''' +
         rf''' {a[0]:.2f} '''
         )
st.latex(r'''
         p =
         ''' +
         rf''' {a[1]:.19f} '''
         )

st.write("We observe that Kent and Medway CCG sees travel times "+
         "longer then all but 8 CCGs nationally, and these mostly have "+
         "significantly lower population density. Thus there is a case "+
         "for considering a possible site or sites for new cardiac "+
         "valve surgery centre(s) in this area.")


if not os.path.exists('output') :
    os.mkdir('output')
if not os.path.exists(os.getcwd()+'/output/kent_prov.png') :
    f = plot_proposed_sites1(km_prov_gdf,
                             km_lsoa_gdf,
                             'Proposed Sites in Kent and Medway')
    fig, ax = f
    plt.savefig(os.getcwd()+'/output/kent_prov.png')
    #st.pyplot(fig)
else :
    #kent_prov = Image.open(os.getcwd()+'/output/kent_prov.png')
    #st.image(kent_prov)
    pass


end_full = time.time()
st.write('Total time to run '+str(round(end_full - start_full,1)) + ' seconds')

# temp to add for conclusions
# 1 and 2 site configs
# kde, times, impact, threshold
#kde_plot_quick(df_actuals_augmented, test_prov_list, threshold, save_output)
#plot_new_prov_times_quick(lsoa_to_all_gdf, current_providers, new_provider_list, save_file)
#plot_times_impact_quick(lsoa_to_all_gdf, current_providers, new_provider_list, prov_gdf, threshold, save_output)
#plot_time_impact_threshold_quick(lsoa_to_all_gdf, current_providers, new_provider_list, prov_gdf, threshold, save_output)


# current_list = ['time_'+a for a in current_sites]
# test_prov_list = ['time_'+prov for prov in new_provider_list]
# sites = [site_dict2[code] for code in new_provider_list]
# gdf = lsoa_to_all_gdf.copy()
# gdf['new_min_time'] = gdf[current_list+test_prov_list].min(axis=1)
# gdf['current_min_time'] = gdf[current_list].min(axis=1)
# gdf['Orig_<_nat'] = np.where(gdf[current_list].min(axis=1) <= threshold , True , False)
# gdf['New_<_nat'] = np.where(gdf[test_prov_list].min(axis=1) <= threshold , True , False)
# gdf['Compare_with_national'] = np.where(gdf['Orig_<_nat'],
#                                         'Travel time <= national median',
#                                         np.where(gdf['New_<_nat'],
#                                                       'Change to <= national median',
#                                                       'Travel time > national median')
#                                               )
# fig, ax = plt.subplots(figsize=(10, 6))
# gdf.plot(ax=ax,
#          column='Compare_with_national',
#          legend=True)
# ax.set_axis_off()
# test_prov_gdf = prov_gdf[prov_gdf['Provider_Site_Code'].isin(current_sites+new_provider_list)]
# test_prov_gdf.plot(ax=ax,
#                         edgecolor='r',
#                         facecolor='silver',
#                         markersize=200,
#                         marker='*')
# fig.savefig(os.getcwd()+'/output/km_current_threshold_map.png')
