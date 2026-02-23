"""
Generates a realistic 100-row dummy Amazon Sponsored Products Search Term Report (SPSTR).
Covers all 4 performance categories:
  - Wasted Adspend (high clicks, 0 orders)
  - Inefficient Adspend (high ACOS, orders > 0)
  - Scaling Opportunity (Exact match, good CVR, low clicks)
  - Harvesting Opportunity (not targeted, orders > 2)
"""

import csv
import os
import random

CAMPAIGNS = [
    {
        "campaign_id": "514290153054958",
        "campaign_name": '"kids golf clubs 3-5" - EX - HSV - Kids Putter - Incrementum',
        "ad_group_id": "338763421328727",
        "ad_group_name": "03. Kids Putter - Extendable Silver",
        "portfolio": "Go for it Golf",
    },
    {
        "campaign_id": "286611797534744",
        "campaign_name": '"kids golf clubs" - 10K HSV - EX - Junior Golf Club Set - Incrementum',
        "ad_group_id": "447190817537962",
        "ad_group_name": "28. November - Junior Golf Club Set",
        "portfolio": "Go for it Golf",
    },
    {
        "campaign_id": "507042941633893",
        "campaign_name": "2K HSV - BR - Ferrofluid - SKC - Incrementum",
        "ad_group_id": "451442274269531",
        "ad_group_name": "01. Ferrofluid - Pure Source + Stem Source",
        "portfolio": "Science Kits Central",
    },
    {
        "campaign_id": "393518651546755",
        "campaign_name": "SP - Low Bid Auto - Ferrofluid - Close 1",
        "ad_group_id": "557880985911089",
        "ad_group_name": "25. Ferrofluid Auto",
        "portfolio": "Science Kits Central",
    },
    {
        "campaign_id": "556268903645598",
        "campaign_name": "200 LSV - PH - Competitor Brand - Equalizer Golf Card - Incrementum",
        "ad_group_id": "307784767455836",
        "ad_group_name": "14. Equalizer On-Course Golf Card Game",
        "portfolio": "Go for it Golf",
    },
]

SEARCH_TERMS_POOL = [
    "kids golf clubs", "kids golf set", "junior golf clubs", "toddler golf clubs",
    "golf clubs for kids 3-5", "left handed kids golf clubs", "golf set for boys",
    "ferrofluid", "ferrofluid display", "magnetic ferrofluid", "ferrofluid bottle",
    "ferrofluid visualizer", "ferrofluid toy", "magnetic fluid",
    "wicker basket", "storage basket", "wicker storage basket large",
    "seagrass basket", "woven basket", "decorative basket", "laundry basket wicker",
    "card game for golfers", "golf card game", "golf gift for men",
    "play9 card game", "golf accessories", "golf gifts",
    "science kit for kids", "magnetic science toy", "stem toy",
    "kids science experiment", "cool science gifts", "desk toy magnetic",
    "outdoor toys for kids", "sports toys", "backyard games",
    "gift for boys age 5", "birthday gift kids", "christmas gift boys",
    "deals", "prime deal", "lightning deal", "cheap golf clubs",
    "best golf set", "top rated kids golf", "amazon choice golf",
    "golf training aid", "putting practice", "golf swing trainer",
]

COLUMNS = [
    "Product", "Campaign ID", "Ad Group ID", "Keyword ID",
    "Campaign Name (Informational only)", "Ad Group Name (Informational only)",
    "Portfolio Name (Informational only)", "State", "Campaign State (Informational only)",
    "Bid", "Keyword Text", "Match Type",
    "Product Targeting Expression", "Resolved Product Targeting Expression (Informational only)",
    "Customer Search Term", "Impressions", "Clicks", "Click-through Rate",
    "Spend", "Sales", "Orders", "Units", "Conversion Rate", "ACOS", "CPC", "ROAS",
]


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _make_row(camp: dict, search_term: str, keyword_text: str, match_type: str,
              impressions: int, clicks: int, orders: int, units: int,
              spend: float, sales: float, bid: float) -> dict:
    ctr = clicks / impressions if impressions > 0 else 0.0
    cvr = orders / clicks if clicks > 0 else 0.0
    acos = spend / sales if sales > 0 else 0.0
    cpc = spend / clicks if clicks > 0 else 0.0
    roas = sales / spend if spend > 0 else 0.0

    return {
        "Product": "Sponsored Products",
        "Campaign ID": camp["campaign_id"],
        "Ad Group ID": camp["ad_group_id"],
        "Keyword ID": str(random.randint(100000000000000, 999999999999999)),
        "Campaign Name (Informational only)": camp["campaign_name"],
        "Ad Group Name (Informational only)": camp["ad_group_name"],
        "Portfolio Name (Informational only)": camp["portfolio"],
        "State": "enabled",
        "Campaign State (Informational only)": "enabled",
        "Bid": f"{bid:.2f}",
        "Keyword Text": keyword_text,
        "Match Type": match_type,
        "Product Targeting Expression": "",
        "Resolved Product Targeting Expression (Informational only)": "",
        "Customer Search Term": search_term,
        "Impressions": impressions,
        "Clicks": clicks,
        "Click-through Rate": _pct(ctr),
        "Spend": f"{spend:.2f}",
        "Sales": f"{sales:.2f}",
        "Orders": orders,
        "Units": units,
        "Conversion Rate": _pct(cvr),
        "ACOS": _pct(acos),
        "CPC": f"{cpc:.2f}",
        "ROAS": f"{roas:.2f}",
    }


def generate(output_path: str = None, n_rows: int = 100) -> str:
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "dummy_spstr.csv")

    rows = []
    random.seed(42)
    terms = list(SEARCH_TERMS_POOL)

    # ---- Category 1: Wasted Adspend (high clicks, 0 orders) ~25 rows ----
    for i in range(25):
        camp = random.choice(CAMPAIGNS)
        st = random.choice(terms)
        match_type = random.choice(["Exact", "Phrase", "Broad"])
        impressions = random.randint(300, 5000)
        clicks = random.randint(10, 40)
        spend = round(clicks * random.uniform(0.5, 2.5), 2)
        rows.append(_make_row(
            camp, st, st, match_type,
            impressions, clicks,
            orders=0, units=0,
            spend=spend, sales=0.0,
            bid=round(random.uniform(0.5, 3.0), 2),
        ))

    # ---- Category 2: Inefficient Adspend (high ACOS, orders > 0) ~25 rows ----
    for i in range(25):
        camp = random.choice(CAMPAIGNS)
        st = random.choice(terms)
        match_type = random.choice(["Exact", "Phrase", "Broad"])
        impressions = random.randint(500, 8000)
        clicks = random.randint(15, 60)
        orders = random.randint(1, 4)
        units = orders + random.randint(0, 2)
        sales = round(orders * random.uniform(8.0, 35.0), 2)
        acos_target = random.uniform(0.35, 0.90)
        spend = round(sales * acos_target, 2)
        rows.append(_make_row(
            camp, st, st, match_type,
            impressions, clicks,
            orders=orders, units=units,
            spend=spend, sales=sales,
            bid=round(random.uniform(0.8, 3.5), 2),
        ))

    # ---- Category 3: Scaling Opportunity (Exact, good CVR, low clicks) ~25 rows ----
    for i in range(25):
        camp = random.choice(CAMPAIGNS)
        st = random.choice(terms)
        impressions = random.randint(50, 400)
        clicks = random.randint(2, 9)
        orders = random.randint(1, 3)
        units = orders + random.randint(0, 1)
        sales = round(orders * random.uniform(12.0, 40.0), 2)
        spend = round(clicks * random.uniform(0.4, 1.8), 2)
        rows.append(_make_row(
            camp, st, st, "Exact",
            impressions, clicks,
            orders=orders, units=units,
            spend=spend, sales=sales,
            bid=round(random.uniform(0.5, 2.0), 2),
        ))

    # ---- Category 4: Harvesting Opportunity (not targeted, orders > 2) ~25 rows ----
    auto_match_types = ["close-match", "loose-match", "complements", "substitutes"]
    for i in range(25):
        camp = random.choice(CAMPAIGNS)
        st = random.choice(terms)
        match_type = random.choice(auto_match_types)
        impressions = random.randint(200, 6000)
        clicks = random.randint(8, 50)
        orders = random.randint(3, 10)
        units = orders + random.randint(0, 3)
        sales = round(orders * random.uniform(10.0, 35.0), 2)
        spend = round(clicks * random.uniform(0.3, 1.5), 2)
        rows.append(_make_row(
            camp, st, "", match_type,
            impressions, clicks,
            orders=orders, units=units,
            spend=spend, sales=sales,
            bid=round(random.uniform(0.3, 1.5), 2),
        ))

    random.shuffle(rows)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    generate()
