import streamlit as st
from gtts import gTTS
import io
import re
import random
import time

# --- 1. 頁面配置 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0
if 'game_turn' not in st.session_state:
    st.session_state.game_turn = 0
if 'active_en' not in st.session_state:
    st.session_state.active_en = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 側邊欄：進化邏輯 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 進化圖案校正
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍孵化了！", "55px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長期雷龍", "95px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "壯年霸王龍", "135px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "165px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 3. 輔助函數 ---
def get_voice(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 4. 分頁 ---
tab1, tab2, tab3 = st.tabs(["🔤 單字練習", "📖 敘事短文生成", "🎮 互動挑戰"])

with tab1:
    st.header("🔤 單字練習")
    st.write("單字資料庫保持穩定運作中，點擊單字可增加積分。")

# --- Tab 2: 敘事文章生成引擎 (核心修正) ---
with tab2:
    st.header("📖 邏輯敘事教材生成")
    u_topic = st.text_input("📝 請輸入短文主題 (如：我的狗狗、有趣的旅遊)", "我的狗狗")
    u_words = st.select_slider("📏 選擇文章長度 (字數)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成連貫短文", key="gen_btn"):
        # 內建翻譯映射
        map_db = {"狗": "Dogs", "貓": "Cats", "旅遊": "Travel", "煮飯": "Cooking", "學校": "School"}
        en_kw = map_db.get(u_topic, u_topic) if not re.match(r'^[A-Za-z ]+$', u_topic) else u_topic

        # 年齡層敘事模板
        if user_age <= 6:
            en_story = f"I love {en_kw}. It is a happy day to see {en_kw}. {en_kw} is very big and cool. We can play together now."
            tr_story = f"我愛{u_topic}。看到{u_topic}是很開心的一天。{u_topic}又大又酷，我們現在可以一起玩了。"
        elif user_age <= 10:
            en_story = f"Today, I want to share something about {en_kw}. I think {en_kw} is very interesting because it brings me joy. We can learn many things while exploring {en_kw} with my best friends."
            tr_story = f"今天，我想分享關於{u_topic}的事情。我覺得{u_topic}很有趣，因為它帶給我快樂。當我和好朋友一起探索{u_topic}時，我們可以學到很多東西。"
        else: # 12歲
            en_story = f"The unique experience of {en_kw} provides us with an incredible opportunity to understand the beauty of life. Moreover, focusing on {en_kw} helps us create unforgettable memories that will stay with us forever."
            tr_story = f"{u_topic}的獨特體驗為我們提供了了解生命之美的絕佳機會。此外，關注{u_topic}能幫助我們創造伴隨終生的難忘回憶。"

        # 根據字數截斷 (大約值)
        en_final = " ".join(en_story.split()[:u_words])
        if not en_final.endswith('.'): en_final += "."
        
        st.session_state.active_en = en_final
        st.session_state.active_tr = tr_story

    if st.session_state.active_en:
        st.subheader("📜 課文原文 (一句一行)")
        # 分句顯示邏輯
        sentences = st.session_state.active_en.split('. ')
        for s in sentences:
            if s.strip():
                clean_s = s.strip() if s.strip().endswith('.') else s.strip() + '.'
                st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {clean_s}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文音軌"):
            st.audio(get_voice(st.session_state.active_en, "en", voice_speed), format="audio/mp3")
        
        with st.expander("👁️ 查看精確翻譯"):
            st.markdown(f"<div style='font-size:18px; line-height:1.6;'>{st.session_state.active_tr}</div>", unsafe_allow_html=True)

with tab3:
    st.header("🎮 互動挑戰")
    st.write("遊戲區域正在等待積分挑戰...")
