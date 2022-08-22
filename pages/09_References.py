import streamlit as st
import pandas as pd
st.title('References')

'To add'
st.write('Include lists of procedure codes, providers as expandable lists')

st.write('Data sources, SQL, software used, relevant NHS policies on this '+
         'service and reducing travel times justification')

#st.markdown('#### Sites with > 10 procedures nationally:')
national_provider_filename = 'valve_providers.csv'
#activity_data_filename = "Cardiac valves_national v0.2.csv"
activity_data_minimal_filename = "activity_data_minimal.csv"
procedure_ref = "opcs_table.csv"


def get_national_providers_list(national_provider_filename, activity_data_minimal_filename) :
    df_prov = pd.read_csv(national_provider_filename)
    df_activity = pd.read_csv(activity_data_minimal_filename)
    df_count = df_activity['Der_Provider_Site_Code'].value_counts()
    prov_code_list = df_count[df_count > 10]
    nat_prov10 = df_prov[df_prov['Provider_Site_Code'].isin(list(prov_code_list.index))]
    return nat_prov10


df_opcs = pd.read_csv(procedure_ref)
with st.expander("Cardiac valve procedures list", 
                 expanded=False) :
    st.write(df_opcs)

with st.expander("Sites with > 10 procedures nationally", 
                 expanded=False) :
    st.write(get_national_providers_list(national_provider_filename, 
                                     activity_data_minimal_filename))
