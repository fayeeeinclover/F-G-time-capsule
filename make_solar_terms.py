import json
import os
from lunar_python import Lunar

# 24节气顺序（用来给 index）
SOLAR_TERMS = [
    "小寒","大寒","立春","雨水","惊蛰","春分","清明","谷雨",
    "立夏","小满","芒种","夏至","小暑","大暑","立秋","处暑",
    "白露","秋分","寒露","霜降","立冬","小雪","大雪","冬至",
]

def _to_mmdd(val):
    """
    val 可能是：
    - Solar 对象（有 getMonth/getDay）
    - 字符串 'YYYY-MM-DD'
    - 其他：我们就打印出来方便排查
    """
    if hasattr(val, "getMonth") and hasattr(val, "getDay"):
        return f"{val.getMonth():02d}-{val.getDay():02d}"

    if isinstance(val, str):
        # 常见：'2026-02-04'
        s = val.strip()
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s[5:7] + "-" + s[8:10]

    raise TypeError(f"Unsupported JieQi value type: {type(val)} value={val!r}")

def main(start_year=2026, end_year=2085, out_path="data/solar_terms.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []

    for year in range(start_year, end_year + 1):
        # 关键：节气表在 Lunar 上
        # 用该年的 1/1（农历参数并不重要，我们只要“这一年的节气表”）
        table = Lunar.fromYmd(year, 1, 1).getJieQiTable()

        for idx, name in enumerate(SOLAR_TERMS, start=1):
            val = table.get(name)
            if val is None:
                raise RuntimeError(f"missing solar term: {year} {name}")

            mmdd = _to_mmdd(val)

            rows.append({
                "year": year,
                "mmdd": mmdd,
                "name": name,
                "index": idx,
                "source": "lunar_python_v1"
            })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"wrote {out_path} rows={len(rows)} expected={(end_year-start_year+1)*24}")

if __name__ == "__main__":
    main()