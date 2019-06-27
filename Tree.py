class Node:
  def __init__(self, value):
    self.value = value
    self.text = ""
    self.parent = None
    self.children = []
    
  def addChild(self, child):
    self.children.append(child)
    child.parent = self

  def setText(self, text):
    self.text = text    

  def isLeaf(self):
    if len(self.children) == 0:
      return True
    else:
      return False

  def isRoot(self):
    if self.parent == None:
      return True
    else:
      return False

  def getHeight(self):
    if self.parent == None:
      return 1
    else:
      return 1 + self.parent.getHeight()

  def getDescendants(self):
    descendants = []
    for i in range(0, self.getHeight()):
      descendants_sublist = self.getNodesAtHeight(i)
      for descendant in descendants_sublist:
        descendents.append(descendent)
    return descendants

  def getNodesAtHeight(self, index):
    nodes = []
    self._getNodesAtHeight(index, nodes)
    return nodes

  def _getNodesAtHeight(self, index, nodes):
    if self is not None:
      if self.getHeight() == index:
        return nodes.append(self)
      else:
        for child in self.children:
          child._getNodesAtHeight(index, nodes)

  def getDistanceFromLeaf(self):
    if self.isLeaf():
      return 0
    else:
      maxDistance = 0
      for child in self.children:
        tempDistance = 1 + child.getDistanceFromLeaf()
        if tempDistance > maxDistance:
          maxDistance = tempDistance
      return maxDistance 

  def getLeaves(self):
    leaves = []
    self._getLeaves(self, leaves)
    return leaves

  def _getLeaves(self, node, leaves):
    if node is not None: 
      if node.isLeaf():
        return leaves.append(node)
      else:
        for child in node.children:
          self._getLeaves(child, leaves)

  def getNodesWithDistance(self, distance):
    nodes = []
    self._getNodesWithDistance(distance, nodes)
    return nodes

  def _getNodesWithDistance(self, distance, nodes):
    if self is not None:
      #print str(self.getDistanceFromLeaf())
      #print str(distance)
      if self.getDistanceFromLeaf() == distance:
        #print self.value
        return nodes.append(self)
      else:
        for child in self.children:
          child._getNodesWithDistance(distance, nodes)

  def contains(self, string):
    if self is None:
      return False
    else:
      if string in self.value:
        return True
      flag = False
      for child in self.children:
        flag = flag or child.contains(string)
      return flag

  def isEqual(self, node):

    if self.isLeaf() and node.isLeaf() and self.value == node.value:
      return True
    if self.isLeaf() or node.isLeaf() or self.value != node.value:
      return False

    if len(self.children) != len(node.children):
      return False

    isEqual = self.value == node.value
    for i in range(0, len(self.children)):
        isEqual = isEqual and self.children[i].isEqual(node.children[i])
    return isEqual

class Tree:
  def __init__(self):
    self.root = None

  def setRoot(self, root):
    self.root = root

  def getHeight(self):
    leafNodes = self.root.getLeaves()
    maxHeight = 0
    for node in leafNodes:
      if node.getHeight() > maxHeight:
        maxHeight = node.getHeight()
    return maxHeight

  def isEqual(self, tree):
    return self.root.isEqual(tree.root) 
        
    
    


