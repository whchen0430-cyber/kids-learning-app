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
if 'active_story_tr' not in st.session_state:
    st.session_state.active_story_tr = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 獨立字母資料庫 (確保不亂跳) ---
@st.cache_data
def get_alphabet_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "The apple is red.", "蘋果是紅的。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "Kick the ball.", "踢球。")]},
        "C": {"upper": "C", "lower": "c", "words": [("Cat", "🐱", "The cat is cute.", "貓很可愛。"), ("Cake", "🎂", "Sweet cake.", "甜蛋糕。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。"), ("Duck", "🦆", "Duck swims.", "鴨子游泳。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "強壯老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zero", "0️⃣", "Zero is a number.", "零是一個數字。")]}
    }
ALPHABET_DB = get_alphabet_db()

# --- 3. 側邊欄：進化與難度 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 恐龍進化 (龍族系統，無小雞)
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化了！", "55px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "雷龍成長中", "95px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "成年霸王龍", "135px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "165px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡 (影響教材難度)", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 語音輔助 ---
def generate_audio(text, speed):
    tts = gTTS(text=text, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母練習區", "📖 智能文章生成", "🎮 互動挑戰"])

with tab1:
    st.header("🔤 字母與單字發音")
    sel_letter = st.selectbox("請選擇字母", list(ALPHABET_DB.keys()), key="letter_select")
    letter_info = ALPHABET_DB[sel_letter]
    
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{letter_info['upper']} {letter_info['lower']}</h1>", unsafe_allow_html=True)
    if st.button(f"🔊 聽字母 {sel_letter} 的發音"):
        st.audio(generate_audio(letter_info['upper'], voice_speed), format="audio/mp3")
    
    st.divider()
    for w, emo, sent, tr in letter_info["words"]:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"<h1 style='font-size:70px;'>{emo}</h1>", unsafe_allow_html=True)
        with col2:
            st.subheader(w)
            st.write(f"**Sentence:** {sent}")
            st.caption(f"翻譯：{tr}")
            if st.button(f"🔊 聽單字發音", key=f"btn_w_{w}"):
                st.audio(generate_audio(f"{w}. {sent}", voice_speed), format="audio/mp3")
                st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 智能短文文章生成 (徹底解決中文混入問題) ---
with tab2:
    st.header("📖 敘事短文教材生成")
    u_topic = st.text_input("📝 請輸入文章主題 (例如：去日本、我的狗狗、煮披薩)", "去旅遊")
    u_length = st.select_slider("📏 選擇文章長度 (字數)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成對應年齡教材", key="gen_story_btn"):
        # 1. 主題語意映射 (內部變數絕對純英)
        mapping = {"狗": "Dogs", "貓": "Cats", "旅": "Travel", "煮": "Cooking", "學": "School", "龍": "Dinosaurs"}
        topic_en = "Your Topic"
        for k, v in mapping.items():
            if k in u_topic: topic_en = v; break
        if re.match(r'^[A-Za-z ]+$', u_topic): topic_en = u_topic

        # 2. 敘事邏輯文章組裝
        if user_age <= 6:
            en_p = f"I love {topic_en}. It is very cool and big. We can play together every day. This makes us very happy."
            tr_p = f"我愛{u_topic}。它非常酷而且很大。我們每天都可以一起玩。這讓我們非常開心。"
        elif user_age <= 10:
            en_p = f"Today, I want to talk about {topic_en}. I think {topic_en} is very interesting because it brings joy to our lives. We can learn many things while exploring it with friends."
            tr_p = f"今天，我想談談{u_topic}。我覺得{u_topic}很有趣，因為它給我們的生活帶來喜悅。當我們和朋友一起探索它時，可以學到很多東西。"
        else: # 12歲
            en_p = f"Exploring the world of {topic_en} provides us with unique opportunities to understand nature. Furthermore, focusing on {topic_en} helps us create unforgettable memories that last forever."
            tr_p = f"探索{u_topic}的世界為我們提供了了解大自然的獨特機會。此外，關注{u_topic}能幫助我們創造伴隨終生的難忘回憶。"

        # 3. 字數截斷
        words = en_p.split()
        st.session_state.active_story_en = " ".join(words[:u_length])
        if not st.session_state.active_story_en.endswith('.'): st.session_state.active_story_en += "."
        st.session_state.active_story_tr = tr_p
        st.session_state.active_story_topic = u_topic

    if st.session_state.active_story_en:
        st.subheader(f"📜 課文原文：{st.session_state.get('active_story_topic', '')}")
        # 強制純英過濾 (Double Check)
        pure_text = re.sub(r'[\u4e00-\u9fa5]', '', st.session_state.active_story_en)
        
        # 鎖定結構：大字體 + 一句一行
        for sentence in pure_text.split('.'):
            if sentence.strip():
                st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {sentence.strip()}.</div>", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文音軌"):
            st.audio(generate_audio(pure_text, voice_speed), format="audio/mp3")
        
        with st.expander("👁️ 查看精確翻譯"):
            st.write(st.session_state.active_story_tr)

with tab3:
    st.header("🎮 互動挑戰")
    st.write("遊戲區域穩定載入中...")
