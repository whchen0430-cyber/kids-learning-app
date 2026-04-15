import streamlit as st
from gtts import gTTS
import io
import re
import random
import time

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0
if 'game_turn' not in st.session_state:
    st.session_state.game_turn = 0
if 'final_en' not in st.session_state:
    st.session_state.final_en = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 字母資料庫 (穩定 A-Z) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "Red apple.", "紅蘋果。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "Brown bear.", "棕熊。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "老虎壯。")]}
    }
DB = get_db()

# --- 3. 側邊欄：恐龍成長與設定 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 去小雞化成長邏輯
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化了！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "活潑雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "猛壯霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母與單字", "📖 敘事教材生成", "🎮 互動挑戰"])

with tab1:
    st.header("🔤 單字發音練習")
    sel_let = st.selectbox("請選擇字母", list(DB.keys()), key="alphabet_key")
    info = DB[sel_let]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emo, sent, tr in info["words"]:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"<h1 style='font-size:70px;'>{emo}</h1>", unsafe_allow_html=True)
        with col2:
            st.subheader(w)
            st.write(f"**Sentence:** {sent}")
            if st.button(f"🔊 聽發音", key=f"v_w_{w}"):
                st.audio(get_voice(f"{w}. {sent}", voice_speed), format="audio/mp3")
                st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 敘事生成引擎 (核心：確保句子完整) ---
with tab2:
    st.header("📖 指令式教材生成")
    u_topic = st.text_input("📝 請輸入教材主題 (如：爸爸、去日本、小貓咪)", "爸爸")
    u_len_goal = st.select_slider("📏 目標總字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成完整教材文章", key="gen_btn"):
        # 1. 主題語意智慧判定
        t_en = u_topic if re.match(r'^[A-Za-z ]+$', u_topic) else "Family"
        if any(x in u_topic for x in ["爸", "父"]): t_en = "Father"
        elif any(x in u_topic for x in ["媽", "母"]): t_en = "Mother"
        elif any(x in u_topic for x in ["貓"]): t_en = "Cat"
        elif any(x in u_topic for x in ["旅", "遊"]): t_en = "Travel"

        # 2. 根據年齡與主題構造「完整句型池」
        if user_age <= 6:
            pool = [f"I love my {t_en}.", f"My {t_en} is very kind.", f"We play games together.", f"It is a happy day.", f"He is very strong."]
        elif user_age <= 10:
            pool = [f"Today, I want to share something about my {t_en}.", f"I think my {t_en} is very special because we have fun.", f"We can learn many new things from my {t_en} every day.", f"It is the best way to spend time with my family."]
        else: # 12歲
            pool = [f"The unique experience of being with my {t_en} provides me with an opportunity to grow.", f"I believe that every moment spent with my {t_en} creates memories that stay with me forever.", f"Exploring the world of {t_en} helps us understand the importance of family love."]

        # 3. 語意完整截斷邏輯：以「句」為單位，絕不砍斷單字
        selected_sentences = []
        current_word_count = 0
        for s in pool:
            s_len = len(s.split())
            if current_word_count + s_len <= u_len_goal + 10: # 容許 10 個字的溢出以保證完整
                selected_sentences.append(s)
                current_word_count += s_len
        
        st.session_state.final_en = " ".join(selected_sentences)
        st.session_state.final_tr = f"這是一段關於「{u_topic}」的精確教材內容。"
        st.session_state.final_label = u_topic

    if st.session_state.final_en:
        st.subheader(f"📜 課文原文：{st.session_state.get('final_label','')}")
        # 鎖定結構：大字體 + 一句一行
        for sentence in st.session_state.final_en.split('.'):
            if sentence.strip():
                st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {sentence.strip()}.</div>", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文導讀"):
            st.audio(get_voice(st.session_state.final_en, voice_speed), format="audio/mp3")
        with st.expander("👁️ 查看翻譯"):
            st.write(st.session_state.final_tr)

with tab3:
    st.header("🎮 互動挑戰")
    st.write("挑戰區域穩定載入中...")
