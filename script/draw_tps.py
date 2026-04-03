import os
import sys
import re
import matplotlib.pyplot as plt

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
    """
    文字列を数値と非数値に分割し、数値部分はintとして返す
    (自然順ソート用のキー関数)
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def main():
    if len(sys.argv) < 3:
        print("Usage: python plot_tps.py <Graph_Title> <Directory_Path>")
        sys.exit(1)

    graph_title = sys.argv[1]
    base_dir = sys.argv[2]

    tps_data = {}

    if not os.path.isdir(base_dir):
        print(f"Error: {base_dir} is not a directory.")
        sys.exit(1)

    # サブディレクトリを走査
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    for subdir in subdirs:
        file_path = os.path.join(base_dir, subdir, "summary.txt")
        if os.path.exists(file_path):
            val = extract_tps(file_path)
            if val is not None:
                tps_data[subdir] = val

    if 'default' not in tps_data:
        print("Error: 'default' directory or TPS_avg in default/summary.txt not found.")
        sys.exit(1)

    # --- 並び替えロジック ---
    # defaultを除いたディレクトリ名をソートし、先頭にdefaultを追加する
    other_dirs = sorted([d for d in tps_data.keys() if d != 'default'])
    other_dirs.sort(key=natural_keys)
    sorted_keys = ['default'] + other_dirs

    # defaultの値を基準に正規化
    baseline = tps_data['default']
    labels = sorted_keys
    values = [tps_data[k] / baseline for k in labels]

    # グラフ描画
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color='skyblue', edgecolor='navy')
    
    # 基準線 (1.0)
    plt.axhline(y=1.0, color='red', linestyle='--', linewidth=1)
    
    plt.title(graph_title)
    plt.ylabel('Normalized TPS (default = 1.0)')
    plt.xlabel('Configuration')
    plt.xticks(rotation=45)
    #plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.7)

    # バーの上に数値を表示
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', va='bottom', ha='center')

    plt.tight_layout()
    
    # PDFとして保存
    output_filename = "tps_graph.pdf"
    plt.savefig(output_filename)
    print(f"Graph saved as {output_filename}")
    
    # 実行環境に画面がある場合は表示
    plt.show()

if __name__ == "__main__":
    main()
