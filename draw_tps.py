import os
import glob
import sys
import matplotlib.pyplot as plt
import pandas as pd
import re

def collect_tps_data(target_dirs):
    data = []
    files = []
    
    # 指定された各ディレクトリに対して summary.txt を検索
    for d in target_dirs:
        search_path = os.path.join(d, "**/summary.txt")
        found_files = glob.glob(search_path, recursive=True)
        files.extend(found_files)
    
    if not files:
        print("指定されたディレクトリ内に summary.txt が見つかりませんでした。")
        return None

    for file_path in files:
        # ディレクトリ名を取得 (例: baseline, multiplier_5_delay_1 など)
        dir_name = os.path.dirname(file_path).split(os.sep)[-1]
        
        tps_value = None
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    # "TPS_avg=635.2630" のような形式を正規表現で抽出
                    match = re.search(r"TPS_avg=([\d.]+)", line)
                    if match:
                        tps_value = float(match.group(1))
                        break # 見つかったらそのファイルの読み込みを終了
            
            if tps_value is not None:
                data.append({'directory': dir_name, 'tps_avg': tps_value})
            else:
                print(f"警告: {file_path} 内に TPS_avg が見つかりませんでした。")
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    df = pd.DataFrame(data)
    # ディレクトリ名でソート
    df = df.sort_values('directory').reset_index(drop=True)
    return df

def plot_tps_data(df, x_label_text):
    if df is None or df.empty:
        print("表示するデータがありません。")
        return

    plt.figure(figsize=(12, 6))
    # TPSなので色は少し変えて「黄緑(lightgreen)」にしています
    bars = plt.bar(df['directory'], df['tps_avg'], color='lightgreen', edgecolor='darkgreen')
    
    # Y軸の範囲調整（ズーム）
    min_val = df['tps_avg'].min()
    max_val = df['tps_avg'].max()
    margin = (max_val - min_val) * 0.3
    
    if margin == 0: margin = min_val * 0.1
    plt.ylim(min_val - margin, max_val + margin)

    # バーの上に数値を表示
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', 
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.xlabel(x_label_text)
    plt.ylabel('Average TPS (Transactions Per Second)')
    plt.title('Throughput Performance (TPS_avg)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    output_file = 'tps_performance.png'
    plt.savefig(output_file)
    print(f"グラフを '{output_file}' として保存しました。")
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python draw_tps_graph.py \"X軸のラベル名\" ディレクトリ1 [ディレクトリ2 ...]")
        sys.exit(1)

    x_label_input = sys.argv[1]
    target_directories = sys.argv[2:] if len(sys.argv) > 2 else ["."]
    
    print(f"X軸ラベル: {x_label_input}")
    print(f"探索対象ディレクトリ: {target_directories}")
    
    df_results = collect_tps_data(target_directories)
    
    if df_results is not None:
        print("\n集計結果:")
        print(df_results)
        plot_tps_data(df_results, x_label_input)
