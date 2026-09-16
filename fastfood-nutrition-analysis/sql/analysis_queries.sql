/*
Fast Food Nutrition Analysis — SQL Queries
Dataset: fastfood_calories.csv (515 menu items, 8 restaurants)
Source:  R for Data Science TidyTuesday project (2018-09-04),
         originally compiled from each restaurant's published nutrition facts
Tool:    SQLite (works in DB Browser for SQLite, or any SQL engine with minor tweaks)

Load the CSV into a table called `fastfood` before running these
(in DB Browser for SQLite: File > Import > Table from CSV).
*/

-- ============================================================
-- 1. Menu size and average calories per restaurant, ranked
-- ============================================================
SELECT
    restaurant,
    COUNT(*)                        AS menu_items,
    ROUND(AVG(calories), 0)         AS avg_calories,
    MIN(calories)                   AS min_calories,
    MAX(calories)                   AS max_calories
FROM fastfood
GROUP BY restaurant
ORDER BY avg_calories DESC;


-- ============================================================
-- 2. Average sodium per restaurant (daily recommended max ~2300mg)
-- ============================================================
SELECT
    restaurant,
    ROUND(AVG(sodium), 0)           AS avg_sodium_mg,
    ROUND(100.0 * AVG(sodium) / 2300, 1) AS pct_of_daily_limit
FROM fastfood
GROUP BY restaurant
ORDER BY avg_sodium_mg DESC;


-- ============================================================
-- 3. Best protein-to-calorie ratio per restaurant
--    (protein grams per 100 calories — a simple "bang for your
--    calorie buck" metric for anyone eating for muscle/fitness goals)
-- ============================================================
SELECT
    restaurant,
    ROUND(AVG(protein), 1)                         AS avg_protein_g,
    ROUND(AVG(calories), 0)                        AS avg_calories,
    ROUND(100.0 * AVG(protein) / AVG(calories), 2) AS protein_g_per_100cal
FROM fastfood
GROUP BY restaurant
ORDER BY protein_g_per_100cal DESC;


-- ============================================================
-- 4. The single most caloric item at each restaurant
--    (window function: RANK() per restaurant, ordered by calories)
-- ============================================================
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


-- ============================================================
-- 5. "Healthier choice" composite score
--    Simple, transparent scoring: reward protein, penalize sugar
--    and sodium (each normalized to a 0-100 scale within the dataset)
--    Higher score = more protein per calorie, less sugar/sodium.
-- ============================================================
WITH bounds AS (
    SELECT
        MIN(sugar) AS min_sugar, MAX(sugar) AS max_sugar,
        MIN(sodium) AS min_sodium, MAX(sodium) AS max_sodium,
        MIN(protein) AS min_protein, MAX(protein) AS max_protein
    FROM fastfood
),
scored AS (
    SELECT
        f.restaurant,
        f.item,
        f.calories,
        f.protein,
        f.sugar,
        f.sodium,
        ROUND(
            100.0 * (f.protein - b.min_protein) / NULLIF(b.max_protein - b.min_protein, 0)
            - 50.0 * (f.sugar   - b.min_sugar)   / NULLIF(b.max_sugar   - b.min_sugar, 0)
            - 50.0 * (f.sodium  - b.min_sodium)  / NULLIF(b.max_sodium  - b.min_sodium, 0)
        , 1) AS health_score
    FROM fastfood f CROSS JOIN bounds b
)
SELECT restaurant, item, calories, protein, sugar, sodium, health_score
FROM scored
ORDER BY health_score DESC
LIMIT 10;


-- ============================================================
-- 6. Share of each restaurant's menu that is "high calorie"
--    (CASE expression + conditional aggregation, >800 cal threshold)
-- ============================================================
SELECT
    restaurant,
    COUNT(*) AS menu_items,
    SUM(CASE WHEN calories > 800 THEN 1 ELSE 0 END) AS items_over_800cal,
    ROUND(100.0 * SUM(CASE WHEN calories > 800 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_over_800cal
FROM fastfood
GROUP BY restaurant
ORDER BY pct_over_800cal DESC;


-- ============================================================
-- 7. The 10 highest-sodium single items in the dataset
--    (context: FDA daily recommended sodium limit is 2,300mg)
-- ============================================================
SELECT
    restaurant,
    item,
    calories,
    sodium,
    ROUND(100.0 * sodium / 2300, 0) AS pct_of_daily_sodium_limit
FROM fastfood
ORDER BY sodium DESC
LIMIT 10;
