"""Sales KPIs, monthly trend, top products and region vs target. Writes CSVs and charts to reports/."""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")
CHARTS = os.path.join(REPORTS, "charts")

PRIMARY = "#2E5EAA"
ACCENT = "#E4572E"
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False})
millions = mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M")


def load():
    df = pd.read_csv(os.path.join(DATA_DIR, "sales_data.csv"), parse_dates=["order_date"])
    targets = pd.read_csv(os.path.join(DATA_DIR, "targets.csv"))
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df, targets


def headline_kpis(df):
    revenue = df["revenue"].sum()
    profit = df["profit"].sum()
    orders = df["order_id"].nunique()
    customers = df["customer_id"].nunique()
    mom = df.groupby("month")["revenue"].sum().pct_change().dropna()
    return pd.DataFrame([{
        "total_revenue": round(revenue, 2),
        "total_profit": round(profit, 2),
        "profit_margin_pct": round(profit / revenue * 100, 2),
        "total_orders": orders,
        "unique_customers": customers,
        "average_order_value": round(revenue / orders, 2),
        "revenue_per_customer": round(revenue / customers, 2),
        "avg_monthly_growth_pct": round(mom.mean() * 100, 2),
    }])


def monthly_table(df):
    m = df.groupby("month").agg(revenue=("revenue", "sum"),
                                profit=("profit", "sum"),
                                orders=("order_id", "nunique")).reset_index()
    m["mom_growth_pct"] = (m["revenue"].pct_change() * 100).round(2)
    m["profit_margin_pct"] = (m["profit"] / m["revenue"] * 100).round(2)
    return m


def top_products(df, n=10):
    return (df.groupby(["category", "product_name"])
              .agg(revenue=("revenue", "sum"), units=("quantity", "sum"), profit=("profit", "sum"))
              .reset_index()
              .sort_values("revenue", ascending=False)
              .head(n))


def region_performance(df, targets):
    actual = df.groupby("region").agg(revenue=("revenue", "sum"),
                                      profit=("profit", "sum"),
                                      orders=("order_id", "nunique")).reset_index()
    tgt = targets.groupby("region")["target_revenue"].sum().reset_index()
    out = actual.merge(tgt, on="region", how="left")
    out["attainment_pct"] = (out["revenue"] / out["target_revenue"] * 100).round(1)
    out["profit_margin_pct"] = (out["profit"] / out["revenue"] * 100).round(1)
    return out.sort_values("revenue", ascending=False)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, name), dpi=130)
    plt.close(fig)


def charts(df, monthly, products, region):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(monthly["month"], monthly["revenue"], color=PRIMARY, lw=2.2, label="Ciro")
    ax.plot(monthly["month"], monthly["profit"], color=ACCENT, lw=2.0, label="Kâr")
    ax.set_title("Aylık Ciro ve Kâr Trendi", fontweight="bold")
    ax.set_xticks(monthly["month"][::3])
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(millions)
    ax.legend()
    save(fig, "01_monthly_trend.png")

    cat = df.groupby("category")["revenue"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(cat.index, cat.values, color=PRIMARY)
    ax.set_title("Kategoriye Göre Ciro", fontweight="bold")
    ax.xaxis.set_major_formatter(millions)
    save(fig, "02_revenue_by_category.png")

    top = products.head(8).sort_values("revenue")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(top["product_name"], top["revenue"], color=ACCENT)
    ax.set_title("En Çok Ciro Getiren Ürünler", fontweight="bold")
    ax.xaxis.set_major_formatter(millions)
    save(fig, "03_top_products.png")

    x = range(len(region))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar([i - w / 2 for i in x], region["target_revenue"], w, label="Hedef", color="#B8C4D9")
    ax.bar([i + w / 2 for i in x], region["revenue"], w, label="Gerçekleşen", color=PRIMARY)
    ax.set_xticks(list(x))
    ax.set_xticklabels(region["region"], rotation=20)
    ax.set_title("Bölge Bazında Hedef vs Gerçekleşen", fontweight="bold")
    ax.yaxis.set_major_formatter(millions)
    ax.legend()
    save(fig, "04_target_vs_actual.png")


def main():
    os.makedirs(CHARTS, exist_ok=True)
    df, targets = load()
    kpis = headline_kpis(df)
    monthly = monthly_table(df)
    products = top_products(df)
    region = region_performance(df, targets)

    kpis.to_csv(os.path.join(REPORTS, "kpi_summary.csv"), index=False)
    monthly.to_csv(os.path.join(REPORTS, "monthly_revenue.csv"), index=False)
    products.to_csv(os.path.join(REPORTS, "top_products.csv"), index=False)
    region.to_csv(os.path.join(REPORTS, "region_performance.csv"), index=False)
    charts(df, monthly, products, region)

    k = kpis.iloc[0]
    print(f"Revenue        {k.total_revenue:>14,.0f} TL")
    print(f"Profit         {k.total_profit:>14,.0f} TL")
    print(f"Margin         {k.profit_margin_pct:>13.2f} %")
    print(f"Orders         {int(k.total_orders):>14,}")
    print(f"Avg order      {k.average_order_value:>14,.0f} TL")
    print(f"Monthly growth {k.avg_monthly_growth_pct:>13.2f} %")


if __name__ == "__main__":
    main()
