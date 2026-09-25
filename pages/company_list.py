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

@st.dialog("企業詳細")
def detail_dialog(c: dict):
    st.subheader(c["name"])
    st.write(f"**担当者**: {c.get('contact_person') or '未登録'}")

    stat_cols = st.columns(3)
    stat_cols[0].metric("直近アクセス", format_visit(last_visit.get(c["id"])))
    stat_cols[1].metric("候補者PV数", candidate_view_count.get(c["id"], 0))
    stat_cols[2].metric("スカウト希望数", scout_request_count.get(c["id"], 0))

    assigned_id = c.get("assigned_list_id")
    st.write(f"**割り当てリスト**: {list_names[assigned_id] if assigned_id in list_names else '(未割り当て)'}")

    if assigned_id in list_names:
        share_url = f"{SHARE_BASE_URL}?c={c['id']}"
        st.write("**共有URL**")
        st.code(share_url, language=None)

    if c.get("notes"):
        st.write("**メモ**")
        st.write(c["notes"])

    st.caption("リストの割り当て変更は「企業登録・リスト割り当て」ページから行えます。")


header_cols = st.columns([3, 2, 2, 1, 1, 1])
header_labels = ["企業名", "ステータス", "直近アクセス", "候補者PV数", "スカウト希望数", ""]
for col, label in zip(header_cols, header_labels):
    col.caption(label)

for c in companies:
    with st.container(border=True):
        cols = st.columns([3, 2, 2, 1, 1, 1])
        cols[0].markdown(f"**{c['name']}**")
        cols[1].write("リスト割り当て済み" if c.get("assigned_list_id") else "未対応")
        cols[2].write(format_visit(last_visit.get(c["id"])))
        cols[3].write(candidate_view_count.get(c["id"], 0))
        cols[4].write(scout_request_count.get(c["id"], 0))
        if cols[5].button("詳細", key=f"detail_{c['id']}", use_container_width=True):
            detail_dialog(c)
