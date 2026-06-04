import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="MSafe Inside Sales", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{--background-color:#F8FAFC;--text-color:#0F172A;--primary-color:#0F2044;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],
.stApp,.block-container,[data-testid="stMain"]>div{
    background-color:#F8FAFC !important;color:#0F172A !important;}
[data-testid="stMain"] *,.block-container *,
.stMarkdown *,[data-testid="stMarkdownContainer"] *{color:#0F172A !important;}
.stTabs [data-baseweb="tab-list"]{background:#0F2044 !important;border-radius:8px;padding:4px;gap:2px;}
.stTabs [data-baseweb="tab"]{color:#CBD5E1 !important;font-weight:600;font-size:13px;
    border-radius:6px !important;padding:8px 14px !important;}
.stTabs [data-baseweb="tab"]:hover{color:#FFFFFF !important;background:rgba(255,255,255,0.1) !important;}
.stTabs [aria-selected="true"]{color:#0F2044 !important;background:#FFFFFF !important;
    font-weight:700 !important;border-bottom:none !important;}
.stTabs [data-baseweb="tab"] *{color:inherit !important;}
[data-testid="stDownloadButton"] button{
    background:#0F2044 !important;color:white !important;
    border:none !important;border-radius:6px !important;font-weight:600 !important;}
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div,
section[data-testid="stSidebar"]>div:first-child{background:#0F2044 !important;}
section[data-testid="stSidebar"] *{color:white !important;}
section[data-testid="stSidebar"] hr{border-color:#2D5F9E !important;}
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"]>div{
    background:#162955 !important;border:1px solid #2D5F9E !important;border-radius:6px !important;}
section[data-testid="stSidebar"] .stMultiSelect input{color:white !important;caret-color:white !important;}
section[data-testid="stSidebar"] .stMultiSelect [aria-placeholder]{color:#8BAFD4 !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"]{background:#2D5F9E !important;border-radius:4px !important;}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="tag"] svg{color:white !important;fill:white !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{
    background:#162955 !important;border:2px dashed #2D5F9E !important;border-radius:8px !important;}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span{color:#8BAFD4 !important;}
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="input"],
section[data-testid="stSidebar"] .stDateInput div[data-baseweb="base-input"]{
    background:#162955 !important;border:1px solid #2D5F9E !important;border-radius:6px !important;}
section[data-testid="stSidebar"] .stDateInput input{color:white !important;background:#162955 !important;}
.kpi-block{background:white !important;border-radius:10px;padding:14px 10px;
    text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.08);height:84px;
    display:flex;flex-direction:column;justify-content:center;border-top:3px solid #CBD5E1;}
.kpi-label{font-size:10px;color:#475569 !important;font-weight:700;
    text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px;}
.kpi-value{font-size:22px;font-weight:700;color:#0F2044 !important;line-height:1;}
.kpi-value.green{color:#0A6640 !important;}.kpi-value.red{color:#B91C1C !important;}
.kpi-value.amber{color:#92400E !important;}.kpi-value.blue{color:#1D4ED8 !important;}
.sec-hdr{background:#0F2044 !important;color:white !important;padding:9px 18px;
    border-radius:6px;font-weight:700;font-size:13px;margin:14px 0 6px 0;}
.sub-note{font-size:12px !important;color:#475569 !important;font-style:italic;margin:0 0 8px 0;}
[data-testid="stDataFrame"] th,[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"] *{
    background:#1B3A6B !important;color:white !important;
    font-size:12px !important;font-weight:700 !important;}
[data-testid="stDataFrame"] td,[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="gridcell"] *{color:#0F172A !important;font-size:12px !important;}
[data-testid="stDataFrame"] [role="rowheader"],[data-testid="stDataFrame"] [role="rowheader"] *{
    color:#0F172A !important;font-size:12px !important;
    font-weight:600 !important;background:#F1F5F9 !important;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
LOST_S=['Not-Interested','Not Search Our Product','Regret','Other Department Working',
        'Wrong Number','No Response on RNR','Already Purchased','Quoted Order Lost']
WON_S =['Quoted Order Won And Executed']
HIGH_S=['Quoted In Follow Up','Quoted Order In Pipeline','Quote In Progress',
        'Interested Quote Sent','Quoted Not Picking Call','Quoted Project On Hold',
        'Quoted Order Won And Executed','Quoted Order Lost']
RNR_S =['Call Back','RNR Call Back']
ADMIN =['msafe947362','50988-Surbhi']
SRC_MAP={
    'Just Dial':'JustDial','Justdial':'JustDial',
    'Paid clasifieds':'IndiaMart','Paid classifieds':'IndiaMart','Indiamart':'IndiaMart',
    'Exisiting Client Refrence':'Ex-Client Ref.','Existing Client Reference':'Ex-Client Ref.',
    'IVR CALL':'IVR Call','IVR call':'IVR Call',
    'Popup Enquiry':'Website','Webiste':'Website','Product Detail Page':'Website',
    'SEO Landing Pages (Generic)':'Google Ads','Google-Ad (Generic)':'Google Ads',
    'Advertisement':'Other','Aajjo':'Other',
}
MAIN_SOURCES=['JustDial','IndiaMart','IVR Call','Existing Client','Ex-Client Ref.','Facebook','Other']
SRC_SHORT={'JustDial':'JD','IndiaMart':'IM','IVR Call':'IVR',
           'Existing Client':'EC','Ex-Client Ref.':'ECR','Facebook':'FB','Other':'Oth'}
TODAY=pd.Timestamp('2026-06-04')
BASE={'color':'#0F172A','font-size':'12px','font-weight':'500'}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def age_bucket(d):
    if pd.isna(d) or d<0: return '0–7 days'
    if d<=7:  return '0–7 days'
    if d<=15: return '8–15 days'
    if d<=30: return '16–30 days'
    return '30+ days'

def rnr_bucket(d):
    if pd.isna(d) or d<0: return '0–3 days'
    if d<=3:  return '0–3 days'
    if d<=7:  return '4–7 days'
    if d<=15: return '8–15 days'
    return '15+ days'

def c_win(v):
    try:
        p=float(str(v).replace('%',''))
        if p>=5:  return 'background:#E9F7EF;color:#0A6640;font-weight:700'
        if p>=2:  return 'background:#FFFBEB;color:#92400E;font-weight:600'
        if p==0:  return 'background:#FEF2F2;color:#B91C1C;font-weight:700'
        return 'color:#64748B'
    except: return ''

def c_loss(v):
    try:
        p=float(str(v).replace('%',''))
        if p>=70: return 'background:#FEF2F2;color:#B91C1C;font-weight:700'
        if p>=50: return 'background:#FFFBEB;color:#92400E;font-weight:600'
        return 'background:#E9F7EF;color:#0A6640;font-weight:600'
    except: return ''

TOTAL_STYLE='background:#E8EDF5;color:#0F172A;font-weight:800'

def add_total_row(styler, df):
    """Highlight the TOTAL row black bold on light grey."""
    if 'TOTAL' in df.index:
        try:
            styler=styler.apply(
                lambda _:[TOTAL_STYLE]*len(df.columns),
                axis=1,subset=pd.IndexSlice[['TOTAL'],:])
        except: pass
    return styler

def add_total_col(styler, df):
    """Highlight TOTAL column navy-light."""
    if 'TOTAL' in df.columns:
        styler=styler.map(
            lambda v:'background:#EAF0FB;color:#0F2044;font-weight:700',
            subset=['TOTAL'])
    return styler

def show(styler, df, h=480):
    styler=add_total_row(styler,df)
    styler=add_total_col(styler,df)
    return styler

# ── DATA LOAD ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading CRM data…")
def load_data(fb):
    df=pd.read_excel(BytesIO(fb),engine='openpyxl')
    df['Stage']=df['FollowupStatus'].apply(
        lambda x:'Won' if x in WON_S else('Lost' if x in LOST_S else 'Active'))
    df['Source']=df['SourceName'].replace(SRC_MAP)
    df['is_admin']=df['LastFollowupCreatedByName'].isin(ADMIN)
    df['Rep']=df['LastFollowupCreatedByName'].str.replace('50988-','',regex=False)
    df.loc[df['is_admin'],'Rep']='Admin'
    df['Source_group']=df['Source'].apply(lambda x:x if x in MAIN_SOURCES else 'Other')
    if 'CreatedOn' in df.columns:
        df['CreatedOn']=pd.to_datetime(df['CreatedOn'],errors='coerce')
        df['age_days']=(TODAY-df['CreatedOn']).dt.days
    return df

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 MSafe CRM")
st.sidebar.markdown("---")
uploaded=st.sidebar.file_uploader("Upload CRM export (.xls / .xlsx)",type=['xls','xlsx'])

if not uploaded:
    _,mid,_=st.columns([1,2,1])
    with mid:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;padding:48px 24px;background:#FFFFFF;"
            "border-radius:12px;border:1px solid #E2E8F0;'>"
            "<div style='font-size:56px;'>📂</div>"
            "<div style='font-size:22px;font-weight:800;color:#0F2044 !important;"
            "font-family:Arial,sans-serif;margin:16px 0 10px;'>MSafe Inside Sales Dashboard</div>"
            "<div style='font-size:14px;color:#475569;font-family:Arial,sans-serif;'>"
            "Upload your KIT19 CRM export (.xls / .xlsx) from the sidebar.</div>"
            "</div>",unsafe_allow_html=True)
    st.stop()

df_raw=load_data(uploaded.read())
reps_df=df_raw[~df_raw['is_admin']].copy()

st.sidebar.markdown("### Filters")
all_reps=sorted(reps_df['Rep'].dropna().unique().tolist())
sel_reps=st.sidebar.multiselect("Rep",all_reps,default=all_reps)
if 'CreatedOn' in reps_df.columns and reps_df['CreatedOn'].notna().any():
    mn=reps_df['CreatedOn'].min().date(); mx=reps_df['CreatedOn'].max().date()
    dr=st.sidebar.date_input("Date range",[mn,mx],min_value=mn,max_value=mx)
else: dr=None
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Leads in file:** {len(df_raw):,}")

base=reps_df.copy()
if sel_reps: base=base[base['Rep'].isin(sel_reps)]
if dr and len(dr)==2 and 'CreatedOn' in base.columns:
    base=base[(base['CreatedOn'].dt.date>=dr[0])&(base['CreatedOn'].dt.date<=dr[1])]

rep_order=(base.groupby('Rep')['Stage']
           .apply(lambda x:(x=='Won').sum())
           .sort_values(ascending=False).index.tolist())

# ── HEADER + KPIs ─────────────────────────────────────────────────────────────
st.markdown(
    "<div style='background:#0F2044;padding:16px 24px;border-radius:10px;margin-bottom:14px;'>"
    "<span style='color:white !important;font-size:19px;font-weight:700;'>"
    "MSafe Equipments — Inside Sales Dashboard</span>"
    "<span style='color:#8BAFD4;font-size:12px;margin-left:16px;'>KIT19 CRM</span>"
    "</div>",unsafe_allow_html=True)

total=len(base); won=int((base['Stage']=='Won').sum())
lost=int((base['Stage']=='Lost').sum()); active=int((base['Stage']=='Active').sum())
quotes=int(base['FollowupStatus'].isin(HIGH_S).sum())
rnr=int(base['FollowupStatus'].isin(RNR_S).sum())
wr=round(won/total*100,1) if total else 0
q2w=round(won/quotes*100,1) if quotes else 0
ec=base[base['Source']=='Existing Client']
ec_wr=round((ec['Stage']=='Won').sum()/len(ec)*100,1) if len(ec) else 0

kc=st.columns(9)
def kpi(col,label,value,cls=''):
    col.markdown(f"<div class='kpi-block'><div class='kpi-label'>{label}</div>"
                 f"<div class='kpi-value {cls}'>{value}</div></div>",unsafe_allow_html=True)
kpi(kc[0],'Total Leads',f'{total:,}')
kpi(kc[1],'Won',f'{won:,}','green')
kpi(kc[2],'Lost',f'{lost:,}','red')
kpi(kc[3],'Active',f'{active:,}','amber')
kpi(kc[4],'Win Rate',f'{wr}%','blue')
kpi(kc[5],'Quotes Sent',f'{quotes:,}','amber')
kpi(kc[6],'Quote→Win',f'{q2w}%','green')
kpi(kc[7],'Cold RNR',f'{rnr:,}','red')
kpi(kc[8],'EC Win Rate',f'{ec_wr}%','green')
st.markdown("<br>",unsafe_allow_html=True)

t1,t2,t3,t4,t5,t6=st.tabs([
    "📊  Rep × Source",
    "🌐  Source Performance",
    "⏳  Active Lead Aging",
    "❌  Lost Reasons by Rep",
    "🔵  Stage Funnel by Rep",
    "📞  RNR Aging by Rep",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REP × SOURCE
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.markdown("<div class='sec-hdr'>Rep × Source — Leads and Won per Source (with Row & Column Totals)</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>Each source = 2 columns: Leads | Won. Row totals on right. Column totals in TOTAL row.</p>",unsafe_allow_html=True)

    rows=[]
    for rep in rep_order:
        rd=base[base['Rep']==rep]
        row={'Rep':rep}
        for src in MAIN_SOURCES:
            sd=rd[rd['Source_group']==src]; sh=SRC_SHORT[src]
            row[f'{sh} Leads']=len(sd)
            row[f'{sh} Won']=int((sd['Stage']=='Won').sum())
        row['Total Leads']=len(rd)
        row['Total Won']=int((rd['Stage']=='Won').sum())
        row['Total Lost']=int((rd['Stage']=='Lost').sum())
        row['Total Active']=int((rd['Stage']=='Active').sum())
        row['Win %']=f"{round(row['Total Won']/len(rd)*100,1)}%" if len(rd) else '0%'
        rows.append(row)
    tot={'Rep':'TOTAL'}
    for src in MAIN_SOURCES:
        sd=base[base['Source_group']==src]; sh=SRC_SHORT[src]
        tot[f'{sh} Leads']=len(sd)
        tot[f'{sh} Won']=int((sd['Stage']=='Won').sum())
    tot['Total Leads']=total; tot['Total Won']=won
    tot['Total Lost']=lost; tot['Total Active']=active; tot['Win %']=f'{wr}%'
    rows.append(tot)

    df1=pd.DataFrame(rows).set_index('Rep')
    won_cols=[f'{SRC_SHORT[s]} Won' for s in MAIN_SOURCES]+['Total Won']

    sty1=df1.style.set_properties(**BASE)
    # Won cells green
    for col in won_cols:
        if col in df1.columns:
            sty1=sty1.map(
                lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                if isinstance(v,(int,float)) and v>0 else 'color:#94A3B8',
                subset=[col])
    # Total Leads highlight
    if 'Total Leads' in df1.columns:
        sty1=sty1.map(lambda v:'background:#EAF0FB;color:#0F2044;font-weight:700',
                      subset=['Total Leads'])
    # Win %
    if 'Win %' in df1.columns:
        sty1=sty1.map(c_win,subset=['Win %'])
    sty1=add_total_row(sty1,df1)

    st.dataframe(
        sty1.format(lambda x:'' if isinstance(x,(int,float)) and x==0
                    else (f'{x:,}' if isinstance(x,(int,float)) else x)),
        use_container_width=True,height=520)
    st.download_button("⬇ Download CSV",df1.to_csv(),"rep_source.csv","text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SOURCE PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown("<div class='sec-hdr'>Source Performance — Volume, Conversion & Loss</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>Sorted by Win % descending. Which sources give quality leads vs just volume.</p>",unsafe_allow_html=True)

    src_rows=[]
    for src in MAIN_SOURCES:
        sd=base[base['Source_group']==src]
        if len(sd)==0: continue
        n=len(sd); w=int((sd['Stage']=='Won').sum())
        l=int((sd['Stage']=='Lost').sum()); a=int((sd['Stage']=='Active').sum())
        qs=int(sd['FollowupStatus'].isin(HIGH_S).sum())
        rn=int(sd['FollowupStatus'].isin(RNR_S).sum())
        src_rows.append({'Source':src,'Leads':n,
            'Lead %':f'{round(n/total*100,1)}%',
            'Won':w,'Lost':l,'Active':a,
            'Quotes Sent':qs,'Cold RNR':rn,
            'Win %':f'{round(w/n*100,1)}%',
            'Loss %':f'{round(l/n*100,1)}%',
            '_wr':round(w/n*100,1)})
    src_rows.append({'Source':'TOTAL','Leads':total,
        'Lead %':'100%','Won':won,'Lost':lost,'Active':active,
        'Quotes Sent':quotes,'Cold RNR':rnr,
        'Win %':f'{wr}%','Loss %':f'{round(lost/total*100,1)}%','_wr':wr})

    df2=(pd.DataFrame(src_rows)
         .pipe(lambda d:pd.concat([
             d[d['Source']!='TOTAL'].sort_values('_wr',ascending=False),
             d[d['Source']=='TOTAL']]))
         .drop(columns=['_wr']).set_index('Source'))

    sty2=df2.style.set_properties(**BASE)
    sty2=sty2.map(c_win,subset=['Win %'])
    sty2=sty2.map(c_loss,subset=['Loss %'])
    sty2=sty2.map(lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                  if isinstance(v,(int,float)) and v>0 else '',subset=['Won'])
    sty2=add_total_row(sty2,df2)

    st.dataframe(
        sty2.format({'Leads':'{:,}','Won':'{:,}','Lost':'{:,}',
                     'Active':'{:,}','Quotes Sent':'{:,}','Cold RNR':'{:,}'}),
        use_container_width=True,height=420)
    st.download_button("⬇ Download CSV",df2.to_csv(),"source_perf.csv","text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ACTIVE LEAD AGING
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown("<div class='sec-hdr'>Active Lead Aging — How Long Leads Have Been Sitting</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>🟢 0–7 days (fresh)  🟡 8–15 days (needs attention)  🟠 16–30 days (stale)  🔴 30+ days (problem)</p>",unsafe_allow_html=True)

    act_b=base[base['Stage']=='Active'].copy()
    if len(act_b)==0:
        st.info("No active leads.")
    elif 'age_days' not in act_b.columns:
        st.warning("CreatedOn date not in this export — cannot calculate aging.")
    else:
        act_b['bucket']=act_b['age_days'].apply(age_bucket)
        BKTS=['0–7 days','8–15 days','16–30 days','30+ days']
        ag=pd.crosstab(act_b['Rep'],act_b['bucket'],margins=True,margins_name='TOTAL')
        for b in BKTS:
            if b not in ag.columns: ag[b]=0
        col_ord=BKTS+[c for c in ag.columns if c not in BKTS and c!='TOTAL']
        if 'TOTAL' in ag.columns: col_ord.append('TOTAL')
        ag=ag[[c for c in col_ord if c in ag.columns]]

        sty3=ag.style.set_properties(**BASE)
        bucket_styles={
            '0–7 days':  'background:#E9F7EF;color:#0A6640;font-weight:600',
            '8–15 days': 'background:#FFFBEB;color:#92400E;font-weight:600',
            '16–30 days':'background:#FEF3C7;color:#B45309;font-weight:700',
            '30+ days':  'background:#FEF2F2;color:#B91C1C;font-weight:700',
        }
        for bkt,style in bucket_styles.items():
            if bkt in ag.columns:
                sty3=sty3.map(
                    lambda v,s=style:s if isinstance(v,(int,float)) and v>0 else '',
                    subset=[bkt])
        sty3=show(sty3,ag)
        st.dataframe(
            sty3.format(lambda x:'' if isinstance(x,(int,float)) and x==0 else f'{x:,}'),
            use_container_width=True,height=480)
        st.download_button("⬇ Download CSV",ag.to_csv(),"aging.csv","text/csv")

        # Stale % summary
        st.markdown("<div class='sec-hdr'>30+ Day Stale Lead % per Rep</div>",unsafe_allow_html=True)
        sr=[]
        for rep in rep_order:
            rd=act_b[act_b['Rep']==rep]
            if len(rd)==0: continue
            n=len(rd); old=int((rd['bucket']=='30+ days').sum())
            sr.append({'Rep':rep,'Total Active':n,'30+ Days':old,
                'Stale %':f'{round(old/n*100,1)}%','_p':round(old/n*100,1)})
        sd_df=pd.DataFrame(sr).sort_values('_p',ascending=False).drop(columns=['_p']).set_index('Rep')
        sty3b=sd_df.style.set_properties(**BASE)
        sty3b=sty3b.map(lambda v:(
            'background:#FEF2F2;color:#B91C1C;font-weight:700' if float(v.replace('%',''))>=60
            else ('background:#FFFBEB;color:#92400E;font-weight:600' if float(v.replace('%',''))>=30
                  else 'background:#E9F7EF;color:#0A6640;font-weight:600')
            if '%' in str(v) else ''),subset=['Stale %'])
        st.dataframe(sty3b.format({'Total Active':'{:,}','30+ Days':'{:,}'}),
                     use_container_width=True,height=420)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LOST REASONS BY REP
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.markdown("<div class='sec-hdr'>Lost Reasons — Rep-wise Cross-tab</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>Each cell = how many leads that rep lost for that reason. Darker red = higher count relative to column max.</p>",unsafe_allow_html=True)

    lost_b=base[base['Stage']=='Lost']
    if len(lost_b)==0:
        st.info("No lost leads.")
    else:
        lc=pd.crosstab(lost_b['Rep'],lost_b['FollowupStatus'],margins=True,margins_name='TOTAL')
        if 'TOTAL' in lc.columns:
            lc=lc[[c for c in lc.columns if c!='TOTAL']+['TOTAL']]

        sty4=lc.style.set_properties(**BASE)
        for col in [c for c in lc.columns if c!='TOTAL']:
            mx=lc[col].replace(0,np.nan).max()
            if pd.notna(mx) and mx>0:
                def make_fn(m):
                    def fn(v):
                        if not isinstance(v,(int,float)) or v==0: return ''
                        if v>=m*0.6: return 'background:#FEF2F2;color:#B91C1C;font-weight:700'
                        if v>=m*0.3: return 'background:#FEF2F2;color:#B91C1C'
                        return 'color:#B91C1C'
                    return fn
                sty4=sty4.map(make_fn(mx),subset=[col])
        sty4=show(sty4,lc)
        st.dataframe(
            sty4.format(lambda x:'' if isinstance(x,(int,float)) and x==0 else f'{x:,}'),
            use_container_width=True,height=480)
        st.download_button("⬇ Download CSV",lc.to_csv(),"lost_reasons.csv","text/csv")

        # Loss rate summary
        st.markdown("<div class='sec-hdr'>Loss Rate & Top Reason per Rep</div>",unsafe_allow_html=True)
        lr=[]
        for rep in rep_order:
            rd=base[base['Rep']==rep]; ld=rd[rd['Stage']=='Lost']
            n=len(rd); nl=len(ld)
            top=ld['FollowupStatus'].value_counts().index[0] if nl>0 else '—'
            lr.append({'Rep':rep,'Total':n,'Lost':nl,
                'Loss %':f'{round(nl/n*100,1)}%' if n else '0%',
                'Top Reason':top,'_lp':round(nl/n*100,1) if n else 0})
        lr_df=pd.DataFrame(lr).sort_values('_lp',ascending=False).drop(columns=['_lp']).set_index('Rep')
        sty4b=lr_df.style.set_properties(**BASE)
        sty4b=sty4b.map(c_loss,subset=['Loss %'])
        st.dataframe(sty4b.format({'Total':'{:,}','Lost':'{:,}'}),
                     use_container_width=True,height=420)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — STAGE FUNNEL BY REP
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown("<div class='sec-hdr'>Stage Funnel — Where Each Rep's Active Leads Are Right Now</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>🟢 Quoted/Quote stages (high intent)  🟡 Interested/Catalogue (warm)  🔴 Call Back/RNR (cold)</p>",unsafe_allow_html=True)

    act5=base[base['Stage']=='Active']
    if len(act5)==0:
        st.info("No active leads.")
    else:
        fc=pd.crosstab(act5['Rep'],act5['FollowupStatus'],margins=True,margins_name='TOTAL')
        cold_c=[c for c in fc.columns if 'Call Back' in c or 'RNR' in c]
        hot_c =[c for c in fc.columns if any(x in c for x in ['Quoted','Quote']) and c!='TOTAL']
        warm_c=[c for c in fc.columns if c not in cold_c+hot_c+['TOTAL']]
        col_o=cold_c+warm_c+hot_c+[c for c in fc.columns if c not in cold_c+warm_c+hot_c+['TOTAL']]
        if 'TOTAL' in fc.columns: col_o.append('TOTAL')
        fc=fc[[c for c in col_o if c in fc.columns]]

        sty5=fc.style.set_properties(**BASE)
        if cold_c:
            sty5=sty5.map(lambda v:'background:#FEF2F2;color:#B91C1C;font-weight:700'
                          if isinstance(v,(int,float)) and v>0 else '',
                          subset=[c for c in cold_c if c in fc.columns])
        if hot_c:
            sty5=sty5.map(lambda v:'background:#E9F7EF;color:#0A6640;font-weight:700'
                          if isinstance(v,(int,float)) and v>0 else '',
                          subset=[c for c in hot_c if c in fc.columns])
        if warm_c:
            sty5=sty5.map(lambda v:'background:#FFFBEB;color:#92400E'
                          if isinstance(v,(int,float)) and v>0 else '',
                          subset=[c for c in warm_c if c in fc.columns])
        sty5=show(sty5,fc)
        st.dataframe(
            sty5.format(lambda x:'' if isinstance(x,(int,float)) and x==0 else f'{x:,}'),
            use_container_width=True,height=480)
        st.download_button("⬇ Download CSV",fc.to_csv(),"funnel.csv","text/csv")

        # Summary
        st.markdown("<div class='sec-hdr'>Funnel Quality Summary per Rep</div>",unsafe_allow_html=True)
        fs=[]
        for rep in rep_order:
            rd=act5[act5['Rep']==rep]; n=len(rd)
            if n==0: continue
            cn=int(rd['FollowupStatus'].isin(cold_c).sum())
            hn=int(rd['FollowupStatus'].isin(hot_c).sum())
            wn=n-cn-hn
            fs.append({'Rep':rep,'Active':n,
                'Cold CB/RNR':f'{cn} ({round(cn/n*100,1)}%)',
                'High Intent':f'{hn} ({round(hn/n*100,1)}%)',
                'Warm':f'{wn} ({round(wn/n*100,1)}%)',
                '_hp':round(hn/n*100,1),'_cp':round(cn/n*100,1)})
        fs_df=pd.DataFrame(fs).sort_values('_hp',ascending=False)
        fs_disp=fs_df.drop(columns=['_hp','_cp']).set_index('Rep')
        sty5b=fs_disp.style.set_properties(**BASE)
        for i,row in fs_df.iterrows():
            pass  # just use map below
        sty5b=sty5b.map(lambda v:
            'background:#FEF2F2;color:#B91C1C;font-weight:700'
            if v and '(' in str(v) and float(str(v).split('(')[1].replace('%)','').replace('%','').strip())>=60
            else '',subset=['Cold CB/RNR'])
        sty5b=sty5b.map(lambda v:
            'background:#E9F7EF;color:#0A6640;font-weight:700'
            if v and '(' in str(v) and float(str(v).split('(')[1].replace('%)','').replace('%','').strip())>=15
            else '',subset=['High Intent'])
        st.dataframe(sty5b.format({'Active':'{:,}'}),use_container_width=True,height=420)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — RNR AGING BY REP
# ══════════════════════════════════════════════════════════════════════════════
with t6:
    st.markdown("<div class='sec-hdr'>RNR & Call Back Aging — How Long Stuck Leads Have Been Waiting</div>",unsafe_allow_html=True)
    st.markdown("<p class='sub-note'>🟡 0–3 days (normal)  🟠 4–7 days (call again)  🔴 8–15 days (overdue)  🚨 15+ days (abandon or escalate)</p>",unsafe_allow_html=True)

    rnr_b=base[base['FollowupStatus'].isin(RNR_S)].copy()
    if len(rnr_b)==0:
        st.info("No RNR/Call Back leads.")
    elif 'age_days' not in rnr_b.columns:
        st.warning("CreatedOn not available — cannot calculate RNR aging.")
    else:
        rnr_b['bucket']=rnr_b['age_days'].apply(rnr_bucket)
        RBKTS=['0–3 days','4–7 days','8–15 days','15+ days']
        ra=pd.crosstab(rnr_b['Rep'],rnr_b['bucket'],margins=True,margins_name='TOTAL')
        for b in RBKTS:
            if b not in ra.columns: ra[b]=0
        co2=RBKTS+[c for c in ra.columns if c not in RBKTS and c!='TOTAL']
        if 'TOTAL' in ra.columns: co2.append('TOTAL')
        ra=ra[[c for c in co2 if c in ra.columns]]

        rnr_styles={
            '0–3 days': 'background:#FFFBEB;color:#92400E;font-weight:600',
            '4–7 days': 'background:#FEF3C7;color:#B45309;font-weight:700',
            '8–15 days':'background:#FEF2F2;color:#B91C1C;font-weight:700',
            '15+ days': 'background:#7F1D1D;color:white;font-weight:700',
        }
        sty6=ra.style.set_properties(**BASE)
        for bkt,style in rnr_styles.items():
            if bkt in ra.columns:
                sty6=sty6.map(
                    lambda v,s=style:s if isinstance(v,(int,float)) and v>0 else '',
                    subset=[bkt])
        sty6=show(sty6,ra)
        st.dataframe(
            sty6.format(lambda x:'' if isinstance(x,(int,float)) and x==0 else f'{x:,}'),
            use_container_width=True,height=480)
        st.download_button("⬇ Download CSV",ra.to_csv(),"rnr_aging.csv","text/csv")

        # Severity summary
        st.markdown("<div class='sec-hdr'>RNR Severity — Who Has the Most Stuck Leads</div>",unsafe_allow_html=True)
        rr=[]
        for rep in rep_order:
            rd=rnr_b[rnr_b['Rep']==rep]; n=len(rd)
            if n==0: continue
            tot_rep=len(base[base['Rep']==rep])
            old=int((rd['bucket']=='15+ days').sum())
            med=int((rd['bucket']=='8–15 days').sum())
            act_rep=int(len(base[(base['Rep']==rep)&(base['Stage']=='Active')]))
            rr.append({'Rep':rep,'Total Active':act_rep,'In RNR/CB':n,
                'RNR %':f'{round(n/tot_rep*100,1)}%' if tot_rep else '0%',
                '8–15 days':med,'15+ days':old,
                '_old':old,'_rp':round(n/tot_rep*100,1) if tot_rep else 0})
        rr_df=pd.DataFrame(rr).sort_values('_old',ascending=False)
        rr_disp=rr_df.drop(columns=['_old','_rp']).set_index('Rep')
        sty6b=rr_disp.style.set_properties(**BASE)
        sty6b=sty6b.map(lambda v:'background:#7F1D1D;color:white;font-weight:700'
                        if isinstance(v,(int,float)) and v>20
                        else ('background:#FEF2F2;color:#B91C1C;font-weight:700'
                              if isinstance(v,(int,float)) and v>5 else ''),
                        subset=['15+ days'])
        sty6b=sty6b.map(c_loss,subset=['RNR %'])
        st.dataframe(
            sty6b.format({'Total Active':'{:,}','In RNR/CB':'{:,}',
                          '8–15 days':'{:,}','15+ days':'{:,}'}),
            use_container_width=True,height=420)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#94A3B8;font-size:11px;'>"
    f"MSafe Equipments  |  KIT19 CRM  |  {len(df_raw):,} leads in file  |  "
    f"{len(base):,} leads shown with current filters</p>",unsafe_allow_html=True)
