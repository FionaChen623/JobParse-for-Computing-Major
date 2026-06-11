"""
dashboard.py — Interactive JD Resume Database Dashboard

Run with:  streamlit run dashboard.py

Features:
  - Paste any job description to auto-extract structured fields
  - Browse, filter, and analyze your personal resume/job database
  - Skill frequency charts, word clouds, and trend visualizations
  - Export filtered data as CSV
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import Counter
import re
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jd_analyzer.database import get_all_records, append_record, COLUMNS
from jd_analyzer.extractor import extract_fields

# ── Page config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JD Resume Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Chinese font for word clouds ────────────────────────────────────────
def _find_cjk_font() -> str:
    candidates = ['PingFang', 'Heiti', 'NotoSansCJK', 'SourceHanSans',
                  'STHeiti', 'SimHei', 'Microsoft YaHei']
    for fpath in fm.findSystemFonts():
        for c in candidates:
            if c in fpath:
                return fpath
    return None

CJK_FONT = _find_cjk_font()

# ── Helpers ─────────────────────────────────────────────────────────────

def split_skills(series: pd.Series) -> list:
    """Split comma/CJK-separated skill strings into a flat list."""
    all_skills = []
    sep = re.compile(r'[,，、/]')
    for text in series.dropna():
        items = [s.strip() for s in sep.split(str(text)) if s.strip()]
        all_skills.extend(items)
    return all_skills


def render_wordcloud(word_freq: dict, ax):
    """Plot a word cloud on the given matplotlib axes."""
    if not word_freq:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=14)
        ax.axis('off')
        return
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        colormap='viridis',
        max_words=60,
        prefer_horizontal=0.7,
        random_state=42,
        font_path=CJK_FONT,
    ).generate_from_frequencies(word_freq)
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout()


# ── Custom CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%); }
.main > div { padding: 1.5rem 2rem !important; }
h1 { color: #1a2634 !important; font-weight: 700 !important; letter-spacing: -0.3px; }
div[data-testid="metric-container"] {
    background: white; border-radius: 14px; padding: 12px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #eaedf2; transition: all 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-2px);
}
div[data-testid="metric-container"] label {
    font-size: 0.85rem !important; color: #6b7280 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important; font-weight: 700 !important; color: #1f2937 !important;
}
h2, h3 { font-weight: 600 !important; color: #1f2937 !important; margin-top: 0 !important; }
div[data-testid="column"] {
    background: white; border-radius: 16px; padding: 6px 14px 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); border: 1px solid #edf0f5;
    transition: box-shadow 0.3s ease, transform 0.3s ease; margin-bottom: 8px;
}
div[data-testid="column"]:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.10); transform: translateY(-3px);
}
section[data-testid="stSidebar"] > div { background: #ffffff; border-right: 1px solid #eef0f4; }
div[data-testid="stExpander"] {
    background: white; border-radius: 14px; border: 1px solid #e8ecf2;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stButton button { border-radius: 10px !important; font-weight: 500 !important; transition: all 0.25s ease !important; }
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important; box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
}
.stButton button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    box-shadow: 0 6px 16px rgba(37,99,235,0.35) !important;
    transform: translateY(-2px) scale(1.02);
}
hr { margin: 1.2rem 0 !important; border-color: #e2e7ee !important; }
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
div[data-testid="column"] { animation: fadeSlideIn 0.4s ease-out both; }
div[data-testid="metric-container"] { animation: fadeSlideIn 0.4s ease-out both; }
</style>
""", unsafe_allow_html=True)

# ── Title ───────────────────────────────────────────────────────────────
st.title("🔍 JD Resume Analyzer")
st.caption("Paste job descriptions to build your personal resume database — extract, browse, visualize, and export.")

# ── JD input form ───────────────────────────────────────────────────────
with st.expander("📝 Paste a new job description", expanded=False):
    jd_text = st.text_area(
        "Paste the full JD text below. The system will auto-extract fields using keyword matching.",
        height=180, key="jd_input"
    )
    if st.button("🔍 Extract & Preview", type="primary"):
        if jd_text.strip():
            record = extract_fields(jd_text.strip())
            st.session_state['pending_record'] = record
            st.rerun()
        else:
            st.warning("Please paste some text first.")

    if 'pending_record' in st.session_state and st.session_state['pending_record']:
        rec = st.session_state['pending_record']
        st.markdown("**📋 Extracted fields — you can edit before saving:**")
        df_preview = pd.DataFrame([rec])
        edited = st.data_editor(
            df_preview, use_container_width=True, hide_index=True,
            num_rows="fixed",
            column_config={c: st.column_config.TextColumn(c, width="medium") for c in COLUMNS},
            key="preview_editor"
        )
        col_ok, col_cancel = st.columns([1, 1])
        with col_ok:
            if st.button("✅ Save to Database", type="primary", key="confirm_save"):
                row = edited.iloc[0].to_dict()
                count = append_record(row)
                st.success(f"✅ Saved! Total records: {count}")
                st.session_state['pending_record'] = None
                st.rerun()
        with col_cancel:
            if st.button("🗑️ Discard", key="cancel_save"):
                st.session_state['pending_record'] = None
                st.rerun()

st.markdown("---")

# ── Load data ───────────────────────────────────────────────────────────
df = get_all_records()
if df.empty:
    st.info("📭 No records yet. Start by pasting a job description above or in the chat.")
    st.stop()

# ── Sidebar filters ─────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

all_cats = ['All'] + sorted(df['job_category'].unique().tolist())
selected_cat = st.sidebar.selectbox('Job Category', all_cats)

min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()
date_range = st.sidebar.date_input('Date Range', [min_date, max_date])

filtered = df.copy()
if selected_cat != 'All':
    filtered = filtered[filtered['job_category'] == selected_cat]
filtered = filtered[
    (filtered['timestamp'].dt.date >= date_range[0]) &
    (filtered['timestamp'].dt.date <= date_range[1])
].copy()

if filtered.empty:
    st.warning("⚠️ No records match the current filters.")
    st.stop()

# ── KPI cards ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("📄 JDs", len(filtered))
c2.metric("🏢 Companies", filtered['company_name'].nunique())
c3.metric("📍 Cities", filtered['location'].nunique())
c4.metric("📂 Categories", filtered['job_category'].nunique())

st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════
# Row 1: Category pie + Industry bar
# ═════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Job Categories")
    cat_counts = filtered['job_category'].value_counts().reset_index()
    cat_counts.columns = ['category', 'count']
    fig = px.pie(cat_counts, values='count', names='category',
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, key="chart_category", width="stretch")

with col2:
    st.subheader("🏭 Industries")
    ind_counts = filtered['company_industry'].value_counts().reset_index()
    ind_counts.columns = ['industry', 'count']
    ind_counts = ind_counts.head(10)
    fig = px.bar(ind_counts, x='count', y='industry',
                 orientation='h', text='count',
                 color='count', color_continuous_scale='Viridis')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, key="chart_industry", width="stretch")

# ═════════════════════════════════════════════════════════════════════════
# Row 2: Top 10 Languages + Top 10 ML Frameworks
# ═════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("💻 Top 10 Languages / Tools")
    lang_skills = split_skills(filtered['programming_languages'])
    if lang_skills:
        top10 = Counter(lang_skills).most_common(10)
        plot_df = pd.DataFrame(top10, columns=['skill', 'count'])
        fig = px.bar(plot_df, x='count', y='skill',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Blues')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_lang", width="stretch")
    else:
        st.info("No data")

with col2:
    st.subheader("🧠 Top 10 ML / DL Frameworks")
    ml_skills = split_skills(filtered['ml_frameworks'])
    if ml_skills:
        top10 = Counter(ml_skills).most_common(10)
        plot_df = pd.DataFrame(top10, columns=['framework', 'count'])
        fig = px.bar(plot_df, x='count', y='framework',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_ml", width="stretch")
    else:
        st.info("No data")

# ═════════════════════════════════════════════════════════════════════════
# Row 3: Word Cloud (top) + Credentials (bottom)  |  AI Coding Tools
# ═════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Core Knowledge Cloud")
    core_skills = split_skills(filtered['core_knowledge'])
    if core_skills:
        word_freq = dict(Counter(core_skills))
        fig_wc, ax_wc = plt.subplots(figsize=(9, 3.6))
        render_wordcloud(word_freq, ax_wc)
        st.pyplot(fig_wc)
    else:
        st.info("No data")

    # Credentials pinned below
    bonus_skills = split_skills(filtered['bonus_journals'])
    if bonus_skills:
        unique_bonus = sorted(set(bonus_skills),
                              key=lambda x: bonus_skills.count(x), reverse=True)
        tags = ' '.join([
            f'<span style="display:inline-block; background:#e8eaf0; color:#444; '
            f'border-radius:10px; padding:1px 8px; margin:2px 3px; font-size:0.75rem; '
            f'white-space:nowrap;">{t}</span>'
            for t in unique_bonus
        ])
        st.markdown(f'''
<div style="background:white;border-radius:14px;padding:4px 12px 6px;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);border:1px solid #edf0f5;">
  <span style="font-weight:600;font-size:0.9rem;color:#1f2937;">🏅 Credentials</span>
  <div style="line-height:1.7;margin-top:2px;">{tags}</div>
</div>
''', unsafe_allow_html=True)

with col2:
    st.subheader("🤖 AI Coding Tools")
    ai_skills = split_skills(filtered['ai_coding_tools'])
    extra = split_skills(filtered['other_requirements'])
    ai_kw = ['Claude Code', 'Codex', 'OpenClaw', 'Cursor', 'Windsurf',
             'GitHub Copilot', 'Copilot', 'Cline', 'Aider']
    for item in extra:
        for kw in ai_kw:
            if kw.lower() in item.lower() and kw not in ai_skills:
                ai_skills.append(kw)
    if ai_skills:
        top8 = Counter(ai_skills).most_common(8)
        plot_df = pd.DataFrame(top8, columns=['tool', 'count'])
        fig = px.bar(plot_df, x='count', y='tool',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Tealgrn')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_ai_tools", width="stretch")
    else:
        st.info("No data")

# ═════════════════════════════════════════════════════════════════════════
# Row 4: Big Data Tools + Cloud / DevOps
# ═════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗄️ Big Data Tools")
    bd_skills = split_skills(filtered['big_data_tools'])
    if bd_skills:
        top8 = Counter(bd_skills).most_common(8)
        plot_df = pd.DataFrame(top8, columns=['tool', 'count'])
        fig = px.bar(plot_df, x='count', y='tool',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Greens')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_bigdata", width="stretch")
    else:
        st.info("No data")

with col2:
    st.subheader("☁️ Cloud / DevOps")
    cloud_skills = split_skills(filtered['cloud_tools'])
    if cloud_skills:
        top8 = Counter(cloud_skills).most_common(8)
        plot_df = pd.DataFrame(top8, columns=['tool', 'count'])
        fig = px.bar(plot_df, x='count', y='tool',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Purples')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_cloud", width="stretch")
    else:
        st.info("No data")

# ═════════════════════════════════════════════════════════════════════════
# Row 5: Web Dev + Soft Skills
# ═════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Web Development")
    web_skills = split_skills(filtered['web_dev'])
    if web_skills:
        top8 = Counter(web_skills).most_common(8)
        plot_df = pd.DataFrame(top8, columns=['skill', 'count'])
        fig = px.bar(plot_df, x='count', y='skill',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Teal')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_web", width="stretch")
    else:
        st.info("No data")

with col2:
    st.subheader("🤝 Top 8 Soft Skills")
    soft_skills = split_skills(filtered['soft_skills'])
    if soft_skills:
        top8 = Counter(soft_skills).most_common(8)
        plot_df = pd.DataFrame(top8, columns=['skill', 'count'])
        fig = px.bar(plot_df, x='count', y='skill',
                     orientation='h', text='count',
                     color='count', color_continuous_scale='Pinkyl')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, key="chart_soft", width="stretch")
    else:
        st.info("No data")

# ═════════════════════════════════════════════════════════════════════════
# Bottom: detailed table + export
# ═════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📋 All Records")

display_cols = [c for c in filtered.columns if c != 'raw_text']
st.dataframe(filtered[display_cols], width="stretch", height=400)

csv_data = filtered.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Download CSV (filtered)",
    data=csv_data,
    file_name='jd_records_filtered.csv',
    mime='text/csv',
)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.caption(
    f"📅 {len(df)} records total | "
    f"Latest: {df['timestamp'].max().strftime('%Y-%m-%d')}"
)
