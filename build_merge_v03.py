"""Merge v0.3: append 8 new domestic DBs (112 items) from modb.pro dbRank Top 15.
Order by modb rank: kingbase(2), polardb(4), goldendb(5), tdsql(7), gaussdb(9), tdengine(10), yashandb(11), opengauss(13).
Pingkai (#6) = TiDB commercial edition, NOT duplicated (verified by subagent).
Updates data/toolbox-filled.json (with SQL) and data/toolbox.json (list, no SQL),
and appends a v0.3 section to docs/DBA_TOOLBOX_LIST.md.
"""
import json, copy

NEW = ["kingbase", "polardb", "goldendb", "tdsql", "gaussdb", "tdengine", "yashandb", "opengauss"]

def strip_sql(db):
    d = copy.deepcopy(db)
    for c in d["categories"]:
        for s in c.get("subcategories", []):
            for it in s.get("items", []):
                it.pop("sql", None)
    return d

new_dbs = [json.load(open(f"data/toolbox-{x}.json")) for x in NEW]

for fname, with_sql in [("data/toolbox-filled.json", True), ("data/toolbox.json", False)]:
    d = json.load(open(fname))
    assert d["total_items"] == 215, (fname, d["total_items"])
    d["databases"].extend(new_dbs if with_sql else [strip_sql(x) for x in new_dbs])
    d["total_items"] = 327
    d["version"] = "0.3-filled" if with_sql else "0.3"
    d["updated"] = "2026-11-24"
    json.dump(d, open(fname, "w"), ensure_ascii=False, indent=2)
    print(fname, "->", d["total_items"], "dbs:", len(d["databases"]))

# validate merged filled
d = json.load(open("data/toolbox-filled.json"))
ids, missing = [], 0
for db in d["databases"]:
    for c in db["categories"]:
        for s in c.get("subcategories", []):
            for it in s.get("items", []):
                ids.append(it["id"])
                if not it.get("sql", "").strip():
                    missing += 1
assert len(ids) == 327 and len(set(ids)) == 327 and missing == 0, (len(ids), len(set(ids)), missing)
print("merged validation OK: 327 items, unique ids, missing sql = 0")

# append docs section
lines = ["\n## v0.3 新增（112 条）· 墨天轮 2026-11 榜单国产库\n",
         "\n来源：https://www.modb.pro/dbRank（2026 年 11 月，136 个数据库参与）。",
         "第一批只补关系型 Top 15 里缺的 8 个库，每库 14 条；平凯数据库（第 6 名）经核实是 TiDB 商业版，不重复建库，改补第 10 名 TDengine。",
         "脚本均从各库官方手册提取，未在真实环境跑过的条目 notes 里标“需实测核对”。\n"]
for db in new_dbs:
    n = sum(len(s.get("items", [])) for c in db["categories"] for s in c.get("subcategories", []))
    lines.append(f"\n## {db['name']}（{n} 条）· {db['versions']}\n")
    for c in db["categories"]:
        lines.append(f"\n### {c['name']}\n")
        for s in c.get("subcategories", []):
            lines.append(f"\n#### {s['name']}\n\n| 脚本 / 命令 | 适用版本 | 风险 | 说明 |\n|---|---|---|---|\n")
            for it in s.get("items", []):
                lines.append(f"| {it['title']} | {it['versions']} | {it['risk']} | {it['desc']} |\n")
open("docs/DBA_TOOLBOX_LIST.md", "a").write("".join(lines))
print("docs appended")
