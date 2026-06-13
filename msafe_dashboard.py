import streamlit as st
import pandas as pd
import numpy as np
import io as _io
from datetime import datetime

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
     font-weight:700;font-size:13px;margin:20px 0 4px;}
.note{font-size:11px;color:#64748B;font-style:italic;margin:0 0 6px;}
.col-hdr{font-size:10px;font-weight:700;color:#475569;
         border-bottom:2px solid #0F2044;padding-bottom:2px;margin-bottom:2px;
         overflow:hidden;white-space:nowrap;text-overflow:ellipsis;}
.grp-hdr-won{font-size:10px;font-weight:800;color:#0A6640;
             border-bottom:3px solid #0A6640;padding-bottom:2px;margin-bottom:2px;}
.grp-hdr-act{font-size:10px;font-weight:800;color:#92400E;
             border-bottom:3px solid #F59E0B;padding-bottom:2px;margin-bottom:2px;}
.grp-hdr-lost{font-size:10px;font-weight:800;color:#B91C1C;
              border-bottom:3px solid #B91C1C;padding-bottom:2px;margin-bottom:2px;}
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"]*{
    background:#1B3A6B !important;color:white !important;
    font-size:11px !important;font-weight:700 !important;}
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"]*{color:#0F172A !important;font-size:11px !important;}
[data-testid="stDataFrame"] [role="rowheader"],[data-testid="stDataFrame"] [role="rowheader"]*{
    color:#0F172A !important;font-size:11px !important;
    font-weight:600 !important;background:#F1F5F9 !important;}
button[data-testid="baseButton-secondary"]{
    padding:2px 4px !important;font-size:12px !important;min-height:28px !important;}
</style>""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
WON_S    = ['Quoted Order Won And Executed']
LOST_S   = ['Not-Interested','Not Search Our Product','Regret',
            'Other Department Working','Wrong Number','No Response on RNR',
            'Already Purchased','Quoted Order Lost',
            'Repeat Lead','Rental Period Less Than 7 Days']
QUOTED_S = ['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
            'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold']
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
    'Just Dial':'JustDial','Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SRC = ['JustDial','IndiaMart','IVR Call','Existing Client','Ex-Client Ref.','Facebook','Other']
LCOLS    = {'LeadNo':'Lead #','PersonName':'Customer','CompanyName':'Company',
            'City':'City','Source':'Source','Category':'Category','Rep':'Rep',
            'FollowupStatus':'Status','Stage':'Stage','CreatedOn':'Created',
            'age_days':'Age (days)','LastFollowupedOn':'Last Contact','Remarks':'Remarks'}

# ── RAG HELPERS ────────────────────────────────────────────────────────────────
RAG = {0:'🔴', 1:'🟡', 2:'🟢'}
def rag_win(wp):       return 2 if wp>=5  else (1 if wp>=2  else 0)
def rag_stale(p):      return 2 if p<30   else (1 if p<60   else 0)
def rag_quote_conv(p): return 2 if p>=30  else (1 if p>=15  else 0)
def rag_active_age(p): return 2 if p<25   else (1 if p<50   else 0)

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

    if 'assigneduser' in df.columns and df['assigneduser'].notna().any():
        def parse_rep(val):
            if pd.isna(val) or str(val).strip() in ('','nan'): return 'Unassigned'
            s = str(val).strip()
            if '(' in s and ')' in s: return s[s.index('(')+1:s.index(')')].strip()
            return s.replace('50988-','').strip()
        df['Rep']      = df['assigneduser'].apply(parse_rep)
        df['is_admin'] = df['Rep'].isin(['Unassigned','msafe947362'])
    else:
        df['is_admin'] = df['LastFollowupCreatedByName'].isin(ADMIN)
        df['Rep']      = df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
        df.loc[df['is_admin'],'Rep'] = 'Admin'

    def _parse_dates(series):
        # KIT19 exports dates as 'DD-Mon-YYYY HH:MM:SS' e.g. '31-May-2026 23:03:15'
        # Try that first, then fall back through other common formats.
        for fmt in ('%d-%b-%Y %H:%M:%S', '%d-%b-%Y',
                    '%d-%m-%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S',
                    '%d-%m-%Y', '%d/%m/%Y',
                    '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                parsed = pd.to_datetime(series, format=fmt, errors='coerce')
                if parsed.notna().sum() >= 0.8 * max(series.notna().sum(), 1):
                    return parsed
            except Exception:
                pass
        return pd.to_datetime(series, errors='coerce', dayfirst=True)

    for col in ['CreatedOn', 'LastFollowupedOn']:
        if col in df.columns:
            df[col] = _parse_dates(df[col])
    if 'FollowupDate' in df.columns:
        df['FollowupDate_dt'] = _parse_dates(df['FollowupDate'])
    if 'AmountPaid' in df.columns:
        df['AmountPaid'] = pd.to_numeric(df['AmountPaid'], errors='coerce').fillna(0)
    return df

# ── HELPERS ────────────────────────────────────────────────────────────────────
def parse_date_text(s):
    """Parse DD-MM-YYYY or DD/MM/YYYY typed by user. Returns date or None."""
    s = s.strip()
    if not s:
        return None
    for fmt in ('%d-%m-%Y','%d/%m/%Y','%Y-%m-%d','%d-%b-%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def prep_leads(df):
    cols = [c for c in LCOLS if c in df.columns]
    out  = df[cols].copy()
    out.columns = [LCOLS[c] for c in cols]
    for dc in ['Created','Last Contact']:
        if dc in out.columns:
            out[dc] = pd.to_datetime(out[dc], errors='coerce').dt.strftime('%d %b %Y')
    return out

def show_drill():
    if st.session_state.drill_df is None: return
    df  = st.session_state.drill_df
    lbl = st.session_state.drill_label
    st.markdown(f"<div class='drill-box'><b style='color:#0F2044;'>📋 {lbl}</b>"
                f"&nbsp;&nbsp;—&nbsp;&nbsp;{len(df):,} leads</div>", unsafe_allow_html=True)
    if len(df) == 0:
        st.info("No leads match."); return
    ld  = prep_leads(df)
    sty = ld.style.set_properties(**{'color':'#0F172A','font-size':'12px'})
    if 'Stage' in ld.columns:
        sty = sty.map(lambda v:(
            'background:#E9F7EF;color:#0A6640;font-weight:700' if v=='Won'
            else ('background:#FEF2F2;color:#B91C1C;font-weight:700' if v=='Lost'
                  else 'background:#FFFBEB;color:#92400E')), subset=['Stage'])
    st.dataframe(sty, use_container_width=True, height=340)
    st.download_button("⬇ Download CSV", ld.to_csv(index=False),
                       "leads.csv", "text/csv", key="dl_drill")
    if st.button("✕ Close", key="close_drill"):
        st.session_state.drill_df = None; st.rerun()

def txt(col, val, bold=False, color='#0F172A', size='13px'):
    fw = '700' if bold else '500'
    col.markdown(f"<div style='font-size:{size};font-weight:{fw};color:{color};"
                 f"padding:4px 0;white-space:nowrap;overflow:hidden;"
                 f"text-overflow:ellipsis;'>{val}</div>", unsafe_allow_html=True)

def hdr(col, label, cls='col-hdr', tip=''):
    t = f" title='{tip}'" if tip else ''
    col.markdown(f"<div class='{cls}'{t}>{label}</div>", unsafe_allow_html=True)

def nbtn(col, val, key, df_, label):
    if val == 0:
        col.markdown("<div style='font-size:12px;color:#CBD5E1;padding:4px 0;'>—</div>",
                     unsafe_allow_html=True)
    elif col.button(f"{val:,}", key=key, help=label):
        drill(df_, label)

def rag_cell(col, score):
    col.markdown(f"<div style='font-size:16px;text-align:center;padding:3px 0;'>"
                 f"{RAG[score]}</div>", unsafe_allow_html=True)

def sep():
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:1px 0;'>",
                unsafe_allow_html=True)

def tot_txt(col, val, color='#0F172A'):
    col.markdown(f"<div style='font-size:13px;font-weight:800;color:{color};"
                 f"padding:4px 0;'>{val}</div>", unsafe_allow_html=True)

def stages_present(df, order, stage_filter=None):
    sub = df[df['Stage']==stage_filter]['FollowupStatus'] if stage_filter else df['FollowupStatus']
    present = sub.dropna().unique().tolist()
    return [s for s in order if s in present] + [s for s in present if s not in order]

def age_bkt3(d):
    if pd.isna(d) or d < 0: return '0–7 days'
    if d <= 7:  return '0–7 days'
    if d <= 15: return '8–15 days'
    if d <= 30: return '16–30 days'
    return '30+ days'

# ── SIDEBAR — FILE UPLOAD ──────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)", type=['xls','xlsx'])

if not uploaded:
    _, m, _ = st.columns([1,2,1])
    with m:
        st.markdown("<br><br>", unsafe_allow_html=True)
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
reps_df = df_raw[~df_raw['is_admin']].copy()

# ── SIDEBAR — FILTERS ──────────────────────────────────────────────────────────
st.sidebar.markdown("### Filters")

# Date range — plain text inputs, user types DD-MM-YYYY
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

# Apply / Reset buttons
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

    # Validate
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
            'date_from': date_from_parsed,
            'date_to':   date_to_parsed,
            'reps':      sel_reps,
            'src':       sel_src,
        }
        st.session_state.drill_df = None

# ── RESOLVE ACTIVE FILTERS ─────────────────────────────────────────────────────
af = st.session_state.applied_filters
if af is None:
    # Default: no date filter, all reps and sources
    f_date_from = None
    f_date_to   = None
    f_reps      = all_reps
    f_src       = all_src
else:
    f_date_from = af['date_from']
    f_date_to   = af['date_to']
    f_reps      = af['reps'] if af['reps'] else all_reps
    f_src       = af['src']  if af['src']  else all_src

# Show active filter status
if f_date_from and f_date_to:
    st.sidebar.success(f"📅 {f_date_from.strftime('%d %b %Y')} → {f_date_to.strftime('%d %b %Y')}")
else:
    st.sidebar.info("📅 All dates (no date filter applied)")

st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")

# ── APPLY FILTERS TO DATA ──────────────────────────────────────────────────────
base = reps_df.copy()

if f_date_from and f_date_to and 'CreatedOn' in base.columns:
    mask = (
        base['CreatedOn'].dt.normalize() >= pd.Timestamp(f_date_from)
    ) & (
        base['CreatedOn'].dt.normalize() <= pd.Timestamp(f_date_to)
    )
    base = base[mask]

if f_reps: base = base[base['Rep'].isin(f_reps)]
if f_src:  base = base[base['Source'].isin(f_src)]

st.sidebar.markdown(f"**Showing:** {len(base):,} leads")

# ── AGE CALCULATIONS (always fresh, never cached) ──────────────────────────────
TODAY_NOW = pd.Timestamp.now().normalize()
base = base.copy()
if 'CreatedOn'        in base.columns: base['age_days']    = (TODAY_NOW - base['CreatedOn']).dt.days.clip(lower=0)
if 'LastFollowupedOn' in base.columns: base['last_fu_age'] = (TODAY_NOW - base['LastFollowupedOn']).dt.days.clip(lower=0)

# ── AGGREGATES ─────────────────────────────────────────────────────────────────
total = len(base)
won   = int((base['Stage']=='Won').sum())
lost  = int((base['Stage']=='Lost').sum())
opn   = int((base['Stage']=='Open').sum())
wr    = round(won/total*100, 1) if total else 0

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
# HEADER + KPIs
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

kc = st.columns(6)
def kpi(col, l, v, cls=''):
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{l}</div>"
                 f"<div class='kpi-v {cls}'>{v}</div></div>", unsafe_allow_html=True)
kpi(kc[0], 'Total Leads', f'{total:,}')
kpi(kc[1], 'Won',  f'{won:,}',  'g')
kpi(kc[2], 'Open', f'{opn:,}',  'a')
kpi(kc[3], 'Lost', f'{lost:,}', 'r')
kpi(kc[4], 'Win Rate', f'{wr}%', 'b')
q_tot = base[base['FollowupStatus'].isin(QUOTED_S + WON_S)]
q2w   = round(won/len(q_tot)*100, 1) if len(q_tot) else 0
kpi(kc[5], 'Quote → Win', f'{q2w}%', 'g')

st.markdown("<br>", unsafe_allow_html=True)

# ── DRILL BOX ──────────────────────────────────────────────────────────────────
if st.session_state.drill_df is not None:
    show_drill()
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:10px 0;'>",
                unsafe_allow_html=True)
else:
    st.markdown(
        "<div style='background:#F1F5F9;border:1px dashed #CBD5E1;border-radius:8px;"
        "padding:10px 16px;color:#64748B;font-size:13px;margin-bottom:10px;'>"
        "👆 Click any number in the tables below to see the leads behind it."
        "</div>", unsafe_allow_html=True)

if total == 0:
    st.warning("⚠️ No leads match the current filters. Adjust the date range or other filters and click Apply.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# TABLE 1 — REP STAGE BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 1 — Rep Stage Breakdown</div>", unsafe_allow_html=True)
st.markdown("<p class='note'>RAG: 🔴 Win% &lt;2%  🟡 2–5%  🟢 &gt;5% — sorted red→green. "
            "Click ▶ to expand sub-stages.</p>", unsafe_allow_html=True)

tc1, tc2, tc3, _ = st.columns([1.4, 1.4, 1.4, 3.8])
if tc1.button(f"{'▼' if st.session_state.exp_won  else '▶'} Won ({len(won_stages)} stage)",  key='tog_won'):
    st.session_state.exp_won  = not st.session_state.exp_won;  st.rerun()
if tc2.button(f"{'▼' if st.session_state.exp_act  else '▶'} Active ({len(act_stages)} stages)", key='tog_act'):
    st.session_state.exp_act  = not st.session_state.exp_act;  st.rerun()
if tc3.button(f"{'▼' if st.session_state.exp_lost else '▶'} Lost ({len(lost_stages)} stages)", key='tog_lost'):
    st.session_state.exp_lost = not st.session_state.exp_lost; st.rerun()

W_RAG,W_REP,W_TOT,W_GRP,W_SUB,W_WIN = 0.35,1.8,0.7,0.75,0.58,0.65
widths = [W_RAG, W_REP, W_TOT, W_GRP]
if st.session_state.exp_won:  widths += [W_SUB]*len(won_stages)
widths += [W_GRP]
if st.session_state.exp_act:  widths += [W_SUB]*len(act_stages)
widths += [W_GRP]
if st.session_state.exp_lost: widths += [W_SUB]*len(lost_stages)
widths += [W_WIN]

hcols = st.columns(widths)
hdr(hcols[0],''); hdr(hcols[1],'Rep'); hdr(hcols[2],'Total')
ci = 3
hdr(hcols[ci],'Won','grp-hdr-won'); ci+=1
if st.session_state.exp_won:
    for s in won_stages:
        hdr(hcols[ci], s[:14]+'…' if len(s)>14 else s, 'grp-hdr-won', tip=s); ci+=1
hdr(hcols[ci],'Active','grp-hdr-act'); ci+=1
if st.session_state.exp_act:
    for s in act_stages:
        hdr(hcols[ci], s[:14]+'…' if len(s)>14 else s, 'grp-hdr-act', tip=s); ci+=1
hdr(hcols[ci],'Lost','grp-hdr-lost'); ci+=1
if st.session_state.exp_lost:
    for s in lost_stages:
        hdr(hcols[ci], s[:14]+'…' if len(s)>14 else s, 'grp-hdr-lost', tip=s); ci+=1
hdr(hcols[ci],'Win %')

for rep in rep_sorted:
    rd  = base[base['Rep']==rep]
    rw  = rd[rd['Stage']=='Won']
    ro  = rd[rd['Stage']=='Open']
    rl  = rd[rd['Stage']=='Lost']
    wp  = round(len(rw)/len(rd)*100, 1) if len(rd) else 0
    rs  = rag_win(wp)
    wpc = '#0A6640' if rs==2 else ('#92400E' if rs==1 else '#B91C1C')
    c   = st.columns(widths)
    rag_cell(c[0], rs)
    txt(c[1], rep, bold=True, color='#0F2044')
    nbtn(c[2], len(rd), f"t1tot_{rep}", rd, f"All leads — {rep}")
    ci = 3
    nbtn(c[ci], len(rw), f"t1w_{rep}", rw, f"Won — {rep}"); ci+=1
    if st.session_state.exp_won:
        for i,s in enumerate(won_stages):
            sd = rd[rd['FollowupStatus']==s]
            nbtn(c[ci], len(sd), f"t1ws_{rep}_{i}", sd, f"{s} — {rep}"); ci+=1
    nbtn(c[ci], len(ro), f"t1a_{rep}", ro, f"Active — {rep}"); ci+=1
    if st.session_state.exp_act:
        for i,s in enumerate(act_stages):
            sd = rd[rd['FollowupStatus']==s]
            nbtn(c[ci], len(sd), f"t1as_{rep}_{i}", sd, f"{s} — {rep}"); ci+=1
    nbtn(c[ci], len(rl), f"t1l_{rep}", rl, f"Lost — {rep}"); ci+=1
    if st.session_state.exp_lost:
        for i,s in enumerate(lost_stages):
            sd = rd[rd['FollowupStatus']==s]
            nbtn(c[ci], len(sd), f"t1ls_{rep}_{i}", sd, f"{s} — {rep}"); ci+=1
    txt(c[ci], f"{wp}%", bold=True, color=wpc)

sep()
tc = st.columns(widths)
tot_txt(tc[0],''); tot_txt(tc[1],'TOTAL')
nbtn(tc[2], total, "t1_gtot", base, "All leads"); ci=3
nbtn(tc[ci], won, "t1_gwon", base[base['Stage']=='Won'], "All won leads"); ci+=1
if st.session_state.exp_won:
    for i,s in enumerate(won_stages):
        sd = base[base['FollowupStatus']==s]
        nbtn(tc[ci], len(sd), f"t1gws_{i}", sd, f"All — {s}"); ci+=1
nbtn(tc[ci], opn, "t1_gact", base[base['Stage']=='Open'], "All active leads"); ci+=1
if st.session_state.exp_act:
    for i,s in enumerate(act_stages):
        sd = base[base['FollowupStatus']==s]
        nbtn(tc[ci], len(sd), f"t1gas_{i}", sd, f"All — {s}"); ci+=1
nbtn(tc[ci], lost, "t1_glost", base[base['Stage']=='Lost'], "All lost leads"); ci+=1
if st.session_state.exp_lost:
    for i,s in enumerate(lost_stages):
        sd = base[base['FollowupStatus']==s]
        nbtn(tc[ci], len(sd), f"t1gls_{i}", sd, f"All — {s}"); ci+=1
tot_txt(tc[ci], f"{wr}%", color='#1D4ED8')

# ══════════════════════════════════════════════════════════════════════════════
# TABLE 2 — QUOTATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 2 — Quotation Analysis</div>", unsafe_allow_html=True)
st.markdown("<p class='note'>All leads that reached any quoted stage. "
            "Total Quoted = pending sub-stages + Won from Quote + Lost from Quote. "
            "RAG: 🔴 Quote→Win &lt;15%  🟡 15–30%  🟢 &gt;30%</p>", unsafe_allow_html=True)

ALL_Q_S  = QUOTED_S + WON_S + ['Quoted Order Lost']
q_stages = [s for s in QUOTED_S if s in base['FollowupStatus'].values]
W2 = [W_RAG, 1.8, 0.8] + [W_SUB]*len(q_stages) + [0.8, 0.8, 0.7]
h2 = st.columns(W2)
hdr(h2[0],''); hdr(h2[1],'Rep'); hdr(h2[2],'Total Quoted')
for i,s in enumerate(q_stages): hdr(h2[3+i], s[:14]+'…' if len(s)>14 else s, tip=s)
hdr(h2[3+len(q_stages)], 'Won from\nQuote')
hdr(h2[4+len(q_stages)], 'Lost from\nQuote')
hdr(h2[5+len(q_stages)], 'Quote→Win %')

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
    wpc = '#0A6640' if rs==2 else ('#92400E' if rs==1 else '#B91C1C')
    c   = st.columns(W2)
    rag_cell(c[0], rs); txt(c[1], rep, True, '#0F2044')
    nbtn(c[2], nqa, f"t2qa_{rep}", qa, f"All quoted — {rep}")
    for i,s in enumerate(q_stages):
        sd = rd[rd['FollowupStatus']==s]
        nbtn(c[3+i], len(sd), f"t2qs_{rep}_{i}", sd, f"{s} — {rep}")
    nbtn(c[3+len(q_stages)], nqw, f"t2qw_{rep}", qw, f"Won from quote — {rep}")
    nbtn(c[4+len(q_stages)], nql, f"t2ql_{rep}", ql, f"Lost from quote — {rep}")
    txt(c[5+len(q_stages)], f"{qconv}%", True, wpc)

sep()
qcur_all = base[base['FollowupStatus'].isin(QUOTED_S)]
qw_all   = base[base['FollowupStatus'].isin(WON_S)]
ql_all   = base[base['FollowupStatus'].isin(['Quoted Order Lost'])]
qa_all   = base[base['FollowupStatus'].isin(ALL_Q_S)]
gt_nqa   = len(qcur_all) + len(qw_all) + len(ql_all)
qt_conv  = round(len(qw_all)/(len(qw_all)+len(ql_all))*100, 1) if (len(qw_all)+len(ql_all))>0 else 0
tc2 = st.columns(W2)
tot_txt(tc2[0],''); tot_txt(tc2[1],'TOTAL')
nbtn(tc2[2], gt_nqa, 't2_gtot', qa_all, "All quoted leads")
for i,s in enumerate(q_stages):
    sd = base[base['FollowupStatus']==s]
    nbtn(tc2[3+i], len(sd), f"t2gs_{i}", sd, f"All — {s}")
nbtn(tc2[3+len(q_stages)], len(qw_all), 't2_gw', qw_all, "All won from quote")
nbtn(tc2[4+len(q_stages)], len(ql_all), 't2_gl', ql_all, "All lost from quote")
tot_txt(tc2[5+len(q_stages)], f"{qt_conv}%", '#1D4ED8')

# ══════════════════════════════════════════════════════════════════════════════
# TABLE 3 — QUOTED LEADS HYGIENE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 3 — Quoted Leads Hygiene — Stale Quoted Deals</div>",
            unsafe_allow_html=True)
st.markdown("<p class='note'>Only leads currently in a quoted stage. "
            "Age = days since LastFollowupedOn. "
            "RAG: 🔴 &gt;60% stuck 7+ days  🟡 30–60%  🟢 &lt;30%</p>", unsafe_allow_html=True)

qcur_base = base[base['FollowupStatus'].isin(QUOTED_S)].copy()
BKTS3 = ['0–7 days','8–15 days','16–30 days','30+ days']
if 'last_fu_age' in qcur_base.columns:
    qcur_base['bkt'] = qcur_base['last_fu_age'].apply(age_bkt3)
else:
    qcur_base['bkt'] = '0–7 days'

W3 = [W_RAG,1.8,0.9]+[0.8]*4
h3 = st.columns(W3)
hdr(h3[0],''); hdr(h3[1],'Rep'); hdr(h3[2],'In Quoted')
for i,b in enumerate(BKTS3): hdr(h3[3+i], b, tip=f"Age from Last Followup: {b}")

hyg3_rows=[]
for rep in rep_order:
    rd = qcur_base[qcur_base['Rep']==rep]; n = len(rd)
    if n==0: continue
    old7 = int((rd['bkt'].isin(['8–15 days','16–30 days','30+ days'])).sum())
    pct7 = round(old7/n*100, 1) if n else 0
    hyg3_rows.append((rep, rd, n, pct7, rag_stale(pct7)))
hyg3_rows.sort(key=lambda x: x[4])

for rep,rd,n,pct7,rs in hyg3_rows:
    c = st.columns(W3)
    rag_cell(c[0], rs); txt(c[1], rep, True, '#0F2044')
    nbtn(c[2], n, f"t3tot_{rep}", rd, f"All quoted — {rep}")
    for i,b in enumerate(BKTS3):
        bd = rd[rd['bkt']==b]
        nbtn(c[3+i], len(bd), f"t3b_{rep}_{i}", bd, f"{b} (quoted) — {rep}")

sep()
tc3 = st.columns(W3); tot_txt(tc3[0],''); tot_txt(tc3[1],'TOTAL')
nbtn(tc3[2], len(qcur_base), 't3_gtot', qcur_base, "All in quoted stage")
for i,b in enumerate(BKTS3):
    bd = qcur_base[qcur_base['bkt']==b]
    nbtn(tc3[3+i], len(bd), f"t3gb_{i}", bd, f"All quoted — {b}")

# ══════════════════════════════════════════════════════════════════════════════
# TABLE 4 — ACTIVE PIPELINE AGING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 4 — Active Pipeline Aging</div>", unsafe_allow_html=True)
st.markdown("<p class='note'>All Open leads. Age = days since Last Followed Up On. "
            "RAG: 🔴 &gt;50% not touched in 7+ days  🟡 25–50%  🟢 &lt;25%</p>",
            unsafe_allow_html=True)

act_base = base[base['Stage']=='Open'].copy()
if 'last_fu_age' in act_base.columns:
    act_base['bkt'] = act_base['last_fu_age'].apply(age_bkt3)
else:
    act_base['bkt'] = '0–7 days'

W4 = [W_RAG,1.8,0.9]+[0.85]*4
h4 = st.columns(W4)
hdr(h4[0],''); hdr(h4[1],'Rep'); hdr(h4[2],'Total Active')
for i,b in enumerate(BKTS3): hdr(h4[3+i], b, tip=f"Days since Last Followed Up On: {b}")

act4_rows=[]
for rep in rep_order:
    rd = act_base[act_base['Rep']==rep]; n = len(rd)
    if n==0: continue
    old7 = int((rd['bkt'].isin(['8–15 days','16–30 days','30+ days'])).sum())
    pct7 = round(old7/n*100, 1) if n else 0
    act4_rows.append((rep, rd, n, pct7, rag_active_age(pct7)))
act4_rows.sort(key=lambda x: x[4])

for rep,rd,n,pct7,rs in act4_rows:
    c = st.columns(W4)
    rag_cell(c[0], rs); txt(c[1], rep, True, '#0F2044')
    nbtn(c[2], n, f"t4tot_{rep}", rd, f"All active — {rep}")
    for i,b in enumerate(BKTS3):
        bd = rd[rd['bkt']==b]
        nbtn(c[3+i], len(bd), f"t4b_{rep}_{i}", bd, f"{b} (active) — {rep}")

sep()
tc4 = st.columns(W4); tot_txt(tc4[0],''); tot_txt(tc4[1],'TOTAL')
nbtn(tc4[2], len(act_base), 't4_gtot', act_base, "All active leads")
for i,b in enumerate(BKTS3):
    bd = act_base[act_base['bkt']==b]
    nbtn(tc4[3+i], len(bd), f"t4gb_{i}", bd, f"All active — {b}")

# ══════════════════════════════════════════════════════════════════════════════
# TABLE 5 — REP × SOURCE CONVERSION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec'>Table 5 — Rep × Source Conversion</div>", unsafe_allow_html=True)
st.markdown("<p class='note'>Total, Won, Lost, Active per source per rep. "
            "RAG on overall Win%. Drill using selector below.</p>", unsafe_allow_html=True)

src_avail = [s for s in MAIN_SRC if base[base['Source_group']==s].shape[0]>0]

rows5=[]
for rep,*_ in sorted([(r, rep_rag_score(r)) for r in rep_order], key=lambda x: x[1]):
    rd = base[base['Rep']==rep]
    nw = int((rd['Stage']=='Won').sum()); nt = len(rd)
    wp = round(nw/nt*100, 1) if nt else 0; rs = rag_win(wp)
    row = {'RAG':RAG[rs], 'Rep':rep}
    for src in src_avail:
        sd = rd[rd['Source_group']==src]
        row[f'{src} Total']  = len(sd)
        row[f'{src} Won']    = int((sd['Stage']=='Won').sum())
        row[f'{src} Lost']   = int((sd['Stage']=='Lost').sum())
        row[f'{src} Active'] = int((sd['Stage']=='Open').sum())
    row['Total']  = nt; row['Won'] = nw
    row['Lost']   = int((rd['Stage']=='Lost').sum())
    row['Active'] = int((rd['Stage']=='Open').sum())
    row['Win %']  = f"{wp}%"
    rows5.append(row)

gt = {'RAG':'', 'Rep':'TOTAL'}
for src in src_avail:
    sd = base[base['Source_group']==src]
    gt[f'{src} Total']  = len(sd)
    gt[f'{src} Won']    = int((sd['Stage']=='Won').sum())
    gt[f'{src} Lost']   = int((sd['Stage']=='Lost').sum())
    gt[f'{src} Active'] = int((sd['Stage']=='Open').sum())
gt['Total'] = total; gt['Won'] = won; gt['Lost'] = lost; gt['Active'] = opn
gt['Win %'] = f"{wr}%"
rows5.append(gt)

df5 = pd.DataFrame(rows5).set_index('Rep')

def sty_t5(df):
    s = pd.DataFrame('', index=df.index, columns=df.columns)
    for src in src_avail:
        wc = f'{src} Won'
        if wc in df.columns:
            s[wc] = df[wc].apply(lambda v:
                'background:#E9F7EF;color:#0A6640;font-weight:700'
                if isinstance(v,(int,float)) and v>0 else 'color:#CBD5E1')
        lc = f'{src} Lost'
        if lc in df.columns:
            s[lc] = df[lc].apply(lambda v:
                'background:#FEF2F2;color:#B91C1C'
                if isinstance(v,(int,float)) and v>0 else '')
    if 'Won' in df.columns:
        s['Won'] = df['Won'].apply(lambda v:
            'background:#E9F7EF;color:#0A6640;font-weight:700'
            if isinstance(v,(int,float)) and v>0 else '')
    if 'Win %' in df.columns:
        s['Win %'] = df['Win %'].apply(lambda v: (
            'background:#E9F7EF;color:#0A6640;font-weight:700'
            if float(v.replace('%',''))>=5 else (
            'background:#FFFBEB;color:#92400E;font-weight:600'
            if float(v.replace('%',''))>=2 else
            'background:#FEF2F2;color:#B91C1C;font-weight:700'))
            if isinstance(v,str) and '%' in v else '')
    if 'TOTAL' in df.index:
        s.loc['TOTAL'] = 'background:#0F2044;color:white;font-weight:800'
    return s

st.dataframe(
    df5.style.set_properties(**{'color':'#0F172A','font-size':'11px'})
       .apply(sty_t5, axis=None)
       .format(lambda x: '—' if isinstance(x,(int,float)) and x==0
               else (f'{x:,}' if isinstance(x,(int,float)) else x)),
    use_container_width=True, height=460)

st.markdown("<p class='note'>Drill into any combination:</p>", unsafe_allow_html=True)
d1,d2,d3,_,d5 = st.columns([2,2,2,2,1.2])
d_rep = d1.selectbox("Rep",    ['All']+rep_order,                key='t5_rep')
d_src = d2.selectbox("Source", ['All']+src_avail,               key='t5_src')
d_stg = d3.selectbox("Stage",  ['All','Won','Open','Lost'],      key='t5_stg')
if d5.button("→ View", key='t5_drill'):
    fd = base.copy()
    if d_rep!='All': fd = fd[fd['Rep']==d_rep]
    if d_src!='All': fd = fd[fd['Source_group']==d_src]
    if d_stg!='All': fd = fd[fd['Stage']==d_stg]
    drill(fd, f"{d_stg} | {d_rep} | {d_src}")
st.download_button("⬇ Download Table 5", df5.to_csv(), "rep_source.csv", "text/csv", key="dl_t5")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{total:,} leads showing  |  {TODAY_NOW.strftime('%d %b %Y')}</p>",
    unsafe_allow_html=True)
