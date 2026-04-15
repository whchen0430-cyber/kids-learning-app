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

# --- 2. 字母與單字資料庫 A-Z ---
@st.cache_data
def get_db():
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
DB = get_db()

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("👤 學生狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神秘的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化了！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "雷龍成長中", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "成年霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍現身！", "160px", "#B22222"
    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("教材年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母與單字", "📖 萬能隨機短文", "🎮 互動挑戰"])

# --- Tab 2: 萬能隨機短文發送機 (海量主題) ---
with tab2:
    st.header("📖 萬能隨機教材發送機")
    u_len_goal = st.select_slider("📏 文章長度 (字數上限)", options=[10, 20, 30, 40, 50], value=20)
    
    # 萬能主題庫
    master_topics = [
        {"cn": "冰淇淋", "en": "Ice Cream", "type": "Food"},
        {"cn": "大象", "en": "Elephants", "type": "Animal"},
        {"cn": "宇宙", "en": "Space", "type": "Place"},
        {"cn": "下雨", "en": "Rain", "type": "Nature"},
        {"cn": "鋼琴", "en": "The Piano", "type": "Object"},
        {"cn": "腳踏車", "en": "Bicycles", "type": "Object"},
        {"cn": "彩虹", "en": "Rainbows", "type": "Nature"},
        {"cn": "飛行", "en": "Flying", "type": "Activity"},
        {"cn": "海豚", "en": "Dolphins", "type": "Animal"},
        {"cn": "披薩", "en": "Pizza", "type": "Food"},
        {"cn": "超級英雄", "en": "Superheroes", "type": "Person_M"},
        {"cn": "公主", "en": "Princesses", "type": "Person_F"},
        {"cn": "圖書館", "en": "The Library", "type": "Place"},
        {"cn": "恐龍", "en": "Dinosaurs", "type": "Animal"}
    ]

    if st.button("🎲 隨機生成新課文 (多樣化主題)", use_container_width=True):
        pick = random.choice(master_topics)
        t_cn, t_en, mode = pick["cn"], pick["en"], pick["type"]
        
        # 根據模式生成連貫文章
        if mode == "Food" or mode == "Object":
            pool = [(f"I love {t_en}.", f"我愛{t_cn}。"), (f"It is very special to me.", f"它對我來說很特別。"), (f"We can use {t_en.lower()} every day.", f"我們每天都會用到{t_cn}。"), (f"It makes life happy.", f"它讓生活變得快樂。")]
        elif mode == "Animal":
            pool = [(f"Look at the {t_en}.", f"看那些{t_cn}。"), (f"They are very strong and smart.", f"牠們非常強壯且聰明。"), (f"We can see them at the zoo.", f"我們可以在動物園看到牠們。"), (f"Nature is amazing.", f"大自然很神奇。")]
        elif mode == "Nature":
            pool = [(f"I see the {t_en}.", f"我看到了{t_cn}。"), (f"The {t_en} is beautiful.", f"{t_cn}很美麗。"), (f"It is a gift from nature.", f"這是大自然的禮物。"), (f"Let's protect our world.", f"讓我們保護世界。")]
        elif mode.startswith("Person"):
            prn = "She" if mode == "Person_F" else "He"
            pool = [(f"I like {t_en}.", f"我喜歡{t_cn}。"), (f"{prn} is very brave.", f"{'她' if prn=='She' else '他'}非常勇敢。"), (f"We can learn from {prn.lower()}.", f"我們可以向{'她' if prn=='She' else '他'}學習。"), (f"It is a great story.", f"這是一個很棒的故事。")]
        else: # Place / Activity
            pool = [(f"Welcome to {t_en}.", f"歡迎來到{t_cn}。"), (f"Everything here is fun.", f"這裡的一切都很難忘。"), (f"We can explore new things.", f"我們可以探索新事物。"), (f"It is an adventure.", f"這是一場冒險。")]
        
        # 根據字數限制擷取
        st.session_state.active_en_list = [p[0] for p in pool]
        st.session_state.active_tr_list = [p[1] for p in pool]
        st.session_state.current_topic = t_cn

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文主題：{st.session_state.current_topic}")
        for s in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px;'>• {s}</div>", unsafe_allow_html=True)
        if st.button("🔊 播放全文朗讀"):
            st.audio(get_voice(" ".join(st.session_state.active_en_list), voice_speed))
        with st.expander("👁️ 查看精準中文翻譯"):
            for tr in st.session_state.active_tr_list: st.write(tr)
