import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd

from scipy.io import loadmat
from scipy import linalg as la

import logging
import itertools

from .constants import *
from .generalized_age_functions import *

class AgeDebtScheduler_Node:
    def __init__(self, totalnum_nodes):
        self.age = [0] * totalnum_nodes
        self.b_age = [g(0)] * totalnum_nodes
        self.age_n = [0] * totalnum_nodes
        self.b_age_n = [g(0)] * totalnum_nodes
        self.q = [0] * totalnum_nodes
        self.q_n = [0] * totalnum_nodes
        self.qijk =  [0]* totalnum_nodes
        self.qijk_n = [0] * totalnum_nodes
        self.updateflag = [False] * totalnum_nodes
        
class AgeDebtScheduler:
    def __init__(self, alpha_jk, flowcontrol_alpha = False, alphamax = 50, V = 50):
        self.network  = None
        self.alpha_jk = alpha_jk
        self.alphamax = alphamax
        self.V = V
        self.flowcontrol_alpha = flowcontrol_alpha
        
    # the age-debt scheduler has to maintain some data for every node in order to schedule
    def setup_nodedata(self):
        self.nodedata = []
        self.agedata = []
        for i in range(self.network.totalnum_nodes):
            self.agedata.append([])
        for n in self.network.G_up.nodes:
            d = AgeDebtScheduler_Node(self.network.totalnum_nodes)
            self.nodedata.append(d)
    
    def hop_distance_to_dest(self, i):
        return i
    
    def update_slot_alpha(self):
        for k in self.network.source_list:
            if self.nodedata[0].q[k] > self.V:
                self.alpha_jk[k] = self.alphamax
            else:
                self.alpha_jk[k] = 1
        
    def update_slot_virtual(self, activation_vector):
        ttn = self.network.totalnum_nodes
        # sht = self.network.get_link_s_ht(activation_vector)
        sht = activation_vector # changed - activation vector is now sht itself
        
        for n in self.network.G_up.nodes:
            self.nodedata[n].age_n = [0] * ttn
            for k in self.network.source_list:
                if n == k:
                    self.nodedata[n].age_n[k] = 0
                else:
                    self.nodedata[n].age_n[k] = self.nodedata[n].age[k] + 1

        for (s, j, i) in sht: # if there is a transmission, update rule is different
            if not j == s:
                self.nodedata[j].age_n[s] = np.min([self.nodedata[j].age[s], self.nodedata[i].age[s]]) + 1

        for k in self.network.source_list: # q update for the 0th node (or the destination)
            bk = g(self.nodedata[0].age_n[k])
            self.nodedata[0].q_n[k] = np.max([self.nodedata[0].q[k] + bk - self.alpha_jk[k],0])
            
        for n in self.network.G_up.nodes: # intermediate nodes
            if n == 0: 
                continue
            for k in self.network.source_list:
                bk = g(self.nodedata[0].age_n[k])
                self.nodedata[n].qijk_n[k] = np.max([self.nodedata[n].qijk[k] + bk - self.alpha_jk[k],0])

        for (s, j, i) in sht: # if there is a transmission for kth source, update rule is different, i is the intermediate node
            if not j == s:
                t = np.min([self.nodedata[i].age[s], self.nodedata[0].age[s]]) + self.hop_distance_to_dest(i)
                self.nodedata[i].qijk_n[s] = np.max([self.nodedata[i].qijk[s] + g(t) - self.alpha_jk[s],0])

    def update_slot_actual(self, activation_vector):
        # sht = self.network.get_link_s_ht(activation_vector)
        sht = activation_vector
        for n in self.network.G_up.nodes:
            for k in self.network.source_list:
                self.nodedata[n].updateflag[k] = 0

        for n in self.network.G_up.nodes:
            self.nodedata[n].age[n] = 0
            self.nodedata[n].updateflag[n] = 1
                    
        for (s, j, i) in sht: # if there is a transmission, update rule is different
            if self.nodedata[j].updateflag[s] == 0:
                self.nodedata[j].age[s] = np.min([self.nodedata[j].age[s], self.nodedata[i].age[s]]) + 1
                self.nodedata[j].updateflag[s] = 1

        for n in self.network.G_up.nodes:
            for k in self.network.source_list:
                if self.nodedata[n].updateflag[k] == 0:
                    self.nodedata[n].age[k] = self.nodedata[n].age[k] + 1

        for k in self.network.source_list: # q update for the 0th node (or the destination)
            bk = g(self.nodedata[0].age[k])
            self.nodedata[0].q[k] = np.max([self.nodedata[0].q[k] + bk - self.alpha_jk[k],0])
            
        for n in self.network.G_up.nodes:
            for k in self.network.source_list:
                self.nodedata[n].updateflag[k] = 0

        for (s, j, i) in sht: # if there is a transmission, update rule is different, i is the intermediate node, j - not used
            if not i == s:
                t = np.min([self.nodedata[i].age[s], self.nodedata[0].age[s]]) + self.hop_distance_to_dest(i)
                self.nodedata[i].qijk[s] = np.max([self.nodedata[i].qijk[s] + g(t) - self.alpha_jk[s], 0])
                self.nodedata[i].updateflag[s] = 1
        
        for k in self.network.source_list:
            for n in self.network.commissioned_nodes[k]:
                if self.nodedata[n].updateflag[k] == 0:
                    bk = g(self.nodedata[0].age[k])
                    self.nodedata[n].qijk[k] = np.max([self.nodedata[n].qijk[k] + bk - self.alpha_jk[k],0])
                    
        for k in self.network.source_list:
            d1 = self.nodedata[ROOTNODE_ID].age[k]
            self.agedata[k].append(d1)
#             d2 = self.nodedata[1].age[k]
#             self.agedata_1[k].append(d2)
        
    def lyapunov_t(self):
        l = 0
        for k in self.network.source_list:
            l += self.nodedata[0].q[k] ** 2
            for n in self.network.G_up.nodes:
                if n in self.network.commissioned_nodes[k]:
                    l += self.nodedata[n].qijk[k] ** 2
        return l

    def lyapunov_tplus1(self):
        l = 0
        for k in self.network.source_list:
            l += self.nodedata[0].q_n[k] ** 2
            for n in self.network.G_up.nodes:
                if n in self.network.commissioned_nodes[k]:
                    l += self.nodedata[n].qijk_n[k] ** 2
        return l
    
    def get_packet_generated_slot(self, activation_vector): # note that this is called from within the get_activation_vector_slot()
        sources_packet_generated = []
        # sht = self.network.get_link_s_ht(activation_vector)
        sht = activation_vector

        for (s,h,t) in sht:
            if s == t:
                sources_packet_generated.append(t)
        return sources_packet_generated
        
    def get_activation_vector_slot(self):
        min_lyapunov_drift = np.Inf
        min_index = -1
        lt = self.lyapunov_t()
        
        logging.info("AgeDebt:Lt % f" % (lt))
        # self.pp_age_vq()
        
        feasible_indices = []
        drifts = []
        lengthofa = []
        if self.flowcontrol_alpha:
            self.update_slot_alpha()

        for ai, a in enumerate(self.network.A):
            if not self.network.isfeasible(a):
                continue
            self.update_slot_virtual(a)
            ltplus1 = self.lyapunov_tplus1()
            logging.info("AgeDebt:Activation vector %s:Lt+1 %f" % (a, ltplus1))
            # self.pp_age_vq()
            drifts.append(ltplus1 - lt)
            lengthofa.append(len(a))
            feasible_indices.append(ai)
            
        min_drift = np.min(drifts)
        lengthofa = np.array(lengthofa)
        min_indices = list(np.array(feasible_indices)[np.where(drifts == min_drift)[0]])
#         min_indices = list(np.array(feasible_indices)[np.where((drifts == min_drift) * (lengthofa == np.max(lengthofa)))[0]])
#         print('min_indices',min_indices,'min_drift',min_drift, drifts)
        min_index = np.random.choice(min_indices)
        
        best_activation_vector = self.network.A[min_index]
#         print('Act', best_activation_vector)
        sources_packet_generated = self.get_packet_generated_slot(best_activation_vector)
        self.update_slot_actual(best_activation_vector) # this is for updating the scheduler's node data 
        return min_index, sources_packet_generated # this will be used for actual scheduling within the simulator
    
    def pp_age(self):
        for n in self.network.source_list:
            t = [self.nodedata[n].age[k] for k in self.network.source_list]
            logging.info("AgeDebt:Age@%u - %s" % (n, t))

    def pp_age_vq(self):
        t1 = [self.nodedata[0].age[k] for k in self.network.source_list]
        t4 = [self.nodedata[0].age_n[k] for k in self.network.source_list]
        t2 = [self.nodedata[0].q[k] for k in self.network.source_list]
        t3 = [self.nodedata[0].q_n[k] for k in self.network.source_list]
        logging.info("AgeDebt:Age   @0 - %s" % (t1))
        logging.info("AgeDebt:Age_n @0 - %s" % (t4))
        logging.info("AgeDebt:Q     @0 - %s" % (t2))
        logging.info("AgeDebt:Q_n   @0 - %s" % (t3))
        
        for n in self.network.G_up.nodes:
            if n == 0:
                continue
            t1 = [self.nodedata[n].age[k] for k in self.network.source_list]
            t4 = [self.nodedata[n].age_n[k] for k in self.network.source_list]
            t2 = [self.nodedata[n].qijk[k] for k in self.network.source_list]
            t3 = [self.nodedata[n].qijk_n[k] for k in self.network.source_list]
            logging.info("AgeDebt:Age    @%u - %s" % (n, t1))
            logging.info("AgeDebt:Age_n  @%u - %s" % (n, t4))
            logging.info("AgeDebt:Qijk   @%u - %s" % (n, t2))
            logging.info("AgeDebt:Qijk_n @%u - %s" % (n, t3))

    def pp_age_0(self):
        t = [self.nodedata[0].age[k] for k in self.network.source_list]
        logging.info("AgeDebt:Age@0 - %s" % (t))

