import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="小天才語文樂園", page_icon="🎓", layout="wide")

# 自定義可愛風 CSS
st.markdown("""
    <style>
    .main { background-color: #FFF9FB; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #F0F2F6; 
        border-radius: 15px 15px 0 0; 
        padding: 10px 20px;
        font-weight: bold;
    }
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

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 教學設定")
    lang_choice = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速 (建議 0.8)", 0.5, 1.0, 0.8)
    st.write("---")
    st.caption("教學順序：發音 → 單字 → 短文 → 遊戲")

# --- 通用語音與圖片函數 ---
def play_audio(text, lang):
    # 清理非目標語系的文字（避免讀到中文）
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=True)
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

def get_image(keyword):
    # 加入 'clipart' 或 'kids' 標籤讓圖片更符合兒童教材風格
    return f"https://source.unsplash.com/featured/?{keyword},kid,illustration"

# --- 功能分頁 (依照要求的順序更動) ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 發音練習", "🖼️ 單字卡", "📖 短文閱讀", "🎮 遊戲區"])

# --- 1. 發音練習 (基礎練習) ---
with tab1:
    st.header("🔤 Phonics 自然發音啟蒙")
    letter = st.selectbox("請選擇一個字母開始：", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    # 建立字母對應單字表
    phonics_map = {
        "A": "Apple", "B": "Bear", "C": "Cat", "D": "Dog", "E": "Elephant",
        "F": "Fish", "G": "Goat", "H": "Hat", "I": "Igloo", "J": "Jam"
    }
    word = phonics_map.get(letter, "Ant")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(get_image(word), use_column_width=True)
    with col2:
        st.markdown(f"## 字母：{letter}")
        st.subheader(f"發音：{letter}, {letter}, {word}")
        st.write("👉 點擊下方播放音檔跟著讀：")
        if st.button(f"🔊 播放 {letter} 發音"):
            play_audio(f"{letter}, {letter}, {word}", lang_choice)

# --- 2. 圖片與單字 (單字練習) ---
with tab2:
    st.header("🖼️ 閃視單字記憶卡")
    word_input = st.text_input("輸入想學習的單字主題（例如：Banana, Car, Sky）：", "Banana")
    if word_input:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(get_image(word_input), width=350)
        with c2:
            st.title(f"Target Word: {word_input}")
            if st.button(f"🔊 聽聽看 {word_input} 怎麼說"):
                play_audio(word_input, lang_choice)

# --- 3. 短文搭配圖片 (練習閱讀) ---
with tab3:
    st.header("📖 情境小短文閱讀")
    story_topic = st.text_input("輸入短文主題（如：Ocean, Farm）：", "Ocean")
    if st.button("✨ 生成圖文短文"):
        col1, col2 = st.columns([1, 1.2])
        # 模擬小短文 (非對話式)
        if "日" in lang_choice:
            story_text = f"海はとても広いです。青い魚が泳いでいます。水は冷たくて気持ちいいです。海が大好きです！"
            trans = "大海非常寬廣。有青色的魚在游泳。水涼涼的很舒服。我最喜歡大海了！"
        else:
            story_text = f"The ocean is very big and blue. I can see many small fish. The water is cool and clean. I love the ocean so much!"
            trans = "大海又大又藍。我可以看到很多小魚。水很涼爽乾淨。我好喜歡大海！"

        with col1:
            st.image(get_image(story_topic), use_column_width=True)
        with col2:
            st.markdown(f"<div class='article-box'><h3>{story_text}</h3><hr><p style='color:gray;'>{trans}</p></div>", unsafe_allow_html=True)
            play_audio(story_text, lang_choice)

# --- 4. 遊戲區 (加強連結) ---
with tab4:
    st.header("🎮 互動驗收區")
    st.subheader("🔊 聽聽看，點點看！")
    
    # 數數遊戲 HTML 嵌入
    game_html = """
    <div style="background:#FFF9E3; padding:20px; border-radius:20px; text-align:center; border:3px solid #FFB6C1;">
        <h3>🔔 指令：點選 4 個星星！</h3>
        <div style="font-size:50px; margin:20px;">
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:5px; display:inline-block;">⭐</span>
        </div>
        <h2 id="msg" style="color:#FF69B4;"></h2>
        <button onclick="location.reload()">重新挑戰</button>
    </div>
    <script>
        let score = 0;
        function check(el) {
            if(el.style.filter == 'grayscale(100%)') return;
            el.style.filter = 'grayscale(100%)';
            el.style.transform = 'scale(0.8)';
            score++;
            if(score == 4) document.getElementById('msg').innerText = "🎉 答對了！You are amazing!";
            if(score > 4) document.getElementById('msg').innerText = "😵 點太多了，再試一次！";
        }
    </script>
    """
    components.html(game_html, height=450)
