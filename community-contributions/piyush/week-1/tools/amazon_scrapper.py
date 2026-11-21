import time
from curl_cffi import requests as cffi_requests

session = cffi_requests.Session()

CAPTCHA_SIGNS = [
    "captcha",
    "enter the characters you see below",
    "sorry, we just need to make sure you're not a robot",
]


def fetch_amazon_page(url: str, save_to: str = "amazon.html", retries: int = 2) -> dict:
    """
    Fetch an Amazon search page and return its raw HTML.
    Returns a dict: {"ok": bool, "reason": str, "html": str}
    """
    reason = "unknown error"

    for attempt in range(1, retries + 2):
        try:
            # Visit homepage first to grab fresh cookies
            if not session.cookies:
                session.get("https://www.amazon.in/", impersonate="chrome", timeout=15)

            response = session.get(url, impersonate="chrome", timeout=15)

        except Exception as e:
            reason = f"request failed: {e}"
            print(f"Attempt {attempt}: {reason}")
            if attempt <= retries:
                time.sleep(3 * attempt)
            continue

        html = response.text
        lower = html.lower()
        product_count = html.count("data-asin=")

        if response.status_code != 200:
            reason = f"bad request {response.status_code}"
        elif any(sign in lower for sign in CAPTCHA_SIGNS):
            reason = "blocked_sign"
        elif product_count < 5:
            reason = "page loaded but only minimal data count"
        else:
            with open(save_to, "w", encoding="utf-8") as f:
                f.write(html)
            reason = (
                f"got real page: {len(html)} chars, "
                f"{product_count} data-asin found, saved to {save_to}"
            )
            print(reason)
            return {"ok": True, "reason": reason, "html": html}

        print(f"Attempt {attempt}: {reason}")
        with open("amazon_failed.html", "w", encoding="utf-8") as f:
            f.write(html)

        if attempt <= retries:
            time.sleep(3 * attempt)

    return {"ok": False, "reason": reason, "html": ""}


if __name__ == "__main__":
    test_url = "https://www.amazon.in/s?k=cotton+t-shirt"
    result = fetch_amazon_page(test_url, retries=0)
    print(result["ok"], result["reason"])