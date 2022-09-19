# Page for intro

import streamlit as st

st.title('Reducing Travel Times to Treatment for Cardiac Patients in South East England')

st.markdown('This project was created as part of the [HSMA4 programme](https://sites.google.com/nihr.ac.uk/hsma).')

st.markdown('_Glenn Ubly - NHS England and Improvement<br>Janine James - NHS England and Improvement<br>Antonia Drummond - NHS England and Improvement<br>Victor Yu - Hertfordshire County Council_<br>_Adam Scull - Mentor_', unsafe_allow_html=True)

st.markdown('"Moving care closer to home" has become a high-priority goal for many NHS commissioning bodies, in particular for the South East Specialised Commissioning region, with a specific focus on moving cardiac activity away from London and back in to the South East region for all type of referral pathways.')

st.markdown('Bringing care closer to home can reduce travel times for patients, with it being a critical factor in aspects of healthcare delivery, patient satisfaction, health outcomes and more.')

st.markdown('Initial scoping of our project focused on all cardiac activity, but we later honed this specifically towards cardiac valve procedures and the Kent and Medway region.')


with st.expander('Resources used:',
                 expanded=False) :
    st.markdown('This is app is created and shared using using [Streamlit](https://streamlit.io/) ')
    st.markdown('Time and distance calculations from [Routino](https://www.routino.org/uk/) ')
    st.markdown('NHS activity data from [National Commissioning Data Repository](https://www.ardengemcsu.nhs.uk/services/business-intelligence/ncdr/) ')
    st.markdown('LSOA geographic data from [Cambridgeshire Insight Open Data](https://data.cambridgeshireinsight.org.uk/dataset/output-areas)')
    st.markdown('NHS CCG geographic data from [Office for National Statistics](https://geoportal.statistics.gov.uk/maps/d6acd30ad71f4e14b4de808e58d9bc4c)')
    st.markdown('##### Python dependencies:')
    st.text("""
            bokeh==2.4.3
            geopandas==0.9.0
            matplotlib==3.5.1
            numpy==1.22.3
            pandas==1.4.2
            Pillow==9.2.0
            scipy==1.7.3
            seaborn==0.11.2
            streamlit==1.11.1
            """)
