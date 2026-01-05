def calculate_observed_throughput(pcap_path):
    """
    Calculate observed throughput from a PCAP file.

    T_obs = (sum(frame.len) * 8) / (Δt * 1e6)
    """
    pass


if __name__ == "__main__":
    pcap_path = "../data/sample.pcap"
    calculate_observed_throughput(pcap_path)
