"""Creates a synthetic retail sales dataset (2023-2025) and monthly regional targets."""

import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

N_ORDERS = 6000
START = pd.Timestamp("2023-01-01")
END = pd.Timestamp("2025-12-31")

REGIONS = ["Lefkoşa", "Girne", "Gazimağusa", "Güzelyurt", "İskele"]
REGION_WEIGHTS = [0.32, 0.26, 0.20, 0.12, 0.10]

# category: (products, unit price range, margin range)
CATALOG = {
    "Elektronik": (["Dizüstü Bilgisayar", "Akıllı Telefon", "Tablet", "Kulaklık", "Monitör"], (300, 1500), (0.12, 0.22)),
    "Ev & Yaşam": (["Kahve Makinesi", "Elektrikli Süpürge", "Aydınlatma", "Mutfak Robotu"], (40, 400), (0.25, 0.40)),
    "Giyim": (["Erkek Mont", "Kadın Elbise", "Spor Ayakkabı", "Çanta"], (25, 250), (0.35, 0.55)),
    "Ofis": (["Yazıcı", "Ofis Koltuğu", "Kırtasiye Seti", "Masa Lambası"], (15, 350), (0.20, 0.35)),
    "Market": (["Gıda Paketi", "Temizlik Seti", "İçecek Kutusu"], (5, 60), (0.08, 0.18)),
}
CATEGORY_WEIGHTS = [0.30, 0.22, 0.20, 0.15, 0.13]
SALES_REPS = ["A. Yılmaz", "M. Demir", "S. Kaya", "E. Çelik", "B. Şahin", "D. Arslan"]
YEARLY_GROWTH = {2023: 1.0, 2024: 1.12, 2025: 1.27}


def build_orders():
    categories = RNG.choice(list(CATALOG), size=N_ORDERS, p=CATEGORY_WEIGHTS)
    regions = RNG.choice(REGIONS, size=N_ORDERS, p=REGION_WEIGHTS)
    days = RNG.integers(0, (END - START).days + 1, size=N_ORDERS)
    dates = START + pd.to_timedelta(days, unit="D")
    reps = RNG.choice(SALES_REPS, size=N_ORDERS)

    rows = []
    for i in range(N_ORDERS):
        products, (pmin, pmax), (mmin, mmax) = CATALOG[categories[i]]
        product = RNG.choice(products)
        unit_price = round(float(RNG.uniform(pmin, pmax)), 2)
        margin = float(RNG.uniform(mmin, mmax))
        qty = int(RNG.integers(1, 6))
        qty = max(1, int(round(qty * YEARLY_GROWTH[dates[i].year])))
        rows.append({
            "order_id": f"ORD-{100000 + i}",
            "order_date": dates[i].date().isoformat(),
            "region": regions[i],
            "category": categories[i],
            "product_name": product,
            "quantity": qty,
            "unit_price": unit_price,
            "unit_cost": round(unit_price * (1 - margin), 2),
            "sales_rep": reps[i],
            "customer_id": f"CUST-{int(RNG.integers(1, 1800)):04d}",
        })

    df = pd.DataFrame(rows)
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["profit"] = (df["quantity"] * (df["unit_price"] - df["unit_cost"])).round(2)
    return df.sort_values("order_date").reset_index(drop=True)


def build_targets(df):
    month = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str).rename("month")
    actual = df.groupby([month, "region"])["revenue"].sum().reset_index()
    actual["target_revenue"] = (actual["revenue"] * RNG.uniform(0.85, 1.10, size=len(actual))).round(0)
    return actual[["month", "region", "target_revenue"]]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = build_orders()
    targets = build_targets(df)
    df.to_csv(os.path.join(DATA_DIR, "sales_data.csv"), index=False)
    targets.to_csv(os.path.join(DATA_DIR, "targets.csv"), index=False)
    print(f"{len(df):,} orders, {len(targets)} target rows, revenue {df['revenue'].sum():,.0f} TL")


if __name__ == "__main__":
    main()
