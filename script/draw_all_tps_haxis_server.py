import os
import sys
import re
import matplotlib.pyplot as plt
import numpy as np

def extract_tps(file_path):
    """summary.txtからTPS_avgの値を抽出する"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            match = re.search(r'TPS_avg=([\d\.]+)', content)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def natural_keys(text):
    """自然順ソート用のキー関数"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def get_dir_data(base_dir):
    """特定のディレクトリ内の全サブディレクトリからTPSデータを取得する"""
    tps_data = {}
    if not os.path.isdir(base_dir):
        return None
    
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    for subdir in subdirs:
        file_path = os.path.join(base_dir, subdir, "summary.txt")
        if os.path.exists(file_path):
            val = extract_tps(file_path)
            if val is not None:
                tps_data[subdir] = val
    return tps_data

def main():
    if len(sys.argv) < 3:
        print("Usage: python draw_all_tps_haxis_server.py <Graph_Title> <Dir1> <Dir2> ...")
        sys.exit(1)

    graph_title = sys.argv[1]
    target_dirs = sys.argv[2:]

    all_results = {}
    all_configs = set()
    
    # 横軸用のラベルリスト
    dir_labels = []
    
    for d in target_dirs:
        data = get_dir_data(d)
        if data:
            all_results[d] = data
            all_configs.update(data.keys())
            
            # ディレクトリ名を取得し、最初の '_' で分割して先頭を採用
            folder_name = os.path.basename(d.rstrip('/'))
            short_name = folder_name.split('_')[0]
            dir_labels.append(short_name)

    # 設定項目のソート
    sorted_configs = sorted([c for c in all_configs if c != 'default'], key=natural_keys)
    sorted_configs = ['default'] + sorted_configs

    # グラフ描画
    x = np.arange(len(dir_labels))
    width = 0.8 / len(sorted_configs)

    plt.figure(figsize=(12, 7))

    for i, config in enumerate(sorted_configs):
        values = []
        for d in target_dirs:
            data = all_results.get(d, {})
            baseline = data.get('default', 1.0)
            val = data.get(config, 0) / baseline if baseline != 0 else 0
            values.append(val)
        
        offset = i * width - (len(sorted_configs) - 1) * width / 2
        bars = plt.bar(x + offset, values, width, label=config)

        # バーの上に数値を表示
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                plt.text(bar.get_x() + bar.get_width()/2, h, f'{h:.2f}', 
                         va='bottom', ha='center', fontsize=8)

    # グラフ装飾
    plt.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    plt.title(graph_title)
    plt.ylabel('Normalized TPS (default = 1.0)')
    plt.xlabel('Experiments')
    plt.xticks(x, dir_labels) # 短縮したラベルを適用
    plt.legend(title="Configurations", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    
    output_filename = "tps_comparison_by_server.pdf"
    plt.savefig(output_filename)
    print(f"Graph saved as {output_filename} with shortened labels.")
    plt.show()

if __name__ == "__main__":
    main()
