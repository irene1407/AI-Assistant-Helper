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

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOKENS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
:root {
  --bg:         #080E1C;
  --surface-1:  #0D1526;
  --surface-2:  #131E32;
  --surface-3:  #1A2740;
  --border:     rgba(255,255,255,0.07);
  --border-hi:  rgba(59,130,246,0.45);
  --blue:       #3B82F6;
  --blue-dim:   rgba(59,130,246,0.15);
  --blue-glow:  rgba(59,130,246,0.35);
  --violet:     #8B5CF6;
  --violet-dim: rgba(139,92,246,0.15);
  --green:      #10B981;
  --green-dim:  rgba(16,185,129,0.15);
  --amber:      #F59E0B;
  --amber-dim:  rgba(245,158,11,0.15);
  --red:        #EF4444;
  --red-dim:    rgba(239,68,68,0.15);
  --text-1:     #F1F5F9;
  --text-2:     #94A3B8;
  --text-3:     #475569;
  --radius-sm:  8px;
  --radius-md:  14px;
  --radius-lg:  20px;
  --radius-xl:  28px;
  --shadow-blue: 0 0 40px rgba(59,130,246,0.12);
  --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
  --blur:       blur(20px) saturate(140%);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BASE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text-1) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

/* animated mesh background */
[data-testid="stApp"]::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 10% 0%,   rgba(59,130,246,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 90% 15%,  rgba(139,92,246,0.06) 0%, transparent 50%),
    radial-gradient(ellipse 50% 40% at 50% 100%, rgba(16,185,129,0.04) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* ── hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; visibility: hidden !important; }

/* ── main content ── */
.main .block-container {
  position: relative;
  z-index: 1;
  padding: 2rem 2.5rem 5rem !important;
  max-width: 1300px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SIDEBAR
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stSidebar"] {
  background: var(--surface-1) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }

.sb-brand {
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.5rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.sb-brand-hex {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
  box-shadow: 0 0 20px rgba(59,130,246,0.3);
  flex-shrink: 0;
}
.sb-brand-name  { font-size: 1.05rem; font-weight: 800; color: var(--text-1); letter-spacing: -0.02em; }
.sb-brand-sub   { font-size: 0.65rem; color: var(--text-3); letter-spacing: 0.08em; text-transform: uppercase; }

.sb-label {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-3);
  padding: 1rem 0 0.4rem;
}

/* radio nav */
[data-testid="stSidebar"] .stRadio > div { gap: 0.2rem !important; }
[data-testid="stSidebar"] .stRadio label {
  border-radius: var(--radius-sm) !important;
  padding: 0.55rem 0.8rem !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  color: var(--text-2) !important;
  transition: all 0.15s !important;
  cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: var(--surface-2) !important;
  color: var(--text-1) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: 0.82rem !important; }

/* status pill */
.pill {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.78rem; font-weight: 600;
  padding: 0.28rem 0.75rem;
  border-radius: 999px;
}
.pill::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.pill-green  { background: var(--green-dim);  color: var(--green);  border: 1px solid rgba(16,185,129,0.3); }
.pill-red    { background: var(--red-dim);    color: var(--red);    border: 1px solid rgba(239,68,68,0.3); }
.pill-blue   { background: var(--blue-dim);   color: var(--blue);   border: 1px solid rgba(59,130,246,0.3); }
.pill-amber  { background: var(--amber-dim);  color: var(--amber);  border: 1px solid rgba(245,158,11,0.3); }
.pill-violet { background: var(--violet-dim); color: var(--violet); border: 1px solid rgba(139,92,246,0.3); }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.hero {
  position: relative;
  background: linear-gradient(140deg, #0a1628 0%, #0e1d3a 40%, #110d2e 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 3rem 3rem 2.5rem;
  margin-bottom: 2rem;
  overflow: hidden;
}
/* glow orbs */
.hero::before {
  content: '';
  position: absolute;
  top: -100px; right: -60px;
  width: 420px; height: 420px;
  background: radial-gradient(circle, rgba(59,130,246,0.16) 0%, transparent 65%);
  animation: orb-drift 8s ease-in-out infinite;
  pointer-events: none;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: -120px; left: -60px;
  width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 65%);
  animation: orb-drift 10s ease-in-out infinite reverse;
  pointer-events: none;
}
@keyframes orb-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%       { transform: translate(20px, -20px) scale(1.05); }
}
.hero-inner { position: relative; z-index: 1; }
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 0.45rem;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--blue);
  background: var(--blue-dim); border: 1px solid rgba(59,130,246,0.25);
  padding: 0.25rem 0.7rem; border-radius: 999px;
  margin-bottom: 1.1rem;
}
.hero-h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--text-1);
  margin-bottom: 0.8rem;
}
.hero-h1 .grad {
  background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 1rem; color: var(--text-2);
  max-width: 560px; line-height: 1.7;
  margin-bottom: 1.6rem;
}
.hero-tags { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.hero-tag {
  font-size: 0.72rem; font-weight: 500;
  color: #93C5FD;
  background: rgba(59,130,246,0.09);
  border: 1px solid rgba(59,130,246,0.2);
  padding: 0.22rem 0.7rem;
  border-radius: 999px;
}
/* right-side stat strip in hero */
.hero-stats {
  position: absolute; right: 2.5rem; top: 50%;
  transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 0.8rem;
  z-index: 1;
}
.hero-stat {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.2rem;
  text-align: center;
  backdrop-filter: var(--blur);
  min-width: 110px;
}
.hero-stat-val { font-size: 1.4rem; font-weight: 800; color: var(--blue); line-height: 1; }
.hero-stat-lbl { font-size: 0.67rem; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover { border-color: var(--border-hi); transform: translateY(-2px); box-shadow: var(--shadow-blue); }

/* glassmorphism variant */
.glass {
  background: rgba(13,21,38,0.6);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
}
.glass:hover { border-color: var(--border-hi); }

/* ── section label ── */
.sec-label {
  display: flex; align-items: center; gap: 0.55rem;
  margin-bottom: 1.1rem;
}
.sec-label-icon {
  width: 30px; height: 30px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.9rem; flex-shrink: 0;
}
.sec-label-icon.blue   { background: var(--blue-dim);   box-shadow: 0 0 10px var(--blue-glow); }
.sec-label-icon.violet { background: var(--violet-dim); }
.sec-label-icon.green  { background: var(--green-dim);  }
.sec-label-icon.amber  { background: var(--amber-dim);  }
.sec-label-text { font-size: 0.95rem; font-weight: 700; color: var(--text-1); }
.sec-label-sub  { font-size: 0.75rem; color: var(--text-3); margin-top: 0.05rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   METRIC CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.metrics-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.m-card {
  flex: 1; min-width: 120px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.1rem 1.2rem;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.m-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-a, var(--blue)), var(--accent-b, var(--violet)));
  opacity: 0;
  transition: opacity 0.2s;
}
.m-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-card); border-color: var(--border-hi); }
.m-card:hover::after { opacity: 1; }
.m-lbl { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--text-3); margin-bottom: 0.4rem; }
.m-val { font-size: 1.55rem; font-weight: 800; line-height: 1; color: var(--text-1); }
.m-val.blue   { color: var(--blue); }
.m-val.green  { color: var(--green); }
.m-val.violet { color: var(--violet); }
.m-val.amber  { color: var(--amber); }
.m-sub { font-size: 0.7rem; color: var(--text-3); margin-top: 0.25rem; }

/* KPI (dashboard) bigger cards */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
.kpi-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.25rem 1.35rem;
  transition: all 0.2s;
  cursor: default;
}
.kpi-card:hover { border-color: var(--border-hi); transform: translateY(-3px); box-shadow: var(--shadow-blue); }
.kpi-lbl { font-size: 0.7rem; font-weight: 600; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.45rem; }
.kpi-val { font-size: 2rem; font-weight: 800; color: var(--text-1); line-height: 1; }
.kpi-accent { font-size: 0.78rem; color: var(--green); margin-top: 0.3rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CHAT  (ChatGPT-style)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.chat-wrap { display: flex; flex-direction: column; gap: 1.5rem; padding: 0.5rem 0; }

.msg { display: flex; gap: 0.85rem; align-items: flex-start; }
.msg.user { flex-direction: row-reverse; }

.avatar {
  width: 34px; height: 34px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.9rem; flex-shrink: 0; font-weight: 700;
}
.avatar.ai   {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  box-shadow: 0 0 14px rgba(59,130,246,0.35);
}
.avatar.user { background: var(--surface-3); border: 1px solid var(--border); color: var(--text-2); }

.bubble {
  max-width: 75%;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.7;
}
.bubble.ai {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
  color: var(--text-1);
}
.bubble.user {
  background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(139,92,246,0.12));
  border: 1px solid rgba(59,130,246,0.25);
  border-top-right-radius: 4px;
  color: #BFDBFE;
}
.bubble.refused {
  background: rgba(245,158,11,0.07);
  border: 1px solid rgba(245,158,11,0.2);
  color: #FCD34D;
}
.bubble.error {
  background: rgba(239,68,68,0.07);
  border: 1px solid rgba(239,68,68,0.18);
  color: #FCA5A5;
}
.msg-ts { font-size: 0.66rem; color: var(--text-3); margin-top: 0.35rem; padding: 0 0.2rem; }
.msg.user .msg-ts { text-align: right; }

/* chat input area */
.chat-input-wrap {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.5rem 0.75rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-top: 0.5rem;
}
.chat-input-wrap:focus-within {
  border-color: var(--border-hi);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CITATIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.citation-list { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.25rem; }
.cit-card {
  background: rgba(13,21,38,0.7);
  border: 1px solid var(--border);
  border-left: 3px solid var(--blue);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 0.85rem 1.1rem;
  transition: border-left-color 0.2s;
}
.cit-card:hover { border-left-color: var(--violet); }
.cit-num  { font-size: 0.65rem; font-weight: 700; color: var(--blue); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.cit-text { font-size: 0.83rem; color: var(--text-2); line-height: 1.6; }
.cit-meta { font-size: 0.7rem; color: var(--text-3); margin-top: 0.3rem; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SOURCE / CHUNK CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.chunk {
  background: #060C18;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1rem 1.1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: var(--text-2);
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DOCUMENT CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.doc-card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 0.9rem 1.1rem;
  display: flex; align-items: center; gap: 0.9rem;
  margin-bottom: 0.55rem;
  transition: all 0.2s;
}
.doc-card:hover { border-color: var(--border-hi); transform: translateX(3px); }
.doc-icon {
  width: 38px; height: 38px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; flex-shrink: 0;
}
.doc-icon.pdf  { background: var(--red-dim); }
.doc-icon.txt  { background: var(--blue-dim); }
.doc-icon.md   { background: var(--violet-dim); }
.doc-icon.url  { background: var(--green-dim); }
.doc-name { font-size: 0.85rem; font-weight: 600; color: var(--text-1); }
.doc-meta { font-size: 0.72rem; color: var(--text-3); margin-top: 0.1rem; }
.doc-badge {
  margin-left: auto; flex-shrink: 0;
  font-size: 0.7rem; font-weight: 700;
  padding: 0.2rem 0.6rem; border-radius: 999px;
  background: var(--green-dim); color: var(--green);
  border: 1px solid rgba(16,185,129,0.25);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LOADING ANIMATION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.loading-step {
  display: flex; align-items: center; gap: 0.65rem;
  padding: 0.65rem 1rem;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 0.5rem;
  font-size: 0.83rem; color: var(--text-2);
}
.loading-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--blue);
  animation: pulse-dot 1.2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse-dot {
  0%,100% { opacity: 0.3; transform: scale(0.85); }
  50%      { opacity: 1;   transform: scale(1.15); box-shadow: 0 0 8px var(--blue); }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EVAL BADGES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.gate-pass {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: var(--green-dim); color: var(--green);
  border: 1px solid rgba(16,185,129,0.3);
  font-size: 0.9rem; font-weight: 700;
  padding: 0.5rem 1.1rem; border-radius: 999px;
  margin-bottom: 1rem;
}
.gate-fail {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: var(--red-dim); color: var(--red);
  border: 1px solid rgba(239,68,68,0.3);
  font-size: 0.9rem; font-weight: 700;
  padding: 0.5rem 1.1rem; border-radius: 999px;
  margin-bottom: 1rem;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOOTER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.site-footer {
  margin-top: 5rem; padding-top: 1.75rem;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
}
.footer-brand { font-size: 0.8rem; font-weight: 700; color: var(--text-3); }
.footer-stack { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.footer-chip {
  font-size: 0.68rem; color: var(--text-3);
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 0.18rem 0.55rem; border-radius: 999px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STREAMLIT WIDGET OVERRIDES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* buttons */
.stButton > button {
  background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  padding: 0.55rem 1.35rem !important;
  transition: all 0.18s !important;
  box-shadow: 0 2px 8px rgba(37,99,235,0.35) !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(59,130,246,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-2) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--red) !important;
  color: var(--red) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* inputs */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea {
  background: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text-1) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
.stTextInput label, .stTextArea label { color: var(--text-2) !important; font-size: 0.82rem !important; }

/* selectbox */
.stSelectbox > div > div {
  background: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text-1) !important;
}
.stSelectbox label { color: var(--text-2) !important; font-size: 0.82rem !important; }

/* slider */
[data-baseweb="slider"] [role="slider"] {
  background: var(--blue) !important;
  border-color: var(--blue) !important;
  box-shadow: 0 0 8px var(--blue-glow) !important;
}
.stSlider label { color: var(--text-2) !important; font-size: 0.82rem !important; }

/* checkbox */
.stCheckbox label { color: var(--text-2) !important; font-size: 0.85rem !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface-2) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 2px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 7px !important;
  color: var(--text-3) !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface-1) !important;
  color: var(--text-1) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}

/* expander */
.streamlit-expanderHeader {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-2) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  transition: border-color 0.15s !important;
}
.streamlit-expanderHeader:hover { border-color: var(--border-hi) !important; }
.streamlit-expanderContent {
  background: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
}

/* file uploader */
[data-testid="stFileUploadDropzone"] {
  background: var(--surface-1) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius-md) !important;
  transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--blue) !important;
  background: rgba(59,130,246,0.04) !important;
}

/* progress bar */
.stProgress > div > div { background: var(--surface-2) !important; border-radius: 999px !important; }
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--blue), var(--violet)) !important;
  border-radius: 999px !important;
  box-shadow: 0 0 8px rgba(59,130,246,0.4) !important;
}

/* alerts */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  font-size: 0.875rem !important;
}

/* data table */
[data-testid="stDataFrame"] { border-radius: var(--radius-md) !important; overflow: hidden !important; }

/* spinner */
[data-testid="stSpinner"] p { color: var(--blue) !important; }

/* divider */
hr { border-color: var(--border) !important; }

/* plotly */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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


def render_hero(h1_plain: str, h1_grad: str, subtitle: str, tags: list[str], stats: list[dict] | None = None):
    stats_html = ""
    if stats:
        items = "".join(
            f'<div class="hero-stat"><div class="hero-stat-val">{s["val"]}</div>'
            f'<div class="hero-stat-lbl">{s["lbl"]}</div></div>'
            for s in stats
        )
        stats_html = f'<div class="hero-stats">{items}</div>'

    tags_html = "".join(f'<span class="hero-tag">{t}</span>' for t in tags)
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="hero-eyebrow">⬡ Enterprise RAG Platform</div>
        <div class="hero-h1">{h1_plain} <span class="grad">{h1_grad}</span></div>
        <p class="hero-sub">{subtitle}</p>
        <div class="hero-tags">{tags_html}</div>
      </div>
      {stats_html}
    </div>
    """, unsafe_allow_html=True)


def render_section(icon: str, title: str, sub: str = "", color: str = "blue"):
    sub_html = f'<div class="sec-label-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="sec-label">
      <div class="sec-label-icon {color}">{icon}</div>
      <div>
        <div class="sec-label-text">{title}</div>
        {sub_html}
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(items: list[dict]):
    """items: [{label, value, color?, sub?}]"""
    cards = ""
    for m in items:
        color = m.get("color", "")
        sub = f'<div class="m-sub">{m["sub"]}</div>' if m.get("sub") else ""
        cards += (
            f'<div class="m-card">'
            f'<div class="m-lbl">{m["label"]}</div>'
            f'<div class="m-val {color}">{m["value"]}</div>'
            f'{sub}</div>'
        )
    st.markdown(f'<div class="metrics-row">{cards}</div>', unsafe_allow_html=True)


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
    cls = "green" if online else "red"
    label = "Ollama online" if online else "Ollama offline"
    st.markdown(f'{_pill(label, cls)}', unsafe_allow_html=True)


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


def render_chat_msg(role: str, content: str, ts: str = "", status: str = "normal"):
    if role == "user":
        ts_html = f'<div class="msg-ts">{ts}</div>' if ts else ""
        st.markdown(
            f'<div class="msg user">'
            f'<div><div class="bubble user">{content}</div>{ts_html}</div>'
            f'<div class="avatar user">You</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        cls = {"normal": "ai", "refused": "refused", "error": "error"}.get(status, "ai")
        ts_html = f'<div class="msg-ts">{ts}</div>' if ts else ""
        st.markdown(
            f'<div class="msg">'
            f'<div class="avatar ai">⬡</div>'
            f'<div><div class="bubble {cls}">{content}</div>{ts_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_citations(citations):
    for c in citations:

        # Backend returns citations as strings
        if isinstance(c, str):
            st.markdown(f"📄 {c}")
            continue

        # Future-proof: also supports dict citations
        src = c.get("source", "Unknown")
        chunk = c.get("chunk_id", "?")

        st.markdown(f"📄 {src} (Chunk {chunk})")

def render_loading_step(label: str):
    st.markdown(
        f'<div class="loading-step">'
        f'<div class="loading-dot"></div>{label}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown("""
    <div class="site-footer">
      <div class="footer-brand">⬡ NeuralRAG · Enterprise Console</div>
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
      <div class="sb-brand-hex">⬡</div>
      <div>
        <div class="sb-brand-name">NeuralRAG</div>
        <div class="sb-brand-sub">Enterprise Console</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["🔍 RAG Workspace", "📊 Ops Dashboard"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sb-label">Ollama Status</div>', unsafe_allow_html=True)
    ollama_ok = _ollama_running()
    render_status(ollama_ok)

    if not ollama_ok:
        st.markdown(
            "<p style='font-size:0.78rem;color:#475569;margin-top:0.5rem;line-height:1.6;'>"
            "Ollama is offline or starting. Start it with <code>ollama serve</code>.</p>",
            unsafe_allow_html=True,
        )

    # ── Model selector — always visible ────────────────────────────────────
    st.markdown('<div class="sb-label">Generation Model</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="sb-label">Embedding Models (detected)</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="sb-label">Retrieval</div>', unsafe_allow_html=True)
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
        "Ask questions across your documents. Every answer is grounded, cited, and verifiable — "
        "powered by hybrid retrieval and cross-encoder re-ranking.",
        ["PDF", "Web URLs", "Markdown", "BM25 + Vector", "Ollama LLM", "Ragas Eval"],
        stats=[
            {"val": "2-stage", "lbl": "Retrieval"},
            {"val": "≤4",      "lbl": "Re-ranked"},
            {"val": "100%",    "lbl": "Cited"},
        ],
    )

    if not ollama_ok:
        st.warning(
            "⏳ **Ollama is starting up.** Models are downloading in the background — "
            "normal on first run. Refresh in a minute."
        )

    # ── Ingest panel ───────────────────────────────────────────────────────
    with st.expander("📂  Knowledge Base — Ingest Documents", expanded=True):
        tab_file, tab_url, tab_paste = st.tabs(
            ["📄  Upload File", "🔗  Web URL", "📋  Paste Text"]
        )

        with tab_file:
            uploaded = st.file_uploader(
                "Drop PDFs, Markdown, or plain text here",
                type=["pdf", "md", "txt"],
                accept_multiple_files=True,
                help="Supported: .pdf  .md  .txt",
            )
            if uploaded and st.button("⬆️  Embed & index files", key="ingest_files"):
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
                        st.success(f"✅ **{f.name}** → {result['chunks']} chunks ({result['new_chunks']} new)")
                    else:
                        st.error(f"❌ {f.name}: {result['message']}")

        with tab_url:
            url_input = st.text_input(
                "Web URL",
                placeholder="https://example.com/article",
                label_visibility="collapsed",
            )
            if st.button("🔗  Fetch & embed URL", key="ingest_url"):
                if url_input:
                    from core.ingestion import ingest_url
                    with st.spinner("Fetching and embedding…"):
                        result = ingest_url(url_input)
                    if result["status"] == "ok":
                        st.success(f"✅ **{result['source']}** → {result['chunks']} chunks")
                    else:
                        st.error(f"❌ {result['message']}")

        with tab_paste:
            pasted_text = st.text_area(
                "Document content",
                height=160,
                placeholder="Paste the document text you want to index…",
                label_visibility="collapsed",
            )
            doc_name = st.text_input("Document name", value="pasted_doc.txt")
            if st.button("📋  Embed text", key="ingest_text"):
                if pasted_text.strip():
                    from core.ingestion import ingest_text
                    with st.spinner("Embedding…"):
                        result = ingest_text(pasted_text, doc_name)
                    if result["status"] == "ok":
                        st.success(f"✅ {result['chunks']} chunks indexed")
                    else:
                        st.error(f"❌ {result['message']}")

        # Stats
        try:
            from core.ingestion import get_collection_stats
            stats = get_collection_stats()
            if stats["total_chunks"] > 0:
                st.markdown("---")
                render_metrics([
                    {"label": "Chunks indexed",  "value": str(stats["total_chunks"]), "color": "blue"},
                    {"label": "Documents",        "value": str(len(stats.get("sources", {}))), "color": "green"},
                    {"label": "BM25 index size",  "value": str(stats["bm25_chunks"]),  "color": "violet"},
                ])
                with st.expander("📂  Source breakdown"):
                    for src, cnt in stats.get("sources", {}).items():
                        render_doc_card(src, Path(src).suffix.lstrip("."), cnt)
        except Exception:
            pass

        st.markdown("---")
        if st.button("🗑  Clear all indexed data", type="secondary"):
            from core.ingestion import clear_all_data
            clear_all_data()
            st.success("All data cleared.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat history ───────────────────────────────────────────────────────
    if st.session_state.chat_history:
        render_section("💬", "Conversation", color="blue")
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            render_chat_msg(
                msg["role"], msg["content"],
                ts=msg.get("ts", ""), status=msg.get("status", "normal"),
            )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Model selector bar ─────────────────────────────────────────────────
    all_models_main = _available_models()
    EMBED_PREFIXES = ("nomic-embed", "mxbai-embed", "all-minilm", "bge-", "e5-")
    chat_models_main = [m for m in all_models_main if not any(m.startswith(p) for p in EMBED_PREFIXES)]
    embed_models_main = [m for m in all_models_main if any(m.startswith(p) for p in EMBED_PREFIXES)]

    st.markdown("""
    <div style="
        background: rgba(13,21,38,0.7);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    ">
        <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#475569;white-space:nowrap;">
            🤖 Active Model
        </div>
    </div>
    """, unsafe_allow_html=True)

    mcol1, mcol2, mcol3 = st.columns([3, 2, 2])
    with mcol1:
        if chat_models_main:
            selected_model = st.selectbox(
                "Generation model",
                chat_models_main,
                index=0,
                key="model_main",
                help="LLM used to generate the answer. Pick any model you've pulled via Ollama.",
            )
        elif all_models_main:
            selected_model = st.selectbox(
                "Generation model",
                all_models_main,
                index=0,
                key="model_main",
            )
        else:
            selected_model = st.text_input(
                "Generation model",
                value="llama3.2",
                key="model_main",
                help="No models found. Pull one with `ollama pull llama3.2` then refresh.",
            )

    with mcol2:
        if embed_models_main:
            st.selectbox(
                "Embedding model (auto)",
                embed_models_main,
                index=0,
                disabled=True,
                help="Used by ChromaDB automatically. Not selectable for chat.",
            )
        else:
            st.markdown(
                "<p style='font-size:0.75rem;color:#475569;padding-top:1.9rem;'>"
                "No embedding model detected</p>",
                unsafe_allow_html=True,
            )

    with mcol3:
        st.markdown(
            "<p style='font-size:0.72rem;color:#475569;margin-top:0.3rem;'>Ollama status</p>",
            unsafe_allow_html=True,
        )
        render_status(ollama_ok)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Query input ────────────────────────────────────────────────────────
    render_section("⚡", "Ask a question", "Your query runs through hybrid retrieval + LLM generation", "blue")

    query = st.text_area(
        "Question",
        placeholder="e.g. What are the key conclusions in the uploaded report?",
        height=100,
        label_visibility="collapsed",
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

            with st.spinner(""):
                retrieval = retrieve(query, top_k=top_k, top_k_final=top_k_final)

            with ph.container():
                render_loading_step("🎯  Cross-encoder re-ranking…")

            with st.spinner(""):
                generation = generate(
                    query,
                    retrieval["reranked"],
                    model=selected_model,
                    skip_sufficiency_check=skip_sufficiency,
                )

            ph.empty()
            log_trace(generation, retrieval)

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
            st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
            render_chat_msg("user", query, ts=ts_now)
            render_chat_msg("ai", answer_text, ts=ts_now, status=status)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Metrics ──────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            render_section("⚡", "Response metrics", color="amber")
            render_metrics([
                {"label": "Total latency",  "value": f"{generation['latency_ms']:.0f}ms",               "color": "blue"},
                {"label": "LLM latency",    "value": f"{generation['timings'].get('llm_ms',0):.0f}ms",  "color": "violet"},
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
# PAGE 2 — OPS & QUALITY DASHBOARD
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
