# sentence-schema-expander
A phython script to generate sentences and sentence annotations from a sentence schema. Used to generate the data in Chowdhury Zamparelli 2018, 2019.

Usage: rev-multiplier-align.py [-h] [-f FILTER] [-o OUTPUT] input

This command-line python3 script takes a file (-f <file>) containing one string per line.
The strings can contain options, given in (space-framed) square brackets
 (e.g. A [ B1 B2 ] [ C1 C2 ]). The script generates all possible permutations
(e.g. A B1 C1, A B1 C2, A B2 C1, A B2 C2) and appends them to a
(typically, .csv) file given with -o <output-file>. The output file should be
initialized with a single line containing a list of "|"-separated columns,
the first 3 empty or '|ID|Sentence|Group|'.
The remaining columns contain words whose position the
program should track. Example: a first line such as 
ID|BLOCK|NUM|SENTENCE|ORIG#|dog|cat|@@@@| will write in the 6th, 7th and 8th column of output the sentencial position
of the first occurrence of the strings 'dog', 'cat' and '@@@@' (elements of the form
'@@[0-9]*@@' are automatically deleted 
from the input, and can be used to mark 'empty' positions). The position of
will be written under the corresponding |-marked columns. The elements in the input file should not contain "|".

The optional parameter -f <filter string> takes a string of words
and removes from the output all the lines containing ALL those words.
If -o <outfile> is missing the output is to stout.
If a line begins with '<block' (e.g. <block ID='test'>, the optional ID
is placed in the second output column; if missing, 'default-block' is
inserted) the programs enters 'block mode'
All the expanded lines before </block> are taken to be
minimal pairs, one per line, and are ordered so that minimal pairs
remain adjacent and are marked by the same number in the 3rd column. The program will complain if the word length of the minimal pairs is different (this can be avoided by padding the [...] with @@@@ elements, which are going to be expunged. But mismatched often hide conceptual errors).

For instance, if we want to compare 'Who' and 'What' in the schema
<block>
  
Who [walked walks will_walk]

What [walked walks will_walk]

</block>

The program will generate:

1|default-block|0|Who walked|1|

2|default-block|0|What walked|2|

3|default-block|1|Who walks|1|

4|default-block|1|What walks|2|

5|default-block|2|Who will walk|1|

6|default-block|2|What will walk|2|



Where 'default-block' is added when <block> has no ID, and the last
number is the number of the original.

WARNING: minimal pairs in a block should never have [...] whose order
is inverted across lines. This will break the adjacent ordering of minimal pairs. Using the flag invert-odd inside the block can sometimes (but not always) fix that. Example:

<block ID="crossed block">

[ cats dogs ] resemble [ armadillos whales ]

[ armadillos ] resemble [ cats dogs ]

</block>

Probably undesirable output:

|default-block|0|cats resemble armadillos|1||||

|default-block|0|armadillos resemble cats|2||||

|default-block|1|cats resemble whales|1||||

|default-block|1|armadillos resemble dogs|2||||

|default-block|2|dogs resemble armadillos|1||||

|default-block|2|whales resemble cats|2||||

|default-block|3|dogs resemble whales|1||||

|default-block|3|whales resemble dogs|2||||


Alternative: using invert-odd: 

<block ID="crossed block" invert-odd>

[ cats dogs ] resemble [ armadillos whales ]

[ armadillos ] resemble [ cats dogs ]

</block>

Output:

|default-block|0|cats resemble armadillos|1||||

|default-block|0|armadillos resemble cats|2||||

|default-block|1|cats resemble whales|1||||

|default-block|1|whales resemble cats|2||||

|default-block|2|dogs resemble armadillos|1||||

|default-block|2|armadillos resemble dogs|2||||

|default-block|3|dogs resemble whales|1||||

|default-block|3|whales resemble dogs|2||||



Positional arguments:
  input                 Input file with strings to transform.

optional arguments:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
                        Remove output lines if they contain all the markers in this list
  -o OUTPUT, --output OUTPUT
                        Output file to read features to mark and write transformed strings (append).Its first line contain the sentencial features to record.
                      
Examples of use:

See the pattern file rel-island-align.txt and the output rel-island-align-expanded.csv, used for an experiment on syntactic island detection.


