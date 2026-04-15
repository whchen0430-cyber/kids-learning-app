import streamlit as st
from gtts import gTTS
import io
import re
import random
import time

# --- 1. 頁面配置與積分系統 ---
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

# --- 2. A-Z 資料庫 ---
@st.cache_data
def get_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "The apple is red.", "蘋果是紅的。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "Kick the ball.", "踢球。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "強壯老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zero", "0️⃣", "Zero is a number.", "零是一個數字。")]}
    }
DB = get_db()

# --- 3. 側邊欄：恐龍成長與難度設定 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 進化圖案：絕對去小雞，僅使用龍族系統
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "幼龍剛破殼！", "50px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長期雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "猛壯霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極噴火神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    
    user_age = st.select_slider("學生年齡 (影響短文難度)", options=[4, 6, 8, 10, 12])
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
tab1, tab2, tab3, tab4 = st.tabs(["🔤 單字與字母", "📖 教材動態生成", "🎮 互動挑戰", "🏆 成長紀錄"])

with tab1:
    st.header("🔤 單字發音練習")
    letter = st.selectbox("選擇字母", list(DB.keys()))
    info = DB[letter]
    st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{info['upper']} {info['lower']}</h1>", unsafe_allow_html=True)
    for w, emo, sent, tr in info["words"]:
        st.write(f"### {emo} {w}")
        if st.button(f"🔊 聽發音", key=f"btn_{w}"):
            st.audio(get_voice(f"{w}. {sent}", target_lang, voice_speed), format="audio/mp3")
            st.session_state.user_score = min(st.session_state.user_score + 1, 150)

# --- Tab 2: 指令生成＋年齡分級＋字數控制 ---
with tab2:
    st.header("📖 教材生成引擎")
    u_topic = st.text_input("📝 輸入主題 (例如：去海邊旅遊、我的小狗)", "去旅遊")
    u_words = st.select_slider("📏 設定總字數 (約)", options=[10, 20, 30, 40, 50], value=20)
    
    if st.button("🚀 依照年齡與主題生成內容", key="gen_btn"):
        # 提取關鍵字並過濾
        kw_raw = "".join(re.findall(r'[A-Za-z0-9]+', u_topic))
        kw = kw_raw if kw_raw else "this topic"
        
        # 根據年齡定義句型庫
        if user_age <= 6:
            pool = [f"I like {kw}.", f"See the {kw}.", f"It is very big.", f"We play with {kw}.", f"It is a happy day."]
        elif user_age <= 10:
            pool = [f"Today we are exploring {kw} together.", f"My friends like {kw} because it is very fun.", f"We can learn many new things about {kw}.", f"I want to see more about {kw} with my family."]
        else: # 12歲
            pool = [f"Exploring {kw} provides us with unique opportunities to learn.", f"We believe that {kw} is an essential part of our amazing journey.", f"The beauty of {kw} creates memories that stay with us forever.", f"It is a wonderful experience to discover the secrets of {kw}."]
        
        # 隨機組合直至達到字數要求
        result_list = []
        current_count = 0
        while current_count < u_words:
            sentence = random.choice(pool)
            if sentence not in result_list:
                result_list.append(sentence)
                current_count += len(sentence.split())
            if len(result_list) >= len(pool): break # 防死循環
            
        st.session_state.active_en = " ".join(result_list)
        st.session_state.active_tr = f"這是一段專為 {user_age} 歲學生設計、關於「{u_topic}」的教材內容。"

    if st.session_state.active_en:
        st.subheader("📜 課文原文 (English Only)")
        # 鎖定結構：大字體 + 一句一行 + 絕對無中文
        for line in st.session_state.active_en.split('.'):
            if line.strip():
                st.markdown(f"""<div style="font-size: 32px; font-weight: 500; color: #2E4053; margin-bottom: 15px;">• {line.strip()}.</div>""", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文朗讀"):
            st.audio(get_voice(st.session_state.active_en, target_lang, voice_speed), format="audio/mp3")
        
        with st.expander("👁️ 查看翻譯與說明"):
            st.write(st.session_state.active_tr)

# --- Tab 3: 遊戲區 ---
with tab3:
    st.header("🎮 聽音辨圖挑戰")
    def get_new_q():
        all_pool = []
        for l in DB: all_pool.extend(DB[l]["words"])
        items = random.sample(all_pool, 3)
        return items, random.choice(items)
    
    if f"q_{st.session_state.game_turn}" not in st.session_state:
        st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"] = get_new_q()
    
    cq, ct = st.session_state[f"q_{st.session_state.game_turn}"], st.session_state[f"t_{st.session_state.game_turn}"]
    if st.button("🔊 播放題目"):
        st.audio(get_voice(ct[0], target_lang, voice_speed), format="audio/mp3")
    
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(cq):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"{word}", key=f"g_btn_{st.session_state.game_turn}_{i}", use_container_width=True):
                if word == ct[0]:
                    st.balloons(); st.session_state.user_score += 5; st.session_state.game_turn += 1; time.sleep(1); st.rerun()
                else: st.error("❌ Try again!")

with tab4:
    st.header("🏆 成就")
    st.subheader(f"積分：{st.session_state.user_score} / 150")
