import pandas as pd
import sys

if len(sys.argv) != 2:
    print("Usage: python grep_watts.py <power_log.csv>")
    exit(1)

power_log_file = sys.argv[1]

# 5行目をヘッダーとして読み込む (header=4 は 0始まりのインデックス)
df = pd.read_csv(power_log_file, header=4)

# 日時とWattsの列だけを抽出する
# 'Watts' は Socket 0, 'Watts.1' は Socket 1 を指します
watts_df = df[['Watts']]
# watts_df = df[['Watts', 'Watts.1']]

# 分かりやすい名前に変更（任意）
watts_df = watts_df.rename(columns={'Watts': 'Socket0_Watts'})
# watts_df = watts_df.rename(columns={'Watts': 'Socket0_Watts', 'Watts.1': 'Socket1_Watts'})

# 新しいCSVファイルに保存
watts_df.to_csv(power_log_file.replace('.csv', '_watts.csv'), index=False)
