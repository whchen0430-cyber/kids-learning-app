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
if 'active_tr' not in st.session_state:
    st.session_state.active_tr = ""

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. 資料庫 (鎖定結構) ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "The apple is red.", "蘋果是紅的。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good dog.", "好狗狗。"), ("Duck", "🦆", "Duck swims.", "鴨子游泳。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "強壯老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。")]}
    }
DB = get_db()

# --- 3. 側邊欄：進化邏輯 (絕對無雞) ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "小恐龍剛破殼！", "55px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "活潑成長中", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "壯碩霸王龍", "135px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "165px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡 (難度鎖定)", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0; st.rerun()

# --- 4. 輔助函數 ---
def get_voice(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    tts = gTTS(text=clean, lang=('en' if "英" in lang else 'ja'), slow=(speed < 1.0))
    fp = io.BytesIO(); tts.write_to_fp(fp); return fp.getvalue()

# --- 5. 分頁架構 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 單字練習", "📖 智慧教材生成", "🎮 互動挑戰", "🏆 成長紀錄"])

with tab1:
    st.header("🔤 單字發音練習")
    letter = st.selectbox("選擇字母", list(DB.keys()))
    info = DB[letter]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emo, sent, tr in info["words"]:
        st.write(f"### {emo} {w}")
        if st.button(f"🔊 播放單字發音", key=f"btn_{w}"):
            st.audio(get_voice(f"{w}. {sent}", target_lang, voice_speed), format="audio/mp3")
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 教材生成引擎 (修復翻譯問題) ---
with tab2:
    st.header("📖 智慧教材生成引擎")
    u_topic_cn = st.text_input("📝 請輸入主題 (例如：狗、煮飯、旅遊)", "狗")
    u_words = st.select_slider("📏 設定字數上限 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    # 內建映射庫
    topic_map = {
        "狗": ("Dogs", "狗"), "貓": ("Cats", "貓"), "旅遊": ("Traveling", "旅遊"),
        "煮飯": ("Cooking", "煮飯"), "太空": ("Space", "太空"), "森林": ("Forest", "森林"),
        "海洋": ("The Ocean", "海洋"), "恐龍": ("Dinosaurs", "恐龍")
    }
    
    if st.button("🚀 生成精準翻譯教材", key="gen_btn"):
        en_kw, cn_kw = topic_map.get(u_topic_cn, (u_topic_cn, u_topic_cn))
        
        # 根據年齡與語意同步生成英中對照庫
        if user_age <= 4:
            pool = [
                (f"I like {en_kw}.", f"我喜歡{cn_kw}。"),
                (f"See the {en_kw}.", f"看這個{cn_kw}。"),
                (f"It is very cool.", f"它非常酷。"),
                (f"Happy {en_kw} day.", f"快樂的{cn_kw}日。")
            ]
        elif user_age <= 8:
            pool = [
                (f"Today we learn about {en_kw}.", f"今天我們學習關於{cn_kw}的內容。"),
                (f"The {en_kw} is very big and cool.", f"這個{cn_kw}非常大而且很酷。"),
                (f"We can play with {en_kw} now.", f"我們現在可以玩{cn_kw}。"),
                (f"I am happy to see {en_kw}.", f"我很高興看到{cn_kw}。")
            ]
        else: # 12歲
            pool = [
                (f"Exploring {en_kw} provides us with unique opportunities.", f"探索{cn_kw}為我們提供了獨特的機會。"),
                (f"We believe that {en_kw} is an essential part of life.", f"我們相信{cn_kw}是生命中不可或缺的一部分。"),
                (f"The beauty of {en_kw} creates wonderful memories.", f"這個{cn_kw}的美麗創造了美好的回憶。"),
                (f"It is a wonderful experience to discover {en_kw}.", f"發現{cn_kw}是一個美妙的體驗。")
            ]
        
        # 隨機組合直至字數要求
        random.shuffle(pool)
        selected_en, selected_tr = [], []
        current_wc = 0
        for en, tr in pool:
            if current_wc < u_words:
                selected_en.append(en)
                selected_tr.append(tr)
                current_wc += len(en.split())
        
        st.session_state.active_en = " ".join(selected_en)
        st.session_state.active_tr = " ".join(selected_tr)

    if st.session_state.active_en:
        st.subheader("📜 課文原文 (100% English)")
        # 一句一行 + 大字體
        for line in st.session_state.active_en.split('.'):
            if line.strip():
                st.markdown(f"<div style='font-size: 32px; font-weight: 500; margin-bottom: 15px;'>• {line.strip()}.</div>", unsafe_allow_html=True)
        
        if st.button("🔊 全文朗讀"):
            st.audio(get_voice(st.session_state.active_en, target_lang, voice_speed), format="audio/mp3")
        
        with st.expander("👁️ 查看精準中文翻譯"):
            st.markdown(f"<div style='font-size: 20px; color: #D35400;'>{st.session_state.active_tr}</div>", unsafe_allow_html=True)

# --- Tab 3: 遊戲區 ---
with tab3:
    st.header("🎮 聽音挑戰")
    def refresh_q():
        all_words = []
        for l in DB: all_words.extend(DB[l]["words"])
        items = random.sample(all_words, 3)
        return items, random.choice(items)
    
    if f"q_{st.session_state.game_turn}" not in st.session_state:
        st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"] = refresh_q()
    
    cq, ct = st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"]
    if st.button("🔊 點聽題目"):
        st.audio(get_voice(ct[0], target_lang, voice_speed), format="audio/mp3")
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(cq):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"{word}", key=f"g_btn_{st.session_state.game_turn}_{i}"):
                if word == ct[0]:
                    st.balloons(); st.session_state.user_score += 5; st.session_state.game_turn += 1; time.sleep(1); st.rerun()
                else: st.error("❌ Try again!")

with tab4:
    st.header("🏆 成就紀錄")
    st.subheader(f"積分：{st.session_state.user_score} / 150")
