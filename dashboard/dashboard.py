import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def get_total_count_by_hour_df(hour_df):
  hour_count_df =  hour_df.groupby(by="hours").agg({"count_cr": ["sum"]})
  return hour_count_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count_2011

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def macem_season (day_df): 
    season_df = day_df.groupby(by="season").count_cr.sum().reset_index() 
    return season_df

def create_rfm_recap(hour_df):
    rfm_df = hour_df.groupby(by="hours", as_index=False).agg({
    "dteday": "max",
    "instant": "nunique",
    "count_cr": "sum"
    })
    rfm_df.columns = ["hours", "last_order_date", "order_count", "revenue"]
    # perhitungan recency per hari
    rfm_df["last_order_date"] = rfm_df["last_order_date"].dt.date
    recent_date = hour_df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["last_order_date"].apply(lambda x: (recent_date - x).days)
    
    # Drop kolom 'last_order_date'
    rfm_df.drop("last_order_date", axis=1, inplace=True)
    return rfm_df

days_df = pd.read_csv("https://raw.githubusercontent.com/ardifa24/bike-sharing-dicoding-project/main/dashboard/day_clean.csv")
hours_df = pd.read_csv("https://raw.githubusercontent.com/ardifa24/bike-sharing-dicoding-project/main/dashboard/hour_clean.csv")

datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://jugnoo.io/wp-content/uploads/2022/05/on-demand-bike-sharing-1-1024x506.jpg")
    
        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Range',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
  
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)
rfm_recap_df = create_rfm_recap(main_df_hour)

#Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('BIKE RENTAL ANALYTICS DASHBOARD')

st.subheader('BIKE RENTAL OVERVIEW')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.count_cr.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

st.subheader("Bike Rental Performance in Recent Years")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    days_df["dteday"],
    days_df["count_cr"],
    marker='o', 
    linewidth=2,
    color="#278f02"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Analysis of Bicycle Rental: Highest and Lowest Activity Hours")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5), palette=["#b4d0a6", "#b4d0a6", "#278f02", "#b4d0a6", "#b4d0a6"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Hours with high bike rental activity", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.sort_values(by="hours", ascending=True).head(5), palette=["#b4d0a6", "#b4d0a6", "#b4d0a6", "#b4d0a6", "#278f02"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)",  fontsize=30)
ax[1].set_title("Hours with low bike rental activity", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

st.subheader("Top Rental Volume by Season")

colors = ["#b4d0a6", "#b4d0a6", "#b4d0a6", "#278f02"]
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
        y="count_cr", 
        x="season",
        data=season_df.sort_values(by="season", ascending=False),
        palette=colors,
        ax=ax
    )
ax.set_title("Interseasonal Chart", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

#Subheader RFM Recap
st.subheader('RFM Overview')
 
col1, col2, col3 = st.columns(3)

with col1:
    top_recency = rfm_recap_df.sort_values(by="recency", ascending=True).head(5)
    #membuat bar plot RFM
    fig, ax = plt.subplots(figsize=(10, 6))
    
    #plot top recency
    sns.barplot(
        data=top_recency,
        x="hours",
        y="recency",
        color='tab:green',
        ax=ax
    )
    
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Recency (days)", loc="center", fontsize=50)
    ax.tick_params(axis ='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
    
with col2:
    top_frequency = rfm_recap_df.sort_values(by="order_count", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))
    #plot top frequency
    sns.barplot(
    data=top_frequency,
    x="hours",
    y="order_count",
    color='tab:green',
    ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Frequency", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35) 
    ax.tick_params(axis='y', labelsize=30)  
    st.pyplot(fig) 
    
with col3:
    top_monetary = rfm_recap_df.sort_values(by="revenue", ascending=False).head(5)    
    fig, ax = plt.subplots(figsize=(10, 6))
    #plot top monetary
    sns.barplot(
    data=top_monetary,
    x="hours",
    y="revenue",
    color='tab:green',
    ax=ax
    )
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Monetary", loc="center", fontsize=50)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig) 