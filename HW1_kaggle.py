import operator
import pandas as pd

# all sets from dataset
def dataset():
  # mypath = my input data path
  dataset = pd.read_csv(mypath).drop(columns=['Date', 'Time'],axis = 1)
  dataset = dataset.mask(dataset.eq('NONE')).dropna()
  sector = dataset.groupby('Transaction')
  df2 = pd.DataFrame(columns=['Transaction','ItemList'])
  indexs = list(dataset['Transaction'].unique())
  for i in indexs:
      df2.loc[i] = [i, list(sector.get_group(i)['Item'])]
  mylist = []
  for index, row in df2.iterrows():
      mylist.append(row['ItemList'])
  DataSet = mylist
  return DataSet

# find unique sets
def InitDataSet(dataSet):
    InitDataSet = {}
    for i in dataSet:
        InitDataSet[frozenset(i)] = 1
    #print (InitDataSet)
    return InitDataSet

# define tree 
class Tree:
    def __init__(self, nodeName, nodeNum, nodeParent):
        self.name = nodeName
        self.count = nodeNum
        self.parent = nodeParent
        self.children = {} 
        self.nodeLink = None # link to same item

    def renewNode(self, nodeNum):
        self.count += nodeNum

# create tree
def createTree(dataSet, minSup):
    dic = {}                              # each items' occur time 
    for trans in dataSet:
        for i in trans:
            dic[i] = dic.get(i, 0) + dataSet[trans]
    for k in list(dic.keys()):            # delete occur time < minSup
        if dic[k] < minSup:
            del(dic[k]);
    #print (dic)
    freqItemSet = set(dic.keys())
    if len(freqItemSet) == 0:
        return None, None
    for i in dic:                         # link to the same item 
        dic[i] = [dic[i], None]
    root = Tree('Root', 1, None)
    for trans, count in dataSet.items():
        transaction = {} 
        for item in trans:
            if item in freqItemSet:
                transaction[item] = dic[item][0] # dic[item][1] is the link to the same item
        if len(transaction) > 0:                 # sort all itemset
            orderedSet = [v[0] for v in sorted(transaction.items(), key=lambda kv: kv[1],reverse= True)] 
            updateTree(orderedSet, root, dic, count) # update fp tree
    return root, dic
		
# update tree
def updateTree(item, root, dic, count):
    if item[0] in root.children:     # the item is in the tree so plus 1 to count
      root.children[item[0]].count += 1
    else:       # the item is not in the tree so add a new path and its parent is root and the value is count
      root.children[item[0]] = Tree(item[0], count, root)
      if dic[item[0]][1] == None:
            dic[item[0]][1] = root.children[item[0]]
      else:
        while (dic[item[0]][1].nodeLink != None):
          dic[item[0]][1] = dic[item[0]][1].nodeLink
        dic[item[0]][1].nodeLink = root.children[item[0]] 
    if len(item) > 1:
      updateTree(item[1::], root.children[item[0]], dic, count)

def path(leafNode, prepath):
    if leafNode.parent != None:
        prepath.append(leafNode.name)
        path(leafNode.parent, prepath)

def prefix(nodepath, link):
  condpath = {}
  while link != None:
        prefixPath = []     
        path(link, prefixPath)
        if len(prefixPath) > 1:
            condpath[frozenset(prefixPath[1:])] = link.count
        link = link.nodeLink
  return condpath

def subTree(dic,minSup,preFix,freqItemList):
    d = {}
    for i in dic.keys():
      d[i] = dic[i][0]
    reDic = [v[0] for v in sorted(d.items(),key = lambda p:p[1])]
    for item in reDic:
        fSet = preFix.copy()
        fSet.add(item)
        freqItemList.append(fSet)
        condpath = prefix(item, dic[item][1])
        subroot,subdic = createTree(condpath, minSup)
        if subdic != None:
          subTree(subdic, minSup, fSet, freqItemList)
                         
# main
data = dataset()
minsupport= 2
initdata = InitDataSet(data)
root, dictionary = createTree(initdata,minsupport)
freqItems = []
subTree(dictionary,minsupport,set([]),freqItems)

# my path = my output data path
with open(mypath, 'w') as f:
    for item in freqItems:
        f.write("%s\n" % item)
