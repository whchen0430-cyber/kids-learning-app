import streamlit as st
from gtts import gTTS
import io
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state: st.session_state.user_score = 0
if 'active_en_list' not in st.session_state: st.session_state.active_en_list = []
if 'active_tr_list' not in st.session_state: st.session_state.active_tr_list = []
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE: st.session_state.user_score = 0

# --- 2. 字母與單字資料庫 A-Z (完整 26 個字母) ---
@st.cache_data
def get_full_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "The apple is red.", "蘋果是紅的。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。")]},
        "C": {"upper": "C", "lower": "c", "words": [("Cat", "🐱", "The cat is cute.", "貓很可愛。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。")]},
        "E": {"upper": "E", "lower": "e", "words": [("Egg", "🥚", "I eat an egg.", "我吃一顆蛋。")]},
        "F": {"upper": "F", "lower": "f", "words": [("Fish", "🐟", "Blue fish.", "藍色的魚。")]},
        "G": {"upper": "G", "lower": "g", "words": [("Goat", "🐐", "The goat eats grass.", "山羊吃草。")]},
        "H": {"upper": "H", "lower": "h", "words": [("Hat", "🎩", "Wear a hat.", "戴帽子。")]},
        "I": {"upper": "I", "lower": "i", "words": [("Ice cream", "🍦", "Cold ice cream.", "冷冰淇淋。")]},
        "J": {"upper": "J", "lower": "j", "words": [("Jam", "🍯", "Sweet jam.", "甜果醬。")]},
        "K": {"upper": "K", "lower": "k", "words": [("Kite", "🪁", "Fly a kite.", "放風箏。")]},
        "L": {"upper": "L", "lower": "l", "words": [("Lion", "🦁", "King lion.", "獅子王。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Mother", "👩", "I love Mother.", "我愛媽媽。")]},
        "N": {"upper": "N", "lower": "n", "words": [("Nose", "👃", "My nose.", "我的鼻子。")]},
        "O": {"upper": "O", "lower": "o", "words": [("Orange", "🍊", "Juicy orange.", "多汁橘子。")]},
        "P": {"upper": "P", "lower": "p", "words": [("Pig", "🐷", "Pink pig.", "粉紅豬。")]},
        "Q": {"upper": "Q", "lower": "q", "words": [("Queen", "👸", "The queen.", "皇后。")]},
        "R": {"upper": "R", "lower": "r", "words": [("Rabbit", "🐰", "White rabbit.", "小白兔。")]},
        "S": {"upper": "S", "lower": "s", "words": [("Sun", "☀️", "Hot sun.", "熱太陽。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "老虎壯。")]},
        "U": {"upper": "U", "lower": "u", "words": [("Umbrella", "🌂", "My umbrella.", "雨傘。")]},
        "V": {"upper": "V", "lower": "v", "words": [("Van", "🚐", "Drive a van.", "開廂型車。")]},
        "W": {"upper": "W", "lower": "w", "words": [("Whale", "🐋", "Big whale.", "大鯨魚。")]},
        "X": {"upper": "X", "lower": "x", "words": [("Box", "📦", "A box.", "盒子。")]},
        "Y": {"upper": "Y", "lower": "y", "words": [("Yellow", "💛", "Bright yellow.", "黃色。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。")]}
    }
FULL_DB = get_full_db()

# --- 3. 側邊欄：恐龍成長系統 ---
with st.sidebar:
    st.header("👤 學生學習進度")
    score = st.session_state.user_score
    st.write(f"🌟 目前積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神秘的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化了！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "雷龍成長中", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "成年霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍現身！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("教學年齡設定", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("朗讀語速", 0.5, 1.0, 0.8)
    if st.button("🔄 積分重置"): st.session_state.user_score = 0; st.rerun()

# --- 4. 語音輔助 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 三大功能分頁 ---
tab1, tab2, tab3 = st.tabs(["🔤 A-Z 字母練習區", "📖 萬能隨機短文", "🎮 聽音挑戰遊戲"])

with tab1:
    st.header("🔤 字母與單字發音練習")
    # 這裡加入 key 確保狀態獨立
    sel_let = st.selectbox("請選擇字母練習", list(FULL_DB.keys()), key="alphabet_panel_new")
    info = FULL_DB[sel_let]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B; font-size:100px;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    
    for w, emo, sent, tr in info["words"]:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"<h1 style='font-size:80px;'>{emo}</h1>", unsafe_allow_html=True)
        with col2:
            st.subheader(w)
            st.write(f"**Sentence:** {sent}")
            st.caption(f"翻譯：{tr}")
            if st.button(f"🔊 聽 {w} 發音", key=f"btn_tab1_v2_{w}"):
                st.audio(get_voice(f"{w}. {sent}", voice_speed), format="audio/mp3")
                st.session_state.user_score = min(st.session_state.user_score + 1, 150)

with tab2:
    st.header("📖 萬能隨機教材發送機")
    u_len_goal = st.select_slider("📏 文章字數調整", options=[10, 20, 30, 40, 50], value=20)
    
    master_topics = [
        {"cn": "冰淇淋", "en": "Ice Cream", "type": "Food"},
        {"cn": "大象", "en": "Elephants", "type": "Animal"},
        {"cn": "宇宙", "en": "Space", "type": "Place"},
        {"cn": "下雨", "en": "Rain", "type": "Nature"},
        {"cn": "腳踏車", "en": "Bicycles", "type": "Object"},
        {"cn": "彩虹", "en": "Rainbows", "type": "Nature"},
        {"cn": "海豚", "en": "Dolphins", "type": "Animal"},
        {"cn": "公主", "en": "Princesses", "type": "Person_F"},
        {"cn": "恐龍", "en": "Dinosaurs", "type": "Animal"}
    ]

    if st.button("🎲 隨機生成新課文", use_container_width=True, key="random_gen_v2"):
        pick = random.choice(master_topics)
        t_cn, t_en, mode = pick["cn"], pick["en"], pick["type"]
        
        # 根據模式生成連貫文章
        if mode == "Animal":
            pool = [(f"I see the {t_en}.", f"我看到了{t_cn}。"), (f"They are very strong.", f"牠們非常強壯。"), (f"Nature is amazing.", f"大自然很神奇。")]
        elif mode == "Nature":
            pool = [(f"The {t_en} is beautiful.", f"{t_cn}很美麗。"), (f"We can see it today.", f"我們今天可以看到它。"), (f"I love the colors.", f"我喜歡這些顏色。")]
        else:
            pool = [(f"I like {t_en}.", f"我喜歡{t_cn}。"), (f"It is very cool.", f"這非常酷。"), (f"Happy day!", f"快樂的一天！")]
        
        st.session_state.active_en_list = [p[0] for p in pool]
        st.session_state.active_tr_list = [p[1] for p in pool]
        st.session_state.current_topic = t_cn

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文主題：{st.session_state.current_topic}")
        for s in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {s}</div>", unsafe_allow_html=True)
        if st.button("🔊 播放全文朗讀", key="read_all_v2"):
            st.audio(get_voice(" ".join(st.session_state.active_en_list), voice_speed))
        with st.expander("👁️ 查看中文翻譯"):
            for tr in st.session_state.active_tr_list: st.write(tr)

with tab3:
    st.header("🎮 聽音挑戰遊戲")
    q_word = random.choice(["Apple", "Bear", "Cat", "Dog", "Mother", "Sun"])
    if st.button("🔊 播放題目音效", key="game_audio_v2"): st.audio(get_voice(q_word, voice_speed))
    ans = st.radio("正確單字是？", ["Apple", "Bear", "Cat", "Dog", "Mother", "Sun"], key="game_radio_v2")
    if st.button("提交回答", key="game_submit_v2"):
        if ans == q_word:
            st.success("答對了！+10 分"); st.session_state.user_score += 10; st.balloons()
        else: st.error("再試一次！")
