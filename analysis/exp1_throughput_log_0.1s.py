import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from pathlib import Path
import numpy as np

TSHARK_PATH = r"C:\Program Files\Wireshark\tshark.exe"
PCAP_PATH   = r"C:\Users\nanev\Documents\wifi_test_10s.pcapng"
BIN_SIZE    = 0.1

def load_pcap_df(pcap_path: str, tshark_path: str = TSHARK_PATH) -> pd.DataFrame:
    pcap_path = str(Path(pcap_path))

    cmd = [
        tshark_path,
        "-r", pcap_path,
        "-T", "fields",
        "-E", "separator=,",
        "-E", "header=y",
        "-e", "frame.time_epoch",
        "-e", "frame.len",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("tshark failed:\n" + result.stderr)

    df = pd.read_csv(StringIO(result.stdout)).dropna()
    df["frame.time_epoch"] = df["frame.time_epoch"].astype(float)
    df["frame.len"] = df["frame.len"].astype(int)
    return df

def throughput_timeseries(df: pd.DataFrame, bin_size: float = 0.1):
    t0 = df["frame.time_epoch"].min()
    t1 = df["frame.time_epoch"].max()
    duration = t1 - t0

    d = df.copy()
    d["t_rel"] = d["frame.time_epoch"] - t0
    d["bin"] = (d["t_rel"] // bin_size).astype(int)

    bytes_per_bin = d.groupby("bin")["frame.len"].sum()
    max_bin = int(duration // bin_size)
    bytes_per_bin = bytes_per_bin.reindex(range(max_bin + 1), fill_value=0)

    mbps = (bytes_per_bin.values * 8) / (bin_size * 1e6)
    bin_starts = bytes_per_bin.index.values * bin_size

    return bin_starts, mbps, duration

def overall_throughput(df: pd.DataFrame):
    t0 = df["frame.time_epoch"].min()
    t1 = df["frame.time_epoch"].max()
    dt = t1 - t0
    total_bytes = df["frame.len"].sum()
    t_obs = (total_bytes * 8) / (dt * 1e6)
    return total_bytes, dt, t_obs

def plot_throughput_B_log_safe(bin_starts, mbps, bin_size: float, eps: float = 1e-6):
    """
    eps: log scale에서 0을 피하기 위한 최소값 (Mbps)
    """
    y = np.array(mbps, dtype=float)
    y[y <= 0] = eps  # ✅ B: 0을 eps로 치환 (log 스케일 안정)

    plt.figure(figsize=(10, 5))
    plt.plot(bin_starts, y, linewidth=1)  # marker 제거
    plt.title(f"Experiment 1: Throughput over Time ({bin_size}s bins)")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Mbps) (log scale, eps applied)")
    plt.yscale("log")
    plt.grid(True, which="both")
    plt.tight_layout()

    plt.savefig("exp1_throughput_B_log_safe.png", dpi=200, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    df = load_pcap_df(PCAP_PATH, TSHARK_PATH)

    total_bytes, dt, t_obs = overall_throughput(df)
    bin_starts, mbps, duration = throughput_timeseries(df, BIN_SIZE)

    print(f"PCAP: {PCAP_PATH}")
    print(f"Packets(lines): {len(df)}")
    print(f"Total bytes (Σ frame.len): {total_bytes} bytes")
    print(f"Measurement duration (Δt): {dt:.6f} seconds")
    print(f"Observed throughput (T_obs): {t_obs:.3f} Mbps")
    print(f"bin_size={BIN_SIZE}s  bins={len(mbps)}")
    print(f"Peak bin throughput: {np.max(mbps):.2f} Mbps")
    print(f"95th percentile bin throughput: {np.percentile(mbps, 95):.2f} Mbps")

    plot_throughput_B_log_safe(bin_starts, mbps, BIN_SIZE)
