# -*- coding: utf-8 -*-
"""
/////////////////////////////////////////////////////////////////////////////////
tagger.py

@author: Stephen Kalen
@Created on Thu Mar 11 15:54:56 2021
@description:
    This program uses training data mapping words to part of speech tags to 
    label the part of speech of each word in a test set using POS tag bigrams, 
    POS tag frequencies, and a table counting the frequency of each tag that a 
    word occurs as. Each word in the test set is given its most likely POS tag.
@problem:
    Part of speech tags are the tags given to words to show what part of 
    speech they are in the sentence(noun, verb, ...). Can we create a program
    that assigns each word its most likely POS tag using an existing set of
    words and their possible tags?
@instructions:
    1. run the program using the following on the command line:
        python tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt
    2. use scorer.py to get a report of the program's accuracy
@algorithm:
    -reads the train file and stores words and tags, counting the frequency of
     each tag
    -creates a table showing the frequency of each tag for each word by counting
     the occurence of each tag for each word in the training set
    -creates a table showing the frequency of each tag given that another tag
     has occured using the training set
    -reads the test file and for each word do the following:
        -if the word didn't occur in the training data, give it the NN tag
        -otherwise if the word only ever occured with one tag in the training
         set, give it that tag
        -otherwise calculate the probabilities for each tag by:
            -taking the bigram value given the current tag t and the previous
             tag t-1 and dividing it by the total frequency of the tag t
            -taking the frequency of the word having that tag divided by the
             total frequency of the tag
            -and multiplying those values together
        -then takes these probabilities and gives the current word the tag 
        with the highest probability
    -prints the words and their matching tags to STDOUT
@results
    original algorithm:
        accuracy = 0.8442911445867943
    rule 1: if the word contains numbers, it gets the CD tag
        accuracy = 0.5619104603688583
    rule 2: eliminate VBN if VBD is an option when VBN|VBD follows ". PRP"
        accuracy = 0.8442911445867943
    rule 3: if the word is unknown and ends in a vowel it is given the FW tag
        accuracy = 0.7962480641982261
    rule 4: eliminate DT if RB is an option when DT|RB follows "."
        accuracy = 0.8442559481909052
    rule 5: if a number follows a VBD it is not 
        accuracy = 0.8444671265662396
/////////////////////////////////////////////////////////////////////////////////
"""
"""
Imports the sys and re packages
"""
import sys
import re

"""
getArgs() sets the names of the input files from the command line inputs
"""
def getArgs():
    trainfile = sys.argv[1]
    testfile = sys.argv[2]
    return trainfile, testfile

"""
readTrainFile() reads the train file for the list of words and tags and also
finds and returns a dictionary mapping the words to and tags it is associated
with, a list of all tags without repeating, a list of all words without 
repeating and a list counting the number of times each tag is found
"""
def readTrainFile(str):
    f = open(str)
    words = []
    tags = []
    taglist = []
    wordlist = []
    wordsdict = {}
    for line in f:
        line = re.sub(r'[\[\]]', '',line)
        line = line.replace('\\/', '\\')
        line = re.sub('\|[a-zA-Z0-9]*','',line)
        line += " "
        linecontent = line.split()#do i need this???
        linecontent = re.split("\s",line)
        for wor in linecontent:
            linecontent2 = re.split('/',wor)
            if len(linecontent2) > 1:
                words.append(linecontent2[0])
                tags.append(linecontent2[1])
                if wordsdict.get(linecontent2[0], 0) == 0:
                    tagset = {linecontent2[1]}
                    wordsdict[linecontent2[0]] = tagset
                else:
                    wordsdict[linecontent2[0]].add(linecontent2[1])
                if taglist.count(linecontent2[1]) == 0:
                    taglist.append(linecontent2[1])
                if wordlist.count(linecontent2[0]) == 0:
                    wordlist.append(linecontent2[0])
    f.close()
    tagcount = [0] * len(tags)
    for tag in tags:
        index = taglist.index(tag)
        tagcount[index] += 1
    return words, tags, wordsdict, taglist, wordlist, tagcount

"""
makeWordsTagTable() creates a table showing the frequency of each tag for each
word
"""
def makeWordsTagTable(words, tags, taglist, wordlist):
    wordtagtable = [0] * len(taglist)
    for i in range(len(taglist)):
        wordtagtable[i] = [0] * len(wordlist)
    index = 0
    for word in words:
        y = wordlist.index(word)
        tag = tags[index]
        x = taglist.index(tag)
        wordtagtable[x][y] += 1
        index += 1
    return wordtagtable

"""
makeTagTable() creates a bigram table for tags showing the frequency of each
two tag combination
"""
def makeTagTable(words, tags, taglist):
    history = []
    tagstable = [0] * len(taglist)
    for i in range(len(taglist)):
        tagstable[i] = [0] * len(taglist)
    for tag in tags:
        history.append(tag)
        if len(history) > 2:
            history.pop(0)
        if len(history) == 2:
            x = taglist.index(history[0])#index of t-1
            y = taglist.index (history[1])#index of t
            tagstable[x][y] += 1
    return tagstable

"""
makeFreqTable() creates a list of probabilites for each tag that show the
chance that that tag is the tag for the current word
"""
def makeFreqTable(first, words, tags, taglist, wordlist, wordtagtable, tagstable, tagscount, history):
    frequencies = [0] * len(taglist)
    taglist = list(taglist)
    if first == False:
        pwordindex = words.index(history[0])
    if first == True:
        prevtag = '.'
    else:
        prevtag = tags[pwordindex]
    freqindex = 0
    for tag in taglist:
        x = taglist.index(prevtag)#index of t-1
        y = taglist.index(tag)#index of t
        z = wordlist.index(history[1])#index of w
        numerator1 = tagstable[x][y]
        numerator2 = wordtagtable[y][z]
        denominator = tagscount[y]
        num1 = numerator1 / denominator
        num2 = numerator2 / denominator
        num3 = num1 * num2
        frequencies[freqindex] = num3
        freqindex += 1
    frequencies = applyRules(frequencies, taglist, prevtag, history, tags)#executes rules on frequencies for tags
    return frequencies

"""
applyRules() applies the POS rules to the frequency tables
"""
def applyRules(frequencies, taglist, prevtag, history, tags):
    #rule 1:
    """
    currentword = history[1]
    if re.search(r'\d', currentword) != 'None':
        tagindex = taglist.index('CD')
        frequencies[tagindex] = 1
    """
    #rule 2:
    """
    if len(tags) > 1:
        if tags[-1] == 'PRP' and tags[-2] == '.':
            VBDindex = taglist.index('VBD')
            if frequencies[VBDindex] > 0:
                VBNindex = taglist.index('VBN')
                frequencies[VBNindex] = 0
    """
    #rule 4:
    """
    if history[0] == '.' or tags[-1] == '.':
        DTindex = taglist.index('DT')
        RBindex = taglist.index('RB')
        if frequencies[DTindex] > 0 and frequencies[RBindex] > 0:
            frequencies[DTindex] = 0
    """
    return frequencies

"""
tagTestingDate() reads the testing data, gets all the words in the testing set,
and finds the most likely POS tag. If the word only has one tag in the 
words dictionary it is given that word. If the word was not in the training set
the word is given the NN tag. Otherwise the word is given the tag with the
highest probability from the probability table made in makeFreqTable()
"""
def tagTestingData(testfile, wordsdict, wordlist, taglist, tagscount, wordtagtable, tagstable):
    f = open(testfile)
    words = []
    tags = []
    for line in f:
        line = re.sub(r'[\[\]]', '',line)
        line = line.replace('\\/', '\\')
        line = line + ' '
        linecontent = line.split()
        for wor in linecontent:
            words.append(wor)
    f.close()
    history = ['.']
    count = 0
    for word in words:
        history.append(word)
        if len(history) > 2:
            history.pop(0)
        currenttaglist = list(wordsdict.get(word, "<NONE>"))
        if currenttaglist == ['<', 'N', 'O', 'N', 'E', '>']:
            #rule 3
            """
            if re.search(r'[aeiou]$', history[1]) != 'None':
                tags.append('FW')
            else:
                tags.append('NN')
            """
            #rule 5
            """
            if re.search(r'\d', history[1]) != 'None' and tags[-1] == 'VBD':
                tags.append('CD')
            else:
                tags.append('NN')
            """
            tags.append('NN')#needs to be commented out if rule 3 or 4 is uncommented
        elif len(currenttaglist) == 1:
            tags.append(currenttaglist[0])
        else:
            if count == 0:
                first = True
            else:
                first = False
            frequencies = makeFreqTable(first, words, tags, taglist, wordlist, wordtagtable, tagstable, tagscount, history)
            maxfreq = frequencies[0]
            freqindex = 0
            index = 0
            for freq in frequencies:
                if freq > maxfreq:
                    maxfreq = freq
                    freqindex = index
                index += 1
            tags.append(taglist[freqindex])
        count += 1
    return tags, words

"""
printTagsAndWords() prints the words in the training set and their most likely
tags in the proper format
"""
def printTagsAndWords(words, tags):
    index = 0
    for word in words:
        word = word.replace('\\\\', '\\\/')
        out = word + '/' + tags[index]
        index += 1
        sys.stdout.write(out + '\n')

"""
The following code executes the previous functions
"""
trainfile, testfile = getArgs()
words, tags, wordsdict, taglist, wordlist, tagcount = readTrainFile(trainfile)
wordtagtable = makeWordsTagTable(words, tags, taglist, wordlist)
tagstable = makeTagTable(words, tags, taglist)
testtags, testwords = tagTestingData(testfile, wordsdict, wordlist, taglist, tagcount, wordtagtable, tagstable)
printTagsAndWords(testwords,testtags)