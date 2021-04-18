# -*- coding: utf-8 -*-
"""
////////////////////////////////////////////////////////////////////////////////////////////
scorer.py

@author: Stephen Kalen
@Created on Thu Mar 11 15:55:32 2021
@description:
    This program takes a tagged test file and the key to the test file with
    the correct tags and calculates the accuracy and confusion matrix by 
    comparing the tags in each file.
@instrucions:
    1. use tagger.py to get pos-test-with-tags.txt
    2. run the program using the following on the command line:
        python scorer.py pos-test-with-tags.txt pos-test-key.txt > pos-tagging-report.txt
@algorithm:
    -reads both files and gets the word and tag information from each file
    -counts the number of tags total
    -counts the number of tags that match (and are correct)
    -gets accuracy by dividing the number of matching tags by the total 
     number of tags
    -creates the confusion matrix by adding each tag to a table mapping the
     actual tag to the predicted tag
    -prints the accuracy and the confustion matrix to STOUT
//////////////////////////////////////////////////////////////////////////////////////////
"""
"""
imports the system and regular expression packages
"""
import sys
import re

"""
getArgs() sets the names of the input files from the command line arguments
"""
def getArgs():
    taggedtestfile = sys.argv[1]
    testkeyfile = sys.argv[2]
    return taggedtestfile, testkeyfile

"""
readTestFile() reads the test file for a list of words and their tags
"""
def readTestFile(taggedtestfile):
    f = open(taggedtestfile)
    words = []
    tags = []
    for line in f:
        line = re.sub(r'[\[\]]', '',line)
        line = re.sub(r'\n', '',line)
        line = re.sub('\|[a-zA-Z0-9]*','',line)
        linecontent = re.split('/',line)
        words.append(linecontent[0])
        tags.append(linecontent[1])
    f.close()
    return words, tags
    
"""
readKeyFile() reads the key file for a list of words, tags, the total number
of words in the text, and a list of all tags without repeating
"""
def readKeyFile(testkeyfile):
    f = open(testkeyfile)
    keywords = []
    keytags = []
    taglist = []
    numwords = 0
    for line in f:
        line = re.sub(r'[\[\]]', '',line)
        line = line.replace('\\/', '\\')
        line = re.sub('\|[a-zA-Z0-9]*','',line)
        linecontent = line.split()
        for wor in linecontent:
            linecontent2 = re.split('/',wor)
            if len(linecontent2) > 1:
                keywords.append(linecontent2[0])
                keytags.append(linecontent2[1])
                if taglist.count(linecontent2[1]) == 0:
                    taglist.append(linecontent2[1])
                numwords +=1
    f.close()
    return keywords, keytags, numwords, taglist

"""
getAccuracy() calculates the accuracy of the tagger by finding the total
number of words correctly tagged and dividing it by the total number of words
"""
def getAccureacy(tags, keytags, numwords):
    numcorrect = 0
    index = 0
    for tag in tags:
        if tag == keytags[index]:
            numcorrect += 1
        index += 1
    accuracy = numcorrect / numwords
    return accuracy

"""
getConfusionMatrix() creates the confusion matrix for the results by tallying
each tag in the table according to its expected value from the key and actual 
value from the tagger
"""
def getConfusionMatrix(tags, keytags, taglist):
    confusionmatrix = [0] * len(taglist)
    for i in range(len(taglist)):
        confusionmatrix[i] = [0] * len(taglist)
    index = 0
    for tag in tags:
        actual = taglist.index(keytags[index])
        predicted = taglist.index(tag)
        confusionmatrix[actual][predicted] += 1
        index += 1
    return confusionmatrix

"""
writeOutput() prints the accuracy and confusion matrix to STOUT
"""
def writeOutput(accuracy, confusionmatrix, taglist):
    out = "Accuracy: " + str(accuracy) + '\n'
    sys.stdout.write(out)
    index = 0
    sys.stdout.write("Confusion Matrix: \n")
    for x in confusionmatrix:
        out = taglist[index] + " " + str(x) + '\n'
        sys.stdout.write(out)
        index += 1

"""
The following code executes the previous functions and exits the program.
"""
taggedtestfile, testkeyfile = getArgs()
words, tags = readTestFile(taggedtestfile)
keywords, keytags, numwords, taglist = readKeyFile(testkeyfile)
accuracy = getAccureacy(tags, keytags, numwords)
confusionmatrix = getConfusionMatrix(tags, keytags, taglist)
writeOutput(accuracy, confusionmatrix, taglist)