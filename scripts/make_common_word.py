import sys;
import os;
import codecs;
import string;
from nltk.stem.snowball import SnowballStemmer;

def readDatabase(directoryName):
    database = [];

    for (dirName, dirNames, fileNames) in os.walk(directoryName):
        for fileName in fileNames:
            filePath = os.path.join(dirName, fileName);

            database.append([]);
            inFile = open(filePath, "r");
            
            for line in inFile:
                database[-1].extend(line.strip().split());

            inFile.close();

    return database;

def moreSplitWord(word):
    newWords = [];
    splitCharacterDict = {"-": True, "'": True};

    recursive = False;
    for (c, character) in enumerate(word):
        if character in splitCharacterDict:
            recursive = True;
            preWord = word[ : c];
            postWord = word[c + 1 : ];
            newWords.append(preWord);
            newWords.extend(moreSplitWord(postWord));
            break;

    if not recursive:
        newWords.append(word);

    return newWords;

def transformLowerCase(word):
    return word.lower();

def removePunctuation(word, punctuationDict):
    newWord = "";
    
    for (c, character) in enumerate(word):
        if character in punctuationDict:
            continue;
        newWord += character;
    
    return newWord;

def leaveAlphabetDigit(word, alphabetDict, digitDict):
    newWord = "";

    for character in word:
        if character in alphabetDict or character in digitDict:
            newWord += character;

    return newWord;

def stemWord(word, stemmer):
    newWord = stemmer.stem(word);
    return newWord;

def handleDocumentWords(document, punctuationDict, alphabetDict, digitDict, stemmer):
    newDocument = [];

    for (w, word) in enumerate(document):
        newWords = moreSplitWord(word);
        
        for newWord in newWords:
            newWord = transformLowerCase(newWord);
            newWord = removePunctuation(newWord, punctuationDict);
            newWord = leaveAlphabetDigit(newWord, alphabetDict, digitDict);
            newWord = stemWord(newWord, stemmer);

            if len(newWord) > 0:
                newDocument.append(newWord);

    return newDocument;

def handleDatabaseWords(database):
    punctuationDict = {p: True for p in string.punctuation};
    alphabetDict = {a: True for a in string.letters};
    digitDict = {d: True for d in string.digits};
    stemmer = SnowballStemmer("english");
    for (d, document) in enumerate(database):
        database[d] = handleDocumentWords(document, punctuationDict, alphabetDict, digitDict, stemmer);

def countDocumentFrequency(database):
    dfDict = {};

    for document in database:
        occurrenceDict = {};

        for word in document:
            if word not in occurrenceDict:
                occurrenceDict[word] = True;

                if word in dfDict:
                    dfDict[word] += 1;
                else:
                    dfDict[word] = 1;

    return dfDict;

def writeDocumentFrequencyFile(dfDict, dfThresholdRate, dfFileName):
    dfThreshold = round(len(dfDict) * dfThresholdRate);

    dfFile = open(dfFileName, "w");

    for (w, (word, df)) in enumerate(sorted(dfDict.items(), key = lambda (k, v): v, reverse = True)):
        if w > dfThreshold:
            break;
        dfFile.write(str(word) + "\t" + str(df) + "\n");

    dfFile.close();

def main():
    directoryName = sys.argv[1];
    dfFileName = sys.argv[2];
    dfThresholdRate = float(sys.argv[3]);
    
    print("Read database");
    database = readDatabase(directoryName);
    
    print("Handle words");
    handleDatabaseWords(database);

    print("Count document frequency");
    dfDict = countDocumentFrequency(database);
    
    print("Write document frequency file");
    writeDocumentFrequencyFile(dfDict, dfThresholdRate, dfFileName);

if __name__ == "__main__":
    main();
