import sys;
import os;
import codecs;
import string;
import httplib;
import copy;

class RetrievalFileReader:
    def __init__(self, fileName):
        self.fileName = fileName;
        self._readKeywordURLPairs();

    def _readKeywordURLPairs(self):
        inFile = open(fileName, "r");

        self.keywordURLs = [];
        itemIndex = 0;
        keyword = "";
        URL = "";
        for line in inFile:
            row = line.strip();
            if len(row) == 0:
                itemIndex = 0;
                continue;
            if itemIndex == 4:
                itemIndex = 0;

            if itemIndex == 0:
                keyword = row;

            if itemIndex == 3:
                URL = row;
                self.keywordURLs.append((keyword, URL));
            
            itemIndex += 1;    

        inFile.close();

    def getKeywordURLPairs(self):
        return self.keywordURLs;

class WebpageReader:
    def __init__(self, webpageURL):
        self.webpageURL = copy.deepcopy(webpageURL);
        self._removeProtocalName();
        self._getDomainName();
        self._getPortNumber();
        self._getResourcePath();

    def _removeProtocalName(self):
        if self.webpageURL.find("http://") == 0:
            self.webpageURLNoProtocal = self.webpageURL[7 : ];
        else:
            self.webpageURLNoProtocal = self.webpageURL;

        #print(self.webpageURLNoProtocal);

    def _getDomainName(self):
        slashIndex = self.webpageURLNoProtocal.find("/");
        self.domainName = self.webpageURLNoProtocal[ : slashIndex];

        #print(self.domainName);

    def _getPortNumber(self):
        colonIndex = self.domainName.rfind(":");
        if colonIndex != -1:
            self.portNumber = int(self.domainName[colonIndex + 1 : ]);
            self.domainName = self.domainName[ : colonIndex];
        else:
            self.portNumber = 80;

        #print(self.portNumber);

    def _getResourcePath(self):
        slashIndex = self.webpageURLNoProtocal.find("/");
        self.resourcePath = self.webpageURLNoProtocal[slashIndex : ];
        
        #print(self.resourcePath);

    def readContent(self):
        connection = httplib.HTTPConnection(self.domainName, self.portNumber);
        connection.request("GET", self.resourcePath);
        content = connection.getresponse().read();
        connection.close();

        return content;

class DocumentBrowser:
    def __init__(self, _content):
        content = copy.deepcopy(_content);
        content = self._removeHTMLTags(content);
        content = self._transformLowerCase(content);
        content = self._removePunctuation(content);

        self.documentWords = content.strip().split();
        self.documentWordCount = len(self.documentWords);

    def _removeHTMLTags(self, content):
        newContent = "";

        tagLayer = 0;
        for character in content:
            if character == "<":
                tagLayer += 1;
            
            if tagLayer == 0:
                newContent += character;
            
            if character == ">":
                tagLayer -= 1;
        
        return newContent;

    def _transformLowerCase(self, content):
        return content.lower();

    def _removePunctuation(self, content):
        newContent = "";
        punctuationDict = {p: True for p in string.punctuation};

        for character in content:
            if character not in punctuationDict:
                newContent += character;

        return newContent;

    def _getEditDistance(self, word1, word2):
        charCount1 = len(word1);
        charCount2 = len(word2);

        editTable = [[0 for j in xrange(charCount2)] for i in xrange(charCount1)];

        for i in xrange(1, charCount1):
            difference = 0 if word2[0] == word1[i] else 1;
            editTable[i][0] = difference + editTable[i - 1][0];

        for j in xrange(1, charCount2):
            difference = 0 if word1[0] == word2[j] else 1;
            editTable[0][j] = difference + editTable[0][j - 1];

        for i in xrange(1, charCount1):
            char1 = word1[i];

            for j in xrange(1, charCount2):
                char2 = word2[j];
                difference = 0 if char1 == char2 else 1;

                minDistance = editTable[i - 1][j - 1];
                minDistance = editTable[i - 1][j] if minDistance > editTable[i - 1][j] else minDistance;
                minDistance = editTable[i][j - 1] if minDistance > editTable[i][j - 1] else minDistance;

                editTable[i][j] = difference + minDistance;

        return editTable[charCount1 - 1][charCount2 - 1];

    def _isSameWord(self, word1, word2, distanceThreshold):
        editDistance = self._getEditDistance(word1, word2);
        return editDistance <= distanceThreshold;

    def _findKeywords(self, keywords, distanceThreshold = 3):
        keywordIndices = [];
        keywordCount = len(keywords);

        print("Word count in document:", self.documentWordCount);

        w = 0;
        while w < self.documentWordCount - keywordCount + 1:
            print "\t", w;
            wellMatched = True;

            for t in xrange(keywordCount):
                documentWord = self.documentWords[w + t];
                keyword = keywords[t];
                if not self._isSameWord(documentWord, keyword, distanceThreshold):
                    wellMatched = False;
                    break;
                
            if wellMatched:
                keywordIndices.append(w);
                w += keywordCount;
            else:
                w += 1;

        return keywordIndices;

    def _fetchParagraph(self, firstIndex, lastIndex):
        return self.documentWords[firstIndex : lastIndex + 1];

    def _getKeywordParagraphs(self, keyword, previousWordCount = 20, nextWordCount = 20):
        paragraphs = [];
        subKeywords = keyword.strip().split();
        subKeywordCount = len(subKeywords);
        keywordIndices = self._findKeywords(subKeywords);

        for keywordIndex in keywordIndices:
            paragraphFirstIndex = keywordIndex - previousWordCount;
            if paragraphFirstIndex < 0:
                paragraphFirstIndex = 0;

            paragraphLastIndex = keywordIndex + subKeywordCount + nextWordCount;
            if paragraphLastIndex >= self.documentWordCount:
                paragraphLastIndex = self.documentWordCount - 1;

            newParagraph = self._fetchParagraph(paragraphFirstIndex, paragraphLastIndex);
            paragraphs.append(newParagraph);

        return paragraphs;

    def gatherFeedbackWords(self, keyword):
        paragraphs = self._getKeywordParagraphs(keyword);

        feedbackDict = {};
        for paragraph in paragraphs:
            for word in paragraph:
                if word in feedbackDict:
                    feedbackDict[word] += 1;
                else:
                    feedbackDict[word] = 1;

        return feedbackDict;

def main():
    retrievalFileName = sys.argv[1];
    feedbackFileName = sys.argv[2];

    retrievalFileReader = RetrievalFileReader(retrievalFileName);
    keywordURLs = retrievalFileReader.getKeywordURLPairs();
    
    feedbackFile = open(feedbackFileName, "w");
    
    for (keyword, URL) in keywordURLs:
        print("Read webpage " + str(URL));
        webpageReader = WebpageReader(URL);
        content = webpageReader.readContent();

        print("Execute feedback of the keyword " + str(keyword));
        documentBrowser = DocumentBrowser(content);
        feedbackDict = documentBrowser.gatherFeedbackWords(keyword);
        
        for (word, count) in sorted(feedbackDict.items(), key = lambda (k, v): (v, k), reverse = True):
            feedbackFile.write(str(word) + "\n");
    
    feedbackFile.close();

if __name__ == "__main__":
    main();
