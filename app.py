import streamlit as st
from gtts import gTTS
import os
import re

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. 深度整合資料庫 (字母 -> 5個單字/例句/翻譯) ---
# 老師您好，這裡我先幫您補完 A-E 的豐富內容，其餘字母可依樣畫葫蘆
INTEGRATED_DB = {
    "A": [
        ("Apple", "🍎", "I like the red apple.", "我喜歡這顆紅蘋果。"),
        ("Ant", "🐜", "An ant is very small.", "螞蟻非常小。"),
        ("Alligator", "🐊", "The alligator is in the water.", "短吻鱷在水裡。"),
        ("Astronaut", "👨‍🚀", "The astronaut flies to the moon.", "太空人飛向月球。"),
        ("Airplane", "✈️", "The airplane is in the sky.", "飛機在天空中。")
    ],
    "B": [
        ("Bear", "🧸", "The bear is brown.", "這隻熊是咖啡色的。"),
        ("Ball", "⚽", "I play with a ball.", "我玩球。"),
        ("Banana", "🍌", "The banana is yellow.", "香蕉是黃色的。"),
        ("Bird", "🐦", "The bird can fly.", "鳥會飛。"),
        ("Bee", "🐝", "The bee makes honey.", "蜜蜂會造蜂蜜。")
    ],
    "C": [
        ("Cat", "🐱", "The cat is sleeping.", "貓正在睡覺。"),
        ("Cake", "🎂", "I love chocolate cake.", "我愛巧克力蛋糕。"),
        ("Car", "🚗", "The car is very fast.", "這輛車很快。"),
        ("Cup", "🥛", "A cup of milk.", "一杯牛奶。"),
        ("Candy", "🍬", "The candy is sweet.", "糖果很甜。")
    ],
    "D": [
        ("Dog", "🐶", "The dog is my friend.", "狗是我的朋友。"),
        ("Duck", "🦆", "The duck goes quack.", "鴨子呱呱叫。"),
        ("Dolphin", "🐬", "Dolphin is a smart animal.", "海豚是很聰明的動物。"),
        ("Drum", "🥁", "He plays the drum.", "他在打鼓。"),
        ("Door", "🚪", "Please open the door.", "請開門。")
    ],
    "E": [
        ("Elephant", "🐘", "The elephant is big.", "大象很大。"),
        ("Egg", "🥚", "I eat an egg.", "我吃一顆蛋。"),
        ("Eye", "👁️", "I have two eyes.", "我有兩隻眼睛。"),
        ("Eagle", "🦅", "The eagle flies high.", "老鷹飛得很高。"),
        ("Ear", "👂", "I listen with my ears.", "我用耳朵聽。")
    ]
}

# --- 3. 側邊欄：恐龍狀態與語速設定 ---
with st.sidebar:
    st.header("👤 學生狀態")
    score = st.session_state.user_score
    d_emo = "🥚" if score < 50 else ("🦖" if score < 150 else "🦕")
    st.markdown(f"<h1 style='text-align:center; font-size:80px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.write(f"🌟 積分：{score}")
    st.divider()
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)

# --- 4. 輔助函數 ---
def play_audio(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 5. 分頁區 (整合後變精簡有力) ---
tab1, tab2, tab3 = st.tabs(["🔤 字母與單字整合練習", "📖 短文自定義區", "🎮 互動遊戲"])

# --- Tab 1: 字母單字一體化 (核心修正！) ---
with tab1:
    st.header("🔤 字母與單字同步學")
    letter = st.selectbox("請選擇您要教的字母：", list(INTEGRATED_DB.keys()))
    
    st.markdown(f"### 當前進度：字母 **{letter}**")
    
    # 單字卡排列
    for word, emoji, sentence, trans in INTEGRATED_DB[letter]:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<h1 style='text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
            with col2:
                st.subheader(f"{word}")
                st.write(f"**例句:** {sentence}")
                st.caption(f"翻譯: {trans}")
                if st.button(f"🔊 聽 {word} 與例句", key=f"btn_{word}"):
                    play_audio(f"{word}. {sentence}", target_lang, voice_speed)
                    st.session_state.user_score += 1
                    st.rerun()
            st.divider()

# --- Tab 2: 短文指令區 ---
with tab2:
    st.header("📖 教學短文產生器")
    user_topic = st.text_input("輸入主題 (例如：Beach)", "Forest")
    if st.button("🚀 生成解析內容"):
        st.session_state['story'] = f"The {user_topic} is beautiful."
    if 'story' in st.session_state:
        st.info(st.session_state['story'])

# --- Tab 3: 互動遊戲 ---
with tab3:
    st.header("🎮 聽音辨圖遊戲")
    st.write("點擊按鈕獲取積分，讓恐龍長大！")
    if st.button("🎁 領取練習積分 (+10)"):
        st.session_state.user_score += 10
        st.balloons()
        st.rerun()
