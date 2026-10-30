"""Draws the diagrams in this folder. Run: python3 diagrams/make_diagrams.py"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).parent
INK, MUTED, BG = "#1f2328", "#57606a", "#ffffff"
OK, BAD = "#1a7f37", "#cf222e"
STYLE = {
    "resolved": dict(color="#1f6feb", ls="-", lw=2.0),
    "registered": dict(color="#1a7f37", ls="-", lw=2.0),
    "asserted": dict(color="#8250df", ls=(0, (6, 4)), lw=2.2),
    "unknown": dict(color="#cf222e", ls=(0, (1, 3)), lw=2.0),
}
W, H = 1.9, 0.6


def box(ax, x, y, text, w=W, h=H, face="#f6f8fa", edge=INK, mono=True, size=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc=face, ec=edge, lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=INK, weight=weight,
            family="monospace" if mono else None)


def border(x, y, tx, ty, w=W, h=H, pad=0.06):
    dx, dy = tx - x, ty - y
    t = min((w / 2 + pad) / abs(dx) if dx else 9e9, (h / 2 + pad) / abs(dy) if dy else 9e9)
    return x + dx * t, y + dy * t


def arrow(ax, a, b, tier, label="", at=None, head=True):
    s = STYLE[tier]
    ax.add_patch(FancyArrowPatch(border(*a, *b), border(*b, *a), arrowstyle="-|>" if head else "-",
                                 mutation_scale=15, color=s["color"], linestyle=s["ls"], lw=s["lw"]))
    if label:
        x, y = at or ((a[0] + b[0]) / 2 + 0.1, (a[1] + b[1]) / 2)
        ax.text(x, y, label, fontsize=8.5, color=s["color"], family="monospace")


def pipeline(path):
    fig, ax = plt.subplots(figsize=(15, 4.4), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    steps = [
        ("SPEC.md", "S2  Every deletion of a\nnote is written to the\naudit log."),
        ("the words, in code", "deletion = reaches\n  SqlNoteStore.remove\naudit log = reaches\n  audit"),
        ("rules/S2-….sql", "every handler that\nreaches .remove\n=> it reaches audit"),
        ("axiomcode index", "builds the OSS graph\n.axiomcode/out/\n  graph.sqlite"),
        ("node rules/check.ts", "runs every rule\nagainst the graph"),
    ]
    for i, (h, b) in enumerate(steps):
        x = 1.35 + i * 2.85
        box(ax, x, 2.45, "", w=2.45, h=2.2)
        ax.text(x, 3.25, h, ha="center", fontsize=11, weight="bold", color=INK)
        ax.text(x, 2.2, b, ha="center", va="center", fontsize=8.8, family="monospace", color=INK)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + 1.27, 2.45), (x + 1.58, 2.45), arrowstyle="-|>", mutation_scale=15,
                                         color=MUTED, lw=2))
    for j, (word, color, note) in enumerate([("✓ ok", OK, "the graph proved it"),
                                             ("✗ violation", BAD, "the graph proved it is missing"),
                                             ("unsure", STYLE["asserted"]["color"], "a call it could not follow: read, link, re-check")]):
        y = 0.95 - j * 0.38
        ax.text(9.9, y, word, fontsize=10, weight="bold", color=color)
        ax.text(11.35, y, note, fontsize=9, color=INK)
    ax.text(0.15, 4.15, "From a requirement to a check that runs after every build", fontsize=14, weight="bold", color=INK)
    fig.savefig(path, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def gap(path):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), dpi=150)
    fig.patch.set_facecolor(BG)
    P = {"clearNotes": (1.2, 4.2), "deleted": (1.2, 2.6), "whenDeleted": (4.6, 4.2),
         "auditDeletion": (4.6, 2.6), "audit": (4.6, 1.0)}
    for ax, after in zip(axes, (False, True)):
        ax.set_xlim(-0.2, 6.2)
        ax.set_ylim(-0.6, 5.3)
        ax.axis("off")
        arrow(ax, P["clearNotes"], P["deleted"], "resolved", "deleted(user, id)", at=(1.3, 3.45))
        arrow(ax, P["whenDeleted"], P["auditDeletion"], "registered", "whenDeleted(auditDeletion)", at=(4.7, 3.45))
        arrow(ax, P["auditDeletion"], P["audit"], "resolved")
        if after:
            arrow(ax, P["deleted"], P["auditDeletion"], "asserted", "hook(user, id)", at=(2.2, 2.75))
        else:
            x, y = P["deleted"]
            ax.add_patch(FancyArrowPatch((x, y - H / 2 - 0.05), (x, y - 1.15), arrowstyle="-",
                                         color=STYLE["unknown"]["color"], linestyle=STYLE["unknown"]["ls"], lw=2))
            ax.text(x, y - 1.4, "?", fontsize=14, weight="bold", color=BAD, ha="center")
            ax.text(x, y - 1.75, "hook(user, id)\nsrc/hooks.ts:10:32", fontsize=8.5, color=BAD, ha="center",
                    family="monospace")
        for n, (x, y) in P.items():
            box(ax, x, y, n, face="#fff8c5" if n == "clearNotes" else "#f6f8fa")
        verdict = ("✓ S2 ok  [through an asserted link]", OK) if after else ("✗ S2 violation: clearNotes does not reach audit", BAD)
        ax.text(-0.1, 5.05, "After `axiomcode link src/hooks.ts:10:32 auditDeletion`" if after else "Before: the rule stops at a call through a value",
                fontsize=12, weight="bold", color=INK)
        ax.text(-0.1, -0.45, verdict[0], fontsize=11, weight="bold", color=verdict[1])
    fig.savefig(path, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


pipeline(OUT / "01-spec-to-rules.png")
gap(OUT / "02-rule-gap-and-link.png")
