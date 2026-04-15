import streamlit as st
from gtts import gTTS
import os
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. 強化版單字資料庫 (含例句與翻譯) ---
# 格式: (單字, Emoji, 例句, 翻譯)
VOCAB_DB = {
    "🦁 動物 (Animals)": {
        4: [("Dog", "🐶", "The dog is happy.", "這隻狗很開心。"), 
            ("Cat", "🐱", "I see a small cat.", "我看見一隻小貓。")],
        8: [("Lion", "🦁", "The lion is the king of the forest.", "獅子是森林之王。"), 
            ("Zebra", "🦓", "A zebra has black and white stripes.", "斑馬有黑白相間的條紋。")],
        12: [("Dolphin", "🐬", "Dolphins are very intelligent sea animals.", "海豚是非常聰明的海洋動物。"), 
             ("Chameleon", "🦎", "A chameleon can change its color.", "變色龍會改變顏色。")]
    },
    "🍎 食物 (Food)": {
        4: [("Apple", "🍎", "I like the red apple.", "我喜歡這顆紅蘋果。")],
        8: [("Pizza", "🍕", "We share a big pizza for dinner.", "我們晚餐分享一個大披薩。")],
        12: [("Nutrition", "🥗", "Vegetables provide good nutrition for us.", "蔬菜為我們提供良好的營養。")]
    }
}

# --- 3. 側邊欄與進化邏輯 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    if score < 50: d_emo, d_name = "🥚", "恐龍蛋"
    elif score < 150: d_emo, d_name = "🦖", "小恐龍"
    else: d_emo, d_name = "🦕", "巨龍"
    
    st.markdown(f"<h1 style='text-align:center; font-size:80px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.subheader(f"等級：{d_name} (積分: {score})")
    st.divider()
    target_lang = st.radio("學習語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    age_tag = 4 if user_age <= 6 else (8 if user_age <= 10 else 12)

# --- 4. 輔助函數 ---
def play_audio(text, lang):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=True)
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 5. 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 專業發音", "🖼️ 單字與例句", "📖 短文解析", "🎮 互動遊戲"])

# --- Tab 2: 單字教材 (含例句翻譯) ---
with tab2:
    st.header("🖼️ 類別單字與例句練習")
    cat = st.selectbox("選擇主題：", list(VOCAB_DB.keys()))
    words = VOCAB_DB[cat][age_tag]
    
    for word, emoji, sentence, trans in words:
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"<h1 style='font-size:80px;'>{emoji}</h1>", unsafe_allow_html=True)
            with c2:
                st.subheader(word)
                st.markdown(f"**例句：** {sentence}")
                st.caption(f"翻譯：{trans}")
                if st.button(f"🔊 聽發音 (+1分)", key=f"btn_{word}"):
                    play_audio(f"{word}. {sentence}", target_lang)
                    st.session_state.user_score += 1
                    st.rerun()
            st.divider()

# --- Tab 3: 短文解析 (單字+文法) ---
with tab3:
    st.header(f"📖 {user_age}歲 專業短文解析")
    
    # 根據年齡生成不同深度的內容
    if user_age <= 6:
        content = "The sun is hot. It is yellow and bright."
        vocab_list = [("Sun", "太陽"), ("Hot", "熱的")]
        grammar = "主詞 (The sun) + Be動詞 (is) + 形容詞 (hot)。用來描述東西的狀態。"
    elif user_age <= 10:
        content = "The sun provides energy to all living things on Earth."
        vocab_list = [("Provide", "提供"), ("Energy", "能量")]
        grammar = "現在簡單式：主詞是單數 (The sun)，動詞要加 's' (provides)。"
    else:
        content = "The sun's gravity keeps the entire solar system in orbit."
        vocab_list = [("Gravity", "重力"), ("Orbit", "軌道")]
        grammar = "所有格代名詞：Sun's 代表「太陽的」。 keeps... in orbit 表示「使...保持在軌道上」。"

    st.info(content)
    if st.button("🔊 全文朗讀"):
        play_audio(content, target_lang)

    col_v, col_g = st.columns(2)
    with col_v:
        st.subheader("📝 重點單字 (Vocabulary)")
        for v, t in vocab_list:
            st.write(f"• **{v}**: {t}")
            
    with col_g:
        st.subheader("💡 文法點撥 (Grammar)")
        st.success(grammar)
    
    with st.expander("👁️ 查看全文翻譯"):
        st.write("這是根據內容生成的翻譯...")

# --- Tab 4: 遊戲區 (略) ---
with tab4:
    st.write("遊戲與積分領取區")
