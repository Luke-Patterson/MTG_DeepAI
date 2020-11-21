import sys
import datetime
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import scipy
import pickle
sys.path.append("..")
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torchvision import transforms


# define a class for game decision logic
class NN_Logic:
    def __init__(self,name=None):
        self.name=name
        self.models={}
        self.data_collector=None
        self.xtrain={}
        self.ytrain={}
        self.all_xtrain={}
        self.all_ytrain={}
        self.plyr=None
        self.test=False
        self.dynamic_train=False
        self.game_log=pd.Series()
        self.card_df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')
        self.xvars={}
        self.n_xvars={}
        self.board_analyzer=None

    # load board analyzer from pickle file
    def load_board_analyzer(self, file):
        self.models['board_analyzer'] = pickle.load(open(file, 'rb'))

    # assign data collector object to model
    def set_data_collector(self, data_collector):
        self.data_collector=data_collector
        data_collector.model=self


    def input_bool(self,decision,player=None,label=None,obj=None):
        # functions that MTG game will call
        if label=='make attack':
            x= self.data_collector.get_data(obj)
            # if we have some training data, start to make predictions
            if self.test==True:
                x = x[self.xvars['attackers']]
                predict=self.models['attackers'](torch.from_numpy(x.values).float().to(torch.device('cuda:0')))
                if predict>.5:
                    decision=True
                else:
                    decision=False

            if self.data_collector.gather_attackers==True:
                self.xtrain['attackers']=self.xtrain['attackers'].append(x, ignore_index=True, sort=False)
                self.ytrain['attackers']=self.ytrain['attackers'].append(pd.Series({'decision':decision}),
                    ignore_index=True, sort=False)
        return(decision)

    def input_choose(self, player, decision, choices,choose_color_cost=False,
        label=None, n=1):
        return(decision)

    def input_order(self, player, object_list,label=None):
        return(object_list)

    def export_results(self, drop_identical_cols=False):
        for i in self.all_xtrain.keys():
            xdf= self.all_xtrain[i]
            ydf= self.all_ytrain[i]
            if drop_identical_cols:
                # drop columns that are all the same value
                nunique = xdf.apply(pd.Series.nunique)
                cols_to_drop = nunique[nunique == 1].index
                xdf=xdf.drop(cols_to_drop, axis=1)
                nunique = ydf.apply(pd.Series.nunique)
                cols_to_drop = nunique[nunique == 1].index
                ydf=ydf.drop(cols_to_drop, axis=1)
            # export columns
            xtrain_cols= pickle.dump(xdf.columns, open('output/'+i+'_xtrain_cols.p', "wb"))
            ytrain_cols= pickle.dump(ydf.columns, open('output/'+i+'_ytrain_cols.p', "wb"))
            xdf = csr_matrix(xdf.values)
            ydf = csr_matrix(ydf.values)
            pickle.dump(xdf, open( 'output/'+i+'_xtrain.p', "wb" ) )
            pickle.dump(ydf, open( 'output/'+i+'_ytrain.p', "wb" ) )

    def set_bool_model(self,label):
        print('Number of Parameters:',self.n_xvars[label])
        self.models[label] = nn.Sequential(nn.Linear(self.n_xvars[label],self.n_xvars[label]*4),
                              nn.ReLU(),
                              nn.Linear(self.n_xvars[label]*4, self.n_xvars[label]*8),
                              nn.ReLU(),
                              nn.Linear(self.n_xvars[label]*8, self.n_xvars[label]*16),
                              nn.ReLU(),
                              nn.Linear(self.n_xvars[label]*16, 1),
                              nn.Sigmoid())
        self.models[label].batch_size=32
        self.models[label].to(torch.device('cuda:0'))

    def load_train_data(self, labels=['attackers','game_state'],
        drop_identical_cols=True):
        for i in labels:
            self.all_xtrain[i]=pickle.load(open('output/'+i+'_xtrain.p','rb'))
            self.all_xtrain[i]=pd.DataFrame.sparse.from_spmatrix(self.all_xtrain[i])
            self.all_xtrain[i].columns=pickle.load(open('output/'+i+'_xtrain_cols.p','rb'))
            self.all_ytrain[i]=pickle.load(open('output/'+i+'_ytrain.p','rb'))
            self.all_ytrain[i]=pd.DataFrame.sparse.from_spmatrix(self.all_ytrain[i])
            self.all_ytrain[i].columns=pickle.load(open('output/'+i+'_ytrain_cols.p','rb'))
            if drop_identical_cols:
                # drop columns that are all the same value
                nunique = self.all_xtrain[i].apply(pd.Series.nunique)
                cols_to_drop = nunique[nunique == 1].index
                print('dropping',len(cols_to_drop),'columns with all same values')
                self.all_xtrain[i]=self.all_xtrain[i].drop(cols_to_drop, axis=1)


    def load_models(self,labels=['attackers','game_state']):
        for i in labels:
            self.models[i]=pickle.load(open('models/nn_model_'+i+'.p', "rb" ))
            self.xvars[i]=pd.read_csv('models/'+i+'_feats_used.csv',header=None, squeeze=True)
            self.n_xvars[i]=len(self.xvars[i])

    def save_model(self,label):
        pickle.dump( self.models[label], open( "models/nn_model_"+label+".p", "wb" ) )
        # save the features used
        feats=pd.Series(self.all_xtrain[label].columns)
        feats=feats.str.replace('"','')
        feats.to_csv('output/'+label+'_feats_used.csv',index=False)

    def train_bool(self,label,epochs=5000):
        xtrain=self.all_xtrain[label]
        ytrain=self.all_ytrain[label]
        self.n_xvars[label]=len(xtrain.columns)
        self.set_bool_model(label)
        batch_size=self.models[label].batch_size
        transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.5,), (0.5,)),
                              ])
        device=torch.device('cuda:0')
        trainset=torch.from_numpy(np.concatenate((xtrain.values,ytrain.values),axis=1)).to(device)
        trainset=torch.utils.data.DataLoader(trainset,batch_size=batch_size, shuffle=True)
        criterion = nn.BCELoss()
        optimizer = torch.optim.SGD(self.models[label].parameters(), lr=0.01)
        running_loss = 0
        moving_avg_acc= []
        for e in range(epochs):
            start=datetime.datetime.now()
            running_loss = 0
            correct=0
            for obs in trainset:
                # split up the batch into labels and features
                split=torch.split(obs,self.n_xvars[label],dim=1)
                yvar=Variable(split[1])
                features=Variable(split[0])
                optimizer.zero_grad()
                # get the predictions
                output = self.models[label](features.float())
                # evaluate the predictions
                loss = criterion(output, yvar.float())
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
                correct += (torch.round(output) == yvar.float()).float().sum()
            else:
                accuracy=correct / (len(trainset)*batch_size)
                print('Epoch:',e,"| Training loss:", running_loss/len(trainset),
                    "| Accuracy:",accuracy, '| Epoch runtime:',datetime.datetime.now()-start)
                moving_avg_acc.append(accuracy)
            if e % 100:
                self.save_model(label)

        self.last_10_acc=sum(moving_avg_acc[-10:])/10
