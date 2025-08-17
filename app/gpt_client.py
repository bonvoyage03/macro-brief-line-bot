from typing import List, Dict, Any
from logging import getLogger
import os
import datetime as dt
import json
from openai import OpenAI


JST = dt.timezone(dt.timedelta(hours=9))  # Japan Standard Time
logging = getLogger(__name__)


def build_prompt() -> List[Dict[str, Any]]:
    now = dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M %Z")

    sys_inst = (
        "You are a macro/commodities strategist. "
        "Summarize inputs specifically for *gold (XAU)* market watchers."
    )
    user_req = f"""
        [Objective]
        Please provide a concise summary of news potentially impacting the gold (XAU) market,
        including aspects such as interest rates, monetary policies, inflation indicators, supply/demand flows, geopolitical events, and other relevant developments recently.

        [Output Requirements]
        - At first, summarize the 1-3 most important news from the last 24 hours.
        - In Japanese, format the summary with a headline followed by bullet points organized under these categories: "Interest Rates and Monetary Policy", "Inflation", "USD & Interest Rate Trends", "Supply/Demand/Flows (ETF/Central Bank/Speculative)", and "Geopolitics & Other".
        - List items in order of significance.
        - Each bullet point should consist of some lines, and where possible, add a brief note (prefixed by an asterisk) regarding the implications for gold.
        - At the end, if there are any notable events or indicators (Japan time), include them with schedule information.
        - The summary should be approximately 500–1200 characters in length.
        - Do not include any hyperlinks.
        - No markdown formatting.
        """
    return [
        {"role": "system", "content": sys_inst},
        {"role": "user", "content": user_req},
    ]


def summarize_with_openai(prompt_messages: List[Dict[str, Any]]) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    logging.info(f"Using OpenAI model: {model}")
    client = OpenAI()
    resp = client.responses.create(
        model=model,
        input=prompt_messages,
        tools=[{"type": "web_search"}],
    )
    # SDK v1: convenient accessor
    try:
        return resp.output_text
    except Exception:
        # Fallback: stitch text from content parts
        if hasattr(resp, "output") and resp.output:
            parts = []
            for el in resp.output:
                if getattr(el, "content", None):
                    for c in el.content:
                        if getattr(c, "type", None) == "output_text" and getattr(c, "text", None):
                            parts.append(c.text)
            return "\n".join(parts)
        return json.dumps(resp, default=str)
