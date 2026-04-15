import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="小天才語文樂園", page_icon="🎨", layout="wide")

# --- 自定義 CSS 讓介面更可愛 ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 10px 10px 0px 0px; font-weight: bold; font-size: 18px; }
    .main { background-color: #FFFDF5; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 小天才語文多樣化學習機 🤖")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 教學設定")
    lang_choice = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    age_group = st.select_slider("適齡階段", options=["4-6", "7-8", "9-10", "11-12"])
    voice_speed = st.slider("語速 (0.8 最推薦)", 0.5, 1.0, 0.8)
    st.write("---")
    st.info("💡 提示：切換上方分頁來選擇不同的練習模式！")

# --- 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["📖 短文閱讀", "🔤 發音練習", "🖼️ 單字卡", "🎮 遊戲區"])

# --- 語音生成函數 ---
def play_audio(text, lang):
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=True)
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# --- Tab 1: 短文搭配圖片 (練習閱讀) ---
with tab1:
    st.header("📖 情境短文練習")
    topic_story = st.text_input("輸入短文主題：", "公園野餐", key="t1")
    if st.button("生成短文"):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image("https://img.freepik.com/free-vector/children-playing-park_1308-31203.jpg", caption="情境預覽圖")
        with col2:
            story_en = f"It is a sunny day. We are in the park. Look! I have a big sandwich. It is yummy!"
            story_jp = f"今日はいい天気です。公園にいます。見て！大きなサンドイッチがあります。美味しいです！"
            display_text = story_jp if "日" in lang_choice else story_en
            st.info(f"**{display_text}**")
            st.write(f"（中文：今天天氣很好。我們在公園裡。看！我有一個大三明治。真好吃！）")
            play_audio(display_text, lang_choice)

# --- Tab 2: 字母與發音練習 (基礎練習) ---
with tab2:
    st.header("🔤 字母與自然發音")
    letter = st.selectbox("選擇要練習的字母：", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Letter", value=letter)
        st.write(f"Phonics: {letter} says /" + letter.lower() + "/.")
    with col2:
        st.write("範例單字：")
        example_word = {"A": "Apple", "B": "Bear", "C": "Cat"}.get(letter, "Ant")
        st.subheader(f"👉 {example_word}")
        play_audio(f"{letter}, {letter}, {example_word}", lang_choice)

# --- Tab 3: 圖片與單字 (單字練習) ---
with tab3:
    st.header("🖼️ 閃視單字卡")
    col1, col2, col3 = st.columns(3)
    words = [("Apple", "🍎"), ("Dog", "🐶"), ("Sun", "☀️")]
    for i, (w, e) in enumerate(words):
        with [col1, col2, col3][i]:
            st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{e}</h1>", unsafe_allow_html=True)
            st.button(f"聽發音: {w}", on_click=play_audio, args=(w, lang_choice), key=f"btn_{w}")

# --- Tab 4: 遊戲區 ---
with tab4:
    st.header("🎮 互動小遊戲")
    game_type = st.selectbox("選擇遊戲", ["數數看遊戲", "連連看 (開發中)"])
    
    if game_type == "數數看遊戲":
        game_html = """
        <div style="background:#FFF9E3; padding:20px; border-radius:20px; text-align:center; border:2px dashed #FFB6C1;">
            <h3>🔊 Listen: "Four Apples"</h3>
            <p>請點選 4 顆蘋果！</p>
            <div id="apples" style="font-size:50px;">
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
                <span onclick="check(this)" style="cursor:pointer">🍎</span>
            </div>
            <h2 id="msg"></h2>
            <button onclick="location.reload()" style="padding:10px; border-radius:10px;">重新開始</button>
        </div>
        <script>
            let count = 0;
            function check(el) {
                if(el.style.opacity == '0.3') return;
                el.style.opacity = '0.3';
                count++;
                if(count == 4) document.getElementById('msg').innerText = "🎉 Correct! You did it!";
                if(count > 4) document.getElementById('msg').innerText = "❌ Too many! Try again.";
            }
        </script>
        """
        components.html(game_html, height=400)
