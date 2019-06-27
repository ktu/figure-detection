To run, use the command `python figureDetection.py'.

The command reads input from input.txt. Separate different entries with a newline. Multiple-sentence entries should be surrounded in quotation marks (""). 

You can pipe the intermediary syntax trees from the parser into a file, e.g. `python figureDetection.py > trees'. 

Edit PATH_TO_CORENLP in figureDetectionHelper.py to the path of your CoreNLP lexparser.sh. Note that my personal version uses the lexparser from parser-full-2018-10-17 with the following settings: 

java -mx600m -cp "$scriptdir/*:" edu.stanford.nlp.parser.lexparser.LexicalizedParser \
 -outputFormat "penn,typedDependencies" edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz $*

The command will run lexparser.sh and overwrite the output.txt in the same directory. If you do not want to overwrite output.txt or wish to call it something else, edit CORENLP_OUTPUT in figureDetectionHelper.py.

The command will write to output.txt in the same directory as figureDetection.py. If you wish to call it something else, edit FINAL_OUPUT in figureDetectinHelper.py. 

---------

Versions and notes

0.1 (27/06/2019) Note that some of the false negatives in my thesis are fixed in this current version because of the switch to englishPCFC.ser.gz. 

The homoioptoton detector also outputs a false negative for one of the examples ("In activity commendable, in a commonwealth profitable, and in war terrible") because of the mislabelling of "commendable" as a noun. 

