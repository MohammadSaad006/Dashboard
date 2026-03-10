import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from placement_analyzer import AMCATAnalyzer, DEPT_COLORS, TALENT_TIERS

st.set_page_config(
    page_title="TNP Intelligence Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# DARK GLASSMORPHISM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1337 40%, #0a0a1a 100%);
    color: #e2e8f0;
}

/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(13,19,55,0.97) !important;
    border-right: 1px solid rgba(99,102,241,0.3);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p {
    color: #a5b4fc !important;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(139,92,246,0.2) 50%, rgba(236,72,153,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    text-align: center;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #a5b4fc, #e879f9, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-top: 0.5rem;
    font-weight: 400;
}

/* Metric cards */
.metric-glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-glass:hover {
    border-color: rgba(99,102,241,0.5);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.2);
}
.metric-glass::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, linear-gradient(90deg, #6366f1, #a855f7));
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label {
    font-size: 0.78rem;
    color: #94a3b8;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-delta {
    font-size: 0.85rem;
    margin-top: 0.4rem;
    font-weight: 600;
}

/* Section headers */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    border-left: 4px solid #6366f1;
    padding-left: 1rem;
    margin: 1.5rem 0 1rem 0;
}

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}

/* Alert boxes */
.alert-red {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #fca5a5;
}
.alert-yellow {
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #fcd34d;
}
.alert-green {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #6ee7b7;
}

/* Tier badges */
.tier-diamond { color: #a5f3fc; font-weight: 700; font-size: 1.1rem; }
.tier-gold     { color: #fde68a; font-weight: 700; font-size: 1.1rem; }
.tier-silver   { color: #cbd5e1; font-weight: 700; font-size: 1.1rem; }
.tier-bronze   { color: #d97706; font-weight: 700; font-size: 1.1rem; }

/* Tables */
.stDataFrame { background: rgba(255,255,255,0.03) !important; border-radius: 12px; }
.stDataFrame td, .stDataFrame th { color: #e2e8f0 !important; }

/* Sidebar logo */
.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid rgba(99,102,241,0.3);
    margin-bottom: 1rem;
}
.sidebar-logo h2 {
    background: linear-gradient(135deg, #a5b4fc, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.3rem;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INITIALIZE — Web Hosting Mode
# ─────────────────────────────────────────────
import io

@st.cache_resource
def load_default_analyzer():
    try:
        if os.path.exists('amcat-raw-data.csv'):
            return AMCATAnalyzer('amcat-raw-data.csv'), 'amcat-raw-data.csv'
    except Exception:
        pass
    return None, None

# Session state for dynamic uploads
if 'uploaded_analyzer' not in st.session_state:
    st.session_state['uploaded_analyzer'] = None
if 'upload_filename' not in st.session_state:
    st.session_state['upload_filename'] = None

# Logic: use upload if exists, otherwise default
if st.session_state['uploaded_analyzer'] is not None:
    analyzer = st.session_state['uploaded_analyzer']
    active_filename = st.session_state['upload_filename']
else:
    analyzer, active_filename = load_default_analyzer()

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e2e8f0', family='Inter'),
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
)

def apply_theme(fig, title=None):
    fig.update_layout(**PLOTLY_THEME)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=16, color='#c4b5fd')))
    return fig

def hex_to_rgba(hex_color, alpha=0.2):
    """Convert a 6-char hex color (#rrggbb) to rgba() string for Plotly fillcolor."""
    h = hex_color.lstrip('#')
    if len(h) == 6:
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f'rgba({r},{g},{b},{alpha})'
    return hex_color

def kpi_card(value, label, color="#6366f1", delta=None, prefix="", suffix=""):
    delta_html = ""
    if delta is not None:
        sign = "▲" if delta >= 0 else "▼"
        clr = "#10b981" if delta >= 0 else "#ef4444"
        delta_html = f'<div class="metric-delta" style="color:{clr}">{sign} {abs(delta):.1f}</div>'
    return f"""
    <div class="metric-glass" style="--accent: linear-gradient(90deg, {color}, {color}88);">
        <div class="metric-value">{prefix}{value}{suffix}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>"""

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2rem;">🎯</div>
        <h2>TNP Intelligence Hub</h2>
        <div style="color:#64748b;font-size:0.75rem;">Placement Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # ── CSV/Excel Upload ──────────────────────────────
    st.markdown("**📂 Data Source**")
    uploaded_file = st.file_uploader(
        "Upload File (drag & drop)",
        type=["csv", "xlsx", "xls"],
        help="Upload your AMCAT data (.csv or .xlsx). It will be saved automatically.",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.get('upload_filename'):
            with st.spinner("🔄 Analyzing data..."):
                try:
                    # In stlite, we just load into memory
                    new_analyzer = AMCATAnalyzer(io.BytesIO(uploaded_file.getvalue()))
                    st.session_state['uploaded_analyzer'] = new_analyzer
                    st.session_state['upload_filename'] = uploaded_file.name
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.success(f"✅ Active: {uploaded_file.name}")
    else:
        # Allow clearing previously uploaded data
        if st.session_state['uploaded_analyzer'] is not None:
            if st.button("🗑️ Clear Uploaded Data"):
                st.session_state['uploaded_analyzer'] = None
                st.session_state['upload_filename'] = None
                st.rerun()

    st.markdown("---")
    page = st.radio("📍 Navigation", [
        "🚀 Mission Control",
        "🏢 Department HQ",
        "⚔️ Cross-Dept Battle",
        "🧠 Student Intelligence",
        "🎯 Talent Pipeline",
        "📅 Batch Comparison",
        "📤 Export & Report",
    ], label_visibility="collapsed", disabled=(analyzer is None))

    st.markdown("---")
    if analyzer:
        src_label = f"📄 {active_filename}"
        st.markdown(f"<div style='color:#475569;font-size:0.72rem;text-align:center;'>{src_label}<br><b>{len(analyzer.df)}</b> students · <b>{len(analyzer.branches)}</b> depts</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#475569;font-size:0.72rem;text-align:center;'>No data loaded</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GATE: if no data uploaded, show welcome screen
# ─────────────────────────────────────────────
if analyzer is None:
    st.markdown("""
    <div style="
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        min-height:70vh; text-align:center; padding:3rem;
    ">
        <div style="font-size:5rem; margin-bottom:1.5rem;">📂</div>
        <div style="
            font-size:2.5rem; font-weight:900;
            background:linear-gradient(135deg,#a5b4fc,#e879f9);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            margin-bottom:1rem;
        ">Upload Your AMCAT Data</div>
        <div style="color:#94a3b8; font-size:1.1rem; max-width:480px; line-height:1.7;">
            Drag & drop your <b style="color:#c4b5fd;">CSV file</b> into the sidebar uploader
            to instantly generate your full placement analytics dashboard.
        </div>
        <div style="margin-top:2.5rem; display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center;">
            <div style="background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);border-radius:12px;padding:1rem 1.5rem;color:#a5b4fc;font-size:0.9rem;">🏢 Department Analysis</div>
            <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:1rem 1.5rem;color:#6ee7b7;font-size:0.9rem;">⚔️ Cross-Dept Comparison</div>
            <div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:1rem 1.5rem;color:#fcd34d;font-size:0.9rem;">🎯 Talent Pipeline</div>
            <div style="background:rgba(236,72,153,0.12);border:1px solid rgba(236,72,153,0.3);border-radius:12px;padding:1rem 1.5rem;color:#f9a8d4;font-size:0.9rem;">📤 Export Reports</div>
        </div>
        <div style="margin-top:2rem;color:#475569;font-size:0.8rem;">
            ← Use the sidebar uploader on the left
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Only reachable if analyzer is not None — resolve batch filter
with st.sidebar:
    st.markdown("**🔧 Global Filters**")
    batch_filter   = st.selectbox("Batch Year", ["All Batches"] + [str(b) for b in sorted(analyzer.batches)])
    selected_batch = None if batch_filter == "All Batches" else int(batch_filter)


# ─────────────────────────────────────────────
# PAGE 1 — MISSION CONTROL
# ─────────────────────────────────────────────
if page == "🚀 Mission Control":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🎯 TNP Intelligence Hub</div>
        <div class="hero-subtitle">Training & Placement — AMCAT Performance Command Center</div>
    </div>
    """, unsafe_allow_html=True)

    stats = analyzer.summary_stats(batch=selected_batch)
    comp  = analyzer.branch_competitiveness(batch=selected_batch)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card(stats['Total Students'], "Total Students", "#6366f1"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card(stats['Avg Dept Score'], "Avg Score", "#10b981"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card(f"{stats['Placement Ready %']}%", "Placement Ready", "#f59e0b"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card(stats['Top Performers (>70%)'], "Top Performers", "#ef4444"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card(stats['Diamond Tier'], "Diamond Tier 💎", "#a5f3fc"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">🏆 Department Performance Ranking</div>', unsafe_allow_html=True)
        comp_sorted = comp.sort_values('Avg_Dept_Score', ascending=True).reset_index()
        colors_list = [DEPT_COLORS.get(b, '#6366f1') for b in comp_sorted['Branch']]
        fig_bar = go.Figure(go.Bar(
            x=comp_sorted['Avg_Dept_Score'],
            y=comp_sorted['Branch'],
            orientation='h',
            marker=dict(color=colors_list, line=dict(width=0)),
            text=[f" {v:.1f}" for v in comp_sorted['Avg_Dept_Score']],
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=13),
        ))
        apply_theme(fig_bar, "Average Department Score")
        fig_bar.update_xaxes(range=[0, 80])
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">💎 Talent Tier Distribution</div>', unsafe_allow_html=True)
        tier_df  = analyzer.talent_tier_distribution(batch=selected_batch)
        pie_colors = ['#a5f3fc', '#fde68a', '#cbd5e1', '#d97706', '#94a3b8']
        fig_pie = go.Figure(go.Pie(
            labels=tier_df['Tier'],
            values=tier_df['Count'],
            hole=0.55,
            marker=dict(colors=pie_colors, line=dict(color='rgba(0,0,0,0.4)', width=2)),
            textfont=dict(size=12, color='#e2e8f0'),
        ))
        apply_theme(fig_pie, "All Students")
        fig_pie.update_traces(textposition='outside')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="section-header">📊 Department Scorecard</div>', unsafe_allow_html=True)
    comp_display = comp.copy()
    comp_display.index.name = "Department"
    comp_display.columns = ['Students', 'Avg Score', 'Core Aptitude', 'Top % (>70)', 'Ready %', 'Diamond %', 'Std Dev']
    comp_display = comp_display.sort_values('Avg Score', ascending=False)
    st.dataframe(comp_display.style.background_gradient(cmap='viridis', subset=['Avg Score', 'Ready %', 'Diamond %']), use_container_width=True)

    st.markdown('<div class="section-header">📈 Core Aptitude vs Dept Score</div>', unsafe_allow_html=True)
    scatter_data = analyzer.get_branch_data(batch=selected_batch).dropna(subset=['Core_Aptitude', 'Dept_Score'])
    scatter_data = scatter_data[scatter_data['Dept_Score'] > 0]
    fig_scatter = px.scatter(
        scatter_data, x='Core_Aptitude', y='Dept_Score',
        color='Branch', hover_name='fullName',
        hover_data={'Branch': True, 'Talent_Tier': True, 'Batch': True},
        color_discrete_map=DEPT_COLORS,
        opacity=0.7, size_max=8,
    )
    apply_theme(fig_scatter, "Core Aptitude vs Department Score — All Students")
    fig_scatter.update_traces(marker=dict(size=7))
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 2 — DEPARTMENT HQ
# ─────────────────────────────────────────────
elif page == "🏢 Department HQ":
    st.markdown('<div class="hero-banner"><div class="hero-title">🏢 Department HQ</div><div class="hero-subtitle">Deep-dive into any single department\'s performance</div></div>', unsafe_allow_html=True)

    dept_sel = st.selectbox("Select Department", analyzer.branches, key="dept_hq")
    data     = analyzer.get_branch_data(dept_sel, selected_batch)
    stats    = analyzer.summary_stats(dept_sel, selected_batch)
    color    = DEPT_COLORS.get(dept_sel, '#6366f1')

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card(stats['Total Students'], "Students", color), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card(stats['Avg Dept Score'], "Avg Score", color), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card(f"{stats['Placement Ready %']}%", "Placement Ready", color), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card(stats['Diamond Tier'], "Diamond Tier 💎", color), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    relevant_cols = analyzer.get_relevant_cols(dept_sel)
    valid_cols = [c for c in relevant_cols if c in data.columns and data[c].notna().sum() > 0]
    avg_scores = data[valid_cols].mean(skipna=True)

    with col_a:
        st.markdown('<div class="section-header">🕸️ Skill Radar</div>', unsafe_allow_html=True)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=avg_scores.values.tolist() + [avg_scores.values[0]],
            theta=avg_scores.index.tolist() + [avg_scores.index[0]],
            fill='toself',
            name=dept_sel,
            line=dict(color=color, width=2),
            fillcolor=hex_to_rgba(color, 0.2),
        ))
        fig_radar.update_layout(**PLOTLY_THEME, polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(showline=False, gridcolor='rgba(255,255,255,0.1)', tickcolor='rgba(255,255,255,0.3)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickcolor='rgba(255,255,255,0.4)'),
        ))
        apply_theme(fig_radar, f"Skill Profile — {dept_sel}")
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">📦 Score Distribution</div>', unsafe_allow_html=True)
        violin_data = data[['Dept_Score', 'Core_Aptitude']].melt(var_name='Metric', value_name='Score').dropna()
        fig_violin = px.violin(violin_data, x='Metric', y='Score', color='Metric', box=True, points='outliers',
                               color_discrete_sequence=[color, '#a855f7'])
        apply_theme(fig_violin, "Score Distribution")
        st.plotly_chart(fig_violin, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="section-header">📊 Subject-wise Averages</div>', unsafe_allow_html=True)
        bar_df = avg_scores.reset_index()
        bar_df.columns = ['Subject', 'Score']
        bar_df['Gap']   = bar_df['Subject'].map(lambda s: max(0, (analyzer.skill_gap_analysis(dept_sel, selected_batch).get(s, {}).get('threshold', 60)) - bar_df.loc[bar_df['Subject']==s, 'Score'].values[0]))
        bar_df['Color'] = bar_df['Score'].apply(lambda x: '#10b981' if x>=60 else ('#f59e0b' if x>=45 else '#ef4444'))
        fig_bar_subj = go.Figure()
        fig_bar_subj.add_trace(go.Bar(
            x=bar_df['Subject'], y=bar_df['Score'],
            marker_color=bar_df['Color'],
            name='Avg Score', text=[f"{v:.0f}" for v in bar_df['Score']], textposition='outside',
        ))
        apply_theme(fig_bar_subj, "Subject-wise Average Scores")
        st.plotly_chart(fig_bar_subj, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header">💎 Talent Tier Breakdown</div>', unsafe_allow_html=True)
        tier_counts = data['Talent_Tier'].value_counts()
        tier_cols_order = ['Diamond 💎', 'Gold 🥇', 'Silver 🥈', 'Bronze 🥉']
        tier_vals   = [tier_counts.get(t, 0) for t in tier_cols_order]
        fig_tier    = go.Figure(go.Bar(
            x=tier_cols_order, y=tier_vals,
            marker_color=['#a5f3fc','#fde68a','#cbd5e1','#d97706'],
            text=tier_vals, textposition='outside',
        ))
        apply_theme(fig_tier, "Talent Tier Distribution")
        st.plotly_chart(fig_tier, use_container_width=True)

    st.markdown('<div class="section-header">🏅 Top 15 Students — Leaderboard</div>', unsafe_allow_html=True)
    top_df = analyzer.top_performers(n=15, branch=dept_sel, batch=selected_batch)
    top_df.index = top_df.index + 1
    st.dataframe(
        top_df.style.background_gradient(cmap='viridis', subset=['Dept_Score']),
        use_container_width=True
    )

    st.markdown('<div class="section-header">🎯 Skill Gap vs Industry Standard</div>', unsafe_allow_html=True)
    gaps = analyzer.skill_gap_analysis(dept_sel, selected_batch)
    if gaps:
        gap_rows = []
        for subj, v in gaps.items():
            status = "🔴 Critical" if v['gap']>15 else ("🟡 Needs Work" if v['gap']>0 else "🟢 On Target")
            gap_rows.append({'Subject': subj, 'Avg Score': v['avg'], 'Target': v['threshold'], 'Gap': v['gap'], 'Status': status})
        gap_df = pd.DataFrame(gap_rows).sort_values('Gap', ascending=False)
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(x=gap_df['Subject'], y=gap_df['Avg Score'], name='Current Avg', marker_color=color))
        fig_gap.add_trace(go.Scatter(x=gap_df['Subject'], y=gap_df['Target'], name='Industry Target',
                                     mode='markers+lines', line=dict(color='#f59e0b', dash='dash'), marker=dict(size=10, color='#f59e0b')))
        apply_theme(fig_gap, "Current Performance vs Industry Standards")
        st.plotly_chart(fig_gap, use_container_width=True)
        st.dataframe(gap_df, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 3 — CROSS-DEPT BATTLE
# ─────────────────────────────────────────────
elif page == "⚔️ Cross-Dept Battle":
    st.markdown('<div class="hero-banner"><div class="hero-title">⚔️ Cross-Department Battle</div><div class="hero-subtitle">Compare departments head-to-head and find the winners</div></div>', unsafe_allow_html=True)

    selected_depts = st.multiselect(
        "Select 2–8 Departments to Compare",
        analyzer.branches,
        default=analyzer.branches[:4],
        max_selections=8
    )

    if len(selected_depts) < 2:
        st.warning("Please select at least 2 departments.")
        st.stop()

    comp = analyzer.branch_competitiveness(batch=selected_batch)
    comp_sel = comp.loc[[d for d in selected_depts if d in comp.index]]

    # Winner badges row
    col_winners = st.columns(4)
    metrics_to_win = [('Avg_Dept_Score', '🏆 Highest Avg Score'), ('Placement_Ready_%', '✅ Most Placement Ready'), ('Diamond_%', '💎 Most Diamond Tier'), ('Avg_Core_Aptitude', '🧠 Best Core Aptitude')]
    for i, (metric, label) in enumerate(metrics_to_win):
        if metric in comp_sel.columns:
            winner = comp_sel[metric].idxmax()
            val    = comp_sel.loc[winner, metric]
            with col_winners[i]:
                st.markdown(f"""
                <div class="metric-glass" style="--accent: linear-gradient(90deg, {DEPT_COLORS.get(winner,'#6366f1')}, #a855f7);">
                    <div style="font-size:1.5rem;">🥇</div>
                    <div class="metric-value" style="font-size:1.2rem;">{winner}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-delta" style="color:#10b981;">{val:.1f}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_radar, col_bar = st.columns(2)

    with col_radar:
        st.markdown('<div class="section-header">🕸️ Multi-Department Radar</div>', unsafe_allow_html=True)
        radar_metrics = ['Avg_Dept_Score', 'Avg_Core_Aptitude', 'Placement_Ready_%', 'Diamond_%', 'Top_Performer_%']
        radar_labels  = ['Avg Score', 'Core Aptitude', 'Placement Ready', 'Diamond %', 'Top Performers']
        fig_radar_multi = go.Figure()
        for dept in selected_depts:
            if dept in comp_sel.index:
                vals = [comp_sel.loc[dept, m] for m in radar_metrics]
                fig_radar_multi.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=radar_labels + [radar_labels[0]],
                    name=dept,
                    line=dict(color=DEPT_COLORS.get(dept, '#6366f1'), width=2),
                    fill='toself', fillcolor=hex_to_rgba(DEPT_COLORS.get(dept,'#6366f1'), 0.13),
                ))
        fig_radar_multi.update_layout(**PLOTLY_THEME, polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(showline=False, gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        ))
        st.plotly_chart(fig_radar_multi, use_container_width=True)

    with col_bar:
        st.markdown('<div class="section-header">📊 Side-by-Side Metrics</div>', unsafe_allow_html=True)
        metrics_compare = {'Avg_Dept_Score': 'Avg Score', 'Placement_Ready_%': 'Placement Ready %', 'Diamond_%': 'Diamond %'}
        fig_grouped = go.Figure()
        for metric, label in metrics_compare.items():
            if metric in comp_sel.columns:
                fig_grouped.add_trace(go.Bar(
                    x=comp_sel.index.tolist(),
                    y=comp_sel[metric].values,
                    name=label,
                    text=[f"{v:.1f}" for v in comp_sel[metric].values],
                    textposition='outside',
                ))
        apply_theme(fig_grouped, "Key Metrics Comparison")
        fig_grouped.update_layout(barmode='group')
        st.plotly_chart(fig_grouped, use_container_width=True)

    st.markdown('<div class="section-header">🔥 Subject-Heatmap (Selected Departments)</div>', unsafe_allow_html=True)
    heat_data = analyzer.subject_avg_by_dept()
    heat_sel  = heat_data.loc[[d for d in selected_depts if d in heat_data.index]]
    heat_sel  = heat_sel.dropna(axis=1, how='all').fillna(0)
    if not heat_sel.empty:
        fig_heat = px.imshow(
            heat_sel.values,
            x=heat_sel.columns.tolist(),
            y=heat_sel.index.tolist(),
            color_continuous_scale='Plasma',
            text_auto='.0f',
            aspect='auto',
        )
        apply_theme(fig_heat, "Average Score per Subject × Department")
        fig_heat.update_traces(textfont=dict(size=12, color='white'))
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown('<div class="section-header">📋 Full Comparison Table</div>', unsafe_allow_html=True)
    display_comp = comp_sel.copy()
    display_comp.columns = ['Students', 'Avg Dept Score', 'Core Aptitude', 'Top % (>70)', 'Placement Ready %', 'Diamond %', 'Std Dev']
    st.dataframe(
        display_comp.style.background_gradient(cmap='RdYlGn', subset=['Avg Dept Score', 'Placement Ready %', 'Diamond %']),
        use_container_width=True
    )


# ─────────────────────────────────────────────
# PAGE 4 — STUDENT INTELLIGENCE
# ─────────────────────────────────────────────
elif page == "🧠 Student Intelligence":
    st.markdown('<div class="hero-banner"><div class="hero-title">🧠 Student Intelligence</div><div class="hero-subtitle">Individual student profiles, clustering, and at-risk detection</div></div>', unsafe_allow_html=True)

    dept_filter_si = st.selectbox("Filter by Department", ["All Departments"] + analyzer.branches, key="si_dept")
    dept_for_si    = None if dept_filter_si == "All Departments" else dept_filter_si

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Student", "🎭 Clusters", "🏅 Leaderboard", "⚠️ At-Risk Students"])

    with tab1:
        query = st.text_input("Search by name or roll number", placeholder="e.g. Pratik, 23BD...")
        if query:
            results = analyzer.search_student(query)
            if len(results) == 0:
                st.warning("No students found.")
            else:
                st.success(f"Found {len(results)} student(s)")
                display_cols = ['fullName', 'Branch', 'Batch', 'Dept_Score', 'Core_Aptitude', 'Talent_Tier', 'Dept_Percentile', 'English', 'Quant', 'Logical', 'WriteX']
                display_cols = [c for c in display_cols if c in results.columns]
                results_display = results[display_cols].copy()
                results_display['Dept_Percentile'] = results_display['Dept_Percentile'].round(1)
                st.dataframe(results_display, use_container_width=True)

                if len(results) == 1:
                    student = results.iloc[0]
                    st.markdown(f"### Profile: {student.get('fullName','—')}")
                    dept = student.get('Branch', '')
                    rel_cols = [c for c in analyzer.get_relevant_cols(dept) if c in results.columns and pd.notna(student.get(c))]
                    if rel_cols:
                        scores = [student[c] for c in rel_cols]
                        fig_student = go.Figure(go.Scatterpolar(
                            r=scores + [scores[0]], theta=rel_cols + [rel_cols[0]],
                            fill='toself', name=student.get('fullName',''),
                            line=dict(color='#6366f1', width=2), fillcolor='rgba(99,102,241,0.2)',
                        ))
                        fig_student.update_layout(**PLOTLY_THEME, polar=dict(bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(showline=False, gridcolor='rgba(255,255,255,0.1)'),
                            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)')))
                        st.plotly_chart(fig_student, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-header">🎭 Student Performance Clusters</div>', unsafe_allow_html=True)
        clustered = analyzer.student_clustering(dept_for_si, selected_batch)
        clustered_clean = clustered.dropna(subset=['English', 'Quant', 'Logical'])
        fig_cluster = px.scatter_3d(
            clustered_clean, x='English', y='Quant', z='Logical',
            color='Cluster_Label', hover_name='fullName',
            hover_data={'Branch': True, 'Talent_Tier': True},
            opacity=0.75,
            color_discrete_sequence=['#6366f1', '#10b981', '#f59e0b', '#ef4444'],
        )
        fig_cluster.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  font=dict(color='#e2e8f0'), margin=dict(l=0, r=0, t=40, b=0), height=550)
        st.plotly_chart(fig_cluster, use_container_width=True)
        cluster_summary = clustered.groupby('Cluster_Label').agg(
            Count=('Dept_Score', 'count'),
            Avg_Dept_Score=('Dept_Score', 'mean'),
            Avg_English=('English', 'mean'),
            Avg_Quant=('Quant', 'mean'),
            Avg_Logical=('Logical', 'mean'),
        ).round(1)
        st.dataframe(cluster_summary, use_container_width=True)

    with tab3:
        n_top = st.slider("Number of top students", 10, 50, 20)
        top_df2 = analyzer.top_performers(n=n_top, branch=dept_for_si, batch=selected_batch)
        top_df2.index = top_df2.index + 1
        st.dataframe(top_df2.style.background_gradient(cmap='viridis', subset=['Dept_Score']), use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">⚠️ At-Risk Students (Bottom 20%)</div>', unsafe_allow_html=True)
        bottom_df = analyzer.bottom_performers(n=30, branch=dept_for_si, batch=selected_batch)
        bottom_df = bottom_df[bottom_df['Dept_Score'] < 40]
        if len(bottom_df) == 0:
            st.success("🎉 No critically at-risk students in this filter.")
        else:
            st.markdown(f'<div class="alert-red">⚠️ {len(bottom_df)} students with Dept Score below 40 — immediate intervention recommended.</div>', unsafe_allow_html=True)
            st.dataframe(bottom_df, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE 5 — TALENT PIPELINE
# ─────────────────────────────────────────────
elif page == "🎯 Talent Pipeline":
    st.markdown('<div class="hero-banner"><div class="hero-title">🎯 Talent Pipeline</div><div class="hero-subtitle">Placement readiness gauges, skill gap radar, and subject trends</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">⚡ Placement Readiness — All Departments</div>', unsafe_allow_html=True)
    comp_all = analyzer.branch_competitiveness(batch=selected_batch)
    n_depts  = len(comp_all)
    gauge_cols = st.columns(min(n_depts, 4))
    for i, (dept, row) in enumerate(comp_all.iterrows()):
        col_idx = i % 4
        ready_val = row['Placement_Ready_%']
        color_g   = '#10b981' if ready_val >= 60 else ('#f59e0b' if ready_val >= 40 else '#ef4444')
        with gauge_cols[col_idx]:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ready_val,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': dept.replace('BTECH-',''), 'font': {'size': 13, 'color': '#c4b5fd'}},
                number={'suffix': '%', 'font': {'size': 22, 'color': '#e2e8f0'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#94a3b8', 'tickfont': {'size': 10}},
                    'bar': {'color': color_g},
                    'bgcolor': 'rgba(255,255,255,0.05)',
                    'borderwidth': 1, 'bordercolor': 'rgba(255,255,255,0.1)',
                    'steps': [
                        {'range': [0, 40],  'color': 'rgba(239,68,68,0.15)'},
                        {'range': [40, 60], 'color': 'rgba(245,158,11,0.15)'},
                        {'range': [60, 100], 'color': 'rgba(16,185,129,0.15)'},
                    ],
                    'threshold': {'line': {'color': '#f59e0b', 'width': 2}, 'thickness': 0.8, 'value': 60}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
        if col_idx == 3 and i < n_depts - 1:
            gauge_cols = st.columns(min(n_depts - i - 1, 4))

    st.markdown('<div class="section-header">🔥 Subject Trend Heatmap — All Departments</div>', unsafe_allow_html=True)
    heat_all   = analyzer.subject_avg_by_dept()
    heat_clean = heat_all.dropna(axis=1, how='all').fillna(0)
    fig_heat_all = px.imshow(
        heat_clean.values,
        x=heat_clean.columns.tolist(),
        y=heat_clean.index.tolist(),
        color_continuous_scale='RdYlGn',
        text_auto='.0f', aspect='auto',
        zmin=0, zmax=80,
    )
    apply_theme(fig_heat_all, "Subject-wise Average Score Across All Departments")
    fig_heat_all.update_traces(textfont=dict(size=11, color='black'))
    st.plotly_chart(fig_heat_all, use_container_width=True)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown('<div class="section-header">🎯 Global Skill Gap (All Students)</div>', unsafe_allow_html=True)
        dept_sel_pipe = st.selectbox("Filter Department", ["All Departments"] + analyzer.branches, key="pipe_dept")
        dept_pipe     = None if dept_sel_pipe == "All Departments" else dept_sel_pipe
        gaps_pipe     = analyzer.skill_gap_analysis(dept_pipe, selected_batch)
        if gaps_pipe:
            gap_rows = [{'Subject': s, 'Current': v['avg'], 'Target': v['threshold'], 'Gap': v['gap']} for s, v in gaps_pipe.items()]
            gap_df   = pd.DataFrame(gap_rows).sort_values('Gap', ascending=False)
            fig_gang = go.Figure()
            bar_colors = ['#ef4444' if g > 15 else ('#f59e0b' if g > 0 else '#10b981') for g in gap_df['Gap']]
            fig_gang.add_trace(go.Bar(x=gap_df['Subject'], y=gap_df['Gap'], marker_color=bar_colors,
                                      text=[f"{g:.1f}" for g in gap_df['Gap']], textposition='outside'))
            apply_theme(fig_gang, "Skill Gap vs Industry Standards")
            fig_gang.add_hline(y=0, line_dash="dash", line_color="#10b981")
            st.plotly_chart(fig_gang, use_container_width=True)

    with col_p2:
        st.markdown('<div class="section-header">💡 Strategic Recommendations</div>', unsafe_allow_html=True)
        recs = analyzer.generate_recommendations(dept_pipe, selected_batch)
        for rec in recs:
            if '🔴' in rec:
                st.markdown(f'<div class="alert-red">{rec}</div>', unsafe_allow_html=True)
            elif '🟡' in rec:
                st.markdown(f'<div class="alert-yellow">{rec}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-green">{rec}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 6 — BATCH COMPARISON
# ─────────────────────────────────────────────
elif page == "📅 Batch Comparison":
    st.markdown('<div class="hero-banner"><div class="hero-title">📅 Batch 2026 vs 2027</div><div class="hero-subtitle">Year-on-year performance comparison and trend analysis</div></div>', unsafe_allow_html=True)

    dept_batch = st.selectbox("Filter Department (optional)", ["All Departments"] + analyzer.branches, key="batch_dept")
    dept_b     = None if dept_batch == "All Departments" else dept_batch

    batch_df = analyzer.batch_comparison(dept_b)
    if batch_df.empty or len(batch_df) < 2:
        st.info("Not enough batch data for comparison with current filter.")
    else:
        b_cols = st.columns(len(batch_df))
        for i, (_, row) in enumerate(batch_df.iterrows()):
            with b_cols[i]:
                delta = None
                if i > 0:
                    delta = row['Avg_Score'] - batch_df.iloc[i-1]['Avg_Score']
                st.markdown(kpi_card(row['Avg_Score'], f"Batch {int(row['Batch'])} Avg", '#6366f1', delta=delta), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            fig_batch_bar = go.Figure()
            subj_cols = ['Avg_English', 'Avg_Quant', 'Avg_Logical']
            subj_labels = ['English', 'Quant', 'Logical']
            bat_colors = ['#6366f1', '#10b981']
            for idx, row in batch_df.iterrows():
                fig_batch_bar.add_trace(go.Bar(
                    x=subj_labels,
                    y=[row[c] for c in subj_cols],
                    name=f"Batch {int(row['Batch'])}",
                    marker_color=bat_colors[idx % 2],
                    text=[f"{row[c]:.1f}" for c in subj_cols],
                    textposition='outside',
                ))
            apply_theme(fig_batch_bar, "Core Subjects — Batch Comparison")
            fig_batch_bar.update_layout(barmode='group')
            st.plotly_chart(fig_batch_bar, use_container_width=True)

        with col_b2:
            fig_batch_radar = go.Figure()
            radar_cols   = ['Avg_Score', 'Placement_Ready_%', 'Avg_English', 'Avg_Quant', 'Avg_Logical']
            radar_labels2 = ['Avg Score', 'Placement Ready', 'English', 'Quant', 'Logical']
            for idx, row in batch_df.iterrows():
                vals = [row[c] for c in radar_cols]
                fig_batch_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]], theta=radar_labels2 + [radar_labels2[0]],
                    name=f"Batch {int(row['Batch'])}",
                    line=dict(color=bat_colors[idx % 2], width=2),
                    fill='toself', fillcolor=hex_to_rgba(bat_colors[idx % 2], 0.2),
                ))
            fig_batch_radar.update_layout(**PLOTLY_THEME, polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(showline=False, gridcolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            ))
            st.plotly_chart(fig_batch_radar, use_container_width=True)

        st.markdown('<div class="section-header">📋 Batch-wise Summary</div>', unsafe_allow_html=True)
        batch_display = batch_df.copy()
        batch_display['Batch'] = batch_display['Batch'].astype(int)
        st.dataframe(batch_display.style.background_gradient(cmap='viridis', subset=['Avg_Score', 'Placement_Ready_%']), use_container_width=True)

        if len(batch_df) == 2:
            diff_score = batch_df.iloc[1]['Avg_Score'] - batch_df.iloc[0]['Avg_Score']
            diff_ready = batch_df.iloc[1]['Placement_Ready_%'] - batch_df.iloc[0]['Placement_Ready_%']
            if diff_score > 0:
                st.markdown(f'<div class="alert-green">✅ Batch {int(batch_df.iloc[1]["Batch"])} shows <strong>+{diff_score:.1f}</strong> pts improvement in avg score over Batch {int(batch_df.iloc[0]["Batch"])}.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-red">⚠️ Batch {int(batch_df.iloc[1]["Batch"])} shows <strong>{diff_score:.1f}</strong> pts decline vs Batch {int(batch_df.iloc[0]["Batch"])}. Curriculum review recommended.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 7 — EXPORT & REPORT
# ─────────────────────────────────────────────
elif page == "📤 Export & Report":
    st.markdown('<div class="hero-banner"><div class="hero-title">📤 Export & Report</div><div class="hero-subtitle">Download presentation-ready Excel reports and analysis summaries</div></div>', unsafe_allow_html=True)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        export_dept = st.selectbox("Department", ["All Departments"] + analyzer.branches, key="exp_dept")
    with col_exp2:
        export_batch = st.selectbox("Batch Year", ["All Batches"] + [str(b) for b in sorted(analyzer.batches)], key="exp_batch")

    exp_dept  = None if export_dept  == "All Departments" else export_dept
    exp_batch = None if export_batch == "All Batches"     else int(export_batch)

    exp_data = analyzer.export_presentation_data(exp_dept, exp_batch)
    stats    = exp_data['summary_stats']

    st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
    stat_cols = st.columns(4)
    stat_items = list(stats.items())
    for i, (k, v) in enumerate(stat_items[:8]):
        with stat_cols[i % 4]:
            st.markdown(kpi_card(v, k, '#6366f1'), unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    tab_e1, tab_e2, tab_e3 = st.tabs(["🏆 Top Performers", "💡 Recommendations", "📥 Download"])

    with tab_e1:
        st.dataframe(exp_data['top_performers'].style.background_gradient(cmap='viridis', subset=['Dept_Score']), use_container_width=True)

    with tab_e2:
        for rec in exp_data['recommendations']:
            if '🔴' in rec:
                st.markdown(f'<div class="alert-red">{rec}</div>', unsafe_allow_html=True)
            elif '🟡' in rec:
                st.markdown(f'<div class="alert-yellow">{rec}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-green">{rec}</div>', unsafe_allow_html=True)

    with tab_e3:
        st.markdown("#### 📥 Download Excel Report (Multi-sheet)")
        if st.button("📊 Generate Excel Report", type="primary"):
            excel_buffer = analyzer.export_to_excel(exp_dept, exp_batch)
            fname = f"TNP_Report_{export_dept.replace(' ','_')}_{export_batch}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_buffer,
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.markdown("#### 📄 Download Text Report")
        top_str = exp_data['top_performers'].to_string(index=False)
        recs_str = "\n".join(f"- {r}" for r in exp_data['recommendations'])
        tier_str = exp_data['talent_distribution'].to_string(index=False)
        report_md = f"""# TNP AMCAT Analysis Report
Department: {export_dept} | Batch: {export_batch}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## Summary Statistics
{chr(10).join(f"- {k}: {v}" for k,v in stats.items())}

## Talent Tier Distribution
{tier_str}

## Strategic Recommendations
{recs_str}

## Top Performers
{top_str}
"""
        st.download_button(
            label="⬇️ Download Text Report",
            data=report_md,
            file_name=f"TNP_Report_{export_dept}_{export_batch}.md",
            mime="text/plain",
        )