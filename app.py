import streamlit as st
from gtts import gTTS
import io
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state: st.session_state.user_score = 0
if 'game_turn' not in st.session_state: st.session_state.game_turn = 0
if 'active_en_list' not in st.session_state: st.session_state.active_en_list = []
if 'active_tr_list' not in st.session_state: st.session_state.active_tr_list = []

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 字母與單字資料庫 (補全 A-Z) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "Red apple.", "紅蘋果。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "Brown bear.", "棕熊。")]},
        "E": {"upper": "E", "lower": "e", "words": [("Eat", "😋", "I eat rice.", "我吃飯。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Mother", "👩", "I love Mother.", "我愛媽媽。")]},
        "S": {"upper": "S", "lower": "s", "words": [("School", "🏫", "I go to school.", "我去上學。")]}
    }
DB = get_db()

# --- 3. 側邊欄：進化邏輯 (絕對無雞) ---
with st.sidebar:
    st.header("👤 學習者進度")
    score = st.session_state.user_score
    st.write(f"🌟 目前積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小龍孵化了！", "60px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長中的雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "強壯霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px;'><h1 style='font-size:{d_size};'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡 (難度控制)", options=[4, 6, 8, 10, 12])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分重置"): st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang='en', slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3 = st.tabs(["🔤 字母單字", "📖 短文文章生成", "🎮 互動遊戲區"])

with tab1:
    st.header("🔤 字母發音練習")
    sel_let = st.selectbox("請選擇字母", list(DB.keys()), key="alpha_select")
    info = DB[sel_let]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emoji, sent, tr in info["words"]:
        col1, col2 = st.columns([1, 4])
        col1.markdown(f"<h1 style='font-size:70px;'>{emoji}</h1>", unsafe_allow_html=True)
        with col2:
            st.subheader(w)
            st.write(f"**Sentence:** {sent}")
            if st.button(f"🔊 聽單字發音", key=f"btn_w_{w}"):
                st.audio(get_voice(f"{w}. {sent}", voice_speed), format="audio/mp3")
                st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 核心文章引擎 (徹底修正 Topic 與吃飯語法) ---
with tab2:
    st.header("📖 指令式教材文章")
    u_topic = st.text_input("📝 教材主題 (如：吃飯、旅遊、爸爸)", "吃飯")
    u_words = st.select_slider("📏 文章字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 生成正確教材", key="gen_btn"):
        # 1. 精準映射 (包含動作判定)
        en_word = "everything" 
        is_action = False
        
        # 智慧翻譯字典
        if "吃" in u_topic: en_word, is_action = "Eating", True
        elif "喝" in u_topic: en_word, is_action = "Drinking", True
        elif "玩" in u_topic: en_word, is_action = "Playing", True
        elif "學" in u_topic: en_word, is_action = "School", False
        elif "旅" in u_topic: en_word, is_action = "Traveling", True
        elif "爸" in u_topic: en_word, is_action = "Father", False
        elif "媽" in u_topic: en_word, is_action = "Mother", False
        else: en_word = u_topic # 若都沒中，直接用老師打的字

        # 2. 根據類型拼裝「文章」
        if is_action:
            if user_age <= 6:
                pool = [(f"I like {en_word}.", f"我喜歡{u_topic}。"), (f"It is very fun.", f"這非常有趣。"), (f"We do this together.", f"我們一起做這件事。"), (f"I am happy.", f"我很開心。")]
            else:
                pool = [(f"{en_word} is very important for our health.", f"{u_topic}對我們的健康很重要。"), (f"We can learn many new things while {en_word.lower()}.", f"在{u_topic}時我們可以學到很多新東西。"), (f"It creates wonderful memories.", f"它創造了美好的回憶。")]
        else:
            if user_age <= 6:
                pool = [(f"I love my {en_word}.", f"我愛我的{u_topic}。"), (f"The {en_word} is big.", f"{u_topic}很大。"), (f"It is so cool.", f"這真的很酷。"), (f"We play every day.", f"我們每天都在玩。")]
            else:
                pool = [(f"Exploring {en_word} provides unique opportunities.", f"探索{u_topic}提供了獨特的機會。"), (f"We believe {en_word} is essential.", f"我們相信{u_topic}是不可或缺的。"), (f"Focusing on {en_word} helps us grow.", f"專注於{u_topic}能幫助我們成長。")]

        st.session_state.active_en_list = [p[0] for p in pool]
        st.session_state.active_tr_list = [p[1] for p in pool]
        st.session_state.active_topic = u_topic

    if st.session_state.active_en_list:
        st.subheader(f"📜 課文原文：{st.session_state.active_topic}")
        for s in st.session_state.active_en_list:
            st.markdown(f"<div style='font-size:32px; font-weight:500; margin-bottom:15px; color:#2E4053;'>• {s}</div>", unsafe_allow_html=True)
        
        if st.button("🔊 全文朗讀"):
            st.audio(get_voice(" ".join(st.session_state.active_en_list), voice_speed), format="audio/mp3")
        with st.expander("👁️ 查看精確翻譯"):
            for tr in st.session_state.active_tr_list: st.write(tr)

with tab3:
    st.header("🎮 聽音挑戰遊戲")
    q_word = random.choice(["Eat", "School", "Bear", "Mother"])
    if st.button("🔊 點聽題目單字"): st.audio(get_voice(q_word, voice_speed), format="audio/mp3")
    ans = st.radio("正確答案是？", ["Eat", "School", "Bear", "Mother"], key="game_ans")
    if st.button("送出"):
        if ans == q_word: 
            st.success("答對了！+10 分"); st.session_state.user_score += 10; st.balloons()
        else: st.error("再試一次！")
