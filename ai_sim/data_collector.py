# data collector object for model to get info on board state
import pandas as pd
import torch
import random

class DataCollector:
    def __init__(self,gather_data_types,model=None):
        self.game_count=0
        self.win_count=0
        self.model=model
        if model!=None:
            model.data_collector=self
        self.set_data_collect_types(gather_data_types)
        self.plyr=model.plyr
        self.game_log=pd.Series()
        self.card_df=pd.read_csv('C:/Users/lsp52/AnacondaProjects/card_sim/cards/M20_index.csv')

    def set_data_collect_types(self,gather_data_types):
        self.gather_data_types=gather_data_types
        # whether to collect data on game state for models
        self.gather_gamestate= 'game_state' in gather_data_types
        self.gather_attackers= 'attackers' in gather_data_types
        for i in gather_data_types:
            self.model.xtrain[i]=pd.DataFrame()
            self.model.ytrain[i]=pd.DataFrame()
            self.model.all_xtrain[i]=pd.DataFrame()
            self.model.all_ytrain[i]=pd.DataFrame()

    # function to note a new game had started.
    def game_start(self, single_turn=True):
        # param single_turn: whether to collect data on just a single turn this
        # game. If False, collects data at the end of all turns
        self.game_count+=1
        self.single_turn=single_turn
        # what turn from the first 20 to collect data from
        self.turn_collect=random.randint(2,16)

        # note whether data has been collected from a game yet
        self.collected=False

    # combine results into data collector's attribute dataframes
    def compile_results(self, results):
        keys = results[0][0].keys()
        for n in range(len(results)):
            for i in keys:
                xdf= results[n][0][i]
                ydf= results[n][1][i]
                self.model.all_xtrain[i]=self.model.all_xtrain[i].append(xdf,
                    sort=False, ignore_index=True)
                self.model.all_ytrain[i]=self.model.all_ytrain[i].append(ydf,
                    sort=False, ignore_index=True)

    # collect data on board state
    def get_gamestate(self,plyr=None):
        # if statement that handles whether we are collecting data on all turns of the game
        # or whether this data collector is just collecting data on a single turn
        # of the game
        if self.single_turn==False or (self.collected==False and self.plyr.game.turn_count==self.turn_collect
            and self.plyr.game.act_plyr==self.plyr):
            self.model.xtrain['game_state']=self.model.xtrain['game_state'].append(
                self.return_gamestate_data(plyr), ignore_index=True)
            self.collected==True

    def return_gamestate_data(self,plyr=None):
        if plyr==None:
            plyr=self.plyr
        self_creatures= [i for i in plyr.field if 'creature' in i.types]
        opp_creatures= [i for i in plyr.opponent.field if 'creature' in i.types]
        x=pd.Series({
            'game': self.game_count,
            'turn': plyr.game.turn_count,
            'num_lands':len([i for i in plyr.field if
                'land' in i.types]),
            'num_lands_opp':len([i for i in plyr.opponent.field if
                'land' in i.types]),
            'life': plyr.life,
            'life_opp':plyr.opponent.life,
            'handsize':len(plyr.hand),
            'handsize_opp':len(plyr.opponent.hand),
            'libsize':len(plyr.lib),
            'libsize_opp':len(plyr.opponent.lib),
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
            x[n+'_opp_field']=len([i for i in plyr.opponent.field if n==i.name])
            x[n+'_field']=len([i for i in plyr.field if n==i.name])
            x[n+'_hand']=len([i for i in plyr.hand if n==i.name])
        return(x)

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

        # get the model board analyzer assessment of board and add it as a feature
        game_state= self.return_gamestate_data()
        # ensure we're using the same feature set as expected by the model
        feats= game_state[self.model.xvars['game_state']]
        x['pwin_board'] = self.model.models['board_analyzer'](torch.from_numpy(
            feats.values).float().to(torch.device('cuda:0')))
        return(x)

    def end_game(self,winner):
        # record winner
        self.game_log[str(self.game_count)]=winner.name
        # record game state data
        # if we won the game, add to the training data. Otherwise, discard
        if self.gather_gamestate:
            result=int(winner.name==self.plyr.name)
            self.model.all_xtrain['game_state']=self.model.all_xtrain['game_state'].append(
                self.model.xtrain['game_state'], sort=False, ignore_index=True)
            self.model.all_ytrain['game_state']=self.model.all_ytrain['game_state'].append(
                pd.DataFrame({'win':result},index=self.model.xtrain['game_state'].index), sort=False, ignore_index=True)
            self.model.xtrain['game_state']=pd.DataFrame()
        if winner==self.plyr:
            self.win_count+=1
            for key in self.model.xtrain.keys():
                if key!='game_state':
                    self.model.all_xtrain[key]=self.model.all_xtrain[key].append(self.model.xtrain[key], sort=False,
                        ignore_index=True)
                    self.model.all_ytrain[key]=self.model.all_ytrain[key].append(self.model.ytrain[key], sort=False,
                        ignore_index=True)
                    self.model.xtrain[key]=pd.DataFrame()
                    self.model.ytrain[key]=pd.DataFrame()
            # train the network
            if self.model.dynamic_train==True:
                self.model.models['attackers'].train_bool(self.model.all_xtrain.values, self.model.all_ytrain.values,
                    epochs=50)
