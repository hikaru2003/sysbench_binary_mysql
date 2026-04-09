import os
import sys
import re
import matplotlib.pyplot as plt
import numpy as np

# 対象とするメトリクスのリスト
TARGET_METRICS = [
    "TPS_avg",
    "QPS_avg",
    "Latency_avg_ms",
    "Latency_p95_ms_avg",
    "Ignored_errors_per_sec_avg"
]

def extract_metric_value(file_path, metric_name):
    """summary.txtから指定されたメトリクスの値を抽出する"""
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as f:
            content = f.read()
            pattern = rf'{re.escape(metric_name)}=([\d\.]+)'
            match = re.search(pattern, content)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def natural_keys(text):
    """自然順ソート用のキー関数"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def get_dir_data(base_dir, metric_name):
    """ディレクトリ内の全サブディレクトリから特定のメトリクスデータを取得する"""
    data_map = {}
    if not os.path.isdir(base_dir):
        return None
    
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    for subdir in subdirs:
        file_path = os.path.join(base_dir, subdir, "summary.txt")
        val = extract_metric_value(file_path, metric_name)
        if val is not None:
            data_map[subdir] = val
    return data_map

def main():
    # 引数構成: <タイトル> <Dir1> <Dir2> ...
    if len(sys.argv) < 3:
        print("Usage: python draw_all_metrics.py <Graph_Title_Prefix> <Dir1> <Dir2> ...")
        sys.exit(1)

    title_prefix = sys.argv[1]
    target_dirs = sys.argv[2:]

    # 各メトリクスごとにループを回してグラフを作成
    for metric in TARGET_METRICS:
        print(f"Processing metric: {metric}...")
        
        all_results = {}
        all_configs = set()
        dir_labels = []
        
        for d in target_dirs:
            data = get_dir_data(d, metric)
            if data:
                all_results[d] = data
                all_configs.update(data.keys())
                
                folder_name = os.path.basename(d.rstrip('/'))
                short_name = folder_name.split('_')[0]
                
                # default値を取得してラベルに表示
                baseline_val = data.get('default')
                if baseline_val is not None:
                    label = f"{short_name}\n(def: {baseline_val:.2f})"
                else:
                    label = short_name
                dir_labels.append(label)

        if not all_results:
            print(f"No data found for {metric}, skipping...")
            continue

        # 設定のソート
        sorted_configs = sorted([c for c in all_configs if c != 'default'], key=natural_keys)
        if 'default' in all_configs:
            sorted_configs = ['default'] + sorted_configs

        # 描画処理
        x = np.arange(len(dir_labels))
        num_configs = len(sorted_configs)
        width = 0.8 / num_configs

        plt.figure(figsize=(12, 7))

        for i, config in enumerate(sorted_configs):
            norm_values = []
            for d in target_dirs:
                data = all_results.get(d, {})
                baseline = data.get('default')
                current_val = data.get(config)
                
                if baseline is not None and baseline != 0 and current_val is not None:
                    val = current_val / baseline
                else:
                    val = 0
                norm_values.append(val)
            
            offset = i * width - (num_configs - 1) * width / 2
            bars = plt.bar(x + offset, norm_values, width, label=config)

            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    plt.text(bar.get_x() + bar.get_width()/2, h, f'{h:.2f}', 
                             va='bottom', ha='center', fontsize=8)

        # グラフ装飾
        plt.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        plt.title(f"{title_prefix} - {metric}")
        plt.ylabel(f'Normalized {metric} (default = 1.0)')
        plt.xlabel('Experiments (baseline absolute values in brackets)')
        plt.xticks(x, dir_labels)
        plt.legend(title="Configurations", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', linestyle=':', alpha=0.7)
        
        plt.tight_layout()
        
        # ファイル名の保存
        output_filename = f"comparison_{metric.lower()}.pdf"
        plt.savefig(output_filename)
        plt.close() # 次のループのためにリセット
        print(f"  Saved as {output_filename}")

if __name__ == "__main__":
    main()
