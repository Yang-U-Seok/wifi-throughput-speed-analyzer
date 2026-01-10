import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PCAP_PATH = r"C:\Users\nanev\Documents\wifi_test_10s.pcapng"
RESULT_DIR = Path("results")
RESULT_DIR.mkdir(exist_ok=True)

def load_pcap_as_dataframe(pcap_path):
    cmd = [
        "tshark",
        "-r", pcap_path,
        "-T", "fields",
        "-e", "frame.time_epoch",
        "-e", "frame.len",
        "-E", "separator=,",
        "-E", "quote=d",
        "-E", "header=y"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return pd.read_csv(pd.compat.StringIO(result.stdout))

def compute_throughput(df, window=1.0):
    df = df.dropna()
    df["frame.time_epoch"] = df["frame.time_epoch"].astype(float)
    df["frame.len"] = df["frame.len"].astype(int)

    t0 = df["frame.time_epoch"].min()
    df["time_bin"] = ((df["frame.time_epoch"] - t0) // window).astype(int)

    grouped = df.groupby("time_bin")["frame.len"].sum()
    throughput = grouped * 8 / (window * 1e6)

    return throughput

def plot_throughput(throughput):
    plt.figure()
    plt.plot(throughput.index, throughput.values, marker="o")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Mbps)")
    plt.title("Experiment 1: Throughput over Time (1s window)")
    plt.grid(True)

    output_path = RESULT_DIR / "exp1_throughput_over_time.png"
    plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    df = load_pcap_as_dataframe(PCAP_PATH)
    throughput = compute_throughput(df)
    plot_throughput(throughput)
