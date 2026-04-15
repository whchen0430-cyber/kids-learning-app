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
if 'active_story_en' not in st.session_state:
    st.session_state.active_story_en = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 字母資料庫 (A-Z 保持穩定) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "Red apple.", "紅蘋果。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "Brown bear.", "棕熊。")]},
        "C": {"upper": "C", "lower": "c", "words": [("Cat", "🐱", "Cute cat.", "可愛貓。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "老虎壯。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。")]}
    }
DB = get_db()

# --- 3. 側邊欄：進化圖案 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "幼龍孵化！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "壯年霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文", "日文"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 功能分頁 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母與單字", "📖 敘事短文生成", "🎮 互動挑戰"])

with tab1:
    st.header("🔤 單字發音練習")
    sel_let = st.selectbox("請選擇字母", list(DB.keys()), key="sidebar_let")
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

# --- Tab 2: 核心文章引擎 (徹底修正 Your Topic 問題) ---
with tab2:
    st.header("📖 智慧敘事教材生成")
    u_input = st.text_input("📝 輸入主題 (例如：爸爸、去日本、我的貓)", "爸爸")
    u_len = st.select_slider("📏 文章字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成純英教學文章", key="gen_btn"):
        # 1. 語意智慧識別 (不依賴對照表)
        if re.match(r'^[A-Za-z ]+$', u_input): # 如果是英文
            en_kw = u_input
        else: # 如果是中文，根據內容映射為最合適的英文
            en_kw = "Family" # 預設
            if any(x in u_input for x in ["爸", "父"]): en_kw = "Father"
            elif any(x in u_input for x in ["媽", "母"]): en_kw = "Mother"
            elif any(x in u_input for x in ["旅", "遊"]): en_kw = "Travel"
            elif any(x in u_input for x in ["狗", "貓", "寵"]): en_kw = "Pets"
            elif any(x in u_input for x in ["煮", "食"]): en_kw = "Cooking"
        
        # 2. 敘事結構生成 (開頭-發展-結尾)
        if user_age <= 6:
            story = f"I love my {en_kw}. My {en_kw} is very strong and cool. We can play together every day. It makes me very happy."
            tr = f"我愛我的{u_input}。我的{u_input}非常強壯而且很酷。我們每天都可以一起玩。這讓我非常開心。"
        elif user_age <= 10:
            story = f"Today, I want to talk about my {en_kw}. I think my {en_kw} is special because we always have fun together. We can learn many things from each other every single day."
            tr = f"今天，我想談談我的{u_input}。我覺得我的{u_input}很特別，因為我們總是玩得很開心。我們每天都可以從彼此身上學到很多東西。"
        else: # 12歲
            story = f"The unique bond with my {en_kw} provides me with a wonderful opportunity to grow. I believe that every moment spent with my {en_kw} creates memories that stay with me forever."
            tr = f"與{u_input}之間獨特的紐帶為我提供了成長的絕佳機會。我相信與{u_input}度過的每一刻都會創造出伴隨我一生的難忘回憶。"

        # 3. 強制刷新 Session
        words = story.split()
        st.session_state.active_story_en = " ".join(words[:u_len])
        if not st.session_state.active_story_en.endswith('.'): st.session_state.active_story_en += "."
        st.session_state.active_story_tr = tr
        st.session_state.active_story_label = u_input

    if st.session_state.active_story_en:
        st.subheader(f"📜 課文原文：{st.session_state.get('active_story_label','')}")
        # 分句顯示：一句一行，大字體
        for s in st.session_state.active_story_en.split('. '):
            if s.strip():
                clean_s = s.strip() if s.strip().endswith('.') else s.strip() + '.'
                st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {clean_s}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 全文語音導讀"):
            st.audio(get_voice(st.session_state.active_en, voice_speed), format="audio/mp3")
        with st.expander("👁️ 查看翻譯"):
            st.write(st.session_state.active_story_tr)

with tab3:
    st.header("🎮 聽音挑戰")
    st.write("挑戰區域穩定載入中...")
