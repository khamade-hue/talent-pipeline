import streamlit as st

from state import (
    INTENT_OPTIONS,
    STATUS_OPTIONS,
    delete_candidate,
    get_resume_url,
    load_candidates,
    update_candidate,
)


def label(c: dict) -> str:
    return f"{c.get('name') or '(未入力)'} ・ {c.get('current_company') or '現職不明'} ・ {c.get('sales_type') or ''}"


@st.dialog("候補者詳細", width="large")
def detail_dialog(c: dict):
    st.subheader(label(c))
    cols = st.columns(3)
    cols[0].metric("年齢", c.get("age") or "-")
    cols[1].metric("経験年数", f"{c.get('years_experience')}年" if c.get("years_experience") else "-")
    cols[2].metric("現年収", f"{c.get('current_salary')}万円" if c.get("current_salary") else "-")

    st.write(f"**メール**: {c.get('email') or '-'} / **電話**: {c.get('phone') or '-'}")
    st.write(f"**居住エリア**: {c.get('area') or '-'} / **業界**: {c.get('industry') or '-'}")
    st.write(f"**商材の特徴**: {'、'.join(c.get('product_traits') or []) or '-'}")
    st.write(f"**マネジメント経験**: {'あり' if c.get('has_management_exp') else 'なし'}")
    st.write("**実績概要**")
    st.write(c.get("achievements") or "-")

    st.divider()
    st.write(f"**転職意欲**: {c.get('intent_level') or '-'} / **希望年収**: {c.get('desired_salary') or '-'}")
    st.write(f"**希望勤務地**: {'、'.join(c.get('desired_location') or []) or '-'}")
    st.write(f"**興味のある業界**: {'、'.join(c.get('desired_industries') or []) or '-'}")
    st.write(f"**興味のある職種**: {'、'.join(c.get('interested_roles') or []) or '-'}")
    st.write(f"**希望条件**: {'、'.join(c.get('desired_conditions') or []) or '-'}")

    if c.get("resume_path"):
        url = get_resume_url(c["resume_path"])
        if url:
            st.link_button("履歴書を開く", url)
    else:
        st.caption("履歴書ファイルなし")

    st.divider()
    st.write("**社内管理**")
    status_idx = STATUS_OPTIONS.index(c.get("status")) if c.get("status") in STATUS_OPTIONS else 0
    new_status = st.selectbox("ステータス", STATUS_OPTIONS, index=status_idx, key=f"status_{c['id']}")
    assignee = st.text_input("担当者", value=c.get("assignee") or "", key=f"assignee_{c['id']}")
    notes = st.text_area("スタッフメモ", value=c.get("staff_notes") or "", key=f"notes_{c['id']}")

    col_save, col_delete = st.columns([3, 1])
    if col_save.button("保存する", type="primary", use_container_width=True):
        update_candidate(c["id"], {"status": new_status, "assignee": assignee, "staff_notes": notes})
        st.session_state["selected_candidate"] = None
        st.rerun()
    if col_delete.button("削除", use_container_width=True):
        delete_candidate(c["id"])
        st.session_state["selected_candidate"] = None
        st.rerun()


st.title("候補者一覧")

candidates = load_candidates()

counts = {s: 0 for s in STATUS_OPTIONS}
for c in candidates:
    if c.get("status") in counts:
        counts[c["status"]] += 1
stat_cols = st.columns(len(STATUS_OPTIONS) + 1)
stat_cols[0].metric("総登録数", len(candidates))
for i, s in enumerate(STATUS_OPTIONS):
    stat_cols[i + 1].metric(s, counts[s])

st.divider()

col1, col2, col3 = st.columns([2, 1, 1])
query = col1.text_input("検索(氏名・現職)")
status_filter = col2.selectbox("ステータス", ["すべて"] + STATUS_OPTIONS)
intent_filter = col3.selectbox("転職意欲", ["すべて"] + INTENT_OPTIONS)

filtered = candidates
if query:
    q = query.lower()
    filtered = [
        c
        for c in filtered
        if q in (c.get("name") or "").lower() or q in (c.get("current_company") or "").lower()
    ]
if status_filter != "すべて":
    filtered = [c for c in filtered if c.get("status") == status_filter]
if intent_filter != "すべて":
    filtered = [c for c in filtered if c.get("intent_level") == intent_filter]

st.caption(f"{len(filtered)}件 / 全{len(candidates)}件")

if not filtered:
    st.info("該当する候補者がいません。")

for c in filtered:
    with st.container(border=True):
        cols = st.columns([3, 2, 2, 2, 2, 1])
        cols[0].markdown(f"**{c.get('name') or '(未入力)'}**")
        cols[1].write(c.get("current_company") or "-")
        cols[2].write(c.get("sales_type") or "-")
        cols[3].write(c.get("intent_level") or "-")
        cols[4].write(c.get("status") or "-")
        if cols[5].button("詳細", key=f"detail_{c['id']}", use_container_width=True):
            st.session_state["selected_candidate"] = c["id"]

selected_id = st.session_state.get("selected_candidate")
if selected_id:
    selected = next((c for c in candidates if c["id"] == selected_id), None)
    if selected:
        detail_dialog(selected)
