import streamlit as st

from state import load_companies, load_lists

SHARE_BASE_URL = "https://beamish-ganache-be06b1.netlify.app/share.html"

st.title("企業一覧")

companies = load_companies()
lists = load_lists()
list_names = {l["id"]: l["name"] for l in lists}

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

        if assigned_id in list_names:
            share_url = f"{SHARE_BASE_URL}?c={c['id']}"
            st.code(share_url, language=None)

        if c.get("notes"):
            st.caption(c["notes"])
