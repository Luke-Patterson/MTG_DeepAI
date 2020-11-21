import pandas as pd
import scipy
import pickle

xdf=pd.DataFrame()
ydf=pd.DataFrame()
for i in range(1,11):
    xdf=xdf.append(pd.DataFrame.sparse.from_spmatrix(pd.read_pickle('game_state_xtrain_pt'+str(i)+'.p')))
    ydf=ydf.append(pd.DataFrame.sparse.from_spmatrix(pd.read_pickle('game_state_ytrain_pt'+str(i)+'.p')))
import pdb; pdb.set_trace()
xdf=scipy.sparse.csr_matrix(xdf.values)
ydf=scipy.sparse.csr_matrix(ydf.values)
pickle.dump(xdf, open( 'game_state_xtrain.p', "wb" ) )
pickle.dump(ydf, open( 'game_state_ytrain.p', "wb" ) )
