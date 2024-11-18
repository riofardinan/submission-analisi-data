import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.title("Dashboard Kualitas Udara dan Curah Hujan di Stasiun Guanyuan")

air_quality_df = pd.read_csv("dashboard/main_data.csv")

st.header("Trend Kualitas Udara")
st.write("Visualisasi tren kualitas udara berdasarkan parameter PM2.5, PM10, SO2, NO2, O3, dan CO.")

pollutants = ["PM2.5", "PM10", "SO2", "NO2", "O3", "CO"]
selected_pollutant = st.selectbox("Pilih polutan untuk visualisasi:", pollutants)

years = air_quality_df['year'].unique().tolist()
years.insert(0, 'Semua')
selected_year = st.selectbox("Pilih tahun untuk visualisasi:", years, key="pollution_year")

air_quality_df['date'] = pd.to_datetime(air_quality_df[['year', 'month', 'day']])

if selected_year != 'Semua':
    air_quality_df = air_quality_df[air_quality_df['year'] == int(selected_year)]

trend_data = air_quality_df.groupby('date')[selected_pollutant].mean()

fig, ax = plt.subplots(figsize=(10, 6))

if selected_year != 'Semua':
    trend_data_monthly = air_quality_df.groupby([air_quality_df['date'].dt.month])[selected_pollutant].mean()
    months = range(1, 13)
    
    filtered_months = trend_data_monthly.dropna().index
    
    ax.plot(filtered_months, trend_data_monthly.loc[filtered_months], label=selected_pollutant, color="orange")
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    ax.set_title(f"Trend {selected_pollutant} di Stasiun Guanyuan ({selected_year})", fontsize=14)
    ax.set_xlabel("Bulan", fontsize=12)
else:
    ax.plot(trend_data.index, trend_data.values, label=selected_pollutant, color="orange")
    ax.set_title(f"Trend {selected_pollutant} di Stasiun Guanyuan", fontsize=14)
    ax.set_xlabel("Tahun", fontsize=12)

ax.set_ylabel(f"Konsentrasi {selected_pollutant} (µg/m³)", fontsize=12)
ax.legend()

st.pyplot(fig)

st.header("Tren Curah Hujan")
st.write("Visualisasi tren curah hujan berdasarkan data historis di Stasiun Guanyuan.")

rain_trend_data = air_quality_df.groupby('date')['RAIN'].mean()

fig, ax = plt.subplots(figsize=(10, 6))

if selected_year != 'Semua':
    trend_data_monthly = air_quality_df.groupby([air_quality_df['date'].dt.month])["RAIN"].mean()
    months = range(1, 13)
    
    filtered_months = trend_data_monthly.dropna().index
    
    ax.plot(filtered_months, trend_data_monthly.loc[filtered_months], label="RAIN", color="blue")
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
    ax.set_title(f"Trend Curah Hujan di Stasiun Guanyuan ({selected_year})", fontsize=14)
    ax.set_xlabel("Bulan", fontsize=12)
else:
    ax.plot(rain_trend_data.index, rain_trend_data.values, label="RAIN", color="blue")
    ax.set_title(f"Trend Curah Hujan di Stasiun Guanyuan", fontsize=14)
    ax.set_xlabel("Tahun", fontsize=12)

ax.set_ylabel("Curah Hujan (mm)", fontsize=12)
ax.legend()

st.pyplot(fig)


st.header("Korelasi antara Polutan dan Faktor Cuaca")
weather_factors = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]

correlation_data = air_quality_df[pollutants + weather_factors]
correlation_matrix = correlation_data.corr()

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax, cbar_kws={'label': 'Korelasi'})
ax.set_title("Heatmap antara Polutan dan Faktor Cuaca", fontsize=16)
st.pyplot(fig)

stations_coordinates = {
    "Aotizhongxin": [40.0378, 116.4188],
    "Changping": [40.2181, 116.2215],
    "Dingling": [40.2413, 116.2343],
    "Guanyuan": [39.9298, 116.3655],
    "Huairou": [40.3243, 116.6318],
    "Nongzhanguan": [39.9336, 116.4667],
    "Shunyi": [40.1282, 116.6546],
    "Tiantan": [39.8869, 116.4129],
    "Wanliu": [39.9741, 116.3138],
    "Wanshouxigong": [39.8787, 116.3549],
}

st.header("Sebaran Kualitas Udara di Beijing")
st.markdown("""
Dashboard ini menampilkan peta interaktif stasiun pengukuran kualitas udara di Beijing,
dengan indikator rata-rata nilai PM2.5 per stasiun.
""")

station_data = []
for station, coords in stations_coordinates.items():
    url_station = f"data/PRSA_Data_{station}_20130301-20170228.csv"
    df = pd.read_csv(url_station)
    avg_pm25 = df['PM2.5'].mean()
    station_data.append((station, coords[0], coords[1], avg_pm25))

map_beijing = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

for station, lat, lon, pm25 in station_data:
    folium.CircleMarker(
        location=[lat, lon],
        radius=pm25 / 10,
        popup=f"{station}: {pm25:.2f} µg/m³",
        color="red" if pm25 > 75 else "green",
        fill=True,
        fill_color="red" if pm25 > 75 else "green",
        fill_opacity=0.7,
    ).add_to(map_beijing)

heat_data = [[lat, lon, pm25] for _, lat, lon, pm25 in station_data]
HeatMap(heat_data).add_to(map_beijing)

st.markdown("### Peta Interaktif Kualitas Udara")
st_folium(map_beijing, width=800, height=600)
