"""Regenerate the graphs for the handwritten digit classifier project page.

Data sources (all real program output, nothing estimated):
  * test-saved-network.txt: `cargo run --release --bin sct_test_mlp` on the committed test.nnmlp.
  * train-cpu.txt: `sct_train_mlp` (CPU, one pass of SGD) timed with bash `time`, then sct_test_mlp.
  * train-gpu.txt: `sct_train_mlp_gpu` (OpenCL, 100 epochs, batch 32), then sct_test_mlp.
  * MNIST test images: data/t10k-*.idx*-ubyte from C:/Programming/computer_vision_rust
    (only needed for mnist-samples.png; pass another repo path as the first argument).

All runs were on 2026-11-06. Run:  python make_plots.py [path-to-computer_vision_rust]
PNGs are written to the parent folder (projects/digit-classifier/).
"""
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Programming/computer_vision_rust")
ACCENT = "#1f6feb"    # --accent in css/style.css
ACCENT_2 = "#f08a24"  # --accent-2 in css/style.css
GREY = "#6b7280"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e5e7eb", "grid.linewidth": 0.8,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)
    print("wrote", OUT / name)


def per_digit(path):
    text = (HERE / path).read_text()
    rows = re.findall(r"^(\d): (\d+)/(\d+)", text, re.M)
    correct = np.array([int(c) for _, c, _ in rows])
    total = np.array([int(t) for _, _, t in rows])
    c, t = map(int, re.search(r"Overall accuracy of \S+: (\d+)/(\d+)", text).groups())
    return correct / total * 100, c / t * 100


# ------------------------------------------------- per-digit accuracy of the saved network
acc, overall = per_digit("test-saved-network.txt")
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar(range(10), acc, color=ACCENT, width=0.65)
ax.axhline(overall, color=ACCENT_2, ls="--", lw=1.5, label=f"Overall: {overall:.2f}%")
for d, a in enumerate(acc):
    ax.text(d, a + 0.15, f"{a:.1f}", ha="center", fontsize=9)
ax.set_xticks(range(10))
ax.set_ylim(90, 100)
ax.set_xlabel("True digit")
ax.set_ylabel("Test accuracy (%)")
ax.set_title("Accuracy on 10,000 unseen MNIST test images")
ax.legend(frameon=False, loc="upper right")
save(fig, "accuracy-per-digit.png")

# ------------------------------------------------- CPU vs GPU training
cpu_log = (HERE / "train-cpu.txt").read_text()
gpu_log = (HERE / "train-gpu.txt").read_text()
m, s = re.search(r"real\s+(\d+)m([\d.]+)s", cpu_log).groups()
cpu_pass = int(m) * 60 + float(s)  # whole program: load, one pass over 60,000 samples, save
gpu_epochs = np.array([float(x) for x in re.findall(r"Epoch \d+/\d+ took ([\d.]+)ms", gpu_log)]) / 1000
_, cpu_acc = per_digit("train-cpu.txt")
_, gpu_acc = per_digit("train-gpu.txt")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.2))
labels = ["CPU\n(1 sample at a time)", "GPU, OpenCL\n(batches of 32)"]
times = [cpu_pass, gpu_epochs.mean()]
ax1.bar(labels, times, color=[GREY, ACCENT], width=0.55)
for i, t in enumerate(times):
    ax1.text(i, t + 0.05, f"{t:.2f} s", ha="center")
ax1.set_ylabel("Time for one pass over 60,000 images (s)")
ax1.set_title("Training speed")
ax1.set_ylim(0, max(times) * 1.18)

accs = [cpu_acc, gpu_acc]
ax2.bar(["CPU\n1 epoch", "GPU\n100 epochs"], accs, color=[GREY, ACCENT], width=0.55)
for i, a in enumerate(accs):
    ax2.text(i, a + 0.1, f"{a:.2f}%", ha="center")
ax2.set_ylim(90, 100)
ax2.set_ylabel("Test accuracy (%)")
ax2.set_title("Resulting accuracy")
save(fig, "cpu-vs-gpu.png")
print(f"CPU pass {cpu_pass:.2f} s, GPU mean epoch {gpu_epochs.mean():.3f} s "
      f"(total {gpu_epochs.sum():.1f} s); acc CPU {cpu_acc:.2f}%, GPU {gpu_acc:.2f}%")

# ------------------------------------------------- sample MNIST test digits (cover image)
img_path = REPO / "data/t10k-images.idx3-ubyte"
lbl_path = REPO / "data/t10k-labels.idx1-ubyte"
if img_path.exists():
    images = np.frombuffer(img_path.read_bytes(), np.uint8, offset=16).reshape(-1, 28, 28)
    labels = np.frombuffer(lbl_path.read_bytes(), np.uint8, offset=8)
    # The first two test images of each digit, in order, so nothing is cherry-picked.
    picks = [i for d in range(10) for i in np.flatnonzero(labels == d)[:2]]
    picks = sorted(picks, key=lambda i: (picks.index(i) % 2, labels[i]))
    fig, axes = plt.subplots(2, 10, figsize=(10, 2.6))
    for ax, i in zip(axes.flat, picks):
        ax.imshow(images[i], cmap="gray", vmin=0, vmax=255)
        ax.set_title(str(labels[i]), fontsize=12, color=ACCENT, fontweight="bold")
        ax.axis("off")
    fig.suptitle("MNIST test images (28 × 28 px) with their labels", fontsize=12, fontweight="bold")
    save(fig, "mnist-samples.png")

    # Card thumbnail: the first test image of each digit, 2 x 5 on black, no labels.
    first = [np.flatnonzero(labels == d)[0] for d in range(10)]
    grid = np.zeros((2 * 28 + 12, 5 * 28 + 24), np.uint8)
    for k, i in enumerate(first):
        r, c = divmod(k, 5)
        grid[4 + r * 32:4 + r * 32 + 28, 4 + c * 32:4 + c * 32 + 28] = images[i]
    fig = plt.figure(figsize=(8, 8 * grid.shape[0] / grid.shape[1]), facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(grid, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    ax.axis("off")
    fig.savefig(OUT / "card-thumb.png", dpi=100, facecolor="black")
    plt.close(fig)
    print("wrote", OUT / "card-thumb.png")
else:
    print("MNIST data not found, skipped mnist-samples.png")
