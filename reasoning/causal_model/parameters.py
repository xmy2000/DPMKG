import networkx as nx

NODE_DIM = {
    'machine': 2,
    'tool': 12,
    'material': 3,
    'feature': 4,
    'process': 3,
    'wear': 1,
    'breakage': 2,
    'roughness': 1
}
MAX_DIM = 12

NODE_LST = ['machine', 'tool', 'material', 'feature', 'process', 'wear', 'breakage', 'roughness']
CLASSIFY_NODE_LST = ['machine', 'tool', 'material', 'feature', 'breakage']
REGRESSION_NODE_LST = ['process', 'wear', 'roughness']
EPS = 1e-15
MAX_LOGSTD = 10
DEVICE = 'cuda'

# graph create
LAYER_1 = ['machine', 'tool', 'material', 'feature', 'process']
LAYER_2 = ['wear', 'breakage']
LAYER_3 = ['roughness']
EDGE_LST = []
for l1 in LAYER_1:
    for l2 in LAYER_2:
        EDGE_LST.append((l1, l2))
    for l3 in LAYER_3:
        EDGE_LST.append((l1, l3))
for l2 in LAYER_2:
    for l3 in LAYER_3:
        EDGE_LST.append((l2, l3))
EDGE_LST.append(('machine', 'tool'))
EDGE_LST.append(('feature', 'tool'))
EDGE_LST.append(('feature', 'machine'))
EDGE_LST.append(('feature', 'process'))
EDGE_LST.append(('material', 'process'))
EDGE_LST.append(('tool', 'process'))
EDGE_LST.append(('wear', 'breakage'))

NX_GRAPH = nx.DiGraph(EDGE_LST)

DUMMIES = {
    'feature': {
        'fa': [1, 0, 0, 0],
        'fb': [0, 1, 0, 0],
        'fc': [0, 0, 1, 0],
        'fd': [0, 0, 0, 1]
    },
    'breakage': {
        'no': [1, 0],
        'yes': [0, 1]
    },
    'material': {
        'ma': [1, 0, 0],
        'mb': [0, 1, 0],
        'mc': [0, 0, 1]
    },
    'machine': {
        'ma_a': [1, 0],
        'ma_b': [0, 1]
    },
    'tool': {
        't1': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't2': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't3': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't4': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        't5': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        't6': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        't7': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        't8': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        't9': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        't10': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        't11': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        't12': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    }
}

DROPOUT = 0.0
