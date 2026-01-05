import pyshark
TSHARK_PATH = r"C:\Program Files\Wireshark\tshark.exe"
PCAP_PATH = "../data/wifi_test_10s.pcapng"

def calculate_throughput(pcap_path):
    cap = pyshark.FileCapture(
    pcap_path,
    keep_packets=False,
    tshark_path=TSHARK_PATH
)
    total_bytes = 0
    start_time = None
    end_time = None

    for pkt in cap:
        try:
            frame_len = int(pkt.length)
            frame_time = float(pkt.sniff_timestamp)

            total_bytes += frame_len

            if start_time is None:
                start_time = frame_time
            end_time = frame_time

        except Exception:
            continue

    cap.close()

    delta_t = end_time - start_time
    throughput_mbps = (total_bytes * 8) / (delta_t * 1e6)

    return total_bytes, delta_t, throughput_mbps


if __name__ == "__main__":
    total_bytes, delta_t, t_obs = calculate_throughput(PCAP_PATH)

    print(f"Total bytes transmitted: {total_bytes} bytes")
    print(f"Measurement duration: {delta_t:.3f} seconds")
    print(f"Observed throughput: {t_obs:.3f} Mbps")
