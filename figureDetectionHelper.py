from Tree import *
import re
import string
import os
import subprocess
from itertools import groupby

PATH_TO_CORENLP = "../stanford-corenlp-full-2018-10-05/stanford-parser-full-2018-10-17/"

CORENLP_OUTPUT = "output.txt"

FINAL_OUTPUT = "output.txt"

#Minimum required length of a phrase in order to be
#considered in a parison
MIN_LENGTH_PARISON = 3

#Minimum number of words in order to be 
#considered in a epanaphora
MIN_LENGTH_EPANAPHORA = 1

#Minimum number of words in order to be 
#considered in a mesodiplosis
MIN_LENGTH_MESODIPLOSIS = 1


#Taken from Stack Overflow
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

###########################
#Affixes for Homoioptoton#
############################
lines = open('suffixes', 'r')
suffixes = []

for line in lines:
  suffixes.append(line.strip())

lines = open('prefixes', 'r')
prefixes = []

for line in lines:
  prefixes.append(line.strip())


###########################
#This function reads the output from Stanford CoreNLP's lexparser
###########################
def readFromParser():


  treeStrings = []

  with open(PATH_TO_CORENLP + 'output.txt', 'r') as output:

    treeString = ""
    isReadingTree = False
    isMultisentence = False
    endQuotesIsPrevious = False
    isFirstLeaf = False
    previousLine = ""

    for line in output:

      #Check if multi-sentence entry
      if isFirstLeaf and "(`` ``)" in line:
        isMultisentence = True
        line = line.replace("(`` ``)", "")

      #This is the start of the tree
      if "(ROOT" in line:
        isReadingTree = True
        isFirstLeaf = True
      elif " " in line.strip():
        isFirstLeaf = False

      #If string has lower letters or is blank
      if (line[0].islower() and line[0].isalpha()) or line.strip() == "":

        if previousLine != "":
          isMultisentence = False
          treeString = treeString + previousLine.replace(" ('' '')", "")
          previousLine = ""

        #Delete the last end bracket )
        #if isMultisentence:
        #  treeString = treeString.strip()[:-1]
    
        #We are no longer reading a tree
        if isReadingTree == True:
          isReadingTree = False

          #If the text we have isn't blank and is not multi-sentence, add it to the tree
          if treeString != "" and not isMultisentence:
            treeStrings.append(treeString) 
            #Reset the string
            treeString = ""

      else: #This quotation belongs to something in the passage        
        if "('' '')" in line:
          previousLine = line
      

      #If we're reading a tree, add the appropriate text
      if isReadingTree:
        #...But not the root of a multisentence tree
        if not ("(ROOT" in line and isMultisentence) and previousLine == "":
          treeString = treeString + line
  
  for treeString in treeStrings:
    print treeString
  
  return treeStrings


###########################
#This function converts the parse tree text to 
#a tree data structure
###########################
def readParseTree(parseTree):

  treeList = parseTree.split()
  tree = Tree()
  text = ""
  count = 0
  isFollowingStartQuotation = False

  for element in treeList:

    count = count + 1

    #If we see a (, we add a child
    if "(" in element:    

      nodeText = element[element.index("(")+1:len(element)]
      nodeText = applyEquivalences(nodeText)
      tempNode = Node(nodeText)

      if count == 1:
        tree.setRoot(tempNode)
      else:
        node.addChild(tempNode)
      node = tempNode


    #If we see a ), we pop up to the parent
    elif ")" in element:

      elementText = element[0:element.index(")")]

      node.setText(elementText)

      for i in range(0,element.count(")")): 
        if not node.isRoot():
          node = node.parent

  return tree

###########################
#Checks if there is a parison within a sentence
###########################
def hasParisonWithinSentence(tree):

  nodesWithPair = []

  #Compare each node with nodes of the same distance from leaf
  for distance in range(tree.getHeight() - 1, 0, -1):

    nodes = tree.root.getNodesWithDistance(distance)

    if len(nodes) > 1:
      for i in range(0, len(nodes)):
        node = nodes[i]

        for j in range(i+1, len(nodes)):

          otherNode = nodes[j]

          #print "Matching " + node.value + " with " + otherNode.value

          if node.isEqual(otherNode):

            isList = checkIfInList(node, tree) and checkIfInList(otherNode, tree)
            isComplete = checkIfComplete(node)
              
            if (isList and len(node.getLeaves()) >= MIN_LENGTH_PARISON) or isComplete:
              nodesWithPair.append(node)
              nodesWithPair.append(otherNode)
                
            if len(nodesWithPair) != 0:
              return True

  return False

###########################
#Checks two sentences for parison;
#note that their structures have to be exactly equal
###########################
def hasParisonBetweenSentences(firstTree, secondTree):

  if firstTree.isEqual(secondTree):
    return True

  else:
    #Sometimes the parse trees are wrong,
    #so let's try just the POS tags too
    if firstTree.root.getLeaves() == secondTree.root.getLeaves():
      #print firstTree.root.value
      return True

    return False

###########################
#Equivalences for POS tags
###########################
def applyEquivalences(node):

  if "VB" in node:
    return "VB"
  elif "NN" in node:
    return "NN"
  elif "RB" in node:
    return "RB"
  elif "JJ" in node:
    return "JJ"
  elif "WP" in node or "PRP" in node:
    return "PRP"
  elif "LS" in node or "SYM" in node or "," in node or ":" in node or "." in node:
    return "."
  else:
    return node

###########################
#Checks if a phrase contains a "list"; it essentially
#checks the last element of the list (e.g. "..., and X.")
###########################
def checkIfInList(node, tree):

  #Get the node before current node 
  allLeaves = tree.root.getLeaves()
  leaves = node.getLeaves()
  index = sublist(leaves, allLeaves)
  punctuation = {",", ".", "CC"}
  isAfterPunctuation = False
  isBeforePunctuation = False

  if index > 0:
    if allLeaves[index-1].value in punctuation:
      isAfterPunctuation = True
  elif index == 0: #It could be the first element of a list
    isAfterPunctuation = True
  
  index = index + len(leaves)
  #Get the node following the current node
  if index <= len(allLeaves) - 1:
    if allLeaves[index].value in punctuation:
      isBeforePunctuation = True

  return isAfterPunctuation and isBeforePunctuation

###########################
#Make a new tree based on the syntax tree,
#Delimited by punctuation.
###########################
def makeNewTree(oldTree):

  leaves = oldTree.root.getLeaves()
  tree = Tree()
  level0 = Node("LEVEL0")
  level1 = Node("LEVEL1")
  level2 = Node("LEVEL2")
  level3 = Node("LEVEL3")
  tree.setRoot(level0)
  level0.addChild(level1)
  level1.addChild(level2)
  level2.addChild(level3)

  for leaf in leaves:
    if leaf.value.isalpha(): #Not punctuation
      newLeaf = Node(leaf.value)
      newLeaf.setText(leaf.text)
      level3.addChild(newLeaf)

    else: 

      if leaf.value == "," or leaf.value == "-LRB-" or leaf.value == "-RRB-": #Go up one level
        level3 = Node(leaf.value)
        level3.setText(leaf.text)
        level2.addChild(level3)
        level3 = Node("LEVEL3")
        level2.addChild(level3)

      elif leaf.value == ":": #Go up two levels
        level2 = Node(leaf.value)
        level2.setText(leaf.text)
        level1.addChild(level2)
        level2 = Node("LEVEL2")
        level1.addChild(level2)
        level3 = Node("LEVEL3")
        level2.addChild(level3)

      elif leaf.value == ".":
        level1 = Node(leaf.value)
        level1.setText(leaf.text)
        level0.addChild(level1)
        level1 = Node("LEVEL1")
        level0.addChild(level1)
        level2 = Node("LEVEL2")
        level1.addChild(level2)
        level3 = Node("LEVEL3")
        level2.addChild(level3)

  return tree

  

###########################
#Checks if a list is part of another list. 
#Order matters!
###########################
def sublist(toFind, listToSearch):

  for i in range(0, len(listToSearch)):
    isMatch = True

    for j in range(0, len(toFind)):
      if listToSearch[i+j] != toFind[j]:
        isMatch = False
        break
      #If they're all the same, we've arrived here
      if isMatch == True:
        return i
      else:
        break

  #If we've arrived here, we didn't return and we've searched the whole list
  return -1

###########################
#Checks if a phrase is complete;
#We consider a phrase to be complete if 
#it has both an NP and a VP
###########################
def checkIfComplete(root):

   return (root.contains("NP") or root.contains("NN")) and (root.contains("VP") or root.contains("VB")) 

###########################
#Checks if there is an epanaphora within a sentence
###########################
def hasEpanaphora(tree):

  nodesWithPair = []

  #Compare each node with nodes of the same distance from leaf
  for distance in range(tree.getHeight() - 1, 0, -1):

    nodes = tree.root.getNodesWithDistance(distance)

    if len(nodes) > 1:
      for i in range(0, len(nodes)):
        node = nodes[i]

        for j in range(i+1, len(nodes)):

          otherNode = nodes[j]
          hasMatches = True

          leaves = node.getLeaves()
          otherLeaves = otherNode.getLeaves()
          leaf = leaves[0]
          otherLeaf = otherLeaves[0]
          k = 0
          l = 0
          punctuation = {",", ".", ":", "CC", "``", "''", "-LRB-", "-RRB-"}

          #Ignore conjunctions
          while (leaf.value in punctuation or otherLeaf.value in punctuation) and k < len(leaves) - 1 and k < len(otherLeaves) - 1:
            
            if leaf.value in punctuation:
              k = k + 1
              leaf = leaves[k]
            if otherLeaf.value in punctuation:
              l = l + 1
              otherLeaf = otherLeaves[l]

          for m in range(0, MIN_LENGTH_EPANAPHORA):
            leaf = leaves[k+m].text.lower().strip()
            otherLeaf = otherLeaves[l+m].text.lower().strip()
            print leaf + " : " + otherLeaf
            if leaf != otherLeaf or leaf == "" or otherLeaf == "":
              hasMatches = False

            #If we get here, this means MIN_LENGTH number of repetitions were found

            isComplete = checkIfComplete(node) and checkIfComplete(otherNode)
            isList = checkIfInList(node, tree) and checkIfInList(otherNode, tree)
            print hasMatches
            print isComplete
            print isList

            if hasMatches and (isComplete or isList):
              return True

  return False

###########################
#Checks if there is an mesodiplosis within a sentence
###########################
def hasMesodiplosis(tree):

  nodesWithPair = []

  #Compare each node with nodes of the same distance from leaf
  for distance in range(tree.getHeight() - 1, 0, -1):

    nodes = tree.root.getNodesWithDistance(distance)

    if len(nodes) > 1:
      for i in range(0, len(nodes)):
        node = nodes[i]

        for j in range(i+1, len(nodes)):

          otherNode = nodes[j]
          hasMatches = True

          leaves = node.getLeaves()
          otherLeaves = otherNode.getLeaves()
         
          #Remove the first and last elements from each
          del leaves[0]
          del leaves[len(leaves)-1]
          del otherLeaves[0]
          del otherLeaves[len(otherLeaves)-1]

          for k in range(0, len(leaves)):
            if leaves[k] in otherLeaves:
              m = otherLeaves.index(leaves[k])

          for m in range(0, MIN_LENGTH_MESODIPLOSIS):
            leaf = leaves[k+m].text.lower().strip()
            otherLeaf = otherLeaves[l+m].text.lower().strip()
            #print leaf + " : " + otherLeaf
            if leaf != otherLeaf or leaf == "" or otherLeaf == "":
              hasMatches = False

            #If we get here, this means MIN_LENGTH number of repetitions were found

            isComplete = checkIfComplete(node) and checkIfComplete(otherNode)
            isList = checkIfInList(node, tree) and checkIfInList(otherNode, tree)
            #print hasMatches
            #print isComplete
            #print isList

            if hasMatches and (isComplete or isList):
              return True

  return False

###########################
#Regex check for simple antithesis
###########################
def hasAntithesis(plaintext):

  spaces = "[\\b\\s]*"
  regex = "((.+)" + spaces + "not" + spaces + ".+" + spaces + "\2|(.+)" + spaces + ".+" + spaces + "not" + spaces + "\3)"
  match = re.search(regex, plaintext, flags=re.IGNORECASE)
  return len(match) != 0

###########################
#Simple check for homoioptoton
###########################
def hasHomoioptoton(plaintext, pos_tags):

  affixes_found = []
  new_pos_tags = []
  newPlaintext = []

  #Get rid of duplicates
  for i in range(0, len(plaintext)):
    word = plaintext[i]
    tag = pos_tags[i]
    if word not in newPlaintext:
      newPlaintext.append(word)
      new_pos_tags.append(tag)
  #print ' '.join(newPlaintext)


  #Get equivalences
  for tag in new_pos_tags:
    tag = applyEquivalences(tag)

  for i in range(0, len(newPlaintext)):

    word = newPlaintext[i]

    for suffix in suffixes:
      suffix = suffix.strip()
      if (word.endswith(suffix) or word.endswith(suffix + "s")) and suffix != "":
        #print word + " "
        #print suffix + "\n"
        affixes_found.append(new_pos_tags[i] + "_" + suffix)
        #print new_pos_tags[i] + "_" + suffix + "\n"

    for prefix in prefixes:
      prefix = prefix.strip()
      if word.find(prefix) == 0:
        #print word + " "
        #print prefix + "\n"
        affixes_found.append(prefix + "_" + new_pos_tags[i])
        #print new_pos_tags[i] + "_" + suffix + "\n"

    for affix in affixes_found:
      if affixes_found.count(affix) > 1:
        return True

  return False

  
