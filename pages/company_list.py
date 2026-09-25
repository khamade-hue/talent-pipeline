from collections import defaultdict
from datetime import datetime

import streamlit as st

from state import load_companies, load_company_events, load_lists

SHARE_BASE_URL = "https://beamish-ganache-be06b1.netlify.app/share.html"

st.title("企業一覧")

companies = load_companies()
lists = load_lists()
list_names = {l["id"]: l["name"] for l in lists}

events = load_company_events()
last_visit = {}
candidate_view_count = defaultdict(int)
scout_request_count = defaultdict(int)
for e in events:
    cid = e.get("company_id")
    if not cid:
        continue
    if e.get("event_type") == "page_view":
        ts = e.get("created_at")
        if ts and (cid not in last_visit or ts > last_visit[cid]):
            last_visit[cid] = ts
    elif e.get("event_type") == "candidate_view":
        candidate_view_count[cid] += 1
    elif e.get("event_type") == "scout_request":
        scout_request_count[cid] += 1


def format_visit(ts: str | None) -> str:
    if not ts:
        return "未アクセス"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts

col1, col2 = st.columns(2)
col1.metric("総登録数", len(companies))
col2.metric("リスト割り当て済み", sum(1 for c in companies if c.get("assigned_list_id")))

st.divider()

if not companies:
    st.info("まだ企業が登録されていません。「企業登録・リスト割り当て」ページから登録してください。")
    st.stop()

for c in companies:
    with st.container(border=True):
        cols = st.columns([3, 2, 3])
        cols[0].markdown(f"**{c['name']}**")
        cols[1].write(c.get("contact_person") or "担当者未登録")
        assigned_id = c.get("assigned_list_id")
        cols[2].write(f"📋 {list_names[assigned_id]}" if assigned_id in list_names else "(リスト未割り当て)")

        stat_cols = st.columns(3)
        stat_cols[0].metric("直近アクセス", format_visit(last_visit.get(c["id"])))
        stat_cols[1].metric("候補者PV数", candidate_view_count.get(c["id"], 0))
        stat_cols[2].metric("スカウト希望数", scout_request_count.get(c["id"], 0))

        if assigned_id in list_names:
            share_url = f"{SHARE_BASE_URL}?c={c['id']}"
            st.code(share_url, language=None)

        if c.get("notes"):
            st.caption(c["notes"])
