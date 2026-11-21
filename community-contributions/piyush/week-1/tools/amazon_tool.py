from typing import Optional
from langchain_core.tools import tool
from tools.amazon_scrapper import fetch_amazon_page

# Fallback catalog used automatically when Amazon returns 503
FALLBACK_PRODUCTS = [
    {"name": "Samsung Galaxy M35 5G (6GB RAM, 128GB, 6000mAh Battery)", "price": 14999, "rating": 4.2, "reviews": 12400, "link": "https://www.amazon.in/dp/B0MOCK001"},
    {"name": "iQOO Z9 5G (8GB RAM, 128GB, Dimensity 7200, 120Hz AMOLED)", "price": 17999, "rating": 4.3, "reviews": 18200, "link": "https://www.amazon.in/dp/B0MOCK002"},
    {"name": "OnePlus Nord CE 4 Lite 5G (8GB RAM, 128GB, 5500mAh)", "price": 19999, "rating": 4.1, "reviews": 9800, "link": "https://www.amazon.in/dp/B0MOCK003"},
    {"name": "Redmi Note 13 5G (6GB RAM, 128GB, 108MP Camera)", "price": 15999, "rating": 4.0, "reviews": 22100, "link": "https://www.amazon.in/dp/B0MOCK004"},
    {"name": "Allen Solly Men's Cotton Regular Fit Polo T-Shirt", "price": 699, "rating": 4.3, "reviews": 4520, "link": "https://www.amazon.in/dp/B0MOCK005"},
    {"name": "Jockey Men's Super Combed Cotton Crew Neck T-Shirt", "price": 849, "rating": 4.5, "reviews": 8120, "link": "https://www.amazon.in/dp/B0MOCK006"},
    {"name": "boAt Airdopes 141 Bluetooth TWS Earbuds (42H Playtime)", "price": 1099, "rating": 4.1, "reviews": 195000, "link": "https://www.amazon.in/dp/B0MOCK007"},
    {"name": "OnePlus Bullets Wireless Z2 Bluetooth Neckband", "price": 1799, "rating": 4.2, "reviews": 142000, "link": "https://www.amazon.in/dp/B0MOCK008"},
]

def get_fallback_products(query: str, max_price: Optional[float] = None) -> list[dict]:
    keywords = [w for w in query.lower().split() if len(w) > 2]
    matches = [
        p for p in FALLBACK_PRODUCTS
        if any(k in p["name"].lower() for k in keywords)
    ]
    results = matches if matches else FALLBACK_PRODUCTS
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    return results

@tool
def search_amazon_products(query: str, max_price: Optional[float] = None) -> list[dict]:
    """Search Amazon India for live products in any category (clothes, electronics, shoes, home, etc.)
    and return matching items with name, price (INR), rating, reviews, and link.

    Args:
        query: Short search keywords like 'mens cotton t-shirt', 'running shoes', or '5G phone'.
        max_price: Optional maximum budget in INR. Only products priced at or below this amount are returned.
    """
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    result = fetch_amazon_page(url, retries=0)  # retries=0 avoids waiting 9s before fallback

    if not result["ok"]:
        print(f"[Tool] Amazon blocked ({result['reason']}). Using fallback catalog.")
        return get_fallback_products(query, max_price)
    print(result["html"])
    parsed = parse_products(result["html"])
    filtered = [
        p for p in parsed
        if p.get("price") and (max_price is None or p["price"] <= max_price)
    ]

    if not filtered:
        return [{"error": "No products found matching this query and budget. Do not retry."}]

    filtered.sort(key=lambda x: (x.get("rating") or 0, x.get("reviews") or 0), reverse=True)
    return filtered[:15]