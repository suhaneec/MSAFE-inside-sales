import streamlit as st
import pandas as pd
import numpy as np
import io as _io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="MSafe CRM Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k, v in [('drill_df', None), ('drill_label', ''),
             ('exp_won', False), ('exp_act', False), ('exp_lost', False),
             ('applied_filters', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

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

/* ── SIDEBAR ── */
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
section[data-testid="stSidebar"] .stTextInput input{
    background:#162955 !important;border:1px solid #2D5F9E !important;
    border-radius:6px !important;color:white !important;}
section[data-testid="stSidebar"] .stTextInput input::placeholder{color:#8BAFD4 !important;opacity:1 !important;}
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]{
    background:white !important;color:#0F172A !important;border:1px solid #CBD5E1 !important;}
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] *{
    color:#0F172A !important;}

/* ── KPI CARDS ── */
.kpi{background:white;border-radius:10px;padding:14px 14px;text-align:center;
     box-shadow:0 2px 6px rgba(0,0,0,0.07);border-top:3px solid #CBD5E1;
     display:flex;flex-direction:column;justify-content:center;cursor:pointer;min-height:64px;}
.kpi:hover{box-shadow:0 4px 12px rgba(15,32,68,0.15);border-top-color:#0F2044;}
.kpi-l{font-size:11.5px;color:#64748B !important;font-weight:700;text-transform:uppercase;
       letter-spacing:.05em;margin-bottom:5px;}
.kpi-v{font-size:29px;font-weight:800;color:#0F2044 !important;}
.kpi-v.g{color:#0A6640 !important;}.kpi-v.r{color:#B91C1C !important;}
.kpi-v.a{color:#92400E !important;}.kpi-v.b{color:#1D4ED8 !important;}

/* ── DRILL BOX ── */
.drill-box{background:#EEF2FF;border:1px solid #C7D2FE;border-left:4px solid #0F2044;
           border-radius:0 8px 8px 0;padding:10px 16px;margin-bottom:10px;font-size:13px;}

/* ── TABLE SECTION HEADERS ── */
.sec{background:#0F2044;padding:10px 16px;border-radius:6px;
     font-weight:700;font-size:16px;margin:18px 0 4px;letter-spacing:.01em;}
.sec, .sec *{color:white !important;}

/* ── TABLE NOTES ── */
.note{font-size:12.5px;color:#64748B;font-style:italic;margin:0 0 8px;line-height:1.5;}

/* ── TABLE COLUMN HEADERS — bigger, never truncated, allowed to wrap ── */
.col-hdr{font-size:14.5px;font-weight:800;color:#334155;
         border-bottom:2px solid #0F2044;padding:0 2px 6px 0;margin-bottom:6px;
         white-space:normal;line-height:1.2;word-break:break-word;
         min-height:24px;display:flex;align-items:flex-end;}
.grp-hdr-won{font-size:15px;font-weight:800;color:#0A6640;
             border-bottom:3px solid #0A6640;padding:0 0 6px 0;margin-bottom:6px;
             min-height:24px;display:flex;align-items:flex-end;justify-content:center;text-align:center;}
.grp-hdr-act{font-size:15px;font-weight:800;color:#92400E;
             border-bottom:3px solid #F59E0B;padding:0 0 6px 0;margin-bottom:6px;
             min-height:24px;display:flex;align-items:flex-end;justify-content:center;text-align:center;}
.grp-hdr-lost{font-size:15px;font-weight:800;color:#B91C1C;
              border-bottom:3px solid #B91C1C;padding:0 0 6px 0;margin-bottom:6px;
              min-height:24px;display:flex;align-items:flex-end;justify-content:center;text-align:center;}

/* ── ROTATED SUB-STAGE HEADERS — full name always visible, bigger ── */
.sub-hdr{font-size:13px;font-weight:700;color:#334155;
         writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;
         height:150px;display:flex;align-items:flex-end;justify-content:center;
         padding-bottom:6px;margin-bottom:5px;border-bottom:2px solid #CBD5E1;}
.sub-hdr-won{border-bottom:3px solid #0A6640;color:#0A6640;}
.sub-hdr-act{border-bottom:3px solid #F59E0B;color:#92400E;}
.sub-hdr-lost{border-bottom:3px solid #B91C1C;color:#B91C1C;}
.amt-hdr{font-size:15px;font-weight:800;color:#1D4ED8;
         border-bottom:3px solid #1D4ED8;padding:0 0 6px 0;margin-bottom:6px;
         min-height:24px;display:flex;align-items:flex-end;justify-content:center;text-align:center;}

/* ── RAG PILLS (used for Win% / conversion cells) ── */
.pill{display:inline-block;font-size:17px;font-weight:800;border-radius:8px;
      padding:6px 12px;line-height:1.3;border:1.5px solid transparent;}
.pill-g{background:#E9F7EF;color:#0A6640 !important;border-color:#86D6AE;}
.pill-a{background:#FFFBEB;color:#92400E !important;border-color:#FBD38D;}
.pill-r{background:#FEF2F2;color:#B91C1C !important;border-color:#FCA5A5;}

/* ── RAG BADGE (leftmost traffic-light column) ── */
.rag-badge{display:inline-flex;align-items:center;justify-content:center;
    width:30px;height:30px;border-radius:8px;font-size:16px;margin:0 auto;}
.rag-badge-0{background:#FEF2F2;border:1.5px solid #FCA5A5;}
.rag-badge-1{background:#FFFBEB;border:1.5px solid #FBD38D;}
.rag-badge-2{background:#E9F7EF;border:1.5px solid #86D6AE;}

/* ── COLORED VALUE BOXES (pivot number cells) ──
   A zero-height marker div is placed immediately before the st.button;
   CSS uses the adjacent-sibling combinator to skin that button. ── */
.box-mark{height:0;margin:0;padding:0;line-height:0;font-size:0;}
.box-mark-won + div[data-testid="stButton"] button{
    background:#E9F7EF !important;color:#0A6640 !important;
    border:1.5px solid #86D6AE !important;font-weight:800 !important;
    font-size:16px !important;border-radius:8px !important;}
.box-mark-act + div[data-testid="stButton"] button{
    background:#FFFBEB !important;color:#92400E !important;
    border:1.5px solid #FBD38D !important;font-weight:800 !important;
    font-size:16px !important;border-radius:8px !important;}
.box-mark-lost + div[data-testid="stButton"] button{
    background:#FEF2F2 !important;color:#B91C1C !important;
    border:1.5px solid #FCA5A5 !important;font-weight:800 !important;
    font-size:16px !important;border-radius:8px !important;}
.box-mark-neutral + div[data-testid="stButton"] button{
    background:#F1F5F9 !important;color:#0F2044 !important;
    border:1.5px solid #CBD5E1 !important;font-weight:800 !important;
    font-size:16px !important;border-radius:8px !important;}
.box-mark-amt + div[data-testid="stButton"] button{
    background:#EFF6FF !important;color:#1D4ED8 !important;
    border:1.5px solid #93C5FD !important;font-weight:800 !important;
    font-size:16px !important;border-radius:8px !important;}
.box-mark-won + div[data-testid="stButton"] button:hover{border-color:#0A6640 !important;}
.box-mark-act + div[data-testid="stButton"] button:hover{border-color:#92400E !important;}
.box-mark-lost + div[data-testid="stButton"] button:hover{border-color:#B91C1C !important;}
.box-mark-neutral + div[data-testid="stButton"] button:hover{border-color:#0F2044 !important;}
.box-mark-amt + div[data-testid="stButton"] button:hover{border-color:#1D4ED8 !important;}

/* ── EMPTY / ZERO CELL BOX — keeps grid alignment when there's no button ── */
.empty-box{display:flex;align-items:center;justify-content:center;
    font-size:15px;font-weight:700;color:#CBD5E1 !important;background:#F8FAFC;
    border:1.5px dashed #E2E8F0;border-radius:8px;padding:5px 0;min-height:30px;}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"]*{
    background:#1B3A6B !important;color:white !important;
    font-size:13px !important;font-weight:700 !important;}
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"]*{color:#0F172A !important;font-size:13px !important;}
[data-testid="stDataFrame"] [role="rowheader"],[data-testid="stDataFrame"] [role="rowheader"]*{
    color:#0F172A !important;font-size:13px !important;
    font-weight:600 !important;background:#F1F5F9 !important;}

/* ── TABLE BUTTONS (numbers) — bigger, still tappable ── */
button[data-testid="baseButton-secondary"]{
    padding:2px 6px !important;font-size:15px !important;font-weight:700 !important;
    min-height:28px !important;line-height:1.3 !important;}

/* ── TABS ── */
button[data-baseweb="tab"]{font-size:15px !important;font-weight:700 !important;
    color:#0F2044 !important;}
button[data-baseweb="tab"] p{font-size:15px !important;font-weight:700 !important;}
[data-baseweb="tab-highlight"]{background-color:#0F2044 !important;}
[data-baseweb="tab-border"]{background-color:#E2E8F0 !important;}

/* ── BLOCK SPACING — compact but breathable ── */
.block-container{padding-top:0.6rem !important;padding-bottom:1rem !important;
    padding-left:1.2rem !important;padding-right:1.2rem !important;}
div[data-testid="stVerticalBlock"]{gap:0px !important;}
div[data-testid="stVerticalBlockBorderWrapper"]{padding:0px !important;}
div[data-testid="column"]{padding:0px 5px !important;}
div[data-testid="stVerticalBlock"] > div{gap:0px !important;margin:0px !important;}
div.element-container{margin:0px !important;padding:0px !important;}
div[data-testid="stMarkdownContainer"]{margin:0px !important;padding:0px !important;}
div[data-testid="stButton"]{margin:0px !important;padding:1px 0 !important;}
div[data-testid="stHorizontalBlock"]{gap:6px !important;margin:0px !important;}
div.stButton > button[data-testid="baseButton-secondary"]{
    margin-top:2px !important;margin-bottom:0px !important;
    height:24px !important;font-size:12.5px !important;}
</style>""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
WON_S    = ['Quoted Order Won And Executed']
LOST_S   = ['Not-Interested','Not Search Our Product','Regret',
            'Other Department Working','Wrong Number','No Response on RNR',
            'Already Purchased','Quoted Order Lost',
            'Repeat Lead','Rental Period Less Than 7 Days']
QUOTED_S = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
            'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold']
QUOTATION_S = QUOTED_S + WON_S + ['Quoted Order Lost']
WON_ORDER  = ['Quoted Order Won And Executed']
ACT_ORDER  = ['Call Back','RNR Call Back','MS Requirement Call Back',
              'Interested Catalogue Sent','Interested Quote Sent',
              'Quote In Progress','Quoted Not Picking Call',
              'Quoted In Follow Up','Quoted Order In Pipeline',
              'Quoted Project On Hold','Open']
LOST_ORDER = ['Not-Interested','Not Search Our Product','Regret',
              'Other Department Working','Wrong Number','No Response on RNR',
              'Already Purchased','Quoted Order Lost',
              'Repeat Lead','Rental Period Less Than 7 Days']
ADMIN    = ['msafe947362','50988-Surbhi']
SRC_MAP  = {
    'Just Dial':'JustDial','Justdial':'JustDial','Justdial (Justdial)':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'SEO','SEO':'SEO',
    'Google Ads':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'TradeIndia':'TradeIndia',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SRC = ['JustDial','IndiaMart','IVR Call','TradeIndia','Google Ads','SEO',
            'Existing Client','Ex-Client Ref.','Facebook','Other']
LCOLS    = {'LeadNo':'Lead #','PersonName':'Customer','CompanyName':'Company',
            'City':'City','Source':'Source','Category':'Category','Rep':'Rep',
            'FollowupStatus':'Status','Stage':'Stage','CreatedOn':'Created',
            'age_days':'Lead Age (days)','last_fu_age':'Days Since Followup',
            'LastFollowupedOn':'Last Contact','AmountPaid':'Amount Paid','Remarks':'Remarks'}

BKTS = ['0–7 days','8–15 days','16–30 days','30+ days']
BKT_KIND = ['won','act','act','lost']   # box color per aging bucket, freshest→stalest

def age_bkt(d):
    if pd.isna(d) or d < 0: return '0–7 days'
    d = int(d)
    if d <= 7:  return '0–7 days'
    if d <= 15: return '8–15 days'
    if d <= 30: return '16–30 days'
    return '30+ days'

# ── RAG HELPERS ────────────────────────────────────────────────────────────────
RAG = {0:'🔴', 1:'🟡', 2:'🟢'}
RAG_HEX  = {0:'#B91C1C', 1:'#92400E', 2:'#0A6640'}
RAG_BG   = {0:'#FEF2F2', 1:'#FFFBEB', 2:'#E9F7EF'}
RAG_PILL = {0:'pill-r',  1:'pill-a',  2:'pill-g'}
CHART_COLORS = {'won':'#0A6640','active':'#F59E0B','lost':'#B91C1C',
                'navy':'#0F2044','blue':'#2D5F9E'}

def rag_win(wp):       return 2 if wp>=5  else (1 if wp>=2  else 0)
def rag_stale(p):      return 2 if p<30   else (1 if p<60   else 0)
def rag_quote_conv(p): return 2 if p>=30  else (1 if p>=15  else 0)
def rag_active_age(p): return 2 if p<25   else (1 if p<50   else 0)
def rag_hygiene(p):    return 2 if p<10   else (1 if p<30   else 0)  # % missing amount

def style_fig(fig, height=380, title=None):
    """House style for Plotly charts — navy/red/light-blue branding, matches BathExpertz style_fig()."""
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=13, color='#0F172A'),
        title=dict(text=title, font=dict(size=17, color='#0F2044', family='Arial Black')) if title else None,
        margin=dict(l=45, r=25, t=55 if title else 20, b=45),
        height=height,
        legend=dict(font=dict(size=12), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hoverlabel=dict(bgcolor='white', font_size=13, font_family='Arial'),
    )
    fig.update_xaxes(showline=True, linewidth=1.5, linecolor='#0F2044', ticks='outside',
                      tickfont=dict(size=12), tickcolor='#0F2044')
    fig.update_yaxes(showline=True, linewidth=1.5, linecolor='#0F2044', ticks='outside',
                      tickfont=dict(size=12), tickcolor='#0F2044', gridcolor='#E2E8F0')
    return fig

# ── LOAD ───────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading CRM data…")
def load(fb):
    raw = bytes(fb)
    if raw[:200].lstrip()[:1] in (b'<', b'\xef', b'\xff', b'\xfe'):
        parsed = False
        for flavor in ['lxml','html5lib','html.parser']:
            try:
                df = pd.read_html(_io.BytesIO(raw), flavor=flavor)[0]
                parsed = True; break
            except: continue
        if not parsed:
            raise ValueError("Cannot parse HTML export. Try saving as .xlsx.")
    else:
        try:    df = pd.read_excel(_io.BytesIO(raw), engine='openpyxl')
        except: df = pd.read_excel(_io.BytesIO(raw), engine='xlrd')

    df['Stage'] = df['FollowupStatus'].apply(
        lambda x: 'Won' if x in WON_S else ('Lost' if x in LOST_S else 'Open'))

    if 'SourceName' in df.columns:
        df['Source'] = df['SourceName'].replace(SRC_MAP)
    else:
        df['Source'] = 'Other'
    df['Source_group'] = df['Source'].apply(lambda x: x if x in MAIN_SRC else 'Other')

    def _extract_lastfu_name(val):
        if pd.isna(val) or str(val).strip() in ('', 'nan'): return None
        return str(val).strip().replace('50988-','').strip()

    # Rep = lead owner = whoever is on LastFollowupCreatedByName. No assigneduser
    # fallback and no login-name remapping — this column is the single source of truth.
    if 'LastFollowupCreatedByName' in df.columns:
        df['Rep'] = df['LastFollowupCreatedByName'].apply(_extract_lastfu_name).fillna('Unassigned')
    else:
        df['Rep'] = 'Unassigned'

    df['is_admin'] = df['Rep'].isin(['msafe947362', 'Admin'])
    df.loc[df['Rep'].str.lower().str.contains('admin', na=False), 'is_admin'] = True
    df.loc[df['is_admin'], 'Rep'] = 'Admin'

    def _parse_dates(series):
        for fmt in ('%d-%b-%Y %H:%M:%S', '%d-%b-%Y',
                    '%d-%m-%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S',
                    '%d-%m-%Y', '%d/%m/%Y',
                    '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                parsed = pd.to_datetime(series, format=fmt, errors='coerce')
                if parsed.notna().sum() >= 0.8 * max(series.notna().sum(), 1):
                    return parsed
            except: pass
        return pd.to_datetime(series, errors='coerce', dayfirst=True)

    for col in ['CreatedOn', 'LastFollowupedOn']:
        if col in df.columns:
            df[col] = _parse_dates(df[col])
    if 'FollowupDate' in df.columns:
        df['FollowupDate_dt'] = _parse_dates(df['FollowupDate'])
    if 'AmountPaid' in df.columns:
        df['AmountPaid'] = pd.to_numeric(df['AmountPaid'], errors='coerce').fillna(0)
    else:
        df['AmountPaid'] = 0
    return df

# ── HELPERS ────────────────────────────────────────────────────────────────────
def parse_date_text(s):
    s = s.strip()
    if not s: return None
    for fmt in ('%d-%m-%Y','%d/%m/%Y','%Y-%m-%d','%d-%b-%Y'):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: continue
    return None

def prep_leads(df):
    cols = [c for c in LCOLS if c in df.columns]
    out  = df[cols].copy()
    out.columns = [LCOLS[c] for c in cols]
    for dc in ['Created','Last Contact']:
        if dc in out.columns:
            out[dc] = pd.to_datetime(out[dc], errors='coerce').dt.strftime('%d %b %Y')
    for dc in ['Lead Age (days)', 'Days Since Followup']:
        if dc in out.columns:
            out[dc] = pd.to_numeric(out[dc], errors='coerce').astype('Int64')
    if 'Amount Paid' in out.columns:
        out['Amount Paid'] = pd.to_numeric(out['Amount Paid'], errors='coerce').fillna(0).apply(fmt_amt)
    return out

def show_drill():
    if st.session_state.drill_df is None: return
    df  = st.session_state.drill_df
    lbl = st.session_state.drill_label
    st.markdown(f"<div class='drill-box'><b style='color:#0F2044;'>📋 {lbl}</b>"
                f"&nbsp;&nbsp;—&nbsp;&nbsp;{len(df):,} leads</div>", unsafe_allow_html=True)
    if len(df) == 0: st.info("No leads match."); return
    ld  = prep_leads(df)
    sty = ld.style.set_properties(**{'color':'#0F172A','font-size':'12px'})
    if 'Stage' in ld.columns:
        sty = sty.map(lambda v:(
            'background:#E9F7EF;color:#0A6640;font-weight:700' if v=='Won'
            else ('background:#FEF2F2;color:#B91C1C;font-weight:700' if v=='Lost'
                  else 'background:#FFFBEB;color:#92400E')), subset=['Stage'])
    st.dataframe(sty, use_container_width=True, height=340)
    st.download_button("⬇ Download CSV", ld.to_csv(index=False), "leads.csv", "text/csv", key="dl_drill")
    if st.button("✕ Close", key="close_drill"):
        st.session_state.drill_df = None; st.rerun()

def fmt_amt(v):
    if v is None or pd.isna(v) or v == 0:
        return '—'
    v = float(v)
    sign = '-' if v < 0 else ''
    v = abs(v)
    if v >= 1e7:  s = f"₹{v/1e7:.2f}Cr"
    elif v >= 1e5: s = f"₹{v/1e5:.2f}L"
    elif v >= 1e3: s = f"₹{v/1e3:.1f}K"
    else: s = f"₹{v:,.0f}"
    return sign + s

def txt(col, val, bold=False, color='#0F172A', size='16px'):
    fw = '700' if bold else '500'
    col.markdown(f"<div style='font-size:{size};font-weight:{fw};color:{color};"
                 f"padding:4px 0;white-space:normal;line-height:1.25;'>{val}</div>",
                 unsafe_allow_html=True)

def pill_txt(col, val, score):
    """Bold value shown as a colored RAG pill — used for Win%/conversion cells."""
    col.markdown(f"<div class='pill {RAG_PILL[score]}'>{val}</div>", unsafe_allow_html=True)

def hdr(col, label, cls='col-hdr', tip=''):
    t = f" title='{tip}'" if tip else ''
    col.markdown(f"<div class='{cls}'{t}>{label}</div>", unsafe_allow_html=True)

def nbtn(col, val, key, df_, label, kind='neutral'):
    """Number cell rendered as a colored box (kind: won/act/lost/neutral) that drills on click."""
    if val == 0:
        col.markdown("<div class='empty-box'>—</div>", unsafe_allow_html=True)
        return
    col.markdown(f"<div class='box-mark box-mark-{kind}'></div>", unsafe_allow_html=True)
    if col.button(f"{val:,}", key=key, help=label, use_container_width=True):
        drill(df_, label)

def abtn(col, amt, key, df_, label, kind='amt'):
    """Amount cell rendered as a colored box (defaults to blue 'amt' styling)."""
    if amt is None or pd.isna(amt) or amt == 0:
        col.markdown("<div class='empty-box'>—</div>", unsafe_allow_html=True)
        return
    col.markdown(f"<div class='box-mark box-mark-{kind}'></div>", unsafe_allow_html=True)
    if col.button(fmt_amt(amt), key=key, help=label, use_container_width=True):
        drill(df_, label)

def rag_cell(col, score):
    col.markdown(f"<div class='rag-badge rag-badge-{score}'>{RAG[score]}</div>",
                 unsafe_allow_html=True)

def sep():
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:8px 0;'>",
                unsafe_allow_html=True)

def tot_txt(col, val, color='#0F172A'):
    col.markdown(f"<div style='font-size:16px;font-weight:800;color:{color};"
                 f"padding:4px 0;'>{val}</div>", unsafe_allow_html=True)

def stages_present(df, order, stage_filter=None):
    sub = df[df['Stage']==stage_filter]['FollowupStatus'] if stage_filter else df['FollowupStatus']
    present = sub.dropna().unique().tolist()
    return [s for s in order if s in present] + [s for s in present if s not in order]

# ── SIDEBAR — FILE UPLOAD ──────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])

if not uploaded:
    _, m, _ = st.columns([1,2,1])
    with m:
        st.markdown(
            "<div style='text-align:center;padding:48px 24px;background:white;"
            "border-radius:12px;border:1px solid #E2E8F0;'>"
            "<div style='font-size:52px;'>📂</div>"
            "<div style='font-size:22px;font-weight:800;color:#0F2044 !important;margin:14px 0 8px;'>"
            "MSafe Inside Sales Dashboard</div>"
            "<div style='font-size:14px;color:#64748B;'>"
            "Upload your KIT19 CRM export from the sidebar.<br>"
            "Supports old Excel format and new HTML export.</div>"
            "</div>", unsafe_allow_html=True)
    st.stop()

df_raw  = load(uploaded.read())
reps_df = df_raw.copy()

# ── SIDEBAR — FILTERS ──────────────────────────────────────────────────────────
st.sidebar.markdown("### Filters")

has_dates = 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any()
if has_dates:
    _mn = reps_df['CreatedOn'].dropna().min().date()
    _mx = reps_df['CreatedOn'].dropna().max().date()
    st.sidebar.markdown(f"**Date Range** *(DD-MM-YYYY)*  \n"
                        f"<span style='font-size:10px;color:#8BAFD4;'>"
                        f"Data: {_mn.strftime('%d %b %Y')} → {_mx.strftime('%d %b %Y')}"
                        f"</span>", unsafe_allow_html=True)
    from_txt = st.sidebar.text_input("From date", value="", placeholder="e.g. 01-05-2026", key="txt_from")
    to_txt   = st.sidebar.text_input("To date",   value="", placeholder="e.g. 31-05-2026", key="txt_to")
else:
    from_txt = to_txt = ""

all_reps = sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps = st.sidebar.multiselect("Rep", all_reps, default=all_reps)
all_src  = sorted(reps_df['Source'].dropna().unique().tolist())
sel_src  = st.sidebar.multiselect("Source", all_src, default=all_src)

st.sidebar.markdown("---")
col_a, col_r = st.sidebar.columns(2)
apply_clicked = col_a.button("✅ Apply", use_container_width=True, type="primary")
reset_clicked = col_r.button("🔄 Reset", use_container_width=True)

if reset_clicked:
    st.session_state.applied_filters = None
    st.session_state.drill_df = None
    st.rerun()

if apply_clicked:
    date_from_parsed = parse_date_text(from_txt)
    date_to_parsed   = parse_date_text(to_txt)
    err = None
    if from_txt.strip() and date_from_parsed is None:
        err = f"❌ Can't read From date '{from_txt}'. Use DD-MM-YYYY."
    elif to_txt.strip() and date_to_parsed is None:
        err = f"❌ Can't read To date '{to_txt}'. Use DD-MM-YYYY."
    elif date_from_parsed and date_to_parsed and date_from_parsed > date_to_parsed:
        err = "❌ From date must be before To date."
    if err:
        st.sidebar.error(err)
        st.session_state.applied_filters = None
    else:
        st.session_state.applied_filters = {
            'date_from': date_from_parsed, 'date_to': date_to_parsed,
            'reps': sel_reps, 'src': sel_src,
        }
        st.session_state.drill_df = None

af = st.session_state.applied_filters
if af is None:
    f_date_from, f_date_to = None, None
    f_reps = all_reps; f_src = all_src
else:
    f_date_from = af['date_from']; f_date_to = af['date_to']
    f_reps = af['reps'] if af['reps'] else all_reps
    f_src  = af['src']  if af['src']  else all_src

if f_date_from and f_date_to:
    st.sidebar.success(f"📅 {f_date_from.strftime('%d %b %Y')} → {f_date_to.strftime('%d %b %Y')}")
else:
    st.sidebar.info("📅 All dates (no date filter applied)")
st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")

# ── APPLY FILTERS ──────────────────────────────────────────────────────────────
base = reps_df.copy()
if f_date_from and f_date_to and 'CreatedOn' in base.columns:
    mask = (base['CreatedOn'].dt.normalize() >= pd.Timestamp(f_date_from)) & \
           (base['CreatedOn'].dt.normalize() <= pd.Timestamp(f_date_to))
    base = base[mask]
if f_reps: base = base[base['Rep'].isin(f_reps)]
if f_src:  base = base[base['Source'].isin(f_src)]

st.sidebar.markdown(f"**Showing:** {len(base):,} leads")

# ── AGE CALCULATIONS ────────────────────────────────────────────────────────────
TODAY_NOW = pd.Timestamp.now().normalize()
base = base.copy()
if 'CreatedOn'        in base.columns:
    base['age_days']    = (TODAY_NOW - base['CreatedOn']).dt.days.clip(lower=0).astype('Int64')
if 'LastFollowupedOn' in base.columns:
    base['last_fu_age'] = (TODAY_NOW - base['LastFollowupedOn']).dt.days.clip(lower=0).astype('Int64')

if 'last_fu_age' in base.columns:
    base['fu_bkt'] = base['last_fu_age'].apply(age_bkt)
if 'age_days' in base.columns:
    base['age_bkt'] = base['age_days'].apply(age_bkt)

# ── AGGREGATES ─────────────────────────────────────────────────────────────────
HAS_AMT = 'AmountPaid' in base.columns
total   = len(base)
won     = int((base['Stage']=='Won').sum())
lost    = int((base['Stage']=='Lost').sum())
opn     = int((base['Stage']=='Open').sum())
repeats = int((base['FollowupStatus']=='Repeat Lead').sum())
wr      = round(won/total*100, 1) if total else 0

won_stages  = stages_present(base, WON_ORDER,  'Won')
act_stages  = stages_present(base, ACT_ORDER,  'Open')
lost_stages = stages_present(base, LOST_ORDER, 'Lost')

rep_order = (base.groupby('Rep')['Stage']
             .apply(lambda x: (x=='Won').sum())
             .sort_values(ascending=False).index.tolist())

def rep_rag_score(rep):
    rd = base[base['Rep']==rep]
    wp = round(len(rd[rd['Stage']=='Won'])/len(rd)*100, 1) if len(rd) else 0
    return rag_win(wp)

rep_sorted = sorted(rep_order, key=rep_rag_score)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
date_label = (f"{f_date_from.strftime('%d %b %Y')} → {f_date_to.strftime('%d %b %Y')}"
              if f_date_from and f_date_to else "All Dates")
st.markdown(
    "<div style='background:#0F2044;padding:16px 24px;border-radius:10px;"
    "margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;'>"
    "<span style='color:white !important;font-size:18px;font-weight:700;'>"
    "MSafe Equipments — Inside Sales Dashboard</span>"
    f"<span style='color:#8BAFD4;font-size:12px;'>KIT19 CRM &nbsp;|&nbsp; "
    f"{date_label} &nbsp;|&nbsp; {TODAY_NOW.strftime('%d %b %Y')}</span></div>",
    unsafe_allow_html=True)

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
q_tot   = base[base['FollowupStatus'].isin(QUOTATION_S)]
q2w     = round(won/len(q_tot)*100, 1) if len(q_tot) else 0
rep_leads = base[~base['is_admin'] & (base['Rep'] != 'Unassigned')]
unassigned = base[base['Rep']=='Unassigned']

kc = st.columns(8)
kpi_defs = [
    ('Total Leads',   f'{total:,}',   '',  base,                              "All leads"),
    ('Won',           f'{won:,}',     'g', base[base['Stage']=='Won'],         "Won leads"),
    ('Open',          f'{opn:,}',     'a', base[base['Stage']=='Open'],        "Open leads"),
    ('Lost',          f'{lost:,}',    'r', base[base['Stage']=='Lost'],        "Lost leads"),
    ('Repeat Leads',  f'{repeats:,}', 'r', base[base['FollowupStatus']=='Repeat Lead'], "Repeat leads"),
    ('Quotations Sent', f'{len(q_tot):,}', 'b', q_tot, "Quotations sent (all quoted stages + Won + Quoted Order Lost)"),
    ('Win Rate',      f'{wr}%',       'b', None,                              None),
    ('Quote → Win',   f'{q2w}%',      'g', None,                              None),
]
for i, (label, val, cls, df_, lbl) in enumerate(kpi_defs):
    with kc[i]:
        if df_ is not None and lbl is not None:
            st.markdown(f"<div class='kpi'><div class='kpi-l'>{label}</div>"
                        f"<div class='kpi-v {cls}'>{val}</div></div>",
                        unsafe_allow_html=True)
            if st.button(f"▼ drill", key=f"kpi_btn_{i}",
                         help=f"Click to see {lbl}",
                         use_container_width=True):
                drill(df_, lbl)
        else:
            st.markdown(f"<div class='kpi'><div class='kpi-l'>{label}</div>"
                        f"<div class='kpi-v {cls}'>{val}</div></div>",
                        unsafe_allow_html=True)

# ── DRILL BOX ──────────────────────────────────────────────────────────────────
if st.session_state.drill_df is not None:
    show_drill()
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:10px 0;'>",
                unsafe_allow_html=True)
else:
    st.markdown(
        "<div style='background:#F1F5F9;border:1px dashed #CBD5E1;border-radius:6px;"
        "padding:6px 14px;color:#64748B;font-size:12px;margin-bottom:4px;'>"
        "👆 Click any number, ▼ drill, or a chart bar to see leads behind it."
        "</div>", unsafe_allow_html=True)

if total == 0:
    st.warning("⚠️ No leads match the current filters. Adjust and click Apply.")
    st.stop()

# ── SHARED AGGREGATES USED ACROSS TABS ─────────────────────────────────────────
qcur_all = base[base['FollowupStatus'].isin(QUOTED_S)]
qw_all   = base[base['FollowupStatus'].isin(WON_S)]
ql_all   = base[base['FollowupStatus'].isin(['Quoted Order Lost'])]
ALL_Q_S  = QUOTATION_S
qa_all   = base[base['FollowupStatus'].isin(ALL_Q_S)]

rep_summary_rows = []
for rep in rep_order:
    rd = base[base['Rep']==rep]
    nt, nw, no, nl = len(rd), int((rd['Stage']=='Won').sum()), int((rd['Stage']=='Open').sum()), int((rd['Stage']=='Lost').sum())
    wp = round(nw/nt*100, 1) if nt else 0
    amt = rd[rd['Stage']=='Won']['AmountPaid'].sum() if HAS_AMT else 0
    rep_summary_rows.append({'Rep':rep,'Total':nt,'Won':nw,'Open':no,'Lost':nl,'Win%':wp,'AmountWon':amt,'RAG':rag_win(wp)})
rep_summary_df = pd.DataFrame(rep_summary_rows)

src_summary_rows = []
for src in base['Source'].value_counts().index.tolist():
    sd = base[base['Source']==src]
    nt, nw, no, nl = len(sd), int((sd['Stage']=='Won').sum()), int((sd['Stage']=='Open').sum()), int((sd['Stage']=='Lost').sum())
    nr = int((sd['FollowupStatus']=='Repeat Lead').sum())
    wp = round(nw/nt*100, 1) if nt else 0
    amt = sd[sd['Stage']=='Won']['AmountPaid'].sum() if HAS_AMT else 0
    src_summary_rows.append({'Source':src,'Total':nt,'Won':nw,'Open':no,'Lost':nl,'Repeat':nr,'Win%':wp,'AmountWon':amt,'RAG':rag_win(wp)})
src_summary_df = pd.DataFrame(src_summary_rows)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_over, tab_rep, tab_src, tab_age, tab_hyg = st.tabs(
    ["📈 Stage Breakdown", "👤 Rep Analysis", "🌐 Source Analysis",
     "🕒 Pipeline Aging", "⚠️ Amount Hygiene"])

# ────────────────────────────────────────────────────────────────────────────
# TAB — STAGE BREAKDOWN (Table 1 + Table 2, reworked)
# ────────────────────────────────────────────────────────────────────────────
with tab_over:
    st.markdown("<div class='sec'>Rep Stage Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>RAG pill on Win%: 🔴 &lt;2%  🟡 2–5%  🟢 &gt;5% — sorted red→green. "
                "Click ▶ to expand sub-stages.</p>", unsafe_allow_html=True)

    tc1, tc2, tc3, _ = st.columns([1.4, 1.4, 1.4, 3.8])
    if tc1.button(f"{'▼' if st.session_state.exp_won  else '▶'} Won ({len(won_stages)} stage)",  key='tog_won'):
        st.session_state.exp_won  = not st.session_state.exp_won;  st.rerun()
    if tc2.button(f"{'▼' if st.session_state.exp_act  else '▶'} Active ({len(act_stages)} stages)", key='tog_act'):
        st.session_state.exp_act  = not st.session_state.exp_act;  st.rerun()
    if tc3.button(f"{'▼' if st.session_state.exp_lost else '▶'} Lost ({len(lost_stages)} stages)", key='tog_lost'):
        st.session_state.exp_lost = not st.session_state.exp_lost; st.rerun()

    W_RAG,W_REP,W_TOT,W_GRP,W_SUB,W_WIN,W_AMT = 0.4,2.1,0.85,0.9,0.68,0.95,1.1
    widths = [W_RAG, W_REP, W_TOT, W_GRP]
    if st.session_state.exp_won:  widths += [W_SUB]*len(won_stages)
    widths += [W_GRP]
    if st.session_state.exp_act:  widths += [W_SUB]*len(act_stages)
    widths += [W_GRP]
    if st.session_state.exp_lost: widths += [W_SUB]*len(lost_stages)
    widths += [W_WIN]
    if HAS_AMT: widths += [W_AMT]

    hcols = st.columns(widths)
    hdr(hcols[0],''); hdr(hcols[1],'Rep'); hdr(hcols[2],'Total')
    ci = 3
    hdr(hcols[ci],'Won','grp-hdr-won'); ci+=1
    if st.session_state.exp_won:
        for s in won_stages:
            hdr(hcols[ci], s, 'sub-hdr sub-hdr-won'); ci+=1
    hdr(hcols[ci],'Active','grp-hdr-act'); ci+=1
    if st.session_state.exp_act:
        for s in act_stages:
            hdr(hcols[ci], s, 'sub-hdr sub-hdr-act'); ci+=1
    hdr(hcols[ci],'Lost','grp-hdr-lost'); ci+=1
    if st.session_state.exp_lost:
        for s in lost_stages:
            hdr(hcols[ci], s, 'sub-hdr sub-hdr-lost'); ci+=1
    hdr(hcols[ci],'Win %'); ci+=1
    if HAS_AMT: hdr(hcols[ci],'Amount Won','amt-hdr')

    for rep in rep_sorted:
        rd  = base[base['Rep']==rep]
        rw  = rd[rd['Stage']=='Won']
        ro  = rd[rd['Stage']=='Open']
        rl  = rd[rd['Stage']=='Lost']
        wp  = round(len(rw)/len(rd)*100, 1) if len(rd) else 0
        rs  = rag_win(wp)
        c   = st.columns(widths)
        rag_cell(c[0], rs)
        txt(c[1], rep, bold=True, color='#0F2044')
        nbtn(c[2], len(rd), f"t1tot_{rep}", rd, f"All leads — {rep}", kind='neutral')
        ci = 3
        nbtn(c[ci], len(rw), f"t1w_{rep}", rw, f"Won — {rep}", kind='won'); ci+=1
        if st.session_state.exp_won:
            for i,s in enumerate(won_stages):
                sd = rd[rd['FollowupStatus']==s]
                nbtn(c[ci], len(sd), f"t1ws_{rep}_{i}", sd, f"{s} — {rep}", kind='won'); ci+=1
        nbtn(c[ci], len(ro), f"t1a_{rep}", ro, f"Active — {rep}", kind='act'); ci+=1
        if st.session_state.exp_act:
            for i,s in enumerate(act_stages):
                sd = rd[rd['FollowupStatus']==s]
                nbtn(c[ci], len(sd), f"t1as_{rep}_{i}", sd, f"{s} — {rep}", kind='act'); ci+=1
        nbtn(c[ci], len(rl), f"t1l_{rep}", rl, f"Lost — {rep}", kind='lost'); ci+=1
        if st.session_state.exp_lost:
            for i,s in enumerate(lost_stages):
                sd = rd[rd['FollowupStatus']==s]
                nbtn(c[ci], len(sd), f"t1ls_{rep}_{i}", sd, f"{s} — {rep}", kind='lost'); ci+=1
        pill_txt(c[ci], f"{wp}%", rs); ci+=1
        if HAS_AMT:
            amt_won = rw['AmountPaid'].sum()
            abtn(c[ci], amt_won, f"t1amt_{rep}", rw, f"Won (with amount) — {rep}")

    sep()
    tc = st.columns(widths)
    tot_txt(tc[0],''); tot_txt(tc[1],'TOTAL')
    nbtn(tc[2], total, "t1_gtot", base, "All leads", kind='neutral'); ci=3
    nbtn(tc[ci], won, "t1_gwon", base[base['Stage']=='Won'], "All won leads", kind='won'); ci+=1
    if st.session_state.exp_won:
        for i,s in enumerate(won_stages):
            sd = base[base['FollowupStatus']==s]
            nbtn(tc[ci], len(sd), f"t1gws_{i}", sd, f"All — {s}", kind='won'); ci+=1
    nbtn(tc[ci], opn, "t1_gact", base[base['Stage']=='Open'], "All active leads", kind='act'); ci+=1
    if st.session_state.exp_act:
        for i,s in enumerate(act_stages):
            sd = base[base['FollowupStatus']==s]
            nbtn(tc[ci], len(sd), f"t1gas_{i}", sd, f"All — {s}", kind='act'); ci+=1
    nbtn(tc[ci], lost, "t1_glost", base[base['Stage']=='Lost'], "All lost leads", kind='lost'); ci+=1
    if st.session_state.exp_lost:
        for i,s in enumerate(lost_stages):
            sd = base[base['FollowupStatus']==s]
            nbtn(tc[ci], len(sd), f"t1gls_{i}", sd, f"All — {s}", kind='lost'); ci+=1
    pill_txt(tc[ci], f"{wr}%", rag_win(wr)); ci+=1
    if HAS_AMT:
        won_all = base[base['Stage']=='Won']
        abtn(tc[ci], won_all['AmountPaid'].sum(), "t1_gamt", won_all, "All won (with amount)")

    st.markdown("<div class='sec'>Quotation Analysis</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>All leads that reached any quoted stage. "
                "RAG: 🔴 Quote→Win &lt;15%  🟡 15–30%  🟢 &gt;30%</p>", unsafe_allow_html=True)

    q_stages = [s for s in QUOTED_S if s in base['FollowupStatus'].values]
    W2 = [W_RAG, 2.1, 0.95] + [W_SUB]*len(q_stages) + [0.95, 0.95, 0.95]
    if HAS_AMT: W2 += [W_AMT]
    h2 = st.columns(W2)
    hdr(h2[0],''); hdr(h2[1],'Rep'); hdr(h2[2],'Total Quoted')
    for i,s in enumerate(q_stages): hdr(h2[3+i], s, 'sub-hdr')
    hdr(h2[3+len(q_stages)], 'Won from Quote', 'grp-hdr-won')
    hdr(h2[4+len(q_stages)], 'Lost from Quote', 'grp-hdr-lost')
    hdr(h2[5+len(q_stages)], 'Quote→Win %')
    if HAS_AMT: hdr(h2[6+len(q_stages)], 'Amount Won', 'amt-hdr')

    qt_rows = []
    for rep in rep_order:
        rd   = base[base['Rep']==rep]
        qcur = rd[rd['FollowupStatus'].isin(QUOTED_S)]
        qw   = rd[rd['FollowupStatus'].isin(WON_S)]
        ql   = rd[rd['FollowupStatus'].isin(['Quoted Order Lost'])]
        nqw  = len(qw); nql = len(ql)
        nqa  = len(qcur) + nqw + nql
        qa   = rd[rd['FollowupStatus'].isin(ALL_Q_S)]
        qconv= round(nqw/(nqw+nql)*100, 1) if (nqw+nql)>0 else 0
        rs   = rag_quote_conv(qconv) if nqa>0 else 1
        qt_rows.append((rep, rd, qa, qcur, qw, ql, nqa, nqw, nql, qconv, rs))
    qt_rows.sort(key=lambda x: x[10])

    for rep,rd,qa,qcur,qw,ql,nqa,nqw,nql,qconv,rs in qt_rows:
        if nqa == 0: continue
        c   = st.columns(W2)
        rag_cell(c[0], rs); txt(c[1], rep, True, '#0F2044')
        nbtn(c[2], nqa, f"t2qa_{rep}", qa, f"All quoted — {rep}", kind='neutral')
        for i,s in enumerate(q_stages):
            sd = rd[rd['FollowupStatus']==s]
            nbtn(c[3+i], len(sd), f"t2qs_{rep}_{i}", sd, f"{s} — {rep}", kind='act')
        nbtn(c[3+len(q_stages)], nqw, f"t2qw_{rep}", qw, f"Won from quote — {rep}", kind='won')
        nbtn(c[4+len(q_stages)], nql, f"t2ql_{rep}", ql, f"Lost from quote — {rep}", kind='lost')
        pill_txt(c[5+len(q_stages)], f"{qconv}%", rs)
        if HAS_AMT:
            abtn(c[6+len(q_stages)], qw['AmountPaid'].sum(), f"t2amt_{rep}", qw, f"Won from quote (with amount) — {rep}")

    sep()
    gt_nqa=len(qcur_all)+len(qw_all)+len(ql_all)
    qt_conv=round(len(qw_all)/(len(qw_all)+len(ql_all))*100,1) if (len(qw_all)+len(ql_all))>0 else 0
    tc2=st.columns(W2); tot_txt(tc2[0],''); tot_txt(tc2[1],'TOTAL')
    nbtn(tc2[2],gt_nqa,'t2_gtot',qa_all,"All quoted leads", kind='neutral')
    for i,s in enumerate(q_stages):
        nbtn(tc2[3+i],len(base[base['FollowupStatus']==s]),f"t2gs_{i}",base[base['FollowupStatus']==s],f"All — {s}", kind='act')
    nbtn(tc2[3+len(q_stages)],len(qw_all),'t2_gw',qw_all,"All won from quote", kind='won')
    nbtn(tc2[4+len(q_stages)],len(ql_all),'t2_gl',ql_all,"All lost from quote", kind='lost')
    pill_txt(tc2[5+len(q_stages)], f"{qt_conv}%", rag_quote_conv(qt_conv))
    if HAS_AMT:
        abtn(tc2[6+len(q_stages)], qw_all['AmountPaid'].sum(), 't2_gamt', qw_all, "All won from quote (with amount)")

# ────────────────────────────────────────────────────────────────────────────
# TAB — REP ANALYSIS
# ────────────────────────────────────────────────────────────────────────────
with tab_rep:
    st.markdown("<div class='sec'>Rep Performance</div>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        fig = go.Figure()
        fig.add_bar(name='Won', x=rep_summary_df['Rep'], y=rep_summary_df['Won'], marker_color=CHART_COLORS['won'])
        fig.add_bar(name='Open', x=rep_summary_df['Rep'], y=rep_summary_df['Open'], marker_color=CHART_COLORS['active'])
        fig.add_bar(name='Lost', x=rep_summary_df['Rep'], y=rep_summary_df['Lost'], marker_color=CHART_COLORS['lost'])
        fig.update_layout(barmode='stack')
        style_fig(fig, title='Leads by Rep — Won / Open / Lost')
        st.plotly_chart(fig, use_container_width=True)
    with ch2:
        wsort = rep_summary_df.sort_values('Win%', ascending=True)
        colors = [RAG_HEX[rag_win(v)] for v in wsort['Win%']]
        fig2 = go.Figure(go.Bar(x=wsort['Win%'], y=wsort['Rep'], orientation='h', marker_color=colors,
                                 text=[f"{v}%" for v in wsort['Win%']], textposition='outside'))
        style_fig(fig2, title='Win Rate by Rep')
        st.plotly_chart(fig2, use_container_width=True)

    if HAS_AMT and rep_summary_df['AmountWon'].sum() > 0:
        asort = rep_summary_df.sort_values('AmountWon', ascending=True)
        fig3 = go.Figure(go.Bar(x=asort['AmountWon'], y=asort['Rep'], orientation='h',
                                 marker_color=CHART_COLORS['navy'],
                                 text=[fmt_amt(v) for v in asort['AmountWon']], textposition='outside'))
        style_fig(fig3, height=max(320, 34*len(asort)), title='Amount Won by Rep')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='sec'>Rep Summary Table</div>", unsafe_allow_html=True)
    WR = [0.4, 2.1, 0.9, 0.9, 0.9, 0.9, 0.95, 1.1]
    hr = st.columns(WR)
    hdr(hr[0],''); hdr(hr[1],'Rep'); hdr(hr[2],'Total'); hdr(hr[3],'Won','grp-hdr-won')
    hdr(hr[4],'Open','grp-hdr-act'); hdr(hr[5],'Lost','grp-hdr-lost'); hdr(hr[6],'Win %'); hdr(hr[7],'Amount Won','amt-hdr')
    for _, row in rep_summary_df.sort_values('RAG').iterrows():
        rd = base[base['Rep']==row['Rep']]
        c = st.columns(WR)
        rag_cell(c[0], row['RAG']); txt(c[1], row['Rep'], True, '#0F2044')
        nbtn(c[2], row['Total'], f"trep_tot_{row['Rep']}", rd, f"All — {row['Rep']}", kind='neutral')
        nbtn(c[3], row['Won'], f"trep_won_{row['Rep']}", rd[rd['Stage']=='Won'], f"Won — {row['Rep']}", kind='won')
        nbtn(c[4], row['Open'], f"trep_opn_{row['Rep']}", rd[rd['Stage']=='Open'], f"Open — {row['Rep']}", kind='act')
        nbtn(c[5], row['Lost'], f"trep_lst_{row['Rep']}", rd[rd['Stage']=='Lost'], f"Lost — {row['Rep']}", kind='lost')
        pill_txt(c[6], f"{row['Win%']}%", row['RAG'])
        abtn(c[7], row['AmountWon'], f"trep_amt_{row['Rep']}", rd[rd['Stage']=='Won'], f"Won (amount) — {row['Rep']}")
    st.download_button("⬇ Download Rep Summary", rep_summary_df.drop(columns='RAG').to_csv(index=False),
                        "rep_summary.csv", "text/csv", key="dl_rep")

    st.markdown("<div class='sec'>Rep × Source Conversion</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>Total, Won, Lost, Active per source group per rep.</p>", unsafe_allow_html=True)
    src_avail=[s for s in MAIN_SRC if base[base['Source_group']==s].shape[0]>0]
    rows6=[]
    for rep,*_ in sorted([(r,rep_rag_score(r)) for r in rep_order],key=lambda x:x[1]):
        rd=base[base['Rep']==rep]
        nw=int((rd['Stage']=='Won').sum()); nt=len(rd)
        wp=round(nw/nt*100,1) if nt else 0
        row={'RAG':RAG[rag_win(wp)],'Rep':rep}
        for src in src_avail:
            sd=rd[rd['Source_group']==src]
            row[f'{src} Total']=len(sd); row[f'{src} Won']=int((sd['Stage']=='Won').sum())
            row[f'{src} Lost']=int((sd['Stage']=='Lost').sum()); row[f'{src} Active']=int((sd['Stage']=='Open').sum())
        row['Total']=nt; row['Won']=nw
        row['Lost']=int((rd['Stage']=='Lost').sum()); row['Active']=int((rd['Stage']=='Open').sum())
        row['Win %']=f"{wp}%"
        rows6.append(row)
    gt6={'RAG':'','Rep':'TOTAL'}
    for src in src_avail:
        sd=base[base['Source_group']==src]
        gt6[f'{src} Total']=len(sd); gt6[f'{src} Won']=int((sd['Stage']=='Won').sum())
        gt6[f'{src} Lost']=int((sd['Stage']=='Lost').sum()); gt6[f'{src} Active']=int((sd['Stage']=='Open').sum())
    gt6['Total']=total; gt6['Won']=won; gt6['Lost']=lost; gt6['Active']=opn; gt6['Win %']=f"{wr}%"
    rows6.append(gt6)
    df6=pd.DataFrame(rows6).set_index('Rep')

    def sty_t6(df):
        s=pd.DataFrame('',index=df.index,columns=df.columns)
        for src in src_avail:
            wc=f'{src} Won'
            if wc in df.columns:
                s[wc]=df[wc].apply(lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                                    if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
            lc=f'{src} Lost'
            if lc in df.columns:
                s[lc]=df[lc].apply(lambda v:'background:#FEF2F2;color:#B91C1C'
                                    if isinstance(v,(int,float)) and v>0 else '')
        if 'Won' in df.columns:
            s['Won']=df['Won'].apply(lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                                      if isinstance(v,(int,float)) and v>0 else '')
        if 'Win %' in df.columns:
            s['Win %']=df['Win %'].apply(lambda v:(
                'background:#E9F7EF;color:#0A6640;font-weight:700' if float(v.replace('%',''))>=5 else(
                'background:#FFFBEB;color:#92400E;font-weight:600' if float(v.replace('%',''))>=2 else
                'background:#FEF2F2;color:#B91C1C;font-weight:700'))
                if isinstance(v,str) and '%' in v else '')
        if 'TOTAL' in df.index:
            s.loc['TOTAL']='background:#0F2044;color:#FFFFFF;font-weight:800'
        return s

    st.dataframe(
        df6.style.set_properties(**{'color':'#0F172A','font-size':'12px'})
           .apply(sty_t6,axis=None)
           .format(lambda x:'—' if isinstance(x,(int,float)) and x==0
                   else(f'{x:,}' if isinstance(x,(int,float)) else x)),
        use_container_width=True, height=420)

    st.markdown("<p class='note'>Drill into any combination:</p>", unsafe_allow_html=True)
    d1,d2,d3,_,d5=st.columns([2,2,2,2,1.2])
    d_rep=d1.selectbox("Rep",['All']+rep_order,key='t6_rep')
    d_src=d2.selectbox("Source",['All']+src_avail,key='t6_src')
    d_stg=d3.selectbox("Stage",['All','Won','Open','Lost'],key='t6_stg')
    if d5.button("→ View",key='t6_drill'):
        fd=base.copy()
        if d_rep!='All': fd=fd[fd['Rep']==d_rep]
        if d_src!='All': fd=fd[fd['Source_group']==d_src]
        if d_stg!='All': fd=fd[fd['Stage']==d_stg]
        drill(fd,f"{d_stg} | {d_rep} | {d_src}")
    st.download_button("⬇ Download Rep × Source",df6.to_csv(),"rep_source.csv","text/csv",key="dl_t6")

# ────────────────────────────────────────────────────────────────────────────
# TAB — SOURCE ANALYSIS
# ────────────────────────────────────────────────────────────────────────────
with tab_src:
    st.markdown("<div class='sec'>Source Performance</div>", unsafe_allow_html=True)

    sh1, sh2 = st.columns(2)
    with sh1:
        fig = px.bar(src_summary_df, x='Source', y='Total', color='Win%',
                     color_continuous_scale=['#B91C1C','#F59E0B','#0A6640'],
                     text='Total')
        fig.update_traces(textposition='outside')
        style_fig(fig, title='Leads by Source (colored by Win%)')
        st.plotly_chart(fig, use_container_width=True)
    with sh2:
        fig2 = px.pie(src_summary_df, names='Source', values='Total', hole=0.45,
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        style_fig(fig2, title='Lead Distribution by Source')
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    if HAS_AMT and src_summary_df['AmountWon'].sum() > 0:
        asort = src_summary_df.sort_values('AmountWon', ascending=True)
        fig3 = go.Figure(go.Bar(x=asort['AmountWon'], y=asort['Source'], orientation='h',
                                 marker_color=CHART_COLORS['blue'],
                                 text=[fmt_amt(v) for v in asort['AmountWon']], textposition='outside'))
        style_fig(fig3, height=max(320, 34*len(asort)), title='Amount Won by Source')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='sec'>Source Summary Table</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>RAG on Win%: 🔴 &lt;2%  🟡 2–5%  🟢 &gt;5% — sorted by total leads.</p>", unsafe_allow_html=True)
    W5=[0.4, 2.1, 0.9, 0.85, 0.85, 0.85, 0.85, 0.95, 1.1]
    h5=st.columns(W5)
    hdr(h5[0],''); hdr(h5[1],'Source'); hdr(h5[2],'Total')
    hdr(h5[3],'Won','grp-hdr-won'); hdr(h5[4],'Open','grp-hdr-act')
    hdr(h5[5],'Lost','grp-hdr-lost'); hdr(h5[6],'Repeat','grp-hdr-lost'); hdr(h5[7],'Win %')
    if HAS_AMT: hdr(h5[8],'Amount Won','amt-hdr')

    for _, row in src_summary_df.iterrows():
        sd = base[base['Source']==row['Source']]
        c=st.columns(W5); rag_cell(c[0],row['RAG']); txt(c[1],row['Source'],False,'#0F172A')
        nbtn(c[2],row['Total'],f"t5tot_{row['Source'][:15]}",sd,f"All — {row['Source']}", kind='neutral')
        nbtn(c[3],row['Won'],f"t5won_{row['Source'][:15]}",sd[sd['Stage']=='Won'],f"Won — {row['Source']}", kind='won')
        nbtn(c[4],row['Open'],f"t5opn_{row['Source'][:15]}",sd[sd['Stage']=='Open'],f"Open — {row['Source']}", kind='act')
        nbtn(c[5],row['Lost'],f"t5lst_{row['Source'][:15]}",sd[sd['Stage']=='Lost'],f"Lost — {row['Source']}", kind='lost')
        nbtn(c[6],row['Repeat'],f"t5rep_{row['Source'][:15]}",sd[sd['FollowupStatus']=='Repeat Lead'],f"Repeat — {row['Source']}", kind='lost')
        pill_txt(c[7], f"{row['Win%']}%", row['RAG'])
        if HAS_AMT:
            abtn(c[8], row['AmountWon'], f"t5amt_{row['Source'][:15]}", sd[sd['Stage']=='Won'], f"Won (amount) — {row['Source']}")

    sep()
    gt5_t=src_summary_df['Total'].sum(); gt5_w=src_summary_df['Won'].sum()
    gt5_o=src_summary_df['Open'].sum(); gt5_l=src_summary_df['Lost'].sum()
    gt5_r=src_summary_df['Repeat'].sum()
    gt5_wp=round(gt5_w/gt5_t*100,1) if gt5_t else 0
    tc5=st.columns(W5); tot_txt(tc5[0],''); tot_txt(tc5[1],'TOTAL')
    nbtn(tc5[2],gt5_t,'t5_gtot',base,"All leads", kind='neutral')
    nbtn(tc5[3],gt5_w,'t5_gwon',base[base['Stage']=='Won'],"All won", kind='won')
    nbtn(tc5[4],gt5_o,'t5_gopn',base[base['Stage']=='Open'],"All open", kind='act')
    nbtn(tc5[5],gt5_l,'t5_glst',base[base['Stage']=='Lost'],"All lost", kind='lost')
    nbtn(tc5[6],gt5_r,'t5_grep',base[base['FollowupStatus']=='Repeat Lead'],"All repeat", kind='lost')
    pill_txt(tc5[7], f"{gt5_wp}%", rag_win(gt5_wp))
    if HAS_AMT:
        abtn(tc5[8], src_summary_df['AmountWon'].sum(), 't5_gamt', base[base['Stage']=='Won'], "All won (amount)")
    st.download_button("⬇ Download Source Table", src_summary_df.drop(columns='RAG').to_csv(index=False),
                        "source_performance.csv","text/csv",key="dl_t5")

    # ── Source × Date trend ────────────────────────────────────────────────
    st.markdown("<div class='sec'>Source Trend Over Time</div>", unsafe_allow_html=True)
    if not has_dates or 'CreatedOn' not in base.columns or base['CreatedOn'].notna().sum() == 0:
        st.info("No Created date available in this export — trend table unavailable.")
    else:
        dt_base = base.dropna(subset=['CreatedOn']).copy()
        span_days = (dt_base['CreatedOn'].max() - dt_base['CreatedOn'].min()).days
        default_gran = 'Day' if span_days <= 31 else ('Week' if span_days <= 180 else 'Month')
        gran = st.radio("Granularity", ['Day', 'Week', 'Month'],
                         index=['Day', 'Week', 'Month'].index(default_gran),
                         horizontal=True, key='src_trend_gran')
        st.markdown("<p class='note'>Leads created per source, bucketed across the filtered date range. "
                    "Darker cell = higher volume for that period.</p>", unsafe_allow_html=True)

        if gran == 'Day':
            sort_key = dt_base['CreatedOn'].dt.normalize()
            dt_base['period'] = dt_base['CreatedOn'].dt.strftime('%d %b')
        elif gran == 'Week':
            sort_key = dt_base['CreatedOn'] - pd.to_timedelta(dt_base['CreatedOn'].dt.weekday, unit='D')
            dt_base['period'] = 'Wk of ' + sort_key.dt.strftime('%d %b')
        else:
            sort_key = dt_base['CreatedOn'].dt.to_period('M').dt.to_timestamp()
            dt_base['period'] = dt_base['CreatedOn'].dt.strftime('%b %Y')

        period_sort = (dt_base.assign(_s=sort_key)
                        .groupby('period')['_s'].min().sort_values().index.tolist())

        ct2 = pd.crosstab(dt_base['Source'], dt_base['period'])
        ct2 = ct2.reindex(columns=period_sort, fill_value=0)
        ct2 = ct2.reindex(index=src_summary_df['Source'].tolist(), fill_value=0)
        ct2['Total'] = ct2.sum(axis=1)
        ct2 = ct2.sort_values('Total', ascending=False)
        tot_row = ct2.sum(axis=0); tot_row.name = 'TOTAL'
        ct2 = pd.concat([ct2, tot_row.to_frame().T])

        def sty_dt(df):
            s = pd.DataFrame('', index=df.index, columns=df.columns)
            num_cols = [c for c in df.columns if c != 'Total']
            body_idx = [i for i in df.index if i != 'TOTAL']
            vmax = df.loc[body_idx, num_cols].values.max() if num_cols and body_idx else 0
            vmax = vmax if vmax and vmax > 0 else 1
            for c in num_cols:
                s[c] = df[c].apply(lambda v: (
                    f'background:rgba(15,32,68,{min(v/vmax,1)*0.55:.2f});'
                    f'color:{"white" if v/vmax>0.5 else "#0F172A"};font-weight:600')
                    if isinstance(v, (int, float)) and v > 0 else 'color:#CBD5E1')
            if 'Total' in df.columns:
                s['Total'] = 'background:#EFF6FF;color:#1D4ED8;font-weight:800'
            if 'TOTAL' in df.index:
                s.loc['TOTAL'] = 'background:#0F2044;color:#FFFFFF;font-weight:800'
            return s

        st.dataframe(
            ct2.style.set_properties(**{'color': '#0F172A', 'font-size': '12px'})
               .apply(sty_dt, axis=None)
               .format(lambda x: '—' if isinstance(x, (int, float)) and x == 0 else f'{int(x):,}'),
            use_container_width=True, height=min(46*len(ct2)+40, 480))
        st.download_button("⬇ Download Source Trend", ct2.to_csv(), "source_trend.csv", "text/csv",
                            key="dl_src_trend")

    # ── Source × Status ────────────────────────────────────────────────────
    st.markdown("<div class='sec'>Source × Lead Status</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>Count of leads per source across every follow-up status. "
                "🟢 Won stage &nbsp;&nbsp; 🟡 Active stage &nbsp;&nbsp; 🔴 Lost stage.</p>",
                unsafe_allow_html=True)

    status_order = (stages_present(base, WON_ORDER, 'Won') +
                     stages_present(base, ACT_ORDER, 'Open') +
                     stages_present(base, LOST_ORDER, 'Lost'))
    status_order = [s for s in status_order if s in base['FollowupStatus'].unique()]

    ct3 = pd.crosstab(base['Source'], base['FollowupStatus'])
    ct3 = ct3.reindex(columns=status_order, fill_value=0)
    ct3 = ct3.reindex(index=src_summary_df['Source'].tolist(), fill_value=0)
    ct3['Total'] = ct3.sum(axis=1)
    ct3 = ct3.sort_values('Total', ascending=False)
    tot_row3 = ct3.sum(axis=0); tot_row3.name = 'TOTAL'
    ct3 = pd.concat([ct3, tot_row3.to_frame().T])

    def status_kind(s):
        if s in WON_S: return 'won'
        if s in LOST_S: return 'lost'
        return 'act'

    def sty_st(df):
        s = pd.DataFrame('', index=df.index, columns=df.columns)
        for c in df.columns:
            if c == 'Total':
                s[c] = 'background:#EFF6FF;color:#1D4ED8;font-weight:800'
                continue
            kind = status_kind(c)
            bg, fg = {'won': ('#E9F7EF', '#0A6640'), 'lost': ('#FEF2F2', '#B91C1C'),
                      'act': ('#FFFBEB', '#92400E')}[kind]
            s[c] = df[c].apply(lambda v: f'background:{bg};color:{fg};font-weight:700'
                                if isinstance(v, (int, float)) and v > 0 else 'color:#CBD5E1')
        if 'TOTAL' in df.index:
            s.loc['TOTAL'] = 'background:#0F2044;color:#FFFFFF;font-weight:800'
        return s

    st.dataframe(
        ct3.style.set_properties(**{'color': '#0F172A', 'font-size': '12px'})
           .apply(sty_st, axis=None)
           .format(lambda x: '—' if isinstance(x, (int, float)) and x == 0 else f'{int(x):,}'),
        use_container_width=True, height=min(46*len(ct3)+40, 480))
    st.download_button("⬇ Download Source × Status", ct3.to_csv(), "source_status.csv", "text/csv",
                        key="dl_src_status")

# ────────────────────────────────────────────────────────────────────────────
# TAB — PIPELINE AGING (Table 3 + Table 4)
# ────────────────────────────────────────────────────────────────────────────
with tab_age:
    st.markdown("<div class='sec'>Quoted Leads Hygiene — Stale Quoted Deals</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>Only leads currently in a quoted stage. "
                "Buckets = days since last followup action. "
                "Note: KIT19 does not store the exact date a lead was first marked quoted — "
                "days are counted from the most recent followup, which is ≥ when it was quoted. "
                "RAG: 🔴 &gt;60% stuck 7+ days  🟡 30–60%  🟢 &lt;30%</p>", unsafe_allow_html=True)

    qcur_base = base[base['FollowupStatus'].isin(QUOTED_S)].copy()
    qcur_base['bkt'] = qcur_base['fu_bkt'] if 'fu_bkt' in qcur_base.columns else '0–7 days'
    qcur_base['quoted_days'] = qcur_base['last_fu_age'] if 'last_fu_age' in qcur_base.columns else pd.NA

    W3=[0.4, 2.0, 0.9, 0.9, 1.1] + [0.85]*4
    h3=st.columns(W3)
    hdr(h3[0],''); hdr(h3[1],'Rep')
    hdr(h3[2],'Total Received', tip='All leads assigned to this rep')
    hdr(h3[3],'In Quoted', tip='Currently in a quoted stage')
    hdr(h3[4],'Avg Days Since Last Followup')
    for i,b in enumerate(BKTS): hdr(h3[5+i], b, tip=f"Days since last followup: {b}")

    hyg3_rows=[]
    for rep in rep_order:
        rd_all = base[base['Rep']==rep]
        rd=qcur_base[qcur_base['Rep']==rep]; n=len(rd)
        if n==0: continue
        old7=int((rd['bkt'].isin(['8–15 days','16–30 days','30+ days'])).sum())
        pct7=round(old7/n*100,1) if n else 0
        avg_days = round(rd['quoted_days'].dropna().mean(), 1) if n else 0
        hyg3_rows.append((rep, rd_all, rd, n, pct7, avg_days, rag_stale(pct7)))
    hyg3_rows.sort(key=lambda x:x[6])

    for rep, rd_all, rd, n, pct7, avg_days, rs in hyg3_rows:
        c=st.columns(W3); rag_cell(c[0],rs); txt(c[1],rep,True,'#0F2044')
        nbtn(c[2],len(rd_all),f"t3rcv_{rep}",rd_all,f"All received — {rep}", kind='neutral')
        nbtn(c[3],n,f"t3tot_{rep}",rd,f"All quoted — {rep}", kind='act')
        avg_c = '#B91C1C' if avg_days>15 else ('#92400E' if avg_days>7 else '#0A6640')
        txt(c[4], f"{avg_days}d", bold=True, color=avg_c)
        for i,b in enumerate(BKTS):
            bd=rd[rd['bkt']==b]; nbtn(c[5+i],len(bd),f"t3b_{rep}_{i}",bd,f"{b} since last followup — {rep}",kind=BKT_KIND[i])

    sep()
    tc3=st.columns(W3); tot_txt(tc3[0],''); tot_txt(tc3[1],'TOTAL')
    nbtn(tc3[2],len(base),'t3_gtot_rcv',base,"All leads", kind='neutral')
    nbtn(tc3[3],len(qcur_base),'t3_gtot',qcur_base,"All in quoted stage", kind='act')
    overall_avg = round(qcur_base['quoted_days'].dropna().mean(), 1) if len(qcur_base) else 0
    avg_c = '#B91C1C' if overall_avg>15 else ('#92400E' if overall_avg>7 else '#0A6640')
    txt(tc3[4], f"{overall_avg}d", bold=True, color=avg_c)
    for i,b in enumerate(BKTS):
        bd=qcur_base[qcur_base['bkt']==b]; nbtn(tc3[5+i],len(bd),f"t3gb_{i}",bd,f"All quoted — {b}",kind=BKT_KIND[i])

    st.markdown("<div class='sec'>Active Pipeline Aging</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>All Open leads bucketed by <b>days since last followup</b>. "
                "RAG: 🔴 &gt;50% not touched in 7+ days  🟡 25–50%  🟢 &lt;25%</p>", unsafe_allow_html=True)

    act_base=base[base['Stage']=='Open'].copy()
    act_base['bkt'] = act_base['fu_bkt'] if 'fu_bkt' in act_base.columns else '0–7 days'

    W4=[0.4, 2.0, 0.95, 1.1] + [0.9]*4
    h4=st.columns(W4)
    hdr(h4[0],''); hdr(h4[1],'Rep'); hdr(h4[2],'Total Active')
    hdr(h4[3],'Avg Days Since Followup')
    for i,b in enumerate(BKTS):
        hdr(h4[4+i], b, tip=f"Days since last followup: {b}")

    act4_rows=[]
    for rep in rep_order:
        rd=act_base[act_base['Rep']==rep]; n=len(rd)
        if n==0: continue
        old7=int((rd['bkt'].isin(['8–15 days','16–30 days','30+ days'])).sum())
        pct7=round(old7/n*100,1) if n else 0
        avg_fu=round(rd['last_fu_age'].dropna().mean(),1) if 'last_fu_age' in rd.columns and n else 0
        act4_rows.append((rep,rd,n,pct7,avg_fu,rag_active_age(pct7)))
    act4_rows.sort(key=lambda x:x[5])

    for rep,rd,n,pct7,avg_fu,rs in act4_rows:
        c=st.columns(W4); rag_cell(c[0],rs); txt(c[1],rep,True,'#0F2044')
        nbtn(c[2],n,f"t4tot_{rep}",rd,f"All active — {rep}", kind='neutral')
        avg_c='#B91C1C' if avg_fu>15 else ('#92400E' if avg_fu>7 else '#0A6640')
        txt(c[3],f"{avg_fu}d",bold=True,color=avg_c)
        for i,b in enumerate(BKTS):
            bd=rd[rd['bkt']==b]; nbtn(c[4+i],len(bd),f"t4b_{rep}_{i}",bd,f"{b} since last followup — {rep}",kind=BKT_KIND[i])

    sep()
    tc4=st.columns(W4); tot_txt(tc4[0],''); tot_txt(tc4[1],'TOTAL')
    nbtn(tc4[2],len(act_base),'t4_gtot',act_base,"All active leads", kind='neutral')
    overall_act_avg=round(act_base['last_fu_age'].dropna().mean(),1) if 'last_fu_age' in act_base.columns and len(act_base) else 0
    avg_c='#B91C1C' if overall_act_avg>15 else ('#92400E' if overall_act_avg>7 else '#0A6640')
    txt(tc4[3],f"{overall_act_avg}d",bold=True,color=avg_c)
    for i,b in enumerate(BKTS):
        bd=act_base[act_base['bkt']==b]; nbtn(tc4[4+i],len(bd),f"t4gb_{i}",bd,f"All active — {b}",kind=BKT_KIND[i])

# ────────────────────────────────────────────────────────────────────────────
# TAB — AMOUNT HYGIENE (new: quoted / won leads missing AmountPaid)
# ────────────────────────────────────────────────────────────────────────────
with tab_hyg:
    st.markdown("<div class='sec'>Amount Paid Hygiene</div>", unsafe_allow_html=True)
    st.markdown("<p class='note'>Deals sitting in a <b>Quoted</b> stage or marked <b>Won</b> "
                "where the Amount Paid field is blank / zero — a data-entry gap, since both "
                "stages should carry a deal value. RAG: 🔴 &gt;30% missing  🟡 10–30%  🟢 &lt;10%.</p>",
                unsafe_allow_html=True)

    if not HAS_AMT:
        st.info("No AmountPaid column found in this export — hygiene check unavailable.")
    else:
        qcur_base2 = base[base['FollowupStatus'].isin(QUOTED_S)]
        won_base2  = base[base['FollowupStatus'].isin(WON_S)]
        q_missing  = qcur_base2[qcur_base2['AmountPaid']==0]
        w_missing  = won_base2[won_base2['AmountPaid']==0]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='kpi'><div class='kpi-l'>Quoted Leads</div>"
                        f"<div class='kpi-v'>{len(qcur_base2):,}</div></div>", unsafe_allow_html=True)
        with m2:
            pq = round(len(q_missing)/len(qcur_base2)*100,1) if len(qcur_base2) else 0
            cls = 'r' if pq>=30 else ('a' if pq>=10 else 'g')
            st.markdown(f"<div class='kpi'><div class='kpi-l'>Quoted — Amount Missing</div>"
                        f"<div class='kpi-v {cls}'>{len(q_missing):,} ({pq}%)</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='kpi'><div class='kpi-l'>Won Leads</div>"
                        f"<div class='kpi-v'>{len(won_base2):,}</div></div>", unsafe_allow_html=True)
        with m4:
            pw = round(len(w_missing)/len(won_base2)*100,1) if len(won_base2) else 0
            cls = 'r' if pw>=30 else ('a' if pw>=10 else 'g')
            st.markdown(f"<div class='kpi'><div class='kpi-l'>Won — Amount Missing</div>"
                        f"<div class='kpi-v {cls}'>{len(w_missing):,} ({pw}%)</div></div>", unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("▼ View Quoted leads with no amount", key="hyg_q_btn", use_container_width=True):
                drill(q_missing, "Quoted stage — Amount Paid missing")
        with b2:
            if st.button("▼ View Won leads with no amount", key="hyg_w_btn", use_container_width=True):
                drill(w_missing, "Won stage — Amount Paid missing")

        st.markdown("<div class='sec'>By Rep</div>", unsafe_allow_html=True)
        hyg_rows = []
        for rep in rep_order:
            rq  = qcur_base2[qcur_base2['Rep']==rep]
            rqm = rq[rq['AmountPaid']==0]
            rw  = won_base2[won_base2['Rep']==rep]
            rwm = rw[rw['AmountPaid']==0]
            if len(rq)==0 and len(rw)==0: continue
            pq_r = round(len(rqm)/len(rq)*100,1) if len(rq) else 0
            pw_r = round(len(rwm)/len(rw)*100,1) if len(rw) else 0
            combined_pct = round((len(rqm)+len(rwm))/max(len(rq)+len(rw),1)*100, 1)
            hyg_rows.append({'Rep':rep,'rq':rq,'rqm':rqm,'rw':rw,'rwm':rwm,
                              'Quoted Total':len(rq),'Quoted Missing':len(rqm),'Quoted Missing %':pq_r,
                              'Won Total':len(rw),'Won Missing':len(rwm),'Won Missing %':pw_r,
                              'RAG':rag_hygiene(combined_pct)})
        hyg_rows.sort(key=lambda x: x['RAG'])

        WH = [0.4, 2.0, 0.85, 1.0, 1.05, 0.85, 0.9, 0.95]
        hh = st.columns(WH)
        hdr(hh[0],''); hdr(hh[1],'Rep'); hdr(hh[2],'Quoted Total')
        hdr(hh[3],'Quoted — No Amt','grp-hdr-lost'); hdr(hh[4],'Quoted Missing %')
        hdr(hh[5],'Won Total'); hdr(hh[6],'Won — No Amt','grp-hdr-lost'); hdr(hh[7],'Won Missing %')

        for r in hyg_rows:
            c = st.columns(WH)
            rag_cell(c[0], r['RAG']); txt(c[1], r['Rep'], True, '#0F2044')
            nbtn(c[2], r['Quoted Total'], f"hq_tot_{r['Rep']}", r['rq'], f"All quoted — {r['Rep']}", kind='neutral')
            nbtn(c[3], r['Quoted Missing'], f"hq_mis_{r['Rep']}", r['rqm'], f"Quoted, no amount — {r['Rep']}", kind='lost')
            pill_txt(c[4], f"{r['Quoted Missing %']}%", rag_hygiene(r['Quoted Missing %']))
            nbtn(c[5], r['Won Total'], f"hw_tot_{r['Rep']}", r['rw'], f"All won — {r['Rep']}", kind='neutral')
            nbtn(c[6], r['Won Missing'], f"hw_mis_{r['Rep']}", r['rwm'], f"Won, no amount — {r['Rep']}", kind='lost')
            pill_txt(c[7], f"{r['Won Missing %']}%", rag_hygiene(r['Won Missing %']))

        sep()
        tch = st.columns(WH)
        tot_txt(tch[0],''); tot_txt(tch[1],'TOTAL')
        nbtn(tch[2], len(qcur_base2), 'hg_qtot', qcur_base2, "All quoted leads", kind='neutral')
        nbtn(tch[3], len(q_missing), 'hg_qmis', q_missing, "All quoted, no amount", kind='lost')
        pill_txt(tch[4], f"{pq}%", rag_hygiene(pq))
        nbtn(tch[5], len(won_base2), 'hg_wtot', won_base2, "All won leads", kind='neutral')
        nbtn(tch[6], len(w_missing), 'hg_wmis', w_missing, "All won, no amount", kind='lost')
        pill_txt(tch[7], f"{pw}%", rag_hygiene(pw))

        chc1, chc2 = st.columns(2)
        with chc1:
            hdf = pd.DataFrame([{'Rep':r['Rep'],'Missing':r['Quoted Missing']} for r in hyg_rows if r['Quoted Missing']>0])
            if not hdf.empty:
                hdf = hdf.sort_values('Missing', ascending=True)
                fig = go.Figure(go.Bar(x=hdf['Missing'], y=hdf['Rep'], orientation='h',
                                        marker_color=CHART_COLORS['lost'], text=hdf['Missing'], textposition='outside'))
                style_fig(fig, height=max(300, 32*len(hdf)), title='Quoted Leads Missing Amount — by Rep')
                st.plotly_chart(fig, use_container_width=True)
        with chc2:
            hdf2 = pd.DataFrame([{'Rep':r['Rep'],'Missing':r['Won Missing']} for r in hyg_rows if r['Won Missing']>0])
            if not hdf2.empty:
                hdf2 = hdf2.sort_values('Missing', ascending=True)
                fig2 = go.Figure(go.Bar(x=hdf2['Missing'], y=hdf2['Rep'], orientation='h',
                                         marker_color='#7C2D12', text=hdf2['Missing'], textposition='outside'))
                style_fig(fig2, height=max(300, 32*len(hdf2)), title='Won Leads Missing Amount — by Rep')
                st.plotly_chart(fig2, use_container_width=True)

        st.download_button("⬇ Download Amount Hygiene Table",
            pd.DataFrame([{k:v for k,v in r.items() if k not in ('rq','rqm','rw','rwm')} for r in hyg_rows]).to_csv(index=False),
            "amount_hygiene.csv", "text/csv", key="dl_hyg")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{total:,} leads showing  |  {TODAY_NOW.strftime('%d %b %Y')}</p>",
    unsafe_allow_html=True)
