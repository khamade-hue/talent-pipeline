import streamlit as st

from state import (
    add_company,
    delete_company,
    load_candidates,
    load_companies,
    update_company,
)

SHARE_BASE_URL = "https://beamish-ganache-be06b1.netlify.app/share.html"


def candidate_label(c: dict) -> str:
    return f"{c.get('name') or '(未入力)'} ・ {c.get('current_company') or '現職不明'} ・ {c.get('sales_type') or ''}"


st.title("企業・シェアリスト")

candidates = load_candidates()
candidates_by_id = {c["id"]: c for c in candidates}
companies = load_companies()

with st.expander("＋ 企業を追加"):
    with st.form("add_company_form", clear_on_submit=True):
        new_name = st.text_input("企業名")
        new_contact = st.text_input("担当者名(任意)")
        if st.form_submit_button("追加する", type="primary"):
            if new_name.strip():
                add_company(new_name.strip(), new_contact.strip())
                st.rerun()
            else:
                st.warning("企業名を入力してください")

if not companies:
    st.info("まだ企業が登録されていません。")
    st.stop()

company_names = {c["id"]: c["name"] for c in companies}
selected_company_id = st.selectbox(
    "企業を選択", options=list(company_names.keys()), format_func=lambda cid: company_names[cid]
)
company = next(c for c in companies if c["id"] == selected_company_id)

st.divider()

shortlist_ids = company.get("shortlist_ids") or []
shortlisted = [candidates_by_id[cid] for cid in shortlist_ids if cid in candidates_by_id]

st.subheader(f"{company['name']} ・ シェア中の候補者({len(shortlisted)})")

for c in shortlisted:
    cols = st.columns([4, 2, 2, 1])
    cols[0].write(candidate_label(c))
    cols[1].write(c.get("intent_level") or "-")
    cols[2].write(c.get("status") or "-")
    if cols[3].button("外す", key=f"remove_{c['id']}"):
        new_ids = [cid for cid in shortlist_ids if cid != c["id"]]
        update_company(company["id"], {"shortlist_ids": new_ids})
        st.rerun()

st.write("**候補者を追加**")
pickable = [c for c in candidates if c["id"] not in shortlist_ids]
if not pickable:
    st.caption("追加できる候補者がありません")
else:
    pick_id = st.selectbox(
        "候補者を選択して追加",
        options=[c["id"] for c in pickable],
        format_func=lambda cid: candidate_label(candidates_by_id[cid]),
        key="pick_candidate",
    )
    if st.button("シェアリストに追加"):
        update_company(company["id"], {"shortlist_ids": shortlist_ids + [pick_id]})
        st.rerun()

st.divider()
st.subheader("企業向け共有ページ")
st.caption("氏名・直接連絡先は含まれません。シェアリストを更新すると、このURLの内容も自動的に最新になります。")

share_url = f"{SHARE_BASE_URL}?c={company['id']}"
st.code(share_url, language=None)
st.link_button("ページを開く", share_url)

st.divider()
notes = st.text_area("企業メモ", value=company.get("notes") or "")
col_save, col_delete = st.columns([3, 1])
if col_save.button("メモを保存", use_container_width=True):
    update_company(company["id"], {"notes": notes})
    st.success("保存しました")
if col_delete.button("この企業を削除", use_container_width=True):
    delete_company(company["id"])
    st.rerun()
