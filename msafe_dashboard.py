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
/* Global font size bump */
html, body, [class*="css"] { font-size: 15px !important; }
 
[data-testid="stAppViewContainer"] { background-color: #F0F4F8; }
[data-testid="stSidebar"] { background-color: #0F2044; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 15px !important; }
[data-testid="stSidebar"] .stMultiSelect > div > div { background: #1B3A6B; }
 
/* Tab labels larger */
button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; }
 
/* Dataframe text */
[data-testid="stDataFrame"] * { font-size: 14px !important; }
 
.kpi-block {
    background: white;
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.10);
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-label {
    font-size: 12px;
    color: #334155;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.kpi-value { font-size: 30px; font-weight: 800; color: #0F2044; line-height: 1; }
.kpi-value.green { color: #166534; }
.kpi-value.red   { color: #991B1B; }
.kpi-value.amber { color: #78350F; }
.kpi-value.blue  { color: #1E3A8A; }
 
.section-header {
    background: #1E3A8A;
    color: #FFFFFF;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 15px;
    margin: 18px 0 10px 0;
    letter-spacing: 0.03em;
}
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
 
# ── RAG COLOR HELPERS ─────────────────────────────────────────────────────────
# All styles use dark text on light backgrounds for readability
 
def rag_winrate(val):
    """Win %: green ≥5%, amber 1-4.9%, red 0%"""
    try:
        p = float(str(val).replace('%',''))
        if p >= 5:   return 'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
        elif p >= 1: return 'background-color:#FEF9C3; color:#713F12; font-weight:700; font-size:14px'
        return             'background-color:#FEE2E2; color:#7F1D1D; font-weight:700; font-size:14px'
    except: return ''
 
def rag_lossrate(val):
    """Loss %: red ≥70%, amber 50-69%, green <50%"""
    try:
        p = float(str(val).replace('%',''))
        if p >= 70:  return 'background-color:#FEE2E2; color:#7F1D1D; font-weight:700; font-size:14px'
        elif p >= 50:return 'background-color:#FEF9C3; color:#713F12; font-weight:700; font-size:14px'
        return             'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
    except: return ''
 
def rag_hygiene(val):
    """Hygiene %: green ≥70%, amber 30-69%, red <30%"""
    try:
        s = str(val).replace('%','')
        if s in ('—','nan',''): return 'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
        p = float(s)
        if p >= 70:  return 'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
        elif p >= 30:return 'background-color:#FEF9C3; color:#713F12; font-size:14px'
        return             'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
    except: return ''
 
def rag_won_count(val):
    """Won count: green ≥10, amber 1-9, red 0"""
    try:
        v = int(val)
        if v >= 10:  return 'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
        elif v >= 1: return 'background-color:#FEF9C3; color:#713F12; font-size:14px'
        return             'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
    except: return ''
 
def rag_lost_count(val, median=None):
    """Lost count: red = high, amber = medium, green = low (relative to median)"""
    try:
        v = int(val)
        if median is None: return ''
        if v >= median * 1.3: return 'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
        elif v >= median * 0.7: return 'background-color:#FEF9C3; color:#713F12; font-size:14px'
        return 'background-color:#DCFCE7; color:#14532D; font-size:14px'
    except: return ''
 
def rag_source_winrate(val):
    """Source win %: green ≥10%, amber 1-9.9%, red 0%"""
    try:
        p = float(str(val).replace('%',''))
        if p >= 10:  return 'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
        elif p >= 1: return 'background-color:#FEF9C3; color:#713F12; font-size:14px'
        return             'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
    except: return ''
 
def total_row_style():
    return 'background-color:#1E3A8A; color:#FFFFFF; font-weight:700; font-size:14px'
 
# ── DATA LOADER ───────────────────────────────────────────────────────────────
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
 
def to_excel(df_dict):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        for sheet, df in df_dict.items():
            df.to_excel(w, sheet_name=sheet[:31], index=True)
    return buf.getvalue()
 
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM Dashboard")
st.sidebar.markdown("---")
 
uploaded = st.sidebar.file_uploader(
    "Upload CRM export (.xls / .xlsx)",
    type=['xls','xlsx'],
    help="Drop your KIT19 export here to refresh the data"
)
 
if not uploaded:
    st.markdown("""
    <div style='text-align:center; padding:80px 40px;'>
        <div style='font-size:52px;'>📂</div>
        <h2 style='color:#0F2044; font-size:26px;'>MSafe Inside Sales Dashboard</h2>
        <p style='color:#334155; font-size:17px;'>
            Upload your KIT19 CRM export using the sidebar to get started.
        </p>
        <p style='color:#64748B; font-size:14px;'>
            Accepts .xls or .xlsx files exported from KIT19.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
 
# Load
df_raw = load_data(uploaded.read())
reps_df = df_raw[~df_raw['is_admin']].copy()
 
# Sidebar filters
st.sidebar.markdown("### Filters")
 
all_reps = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps = st.sidebar.multiselect("Rep", all_reps, default=all_reps)
 
all_sources = sorted(reps_df['Source_group'].dropna().unique().tolist())
sel_sources = st.sidebar.multiselect("Source", all_sources, default=all_sources)
 
all_stages = ['Active','Won','Lost']
sel_stages = st.sidebar.multiselect("Stage", all_stages, default=all_stages)
 
if 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any():
    min_d = reps_df['CreatedOn'].min().date()
    max_d = reps_df['CreatedOn'].max().date()
    date_range = st.sidebar.date_input("Date range", [min_d, max_d],
                                        min_value=min_d, max_value=max_d)
else:
    date_range = None
 
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total leads:** {len(df_raw):,}")
st.sidebar.markdown(f"**Filtered reps:** {len(sel_reps)} of {len(all_reps)}")
 
# Apply filters
filt = reps_df.copy()
if sel_reps:    filt = filt[filt['Rep'].isin(sel_reps)]
if sel_sources: filt = filt[filt['Source_group'].isin(sel_sources)]
if sel_stages:  filt = filt[filt['Stage'].isin(sel_stages)]
if date_range and len(date_range) == 2 and 'CreatedOn' in filt.columns:
    filt = filt[
        (filt['CreatedOn'].dt.date >= date_range[0]) &
        (filt['CreatedOn'].dt.date <= date_range[1])
    ]
 
# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:#0F2044; padding:20px 28px; border-radius:12px; margin-bottom:18px;'>
    <span style='color:#FFFFFF; font-size:22px; font-weight:800; letter-spacing:0.02em;'>
        MSafe Equipments — Inside Sales Dashboard
    </span>
    <span style='color:#93C5FD; font-size:14px; margin-left:18px; font-weight:600;'>KIT19 CRM</span>
</div>
""", unsafe_allow_html=True)
 
# ── KPI CARDS ─────────────────────────────────────────────────────────────────
total = len(filt)
won   = (filt['Stage']=='Won').sum()
lost  = (filt['Stage']=='Lost').sum()
active= (filt['Stage']=='Active').sum()
high  = filt['FollowupStatus'].isin(HIGH_S).sum()
cold  = filt['FollowupStatus'].isin(['Call Back','RNR Call Back']).sum()
wr    = round(won/total*100,1) if total else 0
q2w   = round(won/high*100,1)  if high  else 0
ec_w  = filt[filt['Source']=='Existing Client']
ec_wr = round((ec_w['Stage']=='Won').sum() / len(ec_w) * 100, 1) if len(ec_w) else 0
 
k1,k2,k3,k4,k5,k6,k7,k8,k9 = st.columns(9)
def kpi(col, label, value, cls=''):
    col.markdown(f"""
    <div class='kpi-block'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value {cls}'>{value}</div>
    </div>""", unsafe_allow_html=True)
 
kpi(k1,'Total Leads', f'{total:,}')
kpi(k2,'Won',         f'{won:,}',   'green')
kpi(k3,'Lost',        f'{lost:,}',  'red')
kpi(k4,'Active',      f'{active:,}','amber')
kpi(k5,'Win Rate',    f'{wr}%',     'blue')
kpi(k6,'Quote→Win',   f'{q2w}%',   'green')
kpi(k7,'High Intent', f'{high:,}',  'amber')
kpi(k8,'Cold CB/RNR', f'{cold:,}',  'red')
kpi(k9,'ExClient Win',f'{ec_wr}%', 'green')
 
st.markdown("<br>", unsafe_allow_html=True)
 
# RAG legend shown once at top
st.markdown("""
<div class='rag-legend'>
    🟢 Green = Good &nbsp;&nbsp;
    🟡 Amber = Needs attention &nbsp;&nbsp;
    🔴 Red = Problem area
</div>
""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Leads by Rep & Source",
    "🏆 Rep Performance",
    "🧹 CRM Hygiene",
    "🔄 Pipeline & Lost",
    "📈 Charts"
])
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REP × SOURCE CROSS-TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Leads by Rep & Source</div>", unsafe_allow_html=True)
    st.markdown("<p class='data-note'>Lead count per rep per source. "
                "🟢 Existing Client & Ex-Client Ref = quality sources with high win rates. "
                "🔴 JustDial / IndiaMart = high volume but very low conversion.</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        pivot = pd.crosstab(filt['Rep'], filt['Source_group'], margins=True, margins_name='TOTAL')
 
        preferred = ['JustDial','IndiaMart','IVR Call','Existing Client',
                     'Ex-Client Ref.','Facebook','Website','Google Ads','Phone',
                     'Email marketing','Other']
        ordered = [c for c in preferred if c in pivot.columns]
        ordered += [c for c in pivot.columns if c not in ordered and c != 'TOTAL']
        if 'TOTAL' in pivot.columns: ordered.append('TOTAL')
        pivot = pivot[ordered]
 
        def style_pivot(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            quality  = ['Existing Client','Ex-Client Ref.']
            bad_src  = ['JustDial','IndiaMart','Facebook']
            for col in df.columns:
                if col in quality:
                    styles[col] = df[col].apply(
                        lambda v: 'background-color:#DCFCE7; color:#14532D; font-weight:700; font-size:14px'
                        if v and v != 0 else 'font-size:14px')
                elif col in bad_src:
                    styles[col] = df[col].apply(
                        lambda v: 'background-color:#FEE2E2; color:#7F1D1D; font-size:14px'
                        if v and v != 0 else 'font-size:14px')
                else:
                    styles[col] = 'font-size:14px; color:#1E293B'
            if 'TOTAL' in df.columns:
                styles['TOTAL'] = 'background-color:#DBEAFE; color:#1E3A8A; font-weight:700; font-size:14px'
            if 'TOTAL' in df.index:
                styles.loc['TOTAL'] = 'background-color:#1E3A8A; color:#FFFFFF; font-weight:700; font-size:14px'
            return styles
 
        styled = pivot.style.apply(style_pivot, axis=None).format(
            lambda x: '' if x==0 else f'{x:,}')
        st.dataframe(styled, use_container_width=True, height=460)
 
        csv = pivot.to_csv()
        st.download_button("⬇ Download table (CSV)", csv,
                           file_name="rep_source_breakdown.csv", mime="text/csv")
 
        st.markdown("<div class='section-header'>Source Distribution by Rep</div>", unsafe_allow_html=True)
        plot_df = filt[filt['Rep']!='TOTAL'].copy()
        fig = px.bar(plot_df, x='Rep', color='Source_group',
                     barmode='stack', height=420,
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={'Source_group':'Source','Rep':'Rep','count':'Leads'})
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                          legend_title='Source', margin=dict(l=0,r=0,t=10,b=0),
                          font=dict(family='Arial', size=14))
        st.plotly_chart(fig, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REP PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>Rep Performance — Active / Won / Lost</div>", unsafe_allow_html=True)
    st.markdown("<p class='data-note'>"
                "Win % 🟢 ≥5% &nbsp; 🟡 1–4.9% &nbsp; 🔴 0% &nbsp;|&nbsp; "
                "Loss % 🟢 &lt;50% &nbsp; 🟡 50–69% &nbsp; 🔴 ≥70% &nbsp;|&nbsp; "
                "Won count 🟢 ≥10 &nbsp; 🟡 1–9 &nbsp; 🔴 0"
                "</p>", unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        awl = filt.groupby('Rep').agg(
            Total  =('Stage','count'),
            Active =('Stage', lambda x:(x=='Active').sum()),
            Won    =('Stage', lambda x:(x=='Won').sum()),
            Lost   =('Stage', lambda x:(x=='Lost').sum()),
        ).reset_index()
        awl['Win %']  = (awl['Won']  / awl['Total'] * 100).round(1).astype(str) + '%'
        awl['Loss %'] = (awl['Lost'] / awl['Total'] * 100).round(1).astype(str) + '%'
        awl = awl.sort_values('Won', ascending=False)
 
        tot_row = pd.DataFrame([{
            'Rep':'TOTAL', 'Total':awl['Total'].sum(), 'Active':awl['Active'].sum(),
            'Won':awl['Won'].sum(), 'Lost':awl['Lost'].sum(),
            'Win %': f"{round(awl['Won'].sum()/awl['Total'].sum()*100,1)}%",
            'Loss %':f"{round(awl['Lost'].sum()/awl['Total'].sum()*100,1)}%",
        }])
        awl_disp = pd.concat([awl, tot_row], ignore_index=True).set_index('Rep')
 
        lost_median = awl['Lost'].median()
 
        def style_awl(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                if idx == 'TOTAL':
                    styles.loc[idx] = total_row_style()
                    continue
                styles.loc[idx,'Won']    = rag_won_count(df.loc[idx,'Won'])
                styles.loc[idx,'Lost']   = rag_lost_count(df.loc[idx,'Lost'], lost_median)
                styles.loc[idx,'Active'] = 'background-color:#EFF6FF; color:#1E3A8A; font-size:14px'
                styles.loc[idx,'Total']  = 'font-size:14px; color:#1E293B; font-weight:600'
                styles.loc[idx,'Win %']  = rag_winrate(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = rag_lossrate(df.loc[idx,'Loss %'])
            return styles
 
        st.dataframe(
            awl_disp.style.apply(style_awl, axis=None)
                .format({'Total':'{:,}','Active':'{:,}','Won':'{:,}','Lost':'{:,}'}),
            use_container_width=True, height=460)
 
        st.download_button("⬇ Download (CSV)", awl_disp.to_csv(),
                           file_name="rep_performance.csv", mime="text/csv")
 
        fig2 = px.bar(awl[awl['Rep']!='TOTAL'],
                      x='Rep', y='Won', text='Won', color='Won',
                      color_continuous_scale=[[0,'#DCFCE7'],[1,'#14532D']],
                      height=360, title='Wins by Rep')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                           showlegend=False, margin=dict(l=0,r=0,t=50,b=0),
                           font=dict(family='Arial', size=14), coloraxis_showscale=False)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CRM HYGIENE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>CRM Data Hygiene — % of Leads with Field Filled</div>", unsafe_allow_html=True)
    st.markdown("<p class='data-note'>"
                "🟢 ≥70% filled &nbsp;&nbsp; 🟡 30–69% &nbsp;&nbsp; 🔴 &lt;30% &nbsp;&nbsp; "
                "Score = average across all fields. Higher is better."
                "</p>", unsafe_allow_html=True)
 
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
            rep_d = filt[filt['Rep']==rep]
            row = {'Rep': rep, 'Leads': len(rep_d)}
            for label, field in HYGIENE_FIELDS.items():
                if field in rep_d.columns:
                    row[label] = f"{real_fill_pct(rep_d[field].fillna(''))}%"
                else:
                    row[label] = '—'
            pcts = []
            for label in HYGIENE_FIELDS:
                v = row[label].replace('%','')
                try: pcts.append(float(v))
                except: pass
            row['Score'] = f"{round(np.mean(pcts))}%" if pcts else '—'
            rows.append(row)
 
        overall = {'Rep':'OVERALL', 'Leads': len(filt)}
        for label, field in HYGIENE_FIELDS.items():
            if field in filt.columns:
                overall[label] = f"{real_fill_pct(filt[field].fillna(''))}%"
            else:
                overall[label] = '—'
        pcts = []
        for label in HYGIENE_FIELDS:
            v = overall[label].replace('%','')
            try: pcts.append(float(v))
            except: pass
        overall['Score'] = f"{round(np.mean(pcts))}%" if pcts else '—'
        rows.append(overall)
 
        hyg_df = pd.DataFrame(rows).set_index('Rep')
 
        def style_hyg(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                if idx == 'OVERALL':
                    styles.loc[idx] = total_row_style()
                    continue
                for col in df.columns:
                    if col == 'Leads':
                        styles.loc[idx, col] = 'font-size:14px; color:#1E293B; font-weight:600'
                    else:
                        styles.loc[idx, col] = rag_hygiene(df.loc[idx, col])
            return styles
 
        st.dataframe(
            hyg_df.style.apply(style_hyg, axis=None),
            use_container_width=True, height=460)
 
        st.download_button("⬇ Download (CSV)", hyg_df.to_csv(),
                           file_name="crm_hygiene.csv", mime="text/csv")
 
        st.markdown("<div class='section-header'>Hygiene Heatmap</div>", unsafe_allow_html=True)
        heat_data = hyg_df.drop(index='OVERALL', errors='ignore').drop(columns=['Leads','Score'], errors='ignore').copy()
        heat_num = heat_data.map(
            lambda v: float(str(v).replace('%',''))
            if v is not None and str(v) not in ['','nan','—'] else 0
        )
        fig3 = px.imshow(heat_num, color_continuous_scale='RdYlGn',
                         zmin=0, zmax=100, aspect='auto',
                         text_auto=True, height=400)
        fig3.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                           paper_bgcolor='#F0F4F8',
                           font=dict(family='Arial', size=14))
        st.plotly_chart(fig3, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PIPELINE & LOST REASONS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c_pipe, c_lost = st.columns(2)
 
    with c_pipe:
        st.markdown("<div class='section-header'>Active Pipeline Breakdown</div>", unsafe_allow_html=True)
        st.markdown("<p class='data-note'>"
                    "🟢 Quote stage = hot leads &nbsp; 🟡 Interested = engaged &nbsp; 🔴 RNR/Call Back = stuck"
                    "</p>", unsafe_allow_html=True)
        active_filt = filt[filt['Stage']=='Active']
        if len(active_filt) == 0:
            st.info("No active leads in current filters.")
        else:
            pipe_df = (active_filt['FollowupStatus']
                       .value_counts()
                       .reset_index()
                       .rename(columns={'FollowupStatus':'Status','count':'Count'}))
            pipe_df['%'] = (pipe_df['Count'] / pipe_df['Count'].sum() * 100).round(1).astype(str) + '%'
 
            def color_pipe(row):
                s = row['Status']
                base = 'font-size:14px; '
                if 'RNR' in s or 'Call Back' in s:
                    return [base + 'background-color:#FEE2E2; color:#7F1D1D']*len(row)
                elif 'Quoted' in s or 'Quote' in s:
                    return [base + 'background-color:#DCFCE7; color:#14532D; font-weight:700']*len(row)
                elif 'Interested' in s or 'Catalogue' in s:
                    return [base + 'background-color:#FEF9C3; color:#713F12']*len(row)
                return [base + 'color:#1E293B']*len(row)
 
            st.dataframe(
                pipe_df.style.apply(color_pipe, axis=1),
                use_container_width=True, hide_index=True, height=420)
 
            fig4 = px.pie(pipe_df.head(8), values='Count', names='Status',
                          hole=0.5, height=320,
                          color_discrete_sequence=px.colors.qualitative.Set3)
            fig4.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                               paper_bgcolor='#F0F4F8', showlegend=True,
                               legend=dict(font=dict(size=13)),
                               font=dict(family='Arial', size=14))
            st.plotly_chart(fig4, use_container_width=True)
 
    with c_lost:
        st.markdown("<div class='section-header'>Lost Reasons</div>", unsafe_allow_html=True)
        st.markdown("<p class='data-note'>"
                    "🔴 All lost — ranked by volume. Regret & Quote Lost = most recoverable."
                    "</p>", unsafe_allow_html=True)
        lost_filt = filt[filt['Stage']=='Lost']
        if len(lost_filt) == 0:
            st.info("No lost leads in current filters.")
        else:
            lost_df = (lost_filt['FollowupStatus']
                       .value_counts()
                       .reset_index()
                       .rename(columns={'FollowupStatus':'Reason','count':'Count'}))
            lost_df['%'] = (lost_df['Count'] / lost_df['Count'].sum() * 100).round(1).astype(str) + '%'
            max_lost = lost_df['Count'].max()
 
            def color_lost(row):
                v = row['Count']
                base = 'font-size:14px; '
                if v >= max_lost * 0.6:
                    return [base + 'background-color:#FEE2E2; color:#7F1D1D; font-weight:700']*len(row)
                elif v >= max_lost * 0.3:
                    return [base + 'background-color:#FEF9C3; color:#713F12']*len(row)
                return [base + 'color:#1E293B']*len(row)
 
            st.dataframe(
                lost_df.style.apply(color_lost, axis=1),
                use_container_width=True, hide_index=True, height=420)
 
            fig5 = px.bar(lost_df, x='Count', y='Reason', orientation='h',
                          height=320, text='Count', color='Count',
                          color_continuous_scale=[[0,'#FEF9C3'],[1,'#991B1B']])
            fig5.update_layout(margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                               plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                               yaxis={'categoryorder':'total ascending'},
                               coloraxis_showscale=False,
                               font=dict(family='Arial', size=14))
            fig5.update_traces(textposition='outside')
            st.plotly_chart(fig5, use_container_width=True)
 
        # Source win rate table
        st.markdown("<div class='section-header'>Source Win Rate</div>", unsafe_allow_html=True)
        st.markdown("<p class='data-note'>"
                    "Win % 🟢 ≥10% &nbsp; 🟡 1–9.9% &nbsp; 🔴 0%"
                    "</p>", unsafe_allow_html=True)
        sw = filt.groupby('Source_group').agg(
            Leads=('Stage','count'),
            Won  =('Stage', lambda x:(x=='Won').sum()),
            Lost =('Stage', lambda x:(x=='Lost').sum()),
        ).reset_index()
        sw['Win %']  = (sw['Won']/sw['Leads']*100).round(1).astype(str) + '%'
        sw['Loss %'] = (sw['Lost']/sw['Leads']*100).round(1).astype(str) + '%'
        sw_disp = sw[sw['Leads']>3].sort_values('Won', ascending=False).set_index('Source_group')
 
        def style_sw(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                styles.loc[idx,'Won']    = rag_won_count(df.loc[idx,'Won'])
                styles.loc[idx,'Win %']  = rag_source_winrate(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = rag_lossrate(df.loc[idx,'Loss %'])
                styles.loc[idx,'Leads']  = 'font-size:14px; color:#1E293B; font-weight:600'
                styles.loc[idx,'Lost']   = 'font-size:14px; color:#7F1D1D'
            return styles
 
        st.dataframe(
            sw_disp.style.apply(style_sw, axis=None)
                .format({'Leads':'{:,}','Won':'{:,}','Lost':'{:,}'}),
            use_container_width=True, height=320)
 
        fig6 = px.bar(sw[sw['Leads']>3].sort_values('Win %'),
                      x=sw[sw['Leads']>3].sort_values('Win %')['Won']/sw[sw['Leads']>3].sort_values('Win %')['Leads']*100,
                      y='Source_group', orientation='h', height=300,
                      color=sw[sw['Leads']>3].sort_values('Win %')['Won']/sw[sw['Leads']>3].sort_values('Win %')['Leads']*100,
                      color_continuous_scale=[[0,'#FEE2E2'],[0.1,'#FEF9C3'],[1,'#DCFCE7']],
                      labels={'Source_group':'Source','x':'Win %'})
        fig6.update_layout(margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                           plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                           coloraxis_showscale=False, font=dict(family='Arial', size=14))
        fig6.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        st.plotly_chart(fig6, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    c1, c2 = st.columns(2)
 
    with c1:
        st.markdown("<div class='section-header'>Won vs Lost vs Active by Rep</div>", unsafe_allow_html=True)
        stage_by_rep = filt.groupby(['Rep','Stage']).size().reset_index(name='Count')
        fig7 = px.bar(stage_by_rep, x='Rep', y='Count', color='Stage',
                      barmode='stack', height=420,
                      color_discrete_map={'Won':'#14532D','Active':'#78350F','Lost':'#991B1B'},
                      text_auto=False)
        fig7.update_layout(plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                           margin=dict(l=0,r=0,t=10,b=0),
                           font=dict(family='Arial', size=14),
                           xaxis_tickangle=-30)
        st.plotly_chart(fig7, use_container_width=True)
 
    with c2:
        st.markdown("<div class='section-header'>Lead Volume by Source</div>", unsafe_allow_html=True)
        src_vol = filt['Source_group'].value_counts().reset_index()
        src_vol.columns = ['Source','Count']
        fig8 = px.pie(src_vol, values='Count', names='Source', hole=0.45,
                      height=420, color_discrete_sequence=px.colors.qualitative.Set2)
        fig8.update_layout(margin=dict(l=0,r=0,t=10,b=30),
                           paper_bgcolor='#F0F4F8',
                           font=dict(family='Arial', size=14))
        st.plotly_chart(fig8, use_container_width=True)
 
    c3, c4 = st.columns(2)
 
    with c3:
        st.markdown("<div class='section-header'>Win Rate by Rep</div>", unsafe_allow_html=True)
        wr_rep = filt.groupby('Rep').agg(
            Total=('Stage','count'),
            Won  =('Stage', lambda x:(x=='Won').sum())
        )
        wr_rep['Win %'] = (wr_rep['Won']/wr_rep['Total']*100).round(1)
        wr_rep = wr_rep[wr_rep['Total']>10].sort_values('Win %', ascending=True).reset_index()
        fig9 = px.bar(wr_rep, x='Win %', y='Rep', orientation='h', height=360,
                      text='Win %', color='Win %',
                      color_continuous_scale=[[0,'#FEE2E2'],[0.4,'#FEF9C3'],[1,'#DCFCE7']])
        fig9.update_layout(plot_bgcolor='white', paper_bgcolor='#F0F4F8',
                           margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                           coloraxis_showscale=False,
                           font=dict(family='Arial', size=14))
        fig9.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig9, use_container_width=True)
 
    with c4:
        st.markdown("<div class='section-header'>Stage Distribution</div>", unsafe_allow_html=True)
        stage_counts = filt['Stage'].value_counts()
        fig10 = go.Figure(go.Pie(
            labels=stage_counts.index, values=stage_counts.values,
            hole=0.5,
            marker_colors=['#78350F','#991B1B','#14532D'],
            textinfo='percent+label',
            textfont=dict(size=15)
        ))
        fig10.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                            paper_bgcolor='#F0F4F8', height=360,
                            font=dict(family='Arial', size=14),
                            showlegend=False)
        st.plotly_chart(fig10, use_container_width=True)
 
    st.markdown("<div class='section-header'>Raw Lead Data (filtered)</div>", unsafe_allow_html=True)
    show_cols = [c for c in ['Rep','Source','Stage','FollowupStatus','City','State','CreatedOn']
                 if c in filt.columns]
    st.dataframe(filt[show_cols].reset_index(drop=True),
                 use_container_width=True, height=320)
    st.download_button("⬇ Download filtered raw data (CSV)",
                       filt[show_cols].to_csv(index=False),
                       file_name="filtered_leads.csv", mime="text/csv")
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:#475569; font-size:13px; font-weight:500;'>"
    f"MSafe Equipments &nbsp;|&nbsp; KIT19 CRM &nbsp;|&nbsp; {len(df_raw):,} total leads &nbsp;|&nbsp; "
    f"Filters applied to {len(filt):,} leads"
    f"</p>", unsafe_allow_html=True)
