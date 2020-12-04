#!/usr/bin/env python
# coding: utf-8

# Stock Analysis

# Dependency

from py2neo import *
import numpy as np
import pandas as pd
import sys

# Connect Graph

graph = Graph("bolt://localhost:7685")

# Get Paths

def find_paths(target):
    result = graph.run("MATCH (a:Name{Name:'" + target + "'})-[:Is_name_of]->(b:NodeID) MATCH p = (:NodeID)-[:Invest*1..]->(b:NodeID) RETURN p")
    paths = result.data()
    tree = list()
    for path in paths:
        tree = tree + (list(path['p'].relationships))
    tree = sorted(set(tree), key = tree.index)
    return tree


# Awesome Method (Current)

def printList(parentId, tree, spaceStr = '               '):
    for x in tree:
        gen = walk(x)
        start = gen.__next__()
        invest = gen.__next__()
        end = gen.__next__()
        if end == parentId:
            name = graph.run("MATCH (a:Name)-[:Is_name_of]->(b:NodeID) WHERE ID(b) =" + str(start.identity) + " RETURN a").data()
            print(spaceStr+'├─ ', "ratio:", invest['ratio'], name[0]['a']["Name"], sep =' ')
            printList(start, tree, spaceStr + '│              ')

def stock_tree(paths):
    _ = walk(paths[0])
    _.__next__()
    _.__next__()
    parent = _.__next__()
    print('└─ '+'\033[1m'+target+'\033[0m')   
    printList(parent, paths)

# Main

if (len(sys.argv) > 2):
    print("WRONG PROGRAM ARGUEMENTS")
target = sys.argv[1]
paths = find_paths(target)
if paths == []:
    print("数据库中没有您想查找的公司信息，请更改要查找的公司名称！")
else:
    stock_tree(paths)

# N-ary Tree (Optional)

class n_node(object):
    def __init__(self,value = None):
        self.value = value
        self.child_list = []
        self.attributes = None
        
    def add_child(self, node):
        self.child_list.append(node)
        
    def set_attributes(self, attributes):
        self.attributes = attributes


def initialize(paths):
    nnodes_list = list()
    for path in paths:
        first = path['p'].end_node
        nfirst = [n for n in nnodes_list if n.value == first]
        if not nfirst:
            nfirst = n_node(first)
            nnodes_list.append(nfirst)
        else:
            nfirst = nfirst[0]
        
        last = nfirst
        current = nfirst
        
        for node, relationship in zip(path['p'].nodes[::-1][1:], path['p'].relationships[::-1]):
            nnode = [n for n in nnodes_list if n.value == node]
            if not nnode:
                nnode = n_node(node)
                nnodes_list.append(nnode)
            else:
                nnode = nnode[0]
            current = nnode
            
            if current not in last.child_list:
                last.add_child(current)
                current.set_attributes(dict(relationship))
            
            last = nnode
    return nnodes_list[0]

# head = initialize(paths)

