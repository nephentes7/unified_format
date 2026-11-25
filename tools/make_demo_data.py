"""Fake demo data for the repository: a Collect Earth export (event slots), split into two operator files, with made-up
classes, coordinates, operators and answers; plus a lookup of forest-type rules, a lexicon and a period history lookup.
Nothing comes from a country's data. Usage: make_demo.py <folder>"""
import os, sys, random
import pandas as pd

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rnd = random.Random(2027)
END = 2024
FOREST = ["dense_forest", "open_forest", "gallery_forest", "riparian_forest", "plantation"]
NONF = {"C": ["annual_crop", "tree_crop"], "G": ["wooded_savanna", "grassland"], "S": ["settlement"], "W": ["water"], "O": ["bare_soil"]}
LABEL = {"dense_forest": "Dense forest", "open_forest": "Open forest", "gallery_forest": "Gallery forest", "riparian_forest": "Riparian forest",
         "plantation": "Plantation", "annual_crop": "Annual crop", "tree_crop": "Tree crop", "wooded_savanna": "Wooded savanna",
         "grassland": "Grassland", "settlement": "Settlement", "water": "Water", "bare_soil": "Bare soil"}
LU_LABEL = {"F": "Forest land", "C": "Cropland", "G": "Grassland", "S": "Settlements", "W": "Wetlands", "O": "Other land"}
LU_OF = {s: "F" for s in FOREST} | {s: k for k, v in NONF.items() for s in v}
DRIVERS = ["agriculture", "logging", "fire", "settlement", "mining"]


def pick_nonforest():
    k = rnd.choices(list(NONF), weights=[40, 40, 6, 6, 8])[0]
    return rnd.choice(NONF[k])


def plot_story():
    """the land in the end year and the events (newest first, as Collect Earth asks): [(year, from_sub, driver)]."""
    r = rnd.random()
    y1, y2 = sorted(rnd.sample(range(2014, END + 1), 2))
    if r < 0.30:                                   # stable forest
        return rnd.choices(FOREST, weights=[30, 35, 8, 7, 20])[0], [], ""
    if r < 0.62:                                   # stable non-forest
        return pick_nonforest(), [], ""
    if r < 0.72:                                   # deforestation
        return rnd.choice(["annual_crop", "tree_crop", "grassland"]), [(y1, rnd.choice(["dense_forest", "open_forest", "plantation"]), rnd.choice(DRIVERS))], ""
    if r < 0.79:                                   # degradation: dense -> open (a change of forest type)
        return "open_forest", [(y1, "dense_forest", rnd.choice(["logging", "fire"]))], ""
    if r < 0.82:                                   # degradation: a disturbance, no change of class
        return "dense_forest", [(y1, "dense_forest", rnd.choice(["logging", "fire"]))], ""   # an event with the same class
    if r < 0.88:                                   # afforestation / regrowth
        return rnd.choice(["open_forest", "plantation"]), [(y1, rnd.choice(["grassland", "annual_crop"]), "")], ""
    if r < 0.91:                                   # forest -> non-forest -> forest (cyclical)
        return "open_forest", [(y2, "annual_crop", ""), (y1, "open_forest", "agriculture")], ""
    if r < 0.93:                                   # gallery <-> riparian (hard to tell apart: a merge in Step 6)
        return "riparian_forest", [(y1, "gallery_forest", "")], ""
    if r < 0.96:                                   # wooded savanna -> grassland (national choice: reclassify)
        return "grassland", [(y1, "wooded_savanna", "fire")], ""
    a = pick_nonforest()
    b = rnd.choice([x for v in NONF.values() for x in v if x != a])
    return a, [(y1, b, "")], ""                                     # non-forest change (two different classes)


rows = []
for i in range(1, 401):
    end_sub, events, disturbance = plot_story()
    events = sorted(events, key=lambda e: -e[0])
    r = {"id": 1000 + i, "location_x": round(10.0 + (i % 20) * 0.05 + rnd.uniform(-0.01, 0.01), 6),
         "location_y": round(5.0 + (i // 20) * 0.05 + rnd.uniform(-0.01, 0.01), 6),
         "operator": "operator_A" if i <= 200 else "operator_B", "actively_saved": "true",
         "plot_file": "demo_A.csv" if i <= 200 else "demo_B.csv",
         "lu_t2": LU_OF[end_sub], "lu_t2_label": LU_LABEL[LU_OF[end_sub]], "sub_t2": end_sub, "sub_t2_label": LABEL[end_sub]}
    for k in range(1, 4):
        if k <= len(events):
            y, frm, drv = events[k - 1]
            r.update({f"event[{k}]_event_num": k, f"event[{k}]_change_yr": y, f"event[{k}]_change_yr_label": y,
                      f"event[{k}]_from_lu": LU_OF[frm], f"event[{k}]_from_lu_label": LU_LABEL[LU_OF[frm]],
                      f"event[{k}]_from_sub": frm, f"event[{k}]_from_sub_label": LABEL[frm],
                      f"event[{k}]_disturbance": drv, f"event[{k}]_driver_regrowth": ""})
        else:
            r.update({f"event[{k}]_{c}": "" for c in ("event_num", "change_yr", "change_yr_label", "from_lu", "from_lu_label",
                                                     "from_sub", "from_sub_label", "disturbance", "driver_regrowth")})
    r["uncert"] = rnd.choice(["low", "medium", "high"])
    rows.append(r)
data = pd.DataFrame(rows)
for name, part in (("demo_collect_earth_operator_A.csv", data[data["operator"] == "operator_A"]),
                   ("demo_collect_earth_operator_B.csv", data[data["operator"] == "operator_B"])):
    os.makedirs(os.path.join(OUT, "exports"), exist_ok=True)
    part.to_csv(os.path.join(OUT, "exports", name), index=False)

print(data["sub_t2"].value_counts().to_dict())
print("events:", (data["event[1]_change_yr"] != "").sum(), "plots with a disturbance-only story: kept as end-year answers")
