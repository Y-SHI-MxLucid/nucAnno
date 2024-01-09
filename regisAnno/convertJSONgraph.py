# %%
from networkx.readwrite import json_graph
import networkx as nx
import json as js
# %%
def trimAttr(dictionary):
    for key in list(dictionary.keys()):
        if key not in ['name', 'acronym']:
            del dictionary[key]

def getSucNodes(diGraph, rtNodeName, baseNodes, applyName=None):
    subnodes = []
    nodeId = 0
    for id, label in enumerate(diGraph.nodes()):
        if diGraph.nodes.data()[label]['acronym'] == rtNodeName:
            scsr = diGraph.successors(n = label)
            nodeId = label
    if rtNodeName in baseNodes:
        subnodes.append([nodeId, rtNodeName])
        applyName = rtNodeName
    elif applyName:
        subnodes.append([nodeId, applyName])

    for id, label in enumerate(scsr):
        branchNodes = getSucNodes(diGraph, diGraph.nodes.data()[label]['acronym'], 
                                  baseNodes, applyName)
        subnodes = subnodes + branchNodes
    return subnodes

def convertJSONgraph(input, output):

    with open(input, 'r') as jf:
        anno = js.load(jf)
    with open('default_base_nodes.json', 'r') as jf:
        default_baseNodes = js.load(jf)
    anno_g = json_graph.tree_graph(anno)

    for id, label in enumerate(anno_g.nodes()):
        trimAttr(anno_g.nodes.data()[label])

    subNodeList = getSucNodes(anno_g, 'CTXpl', default_baseNodes)
    subNodeDict = {}
    for i in subNodeList:
        subNodeDict[i[0]] = i[1]

    with open(output, 'w') as jf:
        js.dump({'brain_atlas_dict': subNodeDict, 'base_node_list': default_baseNodes}, jf)