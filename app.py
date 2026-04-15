import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置與可愛風 CSS ---
st.set_page_config(page_title="小天才語文樂園", page_icon="🧸", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #FFFDF5; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { background-color: #FFB6C1 !important; color: white !important; }
    /* 大型 Emoji 單字卡樣式 */
    .big-emoji { font-size: 150px; text-align: center; margin-top: -30px; margin-bottom: 10px; }
    /* 短文卡片樣式 */
    .article-box { 
        background: white; 
        padding: 30px; 
        border-radius: 25px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
        border-top: 8px solid #FFB6C1;
    }
    .topic-emoji { font-size: 50px; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧸 小天才安全學習樂園 🤖")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 教學設定")
    lang_choice = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速 (建議 0.8)", 0.5, 1.0, 0.8)
    st.write("---")
    st.caption("100% 安全 Emoji 視覺教材 🌱")

# --- 通用語音函數 ---
def play_audio(text, lang):
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=True)
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# 【關鍵修正】建立完全可控的內建 Emoji 對應表，確保絕對圖文相符
# 這裡我們手動輸入最適合幼兒的單字與 Emoji
safe_visual_db = {
    # 發音練習用 (A-J)
    "Apple": "🍎", "Bear": "🧸", "Cat": "🐱", "Dog": "🐶", "Elephant": "🐘",
    "Fish": "🐟", "Goat": "🐐", "Hat": "🎩", "Igloo": "🛖", "Jam": "🍯",
    "Ant": "🐜",
    
    # 單字卡與短文常用主題用 (英中日通用關鍵字)
    "公園": "🌳", "Picnic": "🧺", "Picnic": "🧺",
    "水果": "🍎", "Fruits": "🍎", "くだもの": "🍎",
    "動物": "🐱", "Animals": "🐱", "どうぶつ": "🐱",
    "晴天": "☀️", "Sunny Day": "☀️", "はれ": "☀️",
    "海洋": "🌊", "Ocean": "🌊", "うみ": "🌊",
    "貓咪": "🐱", "Cat": "🐱", "ねこ": "🐱",
    "小狗": "🐶", "Dog": "🐶", "いぬ": "🐶",
    "汽車": "🚗", "Car": "🚗", "くるま": "🚗",
    "星星": "⭐", "Star": "⭐", "ほし": "⭐"
}

#
