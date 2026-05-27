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
 
/* ══ MAIN APP BACKGROUND & TEXT ══════════════════════════════════════════ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F8FAFC;
    color: #0F172A;
}
.stApp p, .stApp span,
.stMarkdown p, .stMarkdown span,
[data-testid="stMarkdownContainer"] p { color: #0F172A; }
.stTabs [data-baseweb="tab"] { color: #475569; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #0F2044 !important;
    border-bottom-color: #0F2044 !important; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { background-color: #F1F5F9;
    border-radius: 8px; padding: 4px; }
[data-testid="stDownloadButton"] button {
    background-color: #0F2044; color: white;
    border: none; border-radius: 6px; font-size: 12px; }
[data-testid="stDownloadButton"] button:hover { background-color: #1B3A6B; }
 
/* ══ SIDEBAR — DARK NAVY ═════════════════════════════════════════════════ */
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
section[data-testid="stSidebar"] small { color: white !important; }
section[data-testid="stSidebar"] hr { border-color: #2D5F9E !important; opacity: 0.5; }
 
/* Multiselect input box */
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
    background-color: #162955 !important;
    border: 1px solid #2D5F9E !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stMultiSelect input {
    color: white !important; caret-color: white !important;
}
section[data-testid="stSidebar"] .stMultiSelect [aria-placeholder] { color: #8BAFD4 !important; }
/* Selected chips */
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #2D5F9E !important; border-radius: 4px !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg {
    color: white !important; fill: white !important;
}
 
/* File uploader */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #162955 !important;
    border: 2px dashed #2D5F9E !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span {
    color: #8BAFD4 !important;
}
 
/* Date input */
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="input"],
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="base-input"] {
    background-color: #162955 !important;
    border: 1px solid #2D5F9E !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stDateInput input {
    color: white !important; background-color: #162955 !important;
}
 
/* ══ KPI CARDS ═══════════════════════════════════════════════════════════ */
.kpi-block {
    background: white; border-radius: 10px; padding: 16px 12px;
    text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    height: 90px; display: flex; flex-direction: column;
    justify-content: center; border-top: 3px solid #E2E8F0;
}
.kpi-label { font-size: 10px; color: #64748B; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #0F2044; line-height: 1; }
.kpi-value.green { color: #0A6640; }
.kpi-value.red   { color: #B91C1C; }
.kpi-value.amber { color: #92400E; }
.kpi-value.blue  { color: #1E40AF; }
 
/* ══ SECTION HEADERS ══════════════════════════════════════════════════════ */
.section-header { background: #0F2044; color: white !important;
    padding: 8px 16px; border-radius: 6px; font-weight: 600;
    font-size: 13px; margin: 16px 0 8px 0; }
.data-note { font-size: 11px; color: #64748B; font-style: italic; margin-top: 4px; }
[data-testid="stAlert"] { color: #0F172A !important; }
 
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
 
# ── STYLING HELPERS ───────────────────────────────────────────────────────────
def color_winrate(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 5:  return 'background-color: #E9F7EF; color: #0A6640; font-weight: 600'
        elif p >= 2:return 'background-color: #FFFBEB; color: #92400E; font-weight: 600'
        elif p == 0:return 'background-color: #FEF2F2; color: #B91C1C; font-weight: 600'
        return ''
    except: return ''
 
def color_hygiene(val):
    try:
        s = str(val).replace('%','')
        if s == '—': return 'background-color: #FEF2F2; color: #B91C1C'
        p = float(s)
        if p >= 70:  return 'background-color: #E9F7EF; color: #0A6640; font-weight: 600'
        elif p >= 30:return 'background-color: #FFFBEB; color: #92400E'
        return 'background-color: #FEF2F2; color: #B91C1C'
    except: return ''
 
def color_lossrate(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 70:  return 'background-color: #FEF2F2; color: #B91C1C; font-weight:600'
        elif p >= 50:return 'background-color: #FFFBEB; color: #92400E'
        return ''
    except: return ''
 
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
        <div style='font-size:48px;'>📂</div>
        <h2 style='color:#0F2044;'>MSafe Inside Sales Dashboard</h2>
        <p style='color:#64748B; font-size:16px;'>
            Upload your KIT19 CRM export using the sidebar to get started.
        </p>
        <p style='color:#94A3B8; font-size:13px;'>
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
 
# Date filter
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
<div style='background:#0F2044; padding:18px 24px; border-radius:10px; margin-bottom:16px;
            display:flex; justify-content:space-between; align-items:center;'>
    <div>
        <span style='color:white; font-size:20px; font-weight:700;'>
            MSafe Equipments — Inside Sales Dashboard
        </span>
        <span style='color:#8BAFD4; font-size:12px; margin-left:16px;'>KIT19 CRM</span>
    </div>
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
    st.markdown("<div class='section-header'>Leads by Rep & Source</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='data-note'>How many leads each rep receives from each source. "
                "Green cells = quality source (Existing Client, Ex-Client Ref.)</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        # Build pivot
        pivot = pd.crosstab(filt['Rep'], filt['Source_group'], margins=True, margins_name='TOTAL')
 
        # Reorder columns: main sources first, then Other, then TOTAL
        preferred = ['JustDial','IndiaMart','IVR Call','Existing Client',
                     'Ex-Client Ref.','Facebook','Website','Google Ads','Phone',
                     'Email marketing','Other']
        ordered = [c for c in preferred if c in pivot.columns]
        ordered += [c for c in pivot.columns if c not in ordered and c != 'TOTAL']
        if 'TOTAL' in pivot.columns: ordered.append('TOTAL')
        pivot = pivot[ordered]
 
        # Style: green for quality sources
        def style_pivot(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            quality = ['Existing Client','Ex-Client Ref.']
            for col in df.columns:
                if col in quality:
                    styles[col] = df[col].apply(
                        lambda v: 'background-color:#E9F7EF; color:#0A6640; font-weight:600'
                        if v and v != 0 else '')
            # TOTAL row + col
            if 'TOTAL' in df.columns:
                styles['TOTAL'] = 'background-color:#EAF0FB; color:#0F2044; font-weight:700'
            if 'TOTAL' in df.index:
                styles.loc['TOTAL'] = 'background-color:#0F2044; color:white; font-weight:700'
            return styles
 
        styled = pivot.style.apply(style_pivot, axis=None).format(
            lambda x: '' if x==0 else f'{x:,}')
 
        st.dataframe(styled, use_container_width=True, height=450)
 
        # Download
        csv = pivot.to_csv()
        st.download_button("⬇ Download table (CSV)", csv,
                           file_name="rep_source_breakdown.csv", mime="text/csv")
 
        # Source share bar (stacked)
        st.markdown("<div class='section-header'>Source Distribution by Rep</div>",
                    unsafe_allow_html=True)
        plot_df = filt[filt['Rep']!='TOTAL'].copy()
        fig = px.bar(plot_df, x='Rep', color='Source_group',
                     barmode='stack', height=380,
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={'Source_group':'Source','Rep':'Rep','count':'Leads'})
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                          legend_title='Source', margin=dict(l=0,r=0,t=10,b=0),
                          font_family='Calibri')
        st.plotly_chart(fig, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REP PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>Rep Performance — Active / Won / Lost</div>",
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
        awl['Win %']  = (awl['Won']  / awl['Total'] * 100).round(1).astype(str) + '%'
        awl['Loss %'] = (awl['Lost'] / awl['Total'] * 100).round(1).astype(str) + '%'
        awl = awl.sort_values('Won', ascending=False)
 
        # Totals row
        tot_row = pd.DataFrame([{
            'Rep':'TOTAL', 'Total':awl['Total'].sum(), 'Active':awl['Active'].sum(),
            'Won':awl['Won'].sum(), 'Lost':awl['Lost'].sum(),
            'Win %': f"{round(awl['Won'].sum()/awl['Total'].sum()*100,1)}%",
            'Loss %':f"{round(awl['Lost'].sum()/awl['Total'].sum()*100,1)}%",
        }])
        awl_disp = pd.concat([awl, tot_row], ignore_index=True).set_index('Rep')
 
        def style_awl(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx in df.index:
                if idx == 'TOTAL':
                    styles.loc[idx] = 'background-color:#0F2044; color:white; font-weight:700'
                    continue
                styles.loc[idx,'Won']    = 'background-color:#E9F7EF; color:#0A6640; font-weight:600'
                styles.loc[idx,'Active'] = 'background-color:#FFFBEB; color:#92400E'
            for idx in df.index:
                if idx == 'TOTAL': continue
                styles.loc[idx,'Win %']  = color_winrate(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = color_lossrate(df.loc[idx,'Loss %'])
            return styles
 
        st.dataframe(
            awl_disp.style.apply(style_awl, axis=None).format({'Total':'{:,}','Active':'{:,}','Won':'{:,}','Lost':'{:,}'}),
            use_container_width=True, height=450)
 
        st.download_button("⬇ Download (CSV)", awl_disp.to_csv(),
                           file_name="rep_performance.csv", mime="text/csv")
 
        # Win rate bar chart
        fig2 = px.bar(awl[awl['Rep']!='TOTAL'],
                      x='Rep', y='Won',
                      text='Won',
                      color='Won',
                      color_continuous_scale=[[0,'#E9F7EF'],[1,'#0A6640']],
                      height=320, title='Wins by Rep')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                           showlegend=False, margin=dict(l=0,r=0,t=40,b=0),
                           font_family='Calibri', coloraxis_showscale=False)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CRM HYGIENE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>CRM Data Hygiene — % of Leads with Field Filled</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='data-note'>"
                "🟢 ≥70% filled &nbsp;&nbsp; 🟡 30–70% &nbsp;&nbsp; 🔴 &lt;30%"
                "</p>", unsafe_allow_html=True)
 
    HYGIENE_FIELDS = {
        'Product':    'product_name',
        'Biz Type':   'Q_Type',
        'City':       'City',
        'Followup Date':'FollowupDate',
        'Quote Value':'quotation_total_amount',
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
            # Score: average of numeric pcts
            pcts = []
            for label in HYGIENE_FIELDS:
                v = row[label].replace('%','')
                try: pcts.append(float(v))
                except: pass
            row['Score'] = f"{round(np.mean(pcts))}%" if pcts else '—'
            rows.append(row)
 
        # Overall row
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
                    styles.loc[idx] = 'background-color:#0F2044; color:white; font-weight:700'
                    continue
                for col in df.columns:
                    if col in ('Leads',): continue
                    styles.loc[idx, col] = color_hygiene(df.loc[idx, col])
            return styles
 
        st.dataframe(
            hyg_df.style.apply(style_hyg, axis=None),
            use_container_width=True, height=450)
 
        st.download_button("⬇ Download (CSV)", hyg_df.to_csv(),
                           file_name="crm_hygiene.csv", mime="text/csv")
 
        # Heatmap of hygiene
        st.markdown("<div class='section-header'>Hygiene Heatmap</div>",
                    unsafe_allow_html=True)
        heat_data = hyg_df.drop(index='OVERALL', errors='ignore').drop(columns=['Leads','Score'], errors='ignore').copy()
        heat_num = heat_data.applymap(lambda v: float(v.replace('%','')) if '%' in str(v) else 0)
        fig3 = px.imshow(heat_num, color_continuous_scale='RdYlGn',
                         zmin=0, zmax=100, aspect='auto',
                         text_auto=True, height=380)
        fig3.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                           paper_bgcolor='#F8FAFC', font_family='Calibri')
        st.plotly_chart(fig3, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PIPELINE & LOST REASONS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c_pipe, c_lost = st.columns(2)
 
    with c_pipe:
        st.markdown("<div class='section-header'>Active Pipeline Breakdown</div>",
                    unsafe_allow_html=True)
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
                if 'RNR' in s or 'Call Back' in s:
                    return ['background-color:#FEF2F2']*len(row)
                elif 'Quoted' in s or 'Quote' in s:
                    return ['background-color:#E9F7EF']*len(row)
                elif 'Interested' in s or 'Catalogue' in s:
                    return ['background-color:#FFFBEB']*len(row)
                return ['']*len(row)
 
            st.dataframe(
                pipe_df.style.apply(color_pipe, axis=1),
                use_container_width=True, hide_index=True, height=400)
 
            # Donut
            fig4 = px.pie(pipe_df.head(8), values='Count', names='Status',
                          hole=0.5, height=300,
                          color_discrete_sequence=px.colors.qualitative.Set3)
            fig4.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                               paper_bgcolor='#F8FAFC', showlegend=True,
                               legend=dict(font=dict(size=10)),
                               font_family='Calibri')
            st.plotly_chart(fig4, use_container_width=True)
 
    with c_lost:
        st.markdown("<div class='section-header'>Lost Reasons</div>",
                    unsafe_allow_html=True)
        lost_filt = filt[filt['Stage']=='Lost']
        if len(lost_filt) == 0:
            st.info("No lost leads in current filters.")
        else:
            lost_df = (lost_filt['FollowupStatus']
                       .value_counts()
                       .reset_index()
                       .rename(columns={'FollowupStatus':'Reason','count':'Count'}))
            lost_df['%'] = (lost_df['Count'] / lost_df['Count'].sum() * 100).round(1).astype(str) + '%'
 
            st.dataframe(
                lost_df.style.applymap(
                    lambda _: 'background-color:#FEF2F2; color:#B91C1C; font-weight:600',
                    subset=['Count']),
                use_container_width=True, hide_index=True, height=400)
 
            fig5 = px.bar(lost_df, x='Count', y='Reason', orientation='h',
                          height=300, text='Count',
                          color='Count',
                          color_continuous_scale=[[0,'#FDECEA'],[1,'#B91C1C']])
            fig5.update_layout(margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                               plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                               yaxis={'categoryorder':'total ascending'},
                               coloraxis_showscale=False, font_family='Calibri')
            fig5.update_traces(textposition='outside')
            st.plotly_chart(fig5, use_container_width=True)
 
        # Source win rate
        st.markdown("<div class='section-header'>Source Win Rate</div>",
                    unsafe_allow_html=True)
        sw = filt.groupby('Source_group').agg(
            Leads=('Stage','count'),
            Won  =('Stage', lambda x:(x=='Won').sum())
        ).reset_index()
        sw['Win %'] = (sw['Won']/sw['Leads']*100).round(1)
        sw = sw[sw['Leads']>3].sort_values('Win %', ascending=True)
 
        fig6 = px.bar(sw, x='Win %', y='Source_group', orientation='h',
                      height=280, text='Win %',
                      color='Win %',
                      color_continuous_scale=[[0,'#FEF2F2'],[0.1,'#FFFBEB'],[1,'#E9F7EF']],
                      labels={'Source_group':'Source'})
        fig6.update_layout(margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                           plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                           coloraxis_showscale=False, font_family='Calibri')
        fig6.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig6, use_container_width=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    c1, c2 = st.columns(2)
 
    with c1:
        st.markdown("<div class='section-header'>Won vs Lost vs Active by Rep</div>",
                    unsafe_allow_html=True)
        stage_by_rep = filt.groupby(['Rep','Stage']).size().reset_index(name='Count')
        fig7 = px.bar(stage_by_rep, x='Rep', y='Count', color='Stage',
                      barmode='stack', height=380,
                      color_discrete_map={'Won':'#0A6640','Active':'#92400E','Lost':'#B91C1C'},
                      text_auto=False)
        fig7.update_layout(plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                           margin=dict(l=0,r=0,t=10,b=0), font_family='Calibri',
                           xaxis_tickangle=-30)
        st.plotly_chart(fig7, use_container_width=True)
 
    with c2:
        st.markdown("<div class='section-header'>Lead Volume by Source</div>",
                    unsafe_allow_html=True)
        src_vol = filt['Source_group'].value_counts().reset_index()
        src_vol.columns = ['Source','Count']
        fig8 = px.pie(src_vol, values='Count', names='Source', hole=0.45,
                      height=380, color_discrete_sequence=px.colors.qualitative.Set2)
        fig8.update_layout(margin=dict(l=0,r=0,t=10,b=30),
                           paper_bgcolor='#F8FAFC', font_family='Calibri')
        st.plotly_chart(fig8, use_container_width=True)
 
    c3, c4 = st.columns(2)
 
    with c3:
        st.markdown("<div class='section-header'>Win Rate by Rep</div>",
                    unsafe_allow_html=True)
        wr_rep = filt.groupby('Rep').agg(Total=('Stage','count'),Won=('Stage',lambda x:(x=='Won').sum()))
        wr_rep['Win %'] = (wr_rep['Won']/wr_rep['Total']*100).round(1)
        wr_rep = wr_rep[wr_rep['Total']>10].sort_values('Win %',ascending=True).reset_index()
        fig9 = px.bar(wr_rep, x='Win %', y='Rep', orientation='h', height=320,
                      text='Win %',
                      color='Win %',
                      color_continuous_scale=[[0,'#FEF2F2'],[0.5,'#FFFBEB'],[1,'#E9F7EF']])
        fig9.update_layout(plot_bgcolor='white', paper_bgcolor='#F8FAFC',
                           margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                           coloraxis_showscale=False, font_family='Calibri')
        fig9.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig9, use_container_width=True)
 
    with c4:
        st.markdown("<div class='section-header'>Stage Distribution</div>",
                    unsafe_allow_html=True)
        stage_counts = filt['Stage'].value_counts()
        fig10 = go.Figure(go.Pie(
            labels=stage_counts.index, values=stage_counts.values,
            hole=0.5,
            marker_colors=['#92400E','#B91C1C','#0A6640'],
            textinfo='percent+label'
        ))
        fig10.update_layout(margin=dict(l=0,r=0,t=10,b=0),
                            paper_bgcolor='#F8FAFC', height=320,
                            font_family='Calibri', showlegend=False)
        st.plotly_chart(fig10, use_container_width=True)
 
    # Full raw data
    st.markdown("<div class='section-header'>Raw Lead Data (filtered)</div>",
                unsafe_allow_html=True)
    show_cols = [c for c in ['Rep','Source','Stage','FollowupStatus','City','State','CreatedOn']
                 if c in filt.columns]
    st.dataframe(filt[show_cols].reset_index(drop=True),
                 use_container_width=True, height=300)
    st.download_button("⬇ Download filtered raw data (CSV)",
                       filt[show_cols].to_csv(index=False),
                       file_name="filtered_leads.csv", mime="text/csv")
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:#94A3B8; font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} total leads  |  "
    f"Business Analyst Dashboard  |  Filters applied to {len(filt):,} leads"
    f"</p>", unsafe_allow_html=True)
