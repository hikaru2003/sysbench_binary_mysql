import os
import glob
import matplotlib.pyplot as plt
import pandas as pd

def collect_data():
    data = []
    files = glob.glob("**/power_run1_watts_mean.csv", recursive=True)
    
    if not files:
        print("ファイルが見つかりませんでした。")
        return None

    for file_path in files:
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
    # ディレクトリ名でソート
    df = df.sort_values('directory').reset_index(drop=True)
    return df

def plot_data(df):
    if df is None or df.empty:
        return

    plt.figure(figsize=(12, 6))
    bars = plt.bar(df['directory'], df['total_watts'], color='skyblue', edgecolor='navy')
    
    # --- Y軸の範囲を調整するロジック ---
    min_val = df['total_watts'].min()
    max_val = df['total_watts'].max()
    margin = (max_val - min_val) * 0.2  # 上下に20%の余白を持たせる
    
    # 差がほとんどない場合のフォールバック
    if margin == 0:
        margin = min_val * 0.05
        
    plt.ylim(min_val - margin, max_val + margin)
    # ---------------------------------

    # 各バーの上に数値を表示
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', 
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.xlabel('Experiment Configuration (Directory)')
    plt.ylabel('Total Watts (Socket0 + Socket1)')
    plt.title('Total Power Consumption (Zoomed)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig('power_consumption.png')
    print("グラフを 'power_consumption.png' として保存しました。")
    plt.show()

if __name__ == "__main__":
    df_results = collect_data()
    if df_results is not None:
        print("集計結果:")
        print(df_results)
        plot_data(df_results)
