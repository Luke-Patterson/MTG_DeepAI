can_pay=[]
for p_mana in self.potential_mana:
    pay_cost=True
    for i in mana_cost.keys():
        print(i)
        print(p_mana[i])
        print(p_mana)
        if i!='C' and p_mana[i]<mana_cost[i]:
            pay_cost=False
    # check to see if we have enough total mana
    if sum(mana_cost.values())>sum(p_mana.values()):
        pay_cost=False
    # also check that all permutations can be activated
    can_pay.append(pay_cost)
