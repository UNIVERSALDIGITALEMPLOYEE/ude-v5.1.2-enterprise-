import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import random

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ И СТИЛИ ---
st.set_page_config(
    page_title="CSP Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для реализации дизайн-кода (цвета, отступы, карточки)
st.markdown("""
<style>
    /* Основной фон */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Белые карточки для контейнеров */
    div[data-testid="stMetric"], div.stDataFrame, div.stPlotlyChart {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Акцентный цвет для метрик */
    [data-testid="stMetricValue"] {
        color: #4361ee;
        font-weight: bold;
    }
    /* Стилизация лейблов методологии */
    .science-label {
        background-color: #eef2ff;
        color: #4361ee;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-style: italic;
        margin-top: 5px;
        display: inline-block;
    }
    /* Сайдбар */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ГЕНЕРАЦИЯ ДАННЫХ (MOCK DATA) ---

def get_analytics_data():
    dates = pd.date_range(start=datetime.today() - timedelta(days=30), end=datetime.today())
    df = pd.DataFrame({
        "Дата": dates,
        "Выручка с ИИ": np.random.randint(50000, 120000, size=len(dates)),
        "Выручка без ИИ": np.random.randint(30000, 90000, size=len(dates))
    })
    return df

def get_chat_history():
    return [
        {"role": "user", "content": "Здравствуйте, сколько стоит курс по Python?"},
        {"role": "ai", "content": "Добрый день! Курс стоит 45 000 ₽, но только до пятницы действует скидка 15%. Это позволит вам сэкономить 6 750 ₽.", "label": "Принцип дефицита (Чалдини)"},
        {"role": "user", "content": "А есть рассрочка? Мне дорого сразу."},
        {"role": "ai", "content": "Понимаю вас. Многие наши студенты сначала сомневались, но оформив рассрочку от 2000 ₽/мес, уже на второй месяц обучения начали брать заказы. Рассрочка позволит вам начать учиться без удара по бюджету.", "label": "Методология SPIN (Решение проблемы)"}
    ]

# --- 3. ИНТЕРФЕЙСНЫЕ ФУНКЦИИ ---

def render_sidebar():
    with st.sidebar:
        st.title("🧩 CSP Platform")
        st.markdown("---")
        
        # Симуляция логина
        st.subheader("Профиль")
        role = st.selectbox("Ваша роль", ["Владелец", "Менеджер продаж", "Менеджер поддержки"])
        st.caption(f"Вход выполнен: {role}")
        
        st.markdown("---")
        
        # Навигация
        page = st.radio("Навигация", ["📊 Аналитика", "💬 Inbox (Живой чат)", "📚 Методология", "👥 Команда"])
        
        st.markdown("---")
        st.info("💡 ИИ-агенты активны")
        return page, role

def render_analytics(role):
    st.header("Аналитика и Метрики")
    
    if role == "Менеджер поддержки":
        st.warning("У вас ограниченный доступ к финансовым метрикам.")
        metrics_cols = st.columns(2)
        metrics_cols[0].metric("Мои диалоги", "142", "+12")
        metrics_cols[1].metric("NPS (мой)", "4.8", "+0.2")
        return

    # Top KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Обработано ИИ", "1,240", "+23%")
    c2.metric("Сэкономлено (ЗП)", "620 т.р.", "+42k ₽", help="Расчет на основе ставки 500р/час")
    c3.metric("Выручка от ИИ", "4.2M ₽", "+18.3%")
    c4.metric("NPS / CSI", "9.2", "+0.5")

    st.markdown("---")

    # Charts Row
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Динамика выручки (ИИ vs Ручное)")
        df = get_analytics_data()
        fig = px.line(df, x="Дата", y=["Выручка с ИИ", "Выручка без ИИ"], 
                      color_discrete_sequence=["#4361ee", "#b0c4de"],
                      template="plotly_white")
        fig.update_layout(legend_title_text='Метод')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📈 Лейбл: Каузальный вывод подтверждает значимость ИИ (p-value < 0.05)")

    with col_right:
        st.subheader("Источники трафика")
        sources = pd.DataFrame({
            "Source": ["Telegram", "WhatsApp", "Avito", "Сайт"],
            "Value": [45, 30, 15, 10]
        })
        fig_pie = px.pie(sources, values="Value", names="Source", 
                         color_discrete_sequence=["#4361ee", "#06d6a0", "#ffd166", "#ef476f"],
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bottom Row
    st.subheader("Топ возражений и жалоб (BIS/BAS Анализ)")
    complaints = pd.DataFrame({
        "Возражение": ["Дорого", "Нет времени", "Не доверяю", "Подумаю"],
        "Частота": [120, 85, 40, 35],
        "Конверсия ИИ": [15, 22, 10, 30]
    })
    st.dataframe(complaints, use_container_width=True, hide_index=True)

def render_inbox(role):
    st.header("Inbox: Омниканальный чат")
    
    # Фильтры
    f1, f2, f3 = st.columns([2, 2, 4])
    f1.multiselect("Статус", ["Все", "Неотвеченные", "Эскалация"], default=["Все"])
    f2.selectbox("Канал", ["Все", "Telegram", "WhatsApp"])
    f3.text_input("🔍 Поиск по диалогам", placeholder="Имя клиента или телефон")

    st.markdown("---")

    # Split View: Список слева, Чат справа
    col_list, col_chat = st.columns([1, 2])

    with col_list:
        st.markdown("### Диалоги")
        # Имитация списка диалогов
        users = [
            {"name": "Алексей Смирнов", "msg": "А есть рассрочка?", "time": "10:45", "channel": "TG", "active": True},
            {"name": "Мария Иванова", "msg": "Спасибо, подумаю.", "time": "09:30", "channel": "WA", "active": False},
            {"name": "Иван Петров", "msg": "Где забрать заказ?", "time": "Вчера", "channel": "Avito", "active": False},
        ]
        
        for u in users:
            bg_color = "#eef2ff" if u["active"] else "#ffffff"
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #eee; cursor: pointer;">
                <strong>{u['name']}</strong> <span style="font-size:0.8em; color:#888">({u['channel']})</span><br>
                <span style="font-size:0.9em; color:#555">{u['msg']}</span><br>
                <span style="font-size:0.7em; color:#999">{u['time']}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_chat:
        st.markdown("### Чат с: Алексей Смирнов (Telegram)")
        
        history = get_chat_history()
        
        # Отрисовка сообщений
        for msg in history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "label" in msg:
                    st.markdown(f'<div class="science-label">🧪 {msg["label"]}</div>', unsafe_allow_html=True)

        # Поле ввода
        st.text_input("Ваш ответ...", key="chat_input")
        col_act1, col_act2 = st.columns([1, 4])
        col_act1.button("Отправить", type="primary")
        col_act2.button("✋ Взять в работу")

def render_methodology(role):
    st.header("📚 Методология и База знаний ИИ")
    
    if role != "Владелец":
        st.info("Вы находитесь в режиме просмотра.")
    
    c1, c2 = st.columns([3, 1])
    c1.file_uploader("Загрузить новые материалы (PDF, DOCX)", help="ИИ автоматически распарсит файл на скрипты")
    
    st.markdown("### Активные скрипты (Editable)")
    
    with st.expander("📂 Продажи / Работа с ценой", expanded=True):
        st.text_area("Скрипт: Отработка 'Дорого'", 
                     value="Согласен, цена — важный фактор. Но если разделить эту сумму на 12 месяцев использования, получается всего 50 рублей в день. Это меньше чашки кофе за автоматизацию вашего бизнеса.",
                     height=100)
        st.markdown('<span class="science-label">Основано на: Рефрейминг (НЛП)</span>', unsafe_allow_html=True)
        if role == "Владелец":
            st.button("Сохранить изменения", key="save_1")

    with st.expander("📂 Поддержка / Гневный клиент"):
        st.write("Скрипт для успокоения клиента через технику присоединения...")
    
    st.markdown("### Предложения от ИИ (Самообучение)")
    suggestions = pd.DataFrame({
        "Фраза": ["Лучше сказать: 'Инвестиция', а не 'Трата'", "Добавить паузу перед ценой"],
        "Теория": ["Психолингвистика", "Управление вниманием"],
        "Эффективность": ["+12% конверсии", "+5% конверсии"]
    })
    st.data_editor(suggestions, num_rows="dynamic")

def render_team(role):
    st.header("Управление командой")
    if role != "Владелец":
        st.error("У вас нет прав для просмотра этой страницы.")
        return

    col_btn, _ = st.columns([1, 5])
    col_btn.button("➕ Пригласить сотрудника")

    team_data = pd.DataFrame({
        "ФИО": ["Анна К.", "Сергей В.", "ИИ-Агент #1"],
        "Роль": ["Менеджер продаж", "Старший менеджер", "Бот"],
        "Статус": ["Онлайн", "Офлайн", "Всегда активен"],
        "Рейтинг": [4.8, 4.9, 5.0],
        "Обработано заявок": [120, 340, 15000]
    })
    
    st.dataframe(team_data, use_container_width=True)

# --- 4. ОСНОВНАЯ ЛОГИКА ---

def main():
    selected_page, user_role = render_sidebar()

    if selected_page == "📊 Аналитика":
        render_analytics(user_role)
    elif selected_page == "💬 Inbox (Живой чат)":
        render_inbox(user_role)
    elif selected_page == "📚 Методология":
        render_methodology(user_role)
    elif selected_page == "👥 Команда":
        render_team(user_role)

if __name__ == "__main__":
    main()
