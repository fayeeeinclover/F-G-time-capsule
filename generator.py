import json
import os
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOLAR_TERMS_PATH = os.path.join(BASE_DIR, "data", "solar_terms.json")
LUNAR_FESTIVALS_PATH = os.path.join(BASE_DIR, "data", "lunar_festivals.json")
TZ = "Asia/Shanghai"
LOCALE = "zh-CN"

# 公历固定节日（后面可以继续加）
# generator.py 中的这部分
FIXED_GREGORIAN_FESTIVALS = {
    "01-01": {"name": "元旦", "tags": ["gregorian", "new_year"]},
    "02-14": {"name": "情人节", "tags": ["gregorian"]},
    "03-08": {"name": "妇女节", "tags": ["gregorian"]},  # 新增
    "03-12": {"name": "植树节", "tags": ["gregorian"]},  # 新增
    "04-22": {"name": "地球日", "tags": ["gregorian"]},  # 新增
    "05-01": {"name": "劳动节", "tags": ["gregorian"]},
    "06-01": {"name": "儿童节", "tags": ["gregorian"]},  # 新增
    "10-01": {"name": "国庆节", "tags": ["gregorian"]},
    "10-31": {"name": "万圣夜", "tags": ["gregorian"]},  # 新增
    "12-25": {"name": "圣诞节", "tags": ["gregorian"]},
}

# 自定义日子：只放日期+名字+标签，不写正文
CUSTOM_DATES = {
    "09-20": {
        "name": "Faye生日",
        "tags": ["birthday", "personal"],
        "privacy": "private"
    },
}

def mmdd(d: date) -> str:
    return f"{d.month:02d}-{d.day:02d}"

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_solar_terms(entries: dict, year: int, solar_terms_path: str):
    if not os.path.exists(solar_terms_path):
        return

    rows = load_json(solar_terms_path)
    for r in rows:
        if r.get("year") != year:
            continue
        k = r["mmdd"]
        if k not in entries:
            continue

        entries[k]["type"] = "solar_term"

        tags = set(entries[k].get("tags", []))
        tags.add("24_solar_terms")
        entries[k]["tags"] = sorted(tags)

        entries[k]["meta"]["name"] = r["name"]
        entries[k]["meta"]["calendar"] = "gregorian"
        entries[k]["meta"]["refs"] = [r.get("source", "solar_terms_unknown")]
        entries[k]["meta"]["notes"] = f"solar_term_index={r.get('index')}"

def apply_lunar_festivals(entries: dict, year: int, path: str):
    """
    把 data/lunar_festivals.json 里指定 year 的节日写入 entries[MM-DD]
    """
    with open(path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    for r in rows:
        if int(r.get("year")) != int(year):
            continue

        mmdd = r["mmdd"]          # '02-17'
        name = r["name"]          # '春节'
        key = r.get("key", "")    # 'spring_festival'
        lunar_md = r.get("lunar", "")

        if mmdd not in entries:
            continue  # 理论不会发生（entries 有全年），但保底

        # 覆盖/补齐：只动 type/tags/meta，不动 text
        e = entries[mmdd]
        e["type"] = "festival"
        tags = set(e.get("tags", []))
        tags.update(["lunar", "traditional_festival", key] if key else ["lunar", "traditional_festival"])
        e["tags"] = sorted(tags)

        meta = e.get("meta") or {}
        meta["name"] = name
        meta["calendar"] = "lunar"
        # refs：记录来源，方便以后追溯
        refs = meta.get("refs") or []
        refs.append("lunar_festivals_v1")
        meta["refs"] = sorted(set(refs))
        if lunar_md:
            meta["notes"] = (meta.get("notes","") + f" lunar={lunar_md}").strip()

        e["meta"] = meta
        # text 留空给 4o 填
        if "text" not in e:
            e["text"] = ""

def build_year_skeleton(year: int) -> dict:
    d = date(year, 1, 1)
    end = date(year + 1, 1, 1)

    entries = {}
    while d < end:
        key = mmdd(d)
        entries[key] = {
    "type": "daily",
    "tags": [],
    "meta": {
        "name": None,
        "calendar": "gregorian",
        "refs": [],
        "notes": ""
    },
    "text": ""
}

        d += timedelta(days=1)

    # 公历固定节日
    for k, v in FIXED_GREGORIAN_FESTIVALS.items():
        if k in entries:
            entries[k]["type"] = "festival"
            entries[k]["tags"] = v["tags"]
            entries[k]["meta"]["name"] = v["name"]
            entries[k]["meta"]["calendar"] = "gregorian"
            entries[k]["meta"]["refs"] = ["fixed_gregorian_v1"]
            entries[k]["text"] = ""

    # 自定义日
    for k, v in CUSTOM_DATES.items():
        if k in entries:
            entries[k]["type"] = "custom"
            entries[k]["tags"] = v["tags"]
            entries[k]["meta"]["name"] = v["name"]
            entries[k]["meta"]["calendar"] = "custom"
            entries[k]["meta"]["refs"] = ["custom_v1"]
            entries[k]["meta"]["notes"] = f"privacy={v.get('privacy','private')}"
            entries[k]["text"] = ""
    # 节气
    apply_solar_terms(entries, year, SOLAR_TERMS_PATH)
    apply_lunar_festivals(entries, year, LUNAR_FESTIVALS_PATH)
    return {
        "year": year,
        "timezone": TZ,
        "locale": LOCALE,
        "entries": entries
    }


def main(start_year: int, end_year: int, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)
    for y in range(start_year, end_year + 1):
        obj = build_year_skeleton(y)
        path = os.path.join(out_dir, f"{y}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        print("wrote", path)

if __name__ == "__main__":
    main(2026, 2085)
