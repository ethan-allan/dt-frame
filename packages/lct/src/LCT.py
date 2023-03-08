"""
This is the code for the LCT

"""
#%% 
# import libraries
import random
import copy
import math
import pandas as pd
from gen_rule_pop import *

# CONFIG FILE
# Configuration file (setting the variables used later)

# Parameters for LCT
###### fitness update
algo_select =  'winner_takes_all'     # 'roulette_wheel' or 'winner_takes_all'    
objective_select = 'vel_first'      #or d_first or phi_first        # for choosing what to reward for 
beta = 0.9                          # choose value
min_v = 0.4                          # choose a min value
max_v = 5                           # check max value (assuming the ROS node would give the vel in m/s)
stop_v = 0.2                        # the speed below which would be considered stopped/crashed

###### action selection
selected_rule = -1
best_fitness = 0

###### apply action
act = 0.3                            # setting initial gain
last_rule = pd.Series(dtype='float64')             # inital last_rule is empty Series

rule_pop = make_rule_pop(5000)

# The constants class saves the variables set in the 'Configuration file' as global constants
class Constants:
    # def __init__(self):
        # self.setConstants()
    def __str__(self) -> str:                       # not sure what the -> str does but came up in autofill
        return "This is the constants class"
    def setConstants(self):
        #### LCT parameters
        self.rule_pop = rule_pop
        ## fitness update
        self.algo_select = algo_select
        self.objective_select = objective_select
        self.beta = beta
        self.min_v = min_v
        self.max_v = max_v
        self.stop_v = stop_v

        ## action selection
        self.last_rule = last_rule
        self.selected_rule = selected_rule
        self.best_fitness = best_fitness
        
        ## apply action
        self.act = act

        self.counter = 0            # for debugging testing large rule pops

        # tbc
cons = Constants()
cons.setConstants()
#%%
# LCT CLASS
# LCT class contains the functions for updating fitness, action selection, and applying the action
# based on c code for implementing LCT 
class LCT:
    def __str__(self) -> str:
        return "This is the LCT class"
    #def __init__(self): 
        #cons = Constants()
        #cons.setConstants()
    def updatefitness(self, d, phi, v):
        #cons = Constants()
        #cons.setConstants()
        #print("Running fitness update")
        if cons.last_rule.empty:
            #print("No action was selected last instance")
            for i, rule in cons.rule_pop.iterrows():                # iterate through each rule 
                    #print(f"rule {i}")
                    # print(rule["in_match_set"])
                    rule["in_match_set"] = 0                        # reset in_match_set to false
                    # print(rule["in_match_set"])
        else:
            reward = 0
            # rewarding for fast speed
            if objective_select == "vel_first" and cons.min_v <= v <= cons.max_v:
                #print("rewarded for fast speed")
                reward = 10 # +ve val
            # punishment for slow speed
            if objective_select == "vel_first" and 0 <= v <= cons.min_v:
                #print("punished for slow speed")
                reward = -10 # -ve val
            # punishment for crashing (going really slow)
            if objective_select == "vel_first" and 0 <= v <= cons.stop_v:
                #print("punished for crashing")
                reward = -20 # -ve val (bigger)
                        
            for i, rule in cons.rule_pop.iterrows():             # iterate through each rule 
                if cons.rule_pop["in_match_set"][i] == 1:                   # if the value of in_match_set is True
                    if cons.rule_pop["act"][i] == cons.last_rule["act"]: 
                        #print(f"Rule {i} has been updated")
                        cons.rule_pop["fit"][i] = cons.rule_pop["fit"][i] + (beta * (reward - rule["fit"]))
                        cons.rule_pop["in_match_set"][i] = 0
                    else:
                        #print(f"The action of the current rule (Rule {i}) does not equal the action of the last rule")
                        cons.rule_pop["in_match_set"][i] = 0
                    
    def actionselection(self, d, phi, v):
        #cons = Constants()
        #cons.setConstants()
        if algo_select == 'winner_takes_all':
            for i, rule in cons.rule_pop.iterrows():             # iterate through each rule
                #print(f"Current Rule: {i}")
                rule_vel_match = rule["vel_lower"] <= v <= rule["vel_upper"]        # true if velocity in range
                #print(f'vel_lower: {rule["vel_lower"]}, vel_upper{rule["vel_upper"]}')
                rule_d_match = rule["d_lower"] <= d <= rule["d_upper"]              # true if d in range
                rule_phi_match = rule["phi_lower"] <= phi <= rule["phi_upper"]      # true if phi in range
                rule_match = rule_vel_match and rule_d_match and rule_phi_match

                if rule_match:
                    cons.rule_pop["in_match_set"][i] = 1
                    #print(f"best fit: {cons.best_fitness}, rule fit :{cons.rule_pop['fit'][i]}")
                    #print(cons.best_fitness < cons.rule_pop["fit"][i])
                    # print("best fit < rule fit")
                    
                    # print(f"Matched rule: {i}")
                    # print(f'match set:{rule["in_match_set"]}')
                    # cons.counter += 1
                    if cons.best_fitness <= cons.rule_pop["fit"][i]:         # this doesnt work 
                        
                        cons.selected_rule = i
                        cons.best_fitness = cons.rule_pop["fit"][i]
                        #print(f"best fitness: {cons.best_fitness}")
        
        elif algo_select == "roulette_wheel":
            acc_weight_list = [] 
            fitness_sum = 0
            for i, rule in cons.rule_pop.iterrows():
                #print(f"Current Rule: {i}")
                rule_vel_match = rule["vel_lower"] <= v <= rule["vel_upper"]        # true if velocity in range
                rule_d_match = rule["d_lower"] <= d <= rule["d_upper"]              # true if d in range
                rule_phi_match = rule["phi_lower"] <= phi <= rule["phi_upper"]      # true if phi in range
                rule_match = rule_vel_match and rule_d_match and rule_phi_match
                if rule_match:
                    cons.rule_pop["in_match_set"][i] = 1                # cons.rule_pop["in_match_set"][i] = 1
                    fitness_sum += rule["fit"]
                    acc_weight_list.append(fitness_sum)
                    #print(f"fitness sum: {fitness_sum} & weight list: {acc_weight_list}")
                else:
                    acc_weight_list.append(fitness_sum)
                
            if fitness_sum > 0:
                rand_number = random.random()
                rand_number = rand_number * fitness_sum
                for i, rule in cons.rule_pop.iterrows():
                    if cons.rule_pop["in_match_set"][i] == 1:
                        #print(f"rule {i} matches")
                        #print(f"the random number is {rand_number}")
                        if rand_number <= acc_weight_list[i]:
                            cons.selected_rule = i
                            cons.best_fitness = cons.rule_pop["fit"][i]
                        

        #print(f"Best fitness is {cons.best_fitness} and the selected rule is {cons.selected_rule}")    
        return cons.best_fitness, cons.selected_rule 
                    
    def applyaction(self, d, phi, v):
        #cons = Constants()
        #cons.setConstants()
        if cons.selected_rule == -1:                                # no rule selected so nothing's done
            #print("No rule selected")
            cons.last_rule = pd.Series(dtype="float64")          # create empty series
        else:            
            print(f"Selected rule: {cons.selected_rule}, gain from selected rule: {cons.rule_pop['act'][cons.selected_rule]} == {cons.act}")           # apply the action of the selected rule
            cons.act = cons.rule_pop["act"][cons.selected_rule]    # get action
            cons.last_rule = cons.rule_pop.iloc[cons.selected_rule]#.astype("float64")  # set current rule to last rule
            cons.counter += 1
        #return cons.gain   

# run LCT class
# class for running the LCT (runs the methods in the LCT class, add timing here?)
class runLCT:
    def __init__(self):
        #print("Initialize LCT algorithm")
        #...
    
        #self.run_LCT()
        pass

    def run_LCT(self, d, phi, v):
        LCT().updatefitness(d, phi, v)
        LCT().actionselection(d, phi, v)
        LCT().applyaction(d, phi, v)
        return float(cons.act)
"""
for x in range(3):
    out = runLCT().run_LCT(-0.06,-0.35,0.3)
#cons.rule_pop.iloc[114]
print(f"{out} is type {type(out)}")
"""