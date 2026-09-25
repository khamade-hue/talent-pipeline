import streamlit as st

from state import add_company, delete_company, load_companies, load_lists, update_company

SHARE_BASE_URL = "https://beamish-ganache-be06b1.netlify.app/share.html"

st.title("企業・シェアリスト")

companies = load_companies()
lists = load_lists()
list_names = {l["id"]: l["name"] for l in lists}

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
st.subheader(company["name"])

if not lists:
    st.warning("先に「候補者リスト」ページでリストを作成してください。")
else:
    options = [None] + list(list_names.keys())
    current_assigned = company.get("assigned_list_id")
    assigned_list_id = st.selectbox(
        "共有するリスト",
        options=options,
        index=options.index(current_assigned) if current_assigned in options else 0,
        format_func=lambda lid: "(未割り当て)" if lid is None else list_names[lid],
    )
    if assigned_list_id != current_assigned:
        update_company(company["id"], {"assigned_list_id": assigned_list_id})
        st.rerun()

    if company.get("assigned_list_id"):
        st.divider()
        st.subheader("企業向け共有ページ")
        st.caption("氏名・直接連絡先は含まれません。割り当てるリストを変更すると、このURLの内容も自動的に最新になります。")
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
