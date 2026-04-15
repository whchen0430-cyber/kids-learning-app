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
if 'active_en_list' not in st.session_state:
    st.session_state.active_en_list = []
if 'active_tr_list' not in st.session_state:
    st.session_state.active_tr_list = []

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 字母資料庫 (A-Z 穩定版) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "Red apple.", "紅蘋果。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Mother", "👩", "I love Mother.", "我愛媽媽。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。")]},
        "F": {"upper": "F", "lower": "f", "words": [("Father", "👨", "Strong Father.", "強壯的爸爸。")]}
    }
DB = get_db()

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "猛壯霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡 (難度控制)", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3 = st.tabs(["🔤 單字音標", "📖 敘事教材生成", "🎮 互動挑戰"])

with tab1:
    st.header("🔤 單字與發音練習")
    sel_let = st.selectbox("選擇字母", list(DB.keys()), key="alphabet_key")
    info = DB[sel_let]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emo, sent, tr in info["words"]:
        st.write(f"### {emo} {w}")
        if st.button(f"🔊 聽單字發音", key=f"v_w_{w}"):
            st.audio(get_voice(f"{w}. {sent}", voice_speed), format="audio/mp3")
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 敘事生成引擎 (核心：代名詞校正) ---
with tab2:
    st.header("📖 智慧敘事教材生成")
    u_topic = st.text_input("📝 請輸入教材主題 (如：媽媽、爸爸、去旅遊)", "媽媽")
    u_len_goal = st.select_slider("📏 目標總字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成精準翻譯教材", key="gen_btn"):
        # 1. 智慧主題映射與性別判定
        t_en, t_cn = u_topic, u_topic
        gender_prn = ("He", "He", "他") # 預設

        if any(x in u_topic for x in ["媽", "母", "姊", "妹", "女", "妻"]): 
            t_en, t_cn, gender_prn = "Mother", "媽媽", ("She", "She", "她")
        elif any(x in u_topic for x in ["爸", "父", "兄", "弟", "男", "夫"]): 
            t_en, t_cn, gender_prn = "Father", "爸爸", ("He", "He", "他")
        elif any(x in u_topic for x in ["貓", "寵"]): 
            t_en, t_cn, gender_prn = "Pet", "寵物", ("It", "It", "它")
        elif any(x in u_topic for x in ["旅", "遊"]): 
            t_en, t_cn, gender_prn = "Travel", "旅遊", ("It", "It", "它")

        # 2. 英中「鏡像」句型池 (代名詞動態嵌入)
        if user_age <= 6:
            pool = [
                (f"I love my {t_en}.", f"我愛我的{t_cn}。"),
                (f"My {t_en} is very kind.", f"我的{t_cn}非常親切。"),
                (f"We play games together.", f"我們一起玩遊戲。"),
                (f"{gender_prn[0]} is very smart.", f"{gender_prn[2]}非常聰明。"),
                (f"It is a happy day.", f"這是快樂的一天。")
            ]
        elif user_age <= 10:
            pool = [
                (f"Today, I want to talk about my {t_en}.", f"今天，我想談談我的{t_cn}。"),
                (f"I think my {t_en} is special because we have fun.", f"我覺得我的{t_cn}很特別，因為我們玩得很開心。"),
                (f"{gender_prn[0]} teaches me many new things every day.", f"{gender_prn[2]}每天都教我很多新事物。"),
                (f"Being with my {t_en} is the best way to spend time.", f"與我的{t_cn}在一起是最好的時光。")
            ]
        else: # 12歲
            pool = [
                (f"The unique experience of being with my {t_en} provides me with a great opportunity to grow.", f"與我的{t_cn}在一起的獨特經驗為我提供了成長的機會。"),
                (f"I believe that every moment spent with {gender_prn[1].lower()} creates memories that stay with me forever.", f"我相信與{gender_prn[2]}共度的每一刻都會創造出伴隨我一生的回憶。"),
                (f"Exploring the world of {t_en} helps us understand the importance of love.", f"探索{t_cn}的世界幫助我們理解愛的重要性。")
            ]

        # 3. 逐句選取邏輯
        selected_en, selected_tr = [], []
        current_wc = 0
        for en, tr in pool:
            s_len = len(en.split())
            if current_wc < u_len_goal:
                selected_en.append(en)
                selected_tr.append(tr)
                current_wc += s_len
        
        st.session_state.active_en_list = selected_en
        st.session_state.active_tr_list = selected_tr
        st.session_state.active_topic = u_topic

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文原文：{st.session_state.get('active_topic','')}")
        full_en_text = " ".join(st.session_state.active_en_list)
        
        for sentence in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {sentence}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文導讀"):
            st.audio(get_voice(full_en_text, voice_speed), format="audio/mp3")
        
        st.divider()
        st.subheader("👁️ 精確中文翻譯")
        for tr_sentence in st.session_state.active_tr_list:
            st.markdown(f"<div style='font-size:20px; color:#D35400; margin-bottom:10px;'>{tr_sentence}</div>", unsafe_allow_html=True)

with tab3:
    st.header("🎮 互動挑戰")
    st.write("穩定運行中，歡迎積分挑戰！")
