import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import date as date_type

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
section[data-testid="stSidebar"] .stDateInput input,
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="input"],
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="base-input"]{
    background:#162955 !important;border:1px solid #2D5F9E !important;
    border-radius:6px !important;color:white !important;}
.kpi{background:white;border-radius:10px;padding:14px;text-align:center;
     box-shadow:0 2px 6px rgba(0,0,0,0.07);border-top:3px solid #CBD5E1;height:80px;
     display:flex;flex-direction:column;justify-content:center;}
.kpi-l{font-size:10px;color:#64748B;font-weight:700;text-transform:uppercase;
       letter-spacing:.06em;margin-bottom:4px;}
.kpi-v{font-size:22px;font-weight:800;color:#0F2044;}
.kpi-v.g{color:#0A6640;}.kpi-v.r{color:#B91C1C;}
.kpi-v.a{color:#92400E;}.kpi-v.b{color:#1D4ED8;}
.drill-box{background:#EEF2FF;border:1px solid #C7D2FE;border-left:4px solid #0F2044;
           border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:12px;}
.sec{background:#0F2044;color:white !important;padding:9px 16px;border-radius:6px;
     font-weight:700;font-size:13px;margin:20px 0 8px;}
.note{font-size:11px;color:#64748B;font-style:italic;margin:0 0 8px;}
.col-hdr{font-size:11px;font-weight:700;color:#475569;
         border-bottom:2px solid #0F2044;padding-bottom:3px;margin-bottom:4px;}
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"]*{
    background:#1B3A6B !important;color:white !important;
    font-size:12px !important;font-weight:700 !important;}
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"]*{color:#0F172A !important;font-size:12px !important;}
[data-testid="stDataFrame"] [role="rowheader"],[data-testid="stDataFrame"] [role="rowheader"]*{
    color:#0F172A !important;font-size:12px !important;
    font-weight:600 !important;background:#F1F5F9 !important;}
</style>""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
WON_S         = ['Quoted Order Won And Executed']
LOST_FROM_Q   = ['Quoted Order Lost']
QUOTED_S      = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
                 'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold']
LOST_S        = ['Not-Interested','Not Search Our Product','Regret',
                 'Other Department Working','Wrong Number','No Response on RNR',
                 'Already Purchased','Quoted Order Lost',
                 'Repeat Lead','Rental Period Less Than 7 Days']
RNR_S         = ['Call Back','RNR Call Back']
ADMIN         = ['msafe947362','50988-Surbhi']
SRC_MAP       = {
    'Just Dial':'JustDial','Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SRC      = ['JustDial','IndiaMart','IVR Call','Existing Client','Ex-Client Ref.','Facebook','Other']
SRC_SHORT     = {'JustDial':'JD','IndiaMart':'IM','IVR Call':'IVR',
                 'Existing Client':'EC','Ex-Client Ref.':'ECR','Facebook':'FB','Other':'Oth'}
# TODAY is computed fresh each render as TODAY_NOW after filters are applied
BASE          = {'color':'#0F172A','font-size':'12px','font-weight':'500'}

WON_LABEL  = "Quoted Order Won And Executed"
LOST_LABEL = ("Not Interested · Not Search Our Product · Regret · Other Department Working · "
              "Wrong Number · No Response on RNR · Already Purchased · Quoted Order Lost · "
              "Repeat Lead · Rental Period Less Than 7 Days")
OPEN_LABEL = ("Call Back · RNR Call Back · Quoted In Follow Up · Quoted Order In Pipeline · "
              "Quote In Progress · Interested Quote Sent · Interested Catalogue Sent · "
              "Quoted Not Picking Call · Quoted Project On Hold · MS Requirement Call Back · "
              "and all remaining active stages")

LCOLS = {
    'LeadNo':'Lead #','PersonName':'Customer','CompanyName':'Company',
    'City':'City','Source':'Source','Category':'Category',
    'Rep':'Rep','FollowupStatus':'Status','Stage':'Stage',
    'CreatedOn':'Created','age_days':'Age (days)',
    'LastFollowupedOn':'Last Contact','Remarks':'Remarks',
}

# ── RAG HELPERS ────────────────────────────────────────────────────────────────
RAG = {0:'🔴', 1:'🟡', 2:'🟢'}
RAG_ORDER = {0:0, 1:1, 2:2}   # red first

def rag_win(wp):
    if wp < 2: return 0
    if wp < 5: return 1
    return 2

def rag_stale(pct_30):       # % of open leads that are 30+ days old
    if pct_30 > 40: return 0
    if pct_30 > 20: return 1
    return 2

def rag_hygiene(issue_pct):  # % of open leads with at least one issue
    if issue_pct > 50: return 0
    if issue_pct > 25: return 1
    return 2

def rag_quote_conv(pct):     # quote → win conversion %
    if pct < 15: return 0
    if pct < 30: return 1
    return 2

def rag_quoted_age(pct_30):  # % of quoted leads stuck 30+ days
    if pct_30 > 30: return 0
    if pct_30 > 15: return 1
    return 2

def rag_src(wp):
    if wp < 2: return 0
    if wp < 10: return 1
    return 2

# ── DATA LOAD ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading CRM data…")
def load(fb):
    df = pd.read_excel(BytesIO(fb), engine='openpyxl')
    df['Stage'] = df['FollowupStatus'].apply(
        lambda x:'Won' if x in WON_S else('Lost' if x in LOST_S else 'Open'))
    df['Source'] = df['SourceName'].replace(SRC_MAP)
    df['Source_group'] = df['Source'].apply(lambda x:x if x in MAIN_SRC else 'Other')
    df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)
    df['Rep'] = df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
    df.loc[df['is_admin'],'Rep'] = 'Admin'
    if 'CreatedOn' in df.columns:
        df['CreatedOn'] = pd.to_datetime(df['CreatedOn'], errors='coerce')
    if 'LastFollowupedOn' in df.columns:
        df['LastFollowupedOn'] = pd.to_datetime(df['LastFollowupedOn'], errors='coerce')
    if 'FollowupDate' in df.columns:
        df['FollowupDate_dt'] = pd.to_datetime(df['FollowupDate'], errors='coerce')
    if 'AmountPaid' in df.columns:
        df['AmountPaid'] = pd.to_numeric(df['AmountPaid'], errors='coerce').fillna(0)
    return df

def prep_leads(df):
    cols = [c for c in LCOLS if c in df.columns]
    out  = df[cols].copy(); out.columns=[LCOLS[c] for c in cols]
    if 'Created'      in out: out['Created']      = out['Created'].dt.strftime('%d %b %Y')
    if 'Last Contact' in out: out['Last Contact']  = out['Last Contact'].dt.strftime('%d %b %Y')
    return out

def show_drill():
    if st.session_state.drill_df is None: return
    df  = st.session_state.drill_df
    lbl = st.session_state.drill_label
    st.markdown(f"<div class='drill-box'><b style='color:#0F2044;'>📋 {lbl}</b> — {len(df):,} leads</div>",
                unsafe_allow_html=True)
    if len(df)==0: st.info("No leads."); return
    ld = prep_leads(df)
    sty = ld.style.set_properties(**BASE)
    if 'Stage' in ld.columns:
        sty = sty.map(lambda v:(
            'background:#E9F7EF;color:#0A6640;font-weight:700' if v=='Won'
            else('background:#FEF2F2;color:#B91C1C;font-weight:700' if v=='Lost'
                 else 'background:#FFFBEB;color:#92400E')),subset=['Stage'])
    st.dataframe(sty, use_container_width=True, height=360)
    st.download_button("⬇ Download CSV", ld.to_csv(index=False),
                       "leads.csv","text/csv",key="dl_drill")
    if st.button("✕ Close", key="close_d"):
        st.session_state.drill_df=None; st.rerun()

# ── LAYOUT HELPERS ─────────────────────────────────────────────────────────────
def hdrs(labels, widths):
    cols = st.columns(widths)
    for c,l in zip(cols,labels):
        c.markdown(f"<div class='col-hdr'>{l}</div>",unsafe_allow_html=True)

def sep():
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:2px 0;'>",
                unsafe_allow_html=True)

def txt(col, val, bold=False, color='#0F172A'):
    fw='700' if bold else '500'
    col.markdown(f"<div style='font-size:13px;font-weight:{fw};color:{color};"
                 f"padding:5px 0;'>{val}</div>",unsafe_allow_html=True)

def nbtn(col, val, key, df_, label, color='#0F172A'):
    if val==0:
        col.markdown("<div style='font-size:13px;color:#CBD5E1;padding:5px 0;'>—</div>",
                     unsafe_allow_html=True)
    elif col.button(f"{val:,}", key=key):
        drill(df_, label)

def rag_cell(col, score):
    col.markdown(f"<div style='font-size:18px;text-align:center;padding:3px 0;'>"
                 f"{RAG[score]}</div>",unsafe_allow_html=True)

def tot_row(cols_data, widths):
    """Render a totals row (grey background)."""
    sep()
    cs = st.columns(widths)
    for c,(val,bold,color) in zip(cs,cols_data):
        txt(c,val,bold,color)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])

if not uploaded:
    _,m,_=st.columns([1,2,1])
    with m:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;padding:48px 24px;background:white;"
            "border-radius:12px;border:1px solid #E2E8F0;'>"
            "<div style='font-size:52px;'>📂</div>"
            "<div style='font-size:22px;font-weight:800;color:#0F2044 !important;margin:14px 0 8px;'>"
            "MSafe Inside Sales Dashboard</div>"
            "<div style='font-size:14px;color:#64748B;'>"
            "Upload your KIT19 CRM export from the sidebar.<br>"
            "Works with single-month or multi-month data.</div>"
            "</div>",unsafe_allow_html=True)
    st.stop()

df_raw  = load(uploaded.read())
reps_df = df_raw[~df_raw['is_admin']].copy()

# Sidebar filters
st.sidebar.markdown("### Filters")

# ── DATE RANGE — two independent pickers, range from data ──────────────────
if 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any():
    _min = reps_df['CreatedOn'].min().date()
    _max = reps_df['CreatedOn'].max().date()
    st.sidebar.markdown("**Date Range (Lead Created On)**")
    date_from = st.sidebar.date_input("From", value=_min, key='dr_from')
    date_to   = st.sidebar.date_input("To",   value=_max, key='dr_to')
    use_dates = True
else:
    date_from = date_to = None
    use_dates = False

all_reps = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps = st.sidebar.multiselect("Rep", all_reps, default=all_reps)
all_src  = sorted(reps_df['Source'].dropna().unique().tolist())
sel_src  = st.sidebar.multiselect("Source", all_src, default=all_src)
sel_stg  = st.sidebar.multiselect("Stage", ['Open','Won','Lost'], default=['Open','Won','Lost'])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")
if use_dates:
    st.sidebar.markdown(f"**Showing:** {date_from.strftime('%d %b %Y')} → {date_to.strftime('%d %b %Y')}")

# ── Apply filters ─────────────────────────────────────────────────────────────
base = reps_df.copy()
# Date filter — purely driven by user's sidebar selection
if use_dates and 'CreatedOn' in base.columns:
    base = base[
        (base['CreatedOn'].dt.date >= date_from) &
        (base['CreatedOn'].dt.date <= date_to)
    ]
if sel_reps: base=base[base['Rep'].isin(sel_reps)]
if sel_src:  base=base[base['Source'].isin(sel_src)]
if sel_stg:  base=base[base['Stage'].isin(sel_stg)]

# ── Age calculations — done HERE (not in cache) so always uses today's date ───
TODAY_NOW = pd.Timestamp.now().normalize()
if 'CreatedOn' in base.columns:
    base = base.copy()
    base['age_days'] = (TODAY_NOW - base['CreatedOn']).dt.days.clip(lower=0)
if 'LastFollowupedOn' in base.columns:
    base['last_followup_age'] = (TODAY_NOW - base['LastFollowupedOn']).dt.days.clip(lower=0)

rep_order=(base.groupby('Rep')['Stage']
           .apply(lambda x:(x=='Won').sum())
           .sort_values(ascending=False).index.tolist())

total=len(base); won=int((base['Stage']=='Won').sum())
lost=int((base['Stage']=='Lost').sum()); opn=int((base['Stage']=='Open').sum())
wr=round(won/total*100,1) if total else 0

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='background:#0F2044;padding:16px 24px;border-radius:10px;"
    "margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;'>"
    "<span style='color:white !important;font-size:18px;font-weight:700;'>"
    "MSafe Equipments — Inside Sales Dashboard</span>"
    "<span style='color:#8BAFD4;font-size:12px;'>KIT19 CRM  |  Today: "
    f"{pd.Timestamp.now().strftime('%d %b %Y')}</span></div>",unsafe_allow_html=True)

kc=st.columns(6)
def kpi(col,l,v,cls=''):
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{l}</div>"
                 f"<div class='kpi-v {cls}'>{v}</div></div>",unsafe_allow_html=True)
kpi(kc[0],'Total Leads',f'{total:,}')
kpi(kc[1],'Won',f'{won:,}','g'); kpi(kc[2],'Open',f'{opn:,}','a')
kpi(kc[3],'Lost',f'{lost:,}','r'); kpi(kc[4],'Win Rate',f'{wr}%','b')
kpi(kc[5],'As of',pd.Timestamp.now().strftime('%d %b %Y'))

bk=st.columns(4)
for col,(lbl,df_) in zip(bk,[('All leads',base),('Won leads',base[base['Stage']=='Won']),
                              ('Open leads',base[base['Stage']=='Open']),
                              ('Lost leads',base[base['Stage']=='Lost'])]):
    if col.button(f"→ View {lbl} ({len(df_):,})",key=f"kpi_{lbl}"):
        drill(df_,lbl.capitalize())

st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:12px 0;'>",
            unsafe_allow_html=True)

# ── DRILL BOX ──────────────────────────────────────────────────────────────────
if st.session_state.drill_df is not None:
    show_drill()
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:12px 0;'>",
                unsafe_allow_html=True)
else:
    st.markdown(
        "<div style='background:#F1F5F9;border:1px dashed #CBD5E1;border-radius:8px;"
        "padding:12px 16px;color:#64748B;font-size:13px;margin-bottom:12px;'>"
        "👆  Click any number button below to see those specific leads here."
        "</div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 1 — REP PERFORMANCE  (sorted red → green by Win%)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 1 — Rep Performance  (🔴 Red = low Win%  →  🟢 Green = high Win%)</div>",
            unsafe_allow_html=True)
st.markdown(
    f"<p class='note'>"
    f"<b title='{WON_LABEL}'>Won ℹ</b> hover for stage list &nbsp;|&nbsp; "
    f"<b title='{OPEN_LABEL}'>Open ℹ</b> hover &nbsp;|&nbsp; "
    f"<b title='{LOST_LABEL}'>Lost ℹ</b> hover &nbsp;|&nbsp; "
    f"RAG: 🔴 Win% &lt;2%  🟡 2–5%  🟢 &gt;5% — sorted red to green</p>",
    unsafe_allow_html=True)

W1=[0.4,2,0.8,0.85,0.85,0.85,0.7,1.2]
hdrs(['','Rep','Total','Won','Open','Lost','Win%','View all'],W1)

# Build sorted list
rep_rag=[]
for rep in rep_order:
    rd=base[base['Rep']==rep]
    nw=int((rd['Stage']=='Won').sum()); nt=len(rd)
    wp=round(nw/nt*100,1) if nt else 0
    rep_rag.append((rep,rd,nt,nw,wp,rag_win(wp)))
rep_rag.sort(key=lambda x:x[5])   # red=0 first

for rep,rd,nt,nw,wp,rs in rep_rag:
    ro=rd[rd['Stage']=='Open']; rl=rd[rd['Stage']=='Lost']; rw=rd[rd['Stage']=='Won']
    wpc='#0A6640' if rs==2 else('#92400E' if rs==1 else '#B91C1C')
    c=st.columns(W1)
    rag_cell(c[0],rs)
    txt(c[1],rep,bold=True,color='#0F2044')
    txt(c[2],f'{nt:,}')
    nbtn(c[3],len(rw),f"t1w_{rep}",rw,f"Won — {rep}")
    nbtn(c[4],len(ro),f"t1o_{rep}",ro,f"Open — {rep}")
    nbtn(c[5],len(rl),f"t1l_{rep}",rl,f"Lost — {rep}")
    txt(c[6],f"{wp}%",bold=True,color=wpc)
    if c[7].button(f"→ All {nt:,}",key=f"t1a_{rep}"):
        drill(rd,f"All leads — {rep}")

sep()
tc=st.columns(W1); txt(tc[0],''); txt(tc[1],'TOTAL',True)
txt(tc[2],f'{total:,}',True)
txt(tc[3],f'{won:,}',True,'#0A6640')
txt(tc[4],f'{opn:,}',True,'#92400E')
txt(tc[5],f'{lost:,}',True,'#B91C1C')
txt(tc[6],f'{wr}%',True,'#1D4ED8')

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 2 — REP × SOURCE  (wide, Won/Open/Lost per source)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 2 — Rep Performance by Source (Won | Open | Lost per Source)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>Each source = 3 columns: Won | Open | Lost. "
            "Row + column totals. Use the drill selector below the table to click into any cell.</p>",
            unsafe_allow_html=True)

src_avail=[s for s in MAIN_SRC if base[base['Source_group']==s].shape[0]>0]
rows2=[]
for rep,rd,nt,nw,wp,rs in rep_rag:
    row={'RAG':RAG[rs],'Rep':rep}
    for src in src_avail:
        sh=SRC_SHORT.get(src,src[:3]); sd=rd[rd['Source_group']==src]
        row[f'{sh}-W']=int((sd['Stage']=='Won').sum())
        row[f'{sh}-O']=int((sd['Stage']=='Open').sum())
        row[f'{sh}-L']=int((sd['Stage']=='Lost').sum())
    row['Tot-W']=nw; row['Tot-O']=int((rd['Stage']=='Open').sum())
    row['Tot-L']=int((rd['Stage']=='Lost').sum())
    rows2.append(row)
tot2={'RAG':'','Rep':'TOTAL'}
for src in src_avail:
    sh=SRC_SHORT.get(src,src[:3]); sd=base[base['Source_group']==src]
    tot2[f'{sh}-W']=int((sd['Stage']=='Won').sum())
    tot2[f'{sh}-O']=int((sd['Stage']=='Open').sum())
    tot2[f'{sh}-L']=int((sd['Stage']=='Lost').sum())
tot2['Tot-W']=won; tot2['Tot-O']=opn; tot2['Tot-L']=lost
rows2.append(tot2)
df2=pd.DataFrame(rows2).set_index('Rep')

def sty_t2(df):
    s=pd.DataFrame('',index=df.index,columns=df.columns)
    for col in df.columns:
        if col.endswith('-W'):
            s[col]=df[col].apply(lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                                  if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif col.endswith('-L'):
            s[col]=df[col].apply(lambda v:'background:#FEF2F2;color:#B91C1C'
                                  if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif col.endswith('-O'):
            s[col]=df[col].apply(lambda v:'background:#FFFBEB;color:#92400E'
                                  if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        elif 'Tot' in col:
            s[col]='background:#EAF0FB;color:#0F2044;font-weight:700'
    if 'TOTAL' in df.index:
        s.loc['TOTAL']='background:#0F2044;color:white;font-weight:800'
    return s

st.dataframe(
    df2.style.set_properties(**BASE).apply(sty_t2,axis=None)
       .format(lambda x:'—' if isinstance(x,(int,float)) and x==0
               else(f'{x:,}' if isinstance(x,(int,float)) else x)),
    use_container_width=True, height=460)

d1,d2,d3,d4=st.columns([2,2,2,1.2])
d_rep=d1.selectbox("Rep",['All']+[r for r,*_ in rep_rag],key='t2_rep')
d_src=d2.selectbox("Source",['All']+src_avail,key='t2_src')
d_stg=d3.selectbox("Stage",['All','Won','Open','Lost'],key='t2_stg')
if d4.button("→ View leads",key='t2_drill'):
    fd=base.copy()
    if d_rep!='All': fd=fd[fd['Rep']==d_rep]
    if d_src!='All': fd=fd[fd['Source_group']==d_src]
    if d_stg!='All': fd=fd[fd['Stage']==d_stg]
    drill(fd,f"{d_stg} — {d_rep} | {d_src}")

st.download_button("⬇ Download Table 2",df2.to_csv(),"rep_source.csv","text/csv",key="dl2")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 3 — SOURCE PERFORMANCE  (sorted red → green)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 3 — Source Performance  (🔴 low Win%  →  🟢 high Win%)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>RAG: 🔴 &lt;2%  🟡 2–10%  🟢 &gt;10%. Sorted red to green.</p>",
            unsafe_allow_html=True)

W3=[0.4,2,0.8,0.85,0.85,0.85,0.7,1.2]
hdrs(['','Source','Total','Won','Open','Lost','Win%','View all'],W3)

src_stats=[]
for src in src_avail:
    sd=base[base['Source_group']==src]
    nw=int((sd['Stage']=='Won').sum()); nt=len(sd)
    wp=round(nw/nt*100,1) if nt else 0
    src_stats.append((src,sd,nt,nw,wp,rag_src(wp)))
src_stats.sort(key=lambda x:x[5])

for src,sd,nt,nw,wp,rs in src_stats:
    so=sd[sd['Stage']=='Open']; sl=sd[sd['Stage']=='Lost']; sw=sd[sd['Stage']=='Won']
    wpc='#0A6640' if rs==2 else('#92400E' if rs==1 else '#B91C1C')
    c=st.columns(W3)
    rag_cell(c[0],rs); txt(c[1],src,bold=True,color='#0F2044')
    txt(c[2],f'{nt:,}')
    nbtn(c[3],len(sw),f"t3w_{src}",sw,f"Won — {src}")
    nbtn(c[4],len(so),f"t3o_{src}",so,f"Open — {src}")
    nbtn(c[5],len(sl),f"t3l_{src}",sl,f"Lost — {src}")
    txt(c[6],f"{wp}%",bold=True,color=wpc)
    if c[7].button(f"→ All {nt:,}",key=f"t3a_{src}"):
        drill(sd,f"All leads — {src}")

sep()
tc3=st.columns(W3); txt(tc3[0],''); txt(tc3[1],'TOTAL',True)
txt(tc3[2],f'{total:,}',True)
txt(tc3[3],f'{won:,}',True,'#0A6640')
txt(tc3[4],f'{opn:,}',True,'#92400E')
txt(tc3[5],f'{lost:,}',True,'#B91C1C')
txt(tc3[6],f'{wr}%',True,'#1D4ED8')

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 4 — AMOUNT PAID
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 4 — Amount Paid (₹)</div>",unsafe_allow_html=True)
st.markdown("<p class='note'>Based on AmountPaid field. Only leads with amount &gt; 0 shown.</p>",
            unsafe_allow_html=True)

if 'AmountPaid' in base.columns:
    W4=[2.2,0.9,1.4,1.5,1.3,1.3]
    hdrs(['Rep','With Amount','Total ₹','Avg ₹','Max ₹','View'],W4)
    for rep,rd,nt,nw,wp,rs in rep_rag:
        paid=rd[rd['AmountPaid']>0]
        ta=paid['AmountPaid'].sum(); av=paid['AmountPaid'].mean() if len(paid) else 0
        mx=paid['AmountPaid'].max() if len(paid) else 0
        c=st.columns(W4)
        txt(c[0],rep,True,'#0F2044')
        nbtn(c[1],len(paid),f"t4n_{rep}",paid,f"Leads with amount — {rep}")
        txt(c[2],f'₹{ta:,.0f}' if ta>0 else '—',bold=ta>0,color='#0A6640' if ta>0 else '#CBD5E1')
        txt(c[3],f'₹{av:,.0f}' if av>0 else '—')
        txt(c[4],f'₹{mx:,.0f}' if mx>0 else '—')
        if c[5].button("→ View",key=f"t4v_{rep}"):
            drill(rd,f"All leads — {rep}")
    sep()
    ap=base[base['AmountPaid']>0]; tc4=st.columns(W4)
    txt(tc4[0],'TOTAL',True)
    nbtn(tc4[1],len(ap),'t4_tot',ap,"All leads with amount paid")
    txt(tc4[2],f'₹{ap["AmountPaid"].sum():,.0f}',True,'#0A6640')
    txt(tc4[3],f'₹{ap["AmountPaid"].mean():,.0f}' if len(ap) else '—')
    txt(tc4[4],f'₹{ap["AmountPaid"].max():,.0f}' if len(ap) else '—')
else:
    st.info("AmountPaid column not found in this export.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 5 — STALE OPEN LEADS  (sorted red → green by % stale)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 5 — Stale Open Leads  (🔴 many stale  →  🟢 fresh pipeline)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>Open leads bucketed by age since created date. "
            "RAG: 🔴 &gt;40% in 30+ days  🟡 20–40%  🟢 &lt;20%. Sorted red to green.</p>",
            unsafe_allow_html=True)

if 'age_days' in base.columns:
    def abkt(d):
        if pd.isna(d) or d<0: return '0–7d'
        if d<=7: return '0–7d'
        if d<=15: return '8–15d'
        if d<=30: return '16–30d'
        return '30+d'
    BKTS=['0–7d','8–15d','16–30d','30+d']
    BKT_C={'0–7d':'#0A6640','8–15d':'#92400E','16–30d':'#B45309','30+d':'#B91C1C'}
    ob=base[base['Stage']=='Open'].copy(); ob['bkt']=ob['age_days'].apply(abkt)
    W5=[0.4,2,0.9,0.9,1,1,0.9,1.2]
    hdrs(['','Rep','Open','0–7 days','8–15 days','16–30 days','30+ days','View all'],W5)

    st5=[]
    for rep,rd,nt,nw,wp,_ in rep_rag:
        rdo=ob[ob['Rep']==rep]; no=len(rdo)
        if no==0: continue
        old=int((rdo['bkt']=='30+d').sum())
        pct_old=round(old/no*100,1) if no else 0
        st5.append((rep,rdo,no,pct_old,rag_stale(pct_old)))
    st5.sort(key=lambda x:x[4])

    for rep,rdo,no,pct_old,rs in st5:
        c=st.columns(W5); rag_cell(c[0],rs)
        txt(c[1],rep,True,'#0F2044'); txt(c[2],f'{no:,}')
        for i,bkt in enumerate(BKTS,3):
            bd=rdo[rdo['bkt']==bkt]
            nbtn(c[i],len(bd),f"t5_{rep}_{bkt}",bd,f"{bkt} open — {rep}",BKT_C[bkt])
        if c[7].button(f"→ All {no}",key=f"t5a_{rep}"):
            drill(rdo,f"All open leads — {rep}")

    sep()
    tc5=st.columns(W5); txt(tc5[0],''); txt(tc5[1],'TOTAL',True)
    txt(tc5[2],f'{len(ob):,}',True)
    for i,bkt in enumerate(BKTS,3):
        bd=ob[ob['bkt']==bkt]
        txt(tc5[i],f'{len(bd):,}',True,BKT_C[bkt])
else:
    st.warning("CreatedOn date not available — cannot calculate aging.")

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 6 — CRM HYGIENE  (sorted red → green)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 6 — CRM Hygiene  (daily report — share with team)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "Open leads only. RAG based on total issues as % of open leads. "
            "🔴 &gt;50% issues  🟡 25–50%  🟢 &lt;25%. Sorted red to green. Click any number.</p>",
            unsafe_allow_html=True)

W6=[0.4,2,0.9,1.1,1.2,1,1.1,1.1,1.1]
hdrs(['','Rep','Open','No Followup\nDate','Overdue\nFollowup',
      'No City','No Category','RNR Stuck\n7+ Days','30+ Day\nOpen'],W6)

oa=base[base['Stage']=='Open'].copy()
hyg_rows=[]
for rep,rd,nt,nw,wp,_ in rep_rag:
    rdo=oa[oa['Rep']==rep]; no=len(rdo)
    if no==0: continue
    no_fu  = rdo[rdo['FollowupDate_dt'].isna()] if 'FollowupDate_dt' in rdo.columns else pd.DataFrame()
    overdue= rdo[rdo['FollowupDate_dt'].notna()&(rdo['FollowupDate_dt']<TODAY_NOW)] \
             if 'FollowupDate_dt' in rdo.columns else pd.DataFrame()
    no_city= rdo[rdo['City'].isna()|rdo['City'].astype(str).str.strip().isin(['','0','nan'])] \
             if 'City' in rdo.columns else pd.DataFrame()
    no_cat = rdo[rdo['Category'].isna()|rdo['Category'].astype(str).str.strip().isin(['','0','nan'])] \
             if 'Category' in rdo.columns else pd.DataFrame()
    rnr_st = rdo[rdo['FollowupStatus'].isin(RNR_S)&(rdo.get('last_followup_age',0)>=7)] \
             if 'last_followup_age' in rdo.columns else rdo[rdo['FollowupStatus'].isin(RNR_S)]
    old30  = rdo[rdo['age_days']>=30] if 'age_days' in rdo.columns else pd.DataFrame()
    tot_issues=max(len(no_fu),len(overdue))+len(no_city)+len(no_cat)+len(rnr_st)+len(old30)
    iss_pct=round(tot_issues/no*100,1) if no else 0
    hyg_rows.append((rep,rdo,no,no_fu,overdue,no_city,no_cat,rnr_st,old30,rag_hygiene(iss_pct)))

hyg_rows.sort(key=lambda x:x[9])
for rep,rdo,no,no_fu,overdue,no_city,no_cat,rnr_st,old30,rs in hyg_rows:
    c=st.columns(W6); rag_cell(c[0],rs)
    txt(c[1],rep,True,'#0F2044'); txt(c[2],f'{no:,}')
    nbtn(c[3],len(no_fu),   f"h_fu_{rep}",  no_fu,   f"No followup date — {rep}")
    nbtn(c[4],len(overdue), f"h_ov_{rep}",  overdue, f"Overdue followup — {rep}")
    nbtn(c[5],len(no_city), f"h_cy_{rep}",  no_city, f"No city — {rep}")
    nbtn(c[6],len(no_cat),  f"h_ct_{rep}",  no_cat,  f"No category — {rep}")
    nbtn(c[7],len(rnr_st),  f"h_rn_{rep}",  rnr_st,  f"RNR stuck 7+ days — {rep}")
    nbtn(c[8],len(old30),   f"h_o30_{rep}", old30,   f"30+ day open — {rep}")

sep()
tc6=st.columns(W6); txt(tc6[0],''); txt(tc6[1],'TOTAL',True); txt(tc6[2],f'{len(oa):,}',True)
cols6_totals=[
    int(oa['FollowupDate_dt'].isna().sum()) if 'FollowupDate_dt' in oa.columns else 0,
    int(len(oa[oa['FollowupDate_dt']<TODAY_NOW])) if 'FollowupDate_dt' in oa.columns else 0,
    int(oa['City'].isna().sum()) if 'City' in oa.columns else 0,
    int(oa['Category'].isna().sum()) if 'Category' in oa.columns else 0,
    int(len(oa[oa['FollowupStatus'].isin(RNR_S)&(oa.get('last_followup_age',pd.Series(0,index=oa.index))>=7)])) if 'last_followup_age' in oa.columns else 0,
    int(len(oa[oa.get('age_days',pd.Series(0,index=oa.index))>=30])) if 'age_days' in oa.columns else 0,
]
for i,v in enumerate(cols6_totals,3):
    txt(tc6[i],f'{v:,}',True,'#B91C1C' if v>0 else '#0F172A')

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 7 — QUOTED PIPELINE  (New to Quoted analysis)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 7 — Quoted Pipeline Analysis  (🔴 low conversion  →  🟢 high conversion)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "All leads that reached a quoted stage. Shows still in quoted, won from quote, "
            "lost from quote, and quote→win conversion %. "
            "RAG: 🔴 &lt;15% quote→win  🟡 15–30%  🟢 &gt;30%. Sorted red to green.</p>",
            unsafe_allow_html=True)

ALL_QUOTED_S = QUOTED_S + WON_S + LOST_FROM_Q
W7=[0.4,2,1,1.1,1,1,1.1,1.2]
hdrs(['','Rep','Reached\nQuoted','In Quoted\n(Pending)','Won from\nQuote','Lost from\nQuote',
      'Quote→Win%','View all quoted'],W7)

qt7=[]
for rep,rd,nt,nw,wp,_ in rep_rag:
    q_all= rd[rd['FollowupStatus'].isin(ALL_QUOTED_S)]
    q_cur= rd[rd['FollowupStatus'].isin(QUOTED_S)]
    q_won= rd[rd['FollowupStatus'].isin(WON_S)]
    q_lst= rd[rd['FollowupStatus'].isin(LOST_FROM_Q)]
    nqa=len(q_all); nqw=len(q_won); nql=len(q_lst)
    qconv=round(nqw/(nqw+nql)*100,1) if (nqw+nql)>0 else 0
    rs=rag_quote_conv(qconv) if nqa>0 else 1
    qt7.append((rep,rd,q_all,q_cur,q_won,q_lst,nqa,nqw,nql,qconv,rs))

qt7.sort(key=lambda x:x[10])
for rep,rd,q_all,q_cur,q_won,q_lst,nqa,nqw,nql,qconv,rs in qt7:
    if nqa==0: continue
    wpc='#0A6640' if rs==2 else('#92400E' if rs==1 else '#B91C1C')
    c=st.columns(W7); rag_cell(c[0],rs)
    txt(c[1],rep,True,'#0F2044')
    nbtn(c[2],nqa,       f"t7a_{rep}", q_all, f"All quoted leads — {rep}")
    nbtn(c[3],len(q_cur),f"t7c_{rep}", q_cur, f"Currently in quoted — {rep}")
    nbtn(c[4],nqw,       f"t7w_{rep}", q_won, f"Won from quote — {rep}")
    nbtn(c[5],nql,       f"t7l_{rep}", q_lst, f"Lost from quote — {rep}")
    txt(c[6],f"{qconv}%",True,wpc)
    if c[7].button(f"→ All {nqa}",key=f"t7all_{rep}"):
        drill(q_all,f"All quoted pipeline — {rep}")

sep()
qa_tot=base[base['FollowupStatus'].isin(ALL_QUOTED_S)]
qc_tot=base[base['FollowupStatus'].isin(QUOTED_S)]
qw_tot=base[base['FollowupStatus'].isin(WON_S)]
ql_tot=base[base['FollowupStatus'].isin(LOST_FROM_Q)]
qconv_tot=round(len(qw_tot)/(len(qw_tot)+len(ql_tot))*100,1) if (len(qw_tot)+len(ql_tot))>0 else 0
tc7=st.columns(W7); txt(tc7[0],''); txt(tc7[1],'TOTAL',True)
txt(tc7[2],f'{len(qa_tot):,}',True)
txt(tc7[3],f'{len(qc_tot):,}',True,'#92400E')
txt(tc7[4],f'{len(qw_tot):,}',True,'#0A6640')
txt(tc7[5],f'{len(ql_tot):,}',True,'#B91C1C')
txt(tc7[6],f'{qconv_tot}%',True,'#1D4ED8')

# ════════════════════════════════════════════════════════════════════════════════
# TABLE 8 — QUOTED STAGE AGING  (age = TODAY - LastFollowupedOn)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 8 — Quoted Stage Aging  (how long leads have been in quoted stage)</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>"
            "Only leads currently sitting in a quoted stage. "
            "Age = days since last status update (LastFollowupedOn). "
            "RAG: 🔴 &gt;30% stuck 30+ days  🟡 15–30%  🟢 &lt;15%. Sorted red to green.</p>",
            unsafe_allow_html=True)

qcur_all=base[base['FollowupStatus'].isin(QUOTED_S)].copy()

if 'last_followup_age' in qcur_all.columns:
    def qbkt(d):
        if pd.isna(d) or d<0: return '0–7d'
        if d<=7:  return '0–7d'
        if d<=15: return '8–15d'
        if d<=30: return '16–30d'
        return '30+d'
    QBKTS=['0–7d','8–15d','16–30d','30+d']
    QBKT_C={'0–7d':'#0A6640','8–15d':'#92400E','16–30d':'#B45309','30+d':'#B91C1C'}
    qcur_all['qbkt']=qcur_all['last_followup_age'].apply(qbkt)

    W8=[0.4,2,0.9,1,1,1,1,1.2]
    hdrs(['','Rep','In Quoted','0–7 days','8–15 days','16–30 days','30+ days','View all'],W8)

    qt8=[]
    for rep,rd,nt,nw,wp,_ in rep_rag:
        rq=qcur_all[qcur_all['Rep']==rep]; nq=len(rq)
        if nq==0: continue
        old=int((rq['qbkt']=='30+d').sum())
        pct_old=round(old/nq*100,1) if nq else 0
        qt8.append((rep,rq,nq,pct_old,rag_quoted_age(pct_old)))
    qt8.sort(key=lambda x:x[4])

    for rep,rq,nq,pct_old,rs in qt8:
        c=st.columns(W8); rag_cell(c[0],rs)
        txt(c[1],rep,True,'#0F2044'); txt(c[2],f'{nq:,}')
        for i,bkt in enumerate(QBKTS,3):
            bd=rq[rq['qbkt']==bkt]
            nbtn(c[i],len(bd),f"t8_{rep}_{bkt}",bd,f"Quoted {bkt} — {rep}",QBKT_C[bkt])
        if c[7].button(f"→ All {nq}",key=f"t8a_{rep}"):
            drill(rq,f"All quoted (pending) — {rep}")

    sep()
    tc8=st.columns(W8); txt(tc8[0],''); txt(tc8[1],'TOTAL',True)
    txt(tc8[2],f'{len(qcur_all):,}',True)
    for i,bkt in enumerate(QBKTS,3):
        bd=qcur_all[qcur_all['qbkt']==bkt]
        txt(tc8[i],f'{len(bd):,}',True,QBKT_C[bkt])
else:
    st.warning("LastFollowupedOn date not available — cannot calculate quoted stage aging.")
    # Fallback: show count only
    W8f=[0.4,2,1,1.2]
    hdrs(['','Rep','In Quoted Stage','View'],W8f)
    for rep,rd,nt,nw,wp,rs in rep_rag:
        rq=base[(base['Rep']==rep)&(base['FollowupStatus'].isin(QUOTED_S))]
        if len(rq)==0: continue
        c=st.columns(W8f); rag_cell(c[0],rs)
        txt(c[1],rep,True,'#0F2044'); txt(c[2],f'{len(rq):,}')
        if c[3].button(f"→ View {len(rq)}",key=f"t8fb_{rep}"):
            drill(rq,f"Quoted stage — {rep}")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{total:,} leads in current filter  |  Dashboard date: {pd.Timestamp.now().strftime('%d %b %Y')}</p>",
    unsafe_allow_html=True)
