# generate win percentages of casting card vs. not casting card

import pandas as pd

df=pd.read_csv("C:/Users/lsp52/AnacondaProjects/card_sim/output/spell_counts_2020_07_01-22_29_44.csv")

result_df=pd.DataFrame(index=['cast','not cast'],columns=df.columns)
for i in df.columns:
    cast= df.loc[df[i]>1]
    not_cast= df.loc[df[i]==1]
    cast_win= cast.winner.sum()/cast.winner.count()
    not_cast_win= not_cast.winner.sum()/not_cast.winner.count()
    total_games_cast= cast.winner.count()
    result_df.loc['cast',i]=cast_win
    result_df.loc['not cast',i]=not_cast_win
    result_df.loc['total_games_cast',i]=total_games_cast

result_df=result_df.T
result_df.to_csv('C:/Users/lsp52/AnacondaProjects/card_sim/output/win_percentages.csv')
