import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

df = xl("A1:H39", headers=True)

plt.style.use("seaborn-v0_8-whitegrid")

plt.rcParams["font.sans-serif"] = [
    "Microsoft JhengHei",
    "PingFang TC",
    "Arial Unicode MS",
    "SimHei"
]
plt.rcParams["axes.unicode_minus"] = False

x = df["Total Business Size & Potential"]
y = df["Capabilities"]

x_avg = 35
y_avg = 35

fig, ax = plt.subplots(figsize=(11.5, 7.2))

tier_colors = {
    "T1": "#000066",
    "T2": "#375623",
    "T3": "#C65911"
}

# scatter
ax.scatter(
    x, y,
    s=78,
    color="#000066",
    alpha=0.92,
    edgecolors="white",
    linewidth=1,
    zorder=3
)

# quadrant lines
ax.axvline(x_avg, linestyle="--", linewidth=0.9, color="#000066", zorder=1)
ax.axhline(y_avg, linestyle="--", linewidth=0.9, color="#000066", zorder=1)

x_min = x.min() - 2
x_max = x.max() + 4.5
y_min = y.min() - 2
y_max = y.max() + 1.5

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

plot_df = df.copy()
plot_df["x"] = x
plot_df["y"] = y

plot_df = plot_df.sort_values(
    ["Total Business Size & Potential", "Capabilities"],
    ascending=[False, False]
).reset_index(drop=True)

placed = []

# stronger collision threshold
min_dx = 3.8
min_dy = 1.8

# expanded offsets
offset_candidates = [
    (10,0),(12,8),(12,-8),(16,14),(16,-14),
    (22,0),(24,10),(24,-10),(30,16),(30,-16),
    (36,0),(38,12),(38,-12),(44,18),(44,-18),
    (-10,0),(-12,8),(-12,-8),(-16,14),(-16,-14),
    (-22,0),(-24,10),(-24,-10),(-30,16),(-30,-16)
]

def offset_to_data(ax, xi, yi, dx_pt, dy_pt):
    p0 = ax.transData.transform((xi, yi))
    p1 = (p0[0] + dx_pt, p0[1] + dy_pt)
    x1, y1 = ax.transData.inverted().transform(p1)
    return x1, y1

for i, row in plot_df.iterrows():

    xi = row["x"]
    yi = row["y"]

    txt = (
        str(row["WS"])
        .replace("股份有限公司", "")
        .replace("有限公司", "")
        .replace("(桃竹專用)", "")
        .replace("(任我行)", "")
        .strip()
    )

    label_color = tier_colors.get(row["Tier"], "#333333")

    # quadrant preference
    if xi >= x_avg and yi >= y_avg:
        preferred = [
            (14,10),(14,-10),(22,14),(22,-14),
            (30,16),(30,-16),(36,20),(36,-20),
            (-14,10),(-14,-10)
        ]
    elif xi >= x_avg:
        preferred = [
            (10,0),(12,8),(12,-8),(18,12),(18,-12),
            (-10,0),(-12,8),(-12,-8)
        ]
    elif yi >= y_avg:
        preferred = [
            (10,0),(12,8),(12,-8),(18,12),(18,-12),
            (22,0),(-10,0)
        ]
    else:
        preferred = [
            (10,0),(12,8),(12,-8),(18,12),(18,-12),
            (22,0),(-10,0)
        ]

    candidates = preferred + [c for c in offset_candidates if c not in preferred]

    chosen = None
    best_score = None

    for dx_pt, dy_pt in candidates:

        xt, yt = offset_to_data(ax, xi, yi, dx_pt, dy_pt)

        penalty = 0
        if xt < x_min + 0.8 or xt > x_max - 0.8:
            penalty += 10
        if yt < y_min + 0.6 or yt > y_max - 0.6:
            penalty += 10

        overlap = False
        overlap_penalty = 0

        for px, py in placed:
            dx = abs(xt - px)
            dy = abs(yt - py)

            if dx < min_dx and dy < min_dy:
                overlap = True
                overlap_penalty += ((min_dx - dx) + (min_dy - dy)) * 3

        distance_penalty = abs(dx_pt) * 0.03 + abs(dy_pt) * 0.04

        score = penalty + overlap_penalty * 15 + distance_penalty

        if best_score is None or score < best_score:
            best_score = score
            chosen = (dx_pt, dy_pt, xt, yt, overlap)

        if not overlap and score < 2:
            break

    dx_pt, dy_pt, xt, yt, _ = chosen

    ha = "left" if dx_pt >= 0 else "right"

    if dy_pt > 3:
        va = "bottom"
    elif dy_pt < -3:
        va = "top"
    else:
        va = "center"

    placed.append((xt, yt))

    ax.annotate(
        txt,
        xy=(xi, yi),
        xytext=(dx_pt, dy_pt),
        textcoords="offset points",
        fontsize=9,
        color=label_color,
        ha=ha,
        va=va,
        zorder=4,
        arrowprops=dict(
            arrowstyle="-",
            color="#666666",
            lw=0.5,
            alpha=0.5,
            shrinkA=0,
            shrinkB=0
        ),
        clip_on=False
    )

ax.set_title(
    "Distributor Matrix",
    fontsize=16,
    weight="bold",
    pad=12,
    color="#222222",
    fontname="Calibri"
)

ax.set_xlabel(
    "Total Business Size & Potential",
    fontsize=11,
    color="#444444",
    fontname="Calibri"
)

ax.set_ylabel(
    "Capabilities",
    fontsize=11,
    color="#444444",
    fontname="Calibri"
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color("#C8C8C8")
ax.spines["bottom"].set_color("#C8C8C8")

ax.spines["left"].set_linewidth(0.8)
ax.spines["bottom"].set_linewidth(0.8)

ax.tick_params(axis="both", colors="#666666", labelsize=10)

ax.grid(True, color="#EAEAEA", linewidth=0.8)
ax.set_axisbelow(True)

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='T1',
           markerfacecolor=tier_colors["T1"], markersize=8),
    Line2D([0], [0], marker='o', color='w', label='T2',
           markerfacecolor=tier_colors["T2"], markersize=8),
    Line2D([0], [0], marker='o', color='w', label='T3',
           markerfacecolor=tier_colors["T3"], markersize=8)
]

ax.legend(
    handles=legend_elements,
    title="Tier",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False,
    prop={"family": "Calibri", "size": 10},
    title_fontproperties={"family": "Calibri", "size": 10}
)

plt.tight_layout()
plt.show()
