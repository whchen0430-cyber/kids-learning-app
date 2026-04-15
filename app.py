import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="專業語文學習機器人", page_icon="🎓", layout="wide")

# --- 1. A-Z 完整發音資料庫 (IPA + 秘訣) ---
ALPHABET_DB = {
    "A": {"le": "🅰️", "w": "Apple", "we": "🍎", "ipa": "/æ/", "tip": "嘴巴張大，舌頭放平"},
    "B": {"le": "🅱️", "w": "Bear", "we": "🧸", "ipa": "/b/", "tip": "雙唇緊閉，突然噴氣"},
    "C": {"le": "©️", "w": "Cat", "we": "🐱", "ipa": "/k/", "tip": "舌根抬起，快速吐氣"},
    "D": {"le": "🇩", "w": "Dog", "we": "🐶", "ipa": "/d/", "tip": "舌尖頂住上齒齦，彈開"},
    "E": {"le": "🇪", "w": "Elephant", "we": "🐘", "ipa": "/ɛ/", "tip": "嘴巴微張，嘴角向兩邊"},
    "F": {"le": "🇫", "w": "Fish", "we": "🐟", "ipa": "/f/", "tip": "上齒輕咬下唇，吹氣"},
    "G": {"le": "🇬", "w": "Goat", "we": "🐐", "ipa": "/ɡ/", "tip": "舌根抬起，喉嚨發聲"},
    "H": {"le": "🇭", "w": "Hat", "we": "🎩", "ipa": "/h/", "tip": "張嘴，輕鬆吐氣"},
    "I": {"le": "ℹ️", "w": "Igloo", "we": "🛖", "ipa": "/ɪ/", "tip": "嘴巴微張，舌尖抵下齒"},
    "J": {"le": "🇯", "w": "Jam", "we": "🍯", "ipa": "/dʒ/", "tip": "雙唇突出，舌尖頂上顎"},
    "K": {"le": "🇰", "w": "Kite", "we": "🪁", "ipa": "/k/", "tip": "快速吐氣"},
    "L": {"le": "🇱", "w": "Lion", "we": "🦁", "ipa": "/l/", "tip": "舌尖頂住上齒齦"},
    "M": {"le": "Ⓜ️", "w": "Monkey", "we": "🐒", "ipa": "/m/", "tip": "雙唇緊閉，鼻子出氣"},
    "N": {"le": "🇳", "w": "Nose", "we": "👃", "ipa": "/n/", "tip": "舌尖頂上齒齦"},
    "O": {"le": "🅾️", "w": "Orange", "we": "🍊", "ipa": "/ɑ/", "tip": "嘴巴張圓，舌頭放低"},
    "P": {"le": "🅿️", "w": "Pig", "we": "🐷", "ipa": "/p/", "tip": "雙唇緊閉，噴氣"},
    "Q": {"le": "🇶", "w": "Queen", "we": "👸", "ipa": "/kw/", "tip": "圓唇，舌根抬起"},
    "R": {"le": "🇷", "w": "Rabbit", "we": "🐇", "ipa": "/r/", "tip": "舌尖捲起，不碰上顎"},
    "S": {"le": "🇸", "w": "Sun", "we": "☀️", "ipa": "/s/", "tip": "舌尖靠近上齒齦，吹氣"},
    "T": {"le": "🇹", "w": "Tiger", "we": "🐯", "ipa": "/t/", "tip": "舌尖頂上齒齦，彈開"},
    "U": {"le": "🇺", "w": "Umbrella", "we": "🌂", "ipa": "/ʌ/", "tip": "嘴巴微張，舌頭放低"},
    "V": {"le": "🇻", "w": "Van", "we": "🚐", "ipa": "/v/", "tip": "上齒咬下唇，發聲"},
    "W": {"le": "🇼", "w": "Watch", "we": "⌚", "ipa": "/w/", "tip": "圓唇，舌根抬起"},
    "X": {"le": "🇽", "w": "Box", "we": "📦", "ipa": "/ks/", "tip": "結尾發出/ks/音"},
    "Y": {"le": "🇾", "w": "Yo-Yo", "we": "🪀", "ipa": "/j/", "tip": "嘴巴微張，舌尖抵下齒"},
    "Z": {"le": "🇿", "w": "Zebra", "we": "🦓", "ipa": "/z/", "tip": "發出類似蜜蜂嗡嗡聲"}
}

# --- 2. 側邊欄設定 (年齡與語系) ---
with st.sidebar:
    st.header("⚙️ 教師設定面板")
    target_lang = st.radio("目標學習語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡區間", options=[4, 6, 8, 10, 12])
    
    # 智慧等級判定
    if user_age <= 6: level = "基礎級 (Kindergarten)"
    elif user_age <= 10: level = "初級 (Elementary)"
    else: level = "進階級 (Junior High)"
    
    st.success(f"📌 目前教材等級：{level}")
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)

# --- 3. 功能分頁 ---
tab1, tab2, tab3 = st.tabs(["🔤 專業發音練習", "📖 程度短文應用", "🎮 互動挑戰遊戲"])

# --- Tab 1: 26字母專業發音 ---
with tab1:
    st.header("🔤 Phonics & IPA 26字母大冒險")
    letter_choice = st.selectbox("請選擇練習字母：", list(ALPHABET_DB.keys()))
    data = ALPHABET_DB[letter_choice]
    
    # 排版展示：左右 Emoji
    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; gap: 40px; background: white; padding: 20px; border-radius: 20px;">
            <div style="font-size: 150px;">{data['le']}</div>
            <div style="font-size: 60px; color: #FFB6C1;">➡️</div>
            <div style="font-size: 150px;">{data['we']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"## **Word: {data['w']}**")
        st.markdown(f"### **IPA: {data['ipa']}**")
    with col2:
        st.warning(f"💡 發音技巧：{data['tip']}")
        if st.button(f"🔊 播放專業發音 ({letter_choice})"):
            clean_text = f"{letter_choice}, {letter_choice}, {data['w']}"
            lang_code = 'en' if "英" in target_lang else 'ja'
            tts = gTTS(text=clean_text, lang=lang_code, slow=True)
            tts.save("speech.mp3")
            with open("speech.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# --- Tab 2: 程度短文 (根據年齡動態變化) ---
with tab2:
    st.header(f"📖 {user_age}歲 專屬情境小文章")
    topic = st.text_input("輸入你想學的主題：", "公園 (Park)")
    
    # 動態文章邏輯
    if user_age <= 6:
        content = f"I see a {topic}. The {topic} is big. It is very pretty."
        trans = f"我看見一個{topic}。它很大。它非常漂亮。"
    elif user_age <= 10:
        content = f"Today is a sunny day. We are playing at the {topic}. I feel very happy with my friends."
        trans = f"今天天氣晴朗。我們正在{topic}玩耍。我和朋友們在一起覺得很快樂。"
    else:
        content = f"The {topic} is an essential part of our community. We should maintain its beauty for everyone to enjoy."
        trans = f"{topic}是我們社區的重要組成部分。我們應該保持它的美感，讓每個人都能享受。"

    st.info(f"**{content}**")
    st.caption(f"翻譯：{trans}")
    if st.button("🔊 播放全文 (0.8x)"):
        lang_code = 'en' if "英" in target_lang else 'ja'
        tts = gTTS(text=content, lang=lang_code, slow=True)
        tts.save("story.mp3")
        with open("story.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

# --- Tab 3: 遊戲區 (語言隨動) ---
with tab3:
    st.header("🎮 語言互動挑戰")
    game_instr = {
        "英文 (English)": {"title": "Listen & Click", "task": "Click on 4 stars!", "success": "Amazing! You got it!"},
        "日文 (日本語)": {"title": "きいて、クリックして", "task": "ほしを 4つ おしてね！", "success": "すごい！せいかいです！"}
    }
    curr = game_instr[target_lang]
    
    game_html = f"""
    <div style="background:white; padding:20px; border-radius:20px; text-align:center; border:4px solid #FFB6C1;">
        <h2>{curr['title']}</h2>
        <p style="font-size:24px;">{curr['task']}</p>
        <div style="font-size:70px;">
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
            <span onclick="check(this)" style="cursor:pointer; margin:10px;">⭐</span>
        </div>
        <h1 id="msg" style="color:#4CAF50;"></h1>
        <button onclick="location.reload()" style="padding:10px; border-radius:10px;">Reset</button>
    </div>
    <script>
        let count = 0;
        function check(el) {{
            if(el.style.opacity == '0.2') return;
            el.style.opacity = '0.2';
            count++;
            if(count == 4) document.getElementById('msg').innerText = "{curr['success']}";
        }}
    </script>
    """
    components.html(game_html, height=450)
