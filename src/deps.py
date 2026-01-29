import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from supabase import Client, create_client


load_dotenv()


def get_supabase() -> Client:
    # storage3 can be picky about trailing slashes
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/"

    # If you want Storage uploads to work without RLS headaches,
    # use the service role key (server-side only, NEVER expose in frontend).
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def get_target_chapter_count() -> int:
    """
    For testing/demo: force a fixed chapter count (default 5).
    """
    try:
        return int(os.environ.get("CHAPTER_TARGET_COUNT", "5"))
    except ValueError:
        return 5


def get_llm() -> ChatOpenAI:
    """
    Main LLM used across the graph.
    You can switch to any OpenAI-compatible model here.
    """
    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=float(os.environ.get("OPENAI_TEMPERATURE", "0.7")),
    )

