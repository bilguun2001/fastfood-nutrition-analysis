# Fast Food Nutrition Analysis

**Which fast food chain actually gives you the best nutritional value — and which single menu item comes closest to blowing your entire day's sodium budget in one order?**

A SQL analysis of 515 menu items across 8 major U.S. fast food chains (Arby's, Burger King, Chick-fil-A, Dairy Queen, McDonald's, Sonic, Subway, Taco Bell), built to demonstrate querying and analytical thinking on a real, public dataset.

---

## Key Findings

### 1. McDonald's has the highest-calorie menu on average — Chick-fil-A the lowest

![Average calories by restaurant](images/01_avg_calories_by_restaurant.png)

The average McDonald's menu item runs **640 calories**, about 67% more than the average Chick-fil-A item (**384 calories**). Sonic (632) and Burger King (609) aren't far behind McDonald's, while Taco Bell (444) and Subway (503) sit closer to Chick-fil-A on this measure.

### 2. Chick-fil-A gives you the most protein per calorie of any chain

![Protein efficiency by restaurant](images/02_protein_efficiency.png)

Despite having the lowest average calories, Chick-fil-A leads every chain in protein efficiency at **8.3g of protein per 100 calories** — noticeably ahead of McDonald's (6.3g) and Subway (6.0g), and more than double Taco Bell's 3.9g. For anyone optimizing for protein without over-eating on calories, Chick-fil-A's menu is statistically the most efficient of the 8.

### 3. Arby's has the highest average sodium — and it's not close

![Average sodium by restaurant](images/03_avg_sodium_by_restaurant.png)

An average Arby's menu item contains **1,515mg of sodium**, **66% of the FDA's recommended full-day limit of 2,300mg**, in a single item. McDonald's (1,438mg) and Sonic (1,351mg) follow. Taco Bell has the lowest average at 1,014mg (44% of the daily limit).

### 4. One single item is worse than any restaurant's average: 264% of a full day's sodium

The **McDonald's 20-piece Buttermilk Crispy Chicken Tenders** contains **6,080mg of sodium and 2,430 calories** — that's **264% of an entire day's recommended sodium intake in one menu item**. It isn't close: the runner-up (Sonic's Buffalo Dunked Ultimate Chicken Sandwich, 4,520mg) is nearly 1,600mg behind it. Large fried-chicken bundles dominate the top of this list across nearly every chain.

| Rank | Restaurant | Item | Calories | Sodium | % of Daily Sodium Limit |
|---|---|---|---|---|---|
| 1 | McDonald's | 20 piece Buttermilk Crispy Chicken Tenders | 2,430 | 6,080mg | 264% |
| 2 | Sonic | Buffalo Dunked Ultimate Chicken Sandwich | 1,000 | 4,520mg | 197% |
| 3 | McDonald's | 10 pc Sweet N' Spicy Honey BBQ Glazed Tenders | 1,600 | 4,450mg | 193% |
| 4 | McDonald's | 12 piece Buttermilk Crispy Chicken Tenders | 1,510 | 3,770mg | 164% |
| 5 | Chick-fil-A | 30 piece Chicken Nuggets | 970 | 3,660mg | 159% |

*(Full top-10 query, with the `INDEX`/`MATCH`-style ranking logic done in SQL, is query 7 in `sql/analysis_queries.sql`.)*

### 5. Burger King and Sonic carry the most menu-wide calorie risk

Even though McDonald's has the highest *average*, **22.9% of Burger King's menu and 22.6% of Sonic's menu** exceed 800 calories per item — the largest share of any chain. McDonald's is close behind at 17.5%, while Taco Bell has the smallest share of high-calorie items at just 2.6%, despite its reputation.

---

## A note on methodology (and where a simple score breaks down)

The SQL file includes a composite "health score" that rewards protein and penalizes sugar and sodium (see `sql/analysis_queries.sql`, query 5). Worth flagging honestly: because it doesn't penalize total serving size, it tends to rank oversized fried-chicken bundles (20-piece tenders, 30-piece nuggets) as "healthiest," simply because bulk orders carry more total protein. A more rigorous version would score *per 100 calories* rather than per item — left as a natural next step. Calling out a metric's blind spot is as much a part of the analysis as the metric itself.

---

## Repository Structure

```
fastfood-nutrition-analysis/
├── README.md                          # this file — findings + visualizations
├── sql/
│   └── analysis_queries.sql           # 7 queries: GROUP BY, window functions, CASE, composite scoring
├── viz/
│   └── make_charts.py                 # generates the 3 PNGs below directly from the SQL data
└── images/
    ├── 01_avg_calories_by_restaurant.png
    ├── 02_protein_efficiency.png
    └── 03_avg_sodium_by_restaurant.png
```

## Tools & Techniques

- **SQL** (`sql/analysis_queries.sql`): `GROUP BY` aggregation, `RANK() OVER (PARTITION BY ...)` window functions, `CASE`-based conditional aggregation, multi-CTE composite scoring

Example — the window-function query that finds the single most caloric item at each chain:

```sql
WITH ranked AS (
    SELECT
        restaurant,
        item,
        calories,
        sodium,
        RANK() OVER (PARTITION BY restaurant ORDER BY calories DESC) AS calorie_rank
    FROM fastfood
)
SELECT restaurant, item, calories, sodium
FROM ranked
WHERE calorie_rank = 1
ORDER BY calories DESC;
```

The full set of 7 queries — including the multi-CTE composite scoring query and the `CASE`-based conditional aggregation — is in [`sql/analysis_queries.sql`](sql/analysis_queries.sql).

## Visualizations

The three charts above are generated straight from the same data the SQL queries run against, using a small Python script: [`viz/make_charts.py`](viz/make_charts.py) (matplotlib). Running `python viz/make_charts.py` from the repo root downloads the dataset, builds a local SQLite database, and regenerates all three PNGs — so the exact code behind every chart in this README is included and reproducible, not just the output.

**Why a script instead of Power BI:** I considered Power BI for this, but went with a plain script for three reasons — it's free and needs no extra software to view (the charts render inline right in this README), the code that produced them is visible and auditable the same way the SQL is, and it keeps the whole project reproducible from a single `git clone` rather than a binary `.pbix` file GitHub can't preview. That said, the SQL queries here would plug directly into Power BI as a data source if you wanted a live, interactive dashboard version — that's a natural next step, just outside the scope of this static writeup.

## Data Source

[`fastfood_calories.csv`](https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2018/2018-09-04/fastfood_calories.csv), from the [R for Data Science TidyTuesday project (2018-09-04)](https://github.com/rfordatascience/tidytuesday/blob/main/data/2018/2018-09-04/fastfood_calories.csv), originally compiled from each chain's published nutrition facts. Covers entrees only (515 items across 8 chains) — sides, drinks, and desserts are not included. Daily sodium limit reference: FDA recommended maximum of 2,300mg/day.

## How to Reproduce

**Queries:**
1. Download the dataset from the source link above.
2. Import it into any SQL tool (e.g. [DB Browser for SQLite](https://sqlitebrowser.org/), free) as a table named `fastfood`.
3. Run the queries in `sql/analysis_queries.sql`.

**Charts:** with Python 3 and `pandas`/`matplotlib` installed, run `python viz/make_charts.py` from the repo root — it downloads the dataset and regenerates the three PNGs in `images/` automatically.

---

*Built by [Bilguun Boldchingis](https://www.linkedin.com/in/bilguun-boldchingis)*
