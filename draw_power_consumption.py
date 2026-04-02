mport os
import glob
import sys
import matplotlib.pyplot as plt
import pandas as pd

def collect_data(target_dirs):
    data = []
    files = []
    
    # 指定された各ディレクトリに対して検索を実行
    for d in target_dirs:
        search_path = os.path.join(d, "**/power_run1_watts_mean.csv")
        found_files = glob.glob(search_path, recursive=True)
        files.extend(found_files)
    
    if not files:
        print("指定されたディレクトリ内に対象ファイルが見つかりませんでした。")
        return None

    for file_path in files:
        # ディレクトリ名を取得
        dir_name = os.path.dirname(file_path).split(os.sep)[-1]
        total_watts = 0.0
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            total_watts += float(parts[1])
                        except ValueError:
                            continue
            data.append({'directory': dir_name, 'total_watts': total_watts})
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    df = pd.DataFrame(data)
    # グラフの見た目を整えるためディレクトリ名でソート
    df = df.sort_values('directory').reset_index(drop=True)
    return df

def plot_data(df, x_label_text):
    if df is None or df.empty:
        return

    plt.figure(figsize=(12, 6))
    bars = plt.bar(df['directory'], df['total_watts'], color='skyblue', edgecolor='navy')
    
    # Y軸の範囲を調整（ズーム）
    min_val = df['total_watts'].min()
    max_val = df['total_watts'].max()
    margin = (max_val - min_val) * 0.3  # 少し余裕を持たせる
    
    if margin == 0: margin = min_val * 0.1
    plt.ylim(min_val - margin, max_val + margin)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', 
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 63行目付近：引数で受け取った文字列をxlabelにセット
    plt.xlabel(x_label_text)
    plt.ylabel('Total Watts (Socket0 + Socket1)')
    plt.title('Power Consumption (Specified Directories)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig('power_consumption.png')
    print("グラフを 'power_consumption.png' として保存しました。")
    plt.show()

if __name__ == "__main__":
    # 引数チェック
    if len(sys.argv) < 2:
        print("使用法: python draw_power_consumption.py \"X軸のラベル名\" ディレクトリ1 [ディレクトリ2 ...]")
        sys.exit(1)

    # 第1引数をxlabelのテキストとして取得
    x_label_input = sys.argv[1]
    # 第2引数以降を探索ディレクトリとして取得
    target_directories = sys.argv[2:] if len(sys.argv) > 2 else ["."]
    
    print(f"X軸ラベル: {x_label_input}")
    print(f"探索対象ディレクトリ: {target_directories}")
    
    df_results = collect_data(target_directories)
    
    if df_results is not None:
        print("\n集計結果:")
        print(df_results)
        plot_data(df_results, x_label_input)
