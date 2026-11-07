"""Regenerate the graphs for the ultrasonic ranging module project page.

Data sources (all real, nothing estimated):
  * experiment-1-data.xlsx: the 100 raw HC-SR04 readings per fixed distance from Test 1
    (calibration), recorded with the MATLAB script in Appendix A of the technical report.
  * MODEL_CHECK: Table 2 of the technical report (single raw reading vs calibrated model output).
  * ANGLE_ACCURACY: Table 3 of the technical report (Test 2, accuracy vs measurement angle).

Run from anywhere:  python make_plots.py   (needs matplotlib, numpy, openpyxl)
PNGs are written to the parent folder (projects/matlab-control/).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
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


# ---------------------------------------------------------------- Test 1: calibration
def load_test1():
    ws = openpyxl.load_workbook(HERE / "experiment-1-data.xlsx", data_only=True).active
    header = [c.value for c in ws[2]][1:]
    distances = np.array([float(h.split()[0]) / 100 for h in header])  # "10 cm" -> 0.10 m
    readings = np.array([[c for c in row[1:]] for row in
                         ws.iter_rows(min_row=3, max_row=102, values_only=True)], dtype=float)
    # The report's calibration covers 10-50 cm, so the 5 cm column is left out.
    keep = distances >= 0.10 - 1e-9
    return distances[keep], readings[:, keep]


u, X = load_test1()
offset = (u - X).mean(axis=0)                     # o = (1/100) * sum(U - X)
unc = 0.5 * (X.max(axis=0) - X.min(axis=0))       # half the range of the readings
a, b = np.polyfit(u, offset, 1)
pred = a * u + b
r2 = 1 - np.sum((offset - pred) ** 2) / np.sum((offset - offset.mean()) ** 2)
print(f"fit: offset = {a:.5f} u + {b:.6f}, R^2 = {r2:.3f}")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.errorbar(u * 100, offset * 100, yerr=unc * 100, fmt="o", color=ACCENT, ecolor=ACCENT,
            capsize=4, ms=6, label="Mean offset of 100 readings (± half range)")
xs = np.linspace(0.08, 0.52, 50)
ax.plot(xs * 100, (a * xs + b) * 100, color=ACCENT_2, lw=2,
        label=f"Linear fit: offset = {a:.3f}u + {b * 100:.2f} cm  (R² = {r2:.2f})")
ax.set_xlabel("Exact distance, u (cm)")
ax.set_ylabel("Correction offset, u − x̄ (cm)")
ax.set_title("Test 1: calibration offset grows with distance")
ax.legend(frameon=False, loc="upper left", fontsize=9.5)
save(fig, "calibration-offset.png")

# ---------------------------------------------------------------- Test 1: model check (Table 2)
MODEL_CHECK = np.array([  # exact (m), raw reading (m), model output (m)
    [0.10, 0.0883, 0.0976], [0.15, 0.1412, 0.1537], [0.20, 0.1736, 0.1880],
    [0.25, 0.2283, 0.2460], [0.30, 0.2859, 0.3071], [0.35, 0.3259, 0.3495],
    [0.40, 0.3717, 0.3980], [0.45, 0.4241, 0.4535], [0.50, 0.4691, 0.5012],
])
ex, raw, model = MODEL_CHECK.T
err_raw = (raw - ex) * 1000
err_model = (model - ex) * 1000
acc_raw = np.mean(1 - np.abs(ex - raw) / ex) * 100
acc_model = np.mean(1 - np.abs(ex - model) / ex) * 100

fig, ax = plt.subplots(figsize=(7, 4.5))
w = 1.6
ax.bar(ex * 100 - w / 2, err_raw, width=w, color=GREY, label=f"Raw reading (mean accuracy {acc_raw:.1f}%)")
ax.bar(ex * 100 + w / 2, err_model, width=w, color=ACCENT,
       label=f"Calibrated model (mean accuracy {acc_model:.1f}%)")
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(ex * 100)
ax.set_xlabel("Exact distance (cm)")
ax.set_ylabel("Reading − exact distance (mm)")
ax.set_title("Calibration removes most of the sensor's under-reading")
ax.legend(frameon=False, loc="lower left", fontsize=9.5)
save(fig, "model-verification.png")

# ---------------------------------------------------------------- Test 2: angle (Table 3)
ANGLE_ACCURACY = [
    (-0.46, 0.005337), (-0.45, 0.005083), (-0.44, 0.004664), (-0.42, 0.004466),
    (-0.41, 0.004287), (-0.39, 0.004115), (-0.38, 0.003974), (-0.37, 0.004013),
    (-0.35, 0.003703), (-0.34, 0.003700), (-0.32, 0.003453), (-0.31, 0.003341),
    (-0.29, 0.983412), (-0.28, 0.997187), (-0.26, 0.977276), (-0.25, 0.987478),
    (-0.23, 0.974371), (-0.21, 0.961352), (-0.20, 0.989529), (-0.18, 0.975445),
    (-0.17, 0.961345), (-0.15, 0.989312), (-0.13, 0.974381), (-0.12, 0.972604),
    (-0.10, 0.969310), (-0.08, 0.961780), (-0.07, 0.980859), (-0.05, 0.964250),
    (-0.03, 0.946190), (-0.02, 0.946269), (0.00, 0.946491), (0.02, 0.945975),
    (0.03, 0.951449), (0.05, 0.971332), (0.07, 0.972091), (0.08, 0.987846),
    (0.10, 0.960487), (0.12, 0.959923), (0.13, 0.974203), (0.15, 0.972305),
    (0.17, 0.986475), (0.18, 0.958798), (0.20, 0.974037), (0.21, 0.986021),
    (0.23, 0.989462), (0.25, 0.988289), (0.26, 0.831336), (0.28, 0.005130),
    (0.29, 0.003404), (0.31, 0.003504), (0.32, 0.003476), (0.34, 0.003572),
    (0.35, 0.003720), (0.37, 0.003861), (0.38, 0.003995), (0.39, 0.004154),
    (0.41, 0.004318), (0.42, 0.004493), (0.44, 0.004630), (0.45, 0.004858),
    (0.46, 0.005050),
]
theta, acc = np.array(ANGLE_ACCURACY).T
deg = np.degrees(theta)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.axvspan(np.degrees(-0.29), np.degrees(0.26), color=ACCENT, alpha=0.08, lw=0)
ax.plot(deg, acc, "-o", color=ACCENT, ms=4, lw=1.5)
for x in (-15, 15):
    ax.axvline(x, color=ACCENT_2, ls="--", lw=1.2)
ax.text(15.5, 0.5, "Datasheet\n±15°", color=ACCENT_2, fontsize=9.5, va="center")
ax.text(0, 0.88, "Measured cone: −16.6° to +14.9°", ha="center", color=ACCENT, fontsize=10)
ax.set_xlabel("Measurement angle, θ (°)")
ax.set_ylabel("Accuracy, A (dimensionless, 0–1)")
ax.set_ylim(-0.03, 1.05)
ax.set_title("Test 2: accuracy collapses outside the beam cone")
save(fig, "angle-accuracy.png")
