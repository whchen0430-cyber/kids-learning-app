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
if 'story_content' not in st.session_state:
    st.session_state.story_content = None

MAX_SCORE = 150 
if st.session_state.user_score >= MAX_SCORE:
    st.session_state.user_score = 0

# --- 2. A-Z 完整資料庫 ---
@st.cache_data
def get_full_db():
    return {
        "A": {"upper": "A", "lower": "a", "words": [("Apple", "🍎", "I like the red apple.", "我喜歡紅蘋果。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。"), ("Astronaut", "👨‍🚀", "Sky hero.", "太空英雄。"), ("Alligator", "🐊", "Big alligator.", "大鱷魚。"), ("Airplane", "✈️", "Fast airplane.", "快飛機。")]},
        "B": {"upper": "B", "lower": "b", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "I kick the ball.", "我踢球。"), ("Banana", "🍌", "Yellow banana.", "黃香蕉。"), ("Bird", "🐦", "The bird sings.", "鳥在唱歌。"), ("Bee", "🐝", "The bee makes honey.", "忙碌的蜜蜂。")]},
        "C": {"upper": "C", "lower": "c", "words": [("Cat", "🐱", "The cat is cute.", "貓很可愛。"), ("Cake", "🎂", "Happy birthday cake.", "生日蛋糕。"), ("Car", "🚗", "A fast car.", "快車。"), ("Cup", "🥛", "A cup of milk.", "一杯牛奶。"), ("Candy", "🍬", "Sweet candy.", "甜糖果。")]},
        "D": {"upper": "D", "lower": "d", "words": [("Dog", "🐶", "Good doggy.", "好狗狗。"), ("Duck", "🦆", "The duck swims.", "鴨子游泳。"), ("Dolphin", "🐬", "Smart dolphin.", "聰明海豚。"), ("Drum", "🥁", "Play the drum.", "打鼓。"), ("Door", "🚪", "Open the door.", "開門。")]},
        "E": {"upper": "E", "lower": "e", "words": [("Elephant", "🐘", "Big elephant.", "大象很大。"), ("Egg", "🥚", "I eat an egg.", "我吃蛋。"), ("Eagle", "🦅", "The eagle flies.", "老鷹飛。"), ("Eye", "👁️", "Open your eyes.", "張開眼睛。"), ("Ear", "👂", "I hear music.", "我聽見音樂。")]},
        "F": {"upper": "F", "lower": "f", "words": [("Fish", "🐟", "Fish in the sea.", "海裡的魚。"), ("Frog", "🐸", "The frog jumps.", "青蛙跳。"), ("Flower", "🌻", "Pretty flower.", "漂亮的花。"), ("Fan", "🌀", "Cool fan.", "涼風扇。"), ("Fork", "🍴", "Eat with a fork.", "用叉子吃。")]},
        "G": {"upper": "G", "lower": "g", "words": [("Goat", "🐐", "The goat eats grass.", "山羊吃草。"), ("Giraffe", "🦒", "Long neck.", "長脖子。"), ("Grapes", "🍇", "Sweet grapes.", "甜葡萄。"), ("Guitar", "🎸", "Play guitar.", "彈吉他。"), ("Gift", "🎁", "A big gift.", "大禮物。")]},
        "H": {"upper": "H", "lower": "h", "words": [("Horse", "🐎", "I ride a horse.", "我騎馬。"), ("Hat", "🎩", "Wear a hat.", "戴帽子。"), ("House", "🏠", "A big house.", "大房子。"), ("Heart", "❤️", "My heart.", "我的心。"), ("Hippo", "🦛", "Fat hippo.", "胖河馬。")]},
        "I": {"upper": "I", "lower": "i", "words": [("Ice cream", "🍦", "Cold ice cream.", "冷冰淇淋。"), ("Igloo", "🛖", "Ice house.", "冰屋。"), ("Ink", "🖋️", "Blue ink.", "藍墨水。"), ("Iron", "💨", "Hot iron.", "熱熨斗。"), ("Insect", "🐞", "Small insect.", "小昆蟲。")]},
        "J": {"upper": "J", "lower": "j", "words": [("Jam", "🍯", "Sweet jam.", "甜果醬。"), ("Juice", "🧃", "Fruit juice.", "果汁。"), ("Jellyfish", "🪼", "Floating jellyfish.", "水母。"), ("Jet", "🛩️", "Fast jet.", "噴射機。"), ("Jump", "🦘", "Jump high.", "跳高。")]},
        "K": {"upper": "K", "lower": "k", "words": [("Kite", "🪁", "Fly a kite.", "放風箏。"), ("Koala", "🐨", "Cute koala.", "無尾熊。"), ("King", "👑", "The king.", "國王。"), ("Key", "🔑", "Golden key.", "金鑰匙。"), ("Kangaroo", "🦘", "Strong kangaroo.", "強壯袋鼠。")]},
        "L": {"upper": "L", "lower": "l", "words": [("Lion", "🦁", "King of animals.", "萬獸之王。"), ("Lemon", "🍋", "Sour lemon.", "酸檸檬。"), ("Leaf", "🍃", "Green leaf.", "綠葉。"), ("Lamp", "💡", "Bright lamp.", "明亮的燈。"), ("Lollipop", "🍭", "Sweet lollipop.", "棒棒糖。")]},
        "M": {"upper": "M", "lower": "m", "words": [("Monkey", "🐒", "Funny monkey.", "有趣的猴子。"), ("Moon", "🌙", "Moon is white.", "月亮是白的。"), ("Milk", "🥛", "Drink milk.", "喝牛奶。"), ("Mouse", "🐭", "Small mouse.", "老鼠。"), ("Mushroom", "🍄", "Red mushroom.", "紅蘑菇。")]},
        "N": {"upper": "N", "lower": "n", "words": [("Nose", "👃", "My nose.", "我的鼻子。"), ("Nut", "🥜", "Eat a nut.", "吃堅果。"), ("Nest", "🪹", "Bird's nest.", "鳥巢。"), ("Net", "🕸️", "Fishing net.", "魚網。"), ("Nurse", "👩‍⚕️", "Good nurse.", "好護理師。")]},
        "O": {"upper": "O", "lower": "o", "words": [("Orange", "🍊", "Juicy orange.", "多汁橘子。"), ("Owl", "🦉", "Wise owl.", "貓頭鷹。"), ("Octopus", "🐙", "Eight legs.", "八隻腳。"), ("Onion", "🧅", "Strong onion.", "洋蔥。"), ("Ocean", "🌊", "Deep ocean.", "深海。")]},
        "P": {"upper": "P", "lower": "p", "words": [("Pig", "🐷", "Pink pig.", "粉紅豬。"), ("Pear", "🍐", "Sweet pear.", "梨子。"), ("Panda", "🐼", "Cute panda.", "熊貓。"), ("Piano", "🎹", "Play piano.", "彈鋼琴。"), ("Pizza", "🍕", "Hot pizza.", "熱披薩。")]},
        "Q": {"upper": "Q", "lower": "q", "words": [("Queen", "👸", "The queen.", "皇后。"), ("Question", "❓", "Ask a question.", "問問題。"), ("Quiet", "🤫", "Be quiet.", "安靜。"), ("Quack", "🦆", "Quack quack.", "呱呱叫。"), ("Quilt", "🧶", "Soft quilt.", "軟被子。")]},
        "R": {"upper": "R", "lower": "r", "words": [("Rabbit", "🐰", "White rabbit.", "小兔子。"), ("Rain", "🌧️", "Cold rain.", "冷冷的雨。"), ("Robot", "🤖", "Cool robot.", "機器人。"), ("Rainbow", "🌈", "Beautiful rainbow.", "彩虹。"), ("Rocket", "🚀", "Fast rocket.", "火箭。")]},
        "S": {"upper": "S", "lower": "s", "words": [("Sun", "☀️", "Hot sun.", "太陽。"), ("Snake", "🐍", "Long snake.", "長蛇。"), ("Star", "⭐", "Twinkle star.", "閃閃星星。"), ("Spider", "🕷️", "Small spider.", "小蜘蛛。"), ("Ship", "🚢", "Big ship.", "大船。")]},
        "T": {"upper": "T", "lower": "t", "words": [("Tiger", "🐯", "Strong tiger.", "老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。"), ("Train", "🚆", "Long train.", "長火車。"), ("Tomato", "🍅", "Red tomato.", "紅番茄。"), ("Telephone", "☎️", "Call me.", "打給我。")]},
        "U": {"upper": "U", "lower": "u", "words": [("Umbrella", "🌂", "My umbrella.", "我的雨傘。"), ("Unicorn", "🦄", "Magic unicorn.", "獨角獸。"), ("Up", "⬆️", "Go up.", "向上。"), ("Under", "👇", "Down there.", "在下面。"), ("Uniform", "🥋", "School uniform.", "制服。")]},
        "V": {"upper": "V", "lower": "v", "words": [("Van", "🚐", "Drive a van.", "箱型車。"), ("Violin", "🎻", "Play violin.", "小提琴。"), ("Vase", "🏺", "Pretty vase.", "花瓶。"), ("Vegetable", "🥦", "Healthy vegetables.", "健康蔬菜。"), ("Volcano", "🌋", "Hot volcano.", "火山。")]},
        "W": {"upper": "W", "lower": "w", "words": [("Whale", "🐋", "Big whale.", "大鯨魚。"), ("Watch", "⌚", "My watch.", "手錶。"), ("Water", "💧", "Drink water.", "水。"), ("Witch", "🧙‍♀️", "Funny witch.", "巫婆。"), ("Window", "🪟", "Close window.", "窗戶。")]},
        "X": {"upper": "X", "lower": "x", "words": [("Xylophone", "🎼", "Play xylophone.", "木琴。"), ("Box", "📦", "A box.", "盒子。"), ("Fox", "🦊", "Red fox.", "狐狸。"), ("Six", "6️⃣", "Number six.", "數字六。"), ("X-ray", "🩻", "X-ray photo.", "X光。")]},
        "Y": {"upper": "Y", "lower": "y", "words": [("Yo-yo", "🪀", "Red yo-yo.", "溜溜球。"), ("Yellow", "💛", "Bright yellow.", "亮黃色。"), ("Yacht", "🛥️", "White yacht.", "遊艇。"), ("Yak", "🐂", "Strong yak.", "氂牛。"), ("Yogurt", "🍦", "Eat yogurt.", "優格。")]},
        "Z": {"upper": "Z", "lower": "z", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zoo", "🦁", "Go to the zoo.", "去動物園。"), ("Zero", "0️⃣", "Number zero.", "數字零。"), ("Zipper", "🤐", "Close zipper.", "拉鍊。"), ("Zigzag", "📉", "Zigzag line.", "鋸齒線。")]}
    }

DB = get_full_db()

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 目前積分：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 恐龍進化邏輯 (絕對去小雞)
    if score < 30: d_emo, d_text, d_size, d_color = "🥚", "神祕的灰蛋", "100px", "#808080"
    elif score < 60: d_emo, d_text, d_size, d_color = "🦖", "幼龍孵化了！", "50px", "#90EE90"
    elif score < 90: d_emo, d_text, d_size, d_color = "🦕", "成長中的雷龍", "90px", "#2E8B57"
    elif score < 120: d_emo, d_text, d_size, d_color = "🦖", "強壯霸王龍", "130px", "#FF4500"
    else: d_emo, d_text, d_size, d_color = "🐲", "終極神龍！", "160px", "#B22222"

    st.markdown(f"<div style='text-align:center; padding:15px; border:2px solid {d_color}; border-radius:15px;'><h1 style='font-size:{d_size}; margin:0;'>{d_emo}</h1><p style='color:{d_color}; font-weight:bold; font-size:20px;'>{d_text}</p></div>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零"):
        st.session_state.user_score = 0
        st.rerun()

# --- 4. 輔助函數 ---
def get_audio_bytes(text, lang_choice, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang_choice else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# --- 5. 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 字母與單字練習", "📖 萬能短文生成", "🎮 互動遊戲區", "🏆 成就紀錄"])

with tab1:
    st.header("🔤 字母發音練習")
    letter = st.selectbox("請選擇字母", list(DB.keys()))
    info = DB[letter]
    with st.container():
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""<div style="background-color: #f0f2f6; border-radius: 20px; padding: 20px; text-align: center;"><span style="font-size: 120px; font-weight: bold; color: #FF4B4B;">{info['upper']}</span> <span style="font-size: 100px; font-weight: bold; color: #1C83E1;">{info['lower']}</span></div>""", unsafe_allow_html=True)
        with c2:
            if st.button(f"🔊 產生發音音軌"):
                st.audio(get_audio_bytes(info['upper'], target_lang, voice_speed), format="audio/mp3")
    st.divider()
    for word, emoji, sent, tran in info["words"]:
        with st.container():
            col1, col2 = st.columns([1, 4])
            col1.markdown(f"<h1 style='font-size:80px;'>{emoji}</h1>", unsafe_allow_html=True)
            with col2:
                st.subheader(word)
                st.write(f"**Sentence:** {sent}")
                st.caption(f"翻譯：{tran}")
                if st.button(f"🔊 播放單字發音", key=f"v_w_{word}"):
                    st.audio(get_audio_bytes(f"{word}. {sent}", target_lang, voice_speed), format="audio/mp3")
                    st.session_state.user_score = min(st.session_state.user_score + 1, 150)
            st.divider()

# --- Tab 2: 核心動態引擎 (真·萬能教材) ---
with tab2:
    st.header("📖 萬能主題自定義生成")
    user_topic = st.text_input("📝 請輸入任何主題 (如：旅遊、露營、恐龍、外星人)", "旅遊")
    
    if st.button("🚀 生成對應教材", key="gen_btn"):
        # 1. 清空舊狀態
        st.session_state.story_content = None
        
        # 2. 核心邏輯：依照主題與年齡「拼裝」不同句型
        t = user_topic
        if user_age == 4:
            s1 = f"Look at the {t}."
            s2 = f"It is very big."
            s3 = f"I like {t}."
            gram = "4歲：基礎主詞 + be動詞。"
        elif user_age == 6:
            s1 = f"We can go to the {t} today."
            s2 = f"The {t} has many colors."
            s3 = f"It is a happy day for us."
            gram = "6歲：加入顏色描述與動作。"
        elif user_age == 8:
            s1 = f"Traveling to the {t} is very exciting."
            s2 = f"We can explore many interesting things there."
            s3 = f"My friends and I love to discover new places."
            gram = "8歲：加入不定詞與動名詞主詞。"
        elif user_age == 10:
            s1 = f"If you want to have fun, you should visit the {t}."
            s2 = f"It is the best way to spend time with your family."
            s3 = f"Because {t} is special, we always feel happy there."
            gram = "10歲：條件句 (If) 與因果句 (Because)。"
        else: # 12歲
            s1 = f"The {t} provides a unique opportunity for people to explore the beauty of nature."
            s2 = f"Every journey to the {t} creates unforgettable memories that stay with us forever."
            s3 = f"We believe that experiencing new things is essential for our growth."
            gram = "12歲：關係子句 (that) 與名詞子句。"

        full_text = f"{s1} {s2} {s3}"
        st.session_state.story_content = {"text": full_text, "gram": gram, "topic": t}

    if st.session_state.story_content:
        sc = st.session_state.story_content
        st.subheader(f"📜 課文原文：{sc['topic']} (English Only)")
        # 鎖定結構：大字體 + 一句一行
        for line in sc['text'].split('.'):
            if line.strip():
                st.markdown(f"""<div style="font-size: 32px; font-weight: 500; color: #2E4053; margin-bottom: 15px;">• {line.strip()}.</div>""", unsafe_allow_html=True)
        
        if st.button("🔊 播放全文朗讀"):
            st.audio(get_audio_bytes(sc['text'], target_lang, voice_speed), format="audio/mp3")
        st.success(f"**💡 文法重點:** {sc['gram']}")
        with st.expander("👁️ 查看翻譯"):
            st.write(f"這是關於「{sc['topic']}」的主題課程內容。")

with tab3:
    st.header("🎮 聽音辨圖挑戰")
    def get_new_q():
        pool = []
        for l in DB: pool.extend(DB[l]["words"])
        c = random.sample(pool, 3)
        return c, random.choice(c)

    if f"g_q_{st.session_state.game_turn}" not in st.session_state:
        q_d, q_t = get_new_q()
        st.session_state[f"g_q_{st.session_state.game_turn}"] = q_d
        st.session_state[f"g_t_{st.session_state.game_turn}"] = q_t

    cq = st.session_state[f"g_q_{st.session_state.game_turn}"]
    ct = st.session_state[f"g_t_{st.session_state.game_turn}"]

    if st.button("🔊 播放題目"):
        st.audio(get_audio_bytes(ct[0], target_lang, voice_speed), format="audio/mp3")
    
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(cq):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"{word}", key=f"g_btn_{st.session_state.game_turn}_{i}", use_container_width=True):
                if word == ct[0]:
                    st.balloons()
                    st.success("🎉 Correct! 自動換題...")
                    st.session_state.user_score += 5
                    st.session_state.game_turn += 1
                    time.sleep(1)
                    st.rerun()
                else: st.error("❌ Try again!")

with tab4:
    st.header("🏆 成就紀錄")
    st.subheader(f"目前積分：{st.session_state.user_score} / 150")
