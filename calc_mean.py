import sys
import pandas as pd
import glob

args=sys.argv
if len(sys.argv) < 2:
    print("Usage: python3 calc_mean.py [file]")
    sys.exit(1)

file = open(args[1])
df = pd.read_csv(file, header=0)
mean = df.mean()
output_file = open(args[1].replace('.csv', '_mean.csv'), 'w')
output_file.write(mean.to_string())
