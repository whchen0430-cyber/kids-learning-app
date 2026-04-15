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

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. A-Z 資料庫 ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "The apple is red.", "蘋果是紅的。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "Kick the ball.", "踢球。")]},
        "C": {"upper": "C", "lower": "c", "words": [("Cat", "🐱", "Cute cat.", "可愛貓。"), ("Cake", "🎂", "Sweet cake.", "甜蛋糕。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。"), ("Duck", "🦆", "Duck swims.", "鴨子游泳。")]},
        "E": {"upper": "E", "lower": "e", "words": [("Elephant", "🐘", "Big elephant.", "大象很大。"), ("Egg", "🥚", "Eat an egg.", "吃蛋。")]},
        "F": {"upper": "F", "lower": "f", "words": [("Fish", "🐟", "Blue fish.", "藍色的魚。"), ("Frog", "🐸", "Green frog.", "綠青蛙。")]},
        "G": {"upper": "G", "lower": "g", "words": [("Goat", "🐐", "The goat eats.", "山羊吃東西。"), ("Giraffe", "🦒", "Long neck.", "長脖子。")]},
        "H": {"upper": "H", "lower": "h", "words": [("Horse", "🐎", "I ride a horse.", "我騎馬。"), ("Hat", "🎩", "Wear a hat.", "戴帽子。")]},
        "I": {"upper": "I", "lower": "i", "words": [("Ice cream", "🍦", "Cold ice cream.", "冷冰淇淋。"), ("Igloo", "🛖", "Ice house.", "冰屋。")]},
        "J": {"upper": "J", "lower": "j", "words": [("Jam", "🍯", "Sweet jam.", "甜果醬。"), ("Juice", "🧃", "Fruit juice.", "果汁。")]},
        "K": {"upper": "K", "lower": "k", "words": [("Kite", "🪁", "Fly a kite.", "放風箏。"), ("Koala", "🐨", "Cute koala.", "無尾熊。")]},
        "L": {"upper": "L", "lower": "l", "words": [("Lion", "🦁", "King lion.", "獅子王。"), ("Lemon", "🍋", "Sour lemon.", "酸檸檬。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Monkey", "🐒", "Funny monkey.", "猴子好笑。"), ("Moon", "🌙", "White moon.", "白月亮。")]},
        "N": {"upper": "N", "lower": "n", "words": [("Nose", "👃", "My nose.", "我的鼻子。"), ("Nut", "🥜", "Eat a nut.", "吃堅果。")]},
        "O": {"upper": "O", "lower": "o", "words": [("Orange", "🍊", "Juicy orange.", "橘子多汁。"), ("Owl", "🦉", "Wise owl.", "貓頭鷹。")]},
        "P": {"upper": "P", "lower": "p", "words": [("Pig", "🐷", "Pink pig.", "粉紅豬。"), ("Pear", "🍐", "Sweet pear.", "梨子。")]},
        "Q": {"upper": "Q", "lower": "q", "words": [("Queen", "👸", "The queen.", "皇后。"), ("Question", "❓", "Ask me.", "問我。")]},
        "R": {"upper": "R", "lower": "r", "words": [("Rabbit", "🐰", "White rabbit.", "小白兔。"), ("Rain", "🌧️", "Cold rain.", "冷雨。")]},
        "S": {"upper": "S", "lower": "s", "words": [("Sun", "☀️", "Hot sun.", "太陽熱。"), ("Snake", "🐍", "Long snake.", "長蛇。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "老虎壯。"), ("Tree", "🌳", "Tall tree.", "大樹。")]},
        "U": {"upper": "U", "lower": "u", "words": [("Umbrella", "🌂", "My umbrella.", "雨傘。"), ("Up", "⬆️", "Go up.", "向上。")]},
        "V": {"upper": "V", "lower": "v", "words": [("Van", "🚐", "Drive a van.", "開車。"), ("Violin", "🎻", "Play violin.", "小提琴。")]},
        "W": {"upper": "W", "lower": "w", "words": [("Whale", "🐋", "Big whale.", "大鯨魚。"), ("Window", "🪟", "Open window.", "開窗。")]},
        "X": {"upper": "X", "lower": "x", "words": [("Box", "📦", "A box.", "盒子。"), ("Fox", "🦊", "Red fox.", "紅狐狸。")]},
        "Y": {"upper": "Y", "lower": "y", "words": [("Yo-yo", "🪀", "Red yo-yo.", "溜溜球。"), ("Yellow", "💛", "Bright yellow.", "黃色。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zero", "0️⃣", "Zero.", "零。")]}
    }

DB = get_db()

# --- 3. 側邊欄：進化邏輯 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 目前積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "孵化小龍！", "50px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "威猛霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center;'><h1 style='font-size:{d_size};'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 語音輔助 ---
def get_voice(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang=('en' if "英" in lang else 'ja'), slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 基礎練習", "📖 智能短文生成", "🎮 挑戰遊戲", "🏆 成就"])

with tab1:
    st.header("🔤 字母與單字")
    letter = st.selectbox("選擇字母", list(DB.keys()))
    info = DB[letter]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    if st.button("🔊 播放字母發音"):
        st.audio(get_voice(info['upper'], target_lang, voice_speed), format="audio/mp3")
    for w, emo, sent, tr in info["words"]:
        st.write(f"### {emo} {w}")
        st.write(f"**Sentence:** {sent} (翻譯: {tr})")
        if st.button(f"🔊 聽發音", key=f"btn_{w}"):
            st.audio(get_voice(f"{w}. {sent}", target_lang, voice_speed), format="audio/mp3")
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 核心動態生成引擎 (修復內文不動問題) ---
with tab2:
    st.header("📖 智能主題教材生成")
    user_topic = st.text_input("📝 請輸入主題 (例如：去日本、恐龍、我的家)", "去旅遊")
    
    if st.button("🚀 點擊生成全新內容", key="gen_btn"):
        # 1. 映射內部英文關鍵字 (確保 100% 英文原文)
        t_en = "Your Topic"
        if "去" in user_topic or "旅" in user_topic: t_en = "Travel"
        elif "吃" in user_topic or "煮" in user_topic: t_en = "Food"
        elif "貓" in user_topic or "狗" in user_topic: t_en = "Pets"
        elif "學" in user_topic: t_en = "School"
        else: t_en = user_topic[:10] # 直接擷取輸入字

        # 2. 核心：根據年齡直接渲染「完全不同」的結構 (絕對會動)
        if user_age == 4:
            content = f"Look at {t_en}. It is fun. I like {t_en} very much."
            gram = "4歲：基礎單句型。"
        elif user_age == 6:
            content = f"We see {t_en} today. The {t_en} has many colors. It makes us very happy."
            gram = "6歲：加入色彩描述與代名詞。"
        elif user_age == 8:
            content = f"It is a great day to explore {t_en}. We can learn many interesting things about it together."
            gram = "8歲：助動詞 can 與不定詞。"
        elif user_age == 10:
            content = f"If you visit {t_en}, you will find many amazing secrets. It is the best way to spend time with friends."
            gram = "10歲：條件句 (If) 與最高級。"
        else: # 12歲
            content = f"Experiencing {t_en} provides people with a unique opportunity to understand the world. We believe that {t_en} will become a memorable part of our lives."
            gram = "12歲：動名詞主詞與賓語子句。"

        # 3. 強制存入 Session State，確保畫面立刻刷新
        st.session_state.current_text = re.sub(r'[\u4e00-\u9fa5]', '', content) # 確保 100% 英文
        st.session_state.current_gram = gram
        st.session_state.current_topic = user_topic

    # 4. 顯示內容 (鎖定結構：一句一行)
    if 'current_text' in st.session_state:
        st.subheader(f"📜 課文原文：{st.session_state.current_topic}")
        for line in st.session_state.current_text.split('.'):
            if line.strip():
                st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px;'>• {line.strip()}.</div>", unsafe_allow_html=True)
        
        if st.button("🔊 全文朗讀"):
            st.audio(get_voice(st.session_state.current_text, target_lang, voice_speed), format="audio/mp3")
        
        st.success(f"**💡 教學重點:** {st.session_state.current_gram}")
        with st.expander("👁️ 查看翻譯"):
            st.write(f"這是一段關於「{st.session_state.current_topic}」的主題練習內容。")

# --- Tab 3: 遊戲區 ---
with tab3:
    st.header("🎮 挑戰遊戲")
    def refresh_q():
        pool = []
        for l in DB: pool.extend(DB[l]["words"])
        items = random.sample(pool, 3)
        return items, random.choice(items)
    if f"q_{st.session_state.game_turn}" not in st.session_state:
        st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"] = refresh_q()
    
    cq, ct = st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"]
    if st.button("🔊 播放題目"):
        st.audio(get_voice(ct[0], target_lang, voice_speed), format="audio/mp3")
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(cq):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"{word}", key=f"g_btn_{st.session_state.game_turn}_{i}"):
                if word == ct[0]:
                    st.balloons(); st.session_state.user_score += 5; st.session_state.game_turn += 1; time.sleep(1); st.rerun()
                else: st.error("❌ Try again!")

with tab4:
    st.header("🏆 成就")
    st.subheader(f"積分：{st.session_state.user_score} / 150")
