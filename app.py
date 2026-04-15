import streamlit as st
from gtts import gTTS
import os
import re
import random
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="專業分級語文機器人", page_icon="🎨", layout="wide")

# --- 1. 核心教材資料庫 (類別化 + 年齡難度) ---
VOCAB_CATEGORY = {
    "🦁 動物 (Animals)": {
        4: [("Dog", "🐶"), ("Cat", "🐱"), ("Bird", "🐦")],
        8: [("Lion", "🦁"), ("Zebra", "🦓"), ("Elephant", "🐘"), ("Monkey", "🐒")],
        12: [("Chameleon", "🦎"), ("Platypus", "🦆"), ("Kangaroo", "🦘"), ("Dolphin", "🐬")]
    },
    "🍎 食物 (Food)": {
        4: [("Apple", "🍎"), ("Milk", "🥛")],
        8: [("Pizza", "🍕"), ("Burger", "🍔"), ("Cookie", "🍪"), ("Juice", "🧃")],
        12: [("Ingredients", "🧂"), ("Nutrition", "🥗"), ("Spaghetti", "🍝"), ("Breakfast", "🍳")]
    }
}

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 智慧教學設定")
    target_lang = st.radio("目標學習語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡區間", options=[4, 6, 8, 10, 12])
    age_tag = 4 if user_age <= 6 else (8 if user_age <= 10 else 12)
    voice_speed = st.slider("調整語速", 0.5, 1.0, 0.8)
    st.success(f"📌 目前等級：{user_age}歲階段")

# --- 3. 通用語音函數 ---
def play_audio(text, lang):
    clean_text = re.sub(r'[\u4e00-\u9fa5]', '', text).replace("A:", "").replace("B:", "")
    lang_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean_text, lang=lang_code, slow=True)
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

# --- 4. 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 發音練習", "🖼️ 單字類別", "📖 原文短文", "🎮 互動挑戰"])

# --- Tab 1 & 2: 略 (保留之前優化過的 A-Z 發音與單字區) ---
with tab1: st.write("A-Z 專業發音練習區")
with tab2: st.write("類別化單字教材區")

# --- Tab 3: 原文短文 (與遊戲連動) ---
with tab3:
    st.header("📖 原文閱讀專區")
    story_topic = st.selectbox("選擇閱讀主題：", ["公園 (Park)", "農場 (Farm)", "海洋 (Ocean)"])
    
    # 依年齡產生成程度文章
    if user_age <= 6:
        content = f"Look! This is a {story_topic}. It is so big. I can see a blue bird here."
        q_text = "What color is the bird?"
        options = ["Blue", "Red", "Green"]
        correct_ans = "Blue"
    else:
        content = f"The {story_topic} is a beautiful place. People come here to relax. We must keep the {story_topic} clean to protect nature."
        q_text = "Why do people come to this place?"
        options = ["To work", "To relax", "To sleep"]
        correct_ans = "To relax"

    st.info(content)
    with st.expander("👁️ 查看中文翻譯"):
        st.write("這是翻譯內容...") # 建議實作完整翻譯
    
    if st.button("🔊 播放全文"):
        play_audio(content, target_lang)

    # 將資料存入 session_state 供遊戲區使用
    st.session_state['last_story_q'] = {"q": q_text, "options": options, "ans": correct_ans}

# --- Tab 4: 智慧遊戲區 (自動更新) ---
with tab4:
    st.header("🎮 智慧互動挑戰")
    game_mode = st.selectbox("選擇遊戲模式：", ["閱讀理解測驗", "圖片與單字配對"])

    if game_mode == "閱讀理解測驗":
        if 'last_story_q' in st.session_state:
            q_data = st.session_state['last_story_q']
            st.subheader(f"❓ {q_data['q']}")
            user_choice = st.radio("請選擇正確答案：", q_data['options'], index=None)
            
            if user_choice:
                if user_choice == q_data['ans']:
                    st.balloons()
                    st.success("🎉 Correct! You are a great reader!")
                else:
                    st.error("❌ Try again! You can do it!")
        else:
            st.warning("請先到『原文短文』標籤閱讀文章後，再來參加測驗喔！")

    elif game_mode == "圖片與單字配對":
        st.subheader("🔊 Listen and Pick the right one!")
        
        # 自動抓取目前年齡層的單字作為題目
        cat = random.choice(list(VOCAB_CATEGORY.keys()))
        options_list = random.sample(VOCAB_CATEGORY[cat][age_tag], 3)
        target = random.choice(options_list)
        
        col1, col2, col3 = st.columns(3)
        for i, (word, emoji) in enumerate(options_list):
            with [col1, col2, col3][i]:
                if st.button(f"{emoji}", key=f"game_btn_{i}", use_container_width=True):
                    if word == target[0]:
                        st.balloons()
                        st.success(f"✅ Yes! That is a {word}!")
                    else:
                        st.error("❌ Not quite! Try again!")
        
        st.markdown(f"### 💡 指令：找出 **{target[0]}**")
        if st.button("🔊 聽發音"):
            play_audio(target[0], target_lang)
