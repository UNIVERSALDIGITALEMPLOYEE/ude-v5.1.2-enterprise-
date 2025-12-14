import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import altair as alt  # Для pie-chart, установлен в среде

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ И СТИЛИ ---
st.set_page_config(
    page_title="CSP Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Кастомный CSS для премиум-вида (светлый, чистый, как на первой фотке)
st.markdown("""
<style>
    .stApp {background-color: #f8f9fa;}
    div[data-testid="stMetric"], div.stDataFrame, .stExpander, .stTextInput, .stMultiselect {background-color: #ffffff; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
    [data-testid="stMetricValue"] {color: #4361ee; font-weight: bold;}
    .science-label {background-color: #eef2ff; color: #4361ee; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-style: italic; margin-top: 5px; display: inline-block;}
    [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #eee;}
    .stButton > button {background-color: #4361ee; color: white; border-radius: 8px; padding: 0.5em 1em;}
    .notification {background-color: #eef2ff; padding: 10px; border-radius: 8px; border-left: 5px solid #4361ee;}
</style>
""", unsafe_allow_html=True)

# --- 2. НАСТРОЙКИ И ДАННЫЕ ---
SHEET_ID = "your_google_sheet_id_here"  # Замени на реальный ID твоей Google Sheets
SHEET_NAME = "Omnichannel"  # Название листа для омниканала
USERS_SHEET_NAME = "Users"  # Лист для команды

def load_data(sheet_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        if 'Timestamp' in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        return df.fillna("")
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        # Mock-данные для fallback
        if sheet_name == "Omnichannel":
            return pd.DataFrame({
                "Source": ["Telegram", "WhatsApp", "VK", "Avito", "Ozon"],
                "Client_ID": ["+7911000001", "+7916000002", "id123456", "id789012", "id345678"],
                "Message": ["Хочу купить курс", "Когда доставка?", "Есть скидка?", "Размер в наличии?", "Отзыв: 4 звезды"],
                "Timestamp": [datetime.now() - timedelta(minutes=random.randint(1, 60)) for _ in range(5)],
                "Channel": ["TG", "WA", "VK", "Avito", "Ozon"],
                "Status": ["ИИ ответил", "Неотвечено", "Эскалация", "ИИ ответил", "Новый отзыв"],
                "AI_Confidence": [0.94, 0.61, 0.72, 0.88, 0.95],
                "Response": ["Курс стоит 29900 руб. Скидка 10% по промокоду.", "", "Эскалировано на менеджера.", "Размер M в наличии.", "Спасибо за отзыв! Учтём."],
                "Science_Label": ["На основе SPIN и Чалдини", "", "Теория перспектив Канемана", "Принцип дефицита Чалдини", "Теория когнитивного диссонанса Фестингера"]
            })
        elif sheet_name == "Users":
            return pd.DataFrame({
                "Name": ["Иван Иванов", "Мария Петрова", "Алексей Сидоров", "Ольга Кузнецова"],
                "Role": ["owner", "senior_manager", "agent", "sales"],
                "Email": ["owner@example.com", "senior@example.com", "agent@example.com", "sales@example.com"],
                "Processed_Dialogs": [500, 300, 150, 200],
                "Rating": [5.0, 4.9, 4.7, 4.8]
            })
        else:
            return pd.DataFrame()

df_dialogs = load_data(SHEET_NAME)
df_users = load_data(USERS_SHEET_NAME)

def get_analytics_summary(df):
    total_processed = len(df)
    ai_processed = len(df[df["Status"] == "ИИ ответил"])
    economy = ai_processed * 500  # Пример: 500 руб на диалог (экономия на зумере)
    revenue = np.random.randint(1000000, 5000000)  # Mock, в реальности из CRM
    nps = round(random.uniform(8.5, 9.5), 1)
    return total_processed, ai_processed, economy, revenue, nps

def get_analytics_data(df):
    dates = pd.date_range(start=datetime.today() - timedelta(days=30), end=datetime.today())
    df_analytics = pd.DataFrame({
        "Дата": dates,
        "Выручка с ИИ": np.cumsum(np.random.randint(50000, 120000, len(dates))),
        "Выручка без ИИ": np.cumsum(np.random.randint(30000, 90000, len(dates))),
        "Конверсия": np.random.uniform(10, 30, len(dates))
    })
    return df_analytics

# --- 3. АВТОРИЗАЦИЯ ---
users_db = {
    "owner@example.com": {"password": "123", "role": "owner", "name": "Иван Иванов"},
    "senior@example.com": {"password": "123", "role": "senior_manager", "name": "Мария Петрова"},
    "agent@example.com": {"password": "123", "role": "agent", "name": "Алексей Сидоров"},
    "sales@example.com": {"password": "123", "role": "sales", "name": "Ольга Кузнецова"}
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
            st.rerun()
        else:
            st.sidebar.error("Неверный логин или пароль")

if not st.session_state.user:
    login()
    st.stop()

user = st.session_state.user
role = user["role"]
name = user["name"]

# --- 4. САЙДБАР И НАВИГАЦИЯ ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/4361ee/ffffff?text=CSP", use_column_width=True)
    st.markdown(f"**{name}** ({role.replace('_', ' ').title()})")
    st.divider()
    pages = ["Inbox (Живой чат)", "Аналитика", "Методология", "Команда"]
    allowed_pages = {
        "owner": pages,
        "senior_manager": pages,
        "agent": ["Inbox (Живой чат)"],
        "sales": ["Inbox (Живой чат)", "Аналитика"]
    }
    page = st.radio("Навигация", allowed_pages[role], label_visibility="collapsed")
    st.divider()
    if role in ["owner", "senior_manager"]:
        ai_traffic = st.slider("% трафика на ИИ", 0, 100, 50)
        confidence_threshold = st.slider("Порог эскалации (confidence)", 0.0, 1.0, 0.85, step=0.05)
        st.divider()

# --- 5. УВЕДОМЛЕНИЯ ---
if len(df_dialogs[df_dialogs["Status"] == "Неотвечено"]) > 0:
    st.markdown("<div class='notification'>Новый неотвеченный диалог! (Эскалация)</div>", unsafe_allow_html=True)

# --- 6. ВКЛАДКИ ---
if page == "Inbox (Живой чат)":
    st.header("Inbox • Омниканал")
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        status_filter = st.multiselect("Статус", ["Все", "ИИ ответил", "Неотвечено", "Эскалация"], default=["Все"])
    with col_filter2:
        channel_filter = st.selectbox("Канал", ["Все"] + list(df_dialogs["Channel"].unique()))
    with col_filter3:
        search = st.text_input("Поиск по клиентам/сообщениям")
    filtered_df = df_dialogs
    if "Все" not in status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
    if channel_filter != "Все":
        filtered_df = filtered_df[filtered_df["Channel"] == channel_filter]
    if search:
        filtered_df = filtered_df[filtered_df["Message"].str.contains(search, case=False) | filtered_df["Client_ID"].str.contains(search, case=False)]
    col_list, col_chat = st.columns([1, 2])
    with col_list:
        st.subheader("Диалоги")
        for idx, row in filtered_df.iterrows():
            bg = "#eef2ff" if row["Status"] == "Неотвечено" else "#ffffff"
            border = "2px solid #ff0000" if row["Status"] == "Эскалация" else "1px solid #eee"
            st.markdown(f"""
            <div style='background: {bg}; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: {border}; cursor: pointer;'>
                <strong>{row['Source']} • {row['Client_ID']}</strong><br>
                {row['Message'][:50]}...<br>
                <span style='font-size:0.8em; color:#999'>{row['Timestamp'].strftime('%H:%M %d.%m.%Y')}</span><br>
                Статус: {row['Status']} (Confidence: {row['AI_Confidence']})
            </div>
            """, unsafe_allow_html=True)
    with col_chat:
        st.subheader("Переписка")
        selected_idx = st.selectbox("Выберите диалог", filtered_df.index, format_func=lambda x: f"{filtered_df.loc[x, 'Source']} • {filtered_df.loc[x, 'Client_ID']}")
        row = filtered_df.loc[selected_idx]
        st.markdown(f"**Клиент: {row['Client_ID']}** ({row['Source']})")
        st.chat_message("user").write(row["Message"])
        if row["Status"] == "ИИ ответил":
            st.chat_message("assistant").write(row["Response"])
            st.markdown(f"<p class='science-label'>{row['Science_Label']}</p>", unsafe_allow_html=True)
        input_response = st.text_input("Ваш ответ")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Отправить"):
                st.success("Ответ отправлен")
        with col_btn2:
            if st.button("Взять в работу"):
                st.success("Диалог взят в работу")
        st.divider()
        st.subheader("Детали диалога")
        st.metric("Confidence ИИ", row["AI_Confidence"])
        st.markdown(f"<p class='science-label'>{row['Science_Label']}</p>", unsafe_allow_html=True)

elif page == "Аналитика":
    st.header("Аналитика")
    total_processed, ai_processed, economy, revenue, nps = get_analytics_summary(df_dialogs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Обработано всего", total_processed)
    col2.metric("Обработано ИИ", ai_processed, help="На основе каузального вывода (p-value < 0.05)")
    col3.metric("Сэкономлено на зарплатах", f"₽ {economy:,}", help="Расчёт на основе теории перспектив Канемана")
    col4.metric("Выручка от ИИ", f"₽ {revenue:,}", help="На основе принципов Чалдини")
    col5, col6 = st.columns(2)
    with col5:
        st.metric("NPS", nps, help="На основе теории когнитивного диссонанса Фестингера")
    with col6:
        st.metric("Среднее время ответа", "8 сек", "-2 сек")
    st.divider()
    df_analytics = get_analytics_data(df_dialogs)
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Динамика выручки")
        st.line_chart(df_analytics.set_index("Дата")[["Выручка с ИИ", "Выручка без ИИ"]])
        st.markdown("<p class='science-label'>Каузальный вывод на основе DoWhy (p-value < 0.05)</p>", unsafe_allow_html=True)
    with col_right:
        st.subheader("Распределение источников")
        sources = df_dialogs.groupby("Source").size().reset_index(name="Count")
        source_data = pd.DataFrame(dict(
            Source=sources["Source"],
            Count=sources["Count"]
        ))
        chart = alt.Chart(source_data).mark_arc(innerRadius=50).encode(
            theta="Count",
            color="Source",
            tooltip=["Source", "Count"]
        ).properties(width=300, height=300)
        st.altair_chart(chart, use_container_width=True)
    st.subheader("Топ жалоб")
    complaints = df_dialogs.groupby("Message").size().reset_index(name="Count").sort_values("Count", ascending=False).head(10)
    st.bar_chart(complaints.set_index("Message")["Count"])
    st.markdown("<p class='science-label'>Анализ BIS/BAS</p>", unsafe_allow_html=True)

elif page == "Методология":
    st.header("Методология • База знаний")
    st.file_uploader("Загрузить скрипт (PDF/Word)", type=["pdf", "docx"])
    with st.expander("Продажи • Возражения • Цена"):
        st.text_area("Скрипт", "Пример текста скрипта...")
        st.markdown("<p class='science-label'>На основе SPIN и Чалдини</p>", unsafe_allow_html=True)
        if role in ["owner", "senior_manager"]:
            st.button("Сохранить")
    with st.expander("Поддержка • Отзывы • Негатив"):
        st.text_area("Скрипт", "Пример для отзывов...")
        st.markdown("<p class='science-label'>На основе теории диссонанса</p>", unsafe_allow_html=True)
    st.subheader("Предложения ИИ")
    suggestions = pd.DataFrame({
        "Предложение": ["Новая фраза для возражений"],
        "Теория": ["Чалдини"],
        "Эффект": ["+15% конверсия"]
    })
    st.dataframe(suggestions)
    if role in ["owner", "senior_manager"]:
        st.button("Одобрить выбранные")

elif page == "Команда":
    st.header("Команда")
    st.dataframe(df_users, use_container_width=True)
    if role == "owner":
        st.subheader("Пригласить нового")
        col_name, col_email, col_role = st.columns(3)
        col_name.text_input("ФИО")
        col_email.text_input("Email")
        col_role.selectbox("Роль", ["agent", "sales"])
        st.button("Отправить приглашение")

st.caption("CSP • Cognitive Symbiosis Platform © 2025")
