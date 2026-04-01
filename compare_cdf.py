import argparse
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_sysbench_output(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    data = []
    in_histogram = False
    for i, line in enumerate(lines):
        if "value  ------------- distribution ------------- count" in line:
            in_histogram = True
            continue
        if "SQL statistics:" in line:
            in_histogram = False
        if in_histogram and "|" in line:
            parts = line.split("|")
            try:
                latency = float(parts[0].strip())
                count_str = parts[1].strip().split()
                count = int(count_str[-1]) if count_str else int(lines[i + 1].strip())
                data.append([latency, count])
            except Exception:
                continue
    return pd.DataFrame(data, columns=["latency_ms", "count"]) if data else None


def cdf_from_histogram(df):
    df = df.sort_values("latency_ms")
    df = df.copy()
    df["cumsum"] = df["count"].cumsum()
    df["cdf"] = df["cumsum"] / df["count"].sum()
    return df


def mean_cdf_over_runs(run_dfs):
    """run*.txt ごとの CDF を、共通のレイテンシ軸で平均する。"""
    if not run_dfs:
        return None, None
    all_latencies = np.sort(
        np.unique(np.concatenate([df["latency_ms"].values for df in run_dfs]))
    )
    mean_cdf = np.zeros_like(all_latencies, dtype=float)
    for df in run_dfs:
        mean_cdf += np.interp(all_latencies, df["latency_ms"], df["cdf"])
    mean_cdf /= len(run_dfs)
    return all_latencies, mean_cdf


def load_runs_in_directory(dir_path):
    pattern = os.path.join(os.path.expanduser(dir_path), "run*.txt")
    files = sorted(glob.glob(pattern))
    dfs = []
    for f in files:
        raw = parse_sysbench_output(f)
        if raw is not None:
            dfs.append(cdf_from_histogram(raw))
    return dfs, files


def main():
    parser = argparse.ArgumentParser(
        description="各ディレクトリの run*.txt から平均 CDF を求め、環境間で比較プロットする。"
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=["."],
        help="比較する実験ディレクトリ（各ディレクトリに run*.txt）。省略時はカレントディレクトリのみ。",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="latency_cdf_compare.png",
        help="出力画像ファイル名（既定: latency_cdf_compare.png）",
    )
    args = parser.parse_args()

    plt.figure(figsize=(10, 6))
    cmap = plt.get_cmap("tab10")
    plotted = False
    xmin_global = None

    for idx, d in enumerate(args.directories):
        run_dfs, files = load_runs_in_directory(d)
        if not run_dfs:
            print(f"警告: {d!r} に有効な run*.txt が見つかりません。スキップします。")
            continue

        latencies, mean_cdf = mean_cdf_over_runs(run_dfs)
        label = os.path.basename(os.path.abspath(d)) or d
        if len(files) > 1:
            label = f"{label} (mean of {len(run_dfs)} runs)"
        else:
            label = f"{label} ({len(run_dfs)} run)"

        color = cmap(idx % 10)
        plt.plot(latencies, mean_cdf, color=color, linewidth=2, label=label)
        plotted = True
        x0 = latencies[0] if len(latencies) else None
        if x0 is not None:
            xmin_global = x0 if xmin_global is None else min(xmin_global, x0)

    if not plotted:
        print("プロットできるデータがありません。")
        return

    plt.xscale("log")
    plt.title("Latency CDF — mean per directory (experimental environment)")
    plt.xlabel("Latency (ms) — log scale")
    plt.ylabel("Cumulative probability")
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.axhline(0.95, color="gray", linestyle="--", alpha=0.7)
    if xmin_global is not None:
        plt.text(xmin_global, 0.96, "95th percentile", color="gray", fontsize=9)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"CDF 比較図を保存しました: {args.output}")


if __name__ == "__main__":
    main()
