#!/usr/bin/python3
# Program to generate variants of a sentence schema: A [ B1 B2 ] [ C1 C2 ] becomes A B1 C1, A B1 C2, A B2 C1, A B2 C2
import argparse
import sys
import os.path
import re
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description="Takes a file (-f <file>) containing one string per line.\n" +
                                 "Strings should contain options in (space framed) square brackets\n " +
                                 "(e.g. A [ B1 B2 ] [ C1 C2 ]). Generates all possible permutations\n" +
                                 "(e.g. A B1 C1, A B1 C2, A B2 C1, A B2 C2) and appends them to a\n"
                                 "(typically, .csv) file given with -o <file>. The output file should be\n" +
                                 "initialized with a single line containing a list of |-separated columns,\n" +
                                 "the first 3 empty or '|ID|Sentence|Group|'.\n" +
                                 "The remaining columns contain words whose position the\n"
                                 + "program should track. Example: a first line such as \n" +
                                 "ID|BLOCK|NUM|SENTENCE|ORIG#|dog|cat|@@@@| will write the (first) position\n"+
                                 "of the symbol stings 'dog', 'cat' and '@@@@' (elements of the form\n"+
                                 "'@@[0-9]*@@' are automatically deleted \n" +
                                 "from the input, and can be used to mark 'empty' positions). The position of\n" +
                                 "will be written under the corresponding |-marked columns. The elements\n" +
                                 "these items in the input file should not contain |.\n\n"+
                                 "The optional parameter -f <filter string> takes a string of words\n" +
                                 "and removes from the output all the lines containing ALL those words.\n" +
                                 "If -o <outfile> is missing the output is to stout.\n"+
                                 "If a line begins with '<block' (e.g. <block ID='test'>, the optional ID\n"+
                                 "is placed in the second output column; if missing, 'default-block' is\n"+
                                 "inserted) the programs enters 'block mode'\n"
                                 "All the expanded lines before </block> are taken to be\n"+
                                 "minimal pairs, one per line, and are ordered so that minimal pairs\n"+
                                 "remain adjacent and are marked by the same number in the 3rd column.\n\n"+
                                 "For instance, if we want to compare 'Who' and 'What' in the schema\n"+
                                 "<block>\n"+
                                 "Who [walked walks will_walk]\n"+
                                 "What [walked walks will_walk]\n"+
                                 "</block>\n\n"+
                                 "The program will generate:\n\n"+
                                 "1|default-block|0|Who walked|1|\n"+
                                 "2|default-block|0|What walked|2|\n"+
                                 "3|default-block|1|Who walks|1|\n"+
                                 "4|default-block|1|What walks|2|\n"+
                                 "5|default-block|2|Who will walk|1|\n"+
                                 "6|default-block|2|What will walk|2|\n\n"+
                                 "Where 'default-block' is added when <block> has no ID, and the last\n"+
                                 "number is the number of the original.\n\n"+
                                 "WARNING: minimal pairs in a block should never have [...] whose order\n"+
                                 "is inverted across lines. This will break the symmetry.", formatter_class=RawTextHelpFormatter)

parser.add_argument('input', type=str,
                    help="Input file with strings to transform.")
parser.add_argument("-f", '--filter', type=str,
                    help="Remove output lines if they contain all the markers in this list")
parser.add_argument("-o", "--output", type=str,
                    help="Output file to read features to mark and write transformed strings (append)."+
                    "Its first line contain the sentence features to record (see '--help')")

args = parser.parse_args()

colsep = "|"  # the default char to separate columns in the .CSV output file.
st_out = filt1 = False    # default, write to output file

if args.filter:
    filt1 = args.filter.split()


# print("Args.input is %s\n" % args.input)
# print("Args.output is %s\n" % args.output)
if not os.path.isfile(args.input):
    print("The file %s does not exist" % args.input)
    sys.exit("Try again. Bye!")
elif args.output and os.path.isfile(args.output):
    with open(args.output) as fi:
        l1 = fi.readline()
        l2 = fi.readline()
        # print("line 1 is %s line 2 is %s\n" % (l1, l2))
        if l2 != None and l2 != "" and l2 != "\n":
            input_var = input("Warning: the output file %s contains more than 1 line (2nd line = %s).\nAre you sure you want to continue appending the output to it? [y/N]" % (args.output, l2.strip()))
            # print("input_var is %s" % input_var)
            if not input_var in ["y", "Y", "Yes", "YES", "yes"]:           # No, I don't want to append to used file!
                input_var = input("Do you want to reset the output file to\n%s [Y/n]?" % l1.strip())   # want to reset it?
                if not input_var.lower() in ["n", "no"]:                                       # yes
                    with open(args.output, "w") as f2:                                                  # then reset to 1rst line
                        f2.write(l1)
                else:
                    sys.exit("Bye then!")                                                              # otherwise exit
                # else here I will assume you DO want to append to a used existing file
else:           # no file specified with -o <file>, or not an existting file
    print("Outputting to stout")
    with open("./gggggg", "w") as f1:
        f1.write(colsep * 8)          # create a temporary file with a generic feature line (e.g. "||||||||").
        args.output = "./gggggg"    # set args.output to it (so `features' it can be read normally)
    st_out = True

# sys.exit("End")
# s1 = ["A", "B", "C", "D"]
# s2 = ["A", ["B1", "B2"], "C", "D"]
# s3 = ["A", ["B1", "B2"], "C", ["D1", "D2"]]
# s4 = [["B1", "B2"], "C", ["D1", "D2"], "E" ]

# ss1 = "[ D1 D2 ] E [ F1 F2 ]"


def stringp(s):
    return isinstance(s, str)


def listp(l):
    return isinstance(l, list)


def smult1(s):
    """The recursive function which does the actual multiplication. The heart of the program."""
    # print(s)
    if s:                    # the list continues
        if listp(s[0]):      # if the first elements is a list (e.g. "[[A B] C]
            l = []
            for e in s[0]:                     # for every subelement
                l = l + smult1([e]+s[1:])      # add it to the recursive application to the list rest
            return l                         # return l (e.g. [[A C][B C]])
#        else:
        return list(map(lambda x: [s[0]]+x, smult1(s[1:])))  # apply the first element, a string, to each of the results produced
#    else:                                                         # by recursing on the rest
    return [[]]



def multip(sent,orig_index,invp):
    """Takes in input a string and the original ID, splits the string into strings at the spaces, checks parenthesis balance and applies the smult1 function to it.
    If invp is True, invert the patter and inverts it back after smult1"""
    if not stringp(sent):
        print("The argument is not a string!")
        return()
    sent = re.sub(r'([\[\]])', r' \1 ', sent)              # adds spaces padding to the brackets ("[A B]" -> " [ A B ] ")
    if invp:                                               # if the 'invert' flag is on, invert the pattern (and later, invert the multiplied output)
        sent = invert(sent)
    ll = sent.split()
    b = []
    e = []
    in_par = False
    for i in ll:                         # this part checks if the parenthesis are balanced.
        if i == "[":
            in_par = True                    # activates the flag of open [
        elif i == "]":
            if not in_par:
                print("Unbalanced parenthesis (is the input on a single line?)")
                return()
            else:
                in_par = False           # found ] . Changes flag
                b.append(e)              # add the list collected from the opening of the bracket to the main list e = []
                e = []                   # remember to enter  e!

        elif in_par:                      # i is just any word. We are inside a bracket
            if i == sent[-1]:             # if we are at the last word of the sentence
                print("Too many open parentesis!")
                return()
            else:
                e.append(i)              # add it to the list with the content of the bracket
        elif in_par == False:
                # if we are not within a bracket
            b.append(i)                  # add i to the main list
    # print("The input to smult is %s" % b)
    #print("Sent  is %s" % sent)
    #print("B is %s" % b)
    if invp:
        expanded = list(map(lambda x: invert(" ".join(x)).split(), smult1(b)))      # here we reinvert the result of the
        #print("Expanded (inv) %s" % expanded)
    else:
        expanded = smult1(b)                   # Now we apply the multiplication algorithm defined above
        #print("Expanded (no inv) %s" % expanded)
    orig_list = list(str(orig_index))*(len(expanded))
    print("The number of expanded sentences for original '%s' is %d\n" % (sent, len(expanded)))
    return(expanded, orig_list)                  # and return it


# ==================================================================
# Main function
# ==================================================================

def f_main():
    tsent = 0  # The total number of sentences
    with open(args.input, 'rU') as lines, \
      open(args.output, 'r') as variants:         # to read the feature line
        fs = variants.readline().strip()
        print("Feature line of output file is:\n%s" % fs)
        fa = list(fs.split(colsep))               # default: use | as colsep to separate columns
        m = len(fa) -1                             # get the highest number of features 
        print("The feature counter is %d" % m)
        orig_index = 0
        in_block = False
        for orig,line in enumerate(lines):    # for every line which is an original, unexpanded; also keeps index of originals

            if (not line.strip() or line.strip().startswith('#')):   # if one input line is empty,
                #print("Comment: ", line)                             #or the first char which is not space or tab is a comment mark
                continue                                              # move to the next line
            elif line.strip().lower().startswith('<block'):                  # if we are entering a block.
                if  in_block:
                    raise ValueError('Nested pattern blocks!')
                    break
                else:                                    # we were out of a block, now we are entering
                    in_block = True
                    block_expanded = []                  # resets the list where the expansions within the block are accumulated
                    block_expanded_orig = []
                    exp_block_num = []
                    exp_block_name = []
                    exp_block_orig = []                 
                    expanded = []
                    block_counter = 0
                    if re.search("invert-odd", line.lower()):  # search for the flag to invert odd lines
                        inve = True
                    else:
                        inve = False
                    at = re.search("id=\'(.+?)\'", line.lower())  # search for the name of the block, value of attribute "ID" in the line
                    if at:
                        block_name = at.group(1)  # The name of the block is the value of ID
                    else:
                        block_name = 'default-block'     # set default block name
                    continue                             
            elif line.strip().lower().startswith('</block>'):    # if we find a block termination mark
                if  not in_block:
                    raise ValueError('Unbalanced pattern block (no open block)')
                    break
                else:  # then we must just be at the end of a block
                    in_block = False

                    reord = order_blocks(block_expanded, block_name, block_expanded_orig) # expands and reorder the patterns in the block, add numbers and block name, 
                
                    expanded.extend(reord[0])                         # first, add the reordered patterns to expanded
                    exp_block_name.extend(reord[1].split(" "))        # second, add the features (number)
                    exp_block_num.extend(reord[2])                    # third, add the block name)
                    exp_block_orig.extend(reord[3])                   # fourth, add the orig number
                    #print("Expanded is '%s'\n exp_block_name is '%s'\n and exp_block_num is '%s'\n Exp_block_orig is %s\n" % (expanded, exp_block_name, exp_block_num, exp_block_orig))
                    # Now we call the function which extracts the features and does the actual writing to file
                    expand_write(expanded,
                                 exp_block_name,
                                 exp_block_num,
                                 exp_block_orig,
                                 fa,
                                 m ,
                                 args.output
                    )
                    #exp_block_name = exp_block_num = expanded = []
                    

            elif in_block:                       # we must be inside a block
                    orig_index += 1
                    block_counter += 1
                    if inve and block_counter % 2 == 0:              # we do inversions on odd block lines
                        ee = multip(line.strip(), orig_index,True)      # compute the expansions (also returns the list of originals)
                    else:    
                        ee = multip(line.strip(), orig_index,False)      # compute the expansions (also returns the list of originals)
                    block_expanded.append(ee[0])  # add the expanded lines to the list of within-block expansions
                    block_expanded_orig.append(ee[1]) # add the original numbers to the list of within-block expansions list
                    #print("Line at orig %d is %s\n Multip(line) is %s " % (orig_index, line, multip(line.strip())))
                    #print("Block_Expanded at orig %d is %s " % (orig_index, block_expanded))


            else:           # not inside a block, it should just mimic the old Multiply.py

                orig_index += 1                                
                ee = multip(line.strip(),orig_index,False)    # uses multip defined above to expand original, giving list of lists of word-strings, with underscores                
                expanded = ee[0]
                expanded_orig = ee[1]
                expand_write(expanded,"", "",expanded_orig,fa, m, args.output)
                expanded = []
                
    with open(args.output, 'r') as lines:     # the rest adds a progressive line number to the first column of the previous output
        data = lines.readlines()
    with open(args.output, 'w') as lines:
        maxnum = 0
        for (number, line) in enumerate(data):
            if number == 0:
                lines.write(line)
            else:
                lines.write('%d%s' % (number, line))
                maxnum = number
        print("Written %d lines" % maxnum)


                    
def expand_write(expanded,exp_block_name,exp_block_num,expanded_orig,fa,m,arg):    # args.output
    with open(arg, 'a') as variants:
        string_expanded = list(map(lambda x: x.replace("_", " "),(map(" ".join, expanded)))) # reconnect the various wordstrings into one per expansion
        # removing the underscores. Still listed
                        #print(string_expanded)
        for n, a, in enumerate(string_expanded): # now for every individual expansion
                                                 # next, redivide into list of words with split()  
                                                 #[i for i in a.split() if not re.match("@@[0-9]*@@", i)] 
            o = a.split() # next, redivide into list of words with split()  
            if filt1 and set(filt1).issubset(o): # if all the elements of the filter list are present in the expansion, skip it
                continue
            #print("N = %d, o = %s, \n exp_block_name = %s \n exp_block_num = %s " % (n, o, exp_block_name, exp_block_num )) 
            f = [""]*m                      # initializing the list to be appended 
            w_index = 0                     # initializing word position counter
            for b in o:
                if b in fa:               # if a word is found in the first line of the file (the feature list)
                    # print("Word %s in FA at pos %d" % (a, w_index))   # (list of words for which we want presence and position marked)
                    f[fa.index(b)] = w_index +1    # set the n position of the feature list to a's position in the expansion
                                                # where n is given by the position of the feature name in the file's first line, plus an offset of 2
                                                # to accommodate the expansion and the number of the original sentence
                                                # Now we put everything together
                if not re.match("^@@[0-9]*@@$", b):
                    w_index += 1      # we increment the sentence position only if the word is not a gap-mark
                                                      # Now we write the feature line of the sentence.
                                                      #
            f[0] = ""                      # first, the expansion global counter
            if exp_block_name:
                f[1] = exp_block_name[n]        # add the block feature of the index of the current line (e.g. "myblock")
            else:
                f[1] = "-----"                    # Not in a block
            if exp_block_num:
                f[2] =  exp_block_num[n]        # add the block order number of the index of the current line (e.g. "1")
            else:
                f[2] = "-----"                     # Not in a block
            f[3] = re.sub("@@[0-9]*@@", "", " ".join(o)) # then the expansion itself, removing the "@@<num>@@" markers and rejoining it into a string
            if listp(expanded_orig):
                f[4] = expanded_orig[n][0]           # then the number of the original from which it came
            else:
                f[4] = expanded_orig
            for st in range(m):
                if  st_out:     # no or wrong output file
                    # print("I am here (stout)")
                    sys.stdout.write("%s%s" % (str(f[st]).strip(), colsep))   # write each value to standerd output
                else:
                                    # print("I am here (variants = %s)", str(variants))
                    variants.write("%s%s" % (str(f[st]).strip(), colsep))   # , end = ""
                                    # print("%s|" % f[st], end = "")
            if st_out:
                sys.stdout.write("\n")                         #  now close the line
            else:
                variants.write("\n")                           #  now close the line


def order_blocks(lis, name, orig):
    """Takes a set of sets of expanded patters (a list of lists) and orders them
    E:g. from original patters 'Who [A B]', 'What [A B]' it would input the expanded 
    [[[Who A][Who B]] [[What A][What B]]] and should return
    [[Who A][Who B][What A][What B]], plus block names, repeated, in-block numbers [1 1 2 2] and orig numbers [1 2 1 2]"""
    
    if len(lis) < 2:
        raise ValueError("Block is too small")
    elif len(set(map(len, lis))) not in (0, 1):
                                raise ValueError('not all lists have same length!')   # to be truly minimal pairs the list should have the same length (cheat with "_" if needed)
    else:
        min_pair = []
        tags = []
        orig_list = []
        for i in range(len(lis[1])):    # i ranges over the expansions of an individual original  
            for k, l in enumerate(lis):               # j, over the lists of expanded originals
                min_pair.append(l[i])                       # appends the i-th expansion of each original j 
                #print(min_pair)
                tags.append(str(i))
                orig_list.append(orig[k])    # XXX
                #print(tags)
    # return {'r1':min_pair, 'r2':tags}
    #print("Lis is %s \n Len(lis[1]) is %s \n Min_pair is %s \nName is %s \nTags is %s\nOrig_list is %s" % (lis, len(lis[1]), min_pair, (name+" ")*len(lis)*len(lis[1]), tags,orig_list))
    return(min_pair, (name+" ")*len(lis[1])*len(lis),tags, orig_list)  # callable with order_blocks2(args...)[num]


def invert(lis):
    """Take a string of the form A [B C D] E [F G] H" and inverts the position of all the words outside '[]' , treating everythung in brackets as it it was a single word."""
    a = ""
    brack = False
    for c in lis:
        if c == "[":
            brack = True
            a = a+c
        elif brack and c == " ":
            a = a+"&&&"             # inside brackets, replace space with &
        elif c == "]":
            brack = False
            a = a+c
        else:
            a = a+c
    ll = a.split( )
    return(re.sub("&&&", " ", " ".join(list(reversed(ll)))))


    
    
            


f_main()


if st_out:
    os.remove('./gggggg')  # if output to stout, remove the temporary file with default feature line.




#    the_dog [ is are ] sick
#    sick [ is are ] the_dog
#    sick is the_dog
#    the_dog is_sick 
