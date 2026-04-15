import streamlit as st
from gtts import gTTS
import io
import re
import random

# --- 1. 初始化與積分 ---
if 'user_score' not in st.session_state: st.session_state.user_score = 0
if 'active_en_list' not in st.session_state: st.session_state.active_en_list = []
if 'active_tr_list' not in st.session_state: st.session_state.active_tr_list = []

MAX_SCORE = 150
if st.session_state.user_score >= MAX_SCORE: st.session_state.user_score = 0

# --- 2. 字母資料庫 ---
@st.cache_data
def get_alphabet():
    return {
        "D": {"upper": "D", "lower": "d", "words": [("Dance", "💃", "I like to dance.", "我喜歡跳舞。"), ("Dog", "🐶", "Good dog.", "好狗狗。")]},
        "S": {"upper": "S", "lower": "s", "words": [("School", "🏫", "Go to school.", "去上學。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Mother", "👩", "I love Mother.", "我愛媽媽。")]}
    }
DB = get_alphabet()

# --- 3. 側邊欄：進化鏈 ---
with st.sidebar:
    st.header("👤 學生狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_txt, d_sz = "🥚", "灰蛋狀態", "100px"
    elif score < 60: d_emo, d_txt, d_sz = "🦖", "小恐龍孵化", "60px"
    elif score < 90: d_emo, d_txt, d_sz = "🦕", "雷龍成長中", "90px"
    elif score < 120: d_emo, d_txt, d_sz = "🦖", "霸王龍成年", "130px"
    else: d_emo, d_txt, d_sz = "🐲", "終極神龍！", "160px"
    
    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:{d_sz};'>{d_emo}</h1><b>{d_txt}</b></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速", 0.5, 1.0, 0.8)

# --- 4. 輔助函數 ---
def speak(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁功能 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母練習", "📖 短文生成", "🎮 挑戰遊戲"])

with tab1:
    sel_l = st.selectbox("選擇字母", list(DB.keys()))
    info = DB[sel_l]
    st.title(f"{info['upper']} {info['lower']}")
    for w, emo, sent, tr in info["words"]:
        if st.button(f"🔊 {emo} {w}"):
            st.audio(speak(f"{w}. {sent}", voice_speed))
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

with tab2:
    st.header("📖 教材短文生成")
    u_topic = st.text_input("輸入主題 (如：跳舞、媽媽、上學)", "跳舞")
    
    if st.button("🚀 生成文章"):
        # 智慧語意判定
        en_word = u_topic
        mode = "Activity" # 預設

        if any(x in u_topic for x in ["跳", "舞"]): en_word, mode = "Dancing", "Activity"
        elif any(x in u_topic for x in ["爸", "父"]): en_word, mode = "Father", "Person"
        elif any(x in u_topic for x in ["媽", "母"]): en_word, mode = "Mother", "Person"
        elif any(x in u_topic for x in ["學", "校"]): en_word, mode = "School", "Place"
        
        # 根據類別與年齡建立「文章結構」
        if mode == "Activity":
            if user_age <= 6:
                pool = [(f"I love {en_word}.", f"我愛{u_topic}。"), (f"It is very fun.", f"這非常有趣。"), (f"We can {en_word.lower()} every day.", f"我們每天都可以{u_topic}。")]
            else:
                pool = [(f"{en_word} is a wonderful hobby.", f"{u_topic}是一個很棒的愛好。"), (f"It helps us stay happy and healthy.", f"它幫助我們保持快樂與健康。"), (f"We can share the joy of {en_word.lower()} with friends.", f"我們可以與朋友分享{u_topic}的喜悅。")]
        elif mode == "Person":
            prn = "She" if "Mother" in en_word else "He"
            pool = [(f"I love my {en_word}.", f"我愛我的{u_topic}。"), (f"{prn} is very kind and smart.", f"{prn == 'He' and '他' or '她'}非常親切且聰明。"), (f"We are a happy family.", f"我們是一個快樂的家庭。")]
        else: # Place
            pool = [(f"I like going to {en_word}.", f"我喜歡去{u_topic}。"), (f"{en_word} is a big place.", f"{u_topic}是一個很大的地方。"), (f"We learn many things there.", f"我們在那裡學到很多東西。")]

        st.session_state.active_en_list = [p[0] for p in pool]
        st.session_state.active_tr_list = [p[1] for p in pool]
        st.session_state.current_topic = u_topic

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文原文：{st.session_state.get('current_topic', '')}")
        for s in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:12px;'>• {s}</div>", unsafe_allow_html=True)
        if st.button("🔊 全文朗讀"):
            st.audio(speak(" ".join(st.session_state.active_en_list), voice_speed))
        with st.expander("👁️ 查看翻譯"):
            for tr in st.session_state.active_tr_list: st.write(tr)

with tab3:
    st.header("🎮 挑戰區")
    st.write("聽音選單字，答對加 10 分！")
    q = random.choice(["Dance", "School", "Mother", "Apple"])
    if st.button("🔊 聽題目"): st.audio(speak(q, voice_speed))
    ans = st.radio("答案是？", ["Dance", "School", "Mother", "Apple"])
    if st.button("提交"):
        if ans == q: 
            st.success("答對了！"); st.session_state.user_score += 10; st.balloons()
        else: st.error("再試一次！")
