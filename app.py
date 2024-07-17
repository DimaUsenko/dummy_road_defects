import folium
from streamlit_folium import folium_static

from folium import IFrame

import streamlit as st
import os
from PIL import Image
import base64
import pandas as pd

st.title("Система мониторинга дорожных дефектов")

# st.header('Детекция дефектов на дорожном покрытии')


st.file_uploader('Загрузка результатов мониторинга:')

options = ["YOLOv8-x-640", "Detectron2"]

# Создание выпадающего списка
selected_option = st.selectbox("Выберите модель:", options)

st.button('Обработать данные')
st.divider()

# Путь к папке с изображениями
image_folder = 'data/label_draw'

# Получение списка всех изображений в папке
image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

# Настройка интерфейса Streamlit


# Ввод количества отображаемых изображений
# num_images = st.slider('Количество изображений для отображения', min_value=1, max_value=len(image_files), value=10)

# Отображение изображений в гриде
st.subheader('Галерея')
cols = st.columns(4)  # Количество столбцов в гриде

for i, image_file in enumerate(image_files[:8]):
    img_path = os.path.join(image_folder, image_file)
    img = Image.open(img_path)
    col = cols[i % 4]
    col.image(img, caption=image_file, use_column_width=True)

data = {
    'UID': [
        347, 349, 461, 462, 463, 464, 465, 466, 467, 468,
        469, 470, 471, 472, 473, 474, 475, 476, 477, 478
    ],
    'Широта': [
        43.431536, 43.430032, 43.429724, 43.428977, 43.430678,
        43.431781, 43.432670, 43.430229, 43.430839, 43.430258,
        43.431722, 43.431046, 43.432931, 43.429909, 43.427704,
        43.429103, 43.429891, 43.427586, 43.428107, 43.431627
    ],
    'Долгота': [
        43.578934, 43.577205, 43.576473, 43.575920, 43.575432,
        43.575009, 43.575782, 43.576416, 43.578782, 43.575196,
        43.575001, 43.574294, 43.579325, 43.574870, 43.576455,
        43.578309, 43.576577, 43.578008, 43.575488, 43.577594
    ],
    'Площадь': [
        6, 3, 3.5, 5, 2, 2.5, 4, 1.5, 6.5, 1,
        5.5, 2.2, 3.1, 4.2, 2.8, 4.5, 5.2, 3.2, 6.1, 2.6
    ],
    'Код': [
        '3.1', '3.2', '3.1', '3.4', '3.3',
        '3.4', '3.4', '3.1', '3.2', '3.1',
        '3.1', '3.1', '3.1', '3.2', '3.2',
        '3.3', '3.1', '3.2', '3.2', '3.1'
    ],
    'Класс': [
        'Выбоина', 'Выкрашивание', 'Выбоина', 'Проломы', 'Шелушение',
        'Проломы', 'Проломы', 'Выбоина', 'Выкрашивание', 'Выбоина',
        'Выбоина', 'Выбоина', 'Выбоина', 'Выкрашивание', 'Выкрашивание',
        'Шелушение', 'Выбоина', 'Выкрашивание', 'Выкрашивание', 'Выбоина'
    ],
    'Дата': [
        '2024-07-01', '2024-07-01', '2024-07-01', '2024-07-01', '2024-07-01', '2024-07-08', '2024-07-08', '2024-07-10',
        '2024-07-10', '2024-07-10',
        '2024-07-13', '2024-07-13', '2024-07-13', '2024-07-13', '2024-07-13', '2024-07-13', '2024-07-13', '2024-07-13',
        '2024-07-21', '2024-07-21'
    ],

    'Путь к изображению': [
                              r'C:\Users\usenk\PycharmProjects\road_defects_serivce\data\images\43.431536_43.578934.png'] * 20
    # Добавьте правильные пути к изображениям
}

# Создание DataFrame
df = pd.DataFrame(data)

# Добавление ссылки на Яндекс.Карты
df['Ссылка'] = df.apply(
    lambda
        row: f'https://yandex.ru/maps/?ll={row["Долгота"]}%2C{row["Широта"]}&mode=search&sll={row["Долгота"]}%2C{row["Широта"]}&text={row["Широта"]}%2C{row["Долгота"]}&z=20',
    axis=1
)

# Создание копии DataFrame без колонки "Путь к изображению"
df_display = df.drop(columns=['Путь к изображению'])

# Интерфейс Streamlit
st.subheader('Сводная таблица')

# Отображение таблицы
st.dataframe(df_display, column_config={
    "Ссылка": st.column_config.LinkColumn(display_text="Яндекс.Карты")
})

# Создание карты с отметками ям
average_lat = df['Широта'].mean()
average_lon = df['Долгота'].mean()
m = folium.Map(location=[average_lat, average_lon], zoom_start=16, attributionControl=0)

# Добавление маркеров с данными и изображениями
for idx, row in df.iterrows():
    # Создание всплывающего окна с изображением
    with open(row['Путь к изображению'], 'rb') as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    yandex_link = f"https://yandex.ru/maps/?ll={row['Долгота']}%2C{row['Широта']}&mode=search&sll={row['Долгота']}%2C{row['Широта']}&text={row['Широта']}%2C{row['Долгота']}&z=20"
    html = f"""
            <b>UID: {row['UID']}</b><br>
            Оценочная площадь: {row['Площадь']} м<sup>2</sup><br>
            Дата идентификации: {row['Дата']}<br>
            <a href="{yandex_link}" target="_blank">Открыть в Яндекс.Карты</a><br>
            
            <img src="data:image/png;base64,{encoded}" width="300">
        """

    iframe = IFrame(html, width=340, height=280)
    popup = folium.Popup(iframe)

    # Добавление маркера на карту
    folium.Marker(
        location=[row['Широта'], row['Долгота']],
        popup=popup,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# Отображение карты
st.subheader('Карта дефектов')
folium_static(m)

import plotly.express as px

st.header('Статистика')

st.subheader('Общие показатели', help='По сравнению с предыдущим мониторингом')

current_total_defects = len(df)
current_total_area = df['Площадь'].sum()
current_avg_area = df['Площадь'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Общее количество дефектов", current_total_defects, '-12', delta_color="inverse")
col2.metric("Общая площадь дефектов (м²)", f"{current_total_area:.1f}", f"{-24.2:.1f}", delta_color="inverse")
col3.metric("Средняя площадь дефектов (м²)", f"{current_avg_area:.2f}", f"{+0.2:.2f}", delta_color="inverse")

st.subheader('Количество дефектов по классам')
class_counts = df['Класс'].value_counts().reset_index()
class_counts.columns = ['Класс', 'Количество']

fig1 = px.pie(class_counts, values='Количество', names='Класс', title='Количество ям по классам')
st.plotly_chart(fig1)

# Гистограмма по площади ям
st.subheader('Гистограмма по площади ям')
fig2 = px.histogram(df, x='Площадь', nbins=10, title='Распределение ям по площади')
st.plotly_chart(fig2)

# Линейный график по количеству ям, идентифицированных в разные даты
df['Дата'] = pd.to_datetime(df['Дата'])
date_counts = df['Дата'].value_counts().reset_index()
date_counts.columns = ['Дата', 'Количество']
date_counts = date_counts.sort_values('Дата')

st.subheader('Линейный график по количеству ям, идентифицированных в разные даты')
fig3 = px.line(date_counts, x='Дата', y='Количество', title='Количество ям по датам идентификации')
st.plotly_chart(fig3)
