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
        print("Usage: python plot_tps_multi.py <Graph_Title> <Dir1> <Dir2> ...")
        sys.exit(1)

    graph_title = sys.argv[1]
    target_dirs = sys.argv[2:]  # 複数のディレクトリを受け取る

    plt.figure(figsize=(12, 7))
    
    # 共通の設定ラベルを取得（最初のディレクトリを基準にする）
    first_dir_data = get_dir_data(target_dirs[0])
    if not first_dir_data or 'default' not in first_dir_data:
        print(f"Error: 'default' not found in {target_dirs[0]}")
        sys.exit(1)
    
    other_keys = sorted([k for k in first_dir_data.keys() if k != 'default'], key=natural_keys)
    config_labels = ['default'] + other_keys
    
    # グラフ描画の準備
    x = np.arange(len(config_labels))  # ラベルの位置
    width = 0.8 / len(target_dirs)      # 棒の幅をディレクトリ数で割る

    for i, base_dir in enumerate(target_dirs):
        data = get_dir_data(base_dir)
        if not data or 'default' not in data:
            print(f"Warning: Skipping {base_dir} (missing data or default)")
            continue
        
        baseline = data['default']
        # 基準に沿って値を正規化（データが欠けている場合は0を入れる）
        values = [data.get(k, 0) / baseline for k in config_labels]
        
        # 棒をずらして配置
        offset = i * width - (len(target_dirs) - 1) * width / 2
        bars = plt.bar(x + offset, values, width, label=os.path.basename(base_dir))
        
        # 数値ラベル
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', 
                         va='bottom', ha='center', fontsize=8, rotation=90)

    # グラフの装飾
    plt.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    plt.title(graph_title)
    plt.ylabel('Normalized TPS (default = 1.0)')
    plt.xlabel('Configuration')
    plt.xticks(x, config_labels, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.tight_layout()
    
    output_filename = "tps_combined_graph.pdf"
    plt.savefig(output_filename)
    print(f"Graph saved as {output_filename}")
    plt.show()

if __name__ == "__main__":
    main()
