import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="小天才語文樂園", page_icon="🎓", layout="wide")

# 自定義 CSS
st.markdown("""
    <style>
    .main { background-color: #FFF9FB; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { background-color: #FFB6C1 !important; color: white !important; }
    .article-box { 
        background: white; 
        padding: 30px; 
        border-radius: 25px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
        border-top: 8px solid #FFB6C1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 小天才循序漸進學習機 🤖")

# --- 通用語音與圖片函數 ---
def play_audio(text, lang):
    # 清理非目標語系的文字（避免讀到中文）
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=True)
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# 【更新重點】更穩定的圖片抓取語法
def get_image_url(keyword):
    # 加入隨機參數防止緩存失敗，並限制在兒童/插畫風格
    return f"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&q=80&w=800&q={keyword}"

# 或是使用更直接的關鍵字搜尋 (這通常最穩定)
def get_stable_img(keyword):
    return f"https://loremflickr.com/800/600/{keyword},kid,cute/all"

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 教學設定")
    lang_choice = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速 (建議 0.8)", 0.5, 1.0, 0.8)
    st.write("---")
    st.caption("圖片無法顯示時，請重新整理頁面。")

# --- 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 發音練習", "🖼️ 單字卡", "📖 短文閱讀", "🎮 遊戲區"])

# --- 1. 發音練習 (基礎練習) ---
with tab1:
    st.header("🔤 Phonics 自然發音啟蒙")
    letter = st.selectbox("請選擇一個字母開始：", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    phonics_map = {
        "A": "Apple", "B": "Bear", "C": "Cat", "D": "Dog", "E": "Elephant",
        "F": "Fish", "G": "Goat", "H": "Hat", "I": "Igloo", "J": "Jam",
        "K": "Kite", "L": "Lion", "M": "Monkey", "N": "Nose", "O": "Orange"
    }
    word = phonics_map.get(letter, "Ant")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        # 修正：確保每個字母都有對應的穩定圖片
        img_url = get_stable_img(word)
        st.image(img_url, caption=f"{letter} is for {word}", use_column_width=True)
    with col2:
        st.markdown(f"## 字母：{letter}")
        st.subheader(f"發音：{letter}, {letter}, {word}")
        if st.button(f"🔊 播放 {letter} 語音"):
            play_audio(f"{letter}, {letter}, {word}", lang_choice)

# --- 2. 圖片與單字 (單字練習) ---
with tab2:
    st.header("🖼️ 閃視單字記憶卡")
    word_input = st.text_input("輸入單字（英/日）：", "Cat")
    if word_input:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(get_stable_img(word_input), width=400)
        with c2:
            st.title(f"Target Word: {word_input}")
            if st.button(f"🔊 聽聽看 {word_input}"):
                play_audio(word_input, lang_choice)

# --- 3. 短文閱讀 (依據
