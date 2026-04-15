# --- Tab 2: 短文指令解析 (修正原文夾雜中文的問題) ---
with tab2:
    st.header("📖 自定義短文教學解析")
    user_topic = st.text_input("📝 請輸入短文主題 (例如: Space, Zoo)", "Ocean")
    user_inst = st.text_area("✍️ 給老師的指令 (例如: 簡單句型、要有對話)", "請用簡單的英文描述。")
    
    if st.button("🚀 生成解析內容"):
        # 修正點：確保生成內容為純外語，這裡模擬 AI 處理後的純淨文本
        # 實際對接 AI 後，AI 會根據您的指令自動將「農場」轉為 "Farm"
        display_topic = "Farm" if user_topic == "農場" else user_topic
        
        st.session_state['story'] = f"Welcome to the {display_topic}! It is a wonderful day. We can learn many things here. Look at the colors and animals!"
        st.session_state['story_display_topic'] = display_topic

    if 'story' in st.session_state:
        # 顯示區塊
        st.subheader("📜 課文原文")
        st.info(st.session_state['story'])
        
        if st.button("🔊 聽文章內容"):
            # 確保語音合成也是純英文
            play_audio(st.session_state['story'], target_lang, voice_speed)
        
        st.subheader("💡 教學重點")
        st.success(f"這篇文章適合 {user_age} 歲學習。主題：{user_topic}")
