# -*- coding: utf-8 -*-
"""
Created on Mon May 22 13:38:07 2023

@author: Shaoxuan
"""

from pulp import *
import pandas as pd
import numpy as np
import pulp as pl


class MP2P_DSCR:
    def __init__(self, config):
        # Import dictionary file with config params
        self.num_agents = config['num agents']
        self.max_occupancy = config['max agent SC']
        self.min_occupancy = config['min agent SC']
        self.total_SC = config['receiver num SC']
        self.sc_cap = config['SC capacity']

    def load_input_data(self, in_traffic, in_current):
        # if current is list with ints of numbers of SCs occupied ie. [2,3,4]
        # Mu has to be calculated for each potential SC config

        configurations = pd.read_csv('ILP_Optimization_SC_Configs.csv', index_col=0)
        sc_count = configurations.sum(axis=1)
        sc_count.name = 'sc_count'
        configurations = configurations.join(sc_count)
        indx = pd.DataFrame(list(range(len(configurations))), columns=['indx'])
        configurations = configurations.join(indx)

        agent_info = {'ID': [], 'Beta': [], 'delta_dc': [], 'delta_cs': [], 'mu_dc': [], 's_total': [], 'Channels': [], 'subcarriers': []}
        beta_max = []
        mu_max = []

        num_agent = len(in_traffic)
        for i in range(num_agent):
            current = in_current[i]
            traffic = in_traffic[i]

            current_sc = []
            for j in range(self.total_SC):
                current_sc.append(0)
            for k in range(len(current)):
                ind = current[k]
                current_sc[ind] = 1

            # calculate possibilities based on continuous SCs
            # 1. limit rows based on max num of SC
            subset = configurations[configurations['sc_count'] <= self.max_occupancy]

            # 2. Limit rows on continuity
            channel = pd.DataFrame()
            channel = channel.append(configurations.iloc[0])  # Channel 0 is always an option
            for l in range(len(current)):
                str = '%d' % (current[l])
                right = '%d' % ((current[l] + 1) % self.total_SC)
                left = '%d' % ((current[l] - 1) % self.total_SC)
                temp = subset.loc[subset[str] == 1]
                #sub_cont = subset[subset['sc_count'] == self.min_occupancy]
                if str != '15':
                    temp_left = subset.loc[subset[right] == 1]
                    channel = channel.append(temp_left)
                if str != '0':
                    temp_right = subset.loc[subset[left] == 1]
                    channel = channel.append(temp_right)
                channel = channel.append(temp)
            channel = channel.drop_duplicates(subset='indx')

            s_count = list(subset['sc_count'])

            curr_np = np.array(current_sc)
            curr_loc = np.where(curr_np == 1)[0]
            if curr_loc.size == 0:
                channel = subset

            # 3. Add Beta Row to track movements Dimensions 1x58
            beta = []
            for m in range(len(subset)):
                temp_l = list(subset.iloc[m])
                temp_l = temp_l[0:self.total_SC]
                new = list(temp_l)
                new_count = new.count(1)
                original = current_sc.count(1)
                sc_diff = abs(original - new_count)

                new_np = np.array(new)
                old_np = np.array(current_sc)

                new_pos = np.where(new_np == 1)[0]
                old_pos = np.where(old_np == 1)[0]

                if new_pos.size == 0:
                    new_pos = 0
                else:
                    new_pos = int(new_pos[0])
                if old_pos.size == 0:
                    old_pos = 0
                else:
                    old_pos = old_pos[0]

                pos_diff = abs(new_pos - old_pos)

                beta_element = pos_diff #+ sc_diff

                if m == 0:
                    beta_element = sc_diff

                beta.append(beta_element)

            max_b = np.max(np.array(beta))
            beta_max.append(max_b)

            delta_dc = []
            for n in range(len(subset)):
                delta_dc.append(0)
            for o in range(len(channel)):
                end = channel['indx'].iloc[o]
                delta_dc[end] = 1

            # Mu_dc
            mu_dc = []
            for q in range(len(subset)):
                pot_cap = s_count[q] * self.sc_cap
                if pot_cap >= traffic:
                    mu_dc.append(0)
                else:
                    mu_dc.append(abs(pot_cap - traffic))
            max_m = np.max(np.array(mu_dc))
            mu_max.append(max_m)

            subs = []
            for r in range(len(subset)):
                tp = list(subset.iloc[r, 0:16])
                subs.append(tp)

                #subs.append(list(options.iloc[r, 0:16]))

            # Save in dictionary or some structure to have info for each TA
            agent_info['ID'].append(i + 1)
            agent_info['Beta'].append(beta)
            agent_info['delta_dc'].append(delta_dc)
            agent_info['mu_dc'].append(mu_dc)
            agent_info['s_total'].append(s_count)

        # delta_cs = []
        # for p in range(len(options)):
        #     delta_cs.append(list(options.iloc[0, 0:self.total_SC]))
        # for pp in range(len(channel)):
        #     endx = channel['indx'].iloc[pp]
        #     replacement = list(channel.iloc[pp, 0:self.total_SC])
        #     delta_cs[endx] = replacement

        delta_cs = []
        for p in range(self.total_SC):
            delta_cs.append(list(subset.iloc[:,p]))


        agent_info['delta_cs'].append(delta_cs)
        #agent_info['subcarriers'].append(subs)
        agent_info['subcarriers'].append(list(range(0,16)))


        agent_info['Channels'].append(list(range(len(subset))))

        return agent_info

    def solver(self, data):

        # d = demands = 4 (number of TA's will always have at least a minimum of 1 Gb/s) 0-3
        # c = canditate channels (for matricies based off max occupancy of TAs ie. 4) 0-58
        # s = subcarriers (16)
	
	# All model inputs must be in list map format
        Choices = list(map(str, data['Channels'][0]))
        Demands = list(map(str, data['ID']))
        Subcarriers = list(map(str, data['subcarriers'][0]))

        beta = makeDict([Demands, Choices], data['Beta'], 0)
        delta_dc = makeDict([Demands, Choices], data['delta_dc'], 0)

        delta_cs = makeDict([Subcarriers, Choices], data['delta_cs'][0], 0)

        mu_dc = makeDict([Demands, Choices], data['mu_dc'], 0)
        s_total = makeDict([Demands, Choices], data['s_total'], 0)
        
	# Create the problem
        problem = LpProblem("Subcarrier_reassignment", LpMinimize)

        mapping = [(d, c) for d in Demands for c in Choices]

	# Define the decision variable
        var = LpVariable.dicts("Allocation", (Demands, Choices), 0, 1, LpInteger)

	# Define the problem structure
	# First the objective function
        problem += (
            50*lpSum(mu_dc[d][c] * var[d][c] for (d, c) in mapping) + 10*lpSum(var[d][c] * s_total[d][c] for (d, c) in mapping) + lpSum(beta[d][c] * var[d][c] for (d, c) in mapping)
        )
	# Then the restrictions
        for d in Demands:
            problem += (
                lpSum([delta_dc[d][c] * var[d][c] for c in Choices]) == 1,
                "Constraint_1%s" % d,
            )

        for s in Subcarriers:
            problem += (
                lpSum([delta_dc[d][c] * delta_cs[s][c] * var[d][c] for (d, c) in mapping]) <= 1,
                "Constraint_2%s" % s,
            )

        problem.writeLP("ILP_Subcarrier_reassignment.lp")
        # Solve the ILP
        problem.solve()

        names = []
        val = []
        for x in problem.variables():
            names.append(x.name)
            val.append(x.varValue)

        return names, val
