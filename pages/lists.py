import streamlit as st

from state import add_list, delete_list, load_candidates, load_lists, update_list


def candidate_label(c: dict) -> str:
    return f"{c.get('name') or '(未入力)'} ・ {c.get('current_company') or '現職不明'} ・ {c.get('sales_type') or ''}"


st.title("候補者リスト")
st.caption("企業に依存しない、使い回せる候補者リストを作成します。企業への共有は「企業・シェアリスト」ページでこのリストを選択して割り当てます。")

candidates = load_candidates()
candidates_by_id = {c["id"]: c for c in candidates}
lists = load_lists()

with st.expander("＋ リストを新規作成"):
    with st.form("add_list_form", clear_on_submit=True):
        new_name = st.text_input("リスト名(例: エンタープライズ営業A)")
        is_all = st.checkbox("「確認済み」の候補者を自動的に含める(動的リスト)")
        st.caption("動的リストにすると、候補者一覧でステータスが「確認済み」の候補者が自動的に含まれるようになります。個別の追加・削除はできません。")
        if st.form_submit_button("作成する", type="primary"):
            if new_name.strip():
                add_list(new_name.strip(), is_all_candidates=is_all)
                st.rerun()
            else:
                st.warning("リスト名を入力してください")

if not lists:
    st.info("まだリストが作成されていません。")
    st.stop()

list_names = {l["id"]: l["name"] for l in lists}
selected_list_id = st.selectbox("リストを選択", options=list(list_names.keys()), format_func=lambda lid: list_names[lid])
current_list = next(l for l in lists if l["id"] == selected_list_id)

st.divider()

is_dynamic = bool(current_list.get("is_all_candidates"))

if is_dynamic:
    members = [c for c in candidates if c.get("status") == "確認済み"]
    st.subheader(f"{current_list['name']} ・ {len(members)}名 ・ 🔄 動的リスト(確認済みの候補者)")
    st.caption("このリストはステータスが「確認済み」の候補者を自動的に含みます。候補者一覧でステータスを変更すると自動で反映されます。")
    for c in members:
        cols = st.columns([4, 2, 2])
        cols[0].write(candidate_label(c))
        cols[1].write(c.get("intent_level") or "-")
        cols[2].write(c.get("status") or "-")
else:
    member_ids = current_list.get("candidate_ids") or []
    members = [candidates_by_id[cid] for cid in member_ids if cid in candidates_by_id]

    st.subheader(f"{current_list['name']} ・ {len(members)}名")

    for c in members:
        cols = st.columns([4, 2, 2, 1])
        cols[0].write(candidate_label(c))
        cols[1].write(c.get("intent_level") or "-")
        cols[2].write(c.get("status") or "-")
        if cols[3].button("外す", key=f"remove_{c['id']}"):
            new_ids = [cid for cid in member_ids if cid != c["id"]]
            update_list(current_list["id"], {"candidate_ids": new_ids})
            st.rerun()

    st.write("**候補者を追加**")
    pickable = [c for c in candidates if c["id"] not in member_ids]
    if not pickable:
        st.caption("追加できる候補者がありません")
    else:
        pick_id = st.selectbox(
            "候補者を選択して追加",
            options=[c["id"] for c in pickable],
            format_func=lambda cid: candidate_label(candidates_by_id[cid]),
            key="pick_candidate_for_list",
        )
        if st.button("リストに追加"):
            update_list(current_list["id"], {"candidate_ids": member_ids + [pick_id]})
            st.rerun()

st.divider()
notes = st.text_area("リストメモ", value=current_list.get("notes") or "")
col_save, col_delete = st.columns([3, 1])
if col_save.button("メモを保存", use_container_width=True):
    update_list(current_list["id"], {"notes": notes})
    st.success("保存しました")
if col_delete.button("このリストを削除", use_container_width=True):
    delete_list(current_list["id"])
    st.rerun()
