import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
 
st.set_page_config(
    page_title="MSafe Inside Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.markdown("""
<style>
 
/* ══ FORCE WHITE TEXT IN DARK HEADER ════════════════════════════════════ */
div[style*="background:#0F2044"] span,
div[style*="background:#0F2044"] * {
    color: #FFFFFF !important;
}
 
/* ══ GLOBAL FONT SIZE & TEXT COLOR ══════════════════════════════════════ */
html, body, [class*="css"], .stApp {
    font-size: 15px !important;
    color: #0F172A !important;
}
p, span, div, label, li, td, th { color: #0F172A !important; }
 
/* ══ APP BACKGROUND ══════════════════════════════════════════════════════ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F1F5F9 !important;
}
 
/* ══ TABS ════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab"] {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}
.stTabs [aria-selected="true"] {
    color: #0F2044 !important;
    border-bottom: 3px solid #0F2044 !important;
    font-weight: 800 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 4px !important;
}
 
/* ══ DOWNLOAD BUTTONS ════════════════════════════════════════════════════ */
[data-testid="stDownloadButton"] button {
    background-color: #0F2044 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover {
    background-color: #1B3A6B !important;
}
 
/* ══ SIDEBAR ════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    background-color: #0F2044 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] span {
    color: #FFFFFF !important;
    font-size: 15px !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #2D5F9E !important;
    opacity: 0.5;
}
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
    background-color: #162955 !important;
    border: 1px solid #2D5F9E !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stMultiSelect input {
    color: white !important;
    caret-color: white !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #2D5F9E !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg {
    color: white !important;
    fill: white !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #162955 !important;
    border: 2px dashed #2D5F9E !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #8BAFD4 !important;
}
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="input"],
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="base-input"] {
    background-color: #162955 !important;
    border: 1px solid #2D5F9E !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stDateInput input {
    color: white !important;
    background-color: #162955 !important;
}
 
/* ══ KPI CARDS ══════════════════════════════════════════════════════════ */
.kpi-block {
    background: white !important;
    border-radius: 12px !important;
    padding: 18px 14px !important;
    text-align: center !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10) !important;
    height: 100px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    border-top: 4px solid #CBD5E1 !important;
}
.kpi-label {
    font-size: 12px !important;
    color: #334155 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    margin-bottom: 6px !important;
}
.kpi-value {
    font-size: 30px !important;
    font-weight: 800 !important;
    color: #0F2044 !important;
    line-height: 1 !important;
}
.kpi-value.green { color: #166534 !important; }
.kpi-value.red   { color: #991B1B !important; }
.kpi-value.amber { color: #78350F !important; }
.kpi-value.blue  { color: #1E3A8A !important; }
 
/* ══ SECTION HEADERS ════════════════════════════════════════════════════ */
.sec-hdr {
    background: #1E3A8A !important;
    color: #FFFFFF !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    margin: 14px 0 8px 0 !important;
    letter-spacing: 0.02em !important;
}
.sub-note {
    font-size: 13px !important;
    color: #334155 !important;
    font-style: italic !important;
    font-weight: 500 !important;
    margin: 0 0 8px 0 !important;
}
 
/* ══ DATAFRAME — force dark readable text ════════════════════════════════ */
[data-testid="stDataFrame"] { font-size: 14px !important; }
 
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"] * {
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"] * {
    color: #0F172A !important;
    font-size: 14px !important;
}
[data-testid="stDataFrame"] [role="rowheader"],
[data-testid="stDataFrame"] [role="rowheader"] * {
    color: #0F172A !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    background-color: #E2E8F0 !important;
}
 
/* ══ EXPANDER TEXT ═══════════════════════════════════════════════════════ */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] p,
[data-testid="stExpander"] td,
[data-testid="stExpander"] th {
    color: #0F172A !important;
    font-size: 14px !important;
}
 
/* ══ ALERT / INFO BOX ════════════════════════════════════════════════════ */
[data-testid="stAlert"] { color: #0F172A !important; font-size: 14px !important; }
 
/* ══ FOOTER ══════════════════════════════════════════════════════════════ */
.footer-txt { color: #475569 !important; font-size: 13px !important; font-weight: 500 !important; }
 
/* ══ RAG LEGEND ══════════════════════════════════════════════════════════ */
.rag-legend {
    font-size: 14px !important;
    color: #1E293B !important;
    font-weight: 600 !important;
    padding: 8px 14px !important;
    background: #FFFFFF !important;
    border-radius: 8px !important;
    border-left: 4px solid #1E3A8A !important;
    margin-bottom: 10px !important;
}
 
</style>
""", unsafe_allow_html=True)
 
# ── CONSTANTS ─────────────────────────────────────────────────────────────────
LOST_S = ['Not-Interested','Not Search Our Product','Regret','Other Department Working',
          'Wrong Number','No Response on RNR','Already Purchased','Quoted Order Lost']
WON_S  = ['Quoted Order Won And Executed']
HIGH_S = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
          'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold',
          'Quoted Order Won And Executed','Quoted Order Lost']
ADMIN  = ['msafe947362','50988-Surbhi']
SRC_MAP = {
    'Just Dial':'JustDial','Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SOURCES = ['JustDial','IndiaMart','IVR Call','Existing Client',
                'Ex-Client Ref.','Facebook','Website','Google Ads','Phone','Email marketing']
 
# ── DATA LOAD ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading CRM data…")
def load_data(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')
    df['Stage']  = df['FollowupStatus'].apply(
        lambda x: 'Won' if x in WON_S else ('Lost' if x in LOST_S else 'Active'))
    df['Source'] = df['SourceName'].replace(SRC_MAP)
    df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)
    df['Rep'] = df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
    df.loc[df['is_admin'],'Rep'] = 'Admin'
    df['Source_group'] = df['Source'].apply(
        lambda x: x if x in MAIN_SOURCES else 'Other')
    if 'CreatedOn' in df.columns:
        df['CreatedOn'] = pd.to_datetime(df['CreatedOn'], errors='coerce')
    return df
 
def real_fill_pct(series):
    filled = series.apply(
        lambda x: str(x).strip() not in ['','0','0.0','nan','None','NaT','<NA>']).sum()
    return round(filled / len(series) * 100) if len(series) > 0 else 0
 
# ── COLOUR HELPERS ────────────────────────────────────────────────────────────
BASE = 'font-size:14px; font-weight:600; '
 
def c_winpct(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 5:   return BASE + 'background-color:#DCFCE7; color:#14532D;'
        elif p >= 2: return BASE + 'background-color:#FEF9C3; color:#713F12;'
        elif p == 0: return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
        return BASE + 'color:#334155;'
    except: return ''
 
def c_losspct(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 70:  return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
        elif p >= 50:return BASE + 'background-color:#FEF9C3; color:#713F12;'
        return BASE + 'background-color:#DCFCE7; color:#14532D;'
    except: return ''
 
def c_hygiene(val):
    try:
        s = str(val).replace('%','')
        if s in ('—','','nan'): return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
        p = float(s)
        if p >= 70:  return BASE + 'background-color:#DCFCE7; color:#14532D;'
        elif p >= 30:return BASE + 'background-color:#FEF9C3; color:#713F12;'
        return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
    except: return ''
 
def c_source_win(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 15:  return BASE + 'background-color:#DCFCE7; color:#14532D;'
        elif p >= 2: return BASE + 'background-color:#FEF9C3; color:#713F12;'
        elif p == 0: return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
        return BASE + 'color:#334155;'
    except: return ''
 
def c_won(val):
    try:
        v = int(val)
        if v >= 10:  return BASE + 'background-color:#DCFCE7; color:#14532D;'
        elif v >= 1: return BASE + 'background-color:#FEF9C3; color:#713F12;'
        return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
    except: return ''
 
def c_lost_rel(val, median):
    try:
        v = int(val)
        if v >= median * 1.3:  return BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
        elif v >= median * 0.7:return BASE + 'background-color:#FEF9C3; color:#713F12;'
        return BASE + 'background-color:#DCFCE7; color:#14532D;'
    except: return ''
 
def total_style(): return 'background-color:#1E3A8A; color:#FFFFFF !important; font-weight:700; font-size:14px;'
 
BASE_CELL = {"color":"#0F172A","font-size":"14px","font-weight":"500"}
 
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
 
uploaded = st.sidebar.file_uploader(
    "Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])
 
if not uploaded:
    st.markdown("""
    <div style='text-align:center; padding:100px 40px;'>
        <div style='font-size:56px;'>📂</div>
        <h2 style='color:#0F2044; margin-top:16px; font-size:26px;'>MSafe Inside Sales Dashboard</h2>
        <p style='color:#334155; font-size:16px; margin-top:10px;'>
            Upload your KIT19 CRM export from the sidebar to get started.
        </p>
        <p style='color:#64748B; font-size:14px; margin-top:6px;'>
            Accepts .xls or .xlsx files exported from KIT19.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
 
df_raw = load_data(uploaded.read())
reps_df = df_raw[~df_raw['is_admin']].copy()
 
st.sidebar.markdown("### Filters")
all_reps    = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps    = st.sidebar.multiselect("Rep", all_reps, default=all_reps)
all_sources = sorted(reps_df['Source_group'].dropna().unique().tolist())
sel_sources = st.sidebar.multiselect("Source", all_sources, default=all_sources)
sel_stages  = st.sidebar.multiselect("Stage", ['Active','Won','Lost'],
                                      default=['Active','Won','Lost'])
 
if 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any():
    mn = reps_df['CreatedOn'].min().date()
    mx = reps_df['CreatedOn'].max().date()
    date_range = st.sidebar.date_input("Date range", [mn, mx], min_value=mn, max_value=mx)
else:
    date_range = None
 
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total leads in file:** {len(df_raw):,}")
 
# Apply filters
filt = reps_df.copy()
if sel_reps:    filt = filt[filt['Rep'].isin(sel_reps)]
if sel_sources: filt = filt[filt['Source_group'].isin(sel_sources)]
if sel_stages:  filt = filt[filt['Stage'].isin(sel_stages)]
if date_range and len(date_range)==2 and 'CreatedOn' in filt.columns:
    filt = filt[(filt['CreatedOn'].dt.date >= date_range[0]) &
                (filt['CreatedOn'].dt.date <= date_range[1])]
 
# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#0F2044; padding:18px 28px; border-radius:12px;
            margin-bottom:16px; display:flex; align-items:center; gap:18px;'>
    <span style='color:#FFFFFF !important; font-size:22px; font-weight:800; letter-spacing:0.01em;'>
        MSafe Equipments — Inside Sales Dashboard
    </span>
    <span style='color:#93C5FD !important; font-size:14px; font-weight:600;'>KIT19 CRM</span>
</div>
""", unsafe_allow_html=True)
 
# ── KPI ROW ───────────────────────────────────────────────────────────────────
total  = len(filt)
won    = (filt['Stage']=='Won').sum()
lost   = (filt['Stage']=='Lost').sum()
active = (filt['Stage']=='Active').sum()
high   = filt['FollowupStatus'].isin(HIGH_S).sum()
cold   = filt['FollowupStatus'].isin(['Call Back','RNR Call Back']).sum()
wr     = round(won/total*100,1) if total else 0
q2w    = round(won/high*100,1)  if high  else 0
ec     = filt[filt['Source']=='Existing Client']
ec_wr  = round((ec['Stage']=='Won').sum()/len(ec)*100,1) if len(ec) else 0
 
cols = st.columns(9)
def kpi(col, label, value, cls=''):
    col.markdown(f"""<div class='kpi-block'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value {cls}'>{value}</div>
    </div>""", unsafe_allow_html=True)
 
kpi(cols[0],'Total Leads',  f'{total:,}')
kpi(cols[1],'Won',          f'{won:,}',   'green')
kpi(cols[2],'Lost',         f'{lost:,}',  'red')
kpi(cols[3],'Active',       f'{active:,}','amber')
kpi(cols[4],'Win Rate',     f'{wr}%',     'blue')
kpi(cols[5],'Quote → Win',  f'{q2w}%',   'green')
kpi(cols[6],'High Intent',  f'{high:,}',  'amber')
kpi(cols[7],'Cold CB/RNR',  f'{cold:,}',  'red')
kpi(cols[8],'Ex.Client Win',f'{ec_wr}%', 'green')
 
st.markdown("<br>", unsafe_allow_html=True)
 
# RAG legend
st.markdown("""
<div class='rag-legend'>
    🟢 Green = Good &nbsp;&nbsp;&nbsp;
    🟡 Amber = Needs attention &nbsp;&nbsp;&nbsp;
    🔴 Red = Problem / Act now
</div>
""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Leads by Rep & Source",
    "🏆  Rep Performance",
    "🧹  CRM Hygiene",
    "🔄  Pipeline & Lost Reasons",
])
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — REP × SOURCE CROSS-TAB
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='sec-hdr'>Leads by Rep & Source</div>", unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "Number of leads each rep received from each source.&nbsp; "
                "🟢 Existing Client / Ex-Client Ref = quality sources with high win rates.&nbsp; "
                "🔴 JustDial / IndiaMart = high volume, very low conversion.</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        pivot = pd.crosstab(filt['Rep'], filt['Source_group'],
                            margins=True, margins_name='TOTAL')
        preferred = ['JustDial','IndiaMart','IVR Call','Existing Client',
                     'Ex-Client Ref.','Facebook','Website','Google Ads',
                     'Phone','Email marketing','Other']
        ordered = [c for c in preferred if c in pivot.columns]
        ordered += [c for c in pivot.columns if c not in ordered and c!='TOTAL']
        if 'TOTAL' in pivot.columns: ordered.append('TOTAL')
        pivot = pivot[ordered]
 
        def style_pivot(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            quality  = ['Existing Client','Ex-Client Ref.']
            bad_src  = ['JustDial','IndiaMart','Facebook']
            for col in df.columns:
                if col in quality:
                    styles[col] = df[col].apply(
                        lambda v: BASE + 'background-color:#DCFCE7; color:#14532D;'
                        if (isinstance(v,int) and v>0) else BASE + 'color:#0F172A;')
                elif col in bad_src:
                    styles[col] = df[col].apply(
                        lambda v: BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
                        if (isinstance(v,int) and v>0) else BASE + 'color:#0F172A;')
                elif col == 'TOTAL':
                    styles[col] = BASE + 'background-color:#DBEAFE; color:#1E3A8A; font-weight:700;'
                else:
                    styles[col] = BASE + 'color:#0F172A;'
            if 'TOTAL' in df.index:
                styles.loc['TOTAL'] = BASE + 'background-color:#1E3A8A; color:#FFFFFF; font-weight:700;'
            return styles
 
        fmt = lambda x: '' if x==0 else f'{x:,}'
        st.dataframe(
            pivot.style.set_properties(**BASE_CELL).apply(style_pivot, axis=None).format(fmt),
            use_container_width=True, height=460)
 
        st.download_button("⬇ Download CSV", pivot.to_csv(), "rep_source.csv", "text/csv")
 
        # Source win rate
        st.markdown("<div class='sec-hdr'>Source Win Rate</div>", unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Win % 🟢 ≥15% &nbsp; 🟡 2–14% &nbsp; 🔴 0%</p>",
                    unsafe_allow_html=True)
 
        sw = filt.groupby('Source_group').agg(
            Leads =('Stage','count'),
            Won   =('Stage', lambda x:(x=='Won').sum()),
            Lost  =('Stage', lambda x:(x=='Lost').sum()),
            Active=('Stage', lambda x:(x=='Active').sum()),
        ).reset_index().rename(columns={'Source_group':'Source'})
        sw['Win %']  = (sw['Won']/sw['Leads']*100).round(1).astype(str)+'%'
        sw['Loss %'] = (sw['Lost']/sw['Leads']*100).round(1).astype(str)+'%'
        sw = sw[sw['Leads']>2].sort_values('Won',ascending=False).set_index('Source')
 
        def style_sw(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                styles.loc[idx,'Win %']  = c_source_win(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = c_losspct(df.loc[idx,'Loss %'])
                styles.loc[idx,'Won']    = c_won(df.loc[idx,'Won'])
                styles.loc[idx,'Lost']   = BASE + 'color:#7F1D1D;'
                styles.loc[idx,'Leads']  = BASE + 'color:#0F172A; font-weight:700;'
                styles.loc[idx,'Active'] = BASE + 'color:#713F12;'
            return styles
 
        st.dataframe(
            sw.style.set_properties(**BASE_CELL).apply(style_sw, axis=None)
                    .format({'Leads':'{:,}','Won':'{:,}','Lost':'{:,}','Active':'{:,}'}),
            use_container_width=True, height=340)
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — REP PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='sec-hdr'>Rep Performance — Active / Won / Lost</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "Win % 🟢 ≥5% &nbsp; 🟡 2–4.9% &nbsp; 🔴 0% &nbsp;|&nbsp; "
                "Loss % 🟢 &lt;50% &nbsp; 🟡 50–69% &nbsp; 🔴 ≥70% &nbsp;|&nbsp; "
                "Won count 🟢 ≥10 &nbsp; 🟡 1–9 &nbsp; 🔴 0 &nbsp;|&nbsp; "
                "Lost count colored relative to team median.</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        awl = filt.groupby('Rep').agg(
            Total  =('Stage','count'),
            Active =('Stage', lambda x:(x=='Active').sum()),
            Won    =('Stage', lambda x:(x=='Won').sum()),
            Lost   =('Stage', lambda x:(x=='Lost').sum()),
        ).reset_index()
        awl['Win %']  = (awl['Won']  /awl['Total']*100).round(1).astype(str)+'%'
        awl['Loss %'] = (awl['Lost'] /awl['Total']*100).round(1).astype(str)+'%'
        awl = awl.sort_values('Won',ascending=False)
 
        lost_median = awl['Lost'].median()
 
        tot_row = pd.DataFrame([{
            'Rep':'TOTAL','Total':awl['Total'].sum(),'Active':awl['Active'].sum(),
            'Won':awl['Won'].sum(),'Lost':awl['Lost'].sum(),
            'Win %': f"{round(awl['Won'].sum()/awl['Total'].sum()*100,1)}%",
            'Loss %':f"{round(awl['Lost'].sum()/awl['Total'].sum()*100,1)}%",
        }])
        awl_d = pd.concat([awl, tot_row], ignore_index=True).set_index('Rep')
 
        def style_awl(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                if idx=='TOTAL':
                    styles.loc[idx] = total_style()
                    continue
                styles.loc[idx,'Total']  = BASE + 'color:#0F172A; font-weight:700;'
                styles.loc[idx,'Active'] = BASE + 'background-color:#EFF6FF; color:#1E3A8A;'
                styles.loc[idx,'Won']    = c_won(df.loc[idx,'Won'])
                styles.loc[idx,'Lost']   = c_lost_rel(df.loc[idx,'Lost'], lost_median)
                styles.loc[idx,'Win %']  = c_winpct(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = c_losspct(df.loc[idx,'Loss %'])
            return styles
 
        st.dataframe(
            awl_d.style.set_properties(**BASE_CELL).apply(style_awl, axis=None)
                       .format({'Total':'{:,}','Active':'{:,}','Won':'{:,}','Lost':'{:,}'}),
            use_container_width=True, height=500)
 
        st.download_button("⬇ Download CSV", awl_d.to_csv(),
                           "rep_performance.csv", "text/csv")
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — CRM HYGIENE
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='sec-hdr'>CRM Data Hygiene — % of Leads with Field Filled</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "🟢 ≥70% filled &nbsp; 🟡 30–69% &nbsp; 🔴 &lt;30%  &nbsp;|&nbsp;  "
                "Score = average across all tracked fields. Higher = better CRM discipline.</p>",
                unsafe_allow_html=True)
 
    HYGIENE_FIELDS = {
        'Product':       'product_name',
        'Biz Type':      'Q_Type',
        'City':          'City',
        'Followup Date': 'FollowupDate',
        'Quote Value':   'quotation_total_amount',
    }
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        rows = []
        for rep in sorted(filt['Rep'].unique()):
            rd = filt[filt['Rep']==rep]
            row = {'Rep':rep, 'Leads':len(rd)}
            pcts = []
            for label,field in HYGIENE_FIELDS.items():
                if field in rd.columns:
                    p = real_fill_pct(rd[field].fillna(''))
                    row[label] = f'{p}%'
                    pcts.append(p)
                else:
                    row[label] = '—'
            row['Score'] = f"{round(np.mean(pcts))}%" if pcts else '—'
            rows.append(row)
 
        ov = {'Rep':'OVERALL','Leads':len(filt)}
        pcts = []
        for label,field in HYGIENE_FIELDS.items():
            if field in filt.columns:
                p = real_fill_pct(filt[field].fillna(''))
                ov[label] = f'{p}%'; pcts.append(p)
            else:
                ov[label] = '—'
        ov['Score'] = f"{round(np.mean(pcts))}%" if pcts else '—'
        rows.append(ov)
 
        hyg = pd.DataFrame(rows).set_index('Rep')
 
        def style_hyg(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                if idx=='OVERALL':
                    styles.loc[idx] = total_style()
                    continue
                styles.loc[idx,'Leads'] = BASE + 'color:#0F172A; font-weight:700;'
                for col in list(HYGIENE_FIELDS.keys()) + ['Score']:
                    if col in df.columns:
                        styles.loc[idx,col] = c_hygiene(df.loc[idx,col])
            return styles
 
        st.dataframe(
            hyg.style.set_properties(**BASE_CELL).apply(style_hyg, axis=None),
            use_container_width=True, height=500)
 
        st.download_button("⬇ Download CSV", hyg.to_csv(), "crm_hygiene.csv", "text/csv")
 
        with st.expander("What do these fields mean?"):
            st.markdown("""
| Field | What it tracks | Why it matters |
|---|---|---|
| **Product** | Which product the lead enquired about | Without this, no product-level reporting is possible |
| **Biz Type** | Sale or Rental | Two different pipelines — mixing them makes reporting useless |
| **City** | Contact city of the lead | Determines which MSafe yard should fulfil the order |
| **Followup Date** | Whether a next action date is set | No follow-up date = lead is being left to die |
| **Quote Value** | ₹ value of quotation sent | 0% across all reps — pipeline worth is completely unknown |
            """)
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — PIPELINE & LOST REASONS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    c_left, c_right = st.columns(2)
 
    with c_left:
        st.markdown("<div class='sec-hdr'>Active Pipeline Breakdown</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "🟢 Quoted stages = hot leads &nbsp; "
                    "🟡 Interested / Catalogue = engaged &nbsp; "
                    "🔴 Call Back / RNR = cold / stuck</p>", unsafe_allow_html=True)
 
        active_f = filt[filt['Stage']=='Active']
        if len(active_f)==0:
            st.info("No active leads.")
        else:
            pipe_df = (active_f['FollowupStatus'].value_counts()
                       .reset_index()
                       .rename(columns={'FollowupStatus':'Status','count':'Count'}))
            pipe_df['% of Active'] = (pipe_df['Count']/len(active_f)*100).round(1).astype(str)+'%'
            pipe_df = pipe_df.set_index('Status')
 
            def style_pipe(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                for idx in df.index:
                    if 'RNR' in idx or 'Call Back' in idx:
                        styles.loc[idx] = BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
                    elif any(x in idx for x in ['Quoted','Quote']):
                        styles.loc[idx] = BASE + 'background-color:#DCFCE7; color:#14532D;'
                    elif any(x in idx for x in ['Interested','Catalogue','MS Req']):
                        styles.loc[idx] = BASE + 'background-color:#FEF9C3; color:#713F12;'
                    else:
                        styles.loc[idx] = BASE + 'color:#0F172A;'
                return styles
 
            st.dataframe(
                pipe_df.style.set_properties(**BASE_CELL).apply(style_pipe, axis=None)
                             .format({'Count':'{:,}'}),
                use_container_width=True, height=500)
            st.download_button("⬇ Download CSV", pipe_df.to_csv(), "pipeline.csv", "text/csv")
 
    with c_right:
        st.markdown("<div class='sec-hdr'>Why Leads Are Lost</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Sorted by volume. 🔴 Top bucket &nbsp; 🟡 Mid &nbsp; lighter = smaller volume.</p>",
                    unsafe_allow_html=True)
 
        lost_f = filt[filt['Stage']=='Lost']
        if len(lost_f)==0:
            st.info("No lost leads.")
        else:
            lost_df = (lost_f['FollowupStatus'].value_counts()
                       .reset_index()
                       .rename(columns={'FollowupStatus':'Lost Reason','count':'Count'}))
            lost_df['% of Lost'] = (lost_df['Count']/len(lost_f)*100).round(1).astype(str)+'%'
            lost_df = lost_df.set_index('Lost Reason')
            max_v = lost_df['Count'].max()
 
            def style_lost(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                for idx in df.index:
                    v = df.loc[idx,'Count']
                    if v >= max_v * 0.6:
                        styles.loc[idx] = BASE + 'background-color:#FEE2E2; color:#7F1D1D;'
                    elif v >= max_v * 0.3:
                        styles.loc[idx] = BASE + 'background-color:#FEF9C3; color:#713F12;'
                    else:
                        styles.loc[idx] = BASE + 'color:#0F172A;'
                return styles
 
            st.dataframe(
                lost_df.style.set_properties(**BASE_CELL).apply(style_lost, axis=None)
                             .format({'Count':'{:,}'}),
                use_container_width=True, height=500)
            st.download_button("⬇ Download CSV", lost_df.to_csv(), "lost_reasons.csv", "text/csv")
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p class='footer-txt' style='text-align:center;'>"
    f"MSafe Equipments &nbsp;|&nbsp; KIT19 CRM &nbsp;|&nbsp; "
    f"{len(df_raw):,} leads in file &nbsp;|&nbsp; "
    f"{len(filt):,} leads shown with current filters"
    f"</p>", unsafe_allow_html=True)
