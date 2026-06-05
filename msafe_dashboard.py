import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="MSafe CRM Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k,v in [('drill_df',None),('drill_label','')]:
    if k not in st.session_state: st.session_state[k]=v

def drill(df, label):
    st.session_state.drill_df    = df.reset_index(drop=True)
    st.session_state.drill_label = label

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
:root{--bg:#F8FAFC;--ink:#0F172A;--navy:#0F2044;}
html,body,.stApp,[data-testid="stAppViewContainer"],
[data-testid="stMain"],.block-container,[data-testid="stMain"]>div{
    background:#F8FAFC !important;color:#0F172A !important;}
[data-testid="stMain"] *,.block-container *,
.stMarkdown *,[data-testid="stMarkdownContainer"] *{color:#0F172A !important;}
/* Sidebar */
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div{background:#0F2044 !important;}
section[data-testid="stSidebar"] *{color:white !important;}
section[data-testid="stSidebar"] hr{border-color:#2D5F9E !important;}
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"]>div{
    background:#162955 !important;border:1px solid #2D5F9E !important;border-radius:6px !important;}
section[data-testid="stSidebar"] .stMultiSelect input{color:white !important;}
section[data-testid="stSidebar"] .stMultiSelect [aria-placeholder]{color:#8BAFD4 !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"]{background:#2D5F9E !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg{color:white !important;fill:white !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{
    background:#162955 !important;border:2px dashed #2D5F9E !important;border-radius:8px !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span{color:#8BAFD4 !important;}
/* KPI */
.kpi{background:white;border-radius:10px;padding:14px;text-align:center;
     box-shadow:0 2px 6px rgba(0,0,0,0.07);border-top:3px solid #CBD5E1;height:80px;
     display:flex;flex-direction:column;justify-content:center;}
.kpi-l{font-size:10px;color:#64748B;font-weight:700;text-transform:uppercase;
       letter-spacing:.06em;margin-bottom:4px;}
.kpi-v{font-size:22px;font-weight:800;color:#0F2044;}
.kpi-v.g{color:#0A6640;}.kpi-v.r{color:#B91C1C;}
.kpi-v.a{color:#92400E;}.kpi-v.b{color:#1D4ED8;}
/* Drill box */
.drill-box{background:#EEF2FF;border:1px solid #C7D2FE;border-left:4px solid #0F2044;
           border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:12px;}
.drill-title{font-weight:700;color:#0F2044;font-size:13px;margin-bottom:8px;}
/* Section */
.sec{background:#0F2044;color:white !important;padding:9px 16px;border-radius:6px;
     font-weight:700;font-size:13px;margin:20px 0 8px;}
.note{font-size:11px;color:#64748B;font-style:italic;margin:0 0 8px;}
/* Dataframe */
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"]*{
    background:#1B3A6B !important;color:white !important;
    font-size:12px !important;font-weight:700 !important;}
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"]*{color:#0F172A !important;font-size:12px !important;}
[data-testid="stDataFrame"] [role="rowheader"],
[data-testid="stDataFrame"] [role="rowheader"]*{
    color:#0F172A !important;font-size:12px !important;
    font-weight:600 !important;background:#F1F5F9 !important;}
</style>""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
WON_S  = ['Quoted Order Won And Executed']
LOST_S = ['Not-Interested','Not Search Our Product','Regret',
          'Other Department Working','Wrong Number','No Response on RNR',
          'Already Purchased','Quoted Order Lost',
          'Repeat Lead','Rental Period Less Than 7 Days']   # confirmed lost
OPEN_S_LABEL = ("Call Back, RNR Call Back, Quoted In Follow Up, Quoted Order In Pipeline, "
                "Quote In Progress, Interested Quote Sent, Interested Catalogue Sent, "
                "Quoted Not Picking Call, Quoted Project On Hold, MS Requirement Call Back, "
                "and all other active stages")
WON_S_LABEL  = "Quoted Order Won And Executed"
LOST_S_LABEL = ("Not Interested, Not Search Our Product, Regret, Other Department Working, "
                "Wrong Number, No Response on RNR, Already Purchased, Quoted Order Lost, "
                "Repeat Lead, Rental Period Less Than 7 Days")

ADMIN = ['msafe947362','50988-Surbhi']
SRC_MAP = {
    'Just Dial':'JustDial','Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SRC  = ['JustDial','IndiaMart','IVR Call','Existing Client','Ex-Client Ref.','Facebook','Other']
SRC_SHORT = {'JustDial':'JD','IndiaMart':'IM','IVR Call':'IVR',
             'Existing Client':'EC','Ex-Client Ref.':'ECR','Facebook':'FB','Other':'Oth'}
RNR_S     = ['Call Back','RNR Call Back']
TODAY     = pd.Timestamp.now().normalize()   # dynamic — works for any data period

BASE = {'color':'#0F172A','font-size':'12px','font-weight':'500'}

# ── LEAD DISPLAY COLUMNS ───────────────────────────────────────────────────────
LCOLS = {
    'LeadNo':'Lead #','PersonName':'Customer','CompanyName':'Company',
    'City':'City','Source':'Source','Category':'Category',
    'Rep':'Rep','FollowupStatus':'Status','Stage':'Stage',
    'CreatedOn':'Created','age_days':'Age (days)',
    'LastFollowupedOn':'Last Contact','Remarks':'Remarks',
}

# ── DATA LOAD ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading CRM data…")
def load(fb):
    df = pd.read_excel(BytesIO(fb), engine='openpyxl')
    df['Stage'] = df['FollowupStatus'].apply(
        lambda x: 'Won' if x in WON_S else ('Lost' if x in LOST_S else 'Open'))
    df['Source'] = df['SourceName'].replace(SRC_MAP)
    df['Source_group'] = df['Source'].apply(lambda x: x if x in MAIN_SRC else 'Other')
    df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)
    df['Rep'] = df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
    df.loc[df['is_admin'],'Rep'] = 'Admin'
    if 'CreatedOn' in df.columns:
        df['CreatedOn']    = pd.to_datetime(df['CreatedOn'], errors='coerce')
        df['age_days']     = (TODAY - df['CreatedOn']).dt.days.clip(lower=0)
        df['Month']        = df['CreatedOn'].dt.strftime('%b %Y')
    if 'LastFollowupedOn' in df.columns:
        df['LastFollowupedOn'] = pd.to_datetime(df['LastFollowupedOn'], errors='coerce')
    if 'FollowupDate' in df.columns:
        df['FollowupDate_dt'] = pd.to_datetime(df['FollowupDate'], errors='coerce')
    if 'AmountPaid' in df.columns:
        df['AmountPaid'] = pd.to_numeric(df['AmountPaid'], errors='coerce').fillna(0)
    return df

def prep_lead_table(df):
    cols = [c for c in LCOLS if c in df.columns]
    out  = df[cols].copy()
    out.columns = [LCOLS[c] for c in cols]
    if 'Created'      in out: out['Created']      = out['Created'].dt.strftime('%d %b %Y')
    if 'Last Contact' in out: out['Last Contact']  = out['Last Contact'].dt.strftime('%d %b %Y')
    return out

def show_drill():
    if st.session_state.drill_df is None: return
    df  = st.session_state.drill_df
    lbl = st.session_state.drill_label
    st.markdown(f"<div class='drill-box'><div class='drill-title'>"
                f"📋 {lbl}  —  {len(df):,} leads</div></div>",
                unsafe_allow_html=True)
    if len(df) == 0:
        st.info("No leads match.")
        return
    ld = prep_lead_table(df)
    sty = ld.style.set_properties(**BASE)
    if 'Stage' in ld.columns:
        sty = sty.map(lambda v:(
            'background:#E9F7EF;color:#0A6640;font-weight:700' if v=='Won'
            else ('background:#FEF2F2;color:#B91C1C;font-weight:700' if v=='Lost'
                  else 'background:#FFFBEB;color:#92400E')),
            subset=['Stage'])
    st.dataframe(sty, use_container_width=True, height=360)
    st.download_button("⬇ Download these leads",
                       ld.to_csv(index=False), "leads_drill.csv",
                       "text/csv", key="dl_drill")
    if st.button("✕  Close this view", key="close_drill"):
        st.session_state.drill_df = None
        st.rerun()

# ── TABLE HELPER ───────────────────────────────────────────────────────────────
def tbl_header(cols, widths):
    row = st.columns(widths)
    for c,lbl in zip(row, cols):
        c.markdown(f"<div style='font-size:11px;font-weight:700;color:#475569;"
                   f"border-bottom:2px solid #0F2044;padding-bottom:3px;"
                   f"margin-bottom:4px;'>{lbl}</div>", unsafe_allow_html=True)

def tbl_sep():
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:2px 0;'>",
                unsafe_allow_html=True)

def num_btn(col, val, key, df, label, color='#0F172A'):
    if val == 0:
        col.markdown(f"<div style='font-size:13px;color:#CBD5E1;padding:5px 0;'>—</div>",
                     unsafe_allow_html=True)
    elif col.button(f"{val:,}", key=key, help=label):
        drill(df, label)

def txt_cell(col, val, bold=False, color='#0F172A'):
    fw = '700' if bold else '500'
    col.markdown(f"<div style='font-size:13px;font-weight:{fw};color:{color};"
                 f"padding:5px 0;'>{val}</div>", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])

if not uploaded:
    _,m,_ = st.columns([1,2,1])
    with m:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;padding:48px 24px;background:white;"
            "border-radius:12px;border:1px solid #E2E8F0;'>"
            "<div style='font-size:52px;'>📂</div>"
            "<div style='font-size:22px;font-weight:800;color:#0F2044 !important;"
            "margin:14px 0 8px;'>MSafe Inside Sales Dashboard</div>"
            "<div style='font-size:14px;color:#64748B;'>"
            "Upload your KIT19 CRM export from the sidebar.<br>"
            "Supports single month or multi-month exports.</div>"
            "</div>", unsafe_allow_html=True)
    st.stop()

df_raw  = load(uploaded.read())
reps_df = df_raw[~df_raw['is_admin']].copy()

# Sidebar filters
st.sidebar.markdown("### Filters")
all_reps = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps = st.sidebar.multiselect("Rep", all_reps, default=all_reps)

# Month filter — only shown if data spans multiple months
if 'Month' in reps_df.columns:
    months_avail = sorted(reps_df['Month'].dropna().unique().tolist(),
                          key=lambda m: pd.to_datetime(m, format='%b %Y'))
    if len(months_avail) > 1:
        sel_months = st.sidebar.multiselect("Month", months_avail, default=months_avail)
    else:
        sel_months = months_avail
else:
    sel_months = []

all_src = sorted(reps_df['Source'].dropna().unique().tolist())
sel_src = st.sidebar.multiselect("Source", all_src, default=all_src)
sel_stage = st.sidebar.multiselect("Stage", ['Open','Won','Lost'], default=['Open','Won','Lost'])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")
if 'Month' in reps_df.columns and len(months_avail)>1:
    st.sidebar.markdown(f"**Period:** {months_avail[0]} → {months_avail[-1]}")

# Apply filters
base = reps_df.copy()
if sel_reps:   base = base[base['Rep'].isin(sel_reps)]
if sel_src:    base = base[base['Source'].isin(sel_src)]
if sel_stage:  base = base[base['Stage'].isin(sel_stage)]
if sel_months and 'Month' in base.columns:
    base = base[base['Month'].isin(sel_months)]

rep_order = (base.groupby('Rep')['Stage']
             .apply(lambda x:(x=='Won').sum())
             .sort_values(ascending=False).index.tolist())

# Aggregates
total  = len(base)
won    = int((base['Stage']=='Won').sum())
lost   = int((base['Stage']=='Lost').sum())
opn    = int((base['Stage']=='Open').sum())
wr     = round(won/total*100,1) if total else 0

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='background:#0F2044;padding:16px 24px;border-radius:10px;"
    "margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;'>"
    "<span style='color:white !important;font-size:18px;font-weight:700;'>"
    "MSafe Equipments — Inside Sales Dashboard</span>"
    "<span style='color:#8BAFD4;font-size:12px;'>KIT19 CRM  |  Dynamic date range</span>"
    "</div>", unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
kc = st.columns(6)
def kpi(col,lbl,val,cls=''):
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{lbl}</div>"
                 f"<div class='kpi-v {cls}'>{val}</div></div>",unsafe_allow_html=True)
kpi(kc[0],'Total Leads',f'{total:,}')
kpi(kc[1],'Won',f'{won:,}','g')
kpi(kc[2],'Open',f'{opn:,}','a')
kpi(kc[3],'Lost',f'{lost:,}','r')
kpi(kc[4],'Win Rate',f'{wr}%','b')
kpi(kc[5],'Data as of',TODAY.strftime('%d %b %Y'))

# Quick KPI buttons
bk = st.columns(4)
pairs = [('All leads',base),('Won leads',base[base['Stage']=='Won']),
         ('Open leads',base[base['Stage']=='Open']),('Lost leads',base[base['Stage']=='Lost'])]
for col,(lbl,df_) in zip(bk,pairs):
    if col.button(f"→ View {lbl} ({len(df_):,})", key=f"kpi_{lbl}"):
        drill(df_, lbl.capitalize())

st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:12px 0;'>",
            unsafe_allow_html=True)

# ── DRILL BOX (always at top) ──────────────────────────────────────────────────
if st.session_state.drill_df is not None:
    show_drill()
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:12px 0;'>",
                unsafe_allow_html=True)
else:
    st.markdown(
        "<div style='background:#F1F5F9;border:1px dashed #CBD5E1;border-radius:8px;"
        "padding:12px 16px;color:#64748B;font-size:13px;margin-bottom:12px;'>"
        "👆  Click any number button in the tables below to see those leads here."
        "</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 1 — REP PERFORMANCE  (Won / Open / Lost)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 1 — Rep Performance</div>",unsafe_allow_html=True)
st.markdown(
    f"<p class='note'>"
    f"<b title='{WON_S_LABEL}'>Won ℹ</b> = {WON_S_LABEL[:60]}…  &nbsp;|&nbsp;  "
    f"<b>Open</b> = remaining active stages  &nbsp;|&nbsp;  "
    f"<b title='{LOST_S_LABEL}'>Lost ℹ</b> = {LOST_S_LABEL[:70]}…"
    f"<br>Hover the ℹ next to Won and Lost to see full stage list.</p>",
    unsafe_allow_html=True)

WIDS1 = [2.2, 0.8, 0.85, 0.85, 0.85, 0.7, 1.3]

# Column headers with full tooltip via title attribute
st.markdown(
    f"<div style='display:flex;gap:4px;margin-bottom:4px;'>"
    f"<div style='flex:2.2;font-size:11px;font-weight:700;color:#475569;border-bottom:2px solid #0F2044;padding-bottom:3px;'>Rep</div>"
    f"<div style='flex:0.8;font-size:11px;font-weight:700;color:#475569;border-bottom:2px solid #0F2044;padding-bottom:3px;'>Total</div>"
    f"<div style='flex:0.85;font-size:11px;font-weight:700;color:#0A6640;border-bottom:2px solid #0F2044;padding-bottom:3px;' title='{WON_S_LABEL}'>Won ℹ</div>"
    f"<div style='flex:0.85;font-size:11px;font-weight:700;color:#92400E;border-bottom:2px solid #0F2044;padding-bottom:3px;' title='{OPEN_S_LABEL}'>Open ℹ</div>"
    f"<div style='flex:0.85;font-size:11px;font-weight:700;color:#B91C1C;border-bottom:2px solid #0F2044;padding-bottom:3px;' title='{LOST_S_LABEL}'>Lost ℹ</div>"
    f"<div style='flex:0.7;font-size:11px;font-weight:700;color:#475569;border-bottom:2px solid #0F2044;padding-bottom:3px;'>Win %</div>"
    f"<div style='flex:1.3;font-size:11px;font-weight:700;color:#475569;border-bottom:2px solid #0F2044;padding-bottom:3px;'>View all</div>"
    f"</div>", unsafe_allow_html=True)

for rep in rep_order:
    rd  = base[base['Rep']==rep]
    rw  = rd[rd['Stage']=='Won']
    ro  = rd[rd['Stage']=='Open']
    rl  = rd[rd['Stage']=='Lost']
    wp  = round(len(rw)/len(rd)*100,1) if len(rd) else 0
    wpc = '#0A6640' if wp>=5 else ('#92400E' if wp>=2 else '#B91C1C')
    c   = st.columns(WIDS1)
    txt_cell(c[0], rep, bold=True, color='#0F2044')
    txt_cell(c[1], f'{len(rd):,}')
    num_btn(c[2], len(rw), f"t1w_{rep}", rw, f"Won — {rep}", '#0A6640')
    num_btn(c[3], len(ro), f"t1o_{rep}", ro, f"Open — {rep}", '#92400E')
    num_btn(c[4], len(rl), f"t1l_{rep}", rl, f"Lost — {rep}", '#B91C1C')
    txt_cell(c[5], f"{wp}%", bold=True, color=wpc)
    if c[6].button(f"→ All {len(rd):,}", key=f"t1all_{rep}"):
        drill(rd, f"All leads — {rep}")

tbl_sep()
# Totals
tc = st.columns(WIDS1)
for i,v in enumerate([('TOTAL','',True,'#0F172A'),(f'{total:,}','',True,'#0F172A'),
                       (f'{won:,}','',True,'#0A6640'),(f'{opn:,}','',True,'#92400E'),
                       (f'{lost:,}','',True,'#B91C1C'),(f'{wr}%','',True,'#1D4ED8')]):
    txt_cell(tc[i], v[0], bold=v[2], color=v[3])

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 2 — REP × SOURCE  (wide: Won/Open/Lost per source + totals)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 2 — Rep Performance by Source (Won / Open / Lost per Source)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>Each source shows three numbers: Won | Open | Lost. "
            "Row totals on right. Column totals at bottom. Click any number to see those leads.</p>",
            unsafe_allow_html=True)

# Build dataframe for display
src_display = [s for s in MAIN_SRC if base[base['Source_group']==s].shape[0]>0]
rows2 = []
for rep in rep_order:
    rd = base[base['Rep']==rep]
    row = {'Rep':rep}
    for src in src_display:
        sh = SRC_SHORT.get(src, src[:3])
        sd = rd[rd['Source_group']==src]
        row[f'{sh}-W'] = int((sd['Stage']=='Won').sum())
        row[f'{sh}-O'] = int((sd['Stage']=='Open').sum())
        row[f'{sh}-L'] = int((sd['Stage']=='Lost').sum())
    row['Tot-W'] = int((rd['Stage']=='Won').sum())
    row['Tot-O'] = int((rd['Stage']=='Open').sum())
    row['Tot-L'] = int((rd['Stage']=='Lost').sum())
    rows2.append(row)
# Total row
tot2 = {'Rep':'TOTAL'}
for src in src_display:
    sh = SRC_SHORT.get(src, src[:3])
    sd = base[base['Source_group']==src]
    tot2[f'{sh}-W'] = int((sd['Stage']=='Won').sum())
    tot2[f'{sh}-O'] = int((sd['Stage']=='Open').sum())
    tot2[f'{sh}-L'] = int((sd['Stage']=='Lost').sum())
tot2['Tot-W']=won; tot2['Tot-O']=opn; tot2['Tot-L']=lost
rows2.append(tot2)

df2 = pd.DataFrame(rows2).set_index('Rep')

def sty_t2(df):
    s = pd.DataFrame('', index=df.index, columns=df.columns)
    for col in df.columns:
        if col.endswith('-W'):
            s[col] = df[col].apply(
                lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif col.endswith('-L'):
            s[col] = df[col].apply(
                lambda v:'background:#FEF2F2;color:#B91C1C'
                if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif col.endswith('-O'):
            s[col] = df[col].apply(
                lambda v:'background:#FFFBEB;color:#92400E'
                if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif 'Tot' in col:
            s[col] = 'background:#EAF0FB;color:#0F2044;font-weight:700'
    if 'TOTAL' in df.index:
        try:
            s = s.apply(lambda col: col.map(
                lambda v: 'background:#E8EDF5;color:#0F172A;font-weight:800'), axis=0)
            s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:800'
        except: pass
    return s

st.dataframe(
    df2.style.set_properties(**BASE).apply(sty_t2, axis=None)
       .format(lambda x: '—' if isinstance(x,(int,float)) and x==0 else
               (f'{x:,}' if isinstance(x,(int,float)) else x)),
    use_container_width=True, height=450)

# Drill-through for Table 2
st.markdown("<p class='note'>Select rep + source + stage below to drill into any cell:</p>",
            unsafe_allow_html=True)
d1,d2,d3,d4 = st.columns([2,2,2,1.2])
d_rep = d1.selectbox("Rep",   ['All']+rep_order,   key='t2_rep')
d_src = d2.selectbox("Source",['All']+src_display, key='t2_src')
d_stg = d3.selectbox("Stage", ['All','Won','Open','Lost'], key='t2_stg')
if d4.button("→ View leads", key='t2_drill'):
    fd = base.copy()
    if d_rep!='All': fd=fd[fd['Rep']==d_rep]
    if d_src!='All': fd=fd[fd['Source_group']==d_src]
    if d_stg!='All': fd=fd[fd['Stage']==d_stg]
    drill(fd, f"{d_stg} leads — {d_rep} | {d_src}")

st.download_button("⬇ Download Table 2 (CSV)", df2.to_csv(), "rep_source.csv","text/csv",key="dl_t2")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 3 — SOURCE PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 3 — Source Performance</div>",unsafe_allow_html=True)
st.markdown("<p class='note'>Sorted by Win % descending. Click any number to see those leads.</p>",
            unsafe_allow_html=True)

WIDS3 = [2, 0.8, 0.8, 0.8, 0.8, 0.7, 1.3]
tbl_header(['Source','Total','Won','Open','Lost','Win %','View all'], WIDS3)

src_stats=[]
for src in src_display:
    sd=base[base['Source_group']==src]
    nw=int((sd['Stage']=='Won').sum()); nt=len(sd)
    src_stats.append((src,sd,nw,nt))
src_stats.sort(key=lambda x:x[2]/x[3] if x[3] else 0, reverse=True)

for src,sd,nw,nt in src_stats:
    so=sd[sd['Stage']=='Open']; sl=sd[sd['Stage']=='Lost']
    sw=sd[sd['Stage']=='Won']
    wp=round(nw/nt*100,1) if nt else 0
    wpc='#0A6640' if wp>=10 else ('#92400E' if wp>=3 else '#B91C1C')
    c=st.columns(WIDS3)
    txt_cell(c[0], src, bold=True, color='#0F2044')
    txt_cell(c[1], f'{nt:,}')
    num_btn(c[2], len(sw), f"t3w_{src}", sw, f"Won — {src}")
    num_btn(c[3], len(so), f"t3o_{src}", so, f"Open — {src}")
    num_btn(c[4], len(sl), f"t3l_{src}", sl, f"Lost — {src}")
    txt_cell(c[5], f"{wp}%", bold=True, color=wpc)
    if c[6].button(f"→ All {nt:,}", key=f"t3a_{src}"):
        drill(sd, f"All leads — {src}")

tbl_sep()
tc3=st.columns(WIDS3)
txt_cell(tc3[0],'TOTAL',bold=True)
txt_cell(tc3[1],f'{total:,}',bold=True)
txt_cell(tc3[2],f'{won:,}',bold=True,color='#0A6640')
txt_cell(tc3[3],f'{opn:,}',bold=True,color='#92400E')
txt_cell(tc3[4],f'{lost:,}',bold=True,color='#B91C1C')
txt_cell(tc3[5],f'{wr}%',bold=True,color='#1D4ED8')

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 4 — AMOUNT (AmountPaid)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 4 — Amount Paid (₹)</div>",unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "Based on AmountPaid field from KIT19. Only leads where amount > 0 are counted. "
            "Click count to see those leads.</p>", unsafe_allow_html=True)

WIDS4=[2.2,0.9,1.3,1.5,1.3,1.3]
tbl_header(['Rep','Leads with ₹','Total Amount ₹','Avg Amount ₹','Max Amount ₹','View'],WIDS4)

amt_rows=[]
if 'AmountPaid' in base.columns:
    for rep in rep_order:
        rd=base[base['Rep']==rep]
        paid=rd[rd['AmountPaid']>0]
        if len(paid)==0 and len(rd)==0: continue
        ta=paid['AmountPaid'].sum(); av=paid['AmountPaid'].mean() if len(paid) else 0
        mx=paid['AmountPaid'].max() if len(paid) else 0
        amt_rows.append((rep,rd,paid,len(paid),ta,av,mx))
        c=st.columns(WIDS4)
        txt_cell(c[0],rep,bold=True,color='#0F2044')
        num_btn(c[1],len(paid),f"t4n_{rep}",paid,f"Paid leads — {rep}")
        txt_cell(c[2],f'₹{ta:,.0f}' if ta>0 else '—',bold=ta>0,color='#0A6640' if ta>0 else '#CBD5E1')
        txt_cell(c[3],f'₹{av:,.0f}' if av>0 else '—')
        txt_cell(c[4],f'₹{mx:,.0f}' if mx>0 else '—')
        if c[5].button(f"→ View",key=f"t4v_{rep}",help=f"All leads with amount — {rep}"):
            drill(rd,f"All leads (amount) — {rep}")

    tbl_sep()
    all_paid=base[base['AmountPaid']>0]
    tc4=st.columns(WIDS4)
    txt_cell(tc4[0],'TOTAL',bold=True)
    num_btn(tc4[1],len(all_paid),'t4_tot',all_paid,"All leads with amount paid")
    txt_cell(tc4[2],f'₹{all_paid["AmountPaid"].sum():,.0f}',bold=True,color='#0A6640')
    txt_cell(tc4[3],f'₹{all_paid["AmountPaid"].mean():,.0f}' if len(all_paid) else '—')
    txt_cell(tc4[4],f'₹{all_paid["AmountPaid"].max():,.0f}' if len(all_paid) else '—')
else:
    st.info("AmountPaid column not found in this export.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 5 — STALE LEADS  (active lead aging buckets)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 5 — Stale Open Leads (Age Buckets)</div>",unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "Open leads only, bucketed by age from created date to today. "
            "🟢 Fresh  🟡 Needs attention  🟠 Stale  🔴 Problem. Click any number.</p>",
            unsafe_allow_html=True)

if 'age_days' in base.columns:
    def age_bkt(d):
        if pd.isna(d) or d<0: return '0–7 days'
        if d<=7:  return '0–7 days'
        if d<=15: return '8–15 days'
        if d<=30: return '16–30 days'
        return '30+ days'
    BKTS=['0–7 days','8–15 days','16–30 days','30+ days']
    open_b=base[base['Stage']=='Open'].copy()
    open_b['bkt']=open_b['age_days'].apply(age_bkt)
    WIDS5=[2.2,0.9,1,1,1,0.9,1.2]
    tbl_header(['Rep','Total Open','0–7 days','8–15 days','16–30 days','30+ days','→ All Open'],WIDS5)
    bkt_colors={'0–7 days':'#0A6640','8–15 days':'#92400E','16–30 days':'#B45309','30+ days':'#B91C1C'}
    for rep in rep_order:
        rd=open_b[open_b['Rep']==rep]; n=len(rd)
        if n==0: continue
        c=st.columns(WIDS5)
        txt_cell(c[0],rep,bold=True,color='#0F2044')
        txt_cell(c[1],f'{n:,}')
        for i,bkt in enumerate(BKTS,2):
            bd=rd[rd['bkt']==bkt]
            num_btn(c[i],len(bd),f"t5_{rep}_{bkt}",bd,f"{bkt} open — {rep}",bkt_colors[bkt])
        if c[6].button(f"→ All {n}",key=f"t5a_{rep}"):
            drill(rd,f"All open leads — {rep}")
    tbl_sep()
    tc5=st.columns(WIDS5); txt_cell(tc5[0],'TOTAL',bold=True)
    txt_cell(tc5[1],f'{len(open_b):,}',bold=True)
    for i,bkt in enumerate(BKTS,2):
        bd=open_b[open_b['bkt']==bkt]
        txt_cell(tc5[i],f'{len(bd):,}',bold=True,color=bkt_colors[bkt])
else:
    st.warning("CreatedOn date not available — cannot calculate aging.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 6 — CRM HYGIENE  (daily report)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 6 — CRM Hygiene Report  (share with team daily)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "Numbers only. Each number clickable — shows the exact leads causing the issue. "
            "All metrics are for OPEN leads unless noted.</p>", unsafe_allow_html=True)

WIDS6=[2,0.9,1.1,1.2,1.1,1.1,1.1,1.1]
tbl_header([
    'Rep','Total Open',
    'No Followup\nDate',
    'Overdue\nFollowup',
    'No City\nFilled',
    'No Category\nFilled',
    'RNR Stuck\n7+ Days',
    '30+ Day\nOpen Leads'],
    WIDS6)

open_all=base[base['Stage']=='Open'].copy()

for rep in rep_order:
    rd=open_all[open_all['Rep']==rep]
    if len(rd)==0: continue

    # 1. No followup date
    no_fu = rd[rd.get('FollowupDate_dt',pd.Series(dtype='datetime64[ns]',index=rd.index)).isna()] \
        if 'FollowupDate_dt' in rd.columns else rd[rd['FollowupDate'].isna()] \
        if 'FollowupDate' in rd.columns else pd.DataFrame()

    # 2. Overdue followup (followup date < today, still open)
    if 'FollowupDate_dt' in rd.columns:
        overdue=rd[rd['FollowupDate_dt'].notna() & (rd['FollowupDate_dt']<TODAY)]
    else:
        overdue=pd.DataFrame()

    # 3. No city
    no_city=rd[rd['City'].isna()|rd['City'].astype(str).str.strip().isin(['','0','nan'])] \
        if 'City' in rd.columns else pd.DataFrame()

    # 4. No category
    no_cat=rd[rd['Category'].isna()|rd['Category'].astype(str).str.strip().isin(['','0','nan'])] \
        if 'Category' in rd.columns else pd.DataFrame()

    # 5. RNR stuck 7+ days
    rnr_stuck=rd[rd['FollowupStatus'].isin(RNR_S)&(rd.get('age_days',0)>=7)] \
        if 'age_days' in rd.columns else rd[rd['FollowupStatus'].isin(RNR_S)]

    # 6. 30+ day open
    old30=rd[rd.get('age_days',pd.Series(0,index=rd.index))>=30] \
        if 'age_days' in rd.columns else pd.DataFrame()

    c=st.columns(WIDS6)
    txt_cell(c[0],rep,bold=True,color='#0F2044')
    txt_cell(c[1],f'{len(rd):,}')
    num_btn(c[2],len(no_fu),  f"h_nofu_{rep}",  no_fu,   f"No followup date — {rep}")
    num_btn(c[3],len(overdue),f"h_over_{rep}",  overdue, f"Overdue followup — {rep}")
    num_btn(c[4],len(no_city),f"h_ncity_{rep}", no_city, f"No city — {rep}")
    num_btn(c[5],len(no_cat), f"h_ncat_{rep}",  no_cat,  f"No category — {rep}")
    num_btn(c[6],len(rnr_stuck),f"h_rnr_{rep}", rnr_stuck,f"RNR stuck 7+ days — {rep}")
    num_btn(c[7],len(old30),  f"h_old30_{rep}", old30,   f"30+ day open — {rep}")

tbl_sep()
tc6=st.columns(WIDS6)
no_fu_t  = open_all[open_all.get('FollowupDate_dt', open_all['FollowupDate'] if 'FollowupDate' in open_all.columns else open_all.index).isna()] if 'FollowupDate_dt' in open_all.columns or 'FollowupDate' in open_all.columns else pd.DataFrame()
txt_cell(tc6[0],'TOTAL',bold=True)
txt_cell(tc6[1],f'{len(open_all):,}',bold=True)
for i,v in enumerate([
    int(open_all['FollowupDate_dt'].isna().sum()) if 'FollowupDate_dt' in open_all.columns else '—',
    int(len(open_all[open_all['FollowupDate_dt']<TODAY]) if 'FollowupDate_dt' in open_all.columns else 0),
    int(open_all['City'].isna().sum()) if 'City' in open_all.columns else '—',
    int(open_all['Category'].isna().sum()) if 'Category' in open_all.columns else '—',
    int(len(open_all[open_all['FollowupStatus'].isin(RNR_S)&(open_all.get('age_days',0)>=7)])) if 'age_days' in open_all.columns else '—',
    int(len(open_all[open_all.get('age_days',pd.Series(0,index=open_all.index))>=30])) if 'age_days' in open_all.columns else '—',
], 2):
    txt_cell(tc6[i], f'{v:,}' if isinstance(v,int) else v, bold=True, color='#B91C1C' if isinstance(v,int) and v>0 else '#0F172A')

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{total:,} leads shown  |  Data as of {TODAY.strftime('%d %b %Y')}</p>",
    unsafe_allow_html=True)
