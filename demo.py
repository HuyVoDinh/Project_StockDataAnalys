import pandas as pd

vol_symbol_list_1 = ['HPG', 'NVL']
vol_symbol_list_2 = ['ASD', 'TCB']

df1 = pd.DataFrame(vol_symbol_list_1, columns=['vol_symbol_list_1'])
df2 = pd.DataFrame(vol_symbol_list_2, columns=['vol_symbol_list_2'])

result_data = pd.concat([df1, df2], axis=1)
result_data.to_csv("D:/Project/Project_StockDataAnalys/data.csv", index=False)