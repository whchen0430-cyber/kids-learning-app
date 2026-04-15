import streamlit as st
from gtts import gTTS
import os
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. 大規模分級資料庫 ---
VOCAB_DB = {
    "🦁 動物 (Animals)": {
        4: [("Dog", "🐶", "The dog is happy.", "這隻狗很開心。"), ("Cat", "🐱", "The cat is small.", "這隻貓很小。")],
        8: [("Lion", "🦁", "The lion is the king.", "獅子是萬獸之王。"), ("Zebra", "🦓", "Zebras have stripes.", "斑馬有條紋。")],
        12: [("Dolphin", "🐬", "Dolphins are smart.", "海豚很聰明。"), ("Kangaroo", "🦘", "Kangaroos can jump.", "袋鼠會跳。")]
    },
    "🍎 食物 (Food)": {
        4: [("Apple", "🍎", "I eat an apple.", "我吃一顆蘋果。"), ("Milk", "🥛", "I drink milk.", "我喝牛奶。")],
        8: [("Pizza", "🍕", "I like cheese pizza.", "我喜歡起司披薩。"), ("Cookie", "🍪", "The cookie is sweet.", "餅乾很甜。")],
        12: [("Nutrition", "🥗", "Salad is full of nutrition.", "沙拉充滿營養。"), ("Ingredients", "🧂", "Check the ingredients.", "檢查成分。")]
    },
    "🚗 交通 (Transport)": {
        4: [("Car", "🚗", "A blue car.", "一輛藍色的車。"), ("Bus", "🚌", "The school bus.", "校車。")],
        12: [("Submarine", "🚢", "A yellow submarine.", "黃色潛水艇。"), ("Helicopter", "🚁", "The helicopter is loud.", "直升機很吵。")]
    }
}

# --- 3. 側邊欄：進化狀態與語速 ---
with st.sidebar:
    st.header("👤 學生狀態")
    score = st.session_state.user_score
    if score < 50: d_emo, d_name, d_next = "🥚", "恐龍蛋", 50
    elif score < 150: d_emo, d_name, d_next = "🦖", "小恐龍", 150
    elif score < 300: d_emo, d_name, d_next = "🦕", "巨龍", 300
    else: d_emo, d_name, d_next = "👑", "恐龍國王", 9999
    
    st.markdown(f"<h1 style='text-align:center; font-size:80px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.title(f"等級：{d_name}")
    st.write(f"🌟 積分：{score} / {d_next}")
    st.progress(min(score / d_next, 1.0))
    
    st.divider()
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    age_tag = 4 if user_age <= 6 else (8 if user_age <= 10 else 12)

# --- 4. 輔助函數 ---
def play_audio(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 5. 功能分頁 ---
t1, t2, t3, t4 = st.tabs(["🔤 專業發音", "🖼️ 單字與例句", "📖 短文指令區", "🎮 互動遊戲區"])

with t1:
    st.header("🔤 基礎發音練習")
    st.write("請選擇字母進行 IPA 發音練習。")
    # 此處可放入之前的 A-Z DB 邏輯

with t2:
    st.header("🖼️ 分級單字庫")
    cat = st.selectbox("選擇主題：", list(VOCAB_DB.keys()))
    words = VOCAB_DB[cat].get(age_tag, VOCAB_DB[cat][4])
    for w, e, s, t in words:
        with st.expander(f"{e} {w}", expanded=True):
            col1, col2 = st.columns([1, 4])
            col1.markdown(f"<h1>{e}</h1>", unsafe_allow_html=True)
            col2.write(f"**例句:** {s}")
            col2.caption(f"翻譯: {t}")
            if col2.button(f"🔊 聽發音", key=f"v_{w}"):
                play_audio(f"{w}. {s}", target_lang, voice_speed)
                st.session_state.user_score += 1
                st.rerun()

with t3:
    st.header("📖 自定義短文解析")
    user_topic = st.text_input("📝 短文主題", "My Pet")
    user_inst = st.text_area("✍️ 給老師的指令", "請用簡單的英文描述。")
    if st.button("🚀 生成內容"):
        st.session_state['story'] = f"I have a pet. It is a {user_topic}. I love it very much."
    
    if 'story' in st.session_state:
        st.info(st.session_state['story'])
        st.subheader("💡 文法點撥")
        st.success(f"針對 {user_age} 歲的基礎句型說明...")

# --- Tab 4: 互動遊戲區 (重新寫好跑出來了！) ---
with t4:
    st.header("🎮 聽力與圖片配對遊戲")
    st.write("聽聽老師說什麼，然後選出正確的圖片！")

    # 從單字庫隨機抽三個當選項
    all_words = []
    for c in VOCAB_DB:
        for age in VOCAB_DB[c]:
            all_words.extend(VOCAB_DB[c][age])
    
    # 隨機產生題目
    if 'game_options' not in st.session_state or st.button("🔄 換一題"):
        st.session_state.game_options = random.sample(all_words, 3)
        st.session_state.target_item = random.choice(st.session_state.game_options)

    opts = st.session_state.game_options
    target = st.session_state.target_item

    st.markdown(f"### 🎯 請找出： **????** (請點擊下方喇叭聽題目)")
    if st.button("🔊 聽題目音檔"):
        play_audio(target[0], target_lang, voice_speed)

    cols = st.columns(3)
    for i, (word, emo, sent, tran) in enumerate(opts):
        with cols[i]:
            if st.button(f"{emo}", key=f"game_btn_{i}", use_container_width=True):
                if word == target[0]:
                    st.balloons()
                    st.success(f"太棒了！這是 {word}！ 積分 +20")
                    st.session_state.user_score += 20
                    # 延遲一點點後自動換題
                else:
                    st.error("不對喔，再試試看！")

    st.divider()
    st.write(f"目前的進化狀態：{d_name} {d_emo}")
