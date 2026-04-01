import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np

def parse_sysbench_output(file_path):
    # 前回の修正版パースロジックを使用
    with open(file_path, 'r') as f:
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
            parts = line.split('|')
            try:
                latency = float(parts[0].strip())
                count_str = parts[1].strip().split()
                count = int(count_str[-1]) if count_str else int(lines[i+1].strip())
                data.append([latency, count])
            except: continue
    return pd.DataFrame(data, columns=['latency_ms', 'count']) if data else None

# ファイル読み込み
files = sorted(glob.glob("run*.txt"))
plt.figure(figsize=(10, 6))

all_dfs = []
for i, f in enumerate(files):
    df = parse_sysbench_output(f)
    if df is not None:
        # 累積比率 (CDF) の計算
        df = df.sort_values('latency_ms')
        df['cumsum'] = df['count'].cumsum()
        df['cdf'] = df['cumsum'] / df['count'].sum()
        
        # 各試行を薄い線でプロット
        plt.plot(df['latency_ms'], df['cdf'], alpha=0.3, label=f'Run {i+1}' if i==0 else "")
        all_dfs.append(df)

# --- 10回の平均CDFを計算 ---
# 全データのレイテンシ地点を統合して補間（より正確な平均をとるため）
all_latencies = np.sort(np.unique(np.concatenate([df['latency_ms'].values for df in all_dfs])))
mean_cdf = np.zeros_like(all_latencies)

for df in all_dfs:
    mean_cdf += np.interp(all_latencies, df['latency_ms'], df['cdf'])
mean_cdf /= len(all_dfs)

# 平均線を太くプロット
plt.plot(all_latencies, mean_cdf, color='red', linewidth=2, label='10-Run Average')

# グラフの設定
plt.xscale('log')
plt.title("Latency Cumulative Distribution Function (CDF)")
plt.xlabel("Latency (ms) - Log Scale")
plt.ylabel("Cumulative Probability (0.0 - 1.0)")
plt.grid(True, which="both", ls="-", alpha=0.5)
plt.axhline(0.95, color='gray', linestyle='--', alpha=0.7) # P95ライン
plt.text(all_latencies[0], 0.96, '95th Percentile', color='gray')
plt.legend()

plt.savefig('latency_cdf.png')
print("CDF Graph saved as 'latency_cdf.png'")
