import streamlit as st
from gtts import gTTS
import os
import re
import random
import base64
import time
from datetime import datetime

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0
MAX_SCORE = 100

# --- 2. A-Z 完整資料庫 (發音精準校正版) ---
@st.cache_data
def get_full_db():
    return {
        "A": {"upper": "A", "lower": "a", "ipa": "/æ/", "sound_hint": "aaah", "tip": "嘴巴張大，舌頭放低", "words": [("Apple", "🍎", "I like the red apple.", "我喜歡紅蘋果。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。"), ("Astronaut", "👨‍🚀", "The astronaut flies.", "太空人飛翔。"), ("Alligator", "🐊", "Big alligator.", "大鱷魚。"), ("Airplane", "✈️", "Fast airplane.", "快飛機。")]},
        "B": {"upper": "B", "lower": "b", "ipa": "/b/", "sound_hint": "buh", "tip": "雙唇緊閉，突然噴氣", "words": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "I kick the ball.", "我踢球。"), ("Banana", "🍌", "Yellow banana.", "黃香蕉。"), ("Bird", "🐦", "The bird sings.", "鳥在唱歌。"), ("Bee", "🐝", "The bee makes honey.", "忙碌的蜜蜂。")]},
        "C": {"upper": "C", "lower": "c", "ipa": "/k/", "sound_hint": "kuh", "tip": "舌後部抬起，快速吐氣", "words": [("Cat", "🐱", "The cat is cute.", "貓很可愛。"), ("Cake", "🎂", "Happy birthday cake.", "生日蛋糕。"), ("Car", "🚗", "A fast car.", "快車。"), ("Cup", "🥛", "A cup of milk.", "一杯牛奶。"), ("Candy", "🍬", "Sweet candy.", "甜糖果。")]},
        "D": {"upper": "D", "lower": "d", "ipa": "/d/", "sound_hint": "duh", "tip": "舌尖頂住上齒齦再彈開", "words": [("Dog", "🐶", "Good doggy.", "好狗狗。"), ("Duck", "🦆", "The duck swims.", "鴨子游泳。"), ("Dolphin", "🐬", "Smart dolphin.", "聰明海豚。"), ("Drum", "🥁", "Play the drum.", "打鼓。"), ("Door", "🚪", "Open the door.", "開門。")]},
        "E": {"upper": "E", "lower": "e", "ipa": "/ɛ/", "sound_hint": "eh", "tip": "嘴角向兩邊張開，舌尖抵下齒", "words": [("Elephant", "🐘", "Big elephant.", "大象很大。"), ("Egg", "🥚", "I eat an egg.", "我吃蛋。"), ("Eagle", "🦅", "The eagle flies.", "老鷹飛。"), ("Eye", "👁️", "Open your eyes.", "張開眼睛。"), ("Ear", "👂", "I hear music.", "我聽見音樂。")]},
        "F": {"upper": "F", "lower": "f", "ipa": "/f/", "sound_hint": "fff", "tip": "上齒輕咬下唇吹氣", "words": [("Fish", "🐟", "Fish in the sea.", "海裡的魚。"), ("Frog", "🐸", "The frog jumps.", "青蛙跳。"), ("Flower", "🌻", "A pretty flower.", "漂亮的花。"), ("Fan", "🌀", "Cool fan.", "涼風扇。"), ("Fork", "🍴", "Eat with a fork.", "用叉子吃。")]},
        "G": {"upper": "G", "lower": "g", "ipa": "/g/", "sound_hint": "guh", "tip": "喉嚨發出震動音", "words": [("Goat", "🐐", "The goat eats grass.", "山羊吃草。"), ("Giraffe", "🦒", "Long neck.", "長脖子。"), ("Grapes", "🍇", "Sweet grapes.", "甜葡萄。"), ("Guitar", "🎸", "Play guitar.", "彈吉他。"), ("Gift", "🎁", "A big gift.", "大禮物。")]},
        "H": {"upper": "H", "lower": "h", "ipa": "/h/", "sound_hint": "huh", "tip": "放鬆呼出氣體", "words": [("Horse", "🐎", "I ride a horse.", "我騎馬。"), ("Hat", "🎩", "Wear a hat.", "戴帽子。"), ("House", "🏠", "A big house.", "大房子。"), ("Heart", "❤️", "My heart.", "我的心。"), ("Hippo", "🦛", "Fat hippo.", "胖河馬。")]},
        "I": {"upper": "I", "lower": "i", "ipa": "/ɪ/", "sound_hint": "ih", "tip": "嘴角微張發短音", "words": [("Ice cream", "🍦", "Cold ice cream.", "冷冰淇淋。"), ("Igloo", "🛖", "Ice house.", "冰屋。"), ("Ink", "🖋️", "Blue ink.", "藍墨水。"), ("Iron", "💨", "Hot iron.", "熱熨斗。"), ("Insect", "🐞", "Small insect.", "小昆蟲。")]},
        "J": {"upper": "J", "lower": "j", "ipa": "/dʒ/", "sound_hint": "juh", "tip": "雙唇突出頂上顎", "words": [("Jam", "🍯", "Sweet jam.", "甜果醬。"), ("Juice", "🧃", "Fruit juice.", "果汁。"), ("Jellyfish", "🪼", "Floating jellyfish.", "水母。"), ("Jet", "🛩️", "Fast jet.", "噴射機。"), ("Jump", "🦘", "Jump high.", "跳高。")]},
        "K": {"upper": "K", "lower": "k", "ipa": "/k/", "sound_hint": "kuh", "tip": "舌後抬起強力噴氣", "words": [("Kite", "🪁", "Fly a kite.", "放風箏。"), ("Koala", "🐨", "Cute koala.", "無尾熊。"), ("King", "👑", "The king.", "國王。"), ("Key", "🔑", "Golden key.", "金鑰匙。"), ("Kangaroo", "🦘", "Strong kangaroo.", "強壯袋鼠。")]},
        "L": {"upper": "L", "lower": "l", "ipa": "/l/", "sound_hint": "ul", "tip": "舌尖抵住上齒齦", "words": [("Lion", "🦁", "King of animals.", "萬獸之王。"), ("Lemon", "🍋", "Sour lemon.", "酸檸檬。"), ("Leaf", "🍃", "Green leaf.", "綠葉。"), ("Lamp", "💡", "Bright lamp.", "明亮的燈。"), ("Lollipop", "🍭", "Sweet lollipop.", "棒棒糖。")]},
        "M": {"upper": "M", "lower": "m", "ipa": "/m/", "sound_hint": "mmm", "tip": "雙唇緊閉鼻腔發音", "words": [("Monkey", "🐒", "Funny monkey.", "有趣的猴子。"), ("Moon", "🌙", "The moon is white.", "月亮是白的。"), ("Milk", "🥛", "Drink milk.", "喝牛奶。"), ("Mouse", "🐭", "Small mouse.", "小老鼠。"), ("Mushroom", "🍄", "Red mushroom.", "紅蘑菇。")]},
        "N": {"upper": "N", "lower": "n", "ipa": "/n/", "sound_hint": "nnn", "tip": "舌尖抵齒齦鼻腔出氣", "words": [("Nose", "👃", "My nose.", "我的鼻子。"), ("Nut", "🥜", "Eat a nut.", "吃堅果。"), ("Nest", "🪹", "Bird's nest.", "鳥巢。"), ("Net", "🕸️", "Fishing net.", "魚網。"), ("Nurse", "👩‍⚕️", "Good nurse.", "好護理師。")]},
        "O": {"upper": "O", "lower": "o", "ipa": "/ɑ/", "sound_hint": "ah", "tip": "嘴巴張圓舌頭放低", "words": [("Orange", "🍊", "Juicy orange.", "多汁橘子。"), ("Owl", "🦉", "Wise owl.", "貓頭鷹。"), ("Octopus", "🐙", "Eight legs.", "八隻腳。"), ("Onion", "🧅", "Strong onion.", "洋蔥。"), ("Ocean", "🌊", "Deep ocean.", "深海。")]},
        "P": {"upper": "P", "lower": "p", "ipa": "/p/", "sound_hint": "puh", "tip": "雙唇緊閉噴氣發音", "words": [("Pig", "🐷", "Pink pig.", "粉紅豬。"), ("Pear", "🍐", "Sweet pear.", "梨子。"), ("Panda", "🐼", "Cute panda.", "熊貓。"), ("Piano", "🎹", "Play piano.", "彈鋼琴。"), ("Pizza", "🍕", "Hot pizza.", "熱披薩。")]},
        "Q": {"upper": "Q", "lower": "q", "ipa": "/kw/", "sound_hint": "kwuh", "tip": "先發k再接w音", "words": [("Queen", "👸", "The queen.", "皇后。"), ("Question", "❓", "Ask a question.", "問問題。"), ("Quiet", "🤫", "Be quiet.", "安靜。"), ("Quack", "🦆", "Quack quack.", "呱呱叫。"), ("Quilt", "🧶", "Soft quilt.", "軟被子。")]},
        "R": {"upper": "R", "lower": "r", "ipa": "/r/", "sound_hint": "rrr", "tip": "雙唇微縮舌頭捲起", "words": [("Rabbit", "🐰", "White rabbit.", "小兔子。"), ("Rain", "🌧️", "Cold rain.", "冷冷的雨。"), ("Robot", "🤖", "Cool robot.", "機器人。"), ("Rainbow", "🌈", "Beautiful rainbow.", "彩虹。"), ("Rocket", "🚀", "Fast rocket.", "火箭。")]},
        "S": {"upper": "S", "lower": "s", "ipa": "/s/", "sound_hint": "sss", "tip": "牙齒輕咬吹氣發音", "words": [("Sun", "☀️", "Hot sun.", "太陽。"), ("Snake", "🐍", "Long snake.", "長蛇。"), ("Star", "⭐", "Twinkle star.", "閃閃星星。"), ("Spider", "🕷️", "Small spider.", "小蜘蛛。"), ("Ship", "🚢", "Big ship.", "大船。")]},
        "T": {"upper": "T", "lower": "t", "ipa": "/t/", "sound_hint": "tuh", "tip": "舌尖抵齒齦吐氣音", "words": [("Tiger", "🐯", "Strong tiger.", "老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。"), ("Train", "🚆", "Long train.", "長火車。"), ("Tomato", "🍅", "Red tomato.", "紅番茄。"), ("Telephone", "☎️", "Call me.", "打給我。")]},
        "U": {"upper": "U", "lower": "u", "ipa": "/ʌ/", "sound_hint": "uh", "tip": "嘴巴自然放鬆張開", "words": [("Umbrella", "🌂", "My umbrella.", "我的雨傘。"), ("Unicorn", "🦄", "Magic unicorn.", "獨角獸。"), ("Up", "⬆️", "Go up.", "向上。"), ("Under", "👇", "Down there.", "在下面。"), ("Uniform", "🥋", "School uniform.", "制服。")]},
        "V": {"upper": "V", "lower": "v", "ipa": "/v/", "sound_hint": "vuh", "tip": "上齒咬下唇震動發音", "words": [("Van", "🚐", "Drive a van.", "箱型車。"), ("Violin", "🎻", "Play violin.", "小提琴。"), ("Vase", "🏺", "Pretty vase.", "花瓶。"), ("Vegetable", "🥦", "Healthy vegetables.", "健康蔬菜。"), ("Volcano", "🌋", "Hot volcano.", "火山。")]},
        "W": {"upper": "W", "lower": "w", "ipa": "/w/", "sound_hint": "wuh", "tip": "雙唇縮圓快速張開", "words": [("Whale", "🐋", "Big whale.", "大鯨魚。"), ("Watch", "⌚", "My watch.", "手錶。"), ("Water", "💧", "Drink water.", "水。"), ("Witch", "🧙‍♀️", "Funny witch.", "巫婆。"), ("Window", "🪟", "Close window.", "關窗。")]},
        "X": {"upper": "X", "lower": "x", "ipa": "/ks/", "sound_hint": "ks", "tip": "發ks混合音", "words": [("Xylophone", "🎼", "Play xylophone.", "木琴。"), ("Box", "📦", "A box.", "盒子。"), ("Fox", "🦊", "Red fox.", "狐狸。"), ("Six", "6️⃣", "Number six.", "數字六。"), ("X-ray", "🩻", "X-ray photo.", "X光。")]},
        "Y": {"upper": "Y", "lower": "y", "ipa": "/j/", "sound_hint": "yuh", "tip": "舌前抬起嘴角張開", "words": [("Yo-yo", "🪀", "Red yo-yo.", "溜溜球。"), ("Yellow", "💛", "Bright yellow.", "亮黃色。"), ("Yacht", "🛥️", "White yacht.", "遊艇。"), ("Yak", "🐂", "Strong yak.", "氂牛。"), ("Yogurt", "🍦", "Eat yogurt.", "優格。")]},
        "Z": {"upper": "Z", "lower": "z", "ipa": "/z/", "sound_hint": "zzz", "tip": "舌尖抵下齒震動發音", "words": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zoo", "🦁", "Go to the zoo.", "去動物園。"), ("Zero", "0️⃣", "Number zero.", "數字零。"), ("Zipper", "🤐", "Close zipper.", "拉鍊。"), ("Zigzag", "📉", "Zigzag line.", "鋸齒線。")]}
    }

DB = get_full_db()

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分進度：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    d_emo = "🥚" if score < 30 else ("🦖" if score < 70 else "🦕")
    st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)
    if st.button("🔄 積分歸零 (Reset Score)"):
        st.session_state.user_score = 0
        st.rerun()

# --- 4. 輔助函數 ---
def play_audio(text, lang, speed, autoplay=False):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    filename = f"speech_{datetime.now().strftime('%H%M%S%f')}.mp3"
    tts.save(filename)
    if autoplay:
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>""", unsafe_allow_html=True)
    else:
        st.audio(filename)

# --- 5. 分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 字母發音教學", "📖 短文指令解析", "🎮 互動遊戲區", "🏆 成就紀錄"])

with tab1:
    st.header("🔤 字母與拼字發音練習")
    letter = st.selectbox("請選擇字母 (A-Z)", list(DB.keys()))
    info = DB[letter]
    with st.container():
        c_p1, c_p2 = st.columns([1, 1])
        with c_p1:
            st.markdown(f"""<div style="background-color: #f0f2f6; border-radius: 20px; padding: 20px; text-align: center;"><span style="font-size: 120px; font-weight: bold; color: #FF4B4B;">{info['upper']}</span> <span style="font-size: 100px; font-weight: bold; color: #1C83E1;">{info['lower']}</span></div>""", unsafe_allow_html=True)
        with c_p2:
            st.write("### 🔊 聽聽看發音")
            if st.button(f"🗣️ 唸唸字母名 (Name: {info['upper']})", key="v_name"):
                play_audio(info['upper'], target_lang, voice_speed, autoplay=True)
            
            # 【校正重點】使用擬聲 hint 來發出正確的拼字音
            sound_to_play = info.get('sound_hint', info['ipa'].replace("/", ""))
            if st.button(f"👄 唸唸拼字音 (Sound: {info['ipa']})", key="v_sound"):
                play_audio(sound_to_play, target_lang, voice_speed, autoplay=True)
            st.success(f"**💡 發音小祕訣:**\n{info['tip']}")

    st.divider()
    st.subheader(f"✨ 字母 {letter} 的代表單字")
    display_limit = 3 if user_age <= 6 else 5
    for word, emoji, sent, tran in info["words"][:display_limit]:
        with st.container():
            c1, c2 = st.columns([1, 4])
            c1.markdown(f"<h1 style='font-size:80px; text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
            with c2:
                st.subheader(word)
                st.write(f"**Sentence:** {sent}")
                st.caption(f"翻譯：{tran}")
                if st.button(f"🔊 聽單字發音", key=f"v_{word}"):
                    play_audio(f"{word}. {sent}", target_lang, voice_speed, autoplay=True)
                    st.session_state.user_score = min(st.session_state.user_score + 1, MAX_SCORE)
            st.divider()

with tab2:
    st.header("📖 自定義短文教學解析")
    user_topic = st.text_input("📝 請輸入短文主題", "Park")
    if st.button("🚀 生成教材內容"):
        st.session_state['story_text'] = f"The {user_topic} is a wonderful place. We can see many friends here. We play together all day. It is a very happy day!"
        st.session_state['story_vocab'] = [(f"{user_topic}", "主題名詞"), ("Wonderful", "極好的")]
        st.session_state['story_gram'] = f"現在式用法：使用 'is' 描述狀態。"
    if 'story_text' in st.session_state:
        sentences = st.session_state['story_text'].split('.')
        for sentence in sentences:
            if sentence.strip():
                st.markdown(f"""<div style="font-size: 32px; font-weight: 500; line-height: 1.6; color: #2E4053; margin-bottom: 15px;">• {sentence.strip()}.</div>""", unsafe_allow_html=True)
        if st.button("🔊 全文朗讀"):
            play_audio(st.session_state['story_text'], target_lang, voice_speed, autoplay=True)
        col_v, col_g = st.columns(2)
        with col_v:
            st.subheader("📝 重點單字")
            for v, k in st.session_state['story_vocab']: st.write(f"• **{v}**: {k}")
        with col_g:
            st.subheader("💡 文法點撥")
            st.success(st.session_state['story_gram'])
        with st.expander("👁️ 查看中文翻譯"): st.write("（此處顯示翻譯內容）")

with tab3:
    st.header("🎮 聽音辨圖挑戰")
    if 'game_data' not in st.session_state:
        all_words = []
        for l in DB: all_words.extend(DB[l]["words"])
        st.session_state.game_data = random.sample(all_words, 3)
        st.session_state.game_target = random.choice(st.session_state.game_data)
        st.session_state.game_mode = random.choice(["word", "sentence"])
        st.session_state.show_reward = False
    target = st.session_state.game_target
    if st.session_state.get('show_reward'):
        st.markdown("""<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.9); z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center;"><h1 style="font-size: 150px; margin: 0;">🌟</h1><h2 style="font-size: 60px; color: #FFD700;">Amazing!</h2></div>""", unsafe_allow_html=True)
        st.balloons(); time.sleep(1.5); st.session_state.show_reward = False; st.rerun()
    st.subheader(f"🎯 挑戰目標：{'聽單字' if st.session_state.game_mode == 'word' else '聽句子'}辨圖")
    if st.button("🔊 播放題目音檔"):
        play_audio(target[0] if st.session_state.game_mode == 'word' else target[2], target_lang, voice_speed, autoplay=True)
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(st.session_state.game_data):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"{word}", key=f"g_{i}", use_container_width=True):
                if word == target[0]:
                    st.session_state.user_score = min(st.session_state.user_score + 5, MAX_SCORE)
                    st.session_state.show_reward = True
                    all_words = []
                    for l in DB: all_words.extend(DB[l]["words"])
                    st.session_state.game_data = random.sample(all_words, 3); st.session_state.game_target = random.choice(st.session_state.game_data); st.rerun()
                else: st.error("❌ Try again!")

with tab4:
    st.header("🏆 成就紀錄")
    st.subheader(f"目前積分：{score} / 100")
