"""
RAG System — Enterprise Dashboard
Two views: RAG Workspace (query playground) + Ops & Quality Dashboard.
"""

import sys
import os
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests as _requests

st.set_page_config(
    page_title="NeuralRAG — Enterprise Console",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# MASTER STYLESHEET  —  everything that makes it not look like Streamlit
# ══════════════════════════════════════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ━━━━━━━━━━━━━━━━━━━━━━  DESIGN TOKENS  ━━━━━━━━━━━━━━━━━━━━━━ */
:root {
  --bg:          #0F172A;
  --bg2:         #080E1C;
  --s1:          #1E293B;
  --s2:          #162032;
  --s3:          #243044;
  --border:      rgba(255,255,255,0.06);
  --border-hi:   rgba(79,70,229,0.55);
  --indigo:      #4F46E5;
  --indigo-dim:  rgba(79,70,229,0.14);
  --indigo-glow: rgba(79,70,229,0.30);
  --blue:        #3B82F6;
  --blue-dim:    rgba(59,130,246,0.14);
  --cyan:        #06B6D4;
  --cyan-dim:    rgba(6,182,212,0.13);
  --green:       #22C55E;
  --green-dim:   rgba(34,197,94,0.13);
  --amber:       #F59E0B;
  --amber-dim:   rgba(245,158,11,0.13);
  --red:         #EF4444;
  --red-dim:     rgba(239,68,68,0.13);
  --t1:          #F8FAFC;
  --t2:          #CBD5E1;
  --t3:          #64748B;
  --t4:          #334155;
  --r-sm:  8px;
  --r-md:  12px;
  --r-lg:  18px;
  --r-xl:  24px;
  --blur:  blur(18px) saturate(150%);
  --sh-card: 0 4px 24px rgba(0,0,0,0.35);
  --sh-indigo: 0 0 32px rgba(79,70,229,0.18);
}

/* ━━━━━━━━━━━━━━━━━━━━━━  RESET & BASE  ━━━━━━━━━━━━━━━━━━━━━━ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--t1) !important;
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  font-size: 15px;
}

/* ambient background glow */
[data-testid="stApp"]::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse 70% 55% at 15% 0%,   rgba(79,70,229,0.08)  0%, transparent 60%),
    radial-gradient(ellipse 55% 45% at 85% 10%,  rgba(59,130,246,0.06)  0%, transparent 55%),
    radial-gradient(ellipse 45% 35% at 50% 100%, rgba(6,182,212,0.05)   0%, transparent 55%);
}

/* hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; }

/* main content */
.main .block-container {
  position: relative; z-index: 1;
  padding: 1.75rem 2.25rem 5rem !important;
  max-width: 1200px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━  SIDEBAR  ━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

/* brand */
.sb-brand {
  display: flex; align-items: center; gap: 0.65rem;
  padding: 0.25rem 0 1.25rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.75rem;
}
.sb-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #4F46E5, #3B82F6);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 800;
  color: #fff; flex-shrink: 0;
  box-shadow: 0 0 16px rgba(79,70,229,0.4);
}
.sb-name { font-size: 1rem; font-weight: 800; color: var(--t1); letter-spacing: -0.02em; }
.sb-sub  { font-size: 0.6rem; color: var(--t4); letter-spacing: 0.1em; text-transform: uppercase; }

/* section label */
.sb-sec {
  font-size: 0.6rem; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--t4); padding: 0.9rem 0 0.35rem;
}

/* nav radio */
[data-testid="stSidebar"] .stRadio > div { gap: 0.15rem !important; }
[data-testid="stSidebar"] .stRadio label {
  border-radius: var(--r-sm) !important;
  padding: 0.5rem 0.8rem !important;
  font-size: 0.875rem !important; font-weight: 500 !important;
  color: var(--t3) !important;
  transition: all 0.15s !important;
  display: flex; align-items: center; gap: 0.45rem;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: var(--s1) !important; color: var(--t1) !important;
}

/* status pills */
.pill {
  display: inline-flex; align-items: center; gap: 0.38rem;
  font-size: 0.75rem; font-weight: 600;
  padding: 0.25rem 0.7rem; border-radius: 999px;
}
.pill::before { content:''; width:5px; height:5px; border-radius:50%; background:currentColor; }
.pill-green  { background:var(--green-dim); color:var(--green); border:1px solid rgba(34,197,94,0.25); }
.pill-red    { background:var(--red-dim);   color:var(--red);   border:1px solid rgba(239,68,68,0.25); }
.pill-blue   { background:var(--blue-dim);  color:var(--blue);  border:1px solid rgba(59,130,246,0.25); }
.pill-amber  { background:var(--amber-dim); color:var(--amber); border:1px solid rgba(245,158,11,0.25); }
.pill-indigo { background:var(--indigo-dim);color:var(--indigo);border:1px solid rgba(79,70,229,0.25); }

/* ━━━━━━━━━━━━━━━━━━━━━━  PAGE HEADER BAR  ━━━━━━━━━━━━━━━━━━━━━━ */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.75rem; padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}
.page-title { font-size: 1.35rem; font-weight: 800; color: var(--t1); letter-spacing: -0.02em; }
.page-title span {
  background: linear-gradient(135deg, #818CF8, #38BDF8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.page-sub { font-size: 0.8rem; color: var(--t3); margin-top: 0.15rem; }
.page-badges { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.page-badge {
  font-size: 0.68rem; font-weight: 600; color: var(--t3);
  background: var(--s1); border: 1px solid var(--border);
  padding: 0.2rem 0.6rem; border-radius: 999px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━  MODEL SELECTOR BAR  ━━━━━━━━━━━━━━━━━━━━━━ */
.model-bar {
  display: flex; align-items: center; gap: 0.6rem;
  background: var(--s2);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 0.6rem 1rem;
  margin-bottom: 1.25rem;
}
.model-bar-label {
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--t4); white-space: nowrap;
}

/* ━━━━━━━━━━━━━━━━━━━━━━  CARDS  ━━━━━━━━━━━━━━━━━━━━━━ */
.card {
  background: var(--s1);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.35rem;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.card:hover { border-color: var(--border-hi); transform: translateY(-2px); box-shadow: var(--sh-card); }

.glass {
  background: rgba(30,41,59,0.5);
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border); border-radius: var(--r-lg); padding: 1.35rem;
}
.glass:hover { border-color: var(--border-hi); }

/* ━━━━━━━━━━━━━━━━━━━━━━  SECTION LABELS  ━━━━━━━━━━━━━━━━━━━━━━ */
.sec {
  display: flex; align-items: center; gap: 0.5rem;
  margin-bottom: 0.9rem;
}
.sec-icon {
  width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.82rem; flex-shrink: 0;
}
.sec-icon.indigo { background: var(--indigo-dim); box-shadow: 0 0 8px var(--indigo-glow); }
.sec-icon.blue   { background: var(--blue-dim); }
.sec-icon.green  { background: var(--green-dim); }
.sec-icon.amber  { background: var(--amber-dim); }
.sec-icon.cyan   { background: var(--cyan-dim); }
.sec-title { font-size: 0.9rem; font-weight: 700; color: var(--t1); }
.sec-sub   { font-size: 0.72rem; color: var(--t3); margin-top: 0.05rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━  METRIC CARDS  ━━━━━━━━━━━━━━━━━━━━━━ */
.m-row { display: flex; gap: 0.65rem; flex-wrap: wrap; margin-bottom: 1.1rem; }
.m-card {
  flex: 1; min-width: 115px;
  background: var(--s1); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 1rem 1.1rem;
  position: relative; overflow: hidden;
  transition: all 0.2s;
}
.m-card::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--indigo), var(--cyan));
  opacity: 0; transition: opacity 0.2s;
}
.m-card:hover { border-color: var(--border-hi); transform: translateY(-2px); box-shadow: var(--sh-card); }
.m-card:hover::after { opacity: 1; }
.m-lbl { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--t4); margin-bottom: 0.35rem; }
.m-val { font-size: 1.5rem; font-weight: 800; line-height: 1; color: var(--t1); }
.m-val.indigo { color: var(--indigo); }
.m-val.blue   { color: var(--blue); }
.m-val.green  { color: var(--green); }
.m-val.cyan   { color: var(--cyan); }
.m-val.amber  { color: var(--amber); }
.m-sub { font-size: 0.68rem; color: var(--t4); margin-top: 0.2rem; }

/* KPI cards (dashboard) */
.kpi-card {
  background: var(--s1); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 1.2rem 1.3rem;
  transition: all 0.2s;
}
.kpi-card:hover { border-color: var(--border-hi); transform: translateY(-2px); box-shadow: var(--sh-indigo); }
.kpi-lbl { font-size: 0.67rem; font-weight: 600; color: var(--t4); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4rem; }
.kpi-val { font-size: 1.9rem; font-weight: 800; color: var(--t1); line-height: 1; }
.kpi-accent { font-size: 0.72rem; color: var(--green); margin-top: 0.25rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━  CHAT  ━━━━━━━━━━━━━━━━━━━━━━ */
.chat-wrap { display: flex; flex-direction: column; gap: 1.25rem; padding: 0.25rem 0; }

.msg { display: flex; gap: 0.75rem; align-items: flex-start; }
.msg.user { flex-direction: row-reverse; }

.avatar {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; flex-shrink: 0; font-weight: 700;
  letter-spacing: -0.03em;
}
.avatar.ai   { background: linear-gradient(135deg,#4F46E5,#3B82F6); box-shadow:0 0 12px rgba(79,70,229,0.35); color:#fff; }
.avatar.user { background: var(--s3); border: 1px solid var(--border); color: var(--t3); }

.bubble {
  max-width: 72%;
  padding: 0.9rem 1.1rem;
  border-radius: 14px;
  font-size: 0.875rem; line-height: 1.72;
}
.bubble.ai {
  background: var(--s2); border: 1px solid var(--border);
  border-top-left-radius: 4px; color: var(--t1);
}
.bubble.user {
  background: linear-gradient(135deg, rgba(79,70,229,0.18), rgba(59,130,246,0.12));
  border: 1px solid rgba(79,70,229,0.28);
  border-top-right-radius: 4px; color: #C7D2FE;
}
.bubble.refused { background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.2); color:#FCD34D; }
.bubble.error   { background:rgba(239,68,68,0.07);  border:1px solid rgba(239,68,68,0.18); color:#FCA5A5; }

/* response meta row */
.resp-meta {
  display: flex; align-items: center; gap: 0.6rem;
  flex-wrap: wrap; margin-top: 0.5rem; padding: 0 0.15rem;
}
.resp-chip {
  font-size: 0.65rem; font-weight: 600; color: var(--t4);
  background: var(--s1); border: 1px solid var(--border);
  padding: 0.15rem 0.5rem; border-radius: 999px;
}

.msg-ts { font-size: 0.64rem; color: var(--t4); margin-top: 0.3rem; padding: 0 0.15rem; }
.msg.user .msg-ts { text-align: right; }

/* empty state */
.empty-state {
  text-align: center; padding: 3.5rem 2rem;
  background: var(--s2); border: 1px dashed var(--t4);
  border-radius: var(--r-xl); margin: 1rem 0;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.empty-title { font-size: 1.05rem; font-weight: 700; color: var(--t1); margin-bottom: 0.4rem; }
.empty-sub   { font-size: 0.83rem; color: var(--t3); line-height: 1.65; max-width: 360px; margin: 0 auto 1.25rem; }
.empty-hints { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; }
.empty-hint {
  font-size: 0.72rem; color: var(--t3);
  background: var(--s1); border: 1px solid var(--border);
  padding: 0.25rem 0.7rem; border-radius: 999px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━  CITATIONS  ━━━━━━━━━━━━━━━━━━━━━━ */
.cit-list { display: flex; flex-direction: column; gap: 0.55rem; margin-top: 0.2rem; }
.cit-card {
  background: var(--s2); border: 1px solid var(--border);
  border-left: 3px solid var(--indigo);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  padding: 0.8rem 1rem;
  transition: border-left-color 0.18s, transform 0.18s;
}
.cit-card:hover { border-left-color: var(--cyan); transform: translateX(3px); }
.cit-num  { font-size: 0.62rem; font-weight: 700; color: var(--indigo); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem; }
.cit-text { font-size: 0.81rem; color: var(--t2); line-height: 1.6; }
.cit-meta { font-size: 0.67rem; color: var(--t4); margin-top: 0.25rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━  CHUNKS  ━━━━━━━━━━━━━━━━━━━━━━ */
.chunk {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: 0.9rem 1rem;
  font-family: 'JetBrains Mono', monospace; font-size: 0.76rem;
  color: var(--t2); line-height: 1.65;
  white-space: pre-wrap; word-break: break-word;
}

/* ━━━━━━━━━━━━━━━━━━━━━━  DOCUMENT CARDS  ━━━━━━━━━━━━━━━━━━━━━━ */
.doc-card {
  background: var(--s2); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 0.8rem 1rem;
  display: flex; align-items: center; gap: 0.8rem;
  margin-bottom: 0.5rem; transition: all 0.18s;
}
.doc-card:hover { border-color: var(--border-hi); transform: translateX(3px); }
.doc-icon { width: 36px; height: 36px; border-radius: 8px; display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0; }
.doc-icon.pdf { background: var(--red-dim); }
.doc-icon.txt { background: var(--blue-dim); }
.doc-icon.md  { background: var(--indigo-dim); }
.doc-icon.url { background: var(--green-dim); }
.doc-name { font-size:0.83rem; font-weight:600; color:var(--t1); }
.doc-meta { font-size:0.7rem; color:var(--t4); margin-top:0.08rem; }
.doc-badge { margin-left:auto; flex-shrink:0; font-size:0.67rem; font-weight:700; padding:0.18rem 0.55rem; border-radius:999px; background:var(--green-dim); color:var(--green); border:1px solid rgba(34,197,94,0.25); }

/* ━━━━━━━━━━━━━━━━━━━━━━  LOADING  ━━━━━━━━━━━━━━━━━━━━━━ */
.loading-step {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.6rem 0.9rem; background: var(--s2);
  border: 1px solid var(--border); border-radius: var(--r-sm);
  margin-bottom: 0.45rem; font-size: 0.82rem; color: var(--t2);
}
.loading-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--indigo); flex-shrink: 0;
  animation: pulse-dot 1.1s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity:0.3; transform:scale(0.8); }
  50%      { opacity:1;   transform:scale(1.2); box-shadow:0 0 7px var(--indigo); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━  EVAL BADGES  ━━━━━━━━━━━━━━━━━━━━━━ */
.gate-pass { display:inline-flex; align-items:center; gap:0.45rem; background:var(--green-dim); color:var(--green); border:1px solid rgba(34,197,94,0.3); font-size:0.875rem; font-weight:700; padding:0.45rem 1rem; border-radius:999px; margin-bottom:0.9rem; }
.gate-fail { display:inline-flex; align-items:center; gap:0.45rem; background:var(--red-dim);   color:var(--red);   border:1px solid rgba(239,68,68,0.3);  font-size:0.875rem; font-weight:700; padding:0.45rem 1rem; border-radius:999px; margin-bottom:0.9rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━  FOOTER  ━━━━━━━━━━━━━━━━━━━━━━ */
.site-footer {
  margin-top: 4rem; padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
}
.footer-brand { font-size: 0.75rem; font-weight: 700; color: var(--t4); }
.footer-stack { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.footer-chip  { font-size: 0.65rem; color: var(--t4); background: var(--s1); border: 1px solid var(--border); padding: 0.15rem 0.5rem; border-radius: 999px; }

/* ━━━━━━━━━━━━━━━━━━━━━━  WIDGET OVERRIDES  ━━━━━━━━━━━━━━━━━━━━━━ */

/* primary button — indigo gradient */
.stButton > button {
  background: linear-gradient(135deg, #4338CA, #4F46E5) !important;
  color: #fff !important; border: none !important;
  border-radius: 9px !important; font-weight: 600 !important;
  font-size: 0.875rem !important; padding: 0.52rem 1.3rem !important;
  transition: all 0.17s !important;
  box-shadow: 0 2px 8px rgba(79,70,229,0.35) !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover  { transform: translateY(-2px) !important; box-shadow: 0 5px 18px rgba(79,70,229,0.45) !important; }
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
  background: var(--s1) !important; border: 1px solid var(--border) !important;
  color: var(--t2) !important; box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--red) !important; color: var(--red) !important; transform: none !important; }

/* text inputs */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea {
  background: var(--s2) !important; border: 1px solid var(--border) !important;
  border-radius: 9px !important; color: var(--t1) !important;
  font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}
.stTextInput label, .stTextArea label { color: var(--t3) !important; font-size: 0.8rem !important; }

/* the main query textarea — larger */
.query-area textarea {
  font-size: 1rem !important; line-height: 1.6 !important;
  padding: 1rem 1.1rem !important; border-radius: var(--r-md) !important;
  border: 1.5px solid var(--border) !important;
}
.query-area textarea:focus {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

/* selectbox */
.stSelectbox > div > div { background: var(--s2) !important; border: 1px solid var(--border) !important; border-radius: 9px !important; color: var(--t1) !important; }
.stSelectbox label { color: var(--t3) !important; font-size: 0.8rem !important; }

/* slider */
[data-baseweb="slider"] [role="slider"] { background: var(--indigo) !important; border-color: var(--indigo) !important; box-shadow: 0 0 7px var(--indigo-glow) !important; }
.stSlider label { color: var(--t3) !important; font-size: 0.8rem !important; }

/* checkbox */
.stCheckbox label { color: var(--t2) !important; font-size: 0.85rem !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--s2) !important; border-radius: 9px !important; padding: 3px !important; gap: 2px !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 7px !important; color: var(--t4) !important; font-weight: 500 !important; font-size: 0.83rem !important; transition: all 0.15s !important; }
.stTabs [aria-selected="true"] { background: var(--s1) !important; color: var(--t1) !important; box-shadow: 0 1px 4px rgba(0,0,0,0.28) !important; }

/* expander */
.streamlit-expanderHeader { background: var(--s1) !important; border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important; color: var(--t2) !important; font-size: 0.875rem !important; font-weight: 500 !important; transition: border-color 0.15s !important; }
.streamlit-expanderHeader:hover { border-color: var(--border-hi) !important; }
.streamlit-expanderContent { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 var(--r-sm) var(--r-sm) !important; }

/* file uploader */
[data-testid="stFileUploadDropzone"] { background: var(--s2) !important; border: 2px dashed var(--border) !important; border-radius: var(--r-md) !important; transition: all 0.2s !important; }
[data-testid="stFileUploadDropzone"]:hover { border-color: var(--indigo) !important; background: rgba(79,70,229,0.04) !important; }

/* progress */
.stProgress > div > div { background: var(--s1) !important; border-radius: 999px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--indigo), var(--cyan)) !important; border-radius: 999px !important; box-shadow: 0 0 7px rgba(79,70,229,0.4) !important; }

/* alerts */
[data-testid="stAlert"] { border-radius: var(--r-md) !important; font-size: 0.875rem !important; }

/* data table */
[data-testid="stDataFrame"] { border-radius: var(--r-md) !important; overflow: hidden !important; }

/* spinner */
[data-testid="stSpinner"] p { color: var(--indigo) !important; }

/* divider */
hr { border-color: var(--border) !important; }

/* plotly */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--s3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--t4); }

/* fade-in animation */
@keyframes fade-up { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
.fade-up { animation: fade-up 0.35s ease forwards; }

/* ── vdb status pill ── */
.vdb-status {
  display: flex; align-items: center; gap: 0.45rem;
  font-size: 0.74rem; color: var(--t2);
  padding: 0.3rem 0;
}
.vdb-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 7px var(--green);
  flex-shrink: 0;
}

/* ── Answer card wrapper ── */
.answer-card {
  background: var(--s2);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 1.25rem 1.35rem 0.85rem;
}
.answer-meta-bar {
  display: flex; flex-wrap: wrap; gap: 0.4rem;
  margin-top: 0.85rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border);
}
.answer-tag {
  font-size: 0.68rem; font-weight: 600;
  color: var(--t3);
  background: var(--s1);
  border: 1px solid var(--border);
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  white-space: nowrap;
}

/* ── Onboarding tips ── */
.onboarding {
  background: linear-gradient(135deg, rgba(79,70,229,0.07), rgba(59,130,246,0.05));
  border: 1px solid rgba(79,70,229,0.2);
  border-radius: var(--r-md);
  padding: 1.35rem 1.5rem;
  margin-bottom: 1rem;
}
.onboarding-title {
  font-size: 0.72rem; font-weight: 800;
  color: var(--t3); text-transform: uppercase; letter-spacing: 0.1em;
  margin-bottom: 0.8rem;
}
.onboarding-tip {
  display: flex; align-items: flex-start; gap: 0.6rem;
  margin-bottom: 0.65rem;
  font-size: 0.82rem; color: var(--t2); line-height: 1.55;
}
.tip-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: rgba(79,70,229,0.15);
  border: 1px solid rgba(79,70,229,0.3);
  color: #818CF8;
  font-size: 0.64rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 0.1rem;
}

/* ── Citation score + type badge ── */
.cit-badge {
  display: inline-flex; align-items: center;
  font-size: 0.62rem; font-weight: 700;
  padding: 0.1rem 0.45rem; border-radius: 999px;
  margin-left: 0.4rem; vertical-align: middle;
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# perf_history: list of dicts — one record per query with granular stage timings
if "perf_history" not in st.session_state:
    st.session_state.perf_history = []

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND HELPERS  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def _ollama_running() -> bool:
    try:
        r = _requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _available_models() -> list[str]:
    try:
        r = _requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _pull_model(model_name: str):
    try:
        r = _requests.post(
            "http://127.0.0.1:11434/api/pull",
            json={"name": model_name, "stream": False},
            timeout=600,
        )
        return r.status_code == 200
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# UI PRIMITIVES
# ══════════════════════════════════════════════════════════════════════════════

def _pill(label: str, color: str = "blue") -> str:
    return f'<span class="pill pill-{color}">{label}</span>'


# ── Page header (replaces bulky hero) ──────────────────────────────────────
def render_hero(h1_plain: str, h1_grad: str, subtitle: str, tags: list[str], stats=None):
    """Compact, LangSmith-style page header — no giant gradient box."""
    badges = "".join(f'<span class="page-badge">{t}</span>' for t in tags)
    st.markdown(
        f'<div class="page-header fade-up">'
        f'<div>'
        f'<div class="page-title">{h1_plain} <span>{h1_grad}</span></div>'
        f'<div class="page-sub">{subtitle}</div>'
        f'</div>'
        f'<div class="page-badges">{badges}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_section(icon: str, title: str, sub: str = "", color: str = "blue"):
    sub_html = f'<div class="sec-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="sec">'
        f'<div class="sec-icon {color}">{icon}</div>'
        f'<div><div class="sec-title">{title}</div>{sub_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metrics(items: list[dict]):
    cards = ""
    for m in items:
        color = m.get("color", "")
        sub   = f'<div class="m-sub">{m["sub"]}</div>' if m.get("sub") else ""
        cards += (
            f'<div class="m-card">'
            f'<div class="m-lbl">{m["label"]}</div>'
            f'<div class="m-val {color}">{m["value"]}</div>'
            f'{sub}</div>'
        )
    st.markdown(f'<div class="m-row">{cards}</div>', unsafe_allow_html=True)


def render_kpis(items: list[dict]):
    cols = st.columns(len(items))
    for col, k in zip(cols, items):
        accent = k.get("accent", "")
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-lbl">{k["label"]}</div>'
                f'<div class="kpi-val">{k["value"]}</div>'
                f'{"<div class=kpi-accent>" + accent + "</div>" if accent else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_status(online: bool):
    cls   = "green" if online else "red"
    label = "Ollama online" if online else "Ollama offline"
    st.markdown(f'<span class="pill pill-{cls}">{label}</span>', unsafe_allow_html=True)


def render_doc_card(name: str, ext: str, chunks: int, extra: str = ""):
    icons = {"pdf": ("📄","pdf"), "txt": ("📝","txt"), "md": ("✦","md"), "url": ("🔗","url")}
    icon, cls = icons.get(ext.lower().lstrip("."), ("📄","txt"))
    st.markdown(
        f'<div class="doc-card">'
        f'<div class="doc-icon {cls}">{icon}</div>'
        f'<div><div class="doc-name">{name}</div>'
        f'<div class="doc-meta">{chunks} chunks{(" · " + extra) if extra else ""}</div></div>'
        f'<div class="doc-badge">indexed</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_chat_msg(role: str, content: str, ts: str = "", status: str = "normal",
                    meta: dict | None = None):
    if role == "user":
        ts_html = f'<div class="msg-ts">{ts}</div>' if ts else ""
        st.markdown(
            f'<div class="msg user fade-up">'
            f'<div><div class="bubble user">{content}</div>{ts_html}</div>'
            f'<div class="avatar user">You</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        cls    = {"normal": "ai", "refused": "refused", "error": "error"}.get(status, "ai")
        ts_html = f'<div class="msg-ts">{ts}</div>' if ts else ""
        meta_html = ""
        if meta:
            chips = "".join(f'<span class="answer-tag">{k} {v}</span>' for k, v in meta.items())
            meta_html = f'<div class="answer-meta-bar">{chips}</div>'
        if meta_html:
            # Full answer card with meta bar for AI responses that have metadata
            st.markdown(
                f'<div class="msg fade-up">'
                f'<div class="avatar ai">⬡</div>'
                f'<div style="flex:1;min-width:0;">'
                f'<div class="answer-card"><div style="font-size:0.9rem;line-height:1.7;color:var(--t1);">{content}</div>'
                f'{meta_html}</div>'
                f'{ts_html}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg fade-up">'
                f'<div class="avatar ai">⬡</div>'
                f'<div style="flex:1;min-width:0;">'
                f'<div class="bubble {cls}">{content}</div>'
                f'{ts_html}'
                f'</div></div>',
                unsafe_allow_html=True,
            )


def render_empty_state(icon: str, title: str, sub: str, hints: list[str] | None = None):
    hints_html = ""
    if hints:
        hints_html = (
            '<div class="empty-hints">' +
            "".join(f'<span class="empty-hint">{h}</span>' for h in hints) +
            '</div>'
        )
    st.markdown(
        f'<div class="empty-state fade-up">'
        f'<div class="empty-icon">{icon}</div>'
        f'<div class="empty-title">{title}</div>'
        f'<div class="empty-sub">{sub}</div>'
        f'{hints_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_citations(citations: list):
    if not citations:
        return
    render_section("📎", "Citations", f"{len(citations)} sources cited", "indigo")
    items = ""
    _type_colors = {"pdf":"#EF4444","md":"#8B5CF6","txt":"#3B82F6","url":"#10B981"}
    for i, c in enumerate(citations):
        _src  = c.get("source", "Unknown")
        cid   = c.get("chunk_id", "")
        text  = c.get("text", "")[:280]
        score = c.get("score", c.get("rrf_score", c.get("ce_score", None)))
        ext   = str(_src).rsplit(".", 1)[-1].lower()[:5] if "." in str(_src) else "txt"
        tc    = _type_colors.get(ext, "#64748B")
        type_badge = (
            f'<span class="cit-badge" style="background:{tc}22;color:{tc};border:1px solid {tc}44;">'
            f'{ext.upper()}</span>'
        )
        score_badge = (
            f'<span class="cit-badge" style="background:rgba(16,185,129,0.12);'
            f'color:#10B981;border:1px solid rgba(16,185,129,0.25);">'
            f'score {score:.3f}</span>'
            if isinstance(score, float) else ""
        )
        items += (
            f'<div class="cit-card">'
            f'<div class="cit-num">#{i+1} · {_src} · chunk {cid}{type_badge}{score_badge}</div>'
            f'<div class="cit-text">{text}…</div>'
            f'</div>'
        )
    st.markdown(f'<div class="cit-list">{items}</div>', unsafe_allow_html=True)


def render_loading_step(label: str):
    st.markdown(
        f'<div class="loading-step"><div class="loading-dot"></div>{label}</div>',
        unsafe_allow_html=True,
    )


def render_onboarding():
    st.markdown("""
    <div class="onboarding fade-up">
      <div class="onboarding-title">💡 Getting started</div>
      <div class="onboarding-tip">
        <span class="tip-num">1</span>
        Upload a PDF, paste text, or enter a web URL in the <strong>Knowledge Base</strong> panel on the left.
      </div>
      <div class="onboarding-tip">
        <span class="tip-num">2</span>
        Choose your <strong>generation model</strong> from the dropdown — any model you've pulled via Ollama works.
      </div>
      <div class="onboarding-tip">
        <span class="tip-num">3</span>
        Type your question and click <strong>Generate Answer</strong>. Results include citations and source chunks.
      </div>
      <div class="onboarding-tip">
        <span class="tip-num">4</span>
        Check the <strong>⚡ Performance</strong> tab to see stage-by-stage latency for every query.
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="site-footer">
      <div class="footer-brand">RetrievalGPT · Enterprise RAG Platform</div>
      <div class="footer-stack">
        <span class="footer-chip">🧠 Ollama</span>
        <span class="footer-chip">🔷 ChromaDB</span>
        <span class="footer-chip">🔗 LangChain</span>
        <span class="footer-chip">⚡ BM25</span>
        <span class="footer-chip">🎯 Cross-Encoder</span>
        <span class="footer-chip">📐 Ragas</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def dark_plotly(fig, height: int = 300):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(6,12,24,0.8)",
        font=dict(color="#64748B", size=11, family="Inter"),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False, linecolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False, linecolor="rgba(255,255,255,0.06)"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
      <div class="sb-logo">R</div>
      <div>
        <div class="sb-name">RetrievalGPT</div>
        <div class="sb-sub">Enterprise RAG</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["🔍 RAG Workspace", "⚡ Performance", "📊 Ops Dashboard"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sb-sec">System</div>', unsafe_allow_html=True)
    ollama_ok = _ollama_running()
    render_status(ollama_ok)
    if not ollama_ok:
        st.markdown(
            "<p style='font-size:0.75rem;color:#334155;margin-top:0.45rem;line-height:1.6;'>"
            "Start Ollama: <code>ollama serve</code></p>",
            unsafe_allow_html=True,
        )

    # ── Knowledge base quick stats ──────────────────────────────────────────
    try:
        from core.ingestion import get_collection_stats as _gcs
        _ks = _gcs()
        _ndocs   = len(_ks.get("sources", {}))
        _nchunks = _ks["total_chunks"]
        st.markdown(
            f"<div style='margin-top:0.5rem;'>"
            f"<div class='vdb-status'><div class='vdb-dot'></div>ChromaDB · online</div>"
            f"<div style='font-size:0.73rem;color:#475569;margin-top:0.2rem;'>"
            f"<span style='color:#22C55E;font-weight:700;'>{_ndocs}</span> docs"
            f" &nbsp;·&nbsp; "
            f"<span style='color:#3B82F6;font-weight:700;'>{_nchunks}</span> chunks"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            "<div class='vdb-status'>"
            "<div class='vdb-dot' style='background:#EF4444;box-shadow:0 0 6px #EF4444;'></div>"
            "ChromaDB · no data</div>",
            unsafe_allow_html=True,
        )

    # ── Model selector ──────────────────────────────────────────────────────
    st.markdown('<div class="sb-sec">Generation Model</div>', unsafe_allow_html=True)

    # Pull whatever models Ollama knows about right now
    all_models = _available_models()

    # Filter out embedding-only models so they don't accidentally get used for generation
    EMBED_PREFIXES = ("nomic-embed", "mxbai-embed", "all-minilm", "bge-", "e5-")
    chat_models = [m for m in all_models if not any(m.startswith(p) for p in EMBED_PREFIXES)]
    embed_models = [m for m in all_models if any(m.startswith(p) for p in EMBED_PREFIXES)]

    if chat_models:
        selected_model = st.selectbox(
            "Chat / generation model",
            chat_models,
            index=0,
            help="These are the LLMs Ollama has pulled. Used for answer generation.",
        )
    elif all_models:
        # Fallback: show everything if the filter leaves nothing
        selected_model = st.selectbox(
            "Chat / generation model",
            all_models,
            index=0,
            help="All pulled Ollama models.",
        )
    else:
        st.markdown(
            "<p style='font-size:0.78rem;color:#F59E0B;margin:0.4rem 0 0.6rem;'>"
            "⚠️ No models found. Pull one below.</p>",
            unsafe_allow_html=True,
        )
        selected_model = st.text_input(
            "Model name (manual)",
            value="llama3.2",
            help="Type the model name to use once it's pulled.",
        )

    # Embedding models info card (read-only, informational)
    if embed_models:
        st.markdown('<div class="sb-sec">Embedding Models</div>', unsafe_allow_html=True)
        for em in embed_models:
            st.markdown(
                f"<div style='font-size:0.78rem;color:#64748B;padding:0.25rem 0;"
                f"display:flex;align-items:center;gap:0.4rem;'>"
                f"<span style='color:#10B981;'>●</span> {em}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<p style='font-size:0.7rem;color:#334155;margin-top:0.3rem;'>"
            "Used automatically by ChromaDB for indexing — not selectable for chat.</p>",
            unsafe_allow_html=True,
        )

    # Pull a new model
    with st.expander("⬇️ Pull a new model"):
        st.markdown(
            "<p style='font-size:0.75rem;color:#64748B;margin-bottom:0.5rem;'>"
            "Common models: <code>llama3.2</code> · <code>mistral</code> · "
            "<code>gemma2</code> · <code>phi3</code> · <code>nomic-embed-text</code></p>",
            unsafe_allow_html=True,
        )
        pull_name = st.text_input("Model name", value="llama3.2", key="pull_model_name")
        if st.button("Pull model"):
            with st.spinner(f"Pulling {pull_name}… (may take minutes on first run)"):
                ok = _pull_model(pull_name)
            if ok:
                st.success(f"✅ {pull_name} ready")
                st.rerun()
            else:
                st.error("Pull failed — is Ollama running?")

    st.markdown('<div class="sb-sec">Retrieval Settings</div>', unsafe_allow_html=True)
    top_k        = st.slider("Initial retrieval (K)", 5, 20, 10)
    top_k_final  = st.slider("After re-rank (K)", 1, 8, 4)
    skip_sufficiency = st.checkbox("Skip sufficiency check", value=False)

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.68rem;color:#1E293B;text-align:center;letter-spacing:0.05em;'>"
        "HYBRID · BM25 · VECTOR · CROSS-ENCODER</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — RAG WORKSPACE
# ══════════════════════════════════════════════════════════════════════════════

if page == "🔍 RAG Workspace":

    render_hero(
        "Enterprise",
        "RAG Assistant",
        "Query documents with hybrid retrieval · Every answer is cited and verifiable",
        ["PDF", "URL", "Markdown", "BM25 + Vector", "Ollama", "Ragas"],
    )

    if not ollama_ok:
        st.warning("⏳ **Ollama is offline.** Run `ollama serve` then refresh.")

    # ── Two-column layout: ingest left, chat right ─────────────────────────
    left_col, right_col = st.columns([1, 1.6], gap="large")

    with left_col:
        render_section("📚", "Knowledge Base", "Index documents to query", "indigo")
        tab_file, tab_url, tab_paste = st.tabs(
            ["📄 Upload", "🌐 URL", "📋 Paste"]
        )

        with tab_file:
            uploaded = st.file_uploader(
                "Drop PDFs, Markdown, or plain text here",
                type=["pdf", "md", "txt"],
                accept_multiple_files=True,
                help="Supported: .pdf  .md  .txt",
            )
            if uploaded and st.button("⬆️  Embed & index", key="ingest_files"):
                from core.ingestion import ingest_file
                import tempfile
                for f in uploaded:
                    suffix = Path(f.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(f.read())
                        tmp_path = tmp.name
                    with st.spinner(f"Embedding {f.name}…"):
                        result = ingest_file(tmp_path)
                    os.unlink(tmp_path)
                    if result["status"] == "ok":
                        st.success(f"✅ **{f.name}** — {result['chunks']} chunks ({result['new_chunks']} new)")
                    else:
                        st.error(f"❌ {f.name}: {result['message']}")

        with tab_url:
            url_input = st.text_input(
                "Web URL", placeholder="https://example.com/article",
                label_visibility="collapsed",
            )
            if st.button("🌐  Fetch & embed", key="ingest_url"):
                if url_input:
                    from core.ingestion import ingest_url
                    with st.spinner("Fetching and embedding…"):
                        result = ingest_url(url_input)
                    if result["status"] == "ok":
                        st.success(f"✅ {result['source']} — {result['chunks']} chunks")
                    else:
                        st.error(f"❌ {result['message']}")

        with tab_paste:
            pasted_text = st.text_area(
                "Paste content", height=130,
                placeholder="Paste document text to index…",
                label_visibility="collapsed",
            )
            doc_name = st.text_input("Document name", value="pasted_doc.txt")
            if st.button("📋  Embed", key="ingest_text"):
                if pasted_text.strip():
                    from core.ingestion import ingest_text
                    with st.spinner("Embedding…"):
                        result = ingest_text(pasted_text, doc_name)
                    if result["status"] == "ok":
                        st.success(f"✅ {result['chunks']} chunks indexed")
                    else:
                        st.error(f"❌ {result['message']}")

        # ── Knowledge base stats ───────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            from core.ingestion import get_collection_stats
            _kb = get_collection_stats()
            if _kb["total_chunks"] > 0:
                render_metrics([
                    {"label": "Chunks",    "value": str(_kb["total_chunks"]), "color": "blue"},
                    {"label": "Documents", "value": str(len(_kb.get("sources", {}))), "color": "green"},
                    {"label": "BM25",      "value": str(_kb["bm25_chunks"]),  "color": "indigo"},
                ])
                with st.expander("📂  Indexed sources"):
                    for _src, _cnt in _kb.get("sources", {}).items():
                        render_doc_card(_src, Path(_src).suffix.lstrip("."), _cnt)
            else:
                render_empty_state(
                    "📄", "No documents indexed",
                    "Upload a PDF, paste text, or enter a URL to get started.",
                    ["PDF", "Markdown", "TXT", "Web URL"],
                )
        except Exception:
            pass

        st.markdown("---")
        if st.button("🗑  Clear all data", type="secondary"):
            from core.ingestion import clear_all_data
            clear_all_data()
            st.success("Cleared.")
            st.rerun()

    # ── RIGHT COLUMN: model bar + chat + query ─────────────────────────────
    with right_col:

        # Model selector (compact bar)
        _all_m = _available_models()
        _EP = ("nomic-embed", "mxbai-embed", "all-minilm", "bge-", "e5-")
        chat_models_main  = [m for m in _all_m if not any(m.startswith(p) for p in _EP)]
        embed_models_main = [m for m in _all_m if any(m.startswith(p) for p in _EP)]

        _mc1, _mc2 = st.columns([3, 2])
        with _mc1:
            if chat_models_main:
                selected_model = st.selectbox(
                    "🤖 Generation model", chat_models_main, index=0, key="model_main",
                    help="LLM used for answer generation.",
                )
            elif _all_m:
                selected_model = st.selectbox("🤖 Generation model", _all_m, index=0, key="model_main")
            else:
                selected_model = st.text_input(
                    "🤖 Generation model", value="llama3.2", key="model_main",
                    help="Pull a model first: ollama pull llama3.2",
                )
        with _mc2:
            if embed_models_main:
                st.selectbox(
                    "🔡 Embedding model", embed_models_main, index=0,
                    disabled=True, help="Auto-used by ChromaDB.",
                )
            else:
                st.markdown(
                    "<p style='font-size:0.73rem;color:#334155;padding-top:1.85rem;'>"
                    "No embed model</p>", unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Chat history ───────────────────────────────────────────────────
        if st.session_state.chat_history:
            st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                render_chat_msg(
                    msg["role"], msg["content"],
                    ts=msg.get("ts",""), status=msg.get("status","normal"),
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            render_onboarding()
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Query input ────────────────────────────────────────────────────
        render_section("⚡", "Ask a question", "", "indigo")
        query = st.text_area(
            "Question",
            placeholder="e.g. What are the key conclusions in the uploaded report?",
            height=110,
            label_visibility="collapsed",
            key="query_input",
        )
        run_query = st.button("▶  Run Query", type="primary", disabled=not ollama_ok)

    if run_query and query.strip():
        try:
            from core.retrieval import retrieve
            from core.generation import generate
            from observability.tracker import log_trace

            ts_now = time.strftime("%H:%M")
            st.session_state.chat_history.append(
                {"role": "user", "content": query, "ts": ts_now}
            )

            # Animated loading steps
            ph = st.empty()
            with ph.container():
                render_loading_step("🔍  Scanning vector index…")
                render_loading_step("⚡  Running BM25 keyword search…")

            _t0_retrieval = time.perf_counter()
            with st.spinner(""):
                retrieval = retrieve(query, top_k=top_k, top_k_final=top_k_final)
            _retrieval_wall_ms = (time.perf_counter() - _t0_retrieval) * 1000

            with ph.container():
                render_loading_step("🎯  Cross-encoder re-ranking…")

            _t0_gen = time.perf_counter()
            with st.spinner(""):
                generation = generate(
                    query,
                    retrieval["reranked"],
                    model=selected_model,
                    skip_sufficiency_check=skip_sufficiency,
                )
            _gen_wall_ms = (time.perf_counter() - _t0_gen) * 1000

            ph.empty()
            log_trace(generation, retrieval)

            # ── Record granular perf trace into session state ─────────────
            _rt = retrieval.get("timings", {})
            _gt = generation.get("timings", {})
            _context_len = sum(len(c.get("text","")) for c in retrieval.get("reranked", []))
            st.session_state.perf_history.append({
                "ts":         time.strftime("%H:%M:%S"),
                "query":      query,
                "embed_ms":   _rt.get("embed_ms",   _rt.get("embedding_ms", 0)),
                "vector_ms":  _rt.get("vector_ms",  _rt.get("chroma_ms",    0)),
                "bm25_ms":    _rt.get("bm25_ms",    0),
                "rrf_ms":     _rt.get("rrf_ms",     0),
                "prompt_ms":  _gt.get("prompt_ms",  0),
                "llm_ms":     _gt.get("llm_ms",     generation.get("latency_ms", _gen_wall_ms)),
                "total_ms":   generation.get("latency_ms", _retrieval_wall_ms + _gen_wall_ms),
                "n_chunks":   len(retrieval.get("reranked", [])),
                "context_len": _context_len,
                "model":      selected_model,
                "top_k":      top_k,
                "citations":  len(generation.get("citations", [])),
            })

            # Determine status
            if generation.get("error"):
                status = "error"
                answer_text = f"⚠️ Generation error: {generation['error']}"
            elif generation.get("refused"):
                status = "refused"
                answer_text = (
                    "🚫 " + generation["response"] +
                    "\n\n*Insufficient evidence in the retrieved context.*"
                )
            else:
                status = "normal"
                answer_text = generation["response"]

            st.session_state.chat_history.append(
                {"role": "ai", "content": answer_text, "ts": ts_now, "status": status}
            )

            # Render the exchange
            _wc      = len(answer_text.split())
            _ctx_len = sum(len(c.get("text","")) for c in retrieval.get("reranked", []))
            _resp_meta = {
                "⏱": f"{generation['latency_ms']:.0f}ms",
                "📎": f"{len(generation.get('citations',[]))} citations",
                "🔢": f"{generation.get('tokens_output',0)} tokens",
                "📝": f"{_wc} words",
                "📐": f"{_ctx_len:,} ctx chars",
                "🤖": selected_model.split(":")[0],
            }
            st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
            render_chat_msg("user", query, ts=ts_now)
            render_chat_msg("ai", answer_text, ts=ts_now, status=status, meta=_resp_meta)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Metrics ──────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            render_section("⚡", "Response metrics", color="amber")
            render_metrics([
                {"label": "Total latency",  "value": f"{generation['latency_ms']:.0f}ms",               "color": "blue"},
                {"label": "LLM latency",    "value": f"{generation['timings'].get('llm_ms',0):.0f}ms",  "color": "indigo"},
                {"label": "Citations",      "value": str(len(generation.get("citations", []))),          "color": "green"},
                {"label": "Tokens in",      "value": str(generation.get("tokens_input", 0))},
                {"label": "Tokens out",     "value": str(generation.get("tokens_output", 0))},
            ])

            # ── Citations ─────────────────────────────────────────────────
            if generation.get("citations"):
                render_citations(generation["citations"])

            # ── Source tabs ───────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            render_section("📚", "Retrieved sources", color="violet")

            tab_re, tab_vec, tab_bm25, tab_trace = st.tabs([
                f"✨ Re-ranked ({top_k_final})",
                f"🔷 Vector ({top_k})",
                f"🔑 BM25 ({top_k})",
                "🔬 Full trace",
            ])

            with tab_re:
                for i, chunk in enumerate(retrieval.get("reranked", [])):
                    meta = chunk.get("metadata", {})
                    ce   = chunk.get("ce_score", chunk.get("rrf_score", 0))
                    with st.expander(
                        f"[{i+1}] {meta.get('source','?')} · Chunk #{meta.get('chunk_id','?')} · CE {ce:.4f}"
                    ):
                        st.markdown(f'<div class="chunk">{chunk["text"]}</div>', unsafe_allow_html=True)
                        st.caption(f"RRF score: {chunk.get('rrf_score', 0):.4f}")

            with tab_vec:
                for i, chunk in enumerate(retrieval.get("vector_results", [])):
                    meta = chunk.get("metadata", {})
                    with st.expander(
                        f"[{i+1}] {meta.get('source','?')} · similarity {chunk.get('vector_score',0):.4f}"
                    ):
                        st.markdown(f'<div class="chunk">{chunk["text"]}</div>', unsafe_allow_html=True)

            with tab_bm25:
                bm25_chunks = retrieval.get("bm25_results", [])
                if bm25_chunks:
                    for i, chunk in enumerate(bm25_chunks):
                        meta = chunk.get("metadata", {})
                        with st.expander(
                            f"[{i+1}] {meta.get('source','?')} · BM25 {chunk.get('bm25_score',0):.4f}"
                        ):
                            st.markdown(f'<div class="chunk">{chunk["text"]}</div>', unsafe_allow_html=True)
                else:
                    st.info("No BM25 results (index may be empty)")

            with tab_trace:
                st.json({
                    "query":                generation["query"],
                    "model":                generation["model"],
                    "prompt_version":       generation["prompt_version"],
                    "latency_breakdown_ms": generation["timings"],
                    "retrieval_timings_ms": retrieval["timings"],
                    "refused":              generation["refused"],
                    "citations":            generation.get("citations", []),
                    "tokens": {
                        "input":  generation["tokens_input"],
                        "output": generation["tokens_output"],
                    },
                })

        except Exception as e:
            st.error(f"Pipeline error: {e}")
            import traceback
            st.code(traceback.format_exc())

    render_footer()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PERFORMANCE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

elif page == "⚡ Performance":

    render_hero(
        "Pipeline",
        "Performance",
        "Real-time stage-by-stage latency breakdown for every query — "
        "embedding, retrieval, re-ranking, prompt construction, and LLM generation.",
        ["perf_counter", "Stage Timings", "Session History", "Retrieval Metrics", "Observability"],
    )

    history = st.session_state.perf_history

    # ── Summary KPIs ──────────────────────────────────────────────────────
    render_section("📡", "Session summary", color="blue")

    if history:
        totals   = [h["total_ms"]  for h in history]
        llm_all  = [h["llm_ms"]    for h in history]
        ret_all  = [h.get("vector_ms",0) + h.get("bm25_ms",0) for h in history]
        render_kpis([
            {"label": "Queries this session", "value": str(len(history))},
            {"label": "Avg total latency",    "value": f"{sum(totals)/len(totals):.0f}ms"},
            {"label": "Fastest query",         "value": f"{min(totals):.0f}ms",  "accent": "↓ best"},
            {"label": "Slowest query",         "value": f"{max(totals):.0f}ms",  "accent": "↑ worst"},
            {"label": "Avg LLM latency",       "value": f"{sum(llm_all)/len(llm_all):.0f}ms"},
            {"label": "Avg retrieval latency", "value": f"{sum(ret_all)/len(ret_all):.0f}ms"},
        ])
    else:
        st.info("No queries yet — run one in the RAG Workspace to populate this dashboard.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Last query breakdown ───────────────────────────────────────────────
    if history:
        last = history[-1]
        render_section("⏱", "Last query — stage breakdown", color="amber")

        # Timing table card
        stages = [
            ("Embedding",        last.get("embed_ms",  0),  "#3B82F6"),
            ("Semantic search",  last.get("vector_ms", 0),  "#8B5CF6"),
            ("BM25 search",      last.get("bm25_ms",   0),  "#10B981"),
            ("RRF fusion",       last.get("rrf_ms",    0),  "#06B6D4"),
            ("Prompt build",     last.get("prompt_ms", 0),  "#F59E0B"),
            ("LLM generation",   last.get("llm_ms",    0),  "#EC4899"),
        ]
        total_ms = last["total_ms"]

        # Render the timing breakdown table as styled HTML
        rows_html = ""
        for stage, ms, color in stages:
            pct = min(100, (ms / max(total_ms, 1)) * 100)
            bar = (
                f'<div style="height:4px;border-radius:2px;'
                f'background:linear-gradient(90deg,{color},{color}44);'
                f'width:{pct:.1f}%;margin-top:4px;"></div>'
            )
            rows_html += (
                f'<tr>'
                f'<td style="padding:0.6rem 0.5rem;font-size:0.83rem;color:#94A3B8;">{stage}</td>'
                f'<td style="padding:0.6rem 0.5rem;text-align:right;">'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:0.9rem;'
                f'font-weight:700;color:{color};">{ms:.0f} ms</span>'
                f'</td>'
                f'<td style="padding:0.6rem 0.5rem 0.6rem 1rem;width:45%;vertical-align:middle;">'
                f'<div style="background:#1A2740;border-radius:3px;height:6px;">'
                f'<div style="height:6px;border-radius:3px;width:{pct:.1f}%;background:{color};'
                f'box-shadow:0 0 6px {color}66;transition:width 0.4s;"></div>'
                f'</div></td>'
                f'</tr>'
            )

        st.markdown(f"""
        <div style="background:#0D1526;border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:0.5rem 1.25rem 1rem;margin-bottom:1rem;">
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr>
                <th style="padding:0.5rem;text-align:left;font-size:0.65rem;font-weight:700;
                           letter-spacing:0.1em;text-transform:uppercase;color:#475569;
                           border-bottom:1px solid rgba(255,255,255,0.06);">Stage</th>
                <th style="padding:0.5rem;text-align:right;font-size:0.65rem;font-weight:700;
                           letter-spacing:0.1em;text-transform:uppercase;color:#475569;
                           border-bottom:1px solid rgba(255,255,255,0.06);">Time</th>
                <th style="padding:0.5rem 0.5rem 0.5rem 1rem;font-size:0.65rem;font-weight:700;
                           letter-spacing:0.1em;text-transform:uppercase;color:#475569;
                           border-bottom:1px solid rgba(255,255,255,0.06);">Share</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
            <tfoot>
              <tr style="border-top:1px solid rgba(255,255,255,0.08);">
                <td style="padding:0.75rem 0.5rem;font-size:0.83rem;font-weight:700;color:#F1F5F9;">
                  Total end-to-end</td>
                <td style="padding:0.75rem 0.5rem;text-align:right;">
                  <span style="font-family:JetBrains Mono,monospace;font-size:1rem;
                               font-weight:800;color:#3B82F6;">{total_ms:.0f} ms</span>
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
        """, unsafe_allow_html=True)

        # Context + retrieval info
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-lbl">Chunks returned</div>'
                f'<div class="kpi-val" style="color:#8B5CF6;">{last["n_chunks"]}</div></div>',
                unsafe_allow_html=True,
            )
        with rc2:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-lbl">Context length</div>'
                f'<div class="kpi-val" style="color:#10B981;">{last["context_len"]:,}</div>'
                f'<div class="kpi-accent">chars</div></div>',
                unsafe_allow_html=True,
            )
        with rc3:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-lbl">Citations</div>'
                f'<div class="kpi-val" style="color:#F59E0B;">{last["citations"]}</div></div>',
                unsafe_allow_html=True,
            )
        with rc4:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-lbl">Top-K used</div>'
                f'<div class="kpi-val">{last["top_k"]}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Latency waterfall chart ────────────────────────────────────────
        render_section("📊", "Latency waterfall", color="violet")
        colors_map = {
            "Embedding": "#3B82F6", "Semantic search": "#8B5CF6",
            "BM25 search": "#10B981", "RRF fusion": "#06B6D4",
            "Prompt build": "#F59E0B", "LLM generation": "#EC4899",
        }
        stage_names = [s[0] for s in stages]
        stage_vals  = [s[1] for s in stages]
        stage_cols  = [colors_map[s[0]] for s in stages]

        fig_wf = go.Figure(go.Bar(
            x=stage_names,
            y=stage_vals,
            marker_color=stage_cols,
            marker_line_width=0,
            text=[f"{v:.0f}ms" for v in stage_vals],
            textposition="outside",
            textfont=dict(color="#94A3B8", size=11),
        ))
        dark_plotly(fig_wf, height=280)
        fig_wf.update_layout(
            yaxis_title="Latency (ms)",
            bargap=0.35,
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        for i, (name, val, col) in enumerate(zip(stage_names, stage_vals, stage_cols)):
            fig_wf.update_traces(marker=dict(
                color=stage_cols,
                line_width=0,
                opacity=0.9,
            ))
        st.plotly_chart(fig_wf, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Historical latency trend ───────────────────────────────────────────
    if len(history) > 1:
        render_section("📈", "Latency history", color="blue")

        df_h = pd.DataFrame(history)
        df_h.index = range(1, len(df_h) + 1)

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=df_h.index, y=df_h["total_ms"],
            name="Total", line=dict(color="#3B82F6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
            mode="lines+markers", marker=dict(size=5, color="#3B82F6"),
        ))
        fig_hist.add_trace(go.Scatter(
            x=df_h.index, y=df_h["llm_ms"],
            name="LLM", line=dict(color="#EC4899", width=1.5, dash="dot"),
            mode="lines+markers", marker=dict(size=4, color="#EC4899"),
        ))
        fig_hist.add_trace(go.Scatter(
            x=df_h.index, y=df_h["vector_ms"] + df_h["bm25_ms"],
            name="Retrieval", line=dict(color="#10B981", width=1.5, dash="dot"),
            mode="lines+markers", marker=dict(size=4, color="#10B981"),
        ))
        dark_plotly(fig_hist)
        fig_hist.update_layout(
            xaxis_title="Query #",
            yaxis_title="Latency (ms)",
            legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Stage distribution (stacked bar) ──────────────────────────────────
    if len(history) > 1:
        render_section("🔢", "Stage breakdown over queries", color="green")

        df_h = pd.DataFrame(history)
        df_h.index = range(1, len(df_h) + 1)
        labels_q = [f"Q{i}" for i in df_h.index]

        fig_stack = go.Figure()
        for col, label, color in [
            ("embed_ms",  "Embedding",  "#3B82F6"),
            ("vector_ms", "Semantic",   "#8B5CF6"),
            ("bm25_ms",   "BM25",       "#10B981"),
            ("rrf_ms",    "RRF",        "#06B6D4"),
            ("prompt_ms", "Prompt",     "#F59E0B"),
            ("llm_ms",    "LLM",        "#EC4899"),
        ]:
            fig_stack.add_trace(go.Bar(
                name=label,
                x=labels_q,
                y=df_h[col].fillna(0),
                marker_color=color,
                marker_line_width=0,
            ))
        fig_stack.update_layout(barmode="stack")
        dark_plotly(fig_stack, height=260)
        fig_stack.update_layout(
            yaxis_title="ms",
            bargap=0.25,
            legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Observability panel ────────────────────────────────────────────────
    render_section("🔬", "System observability", color="violet")

    obs_col1, obs_col2 = st.columns(2)

    with obs_col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:0.75rem;font-weight:700;color:#64748B;"
            "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;'>"
            "Model Configuration</p>",
            unsafe_allow_html=True,
        )
        try:
            import yaml
            with open(Path(__file__).parent / "config" / "prompts.yaml") as _f:
                _cfg = yaml.safe_load(_f)
            _embed_model = _cfg.get("embedding_model", "nomic-embed-text")
            _llm_model   = _cfg.get("llm_model", history[-1]["model"] if history else "llama3.2")
            _chunk_size  = _cfg.get("chunk_size", "—")
            _chunk_ovlp  = _cfg.get("chunk_overlap", "—")
            _strat       = _cfg.get("retrieval_strategy", "hybrid")
            _topk_cfg    = _cfg.get("top_k", top_k)
        except Exception:
            _embed_model = "nomic-embed-text"
            _llm_model   = history[-1]["model"] if history else "llama3.2"
            _chunk_size  = "—"
            _chunk_ovlp  = "—"
            _strat       = "hybrid"
            _topk_cfg    = top_k

        def _obs_row(label, val, color="#F1F5F9"):
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:0.45rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<span style="font-size:0.8rem;color:#64748B;">{label}</span>'
                f'<span style="font-size:0.82rem;font-weight:600;color:{color};'
                f'font-family:JetBrains Mono,monospace;">{val}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        _obs_row("LLM model",          _llm_model,   "#3B82F6")
        _obs_row("Embedding model",    _embed_model,  "#8B5CF6")
        _obs_row("Chunk size",         str(_chunk_size))
        _obs_row("Chunk overlap",      str(_chunk_ovlp))
        _obs_row("Retrieval strategy", _strat,        "#10B981")
        _obs_row("Top-K (session)",    str(top_k))
        st.markdown('</div>', unsafe_allow_html=True)

    with obs_col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:0.75rem;font-weight:700;color:#64748B;"
            "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;'>"
            "Knowledge Base</p>",
            unsafe_allow_html=True,
        )
        try:
            from core.ingestion import get_collection_stats
            _stats = get_collection_stats()
            _obs_row("Indexed documents", str(len(_stats.get("sources", {}))), "#10B981")
            _obs_row("Total chunks",      str(_stats["total_chunks"]),          "#3B82F6")
            _obs_row("BM25 index size",   str(_stats["bm25_chunks"]),           "#8B5CF6")
            _srcs = _stats.get("sources", {})
            if _srcs:
                _avg_c = sum(_srcs.values()) / len(_srcs)
                _obs_row("Avg chunks/doc", f"{_avg_c:.1f}")
        except Exception:
            _obs_row("Status", "No data yet", "#F59E0B")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Full history table ─────────────────────────────────────────────────
    if history:
        with st.expander("📋  Full query performance log"):
            df_log = pd.DataFrame(history)
            df_log["query"] = df_log["query"].str[:55] + "…"
            df_log = df_log.rename(columns={
                "ts": "Time", "query": "Query",
                "embed_ms": "Embed ms", "vector_ms": "Vector ms",
                "bm25_ms": "BM25 ms", "rrf_ms": "RRF ms",
                "prompt_ms": "Prompt ms", "llm_ms": "LLM ms",
                "total_ms": "Total ms", "n_chunks": "Chunks",
                "context_len": "Ctx chars", "citations": "Citations",
            })
            for c in ["Embed ms","Vector ms","BM25 ms","RRF ms","Prompt ms","LLM ms","Total ms"]:
                if c in df_log.columns:
                    df_log[c] = df_log[c].round(0).astype(int)
            st.dataframe(df_log, use_container_width=True, hide_index=True)

        if st.button("🗑  Clear performance history", type="secondary"):
            st.session_state.perf_history = []
            st.rerun()

    render_footer()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — OPS & QUALITY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Ops Dashboard":

    render_hero(
        "Ops &",
        "Quality Dashboard",
        "Real-time telemetry, latency analytics, cost tracking, and regression evaluation "
        "for your live RAG pipeline.",
        ["Observability", "Eval Suite", "Traces", "CI/CD Gate", "Ragas"],
    )

    try:
        from observability.tracker import (
            get_summary_stats, get_latency_percentiles,
            get_latency_history, get_cost_history, get_eval_history,
            get_recent_traces, clear_traces,
        )

        stats = get_summary_stats()
        perc  = get_latency_percentiles()

        # ── KPI strip ──────────────────────────────────────────────────────
        render_section("📡", "Live KPIs", color="blue")
        render_kpis([
            {"label": "Total Queries",         "value": str(stats["total"])},
            {"label": "P50 Latency",           "value": f"{perc['p50']:.0f}ms"},
            {"label": "P95 Latency",           "value": f"{perc['p95']:.0f}ms"},
            {"label": "Refusal Rate",          "value": f"{stats['refusal_rate']}%"},
            {"label": "Avg Citation Coverage", "value": f"{stats['avg_citation_coverage']}%"},
            {"label": "Cumulative Cost",       "value": f"${stats['total_cost']:.4f}"},
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row 1 ───────────────────────────────────────────────────
        render_section("📈", "Latency & cost", color="violet")
        col_lat, col_cost = st.columns(2)

        with col_lat:
            history = get_latency_history(100)
            if history:
                df_lat = pd.DataFrame(history)
                df_lat["time"] = pd.to_datetime(df_lat["timestamp"], unit="s")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_lat["time"], y=df_lat["latency_ms"],
                    name="Total", line=dict(color="#3B82F6", width=2),
                    fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
                ))
                fig.add_trace(go.Scatter(
                    x=df_lat["time"], y=df_lat["llm_ms"],
                    name="LLM", line=dict(color="#F59E0B", width=1.5, dash="dot"),
                ))
                fig.add_trace(go.Scatter(
                    x=df_lat["time"], y=df_lat["rerank_ms"],
                    name="Re-rank", line=dict(color="#10B981", width=1.5, dash="dot"),
                ))
                p95_val = perc["p95"]
                fig.add_hline(
                    y=p95_val, line_dash="dash", line_color="#EF4444",
                    annotation_text=f"P95 = {p95_val:.0f}ms",
                    annotation_font_color="#EF4444",
                )
                dark_plotly(fig)
                fig.update_layout(xaxis_title="Time", yaxis_title="ms")
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown(
                    "<p style='font-size:0.8rem;font-weight:600;color:#94A3B8;margin-bottom:0.5rem;'>Latency over time</p>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No traces yet — run queries in the Workspace.")

        with col_cost:
            cost_history = get_cost_history(100)
            if cost_history:
                df_cost = pd.DataFrame(cost_history)
                df_cost["time"] = pd.to_datetime(df_cost["timestamp"], unit="s")
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=df_cost["time"], y=df_cost["cumulative_cost"],
                    fill="tozeroy", line=dict(color="#8B5CF6"),
                    fillcolor="rgba(139,92,246,0.08)",
                    name="Cumulative cost",
                ))
                dark_plotly(fig2)
                fig2.update_layout(xaxis_title="Time", yaxis_title="USD")
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown(
                    "<p style='font-size:0.8rem;font-weight:600;color:#94A3B8;margin-bottom:0.5rem;'>Cumulative cost (USD)</p>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig2, use_container_width=True)
                st.caption(
                    "ℹ️ Ollama is free — cost is $0.00 (local inference). "
                    "Update config/prompts.yaml to simulate cloud pricing."
                )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No cost data yet.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row 2 ───────────────────────────────────────────────────
        render_section("🎯", "Quality signals", color="green")
        col_cov, col_err = st.columns(2)

        with col_cov:
            traces = get_recent_traces(100)
            if traces:
                df_tr = pd.DataFrame(traces)
                df_tr["time"] = pd.to_datetime(df_tr["timestamp"], unit="s")
                fig3 = px.line(
                    df_tr, x="time", y="citation_coverage",
                    color_discrete_sequence=["#10B981"],
                )
                dark_plotly(fig3, height=250)
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown(
                    "<p style='font-size:0.8rem;font-weight:600;color:#94A3B8;margin-bottom:0.5rem;'>Citation coverage over time</p>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No traces yet.")

        with col_err:
            if stats["total"] > 0:
                labels = ["Successful", "Refused", "Errors"]
                values = [
                    stats["total"] - stats["refusals"] - stats["errors"],
                    stats["refusals"],
                    stats["errors"],
                ]
                fig4 = go.Figure(go.Pie(
                    labels=labels, values=values, hole=0.52,
                    marker_colors=["#10B981", "#F59E0B", "#EF4444"],
                    textfont=dict(color="#94A3B8", size=11),
                ))
                dark_plotly(fig4, height=250)
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown(
                    "<p style='font-size:0.8rem;font-weight:600;color:#94A3B8;margin-bottom:0.5rem;'>Error & refusal breakdown</p>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig4, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No traces yet.")

        st.markdown("<br>")
        st.markdown("---")

        # ── Evaluation suite ───────────────────────────────────────────────
        render_section("🧪", "Regression evaluation suite",
                        "Runs golden Q&A dataset · scores Faithfulness + Answer Relevancy via Ragas",
                        "violet")

        eval_col1, eval_col2 = st.columns([2, 1])
        with eval_col1:
            eval_model = st.selectbox(
                "Evaluation model",
                _available_models() or ["llama3.2"],
                key="eval_model",
            )
        with eval_col2:
            run_eval = st.button("▶  Run Evaluation Suite", type="primary")

        if run_eval:
            from evaluation.evaluate_pipeline import run_full_evaluation
            progress_bar  = st.progress(0, text="Starting evaluation…")
            result_holder = st.empty()

            def progress_cb(i, total, question):
                pct = int((i / max(total, 1)) * 100)
                progress_bar.progress(pct, text=f"[{i+1}/{total}] {question[:60]}…")

            with st.spinner("Running evaluation — may take a few minutes…"):
                eval_result = run_full_evaluation(model=eval_model, progress_callback=progress_cb)

            progress_bar.empty()

            gate = eval_result["gate_passed"]
            if gate:
                st.markdown('<div class="gate-pass">✅ CI/CD Gate PASSED</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="gate-fail">❌ CI/CD Gate FAILED — REGRESSION DETECTED</div>', unsafe_allow_html=True)
                st.error(
                    f"Faithfulness {eval_result['faithfulness']:.4f} < "
                    f"threshold {eval_result['faithfulness_threshold']} — "
                    "this would block a CI/CD deploy."
                )

            st.markdown("<br>", unsafe_allow_html=True)
            render_metrics([
                {"label": "Faithfulness",     "value": f"{eval_result['faithfulness']:.4f}",     "color": "blue"},
                {"label": "Answer Relevancy", "value": f"{eval_result['answer_relevancy']:.4f}",  "color": "green"},
                {"label": "Answered",         "value": str(eval_result["answered"])},
                {"label": "Refused / Errors", "value": f"{eval_result['refused']} / {eval_result['errors']}", "color": "amber"},
            ])

            if eval_result.get("ragas_error"):
                st.warning(f"Ragas scoring issue: {eval_result['ragas_error']}")

            with st.expander("📋  Sample-level results"):
                for item in eval_result.get("sample_details", []):
                    icon = "🚫" if item.get("refused") else ("⚠️" if item.get("error") else "✅")
                    with st.expander(f"{icon}  {item['question'][:70]}"):
                        st.markdown(f"**Answer:** {item.get('answer','—')}")
                        st.markdown(f"**Latency:** {item.get('latency_ms',0):.0f} ms")

        # ── Eval history ───────────────────────────────────────────────────
        eval_history = get_eval_history(20)
        if eval_history:
            st.markdown("<br>", unsafe_allow_html=True)
            render_section("📉", "Evaluation history", color="blue")
            df_ev = pd.DataFrame(eval_history)
            df_ev["time"] = pd.to_datetime(df_ev["timestamp"], unit="s")
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df_ev["time"], y=df_ev["faithfulness"],
                name="Faithfulness", line=dict(color="#3B82F6", width=2),
                mode="lines+markers", marker=dict(size=5),
            ))
            fig5.add_trace(go.Scatter(
                x=df_ev["time"], y=df_ev["answer_relevancy"],
                name="Answer Relevancy", line=dict(color="#10B981", width=2),
                mode="lines+markers", marker=dict(size=5),
            ))
            import yaml
            with open(Path(__file__).parent / "config" / "prompts.yaml") as f:
                _cfg2 = yaml.safe_load(f)
            threshold = _cfg2["thresholds"]["faithfulness_min"]
            fig5.add_hline(
                y=threshold, line_dash="dash", line_color="#EF4444",
                annotation_text=f"Gate ({threshold})",
                annotation_font_color="#EF4444",
            )
            dark_plotly(fig5)
            fig5.update_layout(yaxis=dict(range=[0, 1.05]))
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")

        # ── Traces table ───────────────────────────────────────────────────
        render_section("🗂", "Recent traces", color="amber")
        traces = get_recent_traces(30)
        if traces:
            df_show = pd.DataFrame(traces)[[
                "timestamp", "query", "latency_ms", "citation_count",
                "refused", "error", "model",
            ]].copy()
            df_show["time"]       = pd.to_datetime(df_show["timestamp"], unit="s").dt.strftime("%H:%M:%S")
            df_show["query"]      = df_show["query"].str[:60] + "…"
            df_show["refused"]    = df_show["refused"].map({0: "No", 1: "Yes"})
            df_show["latency_ms"] = df_show["latency_ms"].round(0).astype(int)
            st.dataframe(
                df_show[["time","query","latency_ms","citation_count","refused","error","model"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No traces recorded yet.")

        if st.button("🗑  Clear all traces", type="secondary"):
            clear_traces()
            st.success("Traces cleared.")
            st.rerun()

    except Exception as e:
        st.error(f"Dashboard error: {e}")
        import traceback
        st.code(traceback.format_exc())

    render_footer()
