import streamlit as st
from gtts import gTTS
import io
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state: st.session_state.user_score = 0
if 'game_turn' not in st.session_state: st.session_state.game_turn = 0
if 'active_en_list' not in st.session_state: st.session_state.active_en_list = []
if 'active_tr_list' not in st.session_state: st.session_state.active_tr_list = []

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE: st.session_state.user_score = 0

# --- 2. 字母資料庫 (A-Z 穩定版) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "Red apple.", "紅蘋果。")]},
        "S": {"upper": "S", "lower": "s", "words": [("School", "🏫", "I go to school.", "我去上學。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Mother", "👩", "I love Mother.", "我愛媽媽。")]}
    }
DB = get_db()

# --- 3. 側邊欄：進化邏輯 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "壯碩霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"): st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 功能分頁 ---
tab1, tab2 = st.tabs(["🔤 字母練習", "📖 教材生成"])

with tab1:
    st.header("🔤 字母發音練習")
    sel_let = st.selectbox("請選擇字母", list(DB.keys()), key="alphabet_key")
    info = DB[sel_let]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emo, sent, tr in info["words"]:
        if st.button(f"🔊 {emo} {w} 發音"):
            st.audio(get_voice(f"{w}. {sent}", voice_speed), format="audio/mp3")
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 敘事生成引擎 (核心修正：類別判定) ---
with tab2:
    st.header("📖 指令式教材生成")
    u_topic = st.text_input("📝 請輸入教材主題 (如：上學、媽媽、旅遊)", "上學")
    u_len_goal = st.select_slider("📏 目標字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成專業教材", key="gen_btn"):
        # 1. 類別與主題映射
        en_topic = "Topic"
        category = "Action" # 預設類別

        # 映射庫擴充
        if any(x in u_topic for x in ["學", "校"]): en_topic, category = "School", "Place"
        elif any(x in u_topic for x in ["爸", "父", "男"]): en_topic, category = "Father", "Person_M"
        elif any(x in u_topic for x in ["媽", "母", "女"]): en_topic, category = "Mother", "Person_F"
        elif any(x in u_topic for x in ["旅", "遊"]): en_topic, category = "Travel", "Action"
        elif any(x in u_topic for x in ["貓", "狗"]): en_topic, category = "Pet", "Animal"

        # 2. 根據類別與年齡生成對應句池
        if category == "Place" or category == "Action":
            pool = [
                (f"I like going to {en_topic}.", f"我喜歡去{u_topic}。"),
                (f"{en_topic} is very fun and big.", f"{u_topic}非常有趣且宏大。"),
                (f"We can learn many things there.", f"我們可以在那裡學到很多東西。"),
                (f"It is a happy day at {en_topic}.", f"在{u_topic}是快樂的一天。")
            ] if user_age <= 8 else [
                (f"Going to {en_topic} provides us with great opportunities to grow.", f"去{u_topic}為我們提供了成長的好機會。"),
                (f"We believe that {en_topic} is essential for our life.", f"我們相信{u_topic}對我們的生活至關重要。")
            ]
        elif category.startswith("Person"):
            prn = "He" if category == "Person_M" else "She"
            pool = [
                (f"I love my {en_topic}.", f"我愛我的{u_topic}。"),
                (f"My {en_topic} is very kind.", f"我的{u_topic}非常親切。"),
                (f"{prn} is very strong and smart.", f"{prn == 'He' and '他' or '她'}非常強壯且聰明。")
            ]

        # 3. 逐句存取
        st.session_state.active_en_list = [p[0] for p in pool]
        st.session_state.active_tr_list = [p[1] for p in pool]
        st.session_state.active_topic = u_topic

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文原文：{st.session_state.active_topic}")
        for s in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {s}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 全文朗讀"):
            st.audio(get_voice(" ".join(st.session_state.active_en_list), voice_speed), format="audio/mp3")
        
        with st.expander("👁️ 查看精確翻譯"):
            for tr in st.session_state.active_tr_list: st.write(tr)
