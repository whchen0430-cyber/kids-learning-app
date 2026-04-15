import streamlit as st
from gtts import gTTS
import base64

# APP 標題與視覺設定
st.set_page_config(page_title="小天才語文機器人", page_icon="🤖")
st.title("🌟 小天才語文學習機器人")

# 側邊欄：設定功能
with st.sidebar:
    st.header("⚙️ 設定中心")
    lang = st.radio("選擇目標語言", ["英文", "日文"])
    age = st.select_slider("選擇孩子年齡", options=["4-6", "7-8", "9-10", "11-12"])
    speed = st.slider("語速調整", 0.5, 1.0, 0.8)
    st.info("目前的語速已設定為 0.8 倍，最適合學習！")

# 主介面：輸入區
topic = st.text_input("你想讓孩子學什麼主題？（例如：水果、天氣、動物）", "水果")

if st.button("✨ 點我自動生成教材"):
    # 這裡未來可以串接 Google Gemini API
    # 暫時先用預設模板模擬機器人生成
    st.subheader(f"📚 {age} 歲 - {topic} 學習單")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🔤 對話內容")
        content = f"A: Look! Here is a {topic}.\nB: It looks yummy!\nA: Let's share it together."
        if lang == "日文":
            content = f"A: 見て！ここに {topic} があるよ。\nB: 美味しそうだね！\nA: 一緒に食べよう。"
        
        st.info(content)
        
    with col2:
        st.write("### 🏮 中文翻譯")
        st.write(f"A: 看！這裡有一個{topic}。\nB: 看起來很好吃！\nA: 我們一起分享吧。")

    # 語音生成邏輯
    target_lang = 'en' if lang == "英文" else 'ja'
    tts = gTTS(text=content.replace("A:", "").replace("B:", ""), lang=target_lang, slow=(speed < 1.0))
    tts.save("temp.mp3")
    
    # 在網頁顯示播放器
    audio_file = open("temp.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")
    st.success("🔊 語音檔已生成，點擊上方播放器聽聽看！")

# 遊戲預留區
st.divider()
st.write("🎮 **互動小遊戲預演**：請點擊正確數量的蘋果 (製作中...)")
st.button("🍎") # 簡單展示
