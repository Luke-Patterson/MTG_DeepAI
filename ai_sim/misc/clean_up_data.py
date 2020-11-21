# 11-21-2020

# this is to randomly select one turn from each game in the training data collected
# for full games. These files have been since moved to old/train_full_games
import pandas as pd
from scipy.sparse import csr_matrix
import pickle

path='C:/Users/lsp52/AnacondaProjects/card_sim/ai_sim/'

full_xdf=pd.DataFrame(columns=pickle.load(open(path+'output/game_state_xtrain_cols.p','rb')))
full_ydf=pd.DataFrame(columns=pickle.load(open(path+'output/game_state_ytrain_cols.p','rb')))
# load data
for i in range(1,11):
    print(i)
    xdf = pickle.load(open(path+'output/game_state_xtrain_pt'+str(i)+'.p','rb'))
    xdf= pd.DataFrame.sparse.from_spmatrix(xdf)
    xdf.columns=full_xdf.columns
    ydf = pickle.load(open(path+'output/game_state_ytrain_pt'+str(i)+'.p','rb'))
    ydf = pd.DataFrame.sparse.from_spmatrix(ydf)
    ydf.columns=full_ydf.columns

    # games are not demarkated, we'll note a new game when the turn decreases suddenly
    xdf['turn_diff']=xdf.turn.diff()
    xdf['game_flag']=0
    xdf.loc[xdf.turn_diff<0,'game_flag']=1
    xdf['game_idx']=xdf.cumsum()['game_flag']
    idx_vals=xdf[['game_idx']].groupby('game_idx',group_keys=False).apply(lambda x: x.sample(1)).index
    xdf=xdf.drop(['turn_diff','game_flag','game_idx'],axis=1)
    full_xdf=full_xdf.append(xdf.loc[idx_vals,])
    full_ydf=full_ydf.append(ydf.loc[idx_vals,])
full_xdf=full_xdf.fillna(0)
full_ydf=full_ydf.astype('int')

full_xm = csr_matrix(full_xdf.values)
full_ym = csr_matrix(full_ydf.values)
pickle.dump(full_xm, open(path+ 'output/game_state_xtrain.p', "wb" ) )
pickle.dump(full_ym, open(path+ 'output/game_state_ytrain.p', "wb" ) )
