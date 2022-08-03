# Page for comparing configurations side by side
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


#############################################################################
#############################################################################
###
###                All functions and values as before
###
#############################################################################
#############################################################################



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

@st.cache(suppress_st_warning=True)
def read_site_geographic_data(sites_filename):
    #st.write("Cache miss: read_site_geographic_data ran")
    df = pd.read_csv(sites_filename)
    new_prov_gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude_1m, df.Latitude_1m))
    new_prov_gdf = new_prov_gdf.set_crs(epsg=4326)
    new_prov_gdf = new_prov_gdf.to_crs(epsg=27700)
    return new_prov_gdf

@st.cache(suppress_st_warning=True)
def filter_lsoa_to_ics(shape_filename,ics_lsoa_filename,left_on,right_on):
    #st.write("Cache miss: filter_lsoa_to_ics ran")
    lsoa_gdf = gpd.read_file(shape_filename)
    ics_lsoa = pd.read_csv(ics_lsoa_filename)
    ics_lsoa_gdf = lsoa_gdf[lsoa_gdf[left_on].isin(list(ics_lsoa[right_on]))]
    ics_lsoa_gdf = ics_lsoa_gdf.to_crs(epsg=27700)
    return ics_lsoa_gdf

#@st.cache(suppress_st_warning=True)
# causes problems if cached, OK if not
def plot_proposed_sites1(prov_gdf, ics_gdf,axis_title):
    #st.write("Cache miss: plot_proposed_sites1 ran")
    fig, ax = plt.subplots(figsize=(10, 10)) # Make max dimensions 10x10 inch
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
    ax.set_title(axis_title)
    # Adjust for printing
    ax.margins(0.05)
    #ax.apply_aspect()
    #plt.subplots_adjust(left=0.01, right=1.0, bottom=0.0, top=1.0)
    # Save figure
    #plt.savefig('map.jpg', dpi=300)
    #return plt.show()
    return fig, ax

# @st.cache(suppress_st_warning=True)
# def import_activity_data(activity_data_filename):
#     #st.write("Cache miss: import_activity_data ran")
#     # import activity data **Function will not work unless data is in correct format**
#     df_activity = pd.read_csv(activity_data_filename, parse_dates = ['Admission_Date'])
#     df_activity.set_index("APCS_Ident", inplace = True)
#     df_activity['Der_Activity_Month'] = df_activity['Der_Activity_Month'].astype(str)
#     df_activity['Admission_Method'] = df_activity['Admission_Method'].astype(str)
#     df_activity['Activity_count'] = 1
#     return df_activity

@st.cache(suppress_st_warning=True)
def import_minimal_activity_data(activity_data_minimal_filename):
    # import minimal activity data **4 fields**
    df_activity = pd.read_csv(activity_data_minimal_filename)
    return df_activity

# confirmed used, consider caching - minimal time so no need
#@st.cache()
def create_ics_df(df_activity, ics_routino_filename, prov_gdf): 
    # filter to ICS data
    df_ics = df_activity[df_activity['Patient_LSOA'].isin(list(ics_lsoa['yr2011_LSOA']))]
    df_ics = df_ics[['Der_Provider_Site_Code',
                     'Patient_LSOA',
                     'Travel_distance_km',
                     'Travel_time',]]
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

@st.cache(suppress_st_warning=True)
def gdf_add_site_list(ics_routino_filename, shape_filename, prov_gdf, test_prov_list) :
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
@st.cache(suppress_st_warning=True)
def get_summary_table(prov_gdf, 
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
               loc='upper right',fontsize=10)
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
#nat_act_gdf = get_national_time_map(ccg_mapping_filename, activity_data_filename)
#nat_prov10_gdf = get_national_providers(national_provider_filename, activity_data_filename)
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

#############################################################################
#############################################################################
###
###                          Streamlit content
###
#############################################################################
#############################################################################


st.title('Side by side comparison of configurations')
st.write("Select configurations to compare in the 2 select boxes in the "+
         "sidebar. Set the Appearance to 'Wide mode' in the Settings to "+
         "expand.")

col1, col2 = st.columns(2)

with st.sidebar :
    with st.form('select_sites_form') :
        selected_site_pair1 = st.multiselect('First configuration for comparison:',site_list)
        selected_site_pair2 = st.multiselect('Second configuration for comparison:',site_list)
        st.form_submit_button("Submit")

with col1 :
    sites = [site_dict[site] for site in selected_site_pair1]
    # kde plot of times comared to current
    f = kde_plot_quick(df_actuals_augmented, sites, threshold, save_output)
    fig, ax = f
    st.pyplot(fig)
    # new time map
    f = plot_new_prov_times_quick(lsoa_to_all_gdf, 
                              current_sites,
                              sites,
                              False)
    fig, ax = f
    st.pyplot(fig)
    # time impact map
    f = plot_times_impact_quick(lsoa_to_all_gdf, 
                            current_sites, 
                            sites, 
                            prov_gdf, 
                            threshold,
                            save_output)
    fig, ax = f
    st.pyplot(fig)
    # impact relative to threshold map
    f = plot_time_impact_threshold_quick(lsoa_to_all_gdf, 
                                     current_sites, 
                                     sites,
                                     prov_gdf, 
                                     threshold,
                                     save_output)
    fig, ax = f
    st.pyplot(fig)
    
    # comparison sentences
    
    if len(sites) == 1 :
        site = ','.join(sites)
        #st.subheader('Comparison with the other configurations with 1 additional site')
        
        df_results_one = df_results.copy().reset_index(drop=False)
        df_results_one = df_results_one[df_results_one['Added_providers'].str.len()==5]
        count_options = len(df_results_one)
        
        med_orig = df_results.loc[site]['Original_median_time']
        med_new = df_results.loc[site]['New_median_time']
        df_results_one['New_median_time_rank'] = df_results_one['New_median_time'].rank(method='min', ascending=True)
        new_med_time_dict = dict(zip(df_results_one['Added_providers'], df_results_one['New_median_time_rank']))
        new_med_time_rank = new_med_time_dict[site]
        
        proportion_reduced = df_results.loc[site]['Proportion_spells_reduced_time']
        df_results_one['Prop_reduced_rank'] = df_results_one['Proportion_spells_reduced_time'].rank(method='min', ascending=False)
        prop_reduced_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Prop_reduced_rank']))
        prop_reduced_rank = prop_reduced_dict[site]
        
        proportion_spells_under_natl_median = df_results.loc[site]['Proportion_spells_under_natl_median']
        df_results_one['Prop_under_nat_median_rank'] = df_results_one['Proportion_spells_under_natl_median'].rank(method='min', ascending=False)
        prop_under_nat_median_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Prop_under_nat_median_rank']))
        prop_under_nat_median_rank = prop_under_nat_median_dict[site]
        
        mean_time_reduction = df_results.loc[site]['Time_reduction_per_spell']
        df_results_one['Time_reduction_rank'] = df_results_one['Time_reduction_per_spell'].rank(method='min', ascending=False)
        time_reduction_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Time_reduction_rank']))
        time_reduction_rank = time_reduction_dict[site]
        
        total_distance_reduction = df_results.loc[site]['Total_distance_reduction']
        df_results_one['Dist_reduction_rank'] = df_results_one['Total_distance_reduction'].rank(method='min', ascending=False)
        dist_reduction_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Dist_reduction_rank']))
        dist_reduction_rank = dist_reduction_dict[site]
        
        new_max_time = df_results.loc[site]['New_maximum_time']
        df_results_one['Max_time_rank'] = df_results_one['New_maximum_time'].rank(method='min', ascending=True)
        max_time_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Max_time_rank']))
        max_time_rank = max_time_dict[site]
        
        st.markdown('#### Impact of additional site at {} on key travel time metrics'.format(selected_site_pair1[0]))
        
        st.markdown(f'* Median travel time for Kent and Medway patients reduced '+
                 f'from {med_orig:.0f} to {med_new:.0f} minutes. '+
                 f'This configuration ranks {new_med_time_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced for {100*proportion_reduced:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_reduced_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown('* Travel times would be reduced to less than the national median '+
                 f'for {100*proportion_spells_under_natl_median:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_under_nat_median_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Mean travel time reduction would be {mean_time_reduction:.0f} '+
                 f'minutes. This configuration ranks {time_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* Total travel distance (1 way) reduction would be {total_distance_reduction:,.0f} '+
                 f'km for the period of actuals considered. This configuration ranks {dist_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* The new maximum travel time would be {new_max_time:.0f} minutes. '+
                 f'This configuration ranks {max_time_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        rank_list1 = [new_med_time_rank,
                      prop_reduced_rank,
                      prop_under_nat_median_rank,
                      time_reduction_rank,
                      dist_reduction_rank,
                      max_time_rank]
        
    elif len(sites) == 2 :
        sites.sort()
        site = ','.join(sites)
        st.subheader('Comparison with the other configurations with 2 additional sites')
        
        df_results_two = df_results.copy().reset_index(drop=False)
        df_results_two = df_results_two[df_results_two['Added_providers'].str.len()==11]
        count_options = len(df_results_two)
    
        med_orig = df_results.loc[site]['Original_median_time']
        med_new = df_results.loc[site]['New_median_time']
        df_results_two['New_median_time_rank'] = df_results_two['New_median_time'].rank(method='min', ascending=True)
        new_med_time_dict = dict(zip(df_results_two['Added_providers'], df_results_two['New_median_time_rank']))
        new_med_time_rank = new_med_time_dict[site]
        
        proportion_reduced = df_results.loc[site]['Proportion_spells_reduced_time']
        df_results_two['Prop_reduced_rank'] = df_results_two['Proportion_spells_reduced_time'].rank(method='min', ascending=False)
        prop_reduced_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Prop_reduced_rank']))
        prop_reduced_rank = prop_reduced_dict[site]
        
        proportion_spells_under_natl_median = df_results.loc[site]['Proportion_spells_under_natl_median']
        df_results_two['Prop_under_nat_median_rank'] = df_results_two['Proportion_spells_under_natl_median'].rank(method='min', ascending=False)
        prop_under_nat_median_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Prop_under_nat_median_rank']))
        prop_under_nat_median_rank = prop_under_nat_median_dict[site]
        
        mean_time_reduction = df_results.loc[site]['Time_reduction_per_spell']
        df_results_two['Time_reduction_rank'] = df_results_two['Time_reduction_per_spell'].rank(method='min', ascending=False)
        time_reduction_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Time_reduction_rank']))
        time_reduction_rank = time_reduction_dict[site]
        
        total_distance_reduction = df_results.loc[site]['Total_distance_reduction']
        df_results_two['Dist_reduction_rank'] = df_results_two['Total_distance_reduction'].rank(method='min', ascending=False)
        dist_reduction_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Dist_reduction_rank']))
        dist_reduction_rank = dist_reduction_dict[site]
        
        new_max_time = df_results.loc[site]['New_maximum_time']
        df_results_two['Max_time_rank'] = df_results_two['New_maximum_time'].rank(method='min', ascending=True)
        max_time_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Max_time_rank']))
        max_time_rank = max_time_dict[site]
        
        st.markdown('#### Impact of additional sites on key travel time metrics:')
        st.markdown(f'#### {selected_site_pair1[0]}')
        st.markdown(f'#### {selected_site_pair1[1]}')
        
        st.markdown(f'* Median travel time for Kent and Medway patients reduced '+
                 f'from {med_orig:.0f} to {med_new:.0f} minutes. '+
                 f'This configuration ranks {new_med_time_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced for {100*proportion_reduced:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_reduced_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced to less than the national median '+
                 f'for {100*proportion_spells_under_natl_median:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_under_nat_median_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Mean travel time reduction would be {mean_time_reduction:.0f} '+
                 f'minutes. This configuration ranks {time_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* Total travel distance (1 way) reduction would be {total_distance_reduction:,.0f} '+
                 f'km for the period of actuals considered. This configuration ranks {dist_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* The new maximum travel time would be {new_max_time:.0f} minutes. '+
                 f'This configuration ranks {max_time_rank:.0f} '+
                 f'out of {count_options} for this metric.')    
        
        rank_list1 = [new_med_time_rank,
                      prop_reduced_rank,
                      prop_under_nat_median_rank,
                      time_reduction_rank,
                      dist_reduction_rank,
                      max_time_rank]
    
    elif len(sites) == 0 :
        pass
    
    else :
        st.write('Rankings not yet available for multiple sites')
    
   
with col2 :
    sites = [site_dict[site] for site in selected_site_pair2]
    f = kde_plot_quick(df_actuals_augmented, sites, threshold, save_output)
    fig, ax = f
    st.pyplot(fig)
    # new time map
    f = plot_new_prov_times_quick(lsoa_to_all_gdf, 
                              current_sites,
                              sites,
                              False)
    fig, ax = f
    st.pyplot(fig)
    # time impact plot
    f = plot_times_impact_quick(lsoa_to_all_gdf, 
                            current_sites, 
                            sites, 
                            prov_gdf, 
                            threshold,
                            save_output)
    fig, ax = f
    st.pyplot(fig)
    # impact relative to threshold map
    f = plot_time_impact_threshold_quick(lsoa_to_all_gdf, 
                                     current_sites, 
                                     sites,
                                     prov_gdf, 
                                     threshold,
                                     save_output)
    fig, ax = f
    st.pyplot(fig)
    
    # comparison sentences
    if len(sites) == 1 :
        site = ','.join(sites)
        #st.subheader('Comparison with the other configurations with 1 additional site')
        
        df_results_one = df_results.copy().reset_index(drop=False)
        df_results_one = df_results_one[df_results_one['Added_providers'].str.len()==5]
        count_options = len(df_results_one)
        
        med_orig = df_results.loc[site]['Original_median_time']
        med_new = df_results.loc[site]['New_median_time']
        df_results_one['New_median_time_rank'] = df_results_one['New_median_time'].rank(method='min', ascending=True)
        new_med_time_dict = dict(zip(df_results_one['Added_providers'], df_results_one['New_median_time_rank']))
        new_med_time_rank = new_med_time_dict[site]
        
        proportion_reduced = df_results.loc[site]['Proportion_spells_reduced_time']
        df_results_one['Prop_reduced_rank'] = df_results_one['Proportion_spells_reduced_time'].rank(method='min', ascending=False)
        prop_reduced_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Prop_reduced_rank']))
        prop_reduced_rank = prop_reduced_dict[site]
        
        proportion_spells_under_natl_median = df_results.loc[site]['Proportion_spells_under_natl_median']
        df_results_one['Prop_under_nat_median_rank'] = df_results_one['Proportion_spells_under_natl_median'].rank(method='min', ascending=False)
        prop_under_nat_median_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Prop_under_nat_median_rank']))
        prop_under_nat_median_rank = prop_under_nat_median_dict[site]
        
        mean_time_reduction = df_results.loc[site]['Time_reduction_per_spell']
        df_results_one['Time_reduction_rank'] = df_results_one['Time_reduction_per_spell'].rank(method='min', ascending=False)
        time_reduction_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Time_reduction_rank']))
        time_reduction_rank = time_reduction_dict[site]
        
        total_distance_reduction = df_results.loc[site]['Total_distance_reduction']
        df_results_one['Dist_reduction_rank'] = df_results_one['Total_distance_reduction'].rank(method='min', ascending=False)
        dist_reduction_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Dist_reduction_rank']))
        dist_reduction_rank = dist_reduction_dict[site]
        
        new_max_time = df_results.loc[site]['New_maximum_time']
        df_results_one['Max_time_rank'] = df_results_one['New_maximum_time'].rank(method='min', ascending=True)
        max_time_dict = dict(zip(df_results_one['Added_providers'], df_results_one['Max_time_rank']))
        max_time_rank = max_time_dict[site]
        
        st.markdown('#### Impact of additional site at {} on key travel time metrics'.format(selected_site_pair2[0]))
        
        st.markdown(f'* Median travel for Kent and Medway patients reduced '+
                 f'from {med_orig:.0f} to {med_new:.0f} minutes. '+
                 f'This configuration ranks {new_med_time_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced for {100*proportion_reduced:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_reduced_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown('* Travel times would be reduced to less than the national median '+
                 f'for {100*proportion_spells_under_natl_median:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_under_nat_median_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Mean travel time reduction would be {mean_time_reduction:.0f} '+
                 f'minutes. This configuration ranks {time_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* Total travel distance (1 way) reduction would be {total_distance_reduction:,.0f} '+
                 f'km for the period of actuals considered. This configuration ranks {dist_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* The new maximum travel time would be {new_max_time:.0f} minutes. '+
                 f'This configuration ranks {max_time_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        rank_list2 = [new_med_time_rank,
                      prop_reduced_rank,
                      prop_under_nat_median_rank,
                      time_reduction_rank,
                      dist_reduction_rank,
                      max_time_rank]
    
    elif len(sites) == 2 :
        sites.sort()
        site = ','.join(sites)
        st.subheader('Comparison with the other configurations with 2 additional sites')
        
        df_results_two = df_results.copy().reset_index(drop=False)
        df_results_two = df_results_two[df_results_two['Added_providers'].str.len()==11]
        count_options = len(df_results_two)
    
        med_orig = df_results.loc[site]['Original_median_time']
        med_new = df_results.loc[site]['New_median_time']
        df_results_two['New_median_time_rank'] = df_results_two['New_median_time'].rank(method='min', ascending=True)
        new_med_time_dict = dict(zip(df_results_two['Added_providers'], df_results_two['New_median_time_rank']))
        new_med_time_rank = new_med_time_dict[site]
        
        proportion_reduced = df_results.loc[site]['Proportion_spells_reduced_time']
        df_results_two['Prop_reduced_rank'] = df_results_two['Proportion_spells_reduced_time'].rank(method='min', ascending=False)
        prop_reduced_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Prop_reduced_rank']))
        prop_reduced_rank = prop_reduced_dict[site]
        
        proportion_spells_under_natl_median = df_results.loc[site]['Proportion_spells_under_natl_median']
        df_results_two['Prop_under_nat_median_rank'] = df_results_two['Proportion_spells_under_natl_median'].rank(method='min', ascending=False)
        prop_under_nat_median_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Prop_under_nat_median_rank']))
        prop_under_nat_median_rank = prop_under_nat_median_dict[site]
        
        mean_time_reduction = df_results.loc[site]['Time_reduction_per_spell']
        df_results_two['Time_reduction_rank'] = df_results_two['Time_reduction_per_spell'].rank(method='min', ascending=False)
        time_reduction_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Time_reduction_rank']))
        time_reduction_rank = time_reduction_dict[site]
        
        total_distance_reduction = df_results.loc[site]['Total_distance_reduction']
        df_results_two['Dist_reduction_rank'] = df_results_two['Total_distance_reduction'].rank(method='min', ascending=False)
        dist_reduction_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Dist_reduction_rank']))
        dist_reduction_rank = dist_reduction_dict[site]
        
        new_max_time = df_results.loc[site]['New_maximum_time']
        df_results_two['Max_time_rank'] = df_results_two['New_maximum_time'].rank(method='min', ascending=True)
        max_time_dict = dict(zip(df_results_two['Added_providers'], df_results_two['Max_time_rank']))
        max_time_rank = max_time_dict[site]
        
        st.markdown('#### Impact of additional sites on key travel time metrics:')
        st.markdown(f'#### {selected_site_pair2[0]}')
        st.markdown(f'#### {selected_site_pair2[1]}')
        
        st.markdown(f'* Median travel for Kent and Medway patients reduced '+
                 f'from {med_orig:.0f} to {med_new:.0f} minutes. '+
                 f'This configuration ranks {new_med_time_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced for {100*proportion_reduced:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_reduced_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Travel times would be reduced to less than the national median '+
                 f'for {100*proportion_spells_under_natl_median:.0f}% '+
                 'of the Kent and Medway patients, based on historic activity. '+
                 f'This configuration ranks {prop_under_nat_median_rank:.0f} out of '+
                 f'{count_options} for this metric.')
        
        st.markdown(f'* Mean travel time reduction would be {mean_time_reduction:.0f} '+
                 f'minutes. This configuration ranks {time_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* Total travel distance (1 way) reduction would be {total_distance_reduction:,.0f} '+
                 f'km for the period of actuals considered. This configuration ranks {dist_reduction_rank:.0f} '+
                 f'out of {count_options} for this metric.')
        
        st.markdown(f'* The new maximum travel time would be {new_max_time:.0f} minutes. '+
                 f'This configuration ranks {max_time_rank:.0f} '+
                 f'out of {count_options} for this metric.')    
        
        rank_list2 = [new_med_time_rank,
                      prop_reduced_rank,
                      prop_under_nat_median_rank,
                      time_reduction_rank,
                      dist_reduction_rank,
                      max_time_rank]
    
    elif len(sites) == 0 :
        pass
    
    else :
        st.write('Rankings not yet available for multiple sites')




if len(sites) == 0 :
        st.write('The maps and chart above show travel times with no additional '+
                 'sites. Add sites from the select box on the left to see the '+
                 'predicted impact on travel times.')

elif len(selected_site_pair1) == 1 and len(selected_site_pair2) == 1 :
    count_metric1 = sum([rank_list1[i]<rank_list2[i] for i in range(len(rank_list1))])
    count_metric2 = sum([rank_list2[i]<rank_list1[i] for i in range(len(rank_list2))])
    if count_metric1 > count_metric2 :
        st.markdown(f'### Comparing these 2 configurations we see the option of')
        st.markdown(f'## {selected_site_pair1[0]}')
        st.markdown(f'### is superior in {count_metric1} out of {len(rank_list1)} metrics.')
   
    elif count_metric2 > count_metric1 :
        st.markdown('### Comparing these 2 configurations we see the option of')
        st.markdown(f'## {selected_site_pair2[0]}')
        st.markdown(f'### is superior in {count_metric2} out of {len(rank_list2)} metrics.')

elif len(selected_site_pair1) == 2 and len(selected_site_pair2) == 2 :
    count_metric1 = sum([rank_list1[i]<rank_list2[i] for i in range(len(rank_list1))])
    count_metric2 = sum([rank_list2[i]<rank_list1[i] for i in range(len(rank_list2))])
    if count_metric1 > count_metric2 :
        st.markdown(f'### Comparing these 2 configurations we see the option of')
        st.markdown(f'## {selected_site_pair1[0]}')
        st.markdown(f'## {selected_site_pair1[1]}')
        st.markdown(f'### is superior in {count_metric1} out of {len(rank_list1)} metrics.')
   
    elif count_metric2 > count_metric1 :
        st.markdown('### Comparing these 2 configurations we see the option of')
        st.markdown(f'## {selected_site_pair2[0]}')
        st.markdown(f'## {selected_site_pair2[1]}')
        st.markdown(f'### is superior in {count_metric2} out of {len(rank_list2)} metrics.')


else :
    pass










