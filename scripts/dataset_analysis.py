"""
ML Dataset Analysis Script
============================
Analyzes ml_ready_dataset.csv for:
1. Major dataset problems / data quality issues
2. Most significant features for duration_ms and cost_usd
3. Boolean encoding problems (True/False usage)
4. Correlation heatmaps
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# ─── Styling ──────────────────────────────────────────────────────────────────
DARK_BG   = "#0d1117"
CARD_BG   = "#161b22"
ACCENT1   = "#58a6ff"
ACCENT2   = "#3fb950"
ACCENT3   = "#f85149"
ACCENT4   = "#d29922"
MUTED     = "#8b949e"
TEXT_COL  = "#e6edf3"

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    MUTED,
    "axes.labelcolor":   TEXT_COL,
    "xtick.color":       MUTED,
    "ytick.color":       MUTED,
    "text.color":        TEXT_COL,
    "grid.color":        "#21262d",
    "font.family":       "DejaVu Sans",
})

print("=" * 70)
print("  ML DATASET ANALYSIS  —  ml_ready_dataset.csv")
print("=" * 70)


from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
dataset_path = base_dir / "data" / "ml_ready_dataset" / "catboost_ready_dataset.csv"

df = pd.read_csv(dataset_path)
print(f"\n  Loaded  {df.shape[0]:,} rows  x  {df.shape[1]} columns")

bool_cols     = df.select_dtypes(include="bool").columns.tolist()
obj_cols      = df.select_dtypes(include=["object", "string"]).columns.tolist()
workload_cols = [c for c in df.columns if c.startswith("workload_")]
platform_cols = [c for c in df.columns if c.startswith("platform_")]

# Convert bools to int for numeric analysis if any boolean types exist
df_num = df.copy()
for c in bool_cols:
    df_num[c] = df_num[c].astype(int)
for c in obj_cols:
    df_num[c] = pd.factorize(df_num[c])[0]

feature_cols = [c for c in df_num.columns if c not in ["duration_ms", "cost_usd"]]

# ─── Feature Importance ───────────────────────────────────────────────────────
print("\nRunning Random Forest feature importance (40k sample)...")
sample = df_num.sample(40_000, random_state=42)
X = sample[feature_cols]

rf_dur  = RandomForestRegressor(n_estimators=120, max_depth=12, n_jobs=-1, random_state=42)
rf_cost = RandomForestRegressor(n_estimators=120, max_depth=12, n_jobs=-1, random_state=42)
rf_dur.fit(X, sample["duration_ms"])
rf_cost.fit(X, sample["cost_usd"])

imp_dur  = pd.Series(rf_dur.feature_importances_,  index=feature_cols).sort_values(ascending=False)
imp_cost = pd.Series(rf_cost.feature_importances_, index=feature_cols).sort_values(ascending=False)

TOP_N = 15
print(f"\nTop {TOP_N} features for duration_ms:")
for i, (f, v) in enumerate(imp_dur.head(TOP_N).items(), 1):
    print(f"  {i:2d}. {f:<42s} {v:.4f}")
print(f"\nTop {TOP_N} features for cost_usd:")
for i, (f, v) in enumerate(imp_cost.head(TOP_N).items(), 1):
    print(f"  {i:2d}. {f:<42s} {v:.4f}")

# ─── Platform/Workload stats ──────────────────────────────────────────────────
row_workload_sum = df_num[workload_cols].sum(axis=1) if workload_cols else pd.Series(0, index=df.index)
plat_sum         = df_num[platform_cols].sum(axis=1) if platform_cols else pd.Series(0, index=df.index)
has_mem_mb       = "memory_mb" in df.columns
corr_m           = df["memory"].corr(df["memory_mb"]) if has_mem_mb else None

# ─── Plot 1: Feature Importance ───────────────────────────────────────────────
import os; os.makedirs("reports", exist_ok=True)

def short(name):
    return (name.replace("workload_","wl_").replace("_xs_v1","")
                .replace("platform_","plt_").replace("runtime_","rt_")
                .replace("region_","rgn_"))

fig, axes = plt.subplots(1, 2, figsize=(20, 9))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("Feature Importance — Serverless ML Dataset", fontsize=17,
             fontweight="bold", color=TEXT_COL)

for ax, imp, target, color, label in [
    (axes[0], imp_dur,  "duration_ms", ACCENT1, "Duration (ms)"),
    (axes[1], imp_cost, "cost_usd",    ACCENT2, "Cost (USD)"),
]:
    top = imp.head(TOP_N)
    names = [short(n) for n in top.index]
    bars = ax.barh(names[::-1], top.values[::-1], color=color, alpha=0.85,
                   edgecolor="none", height=0.7)
    for bar, val in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=8.5, color=TEXT_COL)
    ax.set_title(f"->  {label}", fontsize=13, color=color, pad=10)
    ax.set_xlabel("Importance Score", fontsize=10)
    ax.grid(axis="x", alpha=0.3)
    ax.spines[["top","right"]].set_visible(False)

plt.tight_layout()
plt.savefig("reports/feature_importance.png", dpi=160, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("\n  Saved: reports/feature_importance.png")

# ─── Plot 2: Correlation Heatmap ──────────────────────────────────────────────
combined_imp = (imp_dur + imp_cost).sort_values(ascending=False)
top20_feats  = combined_imp.head(20).index.tolist()
heatmap_cols = top20_feats + ["duration_ms", "cost_usd"]
corr_df = df_num[heatmap_cols].corr()
corr_df = corr_df.rename(index={c: short(c) for c in heatmap_cols},
                          columns={c: short(c) for c in heatmap_cols})

fig, ax = plt.subplots(figsize=(18, 15))
fig.patch.set_facecolor(DARK_BG); ax.set_facecolor(CARD_BG)

cmap = sns.diverging_palette(230, 20, as_cmap=True)
hm = sns.heatmap(corr_df, ax=ax, cmap=cmap, center=0, vmin=-1, vmax=1,
                 linewidths=0.4, linecolor="#0d1117",
                 annot=True, fmt=".2f", annot_kws={"size": 7.5, "color": TEXT_COL},
                 square=True, cbar_kws={"shrink": 0.8, "aspect": 30})

cbar = hm.collections[0].colorbar
cbar.set_label("Pearson Correlation", color=TEXT_COL, fontsize=10)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COL)

ax.set_title("Correlation Heatmap — Top 20 Features + Targets",
             fontsize=15, fontweight="bold", color=TEXT_COL, pad=18)
ax.tick_params(axis="x", rotation=45, labelsize=8.5)
ax.tick_params(axis="y", rotation=0,  labelsize=8.5)

n = len(corr_df)
for i in [n-2, n-1]:
    ax.add_patch(plt.Rectangle((0, i), n, 1, fill=False, edgecolor=ACCENT4, lw=2.5))
for j in [n-2, n-1]:
    ax.add_patch(plt.Rectangle((j, 0), 1, n, fill=False, edgecolor=ACCENT4, lw=2.5))

plt.tight_layout()
plt.savefig("reports/correlation_heatmap.png", dpi=160, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("  Saved: reports/correlation_heatmap.png")

# ─── Plot 3: Dataset Problems Dashboard ───────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("Dataset Problems — Bool Encoding, Orphaned Rows & Duplicate Features",
             fontsize=14, fontweight="bold", color=TEXT_COL)

# 3a — Workload coverage pie
ax = axes[0]
if "workload" in df.columns:
    orphaned_count = df["workload"].isna().sum()
    has_label_count = df["workload"].notna().sum()
else:
    orphaned_count = (row_workload_sum == 0).sum()
    has_label_count = (row_workload_sum > 0).sum()

sizes  = [has_label_count, orphaned_count]
colors = [ACCENT2, ACCENT3]
labels = [f"Has Label\n({sizes[0]:,})", f"Orphaned\n({sizes[1]:,})"]
wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%",
    startangle=140, wedgeprops=dict(edgecolor=DARK_BG, lw=2),
    textprops=dict(color=TEXT_COL, fontsize=10))
for at in autotexts: at.set_color(DARK_BG); at.set_fontsize(10)
title_wl = "Workload Coverage\n(100% labeled - fixed)" if orphaned_count == 0 else "Workload Coverage\n(float_ops = implicit reference)"
ax.set_title(title_wl, color=ACCENT2 if orphaned_count == 0 else ACCENT3, fontsize=11)

# 3b — Platform distribution
ax = axes[1]
if "platform" in df.columns:
    vc = df["platform"].value_counts().to_dict()
    plat_data = {
        "AWS": vc.get("aws", 0),
        "Azure": vc.get("azure", 0),
        "Google": vc.get("google", 0)
    }
    plat_title = "Platform Distribution\n(Using platform column)"
elif "platform_aws" in df.columns:
    plat_data = {
        "AWS": int(df["platform_aws"].sum()),
        "Azure": int(df["platform_azure"].sum()),
        "Google": int(df["platform_google"].sum())
    }
    plat_title = "Platform Distribution\n(All platforms explicit - fixed)"
else:
    plat_data = {
        "AWS (implicit)": int((plat_sum == 0).sum()),
        "Azure": int(df["platform_azure"].sum()),
        "Google": int(df["platform_google"].sum())
    }
    plat_title = "Platform Distribution\n(AWS has no explicit column)"

bars = ax.bar(plat_data.keys(), plat_data.values(),
              color=[ACCENT4, ACCENT1, ACCENT2], edgecolor="none", width=0.5)
for bar, val in zip(bars, plat_data.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1500,
            f"{val:,}", ha="center", fontsize=10, color=TEXT_COL, fontweight="bold")
ax.set_title(plat_title, color=ACCENT4, fontsize=11)
ax.set_ylabel("Row count"); ax.grid(axis="y", alpha=0.3)
ax.spines[["top","right"]].set_visible(False)

# 3c — memory vs memory_mb scatter or memory vs duration
ax = axes[2]
s = df.sample(min(5000, len(df)), random_state=1)
if has_mem_mb:
    sc = ax.scatter(s["memory"], s["memory_mb"], alpha=0.25, s=8,
                    c=s["duration_ms"], cmap="plasma")
    ax.set_xlabel("memory (allocated tier, MB)")
    ax.set_ylabel("memory_mb (actual used, MB)")
    ax.set_title(f"Duplicate Feature Problem\ncorr(memory, memory_mb) = {corr_m:.3f}", color=ACCENT1, fontsize=11)
    cb = plt.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("duration_ms", color=TEXT_COL, fontsize=9)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=TEXT_COL)
else:
    sc = ax.scatter(s["memory"], s["duration_ms"], alpha=0.25, s=8,
                    c=s["cost_usd"], cmap="viridis")
    ax.set_xlabel("memory (allocated tier, MB)")
    ax.set_ylabel("duration_ms")
    ax.set_title("Memory Tier vs Duration\n(memory_mb dropped - clean)", color=ACCENT1, fontsize=11)
    cb = plt.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("cost_usd", color=TEXT_COL, fontsize=9)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=TEXT_COL)
ax.grid(alpha=0.3); ax.spines[["top","right"]].set_visible(False)

plt.tight_layout()
plt.savefig("reports/dataset_problems.png", dpi=160, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("  Saved: reports/dataset_problems.png")

print("\n  All done. 3 charts saved to reports/")
