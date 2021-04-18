# POS_Tagger - CMSC 416
Python program that tags words with the appropriate part of speech.

This program uses training data mapping words to part of speech tags to label the part of speech of each word in a test set using POS tag bigrams, POS tag frequencies, and a table counting the frequency of each tag that a word occurs as. Each word in the test set is given its most likely POS tag.

instructions:
    1. run the tagger using the following on the command line:
        python tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt
    2. run the scorer using the following on the command line:
        python scorer.py pos-test-with-tags.txt pos-test-key.txt > pos-tagging-report.txt
