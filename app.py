import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# --- [CONFIG] ตั้งค่าหน้าจอระดับโปร (Wide Mode) ---
st.set_page_config(
    page_title="XAUUSD AI ANALYZER PRO", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- [STYLE] ตกแต่งอินเตอร์เฟซความคมชัดสูง (High Contrast & Clean) ---
st.markdown("""
    <style>
    .stApp { 
        background-color: #090c0f; 
        color: #ffffff; 
        font-family: 'Inter', 'Helvetica Neue', sans-serif; 
    }
    
    div[data-testid="stColumn"] { 
        background-color: #131722; 
        padding: 26px; 
        border-radius: 12px; 
        border: 1px solid #2a2e39;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    
    p, span, label, .stMarkdown {
        font-size: 16px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    button[data-baseweb="tab"] {
        color: #b3b9c1 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffcc00 !important;
        border-bottom-color: #ffcc00 !important;
    }
    
    .stButton>button { 
        width: 100%; 
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
        color: #ffffff !important; 
        font-weight: 700 !important;
        font-size: 18px !important;
        border-radius: 8px; 
        border: none;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); 
        box-shadow: 0 0 25px rgba(241, 196, 15, 0.8);
        transform: translateY(-2px);
    }
    
    .api-direct-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #2ea44f 0%, #238636 100%);
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        text-decoration: none !important;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }
    .api-direct-btn:hover {
        background: linear-gradient(135deg, #3fb950 0%, #2ea44f 100%);
        box-shadow: 0 0 20px rgba(63, 185, 80, 0.6);
        transform: translateY(-2px);
    }
    
    .strategy-box {
        background-color: #1c2030;
        padding: 22px;
        border-radius: 8px;
        margin-top: 10px;
        border-top: 1px solid #3d4457;
        border-right: 1px solid #3d4457;
        border-bottom: 1px solid #3d4457;
    }
    
    .signal-box {
        background-color: #241c0c;
        border: 2px solid #f39c12;
        padding: 20px;
        border-radius: 10px;
        margin-top: 10px;
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.2);
    }

    /* กล่องสัญญาณระดับความรุนแรงของข่าวสารพร้อมบอกวัน-เวลา */
    .impact-red {
        background-color: #2c1516; border-left: 6px solid #ff4a4a; padding: 14px; border-radius: 6px; margin-bottom: 12px;
    }
    .impact-orange {
        background-color: #2c1e15; border-left: 6px solid #ff9f43; padding: 14px; border-radius: 6px; margin-bottom: 12px;
    }
    .time-tag {
        background-color: #451a1c; color: #ff9496 !important; padding: 3px 8px; border-radius: 4px; font-size: 13px !important; font-weight: bold;
    }
    .time-tag-orange {
        background-color: #452b1a; color: #ffb87d !important; padding: 3px 8px; border-radius: 4px; font-size: 13px !important; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- [DATA] คลังมหากาพย์ 5 สูตรกลยุทธ์ (อัปเดตระบบคัดกรองสัญญาณใน SIGNAL) ---
PROMPTS = {
    "1. MTF Analysis 📊": """คุณคือนักวิเคราะห์ Forex ระดับมืออาชีพที่เชี่ยวชาญ XAUUSD (Gold Spot) 
โปรดวิเคราะห์โครงสร้างภาพกราฟที่แนบมาแบบ Multi-Timeframe (H4, H1, M15, M5) โดยละเอียดดังนี้:
- Trend Direction & Market Structure
- Key Level (แนวรับ/แนวต้านสำคัญ)
- Overall Bias (หน้าเทรดที่ได้เปรียบ)""",

    "2. Price Action 🕯️": """คุณคือ Price Action Trader ผู้เชี่ยวชาญ XAUUSD 
โปรดค้นหาจุดเข้าเทรดจากรูปกราฟโดยละเอียด:
- Identify Key Zones (Supply/Demand/FVG ที่เด่นชัด)
- Candlestick Pattern & Entry Trigger
- Risk Management (SL, TP และ R:R)""",

    "3. Smart Money Concepts 🧠": """คุณคือ ICT/SMC Trader ระดับเซียน 
โปรดสแกนหา Liquidity และเม็ดเงินสถาบันจากรูปกราฟ:
- Market Structure Shift (MSS) / BOS
- Order Block (OB) ที่ยังไม่ถูกใช้ และ Fair Value Gap (FVG)
- Liquidity Pool (BSL / SSL) ที่ตลาดมีโอกาสวิ่งไปล่า""",

    "4. Indicator Confluence 🎛️": """คุณคือนักวิเคราะห์สาย Confluence 
โปรดประเมินสัญญาณจากสิ่งเหล่านี้ที่ปรากฏในรูปภาพ:
- แนวรับแนวต้านเชิงจิตวิทยา
- การอ่านค่า Indicator (เช่น EMA, RSI, MACD หรือปริมาณซื้อขาย)
- สรุปคะแนนความน่าจะเป็น (Confluence Score 1-10)""",

    "5. Pre-Execute Checklist ✓": """จงสวมบทบาทเป็นผู้ควบคุมความเสี่ยงก่อนกดเปิดออเดอร์ทองคำ 
ตรวจสอบเงื่อนไขทั้งหมดจากข้อมูลและรูปกราฟ แล้วสรุปเป็น Checklist 7 ข้อ:
1. เทรดตามเทรนใหญ่? 2. อยู่ในโซนได้เปรียบ? 3. มีสัญญาณแท่งเทียนกลับตัว? 4. RSI ไม่ Overbought/Oversold เกินไป? 5. R:R คุ้มค่า (>1:2)? 6. ปลอดภัยจากข่าวใหญ่? 7. มี Stop Loss ชัดเจน?
[สรุปคำตัดสินสุดท้าย]: ผ่าน 5/7 ข้อขึ้นไปให้พิมพ์ 'GO 🔥' | ต่ำกว่านั้นให้พิมพ์ 'WAIT ⏳'""",

    "🎯 FINAL TRADING SIGNAL": """จากรูปกราฟและเงื่อนไขทั้งหมด จงประเมินความคุ้มค่าและความปลอดภัยตาม Checklist อย่างเคร่งครัด:

[กรณีที่ 1: เงื่อนไขไม่ผ่าน หรือผ่านต่ำกว่า 5 ข้อ จาก Checklist]
ให้พิมพ์ข้อความคำเตือนนี้ตัวโตๆ เด่นชัดไว้ด้านบนสุดทันที:
"🚨 [คำสั่งระบบ]: NO TRADE / WAIT ⏳ (สัญญาณไม่สมบูรณ์ เงื่อนไขไม่ครบถ้วน)"
จากนั้นระบุเหตุผลสั้นๆ เป็นข้อๆ ว่าข้อไหนที่ไม่ผ่าน (เช่น โครงสร้างกราฟขัดแย้ง, ระยะ SL ไกลเกินไป, มีข่าวใหญ่ USD จ่อออก) และ "ไม่ต้องระบุ" จุดเปิดออเดอร์ ENTRY/TP/SL เพื่อป้องกันความสับสน

[กรณีที่ 2: เงื่อนไขผ่านครบถ้วน (5/7 ข้อขึ้นไป) และกราฟได้เปรียบสูง]
ให้พิมพ์ข้อความคำตัดสิน: "🔥 [คำสั่งระบบ]: GO SIGNALS (เงื่อนไขครบถ้วน)"
แล้วแจกแจงแผนตั้งรับออเดอร์อย่างละเอียดตามหัวข้อนี้:
- DIRECTION: (BUY / SELL)
- ENTRY ZONE: (ระบุกรอบหรือตัวเลขราคาเข้าเทรด)
- TAKE PROFIT (TP): (ระบุเป้าหมายทำกำไร)
- STOP LOSS (SL): (ระบุจุดตัดขาดทุนที่ห้ามยอมแพ้)

โปรดตอบเป็นภาษาไทยที่อ่านง่าย ชัดเจน ตรงไปตรงมา เพื่อให้นักเทรดตัดสินใจได้ทันทีโดยไม่สับสน"""
}

# --- [HEADER] ส่วนหัวแดชบอร์ด ---
st.markdown("<h1 style='text-align: center; color: #ffcc00; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 5px; font-size: 32px;'>📊 XAUUSD AI ALL-IN-ONE DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #b3b9c1; font-size: 16px; margin-bottom: 30px; font-weight: 500;'>ระบบประมวลผลวิเคราะห์กราฟทองคำทีเดียว 5 สูตรกลยุทธ์ เพื่อความแม่นยำขั้นสูงสุด</p>", unsafe_allow_html=True)

# ช่องใส่ API Key
api_key = st.text_input("🔑 ยืนยันสิทธิ์ใช้งาน: วาง Gemini API Key ของคุณที่นี่เพื่อรันระบบ", type="password")
st.markdown("<br>", unsafe_allow_html=True)

# --- [LAYOUT] แบ่งอัตราส่วนหน้าต่างแอปพลิเคชัน ---
col_left, col_right = st.columns([1.2, 1])


# ==================== 📈 ฝั่งซ้าย: LIVE CHART & XAUUSD REAL-TIME NEWS HUB ====================
with col_left:
    tab_left_chart, tab_left_news = st.tabs(["📈 กราฟเทคนิคอลสด (Clean)", "⚠️ ตรวจสอบข่าวกล่องแดง Real-Time (USD ล็อกเป้า)"])
    
    # 1. แท็บแสดงกราฟเทคนิคอลเปล่าแบบออริจินัล
    with tab_left_chart:
        st.markdown("<h4 style='color: #58a6ff; font-weight: 700; margin-bottom: 10px;'>แพลตฟอร์มกราฟสดทองคำ (Original Clean Chart)</h4>", unsafe_allow_html=True)
        tradingview_html = """
        <div class="tradingview-widget-container" style="height:530px; margin-bottom: 20px;">
          <div id="tradingview_gold_clean" style="height:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({
            "autosize": true,
            "symbol": "OANDA:XAUUSD",
            "interval": "15",
            "timezone": "Asia/Bangkok",
            "theme": "dark",
            "style": "1",
            "locale": "th",
            "toolbar_bg": "#0c1014",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_gold_clean",
            "studies": []
          });
          </script>
        </div>
        """
        components.html(tradingview_html, height=530)
        
    # 2. แท็บปฏิทินข่าวสารเศรษฐกิจแบบ Real-Time เจาะจงเฉพาะสกุลเงินดอลลาร์ (USD) ที่มีผลโดยตรงกับทองคำ
    with tab_left_news:
        st.markdown("<h4 style='color: #ff5252; font-weight: 700; margin-bottom: 5px;'>🚨 ตารางเช็คข่าวแบบ Real-Time (USD ล็อกเป้าเทรดทอง)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #b3b9c1; font-size: 14px; margin-bottom: 15px;'>ตัวเลขเศรษฐกิจของสหรัฐฯ จะแสดงค่าออกมาทันทีแบบวินาทีต่อวินาทีเมื่อถึงเวลารายงานผล (ไม่ต้องกดรีเฟรชหน้าเว็บ)</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="impact-red">
            <span class="time-tag">📅 ทุกกลางเดือน / ศุกร์แรก | ⏰ 19:30 น. (เวลาไทย)</span><br><br>
            <strong style="color: #ff4a4a; font-size: 16px;">🔴 ข่าวรุนแรงสูงสุด (High Impact) - ตัวเลข CPI / Non-Farm Payrolls / FOMC</strong><br>
            <span style="color: #ffffff; font-size: 14px;"><b>ผลกระทบทองคำ:</b> มีแรงซื้อ/ขายทะลักเข้ามามหาศาล 800-2,000 จุดในพริบตา นิยมเคลียร์พอร์ตหรือหลบข่าวก่อนเปิดออเดอร์</span>
        </div>
        
        <div class="impact-orange">
            <span class="time-tag-orange">📅 รายสัปดาห์ / ทุกวันพฤหัสบดี | ⏰ 19:30 น. (เวลาไทย)</span><br><br>
            <strong style="color: #ff9f43; font-size: 16px;">🟠 ข่าวรุนแรงปานกลาง (Medium Impact) - Unemployment Claims / Retail Sales</strong><br>
            <span style="color: #ffffff; font-size: 14px;"><b>ผลกระทบทองคำ:</b> เกิดอาการสวิงหลอกพุ่งไปเก็บ Liquidity (สะบัดกิน SL) แล้ววิ่งกลับมาตามทิศทางเดิม</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: #2a2e39; margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<span style='color: #ffcc00; font-weight: bold;'>⚡ ปฏิทินสตรีมมิ่งข่าวสด Real-Time (ล็อกเฉพาะข่าวสาร USD ที่ขับเคลื่อน XAUUSD):</span>", unsafe_allow_html=True)
        
        investing_realtime_calendar = """
        <iframe src="https://sslecal2.investing.com?eco_border_color=2a2e39&columns=time,flag,currency,importance,actual,forecast,previous&category=_employment,_economicActivity,_inflation,_credit,_centralBanks,_confidenceIndex,_balance,_bonds&importance=2,3&currencies=5&calType=week&timeZone=28&lang=1" 
                width="100%" height="320" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0" style="background-color:#131722; border-radius:8px; border:1px solid #2a2e39;"></iframe>
        """
        components.html(investing_realtime_calendar, height=330)


# ==================== 🤖 ฝั่งขวา: ALL-IN-ONE AI PANEL (TABS CONTROL) ====================
with col_right:
    st.markdown("<h3 style='color: #bc8cff; margin-top: 0; font-size: 22px; font-weight: 700;'>🤖 ศูนย์ประมวลผล 5 สูตรอัจฉริยะพร้อมกัน</h3>", unsafe_allow_html=True)
    
    st.markdown('<a href="https://aistudio.google.com/" target="_blank" class="api-direct-btn">🔑 กดตรงนี้เพื่อไปรับ Gemini API Key ฟรี (Google AI Studio) ↗️</a>', unsafe_allow_html=True)
    
    uploaded_charts = st.file_uploader(
        "ลากไฟล์รูปกราฟเทรดทั้งหมดมาวางพร้อมกันตรงนี้", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    img_list = []
    if uploaded_charts:
        for chart in uploaded_charts:
            img_list.append(Image.open(chart))
            
    run_button = st.button("🚀 ยิงพลัง AI วิเคราะห์พร้อมกัน 5 สูตรกลยุทธ์", type="primary")
    
    st.markdown("<hr style='border-color: #2a2e39; margin: 15px 0;'>", unsafe_allow_html=True)
    
    t_signal, t_mtf, t_pa, t_smc, t_ind, t_check, t_images = st.tabs([
        "🎯 SIGNAL", "📊 MTF", "🕯️ Price Action", "🧠 SMC/ICT", "🎛️ Indicator", "✓ Checklist", "📸 รูปภาพ"
    ])
    
    status_container = st.empty()
    
    if run_button:
        if not api_key:
            st.error("❌ ไม่สามารถรันระบบได้: กรุณากรอก Gemini API Key ที่แถบด้านบนสุดก่อนครับ")
        elif not uploaded_charts:
            st.error("❌ ไม่พบรูปภาพ: กรุณาอัปโหลดสกรีนช็อตกราฟทองคำของคุณก่อนครับ")
        else:
            st.session_state["ai_responses"] = {}
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                for title, prompt_text in PROMPTS.items():
                    status_container.markdown(f"⚡ **กำลังวิเคราะห์เชิงลึก:** {title} ...")
                    content_to_send = [prompt_text] + img_list
                    response = model.generate_content(content_to_send)
                    st.session_state["ai_responses"][title] = response.text
                    
                status_container.success("✅ ประมวลผลสัญญาณเชิงลึกครบทั้ง 5 สูตรเรียบร้อยแล้ว!")
            except Exception as e:
                status_container.empty()
                st.error(f"เกิดข้อผิดพลาดในการส่งคำสั่งประมวลผล: {e}")
                
    has_data = "ai_responses" in st.session_state and st.session_state["ai_responses"]
    
    with t_signal:
        if has_data and "🎯 FINAL TRADING SIGNAL" in st.session_state["ai_responses"]:
            st.markdown("""
                <div class='signal-box'>
                    <h3 style='color: #f39c12; margin-top: 0; font-weight: 800; font-size: 20px; border-bottom: 2px solid #f39c12; padding-bottom: 5px;'>⚡ แผนประเมินออเดอร์ระบบควบรวม (AI Final Execution)</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["🎯 FINAL TRADING SIGNAL"])
        else:
            st.info("💡 รอสัญญาณ: อัปโหลดกราฟแล้วกดรันระบบ เพื่อประเมินสิทธิ์การเปิดออเดอร์ตามเงื่อนไขความปลอดภัย")

    with t_mtf:
        if has_data and "1. MTF Analysis 📊" in st.session_state["ai_responses"]:
            st.markdown("<div class='strategy-box'><strong style='color: #ffcc00;'>บทวิเคราะห์โครงสร้างภาพใหญ่ Multi-Timeframe</strong></div>", unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["1. MTF Analysis 📊"])
        else:
            st.write("ไม่มีข้อมูลการวิเคราะห์")

    with t_pa:
        if has_data and "2. Price Action 🕯️" in st.session_state["ai_responses"]:
            st.markdown("<div class='strategy-box'><strong style='color: #ffcc00;'>การอ่านสัญญาณแท่งเทียนและโซนสำคัญ</strong></div>", unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["2. Price Action 🕯️"])
        else:
            st.write("ไม่มีข้อมูลการวิเคราะห์")

    with t_smc:
        if has_data and "3. Smart Money Concepts 🧠" in st.session_state["ai_responses"]:
            st.markdown("<div class='strategy-box'><strong style='color: #ffcc00;'>การล่าสภาพคล่อง Liquidity & Order Block</strong></div>", unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["3. Smart Money Concepts 🧠"])
        else:
            st.write("ไม่มีข้อมูลการวิเคราะห์")

    with t_ind:
        if has_data and "4. Indicator Confluence 🎛️" in st.session_state["ai_responses"]:
            st.markdown("<div class='strategy-box'><strong style='color: #ffcc00;'>สัญญาณยืนยันร่วมจากอินดิเคเตอร์และคะแนนความน่าจะเป็น</strong></div>", unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["4. Indicator Confluence 🎛️"])
        else:
            st.write("ไม่มีข้อมูลการวิเคราะห์")

    with t_check:
        if has_data and "5. Pre-Execute Checklist ✓" in st.session_state["ai_responses"]:
            st.markdown("<div class='strategy-box'><strong style='color: #ffcc00;'>ระบบตรวจสอบความพร้อมก่อนสั่งลุย</strong></div>", unsafe_allow_html=True)
            st.markdown(st.session_state["ai_responses"]["5. Pre-Execute Checklist ✓"])
        else:
            st.write("ไม่มีข้อมูลการวิเคราะห์")
            
    with t_images:
        if uploaded_charts:
            for i, chart in enumerate(uploaded_charts):
                st.image(Image.open(chart), caption=f"📸 รูปภาพสแกนกราฟเทรดใบที่ {i+1}", use_container_width=True)
        else:
            st.write("ยังไม่มีการอัปโหลดรูปภาพกราฟเข้ามาในระบบ")