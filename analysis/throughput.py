# -*- coding: utf-8 -*-
"""
Spyder-friendly Wi-Fi throughput calculator (no pyshark event loop issues)

Observed throughput:
T_obs = (sum(frame.len) * 8) / (Δt * 1e6)  [Mbps]
"""

import os
import subprocess

# ✅ tshark 경로 (Wireshark 설치 경로에 맞춰 수정)
TSHARK_PATH = r"C:\Program Files\Wireshark\tshark.exe"

# ✅ PCAP 파일 절대경로 (네 PC에 맞게 수정)
PCAP_PATH = r"C:\Users\nanev\Documents\wifi_test_10s.pcapng"


def calculate_throughput_with_tshark(pcap_path: str, tshark_path: str = TSHARK_PATH):
    """
    tshark로 frame.len + frame.time_epoch(=frame.time_epoch) 추출해서
    T_obs 계산 (Spyder에서도 안정적으로 동작)

    Returns:
        total_bytes (int)
        delta_t (float)
        throughput_mbps (float)
        parsed_lines (int)
        skipped_lines (int)
    """
    if not os.path.exists(pcap_path):
        raise FileNotFoundError(f"PCAP not found: {pcap_path}")

    if not os.path.exists(tshark_path):
        raise FileNotFoundError(f"tshark not found: {tshark_path}")

    # tshark 출력: "<frame.time_epoch>\t<frame.len>\n"
    cmd = [
        tshark_path,
        "-r", pcap_path,
        "-T", "fields",
        "-E", "separator=\t",
        "-e", "frame.time_epoch",
        "-e", "frame.len",
    ]

    # 실행
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "tshark failed.\n"
            f"STDERR:\n{proc.stderr}\n"
        )

    total_bytes = 0
    start_time = None
    end_time = None
    parsed = 0
    skipped = 0

    for line in proc.stdout.splitlines():
        # 빈 줄/이상 줄 스킵
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            skipped += 1
            continue

        t_str, len_str = parts[0].strip(), parts[1].strip()
        if not t_str or not len_str:
            skipped += 1
            continue

        try:
            ts = float(t_str)
            frame_len = int(len_str)
        except Exception:
            skipped += 1
            continue

        total_bytes += frame_len
        parsed += 1

        if start_time is None:
            start_time = ts
        end_time = ts

    if start_time is None or end_time is None:
        raise RuntimeError("No packets parsed. Check the PCAP file.")

    delta_t = end_time - start_time
    if delta_t <= 0:
        raise RuntimeError(f"Invalid delta_t={delta_t}. Check timestamps in the PCAP.")

    throughput_mbps = (total_bytes * 8) / (delta_t * 1e6)
    return total_bytes, delta_t, throughput_mbps, parsed, skipped


if __name__ == "__main__":
    total_bytes, delta_t, t_obs, parsed, skipped = calculate_throughput_with_tshark(PCAP_PATH)

    print(f"PCAP: {PCAP_PATH}")
    print(f"Parsed lines: {parsed} | Skipped lines: {skipped}")
    print(f"Total bytes transmitted (Σ frame.len): {total_bytes} bytes")
    print(f"Measurement duration (Δt): {delta_t:.3f} seconds")
    print(f"Observed throughput (T_obs): {t_obs:.3f} Mbps")
