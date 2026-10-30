"""Draws spec-to-rule.png. Run: python3 make_diagram.py"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK, BLUE, RED, GREEN = "#1f2328", "#1f6feb", "#cf222e", "#1a7f37"
W, H = 1.8, 0.6
P = {"banUser": (1.0, 3.0), "deleteUser": (1.0, 0.6), "removeUser": (4.4, 1.8), "audit": (7.2, 3.0)}

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
fig.patch.set_facecolor("white")
ax.set_xlim(-0.3, 8.3)
ax.set_ylim(-0.4, 4.6)
ax.axis("off")


def border(x, y, tx, ty, pad=0.06):
    dx, dy = tx - x, ty - y
    t = min((W / 2 + pad) / abs(dx) if dx else 9e9, (H / 2 + pad) / abs(dy) if dy else 9e9)
    return x + dx * t, y + dy * t


def edge(a, b, color):
    (x1, y1), (x2, y2) = P[a], P[b]
    ax.add_patch(FancyArrowPatch(border(x1, y1, x2, y2), border(x2, y2, x1, y1), arrowstyle="-|>",
                                 mutation_scale=16, color=color, lw=2.2))


edge("banUser", "removeUser", BLUE)
edge("banUser", "audit", BLUE)
edge("deleteUser", "removeUser", BLUE)

for name, (x, y) in P.items():
    bad = name == "deleteUser"
    ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc="#ffebe9" if bad else "#f6f8fa", ec=RED if bad else INK, lw=1.6))
    ax.text(x, y, name, ha="center", va="center", fontsize=11, family="monospace", color=INK)

ax.text(-0.2, 4.35, "Spec: every function that removes a user also writes to the audit log", fontsize=12.5,
        weight="bold", color=INK)
ax.text(-0.2, 4.0, "Rule: list functions that call removeUser but never call audit", fontsize=10.5, color=INK)
ax.text(1.0, 3.5, "✓ calls removeUser and audit", color=GREEN, fontsize=10.5, weight="bold", ha="center")
ax.text(1.0, 0.05, "✗ calls removeUser, never audit", color=RED, fontsize=10.5, weight="bold", ha="center")
ax.text(5.2, 0.05, "→  a call the graph found", color=BLUE, fontsize=10)
fig.savefig("spec-to-rule.png", bbox_inches="tight", facecolor="white")
