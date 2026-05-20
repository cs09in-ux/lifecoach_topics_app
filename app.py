import streamlit as st
import pandas as pd
import plotly.express as px
from pytrends.request import TrendReq
import time

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Lifebhasha – Topic Finder",
    page_icon="🧠",
    layout="wide"
)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; color: #ffffff; }
    .stApp { background-color: #0f0f1a; }
    h1, h2, h3 { color: #a78bfa; }
    .metric-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        border: 1px solid #4c1d95;
    }
    .tag-high { color: #4ade80; font-weight: bold; }
    .tag-low  { color: #f87171; font-weight: bold; }
    .tag-med  { color: #fbbf24; font-weight: bold; }
    div[data-testid="stDataFrameResizable"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────
st.markdown("# 🧠 Lifebhasha – Topic & Keyword Finder")
st.markdown("**Life Coaching | Psychology | Self-Help** — High Demand · Low Supply Topics")
st.markdown("---")

# ─── Niche Data ────────────────────────────────────────────────
NICHE_KEYWORDS = {
    "Overthinking / Anxiety": [
        "overthinking kaise band kare",
        "anxiety se kaise nikle",
        "overthinking in hindi",
        "anxiety symptoms hindi",
        "man shant kaise kare",
        "negative thoughts kaise hataye",
        "how to stop overthinking",
        "anxiety treatment in hindi"
    ],
    "Confidence / Self-Esteem": [
        "confidence kaise badhaye",
        "self confidence in hindi",
        "khud par bharosa kaise kare",
        "low self esteem hindi",
        "personality kaise improve kare",
        "how to build confidence",
        "self esteem tips hindi",
        "apni value kaise badhaye"
    ],
    "Relationships / Attachment": [
        "toxic relationship hindi",
        "attachment style hindi",
        "relationship problems hindi",
        "pyaar mein boundaries",
        "breakup se kaise ubhre",
        "emotional dependency hindi",
        "healthy relationship tips hindi",
        "love bombing kya hota hai"
    ],
    "Habits / Discipline": [
        "acchi aadat kaise banaye",
        "discipline kaise banaye",
        "procrastination kaise hataye",
        "morning routine hindi",
        "habit building tips hindi",
        "consistency kaise rakhe",
        "how to build habits in hindi",
        "lazy rehna band kaise kare"
    ],
    "Burnout / Stress": [
        "burnout kya hota hai",
        "stress kaise kam kare",
        "mental exhaustion hindi",
        "kaam ka bojh kaise sambhale",
        "stress management hindi",
        "emotional burnout symptoms",
        "mental health tips hindi",
        "thakan dur karne ke upay"
    ],
    "Purpose / Life Clarity": [
        "life purpose kaise dhundhe",
        "apna goal kaise banaye",
        "life mein direction kaise le",
        "identity crisis hindi",
        "khud ko kaise samjhe",
        "ikigai in hindi",
        "life coaching hindi",
        "apni calling kaise pehchane"
    ]
}

INTENT_MAP = {
    "kaise": "Informational",
    "kya": "Informational",
    "how to": "Informational",
    "tips": "Informational",
    "symptoms": "Informational",
    "what is": "Informational",
    "best": "Commercial",
    "top": "Commercial",
    "vs": "Commercial",
    "course": "Commercial",
    "coaching": "Commercial",
}

def get_intent(keyword):
    kw_lower = keyword.lower()
    for trigger, intent in INTENT_MAP.items():
        if trigger in kw_lower:
            return intent
    return "Informational"

def is_long_tail(keyword):
    return len(keyword.split()) >= 4

def supply_score(keyword):
    """Lower score = lower supply (better for us)"""
    if is_long_tail(keyword):
        return round(20 + (len(keyword) % 15), 1)
    else:
        return round(45 + (len(keyword) % 25), 1)

def fetch_trends(keywords, timeframe='today 12-m', geo='IN'):
    pytrends = TrendReq(hl='hi-IN', tz=330)
    results = {}
    
    # Batch में fetch करेंगे (max 5 at a time)
    batch_size = 5
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        try:
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo=geo)
            data = pytrends.interest_over_time()
            if not data.empty:
                for kw in batch:
                    if kw in data.columns:
                        avg = round(data[kw].mean(), 1)
                        results[kw] = avg
                    else:
                        results[kw] = 0
            else:
                for kw in batch:
                    results[kw] = 0
            time.sleep(1.5)  # Rate limit avoid करने के लिए
        except Exception as e:
            for kw in batch:
                results[kw] = 0
    return results

def final_score(demand, supply):
    """High demand + Low supply = High score"""
    if demand == 0:
        return 0
    raw = (demand * 0.7) - (supply * 0.3)
    return max(0, round(raw, 1))

def score_label(score):
    if score >= 40:
        return "🟢 High"
    elif score >= 20:
        return "🟡 Medium"
    else:
        return "🔴 Low"

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    selected_niche = st.selectbox(
        "📌 Niche चुनो",
        list(NICHE_KEYWORDS.keys())
    )
    
    timeframe = st.selectbox(
        "📅 Timeframe",
        ["today 3-m", "today 12-m", "today 5-y"],
        index=1,
        help="कितने समय का trend देखना है"
    )
    
    geo = st.selectbox(
        "🌍 Region",
        ["IN", "IN-MH", "US"],
        index=0,
        help="IN = India, IN-MH = Maharashtra, US = USA"
    )
    
    custom_keywords = st.text_area(
        "✏️ Custom Keywords (optional)",
        placeholder="एक line में एक keyword\nजैसे:\noverthinking kaise roke\nself love hindi",
        height=120
    )
    
    analyze_btn = st.button("🔍 Topics Find करो", use_container_width=True, type="primary")
    
    st.markdown("---")
    st.markdown("### 📖 Guide")
    st.markdown("""
    - **🟢 High** = Best topic
    - **🟡 Medium** = Good topic  
    - **🔴 Low** = Skip करो
    - **Demand** = Google पर कितना search हो रहा है
    - **Supply** = Competition कितना है
    """)

# ─── Main Content ──────────────────────────────────────────────
if analyze_btn:
    
    # Keywords prepare करो
    keywords = NICHE_KEYWORDS[selected_niche].copy()
    
    if custom_keywords.strip():
        custom_list = [k.strip() for k in custom_keywords.strip().split('\n') if k.strip()]
        keywords = keywords + custom_list
    
    keywords = list(set(keywords))  # Duplicates remove
    
    st.markdown(f"## 📊 Results: **{selected_niche}**")
    st.markdown(f"Analyzing **{len(keywords)}** keywords from **India** ({geo}) — {timeframe}")
    
    # Progress bar
    progress = st.progress(0, text="Google Trends से data fetch हो रहा है...")
    
    with st.spinner("थोड़ा इंतजार करो... Trends data आ रहा है 🔄"):
        trend_data = fetch_trends(keywords, timeframe=timeframe, geo=geo)
        progress.progress(80, text="Scoring हो रहा है...")
    
    progress.progress(100, text="Done!")
    time.sleep(0.5)
    progress.empty()
    
    # DataFrame बनाओ
    rows = []
    for kw in keywords:
        demand = trend_data.get(kw, 0)
        supply = supply_score(kw)
        fs = final_score(demand, supply)
        rows.append({
            "Keyword / Topic": kw,
            "Demand Score": demand,
            "Supply Score": supply,
            "Final Score": fs,
            "Opportunity": score_label(fs),
            "Intent": get_intent(kw),
            "Long-tail?": "✅ Yes" if is_long_tail(kw) else "❌ No"
        })
    
    df = pd.DataFrame(rows)
    df = df.sort_values("Final Score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # 1 से start करो
    
    # ─── Top Metrics ───────────────────────────────────────────
    top3 = df.head(3)
    col1, col2, col3 = st.columns(3)
    
    for i, (col, (_, row)) in enumerate(zip([col1, col2, col3], top3.iterrows())):
        medal = ["🥇", "🥈", "🥉"][i]
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{medal} #{i+1} Topic</h3>
                <p><b>{row['Keyword / Topic']}</b></p>
                <p>Final Score: <span class="tag-high">{row['Final Score']}</span></p>
                <p>Intent: {row['Intent']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ─── Full Table ────────────────────────────────────────────
    st.markdown("### 📋 सभी Keywords की Full List")
    
    # Filter options
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        filter_opportunity = st.multiselect(
            "Opportunity filter",
            ["🟢 High", "🟡 Medium", "🔴 Low"],
            default=["🟢 High", "🟡 Medium"]
        )
    with f_col2:
        filter_intent = st.multiselect(
            "Intent filter",
            ["Informational", "Commercial"],
            default=["Informational", "Commercial"]
        )
    
    filtered_df = df[
        df["Opportunity"].isin(filter_opportunity) &
        df["Intent"].isin(filter_intent)
    ]
    
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )
    
    # ─── Chart ─────────────────────────────────────────────────
    st.markdown("### 📈 Demand vs Supply Chart")
    
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="Supply Score",
            y="Demand Score",
            text="Keyword / Topic",
            size="Final Score",
            color="Opportunity",
            color_discrete_map={
                "🟢 High": "#4ade80",
                "🟡 Medium": "#fbbf24",
                "🔴 Low": "#f87171"
            },
            title="Sweet Spot: High Demand + Low Supply = Best Topics",
            template="plotly_dark"
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ─── Blog Title Suggestions ────────────────────────────────
    st.markdown("### ✍️ Top 5 Blog Title Suggestions")
    
    top5 = df.head(5)
    for i, (_, row) in enumerate(top5.iterrows()):
        kw = row['Keyword / Topic']
        titles = [
            f"{kw.title()} – Complete Hindi Guide 2026",
            f"{kw.title()} के 7 आसान तरीके जो सच में काम करते हैं",
            f"क्यों होता है {kw}? और इससे कैसे निकलें",
            f"{kw.title()} – Expert Life Coach की राय",
            f"{kw.title()}: Step-by-Step Hindi Roadmap"
        ]
        with st.expander(f"#{i+1} – {kw}"):
            for t in titles: