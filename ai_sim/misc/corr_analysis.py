import pandas as pd
import pickle
from scipy.sparse import csr_matrix
path='C:/Users/lsp52/AnacondaProjects/card_sim/ai_sim/'

full_xdf=pd.DataFrame(columns=pickle.load(open(path+'output/game_state_xtrain_cols.p','rb')))
full_ydf=pd.DataFrame(columns=pickle.load(open(path+'output/game_state_ytrain_cols.p','rb')))

i=1
xdf = pickle.load(open(path+'output/game_state_xtrain_pt'+str(i)+'.p','rb'))
xdf= pd.DataFrame.sparse.from_spmatrix(xdf)
xdf.columns=full_xdf.columns
ydf = pickle.load(open(path+'output/game_state_ytrain_pt'+str(i)+'.p','rb'))
ydf = pd.DataFrame.sparse.from_spmatrix(ydf)
ydf.columns=full_ydf.columns

full_xdf=full_xdf.append(xdf)
full_ydf=full_ydf.append(ydf)

xdf = pickle.load(open(path+'output/game_state_xtrain.p','rb'))
xdf= pd.DataFrame.sparse.from_spmatrix(xdf)
xdf.columns=full_xdf.columns
ydf = pickle.load(open(path+'output/game_state_ytrain.p','rb'))
ydf = pd.DataFrame.sparse.from_spmatrix(ydf)
ydf.columns=full_ydf.columns

full_xdf=full_xdf.append(xdf).reset_index()
full_ydf=full_ydf.append(ydf).reset_index()

df = full_xdf.merge(full_ydf,left_index=True, right_index=True)
df['win']=df['win'].astype('int')
corr=df.corr()
print(df.corr()['win'])
