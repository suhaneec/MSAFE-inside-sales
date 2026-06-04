import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
 
st.set_page_config(page_title="MSafe Inside Sales", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")
 
st.markdown("""
<style>
:root {
    --background-color: #F8FAFC !important;
    --text-color: #0F172A !important;
    --primary-color: #0F2044 !important;
}
html, body { background-color: #F8FAFC !important; color: #0F172A !important; }
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
.block-container,[data-testid="stMain"]>div {
    background-color: #F8FAFC !important; color: #0F172A !important;
}
[data-testid="stMain"] *, .block-container *,
.stMarkdown *, [data-testid="stMarkdownContainer"] * { color: #0F172A !important; }

/* ── HEADER OVERRIDE: force white text inside the dark header banner ── */
.msafe-header, .msafe-header * { color: white !important; }

/* ── TAB FIX: white text on dark tab bar, visible selected state ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0F2044 !important;
    border-radius: 8px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    color: #CBD5E1 !important;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px !important;
    padding: 8px 14px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
    background: rgba(255,255,255,0.1) !important;
}
.stTabs [aria-selected="true"] {
    color: #0F2044 !important;
    background: #FFFFFF !important;
    font-weight: 700 !important;
    border-bottom: none !important;
}
/* Force all tab label text white except selected */
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] div { color: inherit !important; }
 
[data-testid="stDownloadButton"] button {
    background:#0F2044 !important; color:white !important;
    border:none !important; border-radius:6px !important; font-weight:600 !important; }
 
/* SIDEBAR */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div,
section[data-testid="stSidebar"]>div:first-child { background:#0F2044 !important; }
section[data-testid="stSidebar"] * { color:white !important; }
section[data-testid="stSidebar"] hr { border-color:#2D5F9E !important; }
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"]>div {
    background:#162955 !important; border:1px solid #2D5F9E !important; border-radius:6px !important; }
section[data-testid="stSidebar"] .stMultiSelect input { color:white !important; caret-color:white !important; }
section[data-testid="stSidebar"] .stMultiSelect [aria-placeholder] { color:#8BAFD4 !important; }
section[data-testid="stSidebar"] [data-baseweb="tag"] { background:#2D5F9E !important; border-radius:4px !important; }
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg { color:white !important; fill:white !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background:#162955 !important; border:2px dashed #2D5F9E !important; border-radius:8px !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span { color:#8BAFD4 !important; }
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="input"],
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="base-input"] {
    background:#162955 !important; border:1px solid #2D5F9E !important; border-radius:6px !important; }
section[data-testid="stSidebar"] .stDateInput input { color:white !important; background:#162955 !important; }
 
/* KPI */
.kpi-block { background:white !important; border-radius:10px; padding:16px 12px;
    text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.08); height:88px;
    display:flex; flex-direction:column; justify-content:center; border-top:3px solid #CBD5E1; }
.kpi-label { font-size:10px; color:#475569 !important; font-weight:700;
    text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
.kpi-value { font-size:24px; font-weight:700; color:#0F2044 !important; line-height:1; }
.kpi-value.green { color:#0A6640 !important; }
.kpi-value.red   { color:#B91C1C !important; }
.kpi-value.amber { color:#92400E !important; }
.kpi-value.blue  { color:#1D4ED8 !important; }
.kpi-value.purple{ color:#6D28D9 !important; }
 
/* HEADERS */
.sec-hdr { background:#0F2044 !important; color:white !important; padding:9px 18px;
    border-radius:6px; font-weight:700; font-size:13px; margin:14px 0 6px 0; }
.sub-note { font-size:12px !important; color:#475569 !important; font-style:italic; margin:0 0 8px 0; }
 
/* DATAFRAME */
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"] * {
    background:#1B3A6B !important; color:white !important;
    font-size:13px !important; font-weight:700 !important; }
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"] * { color:#0F172A !important; font-size:13px !important; }
[data-testid="stDataFrame"] [role="rowheader"],[data-testid="stDataFrame"] [role="rowheader"] * {
    color:#0F172A !important; font-size:13px !important;
    font-weight:600 !important; background:#F1F5F9 !important; }
</style>
""", unsafe_allow_html=True)
 
# ── CONSTANTS ─────────────────────────────────────────────────────────────────
LOST_S = ['Not-Interested','Not Search Our Product','Regret','Other Department Working',
          'Wrong Number','No Response on RNR','Already Purchased','Quoted Order Lost']
WON_S  = ['Quoted Order Won And Executed']
HIGH_S = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
          'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold',
          'Quoted Order Won And Executed','Quoted Order Lost']
# Statuses that indicate a quotation was actually sent to the customer
QUOTED_SENT_S = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
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
 
@st.cache_data(show_spinner="Loading…")
def load_data(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')
    df['Stage']  = df['FollowupStatus'].apply(
        lambda x:'Won' if x in WON_S else ('Lost' if x in LOST_S else 'Active'))
    df['Source'] = df['SourceName'].replace(SRC_MAP)
    df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)
    df['Rep'] = df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
    df.loc[df['is_admin'],'Rep'] = 'Admin'
    df['Source_group'] = df['Source'].apply(lambda x: x if x in MAIN_SOURCES else 'Other')
    if 'CreatedOn' in df.columns:
        df['CreatedOn'] = pd.to_datetime(df['CreatedOn'], errors='coerce')
    return df
 
# ── COLOUR HELPERS ─────────────────────────────────────────────────────────────
def fmt_n_pct(n, total):
    if total == 0: return '0'
    pct = round(n / total * 100, 1)
    return f'{n:,}  ({pct}%)'
 
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])
 
if not uploaded:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        st.markdown(
            "<div style='text-align:center;padding:40px 20px;background:#FFFFFF;"
            "border-radius:12px;border:1px solid #E2E8F0;box-shadow:0 2px 8px rgba(0,0,0,0.06);'>"
            "<div style='font-size:56px;margin-bottom:16px;'>📂</div>"
            "<div style='font-size:22px;font-weight:800;color:#0F2044;"
            "font-family:Arial,sans-serif;margin-bottom:10px;'>"
            "MSafe Inside Sales Dashboard</div>"
            "<div style='font-size:14px;color:#475569;font-family:Arial,sans-serif;'>"
            "Upload your KIT19 CRM export (.xls / .xlsx)<br>using the sidebar to get started.</div>"
            "</div>", unsafe_allow_html=True)
    st.stop()
 
df_raw  = load_data(uploaded.read())
reps_df = df_raw[~df_raw['is_admin']].copy()
 
st.sidebar.markdown("### Filters")
all_reps    = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps    = st.sidebar.multiselect("Rep", all_reps, default=all_reps)
all_sources = sorted(reps_df['Source_group'].dropna().unique().tolist())
sel_sources = st.sidebar.multiselect("Source", all_sources, default=all_sources)
sel_stages  = st.sidebar.multiselect("Stage", ['Active','Won','Lost'], default=['Active','Won','Lost'])
if 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any():
    mn = reps_df['CreatedOn'].min().date(); mx = reps_df['CreatedOn'].max().date()
    date_range = st.sidebar.date_input("Date range", [mn, mx], min_value=mn, max_value=mx)
else:
    date_range = None
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")
 
filt = reps_df.copy()
if sel_reps:    filt = filt[filt['Rep'].isin(sel_reps)]
if sel_sources: filt = filt[filt['Source_group'].isin(sel_sources)]
if sel_stages:  filt = filt[filt['Stage'].isin(sel_stages)]
if date_range and len(date_range)==2 and 'CreatedOn' in filt.columns:
    filt = filt[(filt['CreatedOn'].dt.date >= date_range[0]) &
                (filt['CreatedOn'].dt.date <= date_range[1])]
 
# ── HEADER ────────────────────────────────────────────────────────────────────
# Using class="msafe-header" so the CSS override forces white text
st.markdown(
    "<div class='msafe-header' style='background:#0F2044;padding:16px 24px;border-radius:10px;"
    "margin-bottom:14px;'>"
    "<span style='color:white !important;font-size:19px;font-weight:700;'>"
    "MSafe Equipments — Inside Sales Dashboard</span>"
    "<span style='color:#8BAFD4 !important;font-size:12px;margin-left:16px;'>KIT19 CRM</span>"
    "</div>", unsafe_allow_html=True)
 
# ── KPI ROW ───────────────────────────────────────────────────────────────────
total  = len(filt)
won    = (filt['Stage']=='Won').sum()
lost   = (filt['Stage']=='Lost').sum()
active = (filt['Stage']=='Active').sum()
high   = filt['FollowupStatus'].isin(HIGH_S).sum()
cold   = filt['FollowupStatus'].isin(['Call Back','RNR Call Back']).sum()
# Quotations sent = all leads that reached any "Quoted / Quote" status (ever quoted)
quotes_sent = filt['FollowupStatus'].isin(QUOTED_SENT_S).sum()
quote_to_win = round(won / quotes_sent * 100, 1) if quotes_sent else 0
wr     = round(won/total*100,1) if total else 0
q2w    = round(won/high*100,1)  if high  else 0
ec     = filt[filt['Source']=='Existing Client']
ec_wr  = round((ec['Stage']=='Won').sum()/len(ec)*100,1) if len(ec) else 0
 
# 10 KPI cards now (added Quotes Sent + Quote→Win rate)
kcols = st.columns(10)
def kpi(col, label, value, cls=''):
    col.markdown(
        f"<div class='kpi-block'><div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value {cls}'>{value}</div></div>", unsafe_allow_html=True)
 
kpi(kcols[0], 'Total Leads',   f'{total:,}')
kpi(kcols[1], 'Won',           f'{won:,}',        'green')
kpi(kcols[2], 'Lost',          f'{lost:,}',        'red')
kpi(kcols[3], 'Active',        f'{active:,}',      'amber')
kpi(kcols[4], 'Win Rate',      f'{wr}%',           'blue')
kpi(kcols[5], 'Quotes Sent',   f'{quotes_sent:,}', 'purple')
kpi(kcols[6], 'Quote→Win %',   f'{quote_to_win}%', 'green')
kpi(kcols[7], 'High Intent',   f'{high:,}',        'amber')
kpi(kcols[8], 'Cold CB/RNR',   f'{cold:,}',        'red')
kpi(kcols[9], 'ExClient Win',  f'{ec_wr}%',        'green')
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊  Leads by Rep & Source",
    "🔄  Conversion by Rep & Source",
    "🔵  Pipeline by Rep",
    "🔴  Lost Reasons by Rep",
    "💰  Amount by Deal Stage",
    "📈  Source Performance",
    "💵  Revenue Summary",
])
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REP × SOURCE CROSS-TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='sec-hdr'>How Many Leads Each Rep Got from Each Source</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "Raw lead counts. Green = quality sources (Existing Client, Ex-Client Ref.)  |  "
                "TOTAL row = rep's total leads across all sources.</p>", unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        pivot = pd.crosstab(filt['Rep'], filt['Source_group'], margins=True, margins_name='TOTAL')
        preferred = ['JustDial','IndiaMart','IVR Call','Existing Client','Ex-Client Ref.',
                     'Facebook','Website','Google Ads','Phone','Email marketing','Other']
        ordered = [c for c in preferred if c in pivot.columns]
        ordered += [c for c in pivot.columns if c not in ordered and c!='TOTAL']
        if 'TOTAL' in pivot.columns: ordered.append('TOTAL')
        pivot = pivot[ordered]
 
        def sty_pivot(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in df.columns:
                if col in ('Existing Client','Ex-Client Ref.'):
                    s[col] = df[col].apply(
                        lambda v: 'background:#E9F7EF;color:#0A6640;font-weight:700'
                        if isinstance(v,int) and v>0 else '')
                if col=='TOTAL':
                    s[col] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:700'
            return s
 
        st.dataframe(
            pivot.style
                 .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                 .apply(sty_pivot, axis=None)
                 .format(lambda x: '' if x==0 else f'{x:,}'),
            use_container_width=True, height=500)
        st.download_button("⬇ Download CSV", pivot.to_csv(), "leads_by_rep_source.csv", "text/csv")
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONVERSION BY REP & SOURCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='sec-hdr'>Rep-wise Conversion by Source — Won / Lost / Active with %</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "For each rep and each source: total leads received, won, lost, active — "
                "numbers with % of that rep-source bucket in brackets. "
                "Win % column is colour coded 🟢 ≥5%  🟡 2–5%  🔴 0%</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data.")
    else:
        rows = []
        rep_order = (filt.groupby('Rep')['Stage']
                     .apply(lambda x:(x=='Won').sum())
                     .sort_values(ascending=False).index.tolist())
 
        for rep in rep_order:
            rep_d = filt[filt['Rep']==rep]
            for src in sorted(rep_d['Source_group'].unique()):
                src_d = rep_d[rep_d['Source_group']==src]
                n = len(src_d); w = (src_d['Stage']=='Won').sum()
                l = (src_d['Stage']=='Lost').sum(); a = (src_d['Stage']=='Active').sum()
                rows.append({'Rep':rep,'Source':src,'Leads':n,
                    'Won':fmt_n_pct(w,n),'Lost':fmt_n_pct(l,n),'Active':fmt_n_pct(a,n),
                    'Win %':f'{round(w/n*100,1)}%' if n else '0%',
                    '_won_pct':round(w/n*100,1) if n else 0,'_is_total':False,'_rep':rep})
            n = len(rep_d); w = (rep_d['Stage']=='Won').sum()
            l = (rep_d['Stage']=='Lost').sum(); a = (rep_d['Stage']=='Active').sum()
            rows.append({'Rep':f'▸ {rep} — TOTAL','Source':'','Leads':n,
                'Won':fmt_n_pct(w,n),'Lost':fmt_n_pct(l,n),'Active':fmt_n_pct(a,n),
                'Win %':f'{round(w/n*100,1)}%' if n else '0%',
                '_won_pct':round(w/n*100,1) if n else 0,'_is_total':True,'_rep':rep})
 
        detail = pd.DataFrame(rows)
        detail_disp = detail[['Rep','Source','Leads','Won','Lost','Active','Win %']].copy()
 
        def sty_detail(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i, row in detail.iterrows():
                if row['_is_total']:
                    s.loc[i, :] = 'background:#1B3A6B;color:white;font-weight:700'
                else:
                    p = row['_won_pct']
                    if p >= 5:   s.loc[i,'Win %'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                    elif p >= 2: s.loc[i,'Win %'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                    elif p == 0: s.loc[i,'Win %'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                    if row['Source'] in ('Existing Client','Ex-Client Ref.'):
                        s.loc[i,'Source'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                    if row['_won_pct'] > 0:
                        s.loc[i,'Won'] = 'background:#E9F7EF;color:#0A6640'
            return s
 
        st.dataframe(
            detail_disp.style
                       .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                       .apply(sty_detail, axis=None)
                       .format({'Leads':'{:,}'}),
            use_container_width=True, height=700)
        st.download_button("⬇ Download CSV", detail_disp.to_csv(index=False),
                           "conversion_by_rep_source.csv", "text/csv")
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PIPELINE BY REP
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='sec-hdr'>Active Pipeline — Rep-wise Breakdown</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "How many leads each rep has in each pipeline stage right now. "
                "🟢 Quoted stages (high intent)  🔴 Call Back / RNR (cold / stuck)  "
                "🟡 Interested / Catalogue (warm)</p>", unsafe_allow_html=True)
 
    active_f = filt[filt['Stage']=='Active']
    if len(active_f) == 0:
        st.info("No active leads in current filters.")
    else:
        pipe_cross = pd.crosstab(active_f['Rep'], active_f['FollowupStatus'],
                                  margins=True, margins_name='TOTAL')
        cold_cols = [c for c in pipe_cross.columns if 'Call Back' in c or 'RNR' in c]
        hot_cols  = [c for c in pipe_cross.columns
                     if any(x in c for x in ['Quoted','Quote']) and c!='TOTAL']
        warm_cols = [c for c in pipe_cross.columns if c not in cold_cols+hot_cols+['TOTAL']]
        col_order = cold_cols + warm_cols + hot_cols
        col_order += [c for c in pipe_cross.columns if c not in col_order and c!='TOTAL']
        if 'TOTAL' in pipe_cross.columns: col_order.append('TOTAL')
        pipe_cross = pipe_cross[[c for c in col_order if c in pipe_cross.columns]]
 
        def sty_pipe_cross(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in df.columns:
                if col == 'TOTAL':
                    s[col] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
                elif col in cold_cols:
                    s[col] = df[col].apply(
                        lambda v: 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                        if isinstance(v,int) and v>0 else '')
                elif col in hot_cols:
                    s[col] = df[col].apply(
                        lambda v: 'background:#E9F7EF;color:#0A6640;font-weight:700'
                        if isinstance(v,int) and v>0 else '')
                elif col in warm_cols:
                    s[col] = df[col].apply(
                        lambda v: 'background:#FFFBEB;color:#92400E'
                        if isinstance(v,int) and v>0 else '')
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:700'
            return s
 
        st.dataframe(
            pipe_cross.style
                      .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                      .apply(sty_pipe_cross, axis=None)
                      .format(lambda x: '' if x==0 else f'{x:,}'),
            use_container_width=True, height=500)
        st.download_button("⬇ Download CSV", pipe_cross.to_csv(), "pipeline_by_rep.csv", "text/csv")
 
        st.markdown("<div class='sec-hdr'>Where Each Rep's Active Leads Are Sitting</div>",
                    unsafe_allow_html=True)
        summary_rows = []
        for rep in [r for r in active_f['Rep'].unique() if r != 'TOTAL']:
            rd = active_f[active_f['Rep']==rep]; n = len(rd)
            cold_n = rd['FollowupStatus'].isin(cold_cols).sum() if cold_cols else 0
            hot_n  = rd['FollowupStatus'].isin(hot_cols).sum()  if hot_cols  else 0
            warm_n = n - cold_n - hot_n
            summary_rows.append({'Rep':rep,'Total Active':n,
                'Cold — CB/RNR':fmt_n_pct(cold_n,n),
                'High Intent — Quoted':fmt_n_pct(hot_n,n),
                'Warm — Interested':fmt_n_pct(warm_n,n),
                '_cold_pct':round(cold_n/n*100,1) if n else 0,
                '_hot_pct':round(hot_n/n*100,1) if n else 0})
 
        summ = pd.DataFrame(summary_rows).sort_values('_hot_pct', ascending=False)
        summ_disp = summ[['Rep','Total Active','Cold — CB/RNR','High Intent — Quoted','Warm — Interested']].copy()
 
        def sty_summ(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i,row in summ.iterrows():
                if row['_cold_pct'] >= 60:
                    s.loc[i,'Cold — CB/RNR'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                if row['_hot_pct'] >= 15:
                    s.loc[i,'High Intent — Quoted'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
            return s
 
        st.dataframe(
            summ_disp.style
                     .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                     .apply(sty_summ, axis=None)
                     .format({'Total Active':'{:,}'}),
            use_container_width=True, height=450)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LOST REASONS BY REP
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='sec-hdr'>Lost Reasons — Rep-wise Breakdown</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "How many leads each rep lost and why. "
                "Darker red = higher count. TOTAL column = rep's total lost leads.</p>",
                unsafe_allow_html=True)
 
    lost_f = filt[filt['Stage']=='Lost']
    if len(lost_f) == 0:
        st.info("No lost leads in current filters.")
    else:
        lost_cross = pd.crosstab(lost_f['Rep'], lost_f['FollowupStatus'],
                                  margins=True, margins_name='TOTAL')
        if 'TOTAL' in lost_cross.columns:
            non_total = [c for c in lost_cross.columns if c != 'TOTAL']
            lost_cross = lost_cross[non_total + ['TOTAL']]
 
        def sty_lost(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in df.columns:
                if col == 'TOTAL':
                    s[col] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
                else:
                    col_max = df[col].replace(0, np.nan).max()
                    if pd.notna(col_max) and col_max > 0:
                        s[col] = df[col].apply(lambda v: (
                            'background:#FEF2F2;color:#B91C1C;font-weight:700'
                            if v >= col_max * 0.6
                            else ('background:#FEF2F2;color:#B91C1C'
                                  if v >= col_max * 0.3
                                  else ('color:#B91C1C' if v > 0 else ''))))
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:700'
            return s
 
        st.dataframe(
            lost_cross.style
                      .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                      .apply(sty_lost, axis=None)
                      .format(lambda x: '' if x==0 else f'{x:,}'),
            use_container_width=True, height=500)
        st.download_button("⬇ Download CSV", lost_cross.to_csv(), "lost_reasons_by_rep.csv", "text/csv")
 
        st.markdown("<div class='sec-hdr'>Loss Rate Summary per Rep</div>", unsafe_allow_html=True)
        loss_summ_rows = []
        for rep in [r for r in lost_f['Rep'].unique()]:
            tot_rep  = filt[filt['Rep']==rep]
            lost_rep = tot_rep[tot_rep['Stage']=='Lost']
            n_tot = len(tot_rep); n_lost = len(lost_rep)
            top_reason = (lost_rep['FollowupStatus'].value_counts().index[0]
                          if len(lost_rep)>0 else '—')
            loss_summ_rows.append({'Rep':rep,'Total Leads':n_tot,'Lost':n_lost,
                'Loss %':f'{round(n_lost/n_tot*100,1)}%' if n_tot else '0%',
                'Top Lost Reason':top_reason,
                '_loss_pct':round(n_lost/n_tot*100,1) if n_tot else 0})
 
        ls = pd.DataFrame(loss_summ_rows).sort_values('_loss_pct', ascending=False)
        ls_disp = ls[['Rep','Total Leads','Lost','Loss %','Top Lost Reason']].copy()
 
        def sty_ls(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i,row in ls.iterrows():
                p = row['_loss_pct']
                if p >= 70:   s.loc[i,'Loss %'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                elif p >= 50: s.loc[i,'Loss %'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                else:         s.loc[i,'Loss %'] = 'background:#E9F7EF;color:#0A6640;font-weight:600'
            return s
 
        st.dataframe(
            ls_disp.style
                   .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                   .apply(sty_ls, axis=None)
                   .format({'Total Leads':'{:,}','Lost':'{:,}'}),
            use_container_width=True, height=450)
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — AMOUNT BY DEAL STAGE
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='sec-hdr'>💰 Amount Filled — By Deal Stage & Rep</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "Shows exactly which deal stages have quote amounts filled in. "
                "Use this to find where your team IS recording values and where they aren't. "
                "Green = amount present  🔴 = zero / blank.</p>", unsafe_allow_html=True)
 
    amt_col = None
    for possible in ['quotation_total_amount','QuotationAmount','Amount','QuoteValue',
                     'quote_amount','TotalAmount','QuotationTotalAmount','quotation_amount',
                     'Quote Amount','Quote_Amount','EstimatedValue','estimated_value']:
        if possible in filt.columns:
            amt_col = possible
            break
 
    with st.expander("🔍 Debug — All columns in your CRM file"):
        all_cols = list(filt.columns)
        st.write(f"**{len(all_cols)} columns found:**")
        numeric_cols = []
        for col in all_cols:
            try:
                series = pd.to_numeric(filt[col], errors='coerce')
                if series.notna().sum() > 0 and series.sum() != 0:
                    numeric_cols.append(f"✅ {col}  (has numeric values, sum={series.sum():,.0f})")
                else:
                    numeric_cols.append(f"○ {col}")
            except:
                numeric_cols.append(f"○ {col}")
        st.write("\n".join(numeric_cols))
 
    if amt_col is None:
        st.warning(
            "⚠️ No recognised amount column found. "
            "Check the debug expander above — look for a column marked ✅ with numeric values. "
            "Common KIT19 column names: `quotation_total_amount`, `QuotationAmount`, `Amount`."
        )
        st.markdown("<div class='sec-hdr'>Lead Count by Deal Stage (no amount data yet)</div>",
                    unsafe_allow_html=True)
        stage_counts = filt.groupby('FollowupStatus').agg(
            Leads=('Stage','count'),
            Won=('Stage', lambda x:(x=='Won').sum()),
            Lost=('Stage', lambda x:(x=='Lost').sum()),
            Active=('Stage', lambda x:(x=='Active').sum()),
        ).sort_values('Leads', ascending=False)
        st.dataframe(stage_counts, use_container_width=True, height=500)
 
    else:
        filt_amt = filt.copy()
        filt_amt[amt_col] = pd.to_numeric(filt_amt[amt_col], errors='coerce').fillna(0)
        filt_amt['has_amount'] = filt_amt[amt_col] > 0
 
        st.markdown("<div class='sec-hdr'>Where Is Amount Being Filled? — By Deal Stage</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Every FollowupStatus stage: how many leads, how many have amount filled, "
                    "total value, and fill rate. Sorted by total value descending.</p>",
                    unsafe_allow_html=True)
 
        stage_rows = []
        for stage_name in sorted(filt_amt['FollowupStatus'].dropna().unique()):
            sd = filt_amt[filt_amt['FollowupStatus'] == stage_name]
            n = len(sd)
            filled = sd['has_amount'].sum()
            total_val = sd[amt_col].sum()
            avg_val = sd[sd['has_amount']][amt_col].mean() if filled > 0 else 0
            pipeline_stage = sd['Stage'].mode()[0] if len(sd) > 0 else '—'
            stage_rows.append({
                'Deal Stage': stage_name,
                'CRM Stage': pipeline_stage,
                'Leads': n,
                'With Amount': filled,
                'Fill Rate': f'{round(filled/n*100,1)}%' if n else '0%',
                'Total Value ₹': total_val,
                'Avg Value ₹': avg_val,
                '_fill_pct': round(filled/n*100,1) if n else 0,
                '_total_val': total_val,
            })
 
        stage_df = pd.DataFrame(stage_rows).sort_values('_total_val', ascending=False)
        stage_disp = stage_df[['Deal Stage','CRM Stage','Leads','With Amount',
                                'Fill Rate','Total Value ₹','Avg Value ₹']].copy()
 
        def sty_stage(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i, row in stage_df.iterrows():
                p = row['_fill_pct']
                if p >= 50:   s.loc[i,'Fill Rate'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                elif p >= 10: s.loc[i,'Fill Rate'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                elif p == 0:  s.loc[i,'Fill Rate'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                if row['_total_val'] > 0:
                    s.loc[i,'Total Value ₹'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
            return s
 
        st.dataframe(
            stage_disp.style
                      .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                      .apply(sty_stage, axis=None)
                      .format({'Leads':'{:,}','With Amount':'{:,}',
                               'Total Value ₹':'₹{:,.0f}','Avg Value ₹':'₹{:,.0f}'}),
            use_container_width=True, height=500)
        st.download_button("⬇ Download CSV", stage_disp.to_csv(index=False),
                           "amount_by_stage.csv", "text/csv")
 
        st.markdown("<div class='sec-hdr'>Amount Fill Rate — By Rep</div>", unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Which reps are recording quote values and which aren't. "
                    "🟢 ≥50% filled  🟡 10–50%  🔴 &lt;10%</p>", unsafe_allow_html=True)
 
        rep_amt_rows = []
        for rep in sorted(filt_amt['Rep'].unique()):
            rd = filt_amt[filt_amt['Rep']==rep]
            n = len(rd); filled = rd['has_amount'].sum()
            won_d = rd[rd['Stage']=='Won']
            active_d = rd[rd['Stage']=='Active']
            lost_d = rd[rd['Stage']=='Lost']
            rep_amt_rows.append({
                'Rep': rep,
                'Total Leads': n,
                'With Amount': filled,
                'Fill Rate': f'{round(filled/n*100,1)}%' if n else '0%',
                'Won Value ₹': won_d[amt_col].sum(),
                'Active Pipeline ₹': active_d[amt_col].sum(),
                'Lost Value ₹': lost_d[amt_col].sum(),
                '_fill_pct': round(filled/n*100,1) if n else 0,
            })
 
        rep_amt_df = pd.DataFrame(rep_amt_rows).sort_values('_fill_pct', ascending=False)
 
        tot_n = len(filt_amt); tot_filled = filt_amt['has_amount'].sum()
        rep_amt_rows.append({
            'Rep': 'TOTAL',
            'Total Leads': tot_n,
            'With Amount': tot_filled,
            'Fill Rate': f'{round(tot_filled/tot_n*100,1)}%' if tot_n else '0%',
            'Won Value ₹': filt_amt[filt_amt['Stage']=='Won'][amt_col].sum(),
            'Active Pipeline ₹': filt_amt[filt_amt['Stage']=='Active'][amt_col].sum(),
            'Lost Value ₹': filt_amt[filt_amt['Stage']=='Lost'][amt_col].sum(),
            '_fill_pct': round(tot_filled/tot_n*100,1) if tot_n else 0,
        })
        rep_amt_df2 = pd.DataFrame(rep_amt_rows)
        rep_disp = rep_amt_df2.drop(columns=['_fill_pct'])
 
        def sty_rep_amt(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i, row in rep_amt_df2.iterrows():
                if row['Rep'] == 'TOTAL':
                    s.loc[i] = 'background:#0F2044;color:white;font-weight:700'
                    continue
                p = row['_fill_pct']
                if p >= 50:   s.loc[i,'Fill Rate'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                elif p >= 10: s.loc[i,'Fill Rate'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                else:         s.loc[i,'Fill Rate'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                if row['Won Value ₹'] > 0:
                    s.loc[i,'Won Value ₹'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
            return s
 
        st.dataframe(
            rep_disp.style
                    .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                    .apply(sty_rep_amt, axis=None)
                    .format({'Total Leads':'{:,}','With Amount':'{:,}',
                             'Won Value ₹':'₹{:,.0f}','Active Pipeline ₹':'₹{:,.0f}',
                             'Lost Value ₹':'₹{:,.0f}'}),
            use_container_width=True, height=480)
        st.download_button("⬇ Download CSV", rep_disp.to_csv(index=False),
                           "amount_by_rep.csv", "text/csv")
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — SOURCE PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("<div class='sec-hdr'>📈 Lead Source Performance — Full Breakdown</div>",
                unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>"
                "How each lead source is performing: volume, conversion, pipeline health, and loss. "
                "Answers: which sources give the best quality leads, not just the most leads.</p>",
                unsafe_allow_html=True)
 
    if total == 0:
        st.info("No data for current filters.")
    else:
        st.markdown("<div class='sec-hdr'>Source Summary — Volume, Win Rate, Loss Rate</div>",
                    unsafe_allow_html=True)
 
        src_rows = []
        for src in sorted(filt['Source_group'].unique()):
            sd = filt[filt['Source_group']==src]
            n = len(sd)
            w = (sd['Stage']=='Won').sum()
            l = (sd['Stage']=='Lost').sum()
            a = (sd['Stage']=='Active').sum()
            high_n = sd['FollowupStatus'].isin(HIGH_S).sum()
            cold_n = sd['FollowupStatus'].isin(['Call Back','RNR Call Back']).sum()
            wr_src = round(w/n*100,1) if n else 0
            lr_src = round(l/n*100,1) if n else 0
            hr_src = round(high_n/n*100,1) if n else 0
            cr_src = round(cold_n/n*100,1) if n else 0
 
            src_rows.append({
                'Source': src,
                'Leads': n,
                'Lead %': f'{round(n/total*100,1)}%',
                'Won': w,
                'Win Rate': f'{wr_src}%',
                'Lost': l,
                'Loss Rate': f'{lr_src}%',
                'Active': a,
                'High Intent': fmt_n_pct(high_n, n),
                'Cold CB/RNR': fmt_n_pct(cold_n, n),
                '_wr': wr_src, '_lr': lr_src, '_hr': hr_src, '_cr': cr_src,
                '_leads': n, '_won': w,
            })
 
        src_df = pd.DataFrame(src_rows).sort_values('_won', ascending=False)
 
        src_rows.append({
            'Source': 'TOTAL',
            'Leads': total,
            'Lead %': '100%',
            'Won': won,
            'Win Rate': f'{wr}%',
            'Lost': lost,
            'Loss Rate': f'{round(lost/total*100,1)}%',
            'Active': active,
            'High Intent': fmt_n_pct(high, total),
            'Cold CB/RNR': fmt_n_pct(cold, total),
            '_wr': wr, '_lr': 0, '_hr': 0, '_cr': 0, '_leads': total, '_won': won,
        })
        src_df_full = pd.DataFrame(src_rows)
        src_disp = src_df_full[['Source','Leads','Lead %','Won','Win Rate',
                                 'Lost','Loss Rate','Active','High Intent','Cold CB/RNR']].copy()
 
        def sty_src(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i, row in src_df_full.iterrows():
                if row['Source'] == 'TOTAL':
                    s.loc[i] = 'background:#0F2044;color:white;font-weight:700'
                    continue
                wr_v = row['_wr']; lr_v = row['_lr']
                if wr_v >= 10:   s.loc[i,'Win Rate'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                elif wr_v >= 3:  s.loc[i,'Win Rate'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                elif wr_v == 0:  s.loc[i,'Win Rate'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                if lr_v >= 70:   s.loc[i,'Loss Rate'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                elif lr_v >= 50: s.loc[i,'Loss Rate'] = 'background:#FFFBEB;color:#92400E;font-weight:600'
                else:            s.loc[i,'Loss Rate'] = 'background:#E9F7EF;color:#0A6640;font-weight:600'
                if row['_won'] > 0:
                    s.loc[i,'Won'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                if row['Source'] in ('Existing Client','Ex-Client Ref.'):
                    s.loc[i,'Source'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
            return s
 
        st.dataframe(
            src_disp.style
                    .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                    .apply(sty_src, axis=None)
                    .format({'Leads':'{:,}','Won':'{:,}','Lost':'{:,}','Active':'{:,}'}),
            use_container_width=True, height=450)
        st.download_button("⬇ Download CSV", src_disp.to_csv(index=False),
                           "source_performance.csv", "text/csv")
 
        st.markdown("<div class='sec-hdr'>Source × Pipeline Stage — Where Each Source's Leads End Up</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Cross-tab of source vs FollowupStatus. Shows quality of each source's pipeline.</p>",
                    unsafe_allow_html=True)
 
        src_stage_cross = pd.crosstab(filt['Source_group'], filt['FollowupStatus'],
                                       margins=True, margins_name='TOTAL')
        won_cols_ss  = [c for c in src_stage_cross.columns if c in WON_S]
        lost_cols_ss = [c for c in src_stage_cross.columns if c in LOST_S]
        rest_cols_ss = [c for c in src_stage_cross.columns
                        if c not in won_cols_ss + lost_cols_ss + ['TOTAL']]
        col_ord_ss   = won_cols_ss + rest_cols_ss + lost_cols_ss
        col_ord_ss  += [c for c in src_stage_cross.columns if c not in col_ord_ss and c!='TOTAL']
        if 'TOTAL' in src_stage_cross.columns: col_ord_ss.append('TOTAL')
        src_stage_cross = src_stage_cross[[c for c in col_ord_ss if c in src_stage_cross.columns]]
 
        def sty_src_stage(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for col in df.columns:
                if col == 'TOTAL':
                    s[col] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
                elif col in won_cols_ss:
                    s[col] = df[col].apply(
                        lambda v: 'background:#E9F7EF;color:#0A6640;font-weight:700'
                        if isinstance(v,int) and v>0 else '')
                elif col in lost_cols_ss:
                    s[col] = df[col].apply(
                        lambda v: 'background:#FEF2F2;color:#B91C1C'
                        if isinstance(v,int) and v>0 else '')
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:700'
            return s
 
        st.dataframe(
            src_stage_cross.style
                           .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                           .apply(sty_src_stage, axis=None)
                           .format(lambda x: '' if x==0 else f'{x:,}'),
            use_container_width=True, height=400)
 
        st.markdown("<div class='sec-hdr'>Source × Rep — Which Rep Handles Which Source Most</div>",
                    unsafe_allow_html=True)
        st.markdown("<p class='sub-note'>"
                    "Lead count per rep per source. Helps spot if certain sources are concentrated "
                    "with one rep and whether that rep is converting them well.</p>",
                    unsafe_allow_html=True)
 
        src_rep_cross = pd.crosstab(filt['Source_group'], filt['Rep'],
                                     margins=True, margins_name='TOTAL')
 
        def sty_src_rep(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            if 'TOTAL' in df.columns:
                s['TOTAL'] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:700'
            return s
 
        st.dataframe(
            src_rep_cross.style
                         .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                         .apply(sty_src_rep, axis=None)
                         .format(lambda x: '' if x==0 else f'{x:,}'),
            use_container_width=True, height=400)
        st.download_button("⬇ Download CSV", src_rep_cross.to_csv(),
                           "source_by_rep.csv", "text/csv")
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — REVENUE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown("<div class='sec-hdr'>💡 Revenue Summary — Rep-wise & Source-wise</div>",
                unsafe_allow_html=True)
 
    c_info1, c_info2 = st.columns(2)
    with c_info1:
        st.markdown("""
<div style='background:white;border-radius:8px;padding:16px;border:1px solid #E2E8F0;
            border-left:4px solid #0F2044;font-family:Arial,sans-serif;'>
<p style='color:#0F2044;font-weight:700;font-size:13px;margin:0 0 8px 0;'>WHAT IS BEING SHOWN</p>
<p style='color:#334155;font-size:12px;margin:4px 0;'>
  <b>Revenue Won ₹</b> — sum of quotation amounts for Won leads per rep / source.<br>
  <b>Pipeline Value ₹</b> — sum of quotation amounts for Active / Quoted leads still open.<br>
  <b>Lost Value ₹</b> — sum of quotation amounts for Lost leads.<br>
  <b>Avg Deal Size</b> — average quote value per rep, for deals where value is filled.<br>
  <b>Value Fill Rate</b> — % of leads where the quote amount is actually recorded.
</p>
</div>""", unsafe_allow_html=True)
    with c_info2:
        st.markdown("""
<div style='background:white;border-radius:8px;padding:16px;border:1px solid #E2E8F0;
            border-left:4px solid #B91C1C;font-family:Arial,sans-serif;'>
<p style='color:#B91C1C;font-weight:700;font-size:13px;margin:0 0 8px 0;'>⚠ DATA QUALITY WARNING</p>
<p style='color:#334155;font-size:12px;margin:4px 0;'>
  Quote Value is currently <b>0–5% filled</b> across all reps in KIT19.<br>
  This means revenue figures reflect only leads where a rep manually entered a quote amount.<br><br>
  <b>To fix:</b> Reps must fill Quote Value in the CRM when sending a quotation.
  Once fill rate is above 70%, this becomes the most important review metric.
</p>
</div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    amt_col = None
    for possible in ['quotation_total_amount','QuotationAmount','Amount','QuoteValue',
                     'quote_amount','TotalAmount','QuotationTotalAmount','quotation_amount',
                     'Quote Amount','Quote_Amount','EstimatedValue','estimated_value']:
        if possible in filt.columns:
            amt_col = possible
            break
 
    if amt_col is None:
        st.warning("No amount column found. Check the '💰 Amount by Deal Stage' tab for the debug tool.")
        sample = pd.DataFrame({
            'Rep':            ['Farhan','Suman','Nehamsafe','Deepak','Simmi','Shubham','TOTAL'],
            'Won Deals':      [17,17,14,10,6,4,73],
            'Revenue Won ₹':  ['[fill quote value]']*7,
            'Avg Deal Size ₹':['[fill quote value]']*7,
            'Open Pipeline ₹':['[fill quote value]']*7,
            'Lost Value ₹':   ['[fill quote value]']*7,
            'Value Fill %':   ['0%','0%','0%','0%','0%','0%','0%'],
        }).set_index('Rep')
        st.dataframe(sample, use_container_width=True, height=320)
    else:
        filt_amt = filt.copy()
        filt_amt[amt_col] = pd.to_numeric(filt_amt[amt_col], errors='coerce').fillna(0)
 
        st.markdown("<div class='sec-hdr'>Revenue & Pipeline Value — Rep-wise</div>",
                    unsafe_allow_html=True)
 
        rep_order_amt = (filt_amt.groupby('Rep')['Stage']
                          .apply(lambda x:(x=='Won').sum())
                          .sort_values(ascending=False).index.tolist())
 
        amt_rows = []
        for rep in rep_order_amt:
            rd = filt_amt[filt_amt['Rep']==rep]
            won_d = rd[rd['Stage']=='Won']; active_d = rd[rd['Stage']=='Active']
            lost_d = rd[rd['Stage']=='Lost']
            quoted_d = rd[rd['FollowupStatus'].str.contains('Quot|Quote', na=False, case=False)]
            n_total = len(rd); filled = (rd[amt_col] > 0).sum()
            fill_pct = round(filled/n_total*100,1) if n_total else 0
            rev_won = won_d[amt_col].sum(); pip_val = quoted_d[amt_col].sum()
            lost_val = lost_d[amt_col].sum()
            avg_deal = (won_d[won_d[amt_col]>0][amt_col].mean()
                        if len(won_d[won_d[amt_col]>0]) > 0 else 0)
            won_with_val = (won_d[amt_col] > 0).sum()
            amt_rows.append({'Rep':rep,'Won Deals':len(won_d),'Won (with value)':won_with_val,
                'Revenue Won ₹':f'₹{rev_won:,.0f}' if rev_won > 0 else '—',
                'Avg Deal Size ₹':f'₹{avg_deal:,.0f}' if avg_deal > 0 else '—',
                'Open Pipeline ₹':f'₹{pip_val:,.0f}' if pip_val > 0 else '—',
                'Lost Value ₹':f'₹{lost_val:,.0f}' if lost_val > 0 else '—',
                'Value Fill %':f'{fill_pct}%','_fill':fill_pct,'_rev':rev_won})
 
        all_won = filt_amt[filt_amt['Stage']=='Won']
        all_quot = filt_amt[filt_amt['FollowupStatus'].str.contains('Quot|Quote', na=False, case=False)]
        all_lost = filt_amt[filt_amt['Stage']=='Lost']
        tot_fill = round((filt_amt[amt_col]>0).sum()/len(filt_amt)*100,1) if len(filt_amt) else 0
        amt_rows.append({'Rep':'TOTAL','Won Deals':len(all_won),
            'Won (with value)':(all_won[amt_col]>0).sum(),
            'Revenue Won ₹':f'₹{all_won[amt_col].sum():,.0f}',
            'Avg Deal Size ₹':f'₹{all_won[all_won[amt_col]>0][amt_col].mean():,.0f}' if len(all_won[all_won[amt_col]>0])>0 else '—',
            'Open Pipeline ₹':f'₹{all_quot[amt_col].sum():,.0f}',
            'Lost Value ₹':f'₹{all_lost[amt_col].sum():,.0f}',
            'Value Fill %':f'{tot_fill}%','_fill':tot_fill,'_rev':all_won[amt_col].sum()})
 
        amt_df = pd.DataFrame(amt_rows)
        amt_disp = amt_df.drop(columns=['_fill','_rev']).set_index('Rep')
 
        def sty_amt(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i,row in amt_df.iterrows():
                idx = row['Rep']
                if idx == 'TOTAL':
                    s.loc[i if isinstance(df.index, pd.RangeIndex) else idx] = \
                        'background:#0F2044;color:white;font-weight:700'
                    continue
                p = row['_fill']
                if p >= 70:   s.loc[idx,'Value Fill %'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                elif p >= 30: s.loc[idx,'Value Fill %'] = 'background:#FFFBEB;color:#92400E'
                else:         s.loc[idx,'Value Fill %'] = 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                if row['_rev'] > 0:
                    s.loc[idx,'Revenue Won ₹'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
            return s
 
        st.dataframe(
            amt_disp.style
                    .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                    .apply(sty_amt, axis=None),
            use_container_width=True, height=480)
        st.download_button("⬇ Download CSV", amt_disp.to_csv(), "revenue_by_rep.csv", "text/csv")
 
        st.markdown("<div class='sec-hdr'>Revenue by Source</div>", unsafe_allow_html=True)
        src_amt_rows = []
        for src in sorted(filt_amt['Source_group'].unique()):
            sd = filt_amt[filt_amt['Source_group']==src]
            won_sd = sd[sd['Stage']=='Won']
            rev = won_sd[amt_col].sum()
            avg = won_sd[won_sd[amt_col]>0][amt_col].mean() if len(won_sd[won_sd[amt_col]>0])>0 else 0
            src_amt_rows.append({'Source':src,'Total Leads':len(sd),'Won Deals':len(won_sd),
                'Revenue Won ₹':f'₹{rev:,.0f}' if rev > 0 else '—',
                'Avg per Won ₹':f'₹{avg:,.0f}' if avg > 0 else '—',
                '_rev':rev,'_won':len(won_sd)})
 
        src_amt = pd.DataFrame(src_amt_rows).sort_values('_rev', ascending=False)
        src_disp = src_amt.drop(columns=['_rev','_won']).set_index('Source')
 
        def sty_src_amt(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            for i,row in src_amt.iterrows():
                idx = row['Source']
                if row['_rev'] > 0:
                    s.loc[idx,'Revenue Won ₹'] = 'background:#E9F7EF;color:#0A6640;font-weight:700'
                if row['_won'] > 0:
                    s.loc[idx,'Won Deals'] = 'background:#E9F7EF;color:#0A6640;font-weight:600'
            return s
 
        st.dataframe(
            src_disp.style
                    .set_properties(**{'color':'#0F172A','font-size':'13px','font-weight':'500'})
                    .apply(sty_src_amt, axis=None),
            use_container_width=True, height=360)
        st.download_button("⬇ Download CSV", src_disp.to_csv(), "revenue_by_source.csv", "text/csv")
 
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{len(filt):,} leads shown with current filters</p>", unsafe_allow_html=True)
