import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MSafe Inside Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ─────────────────────────────────────────────────────────────
   GLOBAL
───────────────────────────────────────────────────────────── */

html, body, [class*="css"] {
    font-size: 15px !important;
    font-family: 'Segoe UI', sans-serif;
    color: #0F172A;
}

/* Main App Background */
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC;
}

/* Main Content Area */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ─────────────────────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────────────────────── */

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

[data-testid="stSidebar"] * {
    color: #0F172A !important;
    font-size: 15px !important;
}

/* Sidebar Headers */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #1E3A8A !important;
    font-weight: 700;
}

/* Inputs */
[data-testid="stSidebar"] .stMultiSelect > div > div,
[data-testid="stSidebar"] .stDateInput > div,
[data-testid="stSidebar"] .stSelectbox > div {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 1px dashed #CBD5E1;
    border-radius: 10px;
    padding: 10px;
}

/* ─────────────────────────────────────────────────────────────
   TABS
───────────────────────────────────────────────────────────── */

button[data-baseweb="tab"] {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #334155 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #1E3A8A !important;
    border-bottom: 3px solid #1E3A8A !important;
}

/* ─────────────────────────────────────────────────────────────
   DATAFRAMES
───────────────────────────────────────────────────────────── */

[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stDataFrame"] * {
    font-size: 14px !important;
    color: #0F172A !important;
}

/* ─────────────────────────────────────────────────────────────
   KPI CARDS
───────────────────────────────────────────────────────────── */

.kpi-block {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    height: 100px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    transition: 0.2s ease-in-out;
}

.kpi-block:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}

.kpi-label {
    font-size: 12px;
    color: #64748B;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    line-height: 1;
}

/* KPI Colors */
.kpi-value.green { color: #166534; }
.kpi-value.red   { color: #991B1B; }
.kpi-value.amber { color: #92400E; }
.kpi-value.blue  { color: #1E3A8A; }

/* ─────────────────────────────────────────────────────────────
   SECTION HEADERS
───────────────────────────────────────────────────────────── */

.section-header {
    background: #E0E7FF;
    color: #1E3A8A;
    padding: 12px 18px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 15px;
    margin: 18px 0 10px 0;
    letter-spacing: 0.03em;
    border: 1px solid #C7D2FE;
}

/* ─────────────────────────────────────────────────────────────
   NOTES
───────────────────────────────────────────────────────────── */

.data-note {
    font-size: 13px;
    color: #475569;
    font-style: italic;
    margin-top: 4px;
    font-weight: 500;
}

.rag-legend {
    font-size: 13px;
    color: #334155;
    font-weight: 600;
    padding: 6px 0;
}

/* ─────────────────────────────────────────────────────────────
   BUTTONS
───────────────────────────────────────────────────────────── */

.stDownloadButton button,
.stButton button {
    background-color: #1E3A8A;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stDownloadButton button:hover,
.stButton button:hover {
    background-color: #172554;
    color: white;
}

/* ─────────────────────────────────────────────────────────────
   CHARTS
───────────────────────────────────────────────────────────── */

.js-plotly-plot {
    background: white !important;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #E2E8F0;
}

/* ─────────────────────────────────────────────────────────────
   HR
───────────────────────────────────────────────────────────── */

hr {
    border-color: #CBD5E1;
}

</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────

LOST_S = [
    'Not-Interested',
    'Not Search Our Product',
    'Regret',
    'Other Department Working',
    'Wrong Number',
    'No Response on RNR',
    'Already Purchased',
    'Quoted Order Lost'
]

WON_S = [
    'Quoted Order Won And Executed'
]

HIGH_S = [
    'Quoted In Follow Up',
    'Quoted Order In Pipeline',
    'Quote In Progress',
    'Interested Quote Sent',
    'Quoted Not Picking Call',
    'Quoted Project On Hold',
    'Quoted Order Won And Executed',
    'Quoted Order Lost'
]

ADMIN = ['msafe947362','50988-Surbhi']

SRC_MAP = {
    'Just Dial':'JustDial',
    'Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart',
    'Paid classifieds':'IndiaMart',
    'Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.',
    'Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call',
    'IVR call':'IVR Call',
    'Popup Enquiry':'Website',
    'Webiste':'Website',
    'Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads',
    'Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other',
    'Aajjo':'Other',
}

MAIN_SOURCES = [
    'JustDial',
    'IndiaMart',
    'IVR Call',
    'Existing Client',
    'Ex-Client Ref.',
    'Facebook',
    'Website',
    'Google Ads',
    'Phone',
    'Email marketing'
]

# ── DATA LOADER ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading CRM data…")
def load_data(file_bytes):

    df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')

    df['Stage'] = df['FollowupStatus'].apply(
        lambda x: 'Won' if x in WON_S else (
            'Lost' if x in LOST_S else 'Active'
        )
    )

    df['Source'] = df['SourceName'].replace(SRC_MAP)

    df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)

    df['Rep'] = df['LastFollowupCreatedByName'].str.replace(
        '50988-','',regex=False
    )

    df.loc[df['is_admin'],'Rep'] = 'Admin'

    df['Source_group'] = df['Source'].apply(
        lambda x: x if x in MAIN_SOURCES else 'Other'
    )

    if 'CreatedOn' in df.columns:
        df['CreatedOn'] = pd.to_datetime(
            df['CreatedOn'],
            errors='coerce'
        )

    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

st.sidebar.markdown("## 📊 MSafe CRM Dashboard")
st.sidebar.markdown("---")

uploaded = st.sidebar.file_uploader(
    "Upload CRM export (.xls / .xlsx)",
    type=['xls','xlsx']
)

if not uploaded:

    st.markdown("""
    <div style='text-align:center; padding:80px 40px;'>

        <div style='font-size:52px;'>📂</div>

        <h2 style='color:#1E3A8A;'>
            MSafe Inside Sales Dashboard
        </h2>

        <p style='color:#475569; font-size:17px;'>
            Upload your KIT19 CRM export using the sidebar to get started.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────

df_raw = load_data(uploaded.read())

reps_df = df_raw[~df_raw['is_admin']].copy()

# ── FILTERS ───────────────────────────────────────────────────────────────────

st.sidebar.markdown("### Filters")

all_reps = sorted(reps_df['Rep'].dropna().unique().tolist())

sel_reps = st.sidebar.multiselect(
    "Rep",
    all_reps,
    default=all_reps
)

all_sources = sorted(reps_df['Source_group'].dropna().unique().tolist())

sel_sources = st.sidebar.multiselect(
    "Source",
    all_sources,
    default=all_sources
)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────

filt = reps_df.copy()

if sel_reps:
    filt = filt[filt['Rep'].isin(sel_reps)]

if sel_sources:
    filt = filt[filt['Source_group'].isin(sel_sources)]

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='
background:#1E3A8A;
padding:22px 28px;
border-radius:14px;
margin-bottom:22px;
'>

<span style='
color:white;
font-size:24px;
font-weight:800;
'>
MSafe Equipments — Inside Sales Dashboard
</span>

</div>
""", unsafe_allow_html=True)

# ── KPI SECTION ───────────────────────────────────────────────────────────────

total = len(filt)

won = (filt['Stage'] == 'Won').sum()

lost = (filt['Stage'] == 'Lost').sum()

active = (filt['Stage'] == 'Active').sum()

wr = round((won / total) * 100, 1) if total else 0

k1,k2,k3,k4 = st.columns(4)

def kpi(col, label, value, cls=''):

    col.markdown(f"""
    <div class='kpi-block'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value {cls}'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

kpi(k1, 'Total Leads', f'{total:,}')
kpi(k2, 'Won', f'{won:,}', 'green')
kpi(k3, 'Lost', f'{lost:,}', 'red')
kpi(k4, 'Win Rate', f'{wr}%', 'blue')

st.markdown("<br>", unsafe_allow_html=True)

# ── TABLE ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='section-header'>
Lead Summary
</div>
""", unsafe_allow_html=True)

show_cols = [
    c for c in [
        'Rep',
        'Source',
        'Stage',
        'FollowupStatus',
        'City',
        'State',
        'CreatedOn'
    ]
    if c in filt.columns
]

st.dataframe(
    filt[show_cols].reset_index(drop=True),
    use_container_width=True,
    height=500
)

# ── CHART ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='section-header'>
Lead Distribution by Source
</div>
""", unsafe_allow_html=True)

src = filt['Source_group'].value_counts().reset_index()

src.columns = ['Source','Count']

fig = px.pie(
    src,
    values='Count',
    names='Source',
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(size=14)
)

st.plotly_chart(fig, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("---")

st.markdown(f"""
<p style='
text-align:center;
color:#64748B;
font-size:13px;
'>
MSafe Equipments | KIT19 CRM | {len(df_raw):,} total leads
</p>
""", unsafe_allow_html=True)
