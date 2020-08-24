import sys
import datetime
import numpy as np
import pandas as pd
import pickle
sys.path.append("..")
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torchvision import transforms


# define a class for game decision logic
class NN_Logic:
    def __init__(self, gather_data_types=[]):
        self.models={}
        self.game_count=0
        self.win_count=0
        # whether to collect data on game state for models
        self.gather_gamestate= 'game_state' in gather_data_types
        self.gather_attackers= 'attackers' in gather_data_types
        self.xtrain={}
        self.ytrain={}
        self.all_xtrain={}
        self.all_ytrain={}
        for i in gather_data_types:
            self.xtrain[i]=pd.DataFrame()
            self.ytrain[i]=pd.DataFrame()
            self.all_xtrain[i]=pd.DataFrame()
            self.all_ytrain[i]=pd.DataFrame()
        self.plyr=None
        self.test=False
        self.dynamic_train=False
        self.game_log=pd.Series()
        self.card_df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')
        self.xvars={}
        self.n_xvars={}

    # function to note a new game had started.
    def game_start(self):
        self.game_count+=1

    # collect data on board state
    def get_gamestate(self):
        self_creatures= [i for i in self.plyr.field if 'creature' in i.types]
        opp_creatures= [i for i in self.plyr.opponent.field if 'creature' in i.types]
        x=pd.Series({
            'game': self.game_count,
            'turn': self.plyr.game.turn_count,
            'num_lands':len([i for i in self.plyr.field if
                'land' in i.types]),
            'num_lands_opp':len([i for i in self.plyr.opponent.field if
                'land' in i.types]),
            'life': self.plyr.life,
            'life_opp':self.plyr.opponent.life,
            'handsize':len(self.plyr.hand),
            'handsize_opp':len(self.plyr.opponent.hand),
            'libsize':len(self.plyr.lib),
            'libsize_opp':len(self.plyr.opponent.lib),
            'num_creatures':len([i for i in self_creatures]),
            'num_tapped_creatures':len([i for i in self_creatures if i.tapped]),
            'opp_creatures':len([i for i in opp_creatures]),
            'opp_untapped_creatures':len([i for i in opp_creatures if i.legal_blocker()]),
            'opp_tapped_creatures':len([i for i in opp_creatures if i.tapped])
            }
        )
        # count number of creatures with keywords
        for abil in ['first strike','lifelink','flying','vigilance',
            'double strike','hexproof','defender','unblockable',
            'reach','indestructible','flash']:
            x['ncreatures_opp_'+abil] = len([i for i in opp_creatures if i.check_keyword(abil)])
            x['ncreatures_'+abil] = len([i for i in self_creatures if i.check_keyword(abil)])

        # count num of power and toughness combos on creatures
        for tough in range(0,7):
            for power in range(0,7):
                x['opp_power_'+str(power)+'tough_'+str(tough)] = len([i for i in opp_creatures if
                    i.power==power and i.toughness==tough])
                x['power_'+str(power)+'tough_'+str(tough)] = len([i for i in self_creatures if
                    i.power==power and i.toughness==tough])
        # aggregate those 7 and over
        for tough in range(0,7):
            power= 7
            x['opp_power_'+str(power)+'tough_'+str(tough)] = len([i for i in opp_creatures if i.power>=power and i.toughness==tough])
            x['power_'+str(power)+'tough_'+str(tough)] = len([i for i in self_creatures if i.power>=power and i.toughness==tough])
        for power in range(0,7):
            tough= 7
            x['opp_power_'+str(power)+'tough_'+str(tough)] = len([i for i in opp_creatures if i.power==power and i.toughness>=tough])
            x['power_'+str(power)+'tough_'+str(tough)] = len([i for i in self_creatures if i.power==power and i.toughness>=tough])

        # count
        for n in self.card_df.name:
            x[n+'_opp_field']=len([i for i in self.plyr.opponent.field if n==i.name])
            x[n+'_field']=len([i for i in self.plyr.field if n==i.name])
            x[n+'_hand']=len([i for i in self.plyr.hand if n==i.name])
        self.xtrain['game_state']=self.xtrain['game_state'].append(x, ignore_index=True, sort=False)

    # get data about an object, and the current game state
    def get_data(self, obj):
        self_creatures= [i for i in self.plyr.field if 'creature' in i.types]
        opp_creatures= [i for i in self.plyr.opponent.field if 'creature' in i.types]
        x=pd.Series({
            # 'game': self.game_count,
            # 'turn': player.game.turn_count,
            'num_lands':len([i for i in self.plyr.field if
                'land' in i.types]),
            'num_lands_opp':len([i for i in self.plyr.opponent.field if
                'land' in i.types]),
            'life': self.plyr.life,
            'life_opp':self.plyr.opponent.life,
            'handsize':len(self.plyr.hand),
            'handsize_opp':len(self.plyr.opponent.hand),
            'libsize':len(self.plyr.lib),
            'libsize_opp':len(self.plyr.opponent.lib),
            'num_creatures':len([i for i in self_creatures]),
            'num_untapped_creatures':len([i for i in self_creatures if i.legal_blocker()]),
            'num_tapped_creatures':len([i for i in self_creatures if i.tapped]),
            'num_creat_great_power':len([i for i in self_creatures if i.power>=obj.toughness and i.legal_blocker()]),
            'num_creat_great_toughness':len([i for i in self_creatures if i.toughness>=obj.power and i.legal_blocker()]),
            'num_creat_great_both':len([i for i in self_creatures if i.toughness>=obj.power and
                i.power>=obj.toughness and i.legal_blocker()]),
            'num_creat_less_power':len([i for i in self_creatures if i.power<obj.toughness and i.legal_blocker()]),
            'num_creat_less_toughness':len([i for i in self_creatures if i.toughness<obj.power and i.legal_blocker()]),
            'num_creat_less_both':len([i for i in self_creatures if i.toughness<obj.power and
                i.power<obj.toughness and i.legal_blocker()]),
            'opp_creatures':len([i for i in opp_creatures]),
            'opp_untapped_creatures':len([i for i in opp_creatures if i.legal_blocker()]),
            'opp_tapped_creatures':len([i for i in opp_creatures if i.tapped]),
            'opp_creat_great_power':len([i for i in opp_creatures if i.power>=obj.toughness and i.legal_blocker()]),
            'opp_creat_great_toughness':len([i for i in opp_creatures if i.toughness>=obj.power and i.legal_blocker()]),
            'opp_creat_great_both':len([i for i in opp_creatures if i.toughness>=obj.power and
                i.power>=obj.toughness and i.legal_blocker()]),
            'opp_creat_less_power':len([i for i in opp_creatures if i.power<obj.toughness and i.legal_blocker()]),
            'opp_creat_less_toughness':len([i for i in opp_creatures if i.toughness<obj.power and i.legal_blocker()]),
            'opp_creat_less_both':len([i for i in opp_creatures if i.toughness<obj.power and
                i.power<obj.toughness and i.legal_blocker()]),
        })
        # add boolean versions of each creature count parameters
        for i in x.keys():
            if 'creat' in i:
                x[i+'_bool']=x[i]
                if x[i+'_bool']>1:
                    x[i+'_bool']=1

        # add count of each card
        for n in self.card_df.name:
            x[n+'_opp_field']=len([i for i in self.plyr.opponent.field if n==i.name])
            x[n+'_field']=len([i for i in self.plyr.field if n==i.name])
            x[n+'_opp_tapped']=len([i for i in opp_creatures if n==i.name and i.legal_blocker()])
            x[n]= 0
            if any([i for i in self.plyr.field if n==obj.name]):
                x[n]=1
            x[n+'_hand']=len([i for i in self.plyr.hand if n==i.name])
            # some speculative corner case ones
            # x[n+'_stack']=len([i for i in self.plyr.game.stack if n==i.name])
            # x[n+'_attached']=len([i for i in obj.attached_objs if n==i.name])
            # x[n+'_revealed']=len([i for i in self.plyr.known_info if n==i[0]]
            #     and 'hand'==i[1])

        # add obj characteristics
        if 'creature' in obj.types:
            x['power'] = obj.power
            x['toughness'] = obj.toughness
            x['base_power'] = obj.base_power
            x['base_toughness'] = obj.base_toughness
            x['damage_received'] = obj.damage_received
            for abil in ['first strike','lifelink','flying','vigilance',
                'double strike','hexproof','defender','unblockable',
                'reach','indestructible','flash']:
                x[abil] = int(obj.check_keyword(abil))
        for color in ['W','U','B','R','G']:
            x[color] = int(color in obj.colors)
        x['plus1_plus1_counters']=len([i for i in obj.attached_objs if i.name=='+1/+1 counter'])
        return(x)

    def input_bool(self,decision,player=None,label=None,obj=None):
        # functions that MTG game will call
        if label=='make attack':
            x= self.get_data(obj)
            # if we have some training data, start to make predictions
            if self.test==True:
                x = x[self.xvars['attackers']]
                predict=self.models['attackers'](torch.from_numpy(x.values).float().to(torch.device('cuda:0')))
                if predict>.5:
                    decision=True
                else:
                    decision=False

            if self.gather_attackers==True:
                self.xtrain['attackers']=self.xtrain['attackers'].append(x, ignore_index=True, sort=False)
                self.ytrain['attackers']=self.ytrain['attackers'].append(pd.Series({'decision':decision}),
                    ignore_index=True, sort=False)
        return(decision)

    def input_choose(self, player, decision, choices,choose_color_cost=False,
        label=None, n=1):
        return(decision)

    def input_order(self, player, object_list,label=None):
        return(object_list)

    def compile_results(self, results):
        # combine results into data collector's attribute dataframes
        keys = results[0][0].keys()
        for n in range(len(results)):
            for i in keys:
                xdf= results[n][0][i]
                ydf= results[n][1][i]
                self.all_xtrain[i]=self.all_xtrain[i].append(xdf,
                    sort=False, ignore_index=True)
                self.all_ytrain[i]=self.all_ytrain[i].append(ydf,
                    sort=False, ignore_index=True)

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
            xdf.to_csv('output/'+i+'_xtrain.csv', index=False)
            ydf.to_csv('output/'+i+'_ytrain.csv', index=False)


    def end_game(self,winner):
        # record winner
        self.game_log[str(self.game_count)]=winner.name
        # record game state data
        # if we won the game, add to the training data. Otherwise, discard
        if self.gather_gamestate:
            result=int(winner.name==self.plyr.name)
            self.all_xtrain['game_state']=self.all_xtrain['game_state'].append(
                self.xtrain['game_state'], sort=False, ignore_index=True)
            self.all_ytrain['game_state']=self.all_ytrain['game_state'].append(
                pd.DataFrame({'win':result},index=self.xtrain['game_state'].index), sort=False, ignore_index=True)
            self.xtrain['game_state']=pd.DataFrame()
        if winner==self.plyr:
            self.win_count+=1
            for key in self.xtrain.keys():
                if key!='game_state':
                    self.all_xtrain[key]=self.all_xtrain[key].append(self.xtrain[key], sort=False,
                        ignore_index=True)
                    self.all_ytrain[key]=self.all_ytrain[key].append(self.ytrain[key], sort=False,
                        ignore_index=True)
                    self.xtrain[key]=pd.DataFrame()
                    self.ytrain[key]=pd.DataFrame()
            # train the network
            if self.dynamic_train==True:
                self.models['attackers'].train_bool(self.all_xtrain.values, self.all_ytrain.values,
                    epochs=50)

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
            self.all_xtrain[i]=pd.read_csv('output/'+i+'_xtrain.csv')
            self.all_ytrain[i]=pd.read_csv('output/'+i+'_ytrain.csv')
            if drop_identical_cols:
                # drop columns that are all the same value
                nunique = self.all_xtrain[i].apply(pd.Series.nunique)
                cols_to_drop = nunique[nunique == 1].index
                self.all_xtrain[i]=self.all_xtrain[i].drop(cols_to_drop, axis=1)
            # save the features used
            feats=pd.Series(self.all_xtrain[i].columns)
            feats=feats.str.replace('"','')
            feats.to_csv('output/'+i+'_feats_used.csv',index=False, name=False)

    def load_models(self,labels=['attackers','game_state']):
        for i in labels:
            self.models[i]=pickle.load(open('models/nn_model_'+i+'.p', "rb" ))
            self.xvars[i]=pd.read_csv('output/'+i+'_feats_used.csv',header=None, squeeze=True)
            self.n_xvars[i]=len(self.xvars[i])

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
        self.last_10_acc=sum(moving_avg_acc[-10:])/10
