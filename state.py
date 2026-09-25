import os

from supabase import Client, create_client

STATUS_OPTIONS = ["未対応", "確認済み", "企業へ推薦中", "面接設定", "内定", "辞退", "クローズ"]
INTENT_OPTIONS = ["今すぐ転職したい", "良い話があれば検討", "情報収集段階"]


def _client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])


def load_candidates() -> list[dict]:
    res = _client().table("candidates").select("*").order("created_at", desc=True).execute()
    return res.data


def update_candidate(candidate_id: str, patch: dict) -> None:
    _client().table("candidates").update(patch).eq("id", candidate_id).execute()


def delete_candidate(candidate_id: str) -> None:
    _client().table("candidates").delete().eq("id", candidate_id).execute()


def get_resume_url(resume_path: str) -> str | None:
    if not resume_path:
        return None
    res = _client().storage.from_("resumes").create_signed_url(resume_path, 3600)
    return res.get("signedURL") or res.get("signedUrl")


def load_companies() -> list[dict]:
    res = _client().table("companies").select("*").order("created_at", desc=True).execute()
    return res.data


def add_company(name: str, contact_person: str) -> dict:
    res = (
        _client()
        .table("companies")
        .insert({"name": name, "contact_person": contact_person, "shortlist_ids": []})
        .execute()
    )
    return res.data[0]


def update_company(company_id: str, patch: dict) -> None:
    _client().table("companies").update(patch).eq("id", company_id).execute()


def delete_company(company_id: str) -> None:
    _client().table("companies").delete().eq("id", company_id).execute()
