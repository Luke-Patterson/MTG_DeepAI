# index set in a data frame
import json
import pandas as pd
import sys
sys.path.append("..")
from Card_types import *
from M20_cards import *
from copy import deepcopy

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False

M20_df=pd.DataFrame()
objs=deepcopy(list(locals().keys()))
for i in objs:
    obj=locals()[i]
    if isinstance(obj, Card):
        obj_ser=pd.Series(obj.__dict__)
        obj_row=pd.Series()
        for idx,item in obj_ser.iteritems():
            if is_jsonable(item):
                obj_row[idx]=item
        obj_row['object_name']=i
        M20_df=M20_df.append(obj_row,ignore_index=True)

M20_df.to_csv('M20_index.csv')
