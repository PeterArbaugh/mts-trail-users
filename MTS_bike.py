import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title('Mountain to Sound Bike Traffic & Seattle Weather')

st.write(
    """
    Edit: [Here's another demo app I created recently with a bit more interactivity.](https://share.streamlit.io/peterarbaugh/simple-movie-recommender/main)

    I combined 2 data sets to look at weather and number of trail users on the Mountains to Sound Trail in Seattle.
    
    Data sources
    - [MTS Trail west of I-90 Bridge Bicycle and Pedestrian Counter](https: // data.seattle.gov/Transportation/MTS-Trail-west-of-I-90-Bridge-Bicycle-and-Pedestri/u38e-ybnc)
    - [Did it rain in Seattle? 1948-2017](https: // www.kaggle.com/rtatman/did-it-rain-in-seattle-19482017)
    """
)


MTS_DATA_URL = (
    'MTS_Trail_west_of_I-90_Bridge_Bicycle_and_Pedestrian_Counter.csv')
WEATHER_DATA_URL = ('seattleWeather_1948-2017.csv')


@st.cache
def load_data(MTS, WEATHER):
    # load trail user data
    mts_data = pd.read_csv(MTS_DATA_URL)
    mts_data['Date'] = pd.to_datetime(mts_data['Date'])
    mts_data = mts_data.groupby([mts_data['Date'].dt.date]).sum()
    mts_data = mts_data.reset_index()

    # load weather data
    w_data = pd.read_csv(WEATHER_DATA_URL)
    w_data['DATE'] = pd.to_datetime(w_data['DATE'])
    w_data['DATE'] = w_data['DATE'].dt.date

    # merge
    data = pd.merge(mts_data, w_data, how='inner',
                    left_on='Date', right_on='DATE')

    # drop extra date column
    data.drop('DATE', axis=1, inplace=True)

    # set index to datetime for later resample
    data['Date'] = pd.to_datetime(data['Date'])
    data.index = pd.DatetimeIndex(data['Date'])

    return data


data = load_data(MTS_DATA_URL, WEATHER_DATA_URL)

st.markdown(
    'Removing outliers is recommended as a marathon and half-marathon route crossed this bridge in 2016.')
if st.checkbox('Remove outliers'):
    data = data[data['MTS Trl West of I-90 Bridge Total']
                .isin(range(0, 7000))]

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# stacked bar chart of peds and cyclists by week
# ideally, add a multiselect
st.subheader('Pedestrians and cyclists by week, 2014 - 2017')
st.bar_chart(data[['Date', 'Ped East', 'Ped West',
             'Bike East', 'Bike West']].resample('W').sum())

# scatter plot of precipitation by number of cyclists
st.subheader('Precipitation and number of MTS Trail users')
scatter = alt.Chart(data).mark_circle(size=60).encode(
    x='PRCP',
    y='MTS Trl West of I-90 Bridge Total',
    tooltip=['Date', 'Ped East', 'Ped West', 'Bike East', 'Bike West']
).interactive()

st.altair_chart(scatter)

# binned heatmap https://altair-viz.github.io/gallery/binned_heatmap.html
st.subheader('Daily high temperature and number of MTS Trail users')
scatter = alt.Chart(data).mark_rect().encode(
    alt.X('TMAX', bin=alt.Bin(maxbins=30)),
    alt.Y('MTS Trl West of I-90 Bridge Total', bin=alt.Bin(maxbins=30)),
    alt.Color('PRCP', scale=alt.Scale(scheme='greenblue')),
    tooltip=['Date', 'Ped East', 'Ped West', 'Bike East', 'Bike West']
).interactive()

st.altair_chart(scatter)
