import json
import os
from lunar_python import Lunar, Solar
from datetime import date, timedelta


# 你可以随时往里加
LUNAR_FESTS = [
    ("正月初一", "春节", "spring_festival"),
    ("正月十五", "元宵节", "lantern_festival"),
    ("五月初五", "端午节", "dragon_boat_festival"),
    ("七月初七", "七夕", "qixi"),
    ("八月十五", "中秋节", "mid_autumn"),
    ("九月初九", "重阳节", "double_ninth"),
    ("腊月初八", "腊八节", "laba"),
]

def _solar_to_mmdd(solar):
    # solar 可能是 Solar 对象
    if hasattr(solar, "getMonth") and hasattr(solar, "getDay"):
        return f"{solar.getMonth():02d}-{solar.getDay():02d}"
    # 或字符串
    if isinstance(solar, str) and len(solar) >= 10 and solar[4] == "-" and solar[7] == "-":
        return solar[5:7] + "-" + solar[8:10]
    raise TypeError(f"unsupported solar type: {type(solar)} value={solar!r}")

def _parse_lunar_md(md: str):
    """
    md 形如 '正月初一' / '八月十五' / '腊月廿九' 等
    用 lunar_python 的 Lunar.fromYmd 需要数字月日，所以这里先用 Lunar 自带转换：
    直接用 Lunar.fromYmd(year, month, day) 的话得我们自己把中文转数字，太麻烦。
    更稳：用 Lunar.fromYmd(year, 1, 1) 再通过 getFestivals? 但各版本不一。

    所以我们换一条确定可用的路：
    - 我们自己只支持这些固定写法：正月/二月/.../腊月 + 初一/十五/初五/初七/初八/初九
    这些足够覆盖常用节日。
    """
    month_map = {
        "正月": 1, "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6,
        "七月": 7, "八月": 8, "九月": 9, "十月": 10, "冬月": 11, "腊月": 12,
    }
    day_map = {
        "初一": 1, "初五": 5, "初七": 7, "初八": 8, "初九": 9,
        "十五": 15,
    }

    m = None
    for k in month_map:
        if md.startswith(k):
            m = month_map[k]
            rest = md[len(k):]
            break
    if m is None or rest not in day_map:
        raise ValueError(f"unsupported lunar md: {md}")

    d = day_map[rest]
    return m, d

def main(start_year=2026, end_year=2085, out_path="data/lunar_festivals.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []

    for year in range(start_year, end_year + 1):
        for md, name, key in LUNAR_FESTS:
            m, d = _parse_lunar_md(md)
            lunar = Lunar.fromYmd(year, m, d)  # 农历 year 的 m月d日
            solar = lunar.getSolar()           # 对应公历
            mmdd = _solar_to_mmdd(solar)

            rows.append({
                "year": year,
                "mmdd": mmdd,
                "name": name,
                "key": key,
                "lunar": md,
                "source": "lunar_python_v1"
            })
        # 除夕：本年正月初一（春节）的前一天
        cny = Lunar.fromYmd(year, 1, 1).getSolar()  # 本年 正月初一
        cny_date = date(cny.getYear(), cny.getMonth(), cny.getDay())
        chuxi_date = cny_date - timedelta(days=1)
        mmdd = f"{chuxi_date.month:02d}-{chuxi_date.day:02d}"

        rows.append({
            "year": year,
            "mmdd": mmdd,
            "name": "除夕",
            "key": "chuxi",
            "lunar": "除夕(春节前一日)",
            "source": "lunar_python_v1"
        })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"wrote {out_path} rows={len(rows)} expected={(end_year-start_year+1)*len(LUNAR_FESTS)}")

if __name__ == "__main__":
    main()