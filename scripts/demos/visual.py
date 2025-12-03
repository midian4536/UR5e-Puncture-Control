import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

def find_latest_csv(root="outputs"):
    root = Path(root)
    run_dirs = [d for d in root.glob("run_*") if d.is_dir()]
    run_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    latest_run = run_dirs[0]
    csv_path = latest_run / "ur5e_data.csv"
    print(f"Using latest CSV: {csv_path}")
    return csv_path

def plot_basic(csv_path):
    df = pd.read_csv(csv_path)
    t = df["timestamp"]
    currents = np.vstack([df[f"curr_{i}"] for i in range(6)])
    volts = np.vstack([df[f"volt_{i}"] for i in range(6)])
    torqs = np.vstack([df[f"torq_{i}"] for i in range(6)])

    sns.set(style="whitegrid")
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    colors = sns.color_palette("tab10", 6)

    for i in range(6):
        axes[0].plot(t, currents[i], label=f"Current {i}", color=colors[i])
    axes[0].set_title("Joint Currents (A)")
    axes[0].legend(loc="upper left", bbox_to_anchor=(1.02, 1))

    for i in range(6):
        axes[1].plot(t, volts[i], label=f"Voltage {i}", color=colors[i])
    axes[1].set_title("Joint Voltages (V)")
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.02, 1))

    for i in range(6):
        axes[2].plot(t, torqs[i], label=f"Torque {i}", color=colors[i])
    axes[2].set_title("Joint Torques (Nm)")
    axes[2].legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    axes[2].set_xlabel("Timestamp")

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

def plot_3d_trajectory(csv_path):
    df = pd.read_csv(csv_path)
    x = df["tcp_pose_0"]
    y = df["tcp_pose_1"]
    z = df["tcp_pose_2"]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(x, y, z, linewidth=2)

    ax.set_title("3D TCP Trajectory")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    csv_path = find_latest_csv()
    plot_basic(csv_path)
    plot_3d_trajectory(csv_path)
