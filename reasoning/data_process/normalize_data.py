import pandas as pd
import numpy as np

data = pd.read_csv("../data/filter_data.csv")
data = data.replace(-1, np.nan)
data = data.rename(columns={
    '加工类型': 'process_type',
    '特征类型': 'feature_type',
    '进给量': 'feed',
    '转速': 'rotate',
    '切深': 'depth',
    '是否破损': 'breakage_flag',
    '破损类型': 'breakage_type',
    '磨损量': 'wear',
    '破损尺寸': 'breakage_size',
    '粗糙度': 'roughness',
    '零件材料': 'material',
    '机床': 'machine',
    '刀具类型': 'tool_type'
})
normalize_col = []
norm_data = data[normalize_col]

means = norm_data.mean()
stds = norm_data.std(ddof=0)

df_standardized = (norm_data - means) / stds

data[normalize_col] = df_standardized
data.to_csv("../data/data.csv", index=False)
