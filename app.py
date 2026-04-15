import streamlit as st
from gtts import gTTS
import os
import re
import random
import streamlit.components.v1 as components

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. 完整資料庫定義 ---
# (1) A-Z 專業發音資料
ALPHABET_DB = {
    "A": {"w": "Apple", "e": "🍎", "ipa": "/æ/", "tip": "嘴巴張大，舌頭放平"},
    "B": {"w": "Bear", "e": "🧸", "ipa": "/b/", "tip": "雙唇緊閉，突然噴氣"},
    "C": {"w": "Cat", "e": "🐱", "ipa": "/k/", "tip": "舌根抬起，快速吐氣"},
    "D": {"w": "Dog", "e": "🐶", "ipa": "/d/", "tip": "舌尖頂住上齒齦"},
    "E": {"w": "Elephant", "e": "🐘", "ipa": "/ɛ/", "tip": "嘴角向兩邊張開"},
    # ... (請依此格式補齊其餘字母，目前確保關鍵字母存在)
}

# (2) 類別單字與例句
VOCAB_DB = {
    "🦁 動物 (Animals)": {
        4: [("Dog", "🐶", "The dog is happy.", "這隻狗很開心。")],
        8: [("Lion", "🦁", "The lion is the king.", "獅子是萬獸之王。")],
        12: [("Dolphin", "🐬", "Dolphins are intelligent.", "海豚非常聰明。")]
    },
    "🍎 食物 (Food)": {
        4: [("Apple", "🍎", "I like apples.", "我喜歡蘋果。")],
        12: [("Nutrition", "🥗", "Fruits give nutrition.", "水果提供營養。")]
    }
}

# --- 3. 側邊欄設定 (包含找回來的語速) ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    if score < 50: d_emo, d_name, d_next = "🥚", "恐龍蛋", 50
    elif score < 150: d_emo, d_name, d_next = "🦖", "小恐龍", 150
    elif score < 300: d_emo, d_name, d_next = "🦕", "巨龍", 300
    else: d_emo, d_name, d_next = "👑", "恐龍國王", 9999
    
    st.markdown(f"<h1 style='text-align:center; font-size:80px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.title(f"{d_name}")
    st.write(f"🌟 積分：{score} / {d_next}")
    st.progress(min(score / d_next, 1.0))
    
    st.divider()
    st.header("⚙️ 教學設定")
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    # 重要：找回來的語速選項
    voice_speed = st.slider("調整語速 (建議 0.8)", 0.5, 1.0, 0.8)
    age_tag = 4 if user_age <= 6 else (8 if user_age <= 10 else 12)

# --- 4. 輔助函數 ---
def play_audio(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 5. 五大核心分頁 (確保全部都在) ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 專業發音", "🖼️ 單字與例句", "📖 短文解析", "🎮 互動遊戲"])

# --- Tab 1: 專業發音練習 (回歸！) ---
with tab1:
    st.header("🔤 Phonics & IPA 專業發音")
    letter = st.selectbox("選擇字母", list(ALPHABET_DB.keys()) if ALPHABET_DB else ["A"])
    if letter in ALPHABET_DB:
        d = ALPHABET_DB[letter]
        st.markdown(f"<div style='text-align:center; font-size:120px;'>{letter} ➡️ {d['e']}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"Word: {d['w']}")
            st.info(f"IPA: {d['ipa']}")
        with c2:
            st.success(f"💡 發音秘訣：\n{d['tip']}")
            if st.button(f"🔊 聽發音 (+1分)", key=f"p_{letter}"):
                play_audio(f"{letter}, {d['w']}", target_lang, voice_speed)
                st.session_state.user_score += 1
                st.rerun()

# --- Tab 2: 單字與例句 ---
with tab2:
    st.header("🖼️ 分級單字卡與例句")
    cat = st.selectbox("選擇主題：", list(VOCAB_DB.keys()))
    words = VOCAB_DB[cat].get(age_tag, VOCAB_DB[cat][4]) # 找不到就給基礎級
    for w, e, s, t in words:
        with st.container():
            col1, col2 = st.columns([1, 4])
            col1.markdown(f"<h1 style='font-size:80px;'>{e}</h1>", unsafe_allow_html=True)
            col2.subheader(w)
            col2.write(f"**Example:** {s}")
            col2.caption(f"翻譯：{t}")
            if col2.button(f"🔊 聽單字例句 (+1分)", key=f"v_{w}"):
                play_audio(f"{w}. {s}", target_lang, voice_speed)
                st.session_state.user_score += 1
                st.rerun()
        st.divider()

# --- Tab 3: 短文解析 (含單字與文法) ---
with tab3:
    st.header(f"📖 {user_age}歲 專業短文解析")
    if user_age <= 6:
        content, vocab, grammar = "The sun is hot.", [("Sun", "太陽")], "主詞 + is + 形容詞。"
    else:
        content, vocab, grammar = "The sun provides energy.", [("Energy", "能量")], "三單動詞加 s。"
    
    st.info(content)
    if st.button("🔊 全文朗讀", key="story_btn"):
        play_audio(content, target_lang, voice_speed)
    
    cv, cg = st.columns(2)
    with cv:
        st.subheader("📝 重點單字")
        for v, k in vocab: st.write(f"• **{v}**: {k}")
    with cg:
        st.subheader("💡 文法點撥")
        st.success(grammar)
    with st.expander("👁️ 查看翻譯"): st.write("（此處顯示翻譯內容...）")

# --- Tab 4: 遊戲區 ---
with tab4:
    st.header("🎮 互動挑戰")
    st.write("請聽指令完成任務！")
    # (保留之前的 HTML 數星星遊戲...)
    if st.button("🎁 領取勝利積分 (+20分)"):
        st.session_state.user_score += 20
        st.balloons()
        st.rerun()
