import sys 
import pandas as pd

print('argv :=', sys.argv)

month = int(sys.argv[1]) if len(sys.argv) > 1 and 1 <= int(sys.argv[1]) <= 12 and  1 <= int(sys.argv[1]) > 0 else 0
print(f"month := {month}")

df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
print(df.head())

df.to_parquet(f"output_day_{sys.argv[1]}.parquet")