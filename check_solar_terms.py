import json

def check(year=2026):
    with open(f"output/{year}.json", "r", encoding="utf-8") as f:
        obj = json.load(f)

    entries = obj["entries"]
    solar_days = [k for k, v in entries.items() if v.get("type") == "solar_term"]
    print(year, "solar_term count =", len(solar_days))
    # 抽查几条
    for k in sorted(solar_days)[:5]:
        print(k, entries[k]["meta"].get("name"), entries[k].get("tags"))

if __name__ == "__main__":
    check(2026)