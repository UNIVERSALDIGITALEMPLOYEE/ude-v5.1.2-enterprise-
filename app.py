# app.py — полностью готовый дашборд CSP
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ====================== CONFIG ======================
st.set_page_config(
    page_title="CSP • Симбиоз",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стиль как на первой фотке
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stButton>button {background-color: #4361ee; color: white; border-radius: 8px;}
    .css-1d391kg {padding-top: 1rem;}
    .role-owner {color: #4361ee; font-weight: bold;}
    .role-senior {color: #7209b7;}
    .role-agent {color: #f72585;}
    .role-sales {color: #06d6a0;}
</style>
""", unsafe_allow_html=True)

# ====================== SECRETS ======================
# Создай файл secrets.toml в корне:
# [google]
# sheet_id = "твой_ID_таблицы"
# credentials = """тут JSON от сервисного аккаунта Google"""
# Или просто вставь sheet_id вручную ниже для теста

try:
    SHEET_ID = st.secrets["google"]["sheet_id"]
except:
    SHEET_ID = "1a2b3c4d5e6f7g8h9i0j"  # ← замени на свою таблицу

# ====================== АВТОРИЗАЦИЯ ======================
users_db = {
    "owner@demo.ru": {"password": "123", "role": "owner", "name": "Иван Иванов"},
    "senior@demo.ru": {"password": "123", "role": "senior_manager", "name": "Мария Петрова"},
    "agent@demo.ru": {"password": "123", "role": "agent", "name": "Алексей Сидоров"},
    "sales@demo.ru": {"password": "123", "role": "sales", "name": "Ольга Кузнецова"}
}

if "user" not in st.session_state:
    st.session_state.user = None

def login():
    st.sidebar.header("Вход в CSP")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Пароль", type="password")
    if st.sidebar.button("Войти"):
        if email in users_db and users_db[email]["password"] == password:
            st.session_state.user = users_db[email]
            st.sidebar.success(f"Добро пожаловать, {users_db[email]['name']}!")
            st.rerun()
        else:
            st.sidebar.error("Неверный логин или пароль")

if not st.session_state.user:
    login()
    st.stop()

user = st.session_state.user
role = user["role"]
name = user["name"]

# ====================== ДАННЫЕ ======================
@st.cache_data(ttl=5)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Omnichannel"
        df = pd.read_csv(url)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        return df.fillna("")
    except:
        # Демо-данные
        return pd.DataFrame({
            "Source": ["Telegram", "WhatsApp", "VK", "Avito"],
            "Client_ID": ["+7911...", "+7916...", "id123", "id456"],
            "Message": ["Хочу купить курс", "Когда доставка?", "Скидка есть?", "Размер в наличии?"],
            "Timestamp": [datetime.now() - timedelta(minutes=i*10) for i in range(4)],
            "Channel": ["TG", "WA", "VK", "Avito"],
            "Status": ["ИИ ответил", "ИИ ответил", "Эскалация", "Неотвечено"],
            "AI_Confidence": [0.94, 0.88, 0.61, 0.92]
        })

df = load_data()

# ====================== САЙДБАР ======================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/4361ee/ffffff?text=CSP", use_column_width=True)
    st.markdown(f"**{name}**")
    st.markdown(f"<span class='role-{role}'>● {role.replace('_', ' ').title()}</span>", unsafe_allow_html=True)
    st.divider()

    pages = ["Inbox", "Аналитика", "Методология", "Команда"]
    allowed_pages = {
        "owner": pages,
        "senior_manager": pages,
        "agent": ["Inbox"],
        "sales": ["Inbox", "Аналитика"]
    }
    page = st.radio("Навигация", allowed_pages[role], label_visibility="collapsed")

# ====================== СТРАНИЦЫ ======================
if page == "Inbox":
    st.header("Inbox • Омниканал")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Диалоги")
        filter_status = st.multiselect("Фильтр", ["Все", "Неотвечено", "Эскалация", "ИИ ответил"], default="Все")
        selected = st.selectbox("Выберите диалог", df.index, format_func=lambda x: f"{df.loc[x, 'Source']} • {df.loc[x, 'Client_ID'][:20]}...")

    with col2:
        st.subheader("Переписка")
        row = df.loc[selected]
        st.write(f"**{row['Client_ID']}** • {row['Source']} • {row['Timestamp'].strftime('%H:%M')}")
        st.chat_message("user").write(row["Message"])
        if row["Status"] == "ИИ ответил":
            st.chat_message("assistant").write("Спасибо за интерес! Курс стоит 29 900 ₽, сейчас действует рассрочка...")
        if st.button("Взять в работу", type="primary"):
            st.success("Диалог взят в работу!")

elif page == "Аналитика":
    st.header("Аналитика")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Обработано ИИ", "127", "+23")
    col2.metric("Сэкономлено", "₽ 184 000", "+₽ 42 000")
    col3.metric("Выручка от ИИ", "₽ 1.24 млн", "+18.3%")
    col4.metric("NPS", "87", "+5")

    st.plotly_chart(px.line(pd.DataFrame({
        "Дата": pd.date_range(start="2025-04-01", periods=30),
        "Выручка": np.random.randint(20000, 80000, 30).cumsum()
    }), x="Дата", y="Выручка"), use_container_width=True)

elif page == "Методология":
    st.header("Методология • База знаний")
    st.success("Здесь будет редактор скриптов, загрузка PDF и предложения ИИ")
    st.info("Владелец может редактировать, остальные — только читать")

elif page == "Команда":
    st.header("Команда")
    if role == "owner":
        st.write("Управление доступом — скоро здесь будет таблица сотрудников")
    else:
        st.info("Только владелец видит этот раздел")

st.caption("CSP • Cognitive Symbiosis Platform © 2025")
