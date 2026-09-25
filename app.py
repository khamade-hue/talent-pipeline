from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(page_title="タレントパイプライン", page_icon="🤝", layout="wide")


def check_password() -> bool:
    if st.session_state.get("password_correct"):
        return True

    def on_submit():
        entered = st.session_state.get("password_input", "")
        st.session_state["password_correct"] = entered == st.secrets.get("APP_PASSWORD", "")

    st.title("タレントパイプライン")
    st.text_input("パスワード", type="password", key="password_input", on_change=on_submit)
    if st.session_state.get("password_correct") is False:
        st.error("パスワードが違います")
    return False


if not check_password():
    st.stop()

pg = st.navigation(
    [
        st.Page("pages/candidates.py", title="候補者一覧", icon="🧑‍💼"),
        st.Page("pages/lists.py", title="候補者リスト", icon="📋"),
        st.Page("pages/company_list.py", title="企業一覧", icon="🏬"),
        st.Page("pages/companies.py", title="企業・シェアリスト", icon="🏢"),
    ]
)
pg.run()
