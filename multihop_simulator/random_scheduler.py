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

class RandomScheduler_Node:
    def __init__(self, totalnum_nodes):
        self.age = [0] * totalnum_nodes
        self.updateflag = [False] * totalnum_nodes
        
class RandomScheduler:
    def __init__(self, prb, activation_vector_distribution):
        self.prb = prb
        self.activation_vector_distribution = activation_vector_distribution
        self.network = None
        
    def setup_nodedata(self):
        self.agedata = []
        for i in range(self.network.totalnum_nodes):
            self.agedata.append([])
        self.nodedata = [] 
        for n in self.network.G_up.nodes:
            d = RandomScheduler_Node(self.network.totalnum_nodes)
            self.nodedata.append(d)
        
    def get_packet_generated_slot(self, activation_vector): 
        sources_packet_generated = []
        sht = activation_vector
        for (s,h,t) in sht:
            if s == t:
                sources_packet_generated.append(t)
        return sources_packet_generated
    
    def get_activation_vector_slot(self):
        t = len(self.network.A)
        aindex = np.random.choice(t, p = self.activation_vector_distribution)
        best_activation_vector = self.network.A[aindex]
        sources_packet_generated = self.get_packet_generated_slot(best_activation_vector)
        self.age_function_update(best_activation_vector)
        return aindex, sources_packet_generated
    
    def age_function_update(self, activation_vector):
        sht = activation_vector
        for n in self.network.G_up.nodes:
            for k in self.network.source_list:
                self.nodedata[n].updateflag[k] = 0
                
        for n in self.network.G_up.nodes:
            self.nodedata[n].age[n] = 0
            self.nodedata[n].updateflag[n] = 1
            
        for (s, j, i) in sht: # if there is a transmission, age update 
            if self.nodedata[j].updateflag[s] == 0:
                self.nodedata[j].age[s] = np.min([self.nodedata[j].age[s], self.nodedata[i].age[s]]) + 1
                self.nodedata[j].updateflag[s] = 1
                
        for n in self.network.G_up.nodes:
            for k in self.network.source_list:
                if self.nodedata[n].updateflag[k] == 0:
                    self.nodedata[n].age[k] = self.nodedata[n].age[k] + 1
                    
        for k in self.network.source_list:
            d1 = self.nodedata[ROOTNODE_ID].age[k]
            self.agedata[k].append(d1)