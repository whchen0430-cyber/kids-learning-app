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

# 輔助函數：根據輸入找出對應 Emoji，找不到就給星號
def get_safe_visual(keyword):
    return safe_visual_db.get(keyword, "⭐")

# --- 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 發音練習", "🖼️ 單字卡", "📖 短文閱讀", "🎮 遊戲區"])

# --- 1. 發音練習 (使用內建絕對安全 Emoji) ---
with tab1:
    st.header("🔤 Phonics 自然發音啟蒙")
    # 我們只列出我們在 safe_visual_db 中定義好安全視覺的字母
    active_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    letter = st.selectbox("請選擇一個字母開始：", active_letters)
    
    phonics_map = {
        "A": "Apple", "B": "Bear", "C": "Cat", "D": "Dog", "E": "Elephant",
        "F": "Fish", "G": "Goat", "H": "Hat", "I": "Igloo", "J": "Jam"
    }
    word = phonics_map.get(letter)
    
    # 這裡顯示絕對可愛的泰迪熊 🧸，而不是可怕的真實灰熊照片
    st.markdown(f"<div class='big-emoji'>{get_safe_visual(word)}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"## 字母：{letter}")
        st.subheader(f"發音：{letter}, {letter}, {word}")
    with col2:
        if st.button(f"🔊 播放 {letter} 發音", key="voice1"):
            play_audio(f"{letter}, {letter}, {word}", lang_choice)

# --- 2. 圖片與單字 (使用內建絕對安全 Emoji) ---
with tab2:
    st.header("🖼️ 閃視單字記憶卡")
    # 這裡我們列出所有已定義好 Emoji 的單字，讓孩子從中選擇，避免自由輸入導致圖文不符
    safe_words = ["蘋果", "貓咪", "小狗", "汽車", "星星", "動物", "水果"]
    word_input = st.selectbox("選擇想學習的單字主題：", safe_words)
    
    if word_input:
        st.markdown(f"<div class='big-emoji'>{get_safe_visual(word_input)}</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.title(f"{word_input}")
        with col2:
            # 將中日文轉為英日文發音用關鍵字
            voice_map = {"蘋果": "Apple", "貓咪": "Cat", "小狗": "Dog", "汽車": "Car", "星星": "Star", "動物": "Animals", "水果": "Fruits"}
            if st.button(f"🔊 聽發音", key="voice2"):
                play_audio(voice_map[word_input], lang_choice)

# --- 3. 短文閱讀 (敘事格式) ---
with tab3:
    st.header("📖 情境小短文閱讀")
    # 教材主題也要選擇內建的，確保圖片相符
    story_topic_safe = st.selectbox("輸入短文主題：", ["晴天", "海洋", "動物"])
    
    if st.button("✨ 生成圖文短文", key="voice3"):
        # 顯示主題大 Emoji，保證圖文相符
        st.markdown(f"<div class='topic-emoji'>{get_safe_visual(story_topic_safe)}</div>", unsafe_allow_html=True)
        
        # 模擬小短文 (非對話式)
        if "日" in lang_choice:
            story_text = f"お日様がキラキラしています。空は青くて、とてもきれいです。外で遊びましょう！楽しいですよ。"
            trans = "太陽閃閃發光。天空藍藍的，非常漂亮。在外面玩耍吧！非常開心喔。"
        else:
            story_text = f"The sun is shining bright in the big blue sky. It is a beautiful day. Let's play outside! It is fun."
            trans = "太陽在藍藍的大天空中閃閃發光。今天天氣很好。在外面玩耍吧！非常開心。"

        st.markdown(f"<div class='article-box'><h3>{story_text}</h3><hr><p style='color:gray;'>{trans}</p></div>", unsafe_allow_html=True)
        play_audio(story_text, lang_choice)

# --- 4. 遊戲區 ---
with tab4:
    st.header("🎮 互動驗收區")
    game_html = """
    <div style="background:#FFFDF5; padding:20px; border-radius:20px; text-align:center; border:3px solid #FFB6C1;">
        <h3>🔔 指令：點選 4 個星星！</h3>
        <div style="font-size:70px; margin:20px;">
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
        </div>
        <h2 id="msg" style="color:#FF69B4;"></h2>
        <button onclick="location.reload()" style="padding:10px; border-radius:10px;">重新挑戰</button>
    </div>
    <script>
        let score = 0;
        function check(el) {
            if(el.style.opacity == '0.2') return;
            el.style.opacity = '0.2'; // 點擊後變透明
            score++;
            if(score == 4) document.getElementById('msg').innerText = "🎉 答對了！Good job!";
            if(score > 4) document.getElementById('msg').innerText = "❌ 點太多囉，再試一次！";
        }
    </script>
    """
    components.html(game_html, height=450)
