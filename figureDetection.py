from figureDetectionHelper import *
import os
import subprocess

f1 = open(FINAL_OUTPUT, 'w');
threeFigures = ""
twoFiguresPE = ""
twoFiguresPH = ""
twoFiguresEH = ""
oneFigureP = ""
oneFigureE = ""
oneFigureH = ""
noFigures = ""

#with cd(PATH_TO_CORENLP):
#  subprocess.call("./lexparser.sh input.txt > output.txt", shell=True)

subprocess.call("./" + PATH_TO_CORENLP + "lexparser.sh input.txt > " + PATH_TO_CORENLP + CORENLP_OUTPUT, shell=True)

treeStrings = readFromParser()

for i in range(0, len(treeStrings)):

  treeString = treeStrings[i]
  print treeString

  tree = readParseTree(treeString)

  text = []
  tags = []
  for leaf in tree.root.getLeaves():
    text.append(leaf.text)
    tags.append(leaf.value)

  newTree = makeNewTree(tree)

  isParison = hasParisonWithinSentence(tree) or hasParisonWithinSentence(newTree)
  isEpanaphora = hasEpanaphora(tree) or hasEpanaphora(newTree)
  isHomoioptoton = hasHomoioptoton(text, tags)

  textAsString = ""
  for word in text:
    textAsString = textAsString + " " + word
  textAsString = textAsString + "\n"

  #f1.write(textAsString)

  if isParison and isEpanaphora and isHomoioptoton:
    threeFigures = threeFigures + textAsString
  elif isParison and isEpanaphora:
    twoFiguresPE = twoFiguresPE + textAsString
  elif isParison and isHomoioptoton:
    twoFiguresPH = twoFiguresPH + textAsString
  elif isEpanaphora and isHomoioptoton:
    twoFiguresEH = twoFiguresEH + textAsString
  elif isParison:
    oneFigureP = oneFigureP + textAsString
  elif isEpanaphora:
    oneFigureE = oneFigureE + textAsString
  elif isHomoioptoton:
    oneFigureH = oneFigureH + textAsString
  else:
    noFigures = noFigures + textAsString


  #else:

  #  if i + 1 < len(treeStrings):
  #    [nextTree, nextText] = readParseTree(treeStrings[i+1])

  #    if hasParisonBetweenSentences(tree, nextTree):
  #      f1.write(text + " ")
  #      j = i + 1

  #      while hasParisonBetweenSentences(tree, nextTree) and j + 1 < len(treeStrings):
  #        f1.write(nextText + " ")
  #        j = j + 1
  #        [nextTree, nextText] = readParseTree(treeStrings[j])

  #      f1.write("\n")
  #      i = j + 1

f1.write("========== PARISON, EPANAPHORA, AND HOMOIOPTOTON ==========\n")
f1.write(threeFigures)
f1.write("\n================== PARISON AND EPANAPHORA =================\n")
f1.write(twoFiguresPE)
f1.write("\n================= PARISON AND HOMOIOPTOTON ================\n")
f1.write(twoFiguresPH)
f1.write("\n=============== EPANAPHORA AND HOMOIOPTOTON ===============\n")
f1.write(twoFiguresEH)
f1.write("\n====================== PARISON ONLY =======================\n")
f1.write(oneFigureP)
f1.write("\n==================== EPANAPHORA ONLY ======================\n")
f1.write(oneFigureE)
f1.write("\n=================== HOMOIOPTOTON ONLY =====================\n")
f1.write(oneFigureH)
f1.write("\n======== NO PARISON, EPANAPHORA, OR HOMOIOPTOTON ==========\n")
f1.write(noFigures)
