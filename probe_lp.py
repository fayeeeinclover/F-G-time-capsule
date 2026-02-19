from lunar_python import Solar, Lunar, LunarYear

def list_methods(obj, keywords=("jie", "qi", "节气", "JieQi", "Qi")):
    ms = []
    for m in dir(obj):
        low = m.lower()
        if any(k.lower() in low for k in keywords if isinstance(k, str)):
            ms.append(m)
    return ms

print("Solar:", type(Solar.fromYmd(2026, 1, 1)))
print("Solar methods hit:", list_methods(Solar.fromYmd(2026, 1, 1)))

l = Lunar.fromYmd(2026, 1, 1)
print("\nLunar:", type(l))
print("Lunar methods hit:", list_methods(l))

ly = LunarYear.fromYear(2026)
print("\nLunarYear:", type(ly))
print("LunarYear methods hit:", list_methods(ly))