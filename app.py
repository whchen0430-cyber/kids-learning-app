import streamlit as st
from gtts import gTTS
import os
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0
MAX_SCORE = 100

# --- 2. A-Z 完整資料庫 (快取加速) ---
@st.cache_data
def get_full_db():
    return {
        "A": [("Apple", "🍎", "I like the red apple.", "我喜歡紅蘋果。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。"), ("Axe", "🪓", "Be careful.", "要小心。"), ("Alligator", "🐊", "Big alligator.", "大鱷魚。"), ("Airplane", "✈️", "Fast airplane.", "快飛機。")],
        "B": [("Bear", "🧸", "A brown bear.", "一隻棕熊。"), ("Ball", "⚽", "I kick the ball.", "我踢球。"), ("Banana", "🍌", "Yellow banana.", "黃香蕉。"), ("Bird", "🐦", "The bird sings.", "鳥在唱歌。"), ("Bee", "🐝", "The bee makes honey.", "蜜蜂造蜜。")],
        "C": [("Cat", "🐱", "The cat is cute.", "貓很可愛。"), ("Cake", "🎂", "Happy birthday cake.", "生日蛋糕。"), ("Car", "🚗", "A fast car.", "快車。"), ("Cup", "🥛", "A cup of milk.", "一杯牛奶。"), ("Candy", "🍬", "Sweet candy.", "甜糖果。")],
        "D": [("Dog", "🐶", "Good doggy.", "好狗狗。"), ("Duck", "🦆", "The duck swims.", "鴨子游泳。"), ("Dolphin", "🐬", "Smart dolphin.", "聰明海豚。"), ("Drum", "🥁", "Play the drum.", "打鼓。"), ("Door", "🚪", "Open the door.", "開門。")],
        "E": [("Elephant", "🐘", "Big elephant.", "大象很大。"), ("Egg", "🥚", "I eat an egg.", "我吃蛋。"), ("Eagle", "🦅", "The eagle flies.", "老鷹飛。"), ("Eye", "👁️", "Open your eyes.", "張開眼睛。"), ("Ear", "👂", "I hear music.", "我聽見音樂。")],
        "F": [("Fish", "🐟", "Fish in the sea.", "海裡的魚。"), ("Frog", "🐸", "The frog jumps.", "青蛙跳。"), ("Flower", "🌻", "A pretty flower.", "漂亮的花。"), ("Fan", "🌀", "Cool fan.", "涼風扇。"), ("Fork", "🍴", "Eat with a fork.", "用叉子吃。")],
        "G": [("Goat", "🐐", "The goat eats grass.", "山羊吃草。"), ("Giraffe", "🦒", "Long neck.", "長脖子。"), ("Grapes", "🍇", "Sweet grapes.", "甜葡萄。"), ("Guitar", "🎸", "Play guitar.", "彈吉他。"), ("Gift", "🎁", "A big gift.", "大禮物。")],
        "H": [("Horse", "🐎", "I ride a horse.", "我騎馬。"), ("Hat", "🎩", "Wear a hat.", "戴帽子。"), ("House", "🏠", "A big house.", "大房子。"), ("Heart", "❤️", "My heart.", "我的心。"), ("Hippo", "🦛", "Fat hippo.", "胖河馬。")],
        "I": [("Ice cream", "🍦", "Cold ice cream.", "冷冰淇淋。"), ("Igloo", "🛖", "Ice house.", "冰屋。"), ("Ink", "🖋️", "Blue ink.", "藍墨水。"), ("Iron", "💨", "Hot iron.", "熱熨斗。"), ("Insect", "🐞", "Small insect.", "小昆蟲。")],
        "J": [("Jam", "🍯", "Sweet jam.", "甜果醬。"), ("Juice", "🧃", "Fruit juice.", "果汁。"), ("Jellyfish", "🪼", "Floating jellyfish.", "水母。"), ("Jet", "🛩️", "Fast jet.", "噴射機。"), ("Jump", "🦘", "Jump high.", "跳高。")],
        "K": [("Kite", "🪁", "Fly a kite.", "放風箏。"), ("Koala", "🐨", "Cute koala.", "無尾熊。"), ("King", "👑", "The king.", "國王。"), ("Key", "🔑", "Golden key.", "金鑰匙。"), ("Kangaroo", "🦘", "Strong kangaroo.", "強壯袋鼠。")],
        "L": [("Lion", "🦁", "King of animals.", "萬獸之王。"), ("Lemon", "🍋", "Sour lemon.", "酸檸檬。"), ("Leaf", "🍃", "Green leaf.", "綠葉。"), ("Lamp", "💡", "Bright lamp.", "明亮的燈。"), ("Lollipop", "🍭", "Sweet lollipop.", "棒棒糖。")],
        "M": [("Monkey", "🐒", "Funny monkey.", "有趣的猴子。"), ("Moon", "🌙", "The moon is white.", "月亮是白的。"), ("Milk", "🥛", "Drink milk.", "喝牛奶。"), ("Mouse", "🐭", "Small mouse.", "小老鼠。"), ("Mushroom", "🍄", "Red mushroom.", "紅蘑菇。")],
        "N": [("Nose", "👃", "My nose.", "我的鼻子。"), ("Nut", "🥜", "Eat a nut.", "吃堅果。"), ("Nest", "🪹", "Bird's nest.", "鳥巢。"), ("Net", "🕸️", "Fishing net.", "魚網。"), ("Nurse", "👩‍⚕️", "Good nurse.", "好護理師。")],
        "O": [("Orange", "🍊", "Juicy orange.", "多汁橘子。"), ("Owl", "🦉", "Wise owl.", "貓頭鷹。"), ("Octopus", "🐙", "Eight legs.", "八隻腳。"), ("Onion", "🧅", "Strong onion.", "洋蔥。"), ("Ocean", "🌊", "Deep ocean.", "深海。")],
        "P": [("Pig", "🐷", "Pink pig.", "粉紅豬。"), ("Pear", "🍐", "Sweet pear.", "梨子。"), ("Panda", "🐼", "Cute panda.", "熊貓。"), ("Piano", "🎹", "Play piano.", "彈鋼琴。"), ("Pizza", "🍕", "Hot pizza.", "熱披薩。")],
        "Q": [("Queen", "👸", "The queen.", "皇后。"), ("Question", "❓", "Ask a question.", "問問題。"), ("Quiet", "🤫", "Be quiet.", "安費。"), ("Quack", "🦆", "Quack quack.", "呱呱叫。"), ("Quilt", "🧶", "Soft quilt.", "軟被子。")],
        "R": [("Rabbit", "🐰", "White rabbit.", "小兔子。"), ("Rain", "🌧️", "Cold rain.", "冷冷的雨。"), ("Robot", "🤖", "Cool robot.", "機器人。"), ("Rainbow", "🌈", "Beautiful rainbow.", "彩虹。"), ("Rocket", "🚀", "Fast rocket.", "火箭。")],
        "S": [("Sun", "☀️", "Hot sun.", "太陽。"), ("Snake", "🐍", "Long snake.", "長蛇。"), ("Star", "⭐", "Twinkle star.", "閃閃星星。"), ("Spider", "🕷️", "Small spider.", "小蜘蛛。"), ("Ship", "🚢", "Big ship.", "大船。")],
        "T": [("Tiger", "🐯", "Strong tiger.", "老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。"), ("Train", "🚆", "Long train.", "長火車。"), ("Tomato", "🍅", "Red tomato.", "紅番茄。"), ("Telephone", "☎️", "Call me.", "打給我。")],
        "U": [("Umbrella", "🌂", "My umbrella.", "我的雨傘。"), ("Unicorn", "🦄", "Magic unicorn.", "獨件獸。"), ("Up", "⬆️", "Go up.", "向上。"), ("Under", "👇", "Down there.", "在下面。"), ("Uniform", "🥋", "School uniform.", "制服。")],
        "V": [("Van", "🚐", "Drive a van.", "箱型車。"), ("Violin", "🎻", "Play violin.", "小提琴。"), ("Vase", "🏺", "Pretty vase.", "花瓶。"), ("Vegetable", "🥦", "Healthy vegetables.", "健康蔬菜。"), ("Volcano", "🌋", "Hot volcano.", "火山。")],
        "W": [("Whale", "🐋", "Big whale.", "大鯨魚。"), ("Watch", "⌚", "My watch.", "手錶。"), ("Water", "💧", "Drink water.", "水。"), ("Witch", "🧙‍♀️", "Funny witch.", "巫婆。"), ("Window", "🪟", "Close window.", "關窗。")],
        "X": [("Xylophone", "🎼", "Play xylophone.", "木琴。"), ("Box", "📦", "A box.", "盒子。"), ("Fox", "🦊", "Red fox.", "狐狸。"), ("Six", "6️⃣", "Number six.", "數字六。"), ("X-ray", "🩻", "X-ray photo.", "X光。")],
        "Y": [("Yo-yo", "🪀", "Red yo-yo.", "溜溜球。"), ("Yellow", "💛", "Bright yellow.", "亮黃色。"), ("Yacht", "🛥️", "White yacht.", "遊艇。"), ("Yak", "🐂", "Strong yak.", "氂牛。"), ("Yogurt", "🍦", "Eat yogurt.", "優格。")],
        "Z": [("Zebra", "🦓", "Striped zebra.", "斑馬。"), ("Zoo", "🦁", "Go to the zoo.", "去動物園。"), ("Zero", "0️⃣", "Number zero.", "數字零。"), ("Zipper", "🤐", "Close zipper.", "拉鍊。"), ("Zigzag", "📉", "Zigzag line.", "鋸齒線。")]
    }

DB = get_full_db()

# --- 3. 側邊欄：恐龍狀態與核心設定 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    st.write(f"🌟 積分進度：{score} / {MAX_SCORE}")
    st.progress(min(score / MAX_SCORE, 1.0))
    
    # 修正縮進邏輯
    if score < 30:
        d_emo, d_name = "🥚", "恐龍蛋"
    elif score < 70:
        d_emo, d_name = "🦖", "小恐龍"
    else:
        d_emo, d_name = "🦕", "超級巨龍"
    
    st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.title(f"等級：{d_name}")
    st.divider()
    user_age = st.select_slider("學生年齡", options=[4, 6, 8, 10, 12])
    target_lang = st.radio("目標語言", ["英文 (English)", "日文 (日本語)"])
    voice_speed = st.slider("語速設定", 0.5, 1.0, 0.8)

# --- 4. 輔助函數 ---
def play_audio(text, lang, speed):
    clean = re.sub(r'[\u4e00-\u9fa5]', '', text)
    l_code = 'en' if "英" in lang else 'ja'
    tts = gTTS(text=clean, lang=l_code, slow=(speed < 1.0))
    tts.save("speech.mp3")
    st.audio("speech.mp3")

# --- 5. 四大分頁架構 ---
tab1, tab2, tab3, tab4 = st.tabs(["🔤 字母單字一體化", "📖 短文指令解析", "🎮 互動遊戲區", "🏆 成就紀錄"])

with tab1:
    st.header("🔤 字母單字學習")
    letter = st.selectbox("選擇字母", list(DB.keys()))
    for word, emoji, sent, tran in DB[letter]:
        with st.container():
            c1, c2 = st.columns([1, 4])
            c1.markdown(f"<h1 style='font-size:80px;'>{emoji}</h1>", unsafe_allow_html=True)
            c2.subheader(word)
            c2.write(f"{sent} ({tran})")
            if c2.button(f"🔊 聽發音", key=f"v_{word}"):
                play_audio(f"{word}. {sent}", target_lang, voice_speed)
                st.session_state.user_score = min(st.session_state.user_score + 1, MAX_SCORE)
                st.rerun()

with tab2:
    st.header("📖 短文指令解析")
    user_topic = st.text_input("輸入主題 (例如: Farm)", "Ocean")
    if st.button("🚀 生成短文"):
        st.session_state['story'] = f"The ocean is big and blue. We can see many fish in the water."
    if 'story' in st.session_state:
        st.info(st.session_state['story'])
        if st.button("🔊 播放音檔"):
            play_audio(st.session_state['story'], target_lang, voice_speed)

with tab3:
    st.header("🎮 聽音辨圖挑戰 (混合模式)")
    if 'game_data' not in st.session_state or st.button("🔄 換一組新挑戰"):
        all_words = []
        for l in DB: all_words.extend(DB[l])
        st.session_state.game_data = random.sample(all_words, 3)
        st.session_state.game_target = random.choice(st.session_state.game_data)
        st.session_state.game_mode = random.choice(["word", "sentence"])

    target = st.session_state.game_target
    mode = st.session_state.game_mode
    st.subheader(f"🎯 挑戰：{'聽單字' if mode == 'word' else '聽句子'}辨圖")
    
    if st.button("🔊 播放挑戰音檔"):
        play_audio(target[0] if mode == "word" else target[2], target_lang, voice_speed)

    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(st.session_state.game_data):
        with cols[i]:
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"這是 {word} 嗎?", key=f"g_{i}", use_container_width=True):
                if word == target[0]:
                    st.balloons()
                    st.success("✅ 答對了！積分 +5")
                    st.session_state.user_score = min(st.session_state.user_score + 5, MAX_SCORE)
                    st.rerun()
                else:
                    st.error("❌ 錯了，再試一次！")

with tab4:
    st.header("🏆 成就紀錄")
    st.subheader(f"目前積分：{score} / 100")
    if score >= MAX_SCORE:
        st.balloons()
        st.success("恭喜！你已經達成 100 分滿分！")
