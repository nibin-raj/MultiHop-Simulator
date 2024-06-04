from multihop_simulator import *

link_list = [(0, 1), (0, 9), (1, 4), (1, 8), (5, 6), (7, 5), (9, 7), (9, 10), (10, 2), (10, 3)]
Network_Type = multisource #singlesource
interference_k_hop = 2


G_up = nx.DiGraph()
G_down = nx.DiGraph()
root = 0
for l in link_list:
    G_up.add_edge(l[1], l[0])
    G_down.add_edge(l[0], l[1])
            
# Create a dictionary to hold the upstream nodes of each node
commissioned_nodes = {}
for node in G_down.nodes():
    if node ==0: continue
    ancestors = nx.ancestors(G_down, node)
    ancestors_list = sorted(list(ancestors))
    ancestors_list = [x for x in ancestors_list if x != 0]
    commissioned_nodes[node] = ancestors_list
            
source_list = []
for node in G_up.nodes():
    if node ==0: continue
    source_list.append(node)
          
totalnum_nodes = len(link_list)+1
alpha_jk = [12]*totalnum_nodes
num_sources = len(source_list)

import logging
logging.basicConfig(filename = "experiment_logg.csv", level=logging.INFO,format = '%(message)s')
# logging.disable(logging.CRITICAL)
# logging.disable(logging.NOTSET)

print('Age-Difference')
agediffscheduler = AgeDifferenceScheduler()
simulator = NetworkSimulator(totalnum_nodes, link_list, source_list, commissioned_nodes, Network_Type, SCHEDULER_AGEDIFF,  agediffscheduler, K_HOP_INT, interference_k_hop)
simulator.simulate(100)

print('Age-Debt')
agedebtscheduler = AgeDebtScheduler(alpha_jk, flowcontrol_alpha = True, alphamax = 5*num_sources, V = 183)
agedebtsimulator = NetworkSimulator(totalnum_nodes, link_list, source_list, commissioned_nodes, Network_Type, SCHEDULER_AGEDEBT, agedebtscheduler, K_HOP_INT, interference_k_hop)
agedebtsimulator.simulate(100)


print('Randomized Policy')
randomscheduler = RandomScheduler(0.2, None)
randomsimulator = NetworkSimulator(totalnum_nodes, link_list, source_list, commissioned_nodes, Network_Type, SCHEDULER_RANDOM, randomscheduler, K_HOP_INT, interference_k_hop)
randomsimulator.simulate(100)
