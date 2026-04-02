import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
import sys

def parse_sysbench_output(file_path):
    # sysbenchのヒストグラム出力をパース
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
                # レイテンシ値の取得
                latency = float(parts[0].strip())
                # カウント数の取得（行末の数値）
                count_parts = parts[1].strip().split()
                if count_parts:
                    count = int(count_parts[-1])
                    data.append([latency, count])
            except:
                continue
    return pd.DataFrame(data, columns=['latency_ms', 'count']) if data else None

def process_and_plot(target_dirs, x_label_text):
    plt.figure(figsize=(10, 6))
    
    # カラーマップの準備
    cmap = plt.get_cmap('tab10')
    
    has_data = False
    for d_idx, d_path in enumerate(target_dirs):
        # 指定ディレクトリ内の run*.txt を検索
        files = sorted(glob.glob(os.path.join(d_path, "run*.txt")))
        if not files:
            print(f"警告: {d_path} 内に run*.txt が見つかりませんでした。")
            continue
        
        has_data = True
        dir_name = os.path.basename(d_path.rstrip(os.sep))
        all_dfs = []
        color = cmap(d_idx % 10)

        for f in files:
            df = parse_sysbench_output(f)
            if df is not None:
                df = df.sort_values('latency_ms')
                df['cumsum'] = df['count'].cumsum()
                df['cdf'] = df['cumsum'] / df['count'].sum()
                
                # 個別の試行を薄い線で描画
                plt.plot(df['latency_ms'], df['cdf'], color=color, alpha=0.1, linewidth=1)
                all_dfs.append(df)

        if all_dfs:
            # ディレクトリごとの平均CDFを計算
            all_latencies = np.sort(np.unique(np.concatenate([df['latency_ms'].values for df in all_dfs])))
            mean_cdf = np.zeros_like(all_latencies)

            for df in all_dfs:
                mean_cdf += np.interp(all_latencies, df['latency_ms'], df['cdf'])
            mean_cdf /= len(all_dfs)

            # 平均線を太くプロット
            plt.plot(all_latencies, mean_cdf, color=color, linewidth=2, label=f'{dir_name} (Avg)')

    if not has_data:
        print("表示可能なデータがありませんでした。")
        return

    # グラフの設定
    plt.xscale('log')
    plt.title("Latency Cumulative Distribution Function (CDF)")
    plt.xlabel(x_label_text)
    plt.ylabel("Cumulative Probability (0.0 - 1.0)")
    
    # 修正箇所: plt.grid の引数を正しく修正
    plt.grid(True, which="both", ls="-", alpha=0.4)
    
    # P95ライン
    plt.axhline(0.95, color='black', linestyle='--', alpha=0.5, label='95th Percentile')
    
    plt.legend()
    plt.tight_layout()

    output_file = 'latency_cdf.png'
    plt.savefig(output_file)
    print(f"CDF Graph saved as '{output_file}'")
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python draw_cdf.py \"X軸のラベル名\" ディレクトリ1 [ディレクトリ2 ...]")
        sys.exit(1)

    x_label_input = sys.argv[1]
    target_directories = sys.argv[2:] if len(sys.argv) > 2 else ["."]
    
    process_and_plot(target_directories, x_label_input)
