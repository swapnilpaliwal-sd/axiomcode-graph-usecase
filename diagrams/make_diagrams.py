"""Draws the call-graph diagrams in this folder. Run: python3 diagrams/make_diagrams.py"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).parent
INK, MUTED, BG = "#1f2328", "#57606a", "#ffffff"
STYLE = {
    "resolved": dict(color="#1f6feb", ls="-", lw=2.0),
    "registered": dict(color="#1a7f37", ls="-", lw=2.0),
    "asserted": dict(color="#8250df", ls=(0, (6, 4)), lw=2.2),
    "unknown": dict(color="#cf222e", ls=(0, (1, 3)), lw=2.0),
}

NODES = {
    "test_place_order…": (1.2, 6.0, "test"),
    "place_order": (1.2, 4.6, "fn"),
    "OrderService.place": (1.2, 3.2, "fn"),
    "price_for": (0.0, 1.8, "fn"),
    "apply_discount": (0.0, 0.4, "fn"),
    "CardGateway.charge": (2.4, 1.8, "fn"),
    "EventBus.emit": (4.6, 3.2, "fn"),
    "receipts.<module>": (6.9, 6.0, "fn"),
    "send_receipt": (6.9, 4.6, "fn"),
    "dispatch": (6.9, 3.2, "fn"),
    "notify_email": (5.9, 0.9, "fn"),
    "notify_sms": (8.0, 0.9, "fn"),
}
LABEL_AT = {("EventBus.emit", "send_receipt"): (4.6, 4.3), ("dispatch", "notify_email"): (5.3, 2.0)}
BASE = [
    ("test_place_order…", "place_order", "resolved", ""),
    ("place_order", "OrderService.place", "resolved", ""),
    ("OrderService.place", "price_for", "resolved", ""),
    ("price_for", "apply_discount", "resolved", ""),
    ("OrderService.place", "CardGateway.charge", "resolved", "self.payment.charge"),
    ("OrderService.place", "EventBus.emit", "resolved", ""),
    ("receipts.<module>", "send_receipt", "registered", "bus.subscribe(…)"),
    ("send_receipt", "dispatch", "resolved", ""),
]


def node(ax, name, x, y, kind, dim=False):
    w, h = W, H
    face = "#fff8c5" if kind == "test" else "#f6f8fa"
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc=face, ec=MUTED if dim else INK, lw=1.3, alpha=0.55 if dim else 1))
    ax.text(x, y, name, ha="center", va="center", fontsize=10.5, family="monospace",
            color=MUTED if dim else INK)


W, H = 1.75, 0.62


def border(x, y, tx, ty, pad=0.06):
    # where the segment from a box's centre toward (tx, ty) leaves the box
    dx, dy = tx - x, ty - y
    t = min((W / 2 + pad) / abs(dx) if dx else 9e9, (H / 2 + pad) / abs(dy) if dy else 9e9)
    return x + dx * t, y + dy * t


def edge(ax, a, b, tier, label="", rad=0.0):
    (x1, y1, _), (x2, y2, _) = NODES[a], NODES[b]
    s = STYLE[tier]
    ax.add_patch(FancyArrowPatch(border(x1, y1, x2, y2), border(x2, y2, x1, y1), arrowstyle="-|>",
                                 mutation_scale=16, color=s["color"], linestyle=s["ls"], lw=s["lw"],
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        lx, ly = LABEL_AT.get((a, b), ((x1 + x2) / 2 + 0.08, (y1 + y2) / 2 + 0.12))
        ax.text(lx, ly, label, fontsize=8.5, color=s["color"],
                family="monospace", ha="left")


def stub(ax, a, label):
    x, y, _ = NODES[a]
    ax.add_patch(FancyArrowPatch((x, y - H / 2 - 0.05), (x, y - 1.0), arrowstyle="-", color=STYLE["unknown"]["color"],
                                 linestyle=STYLE["unknown"]["ls"], lw=2))
    ax.text(x, y - 1.2, "?", fontsize=14, weight="bold", color=STYLE["unknown"]["color"], ha="center")
    ax.text(x, y - 1.6, label, fontsize=8.5, color=STYLE["unknown"]["color"], family="monospace", ha="center")


def legend(ax, tiers=("resolved", "registered", "asserted", "unknown")):
    words = {"resolved": "resolved — the graph proved the call",
             "registered": "registered — passed as a callback",
             "asserted": "asserted — an agent ran `axiomcode link`",
             "unknown": "unknown — a call through a value (to resolve)"}
    for i, t in enumerate(tiers):
        s = STYLE[t]
        x, y = -0.8 + (i % 2) * 5.0, -0.75 - (i // 2) * 0.45
        head = "-" if t == "unknown" else "-|>"
        ax.add_patch(FancyArrowPatch((x, y), (x + 0.7, y), arrowstyle=head, mutation_scale=12, color=s["color"],
                                     linestyle=s["ls"], lw=s["lw"]))
        if t == "unknown":
            ax.text(x + 0.66, y, "?", va="center", fontsize=12, weight="bold", color=s["color"])
        ax.text(x + 0.85, y, words[t], va="center", fontsize=9.5, color=INK)


def canvas(title, sub):
    fig, ax = plt.subplots(figsize=(11.5, 8.2), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(-1.0, 9.4)
    ax.set_ylim(-1.8, 7.2)
    ax.axis("off")
    ax.text(-0.9, 7.0, title, fontsize=15, weight="bold", color=INK)
    ax.text(-0.9, 6.6, sub, fontsize=10, color=MUTED)
    return fig, ax


def draw(path, title, sub, extra=(), stubs=(), dim=()):
    fig, ax = canvas(title, sub)
    for a, b, t, lbl in BASE:
        edge(ax, a, b, t, lbl)
    for a, b, t, lbl, rad in extra:
        edge(ax, a, b, t, lbl, rad)
    for a, lbl in stubs:
        stub(ax, a, lbl)
    for n, (x, y, k) in NODES.items():
        node(ax, n, x, y, k, dim=n in dim)
    legend(ax)
    fig.savefig(path, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


draw(OUT / "01-before-link.png", "Before: the graph stops at two calls through a value",
     "notify_email has no caller the graph can see, so `impact notify_email` says nothing reaches it and no test covers it",
     stubs=[("EventBus.emit", "fn(payload)\nevents.py:13"), ("dispatch", "handler(message)\nnotify.py:16")],
     dim={"notify_email", "notify_sms"})

draw(OUT / "02-after-link.png", "After: three `axiomcode link` rows bridge the gaps",
     "impact, path and tests now walk the dashed edges, each labelled [asserted]",
     extra=[("EventBus.emit", "send_receipt", "asserted", "fn(payload)", -0.25),
            ("dispatch", "notify_email", "asserted", "handler(message)", 0.0),
            ("dispatch", "notify_sms", "asserted", "", 0.0)])


def workflow(path):
    fig, ax = plt.subplots(figsize=(14, 3.6), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    steps = [("1. ask", "axiomcode impact X\nor path A B"),
             ("2. read to resolve", "file:line:col\n+ candidates (leads)"),
             ("3. read the call", "does the code make\nthe target certain?"),
             ("4. link", "axiomcode link\nfile:line:col target"),
             ("5. ask again", "edges show\n[asserted]")]
    for i, (h, b) in enumerate(steps):
        x = 0.3 + i * 2.75
        hot = h == "4. link"
        ax.add_patch(FancyBboxPatch((x, 0.9), 2.3, 1.8, boxstyle="round,pad=0.04,rounding_size=0.15",
                                    fc="#fbefff" if hot else "#f6f8fa",
                                    ec=STYLE["asserted"]["color"] if hot else INK, lw=2.2 if hot else 1.3,
                                    linestyle=STYLE["asserted"]["ls"] if hot else "-"))
        ax.text(x + 1.15, 2.3, h, ha="center", fontsize=11, weight="bold", color=INK)
        ax.text(x + 1.15, 1.5, b, ha="center", va="center", fontsize=9, family="monospace", color=INK)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + 2.33, 1.8), (x + 2.72, 1.8), arrowstyle="-|>", mutation_scale=16,
                                         color=MUTED, lw=2))
    ax.text(6.9, 0.35, "not certain? do not link. A candidate is a lead, never a fact — leave the site unknown.",
            ha="center", fontsize=9.5, color=MUTED)
    fig.savefig(path, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


workflow(OUT / "03-link-workflow.png")
