# Regenerates the three chart PNGs in images/ from the same fastfood
# dataset the SQL queries run against. Run from the repo root:
#   python viz/make_charts.py
#
# The script builds its own local fastfood.db on first run (downloading the
# CSV straight from the TidyTuesday source), so no manual setup is needed.
import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

CSV_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2018/2018-09-04/fastfood_calories.csv"
DB_PATH = "fastfood.db"

if not os.path.exists(DB_PATH):
    print("No local fastfood.db found — downloading dataset and building one...")
    df_bootstrap = pd.read_csv(CSV_URL, index_col=0)
    with sqlite3.connect(DB_PATH) as bootstrap_conn:
        df_bootstrap.to_sql("fastfood", bootstrap_conn, if_exists="replace", index=False)

conn = sqlite3.connect(DB_PATH)

# Fixed restaurant order (alphabetical) with a colorblind-safe categorical
# palette (Okabe-Ito), assigned in fixed order so color = identity across charts.
ORDER = ["Arbys", "Burger King", "Chick Fil-A", "Dairy Queen",
         "Mcdonalds", "Sonic", "Subway", "Taco Bell"]
PALETTE = {
    "Arbys":        "#E69F00",
    "Burger King":  "#56B4E9",
    "Chick Fil-A":  "#009E73",
    "Dairy Queen":  "#1A1A1A",
    "Mcdonalds":    "#0072B2",
    "Sonic":        "#D55E00",
    "Subway":       "#CC79A7",
    "Taco Bell":    "#999999",
}
INK = "#2B2B2B"
MUTED = "#6B6B6B"
GRID = "#E3E3E3"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def styled_hbar(df, value_col, title, subtitle, fname, fmt="{:.0f}", refline=None, reflabel=None):
    df = df.sort_values(value_col, ascending=True)
    colors = [PALETTE[r] for r in df["restaurant"]]

    fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=200)
    bars = ax.barh(df["restaurant"], df[value_col], color=colors, height=0.62,
                    zorder=3)

    # rounded-looking ends via slight edge, subtle
    for b in bars:
        b.set_linewidth(0)

    ax.set_xlim(0, df[value_col].max() * 1.18)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(left=False, bottom=False)
    ax.set_xticks([])

    # direct labels at bar end
    for y, v in enumerate(df[value_col]):
        ax.text(v + df[value_col].max() * 0.02, y, fmt.format(v),
                 va="center", ha="left", fontsize=10.5, color=INK, fontweight="medium")

    if refline is not None:
        ax.axvline(refline, color="#B33B3B", linewidth=1.4, linestyle=(0, (4, 3)), zorder=2)
        ax.text(refline, len(df) - 0.35, reflabel, color="#B33B3B", fontsize=9,
                 ha="left", va="bottom")

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["restaurant"], fontsize=11)

    fig.suptitle(title, x=0.03, y=0.98, ha="left", fontsize=14.5, fontweight="bold", color=INK)
    ax.set_title(subtitle, loc="left", fontsize=10.5, color=MUTED, pad=14)

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(fname, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# --- Chart 1: Average calories per restaurant ---
q1 = pd.read_sql_query("""
    SELECT restaurant, ROUND(AVG(calories),0) AS avg_calories
    FROM fastfood GROUP BY restaurant
""", conn)
styled_hbar(q1, "avg_calories",
            "McDonald's menu items average 640 calories — the highest of the 8 chains",
            "Average calories per menu item, by restaurant  ·  n = 515 items",
            "images/01_avg_calories_by_restaurant.png")

# --- Chart 2: Protein per 100 calories ---
q2 = pd.read_sql_query("""
    SELECT restaurant, ROUND(100.0*AVG(protein)/AVG(calories),2) AS protein_per_100cal
    FROM fastfood GROUP BY restaurant
""", conn)
styled_hbar(q2, "protein_per_100cal",
            "Chick-fil-A delivers the most protein per calorie of any chain",
            "Grams of protein per 100 calories, by restaurant (higher = more efficient)",
            "images/02_protein_efficiency.png", fmt="{:.1f}g")

# --- Chart 3: Average sodium vs. daily limit ---
q3 = pd.read_sql_query("""
    SELECT restaurant, ROUND(AVG(sodium),0) AS avg_sodium
    FROM fastfood GROUP BY restaurant
""", conn)
styled_hbar(q3, "avg_sodium",
            "An average Arby's item alone covers 66% of a full day's sodium limit",
            "Average sodium (mg) per menu item, vs. FDA daily limit of 2,300mg",
            "images/03_avg_sodium_by_restaurant.png",
            fmt="{:.0f}mg", refline=2300, reflabel="2,300mg daily limit")

print("charts written")
