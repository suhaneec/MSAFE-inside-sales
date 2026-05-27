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
 
/* ══ APP BACKGROUND ══════════════════════════════════════════════════════ */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F8FAFC; color: #0F172A;
}
.stApp p, .stMarkdown p, [data-testid="stMarkdownContainer"] p { color: #0F172A; }
 
/* Tabs */
.stTabs [data-baseweb="tab"] { color: #475569; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #0F2044 !important;
    border-bottom-color: #0F2044 !important; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { background-color: #F1F5F9;
    border-radius: 8px; padding: 4px; }
 
/* Download buttons */
[data-testid="stDownloadButton"] button {
    background-color: #0F2044; color: white;
    border: none; border-radius: 6px; font-size: 12px; }
[data-testid="stDownloadButton"] button:hover { background-color: #1B3A6B; }
 
/* ══ SIDEBAR ════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    background-color: #0F2044 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1, h2, h3,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] small { color: white !important; }
section[data-testid="stSidebar"] hr { border-color: #2D5F9E !important; opacity: 0.5; }
 
/* Multiselect box */
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
    background-color: #162955 !important;
    border: 1px solid #2D5F9E !important; border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stMultiSelect input {
    color: white !important; caret-color: white !important;
}
section[data-testid="stSidebar"] .stMultiSelect [aria-placeholder] { color: #8BAFD4 !important; }
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
    border: 2px dashed #2D5F9E !important; border-radius: 8px !important;
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
    border: 1px solid #2D5F9E !important; border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stDateInput input {
    color: white !important; background-color: #162955 !important;
}
 
/* ══ KPI CARDS ══════════════════════════════════════════════════════════ */
.kpi-block {
    background: white; border-radius: 10px; padding: 16px 12px;
    text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    height: 88px; display: flex; flex-direction: column;
    justify-content: center; border-top: 3px solid #E2E8F0;
}
.kpi-label { font-size: 10px; color: #64748B; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #0F2044; line-height: 1; }
.kpi-value.green { color: #0A6640; }
.kpi-value.red   { color: #B91C1C; }
.kpi-value.amber { color: #92400E; }
.kpi-value.blue  { color: #1E40AF; }
 
/* ══ SECTION HEADERS ════════════════════════════════════════════════════ */
.sec-hdr { background: #0F2044; color: white !important; padding: 8px 16px;
    border-radius: 6px; font-weight: 600; font-size: 13px; margin: 12px 0 6px 0; }
.sub-note { font-size: 11px; color: #64748B; font-style: italic; margin: 0 0 6px 0; }
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
def c_winpct(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 5:  return 'background-color:#E9F7EF; color:#0A6640; font-weight:700'
        elif p >= 2:return 'background-color:#FFFBEB; color:#92400E; font-weight:600'
        elif p == 0:return 'background-color:#FEF2F2; color:#B91C1C; font-weight:700'
        return 'color:#64748B'
    except: return ''
 
def c_losspct(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 70:  return 'background-color:#FEF2F2; color:#B91C1C; font-weight:700'
        elif p >= 50:return 'background-color:#FFFBEB; color:#92400E'
        return ''
    except: return ''
 
def c_hygiene(val):
    try:
        s = str(val).replace('%','')
        if s in ('—',''): return 'background-color:#FEF2F2; color:#B91C1C; font-weight:700'
        p = float(s)
        if p >= 70:  return 'background-color:#E9F7EF; color:#0A6640; font-weight:700'
        elif p >= 30:return 'background-color:#FFFBEB; color:#92400E'
        return 'background-color:#FEF2F2; color:#B91C1C'
    except: return ''
 
def c_source_win(val):
    try:
        p = float(str(val).replace('%',''))
        if p >= 15:  return 'background-color:#E9F7EF; color:#0A6640; font-weight:700'
        elif p >= 2: return 'background-color:#FFFBEB; color:#92400E'
        elif p == 0: return 'background-color:#FEF2F2; color:#B91C1C'
        return ''
    except: return ''
 
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
 
uploaded = st.sidebar.file_uploader(
    "Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])
 
if not uploaded:
    st.markdown("""
    <div style='text-align:center; padding:100px 40px;'>
        <div style='font-size:52px;'>📂</div>
        <h2 style='color:#0F2044; margin-top:16px;'>MSafe Inside Sales Dashboard</h2>
        <p style='color:#64748B; font-size:15px; margin-top:8px;'>
            Upload your KIT19 CRM export from the sidebar to get started.
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
<div style='background:#0F2044; padding:16px 24px; border-radius:10px;
            margin-bottom:14px; display:flex; align-items:center; gap:16px;'>
    <span style='color:white; font-size:19px; font-weight:700;'>
        MSafe Equipments — Inside Sales Dashboard
    </span>
    <span style='color:#8BAFD4; font-size:12px;'>KIT19 CRM</span>
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
 
kpi(cols[0],'Total Leads', f'{total:,}')
kpi(cols[1],'Won',         f'{won:,}',   'green')
kpi(cols[2],'Lost',        f'{lost:,}',  'red')
kpi(cols[3],'Active',      f'{active:,}','amber')
kpi(cols[4],'Win Rate',    f'{wr}%',     'blue')
kpi(cols[5],'Quote → Win', f'{q2w}%',   'green')
kpi(cols[6],'High Intent', f'{high:,}',  'amber')
kpi(cols[7],'Cold CB/RNR', f'{cold:,}',  'red')
kpi(cols[8],'Ex.Client Win',f'{ec_wr}%','green')
 
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
    st.markdown("<p class='sub-note'>Number of leads each rep received from each source. "
                "Green = quality sources (Existing Client, Ex-Client Ref.)  |  "
                "TOTAL row and column in navy.</p>", unsafe_allow_html=True)
 
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
            quality = ['Existing Client','Ex-Client Ref.']
            for col in df.columns:
                if col in quality:
                    styles[col] = df[col].apply(
                        lambda v: 'background-color:#E9F7EF; color:#0A6640; font-weight:700'
                        if (isinstance(v,int) and v>0) else '')
                if col == 'TOTAL':
                    styles[col] = 'background-color:#EAF0FB; color:#0F2044; font-weight:700'
            if 'TOTAL' in df.index:
                styles.loc['TOTAL'] = 'background-color:#0F2044; color:white; font-weight:700'
            return styles
 
        fmt = lambda x: '' if x==0 else f'{x:,}'
        st.dataframe(
            pivot.style.apply(style_pivot, axis=None).format(fmt),
            use_container_width=True, height=460)
 
        st.download_button("⬇ Download CSV", pivot.to_csv(),
                           "rep_source.csv", "text/csv")
 
        # Source win rate below the table (just a plain number table)
        st.markdown("<div class='sec-hdr'>Source Win Rate</div>", unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>How many leads from each source converted to Won.</p>",
                    unsafe_allow_html=True)
 
        sw = filt.groupby('Source_group').agg(
            Leads=('Stage','count'),
            Won  =('Stage', lambda x:(x=='Won').sum()),
            Lost =('Stage', lambda x:(x=='Lost').sum()),
            Active=('Stage',lambda x:(x=='Active').sum()),
        ).reset_index().rename(columns={'Source_group':'Source'})
        sw['Win %'] = (sw['Won']/sw['Leads']*100).round(1).astype(str)+'%'
        sw = sw[sw['Leads']>2].sort_values('Won',ascending=False).set_index('Source')
 
        def style_sw(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            styles['Win %'] = df['Win %'].apply(c_source_win)
            styles['Won']   = df['Won'].apply(
                lambda v: 'background-color:#E9F7EF; color:#0A6640; font-weight:700' if v>0 else '')
            return styles
 
        st.dataframe(
            sw.style.apply(style_sw, axis=None).format({'Leads':'{:,}','Won':'{:,}','Lost':'{:,}','Active':'{:,}'}),
            use_container_width=True, height=320)
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — REP PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='sec-hdr'>Rep Performance — Active / Won / Lost</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "🟢 Win % ≥ 5%   🟡 Win % 2–5%   🔴 Win % 0%  &nbsp;|&nbsp;  "
                "🔴 Loss % ≥ 70%   🟡 Loss % 50–70%</p>",
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
                    styles.loc[idx] = 'background-color:#0F2044; color:white; font-weight:700'
                    continue
                styles.loc[idx,'Win %']  = c_winpct(df.loc[idx,'Win %'])
                styles.loc[idx,'Loss %'] = c_losspct(df.loc[idx,'Loss %'])
                won_v = df.loc[idx,'Won']
                if isinstance(won_v,int) and won_v>0:
                    styles.loc[idx,'Won'] = 'background-color:#E9F7EF; color:#0A6640; font-weight:700'
                lost_v = df.loc[idx,'Lost']
                if isinstance(lost_v,int) and lost_v>300:
                    styles.loc[idx,'Lost'] = 'background-color:#FEF2F2; color:#B91C1C'
            return styles
 
        st.dataframe(
            awl_d.style.apply(style_awl, axis=None)
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
                "🟢 ≥ 70% filled   🟡 30–70% filled   🔴 &lt; 30% filled  &nbsp;|&nbsp;  "
                "Score = average across all tracked fields.</p>",
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
 
        # Overall row
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
                    styles.loc[idx] = 'background-color:#0F2044; color:white; font-weight:700'
                    continue
                for col in HYGIENE_FIELDS.keys():
                    if col in df.columns:
                        styles.loc[idx,col] = c_hygiene(df.loc[idx,col])
                # Score column
                if 'Score' in df.columns:
                    styles.loc[idx,'Score'] = c_hygiene(df.loc[idx,'Score'])
            return styles
 
        st.dataframe(
            hyg.style.apply(style_hyg, axis=None),
            use_container_width=True, height=500)
 
        st.download_button("⬇ Download CSV", hyg.to_csv(),
                           "crm_hygiene.csv", "text/csv")
 
        # What the fields mean
        with st.expander("What do these fields mean?"):
            st.markdown("""
| Field | What it tracks | Why it matters |
|---|---|---|
| **Product** | Which product category the lead enquired about | Without this, no product-level reporting is possible |
| **Biz Type** | Sale or Rental | These are two different pipelines — mixing them makes reporting useless |
| **City** | Contact city of the lead | Determines which MSafe yard should fulfil the order |
| **Followup Date** | Whether a next action date is set | No follow-up date = lead is being left to die |
| **Quote Value** | ₹ value of quotation sent | 0% across all reps — pipeline worth is completely unknown |
            """)
 
# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — PIPELINE & LOST REASONS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    c_left, c_right = st.columns(2)
 
    # ── Active Pipeline ───────────────────────────────────────────────────
    with c_left:
        st.markdown("<div class='sec-hdr'>Active Pipeline Breakdown</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "🟢 Quoted stages (high intent)   🟡 Interested / Catalogue   "
                    "🔴 Call Back / RNR (cold)</p>", unsafe_allow_html=True)
 
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
                        styles.loc[idx] = 'background-color:#FEF2F2; color:#B91C1C'
                    elif any(x in idx for x in ['Quoted','Quote']):
                        styles.loc[idx] = 'background-color:#E9F7EF; color:#0A6640; font-weight:600'
                    elif any(x in idx for x in ['Interested','Catalogue','MS Req']):
                        styles.loc[idx] = 'background-color:#FFFBEB; color:#92400E'
                return styles
 
            st.dataframe(
                pipe_df.style.apply(style_pipe, axis=None)
                             .format({'Count':'{:,}'}),
                use_container_width=True, height=500)
            st.download_button("⬇ Download CSV", pipe_df.to_csv(),
                               "pipeline.csv", "text/csv")
 
    # ── Lost Reasons ──────────────────────────────────────────────────────
    with c_right:
        st.markdown("<div class='sec-hdr'>Why Leads Are Lost</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Sorted by volume. All loss reasons shown for filtered selection.</p>",
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
 
            # All red — all are losses
            def style_lost(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                styles['Count'] = 'background-color:#FEF2F2; color:#B91C1C; font-weight:700'
                return styles
 
            st.dataframe(
                lost_df.style.apply(style_lost, axis=None)
                             .format({'Count':'{:,}'}),
                use_container_width=True, height=500)
            st.download_button("⬇ Download CSV", lost_df.to_csv(),
                               "lost_reasons.csv", "text/csv")
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:#94A3B8; font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{len(filt):,} leads shown with current filters"
    f"</p>", unsafe_allow_html=True)
