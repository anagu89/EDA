import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import holidays
import plotly.express as px
import folium

df_original = pd.read_csv('C:/Users/AnaGu/Downloads/Crime_Data_from_2020_to_Present.csv')
df = df_original.copy()
df = df[['DATE OCC', 'TIME OCC', 'AREA NAME', 'Crm Cd Desc', 'Vict Age', 'Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc', 'LAT', 'LON']]

nan = df.isnull().sum()
rows = len(df)
nan_percentage = (nan / rows) * 100

df['Vict Sex'] = df['Vict Sex'].fillna('X')
df['Vict Descent'] = df['Vict Descent'].fillna('X')
df['Premis Desc'] = df['Premis Desc'].fillna(df['Premis Desc'].mode()[0])
df = df.drop('Weapon Desc', axis = 1)

nan = df.isnull().sum()
rows = len(df)
nan_percentage = (nan / rows) * 100

df['Vict Age'] = df['Vict Age'].astype(int)
df['Vict Age'] = df['Vict Age'].replace([-1, -2, -3, -4, 0, 120], 30)

vict_sex_unknown = ((df['Vict Sex'] == '-') + (df['Vict Sex'] == 'H'))
df['Vict Sex'] = df['Vict Sex'].replace(['-', 'H'], 'X')
df['Vict Descent'] = df['Vict Descent'].replace(['-'], 'H')

df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
df['DATE'] = df['DATE OCC'].dt.date 
df.insert(1, 'DATE', df.pop('DATE'))

df['DAY WEEK'] = df['DATE OCC'].dt.day_name()
df.insert(2, 'DAY WEEK', df.pop('DAY WEEK'))

us_holidays = holidays.US(state='CA', years=df['DATE OCC'].dt.year.unique())

df['DAY TYPE'] = df.apply(
    lambda row: 'DAY OFF' if row['DATE'] in us_holidays
    else ('WEEKEND' if row['DATE OCC'].weekday() >= 5 else 'WEEKDAY'),
    axis=1
)
df.insert(3, 'DAY TYPE', df.pop('DAY TYPE'))
df = df.drop('DATE OCC', axis = 1)

df['TIME OCC'] = df['TIME OCC'].astype(str)
df['TIME OCC'] = df['TIME OCC'].str.zfill(4)
df['TIME OCC'] = df['TIME OCC'].str.slice(0, 2) + ':' + df['TIME OCC'].str.slice(2, 4)
df['TIME OCC'] = df['TIME OCC'].apply(lambda x: dt.datetime.strptime(x, "%H:%M").time())

df = df.rename(columns = {'TIME OCC': 'TIME'})

# HIPÓTESIS 1

def get_season(date):
    month = date.month
    if month in [3, 4, 5]:
        return 'Primavera'
    elif month in [6, 7, 8]:
        return 'Verano'
    elif month in [9, 10, 11]:
        return 'Otoño'
    else:
        return 'Invierno'

df['ESTACION'] = df['DATE'].apply(get_season)

conteo_estaciones = df['ESTACION'].value_counts().reindex(['Primavera', 'Verano', 'Otoño', 'Invierno'])

df_plot = conteo_estaciones.reset_index()
df_plot.columns = ['Estacion', 'Frecuencia']

plt.figure(figsize=(8, 5))
sns.barplot(data=df_plot, x='Estacion', y='Frecuencia', hue='Estacion', palette='Set2', dodge=False)
plt.title('Frecuencia de Estaciones del Año')
plt.xlabel('Estación')
plt.ylabel('Cantidad de Fechas')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.ylim(240000,260000)
plt.savefig("hipotesis_1.png")
plt.show()

# HIPÓTESIS 2

def clasificar_franja(t):
    if dt.time(6, 0) <= t < dt.time(14, 0):
        return 'mañana'
    elif dt.time(14, 0) <= t < dt.time(22, 0):
        return 'tarde'
    else: 
        return 'noche'

df['FRANJA'] = df['TIME'].apply(clasificar_franja)
conteo_franjas = df['FRANJA'].value_counts()

colores = {'mañana': "#FF9D00", 'tarde': "#055B27", 'noche': "#006282"}

colors = [colores[franja] for franja in conteo_franjas.index]

plt.figure(figsize=(6, 6))

wedges, texts, autotexts = plt.pie(conteo_franjas, 
        labels = conteo_franjas.index, 
        autopct = '%1.1f%%', 
        startangle = 90, 
        colors = colors,
        textprops={'fontsize': 14})

for autotext in autotexts:
    autotext.set_fontsize(20)

plt.title('Distribución por franja horaria')
plt.axis('equal')
plt.savefig("hipotesis_2.png")
plt.show()

# HIPÓTESIS 3

sorted_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['DAY WEEK'] = pd.Categorical(df['DAY WEEK'], categories = sorted_days, ordered=True)

sns.countplot(data = df, x = 'DAY WEEK', order = sorted_days)
plt.title('Días de la semana')
plt.xlabel('Día de la semana')
plt.ylabel('Número de registros')
plt.xticks(rotation=45)
plt.ylim(135000,155000)
plt.savefig("hipotesis_3.png")
plt.show()

print(df['DAY WEEK'].value_counts(normalize=True).reindex(sorted_days))

# HIPÓTESIS 4

def plot_grouped_boxplots(df, cat_col, num_col):
    unique_cats = df[cat_col].unique()
    num_cats = len(unique_cats)
    group_size = 5

    for i in range(0, num_cats, group_size):
        subset_cats = unique_cats[i:i+group_size]
        subset_df = df[df[cat_col].isin(subset_cats)]
        
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=cat_col, y=num_col, data=subset_df)
        plt.title(f'Boxplots of {num_col} for {cat_col} (Group {i//group_size + 1})')
        plt.xticks(rotation=45)
        plt.savefig("hipotesis_4.png")
        plt.show()

plot_grouped_boxplots(df,"DAY TYPE","Vict Age")

# HIPÓTESIS 5

sns.countplot(data = df, x = 'Vict Sex', color='rosybrown')
plt.title('Distribución del sexo')
plt.ylim(200000,)
plt.savefig("hipotesis_5.png")
plt.show()

print(df['Vict Sex'].value_counts(normalize=True))

# HIPÓTESIS 6

top10 = df['Crm Cd Desc'].value_counts().head(10)

df_top10 = top10.reset_index()
df_top10.columns = ['Tipo de delito', 'Frecuencia']

fig = px.bar(
    df_top10,
    x='Frecuencia',
    y='Tipo de delito',
    orientation='h',
    title='Top 10 delitos más comunes',
    color_discrete_sequence=["#b4781f"]  
)

fig.update_layout(yaxis=dict(autorange='reversed'))
plt.savefig("hipotesis_6.png")
fig.show()

# MAPA 1

df_map = df[['LAT', 'LON']].copy()
df_map = pd.DataFrame(df_map)
df_map = df_map.head(10000)

fig = px.scatter_mapbox(df_map,
                        lat="LAT",
                        lon="LON",
                        zoom=10,
                        center={"lat": 34.05, "lon": -118.25},  # Los Ángeles city centre
                        height=600)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(title="Coordenadas en Los Ángeles")
fig.write_html("mapa_1.html")
fig.show()

# MAPA 2

# dataframe con LAT y LON
df_map = df[['LAT', 'LON']].copy()
df_map = pd.DataFrame(df_map)
df_map = df_map.head(500)

# mapa de Los Ángeles
map = folium.Map(location=[34.05, -118.25], zoom_start=11)

# marcadores sin texto
for _, row in df_map.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LON']],
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(map)

# guardar como archivo HTML
map.save("mapa_2.html")