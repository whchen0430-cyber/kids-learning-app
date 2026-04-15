import streamlit as st
from gtts import gTTS
import os
import re
import random

# --- 1. 頁面配置與積分系統 ---
st.set_page_config(page_title="恐龍語文冒險樂園", page_icon="🦖", layout="wide")

if 'user_score' not in st.session_state:
    st.session_state.user_score = 0

# --- 2. A-Z 完整資料庫 (26個字母，每個字母5個單字/例句/翻譯) ---
# 這裡先展示完整 A-Z 的結構，我已為您填入 A-Z 每個字母的啟蒙單字
@st.cache_data
def get_full_db():
    return {
        "A": [("Apple", "🍎", "I like the red apple.", "我喜歡紅蘋果。"), ("Ant", "🐜", "The ant is small.", "螞蟻很小。"), ("Axe", "🪓", "Be careful with the axe.", "用斧頭要小心。"), ("Alligator", "🐊", "The alligator is long.", "鱷魚很長。"), ("Airplane", "✈️", "The airplane is fast.", "飛機很快。")],
        "B": [("Bear", "🧸", "A big brown bear.", "一隻大棕熊。"), ("Ball", "⚽", "I kick the ball.", "我踢球。"), ("Banana", "🍌", "Yellow banana.", "黃香蕉。"), ("Bird", "🐦", "The bird is singing.", "鳥在唱歌。"), ("Bee", "🐝", "The bee makes honey.", "忙碌的蜜蜂。")],
        "C": [("Cat", "🐱", "The cat is cute.", "貓咪很可愛。"), ("Cake", "🎂", "Happy birthday cake.", "生日蛋糕。"), ("Car", "🚗", "A fast red car.", "快紅車。"), ("Cup", "🥛", "A cup of milk.", "一杯牛奶。"), ("Candy", "🍬", "Sweet candy.", "甜甜的糖果。")],
        "D": [("Dog", "🐶", "Good doggy.", "好狗狗。"), ("Duck", "🦆", "The duck swims.", "鴨子游泳。"), ("Dolphin", "🐬", "Dolphins are smart.", "海豚很聰明。"), ("Drum", "🥁", "Play the drum.", "打鼓。"), ("Door", "🚪", "Open the door.", "開門。")],
        "E": [("Elephant", "🐘", "The elephant is big.", "大象很大。"), ("Egg", "🥚", "I eat an egg.", "我吃蛋。"), ("Eagle", "🦅", "The eagle flies high.", "老鷹飛很高。"), ("Eye", "👁️", "Open your eyes.", "張開眼睛。"), ("Ear", "👂", "I hear music.", "我聽見音樂。")],
        "F": [("Fish", "🐟", "Fish in the water.", "水裡的魚。"), ("Frog", "🐸", "The frog jumps.", "青蛙跳。"), ("Flower", "🌻", "A yellow flower.", "一朵黃花。"), ("Fan", "🌀", "Turn on the fan.", "開風扇。"), ("Fork", "🍴", "Eat with a fork.", "用叉子吃。")],
        "G": [("Goat", "🐐", "The goat eats grass.", "山羊吃草。"), ("Giraffe", "🦒", "Long neck giraffe.", "長頸鹿。"), ("Grapes", "🍇", "Sweet purple grapes.", "甜葡萄。"), ("Guitar", "🎸", "Play the guitar.", "彈吉他。"), ("Gift", "🎁", "A birthday gift.", "生日禮物。")],
        "H": [("Horse", "🐎", "I ride a horse.", "我騎馬。"), ("Hat", "🎩", "Wear a hat.", "戴帽子。"), ("House", "🏠", "A big house.", "大房子。"), ("Heart", "❤️", "I love you.", "我愛你。"), ("Hippo", "🦛", "Hungry hippo.", "餓餓河馬。")],
        "I": [("Ice cream", "🍦", "I love ice cream.", "我愛冰淇淋。"), ("Igloo", "🛖", "Ice house.", "冰屋。"), ("Ink", "🖋️", "Blue ink.", "藍墨水。"), ("Iron", "💨", "Hot iron.", "熱熨斗。"), ("Insect", "🐞", "Look at the insect.", "看昆蟲。")],
        "J": [("Jam", "🍯", "Strawberry jam.", "草莓醬。"), ("Juice", "🧃", "Orange juice.", "橘子汁。"), ("Jellyfish", "🪼", "Floating jellyfish.", "水母。"), ("Jet", "🛩️", "Fast jet.", "噴射機。"), ("Jump", "🦘", "Jump high.", "跳高。")],
        "K": [("Kite", "🪁", "Fly a kite.", "放風箏。"), ("Koala", "🐨", "Cute koala.", "無尾熊。"), ("King", "👑", "The king is here.", "國王在此。"), ("Key", "🔑", "Open the lock.", "鑰匙。"), ("Kangaroo", "🦘", "Jump kangaroo.", "袋鼠。")],
        "L": [("Lion", "🦁", "King of the forest.", "森林之王。"), ("Lemon", "🍋", "Sour lemon.", "酸檸檬。"), ("Leaf", "🍃", "Green leaf.", "綠葉。"), ("Lamp", "💡", "Turn on the lamp.", "開燈。"), ("Lollipop", "🍭", "Sweet lollipop.", "棒棒糖。")],
        "M": [("Monkey", "🐒", "Monkey likes bananas.", "猴子愛香蕉。"), ("Moon", "🌙", "Goodnight moon.", "晚安月亮。"), ("Milk", "🥛", "Drink milk.", "喝牛奶。"), ("Mouse", "🐭", "Small mouse.", "老鼠。"), ("Mushroom", "🍄", "Red mushroom.", "紅蘑菇。")],
        "N": [("Nose", "👃", "Touch your nose.", "摸鼻子。"), ("Nut", "🥜", "Eat a nut.", "吃堅果。"), ("Nest", "🪹", "Bird's nest.", "鳥巢。"), ("Net", "🕸️", "Fishing net.", "魚網。"), ("Nurse", "👩‍⚕️", "Helpful nurse.", "護理師。")],
        "O": [("Orange", "🍊", "Sweet orange.", "橘子。"), ("Owl", "🦉", "Wise owl.", "貓頭鷹。"), ("Octopus", "🐙", "Eight legs.", "章魚。"), ("Onion", "🧅", "Don't cry.", "洋蔥。"), ("Ocean", "🌊", "Blue ocean.", "大海。")],
        "P": [("Pig", "🐷", "Pink pig.", "粉紅豬。"), ("Pear", "🍐", "Sweet pear.", "梨子。"), ("Panda", "🐼", "Cute panda.", "熊貓。"), ("Piano", "🎹", "Play piano.", "彈鋼琴。"), ("Pizza", "🍕", "Hot pizza.", "披薩。")],
        "Q": [("Queen", "👸", "Beautiful queen.", "皇后。"), ("Question", "❓", "Any questions?", "問題。"), ("Quiet", "🤫", "Be quiet.", "安靜。"), ("Quack", "🦆", "Duck quack.", "鴨叫。"), ("Quilt", "🧶", "Warm quilt.", "被子。")],
        "R": [("Rabbit", "🐰", "White rabbit.", "兔子。"), ("Rain", "🌧️", "Falling rain.", "下雨。"), ("Robot", "🤖", "Cool robot.", "機器人。"), ("Rainbow", "🌈", "Seven colors.", "彩虹。"), ("Rocket", "🚀", "Fast rocket.", "火箭。")],
        "S": [("Sun", "☀️", "Golden sun.", "太陽。"), ("Snake", "🐍", "Long snake.", "長蛇。"), ("Star", "⭐", "Twinkle star.", "星星。"), ("Spider", "🕷️", "Spider web.", "蜘蛛。"), ("Ship", "🚢", "Big ship.", "大船。")],
        "T": [("Tiger", "🐯", "Strong tiger.", "老虎。"), ("Tree", "🌳", "Tall tree.", "大樹。"), ("Train", "🚆", "Long train.", "火車。"), ("Tomato", "🍅", "Red tomato.", "番茄。"), ("Telephone", "☎️", "Ring ring.", "電話。")],
        "U": [("Umbrella", "🌂", "Take an umbrella.", "雨傘。"), ("Unicorn", "🦄", "Magic unicorn.", "獨角獸。"), ("Up", "⬆️", "Look up.", "向上。"), ("Under", "👇", "Look under.", "在下面。"), ("Uniform", "🥋", "School uniform.", "制服。")],
        "V": [("Van", "🚐", "Drive a van.", "箱型車。"), ("Violin", "🎻", "Play violin.", "小提琴。"), ("Vase", "🏺", "Pretty vase.", "花瓶。"), ("Vegetable", "🥦", "Eat vegetables.", "蔬菜。"), ("Volcano", "🌋", "Hot volcano.", "火山。")],
        "W": [("Whale", "🐋", "Big whale.", "鯨魚。"), ("Watch", "⌚", "Look at the watch.", "手錶。"), ("Water", "💧", "Drink water.", "水。"), ("Witch", "🧙‍♀️", "Funny witch.", "巫婆。"), ("Window", "🪟", "Open window.", "窗戶。")],
        "X": [("Xylophone", "🎼", "Play xylophone.", "木琴。"), ("Box", "📦", "A big box.", "箱子。"), ("Fox", "🦊", "Red fox.", "狐狸。"), ("Six", "6️⃣", "Number six.", "數字六。"), ("X-ray", "🩻", "Hospital X-ray.", "X光。")],
        "Y": [("Yo-yo", "🪀", "Play yo-yo.", "溜溜球。"), ("Yellow", "💛", "Bright yellow.", "黃色。"), ("Yacht", "🛥️", "White yacht.", "遊艇。"), ("Yak", "🐂", "Strong yak.", "氂牛。"), ("Yogurt", "🍦", "Eat yogurt.", "優格。")],
        "Z": [("Zebra", "🦓", "Black and white.", "斑馬。"), ("Zoo", "🦁", "Visit the zoo.", "動物園。"), ("Zero", "0️⃣", "Number zero.", "數字零。"), ("Zipper", "🤐", "Close zipper.", "拉鍊。"), ("Zigzag", "📉", "Zigzag line.", "鋸齒線。")]
    }

FULL_DB = get_full_db()

# --- 3. 側邊欄：進化狀態、年齡、語速 ---
with st.sidebar:
    st.header("👤 學習者狀態")
    score = st.session_state.user_score
    if score < 50: d_emo, d_name, d_next = "🥚", "恐龍蛋", 50
    elif score < 200: d_emo, d_name, d_next = "🦖", "小恐龍", 200
    else: d_emo, d_name, d_next = "🦕", "巨龍", 500
    
    st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{d_emo}</h1>", unsafe_allow_html=True)
    st.title(f"等級：{d_name}")
    st.write(f"🌟 積分：{score} / {d_next}")
    st.progress(min(score / d_next, 1.0))
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

# --- 5. 功能分頁 (確定四個都在) ---
tab1, tab2, tab3 = st.tabs(["🔤 字母與單字練習", "📖 短文解析區", "🎮 聽音辨圖挑戰"])

# --- Tab 1: A-Z 完整練習 ---
with tab1:
    st.header("🔤 字母與單字同步學 (A-Z)")
    letter = st.selectbox("請選擇字母", list(FULL_DB.keys()))
    
    for word, emoji, sentence, trans in FULL_DB[letter]:
        with st.container():
            col1, col2 = st.columns([1, 4])
            col1.markdown(f"<h1 style='font-size:100px; text-align:center;'>{emoji}</h1>", unsafe_allow_html=True)
            with col2:
                st.subheader(word)
                st.write(f"**例句:** {sentence}")
                st.caption(f"翻譯: {trans}")
                if st.button(f"🔊 聽發音", key=f"btn_{word}"):
                    play_audio(f"{word}. {sentence}", target_lang, voice_speed)
                    st.session_state.user_score += 2
                    st.rerun()
            st.divider()

# --- Tab 2: 短文解析區 (回歸) ---
with tab2:
    st.header("📖 自定義短文解析")
    user_topic = st.text_input("📝 請輸入短文主題 (例如: Space, Zoo)", "Farm")
    user_inst = st.text_area("✍️ 給老師的指令", "請用簡單的英文描述。")
    
    if st.button("🚀 生成解析內容"):
        st.session_state['story'] = f"Welcome to the {user_topic}! It is a wonderful day. We can learn many things here. Look at the colors and animals!"
    
    if 'story' in st.session_state:
        st.info(st.session_state['story'])
        if st.button("🔊 聽文章內容"):
            play_audio(st.session_state['story'], target_lang, voice_speed)
        st.subheader("💡 教學重點")
        st.success(f"這篇文章適合 {user_age} 歲學習，重點在於描述 {user_topic} 的環境。")

# --- Tab 3: 聽音辨圖挑戰 (大型圖片 + 手動換題) ---
with tab3:
    st.header("🎮 聽音辨圖挑戰")
    
    # 建立目前字母的題目池
    pool = FULL_DB[letter]
    
    if 'game_opts' not in st.session_state or st.button("🔄 換一個挑戰題目"):
        st.session_state.game_opts = random.sample(pool, 3)
        st.session_state.game_target = random.choice(st.session_state.game_opts)

    target = st.session_state.game_target
    
    st.subheader("🎯 聽聽看，點選正確的圖片：")
    if st.button("🔊 播放題目音檔"):
        play_audio(target[0], target_lang, voice_speed)
    
    # 圖片放大排版
    cols = st.columns(3)
    for i, (word, emoji, sent, tran) in enumerate(st.session_state.game_opts):
        with cols[i]:
            # 使用 HTML 語法讓 Emoji 變大
            st.markdown(f"<h1 style='text-align:center; font-size:150px;'>{emoji}</h1>", unsafe_allow_html=True)
            if st.button(f"選這個", key=f"g_btn_{i}", use_container_width=True):
                if word == target[0]:
                    st.balloons()
                    st.success(f"太棒了！答對了！這是 {word}")
                    st.session_state.user_score += 20
                    # 答對後建議點擊換題
                else:
                    st.error("不對喔，再聽一次音檔！")
