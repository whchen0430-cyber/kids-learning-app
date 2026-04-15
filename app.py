import streamlit as st
from gtts import gTTS
import os
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. 深度整合資料庫 (A-E 擴充) ---
INTEGRATED_DB = {
    "A": [("Apple", "🍎", "I like the red apple.", "我喜歡紅蘋果。"), ("Ant", "🐜", "An ant is small.", "螞蟻很小。"), ("Alligator", "🐊", "Big alligator.", "大鱷魚。"), ("Astronaut", "👨‍🚀", "Sky hero.", "太空英雄。"), ("Airplane", "✈️", "Fly high.", "飛很高。")],
    "B": [("Bear", "🧸", "Brown bear.", "棕熊。"), ("Ball", "⚽", "Play ball.", "玩球。"), ("Banana", "🍌", "Yellow banana.", "黃香蕉。"), ("Bird", "🐦", "Singing bird.", "唱歌的鳥。"), ("Bee", "🐝", "Busy bee.", "忙碌的蜜蜂。")],
    "C": [("Cat", "🐱", "Soft cat.", "軟軟的貓。"), ("Cake", "🎂", "Sweet cake.", "甜蛋糕。"), ("Car", "🚗", "Fast car.", "快車。"), ("Cup", "🥛", "Milk cup.", "牛奶杯。"), ("Candy", "🍬", "Yummy candy.", "好吃的糖果。")],
    "D": [("Dog", "🐶", "Good dog.", "好狗狗。"), ("Duck", "🦆", "Yellow duck.", "小黃鴨。"), ("Dolphin", "🐬", "Blue dolphin.", "藍海豚。"), ("Drum", "🥁", "Loud drum.", "響亮的鼓。"), ("Door", "🚪", "Open door.", "開門。")],
    "E": [("Elephant", "🐘", "Big elephant.", "大象很大。"), ("Egg", "🥚", "White egg.", "白色的蛋。"), ("Eye", "👁️", "I see you.", "我看見你。"), ("Eagle", "🦅", "Strong eagle.", "強壯的老鷹。"), ("Ear", "👂", "I hear you.", "我聽見你。")]
}

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("👤 學生狀態")
    score = st.session_state.user_score
    d_emo = "🥚" if score < 50 else ("🦖" if score < 150 else "🦕")
    st.markdown(f"<h1 style='text-align:center; font-size:80px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.write(f"🌟 積分：{score}")
    st.divider()
    st.header("⚙️ 教學設定")
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)

def play_audio(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 4. 功能分頁 (確保四個都在) ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 字母單字練習", "📖 短文指令區", "🎮 互動遊戲區", "🏆 進度紀錄"])

# --- Tab 1: 整合練習 ---
with tab1:
    st.header("🔤 字母與單字同步學")
    letter = st.selectbox("請選擇字母", list(INTEGRATED_DB.keys()))
    for word, emoji, sentence, trans in INTEGRATED_DB[letter]:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"<h1 style='text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
        col2.write(f"**{word}**: {sentence} ({trans})")
        if col2.button(f"🔊 聽發音", key=f"btn_{word}"):
            play_audio(f"{word}. {sentence}", target_lang, voice_speed)
            st.session_state.user_score += 1
            st.rerun()

# --- Tab 3: 互動遊戲區 (核心修復：確保跑出來) ---
with tab3:
    st.header("🎮 聽音辨圖挑戰")
    
    # 建立題目池：從目前選定的字母資料中抽題
    game_pool = INTEGRATED_DB[letter]
    
    # 初始化遊戲狀態
    if 'current_options' not in st.session_state or st.button("🔄 換一題"):
        st.session_state.current_options = random.sample(game_pool, 3)
        st.session_state.current_target = random.choice(st.session_state.current_options)

    target = st.session_state.current_target
    
    st.subheader("🎯 聽聽看，老師在說哪一個單字？")
    if st.button("🔊 播放題目音檔"):
        play_audio(target[0], target_lang, voice_speed)
    
    # 顯示選項圖片
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(st.session_state.current_options):
        with cols[i]:
            if st.button(f"{emoji}", key=f"game_opt_{i}", use_container_width=True):
                if word == target[0]:
                    st.balloons()
                    st.success(f"太棒了！答對了！這是 {word}")
                    st.session_state.user_score += 20
                    # 答對後自動重置題目
                    st.session_state.pop('current_options')
                    st.rerun()
                else:
                    st.error("不對喔，再聽一次！")
