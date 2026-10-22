
import os
import json
import requests
import duckdb
import pandas as pd

DB_PATH = "menu.duckdb"
OUTPUT_DIR = "output"
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_sales_item_counts(con, date_start, date_end):
    """按饮品名称和 L/M 杯型汇总销售数量。"""

    sql = """
    SELECT
        COALESCE(NULLIF(TRIM(r.name), ''), TRIM(s.item)) AS item_name,
        CASE
            WHEN LOWER(TRIM(s."Price Point Name")) = 'l' THEN 'L'
            WHEN LOWER(TRIM(s."Price Point Name")) = 'm' THEN 'M'
            ELSE TRIM(s."Price Point Name")
        END AS size,
        SUM(ABS(TRY_CAST(s.qty AS DOUBLE))) AS total_qty,
        STRING_AGG(DISTINCT TRIM(CAST(s.sku AS VARCHAR)), ', ')
            AS skus
    FROM sales s
    LEFT JOIN menu_items r
        ON (
            NULLIF(TRIM(CAST(s.sku AS VARCHAR)), '') IS NOT NULL
            AND TRIM(CAST(s.sku AS VARCHAR))
                = TRIM(CAST(r.sku AS VARCHAR))
        )
        OR (
            NULLIF(TRIM(CAST(s.sku AS VARCHAR)), '') IS NULL
            AND TRIM(s.item) = TRIM(r.name)
        )
    WHERE CAST(s."date" AS DATE)
        BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
    GROUP BY 1, 2
    ORDER BY total_qty DESC
    """

    df = con.execute(sql, [date_start, date_end]).fetchdf()

    # 让杯型成为饮品名称的一部分，便于 AI 区分 L/M。
    df["original_name"] = df.apply(
        lambda row: (
            f'{row["item_name"]} ({row["size"]})'
            if row["size"] in ("L", "M")
            else row["item_name"]
        ),
        axis=1,
    )

    return df


def merge_names_with_deepseek(df):
    """让 DeepSeek 判断名称归属，不让 AI 计算销量。"""

    items = df[["original_name", "item_name", "size", "total_qty"]]
    records = items.to_dict(orient="records")

    prompt = """
You are matching bubble tea menu item names.

Return a JSON object with a "mappings" array.
For EVERY input record, return exactly one mapping containing:
- original_name: exact input original_name
- canonical_name: normalized base drink name
- merged: true if this name should be combined with another distinct
  original name; otherwise false
- merge_reason: concise explanation

Rules:
1. Leading uppercase D or A may identify delivery or app ordering.
   Remove these prefixes only when they clearly indicate a platform.
2. Expand common abbreviations when the meaning is clear, such as
   BT = Black Tea and MGO = Mango.
3. A "w/" suffix indicates extra toppings. Remove the topping suffix
   when matching the underlying base drink.
4. Any drink name specifying a size in oz, such as 32 oz, must remain
   distinct. Never merge it with a regular drink.
5. "Bubble Tea (L) Redemption" is the same drink as "Pearl Milk Tea".
6. Keep L and M sizes separate. Never merge different cup sizes.
7. Do not merge drinks just because they share a tea base or topping.
8. Preserve meaningful differences in the base drink, such as Mango
   versus Strawberry, Milk Tea versus Pure Tea, or Matcha versus Taro.
9. Do not change or calculate quantities. Python will aggregate them.
10. Every original_name must appear exactly once in the result.
11. If uncertain, keep the original drink distinct rather than guessing.
12. Output valid JSON only, without Markdown fences.

Input records:
""" + json.dumps(records, ensure_ascii=False)

    response = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You normalize drink names and return valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        },
        timeout=180,
    )

    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    mappings = json.loads(content)["mappings"]

    mapping_df = pd.DataFrame(mappings)

    # Ensure every original name has exactly one mapping.
    if mapping_df["original_name"].duplicated().any():
        raise ValueError("DeepSeek returned duplicate original_name values.")

    expected = set(df["original_name"])
    actual = set(mapping_df["original_name"])

    if expected != actual:
        raise ValueError(
            f"Mapping mismatch. Missing: {expected - actual}; "
            f"Unexpected: {actual - expected}"
        )

    return mapping_df


def build_merged_csv(df, mappings):
    """将 AI 映射与原始数量合并，销量由 Python 求和。"""

    merged = df.merge(
        mappings,
        on="original_name",
        how="left",
        validate="one_to_one",
    )

    # Group only by normalized name and cup size.
    result = (
        merged.groupby(["canonical_name", "size"], dropna=False)
        .agg(
            total_qty=("total_qty", "sum"),
            original_names=("original_name", list),
            reasons=("merge_reason", list),
        )
        .reset_index()
    )

    result["merged"] = result["original_names"].apply(
        lambda names: len(set(names)) > 1
    )

    result["calculation"] = result["original_names"].apply(
        lambda names: " + ".join(
            str(int(qty)) if float(qty).is_integer() else str(qty)
            for name, qty in zip(
                merged["original_name"], merged["total_qty"]
            )
            if name in names
        )
    )

    result["original_names"] = result["original_names"].apply(
        lambda names: " | ".join(sorted(set(names)))
    )

    result["merge_reason"] = result["reasons"].apply(
        lambda reasons: " | ".join(sorted(set(reasons)))
    )

    result = result[
        [
            "canonical_name",
            "size",
            "total_qty",
            "merged",
            "original_names",
            "merge_reason",
            "calculation",
        ]
    ]

    return result.sort_values(
        ["canonical_name", "size"]
    ).reset_index(drop=True)


def main():
    date_start = input("Start date (YYYY-MM-DD): ")
    date_end = input("End date (YYYY-MM-DD): ")

    with duckdb.connect(DB_PATH, read_only=True) as con:
        df = get_sales_item_counts(con, date_start, date_end)

    raw_path = os.path.join(OUTPUT_DIR, "sales_item_counts.csv")
    df.to_csv(raw_path, index=False)

    print(f"Raw sales counts saved: {raw_path}")

    mappings = merge_names_with_deepseek(df)

    mapping_path = os.path.join(
        OUTPUT_DIR, "sales_item_name_mappings.csv"
    )
    mappings.to_csv(mapping_path, index=False)

    result = build_merged_csv(df, mappings)

    merged_path = os.path.join(
        OUTPUT_DIR, "sales_item_counts_merged.csv"
    )
    result.to_csv(merged_path, index=False)

    print(f"Name mappings saved: {mapping_path}")
    print(f"Merged sales counts saved: {merged_path}")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
