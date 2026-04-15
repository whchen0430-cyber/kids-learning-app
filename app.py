import streamlit as st
from gtts import gTTS
import os
import re
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="專業語文學習機器人", page_icon="🎓", layout="wide")

# --- 1. 核心教材資料庫 (依年齡與類別設計) ---
# 單字與圖片關鍵字對應表 (類別化)
VOCAB_DB = {
    "動物 (Animals)": {
        "easy": [("Dog", "🐶"), ("Cat", "🐱"), ("Bird", "🐦")],
        "medium": [("Elephant", "🐘"), ("Giraffe", "🦒"), ("Lion", "🦁")],
        "hard": [("Chameleon", "🦎"), ("Platypus", "🦆"), ("Kangaroo", "🦘")]
    },
    "食物 (Food)": {
        "easy": [("Apple", "🍎"), ("Milk", "🥛"), ("Cake", "🍰")],
        "medium": [("Sandwich", "🥪"), ("Broccoli", "🥦"), ("Spaghetti", "🍝")],
        "hard": [("Ingredients", "🧂"), ("Nutrition", "🥗"), ("Delicacy", "🍽️")]
    }
}

# --- 2. 輔助函數 ---
def play_audio(text, lang, speed=0.8):
    # 清理非目標語系文字
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

def get_stable_img(keyword):
    # 加上可愛與插畫標籤，避免嚇到小孩
    return f"https://loremflickr.com/800/600/{keyword},illustration,cute,cartoon/all"

# --- 3. 側邊欄設定 (年齡與語系) ---
with st.sidebar:
    st.header("⚙️ 教學參數設定")
    target_lang = st.radio("目標學習語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    
    # 判定難度等級
    if user_age <= 6: level = "easy"
    elif user_age <= 10: level = "medium"
    else: level = "hard"
    
    st.write(f"📊 目前難度：**Level {level.upper()}**")
    voice_speed = st.slider("調整語速", 0.5, 1.0, 0.8)

# --- 4. 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 專業發音", "🖼️ 單字類別", "📖 程度短文", "🎮 互動遊戲"])

# --- Tab 1: 專業發音練習 ---
with tab1:
    st.header("🔤 Phonics & IPA 專業發音練習")
    letter = st.selectbox("選擇練習字母", list("ABCDEFGHIJ"))
    phonics_info = {
        "A": {"word": "Apple", "ipa": "/æ/", "tip": "嘴巴張大，舌頭放平"},
        "B": {"word": "Bear", "ipa": "/b/", "tip": "雙唇緊閉，突然噴氣"},
        "C": {"word": "Cat", "ipa": "/k/", "tip": "舌根抬起，快速吐氣"}
    }
    info = phonics_info.get(letter, {"word": "Ant", "ipa": "/æ/", "tip": "基礎練習"})
    
    c1, c2 = st.columns(2)
    with c1:
        st.image(get_stable_img(info['word']), use_column_width=True)
    with c2:
        st.title(f"Letter: {letter}")
        st.markdown(f"### **IPA 音標：{info['ipa']}**")
        st.info(f"💡 發音秘訣：{info['tip']}")
        if st.button(f"🔊 播放專業發音 ({letter})"):
            play_audio(f"{letter}, {letter}, {info['word']}", target_lang)

# --- Tab 2: 類別化單字卡 ---
with tab2:
    st.header("🖼️ 分類閃視卡")
    category = st.selectbox("選擇主題類別", list(VOCAB_DB.keys()))
    words_to_show = VOCAB_DB[category][level]
    
    # 依難度調整顯示數量
    cols = st.columns(len(words_to_show))
    for i, (w, emoji) in enumerate(words_to_show):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'><b>{w}</b></p>", unsafe_allow_html=True)
            if st.button(f"🔊", key=f"v_{w}"):
                play_audio(w, target_lang)

# --- Tab 3: 程度短文 (依年齡生成) ---
with tab3:
    st.header(f"📖 {user_age}歲 專屬短文閱讀")
    story_topic = st.text_input("輸入短文主題：", "森林")
    
    # 依年齡調整句型難度
    if user_age <= 6:
        story = f"Look! A {story_topic}. It is big. I like the {story_topic}."
        trans = f"看！這是一個{story_topic}。它很大。我喜歡這個{story_topic}。"
    elif user_age <= 10:
        story = f"Today we went to the {story_topic}. The weather was beautiful. We saw many interesting things there."
        trans = f"今天我們去了{story_topic}。天氣很漂亮。我們在那裡看到了許多有趣的事情。"
    else:
        story = f"Exploring the {story_topic} provides a unique opportunity to understand nature. We should protect our environment for the future."
        trans = f"探索{story_topic}提供了一個了解自然的獨特機會。我們應該為了未來保護我們的環境。"

    st.image(get_stable_img(story_topic), width=500)
    st.markdown(f"**{story}**")
    st.caption(trans)
    if st.button("🔊 播放全文內容"):
        play_audio(story, target_lang)

# --- Tab 4: 互動遊戲 (語言隨動) ---
with tab4:
    st.header("🎮 語言互動挑戰")
    
    # 依語言切換指令
    game_instr = {
        "英文 (English)": {"title": "Listen & Click", "task": "Click on 4 stars!", "success": "Amazing! You got it!"},
        "日文 (日本語)": {"title": "きいて、クリックして", "task": "ほしを 4つ おしてね！", "success": "すごい！せいかいです！"}
    }
    curr_instr = game_instr[target_lang]
    
    game_html = f"""
    <div style="background:white; padding:20px; border-radius:20px; text-align:center; border:4px solid #87CEFA;">
        <h2>{curr_instr['title']}</h2>
        <p style="font-size:20px;">{curr_instr['task']}</p>
        <div style="font-size:60px;">
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
            <span onclick="check(this)" style="cursor:pointer">⭐</span>
        </div>
        <h2 id="msg" style="color:#4CAF50;"></h2>
    </div>
    <script>
        let count = 0;
        function check(el) {{
            if(el.style.opacity == '0.2') return;
            el.style.opacity = '0.2';
            count++;
            if(count == 4) document.getElementById('msg').innerText = "{curr_instr['success']}";
        }}
    </script>
    """
    components.html(game_html, height=400)
