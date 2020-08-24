# define a class for game decision logic
class NN_Logic:
    def __init__(self,model):
        self.model=model

    def input_bool(self,game,label=None):
        return(None)

    def input_choose(self, player, choices,choose_color_cost=False,label=None, n=1):
        return(None)

    def input_order(self, object_list,label=None):
        return(None)
