import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_compact_currency
sns.set(style='dark')

#import data
all_data = pd.read_csv('https://raw.githubusercontent.com/Maryulianti/Data-Analysis-Project/main/dashboard/main_data.csv')

datetime_columns = ['date']
all_data.sort_values(by='date', inplace=True)
all_data.reset_index(inplace=True)

for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

#menyiapkan dataframe
def create_month_recap(df):
    plot_month = df['month'].astype(str)
    plot_year = df['year'].astype(str)
    df['year_month'] = plot_month + ' ' + plot_year
    df['total_sum'] = df.groupby('year_month')['total'].transform('sum')
    return df[['year_month', 'total_sum']]

def create_season_recap(df):
    season_recap = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_recap

def create_weather_recap(df):
    weather_recap = df.groupby(by='weather').agg({
    'total': 'mean'
    }).reset_index()
    return weather_recap

def create_workingday_hour_recap(df):
    filter_workingday = df[(df['workingday'] == 1)]
    workingday_hour_recap = filter_workingday.groupby(by='hour').agg({
    'total': 'sum'
    }).reset_index()
    return workingday_hour_recap

def create_holiday_hour_recap(df):
    filter_holiday = df[(df['holiday'] == 1)|(df['workingday'] == 0)]
    holiday_hour_recap = filter_holiday.groupby(by='hour').agg({
    'total': 'sum'
    }).reset_index()
    return holiday_hour_recap

def create_rfm_recap(df):
    rfm_df = df.groupby(by='hour', as_index=False).agg({
    'date': 'max',
    'instant': 'nunique',
    'total': 'sum'
    })
    rfm_df.columns = ['hour', 'last_order_date', 'order_count', 'revenue'] # mengganti nama kolom

    # perhitungan recency per hari
    rfm_df['last_order_date'] = rfm_df['last_order_date'].dt.date
    recent_date = df['date'].dt.date.max()
    rfm_df['recency'] = rfm_df['last_order_date'].apply(lambda x: (recent_date - x).days)

    rfm_df.drop('last_order_date', axis=1, inplace=True)  # Drop kolom 'last_order_date'
    return rfm_df

def create_daily_recap(df):
    daily_recap = df.groupby(by='date').agg({
        'total': 'sum'
    }).reset_index()
    return daily_recap

def create_registered_recap(df):
    registered_recap = df.groupby(by='date').agg({
        'registered': 'sum'
    }).reset_index()
    return registered_recap

def create_casual_recap(df):
    casual_recap = df.groupby(by='date').agg({
        'casual': 'sum'
    }).reset_index()
    return casual_recap

def create_temp_recap(df):
    temp_recap = df.groupby(by='date').agg({
        'temp': 'mean'
    }).reset_index()
    return temp_recap

def create_hum_recap(df):
    hum_recap = df.groupby(by='date').agg({
        'hum': 'mean'
    }).reset_index()
    return hum_recap

#membuat filter tanggal pada sidebar
max_date = pd.to_datetime(all_data['date']).dt.date.max()
min_date = pd.to_datetime(all_data['date']).dt.date.min()

with st.sidebar:
    st.image('https://raw.githubusercontent.com/Maryulianti/Data-Analysis-Project/main/dashboard/logo.png')

    #input start_date dan end_date
    start_date, end_date = st.date_input(
        label='Pilih  Rentang Waktu',
        max_value=max_date,
        min_value=min_date,
        value=[min_date, max_date]
    )

main_df = all_data[(all_data['date'] >= str(start_date)) &
                (all_data['date'] <= str(end_date))]

month_recap_df = create_month_recap(main_df)
season_recap_df = create_season_recap(main_df)
weather_recap_df = create_weather_recap(main_df)
workingday_hour_recap_df = create_workingday_hour_recap(main_df)
holiday_hour_recap_df = create_holiday_hour_recap(main_df)
rfm_recap_df = create_rfm_recap(main_df)
daily_recap_df = create_daily_recap(main_df)
casual_recap_df = create_casual_recap(main_df)
registered_recap_df = create_registered_recap(main_df)
temp_recap_df = create_temp_recap(main_df)
hum_recap_df = create_hum_recap(main_df)

#Membuat UI
st.header('Bike Rental Company')

#Subheader Rent Summary
st.subheader('Bike Rental Company Summary')
col1, col2, col3= st.columns(3)

with col1:
    daily_recap = daily_recap_df['total'].sum()
    st.metric('Total User', value= daily_recap)

with col2:
    registered_recap = registered_recap_df['registered'].sum()
    st.metric('Registered User', value= registered_recap)

with col3:
    casual_recap = casual_recap_df['casual'].sum()
    st.metric('Casual User', value= casual_recap)


#Subheader Monthly Recap
st.subheader('Monthly Rent Recap')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    month_recap_df['year_month'],
    month_recap_df['total_sum'],
    marker='o',
    linewidth=5,
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)

st.pyplot(fig)

#Subheader Season and Weather Recap
st.subheader('Season and Weather Recap')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y='registered',
        x='season',
        data=season_recap_df.sort_values(by='registered', ascending=False),
        color='tab:blue',
        label='Registered User',
        ax=ax
    )
    sns.barplot(
        y='casual',
        x='season',
        data=season_recap_df.sort_values(by='casual', ascending=False),
        color='tab:orange',
        label='Casual User',
        ax=ax
    )
    ax.set_title('Number of Rent by Season', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    ax.legend(fontsize=20)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y='total',
        x='weather',
        data=weather_recap_df.sort_values(by='total', ascending=False),
        ax=ax
    )

    ax.set_title('Mean of Rent by Weather', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

#Subheader Workingday and Holiday Hour Recap
st.subheader('Workingday and Holiday Hour Recap')

col1, col2 = st.columns(2)

with col1:
    workingday_max_col = workingday_hour_recap_df['total'].idxmax()
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y='total',
        x='hour',
        data=workingday_hour_recap_df,
        color='tab:blue',
        ax=ax
    )
    plt.bar(workingday_max_col, workingday_hour_recap_df.loc[workingday_max_col, 'total'], color='tab:red', label='Most Rented Hour')
    ax.set_title('Workingday Rent Hour Recap', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    ax.legend(fontsize=20)
    st.pyplot(fig)

with col2:
    holiday_max_col = holiday_hour_recap_df['total'].idxmax()
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y='total',
        x='hour',
        data=holiday_hour_recap_df,
        color='tab:blue',
        ax=ax
    )
    plt.bar(holiday_max_col, holiday_hour_recap_df.loc[holiday_max_col, 'total'], color='tab:red', label='Most Rented Hour')
    ax.set_title('Holiday Rent Hour Recap', loc='center', fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    ax.legend(fontsize=20)
    st.pyplot(fig)

#Subheader RFM Recap
st.subheader('RFM')

col1, col2, col3 = st.columns(3)

with col1:
    top_recency = rfm_recap_df.sort_values(by='recency', ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=top_recency,
        x='hour',
        y='recency',
        color='tab:blue',
        ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title('Recency (days)', loc='center', fontsize=50)
    ax.tick_params(axis ='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    top_frequency = rfm_recap_df.sort_values(by='order_count', ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=top_frequency,
        x='hour',
        y='order_count',
        color='tab:blue',
        ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title('Frequency', loc='center', fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col3:
    top_monetary = rfm_recap_df.sort_values(by='revenue', ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=top_monetary,
        x='hour',
        y='revenue',
        color='tab:blue',
        ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title('Monetary', loc='center', fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.caption('Copyright (c) Bike Rental Company 2023')

