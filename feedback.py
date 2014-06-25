import sys;
import os;
import codecs;
import string;
import copy;
import http.client;

class RetrievalFileReader:
    def __init__(self, fileName):
        self.fileName = fileName;
        self._readKeywordURLPairs();

    def _readKeywordURLPairs(self):
        inFile = open(self.fileName, "r");

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
        connection = http.client.HTTPConnection(self.domainName, self.portNumber);
        connection.request("GET", self.resourcePath);
        content = connection.getresponse().read(); # the variable "content" is of type "byte"
        connection.close();

        return str(content); # returns "content" of type "str"

class DocumentBrowser:
    def __init__(self, _content, _previousWordCount = 20, _nextWordCount = 20, _distanceThreshold = 3):

        content = copy.deepcopy(_content);
        content = self._removeHTMLTags(content);
        content = self._removePunctuation(content);
        
        self.contentWords = content.strip().split();

        content = self._transformLowerCase(content);

        self.documentWords = content.strip().split();
        self.documentWordCount = len(self.documentWords);

        self.wordPrimitiveDict = {word: self.contentWords[n] for (n, word) in enumerate(self.documentWords)}; # keeps primitive forms of words
        self.previousWordCount = _previousWordCount;
        self.nextWordCount = _nextWordCount;
        self.distanceThreshold = _distanceThreshold;

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
                newContent += " "; # HTML tags is replaced with " "
        
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

        editTable = [[0 for j in range(charCount1 + 1)] for i in range(charCount2 + 1)];

        for i in range(1, charCount2 + 1):
            editTable[i][0] = editTable[i - 1][0] + 1;

        for j in range(1, charCount1 + 1):
            editTable[0][j] = editTable[0][j - 1] + 1;

        for i in range(1, charCount2 + 1):
            char2 = word2[i - 1];

            for j in range(1, charCount1 + 1):
                char1 = word1[j - 1];

                if char1 == char2:
                    editTable[i][j] = editTable[i - 1][j - 1];
                else:
                    editTable[i][j] = min([editTable[i - 1][j - 1] + 1, editTable[i - 1][j] + 1, editTable[i][j - 1] + 1]);

        return editTable[charCount2][charCount1];

    def _isSameWord(self, word1, word2):
        editDistance = self._getEditDistance(word1, word2);
        isSame = (editDistance <= self.distanceThreshold);
        if isSame:
            print("\tFound word: ", word1);
        return isSame;

    def _findKeywords(self, keywords):
        for (i, keyword) in enumerate(keywords):
            newKeyword = self._removeHTMLTags(keyword);
            newKeyword = self._transformLowerCase(newKeyword);
            newKeyword = self._removePunctuation(newKeyword);
            keywords[i] = newKeyword;

        keywordIndices = [];
        keywordCount = len(keywords);

        w = 0;
        while w < self.documentWordCount - keywordCount + 1:
            wellMatched = True;

            for t in range(keywordCount):
                documentWord = self.documentWords[w + t];
                keyword = keywords[t];
                if not self._isSameWord(documentWord, keyword):
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

    def _getKeywordParagraphs(self, keyword):
        paragraphs = [];
        subKeywords = keyword.strip().split();
        subKeywordCount = len(subKeywords);
        keywordIndices = self._findKeywords(subKeywords);

        for keywordIndex in keywordIndices:
            paragraphFirstIndex = keywordIndex - self.previousWordCount;
            if paragraphFirstIndex < 0:
                paragraphFirstIndex = 0;

            paragraphLastIndex = keywordIndex + subKeywordCount + self.nextWordCount;
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
                wordPrimitive = self.wordPrimitiveDict[word];
                if wordPrimitive in feedbackDict:
                    feedbackDict[wordPrimitive] += 1;
                else:
                    feedbackDict[wordPrimitive] = 1;

        return feedbackDict;

"""
    usage: python3 feedback.py [input_query_file_path] [output_feedback_file_path] [previous_word_count] [next_word_count] [distance_threshold]
"""
def main():
    retrievalFileName = sys.argv[1];
    feedbackFileName = sys.argv[2];

    previousWordCount = 20;
    nextWordCount = 20;
    if len(sys.argv) >= 5:
        previousWordCount = int(sys.argv[3]);
        nextWordCount = int(sys.argv[4]);

    distanceThreshold = 3;
    if len(sys.argv) >= 6:
        distanceThreshold = int(sys.argv[5]);

    retrievalFileReader = RetrievalFileReader(retrievalFileName);
    keywordURLs = retrievalFileReader.getKeywordURLPairs();
    
    feedbackFile = open(feedbackFileName, "w");
    
    for (keyword, URL) in keywordURLs:
        print("Read webpage " + str(URL));
        webpageReader = WebpageReader(URL);
        content = webpageReader.readContent();

        print("Content type: ", type(content));

        print("Execute feedback of the keyword \"" + str(keyword) + "\"");
        documentBrowser = DocumentBrowser(content, previousWordCount, nextWordCount, distanceThreshold);
        feedbackDict = documentBrowser.gatherFeedbackWords(keyword);
        
        for (word, count) in sorted(feedbackDict.items(), key = lambda kv: (kv[1], kv[0]), reverse = True):
            feedbackFile.write(str(word) + "\n");
    
    feedbackFile.close();

if __name__ == "__main__":
    main();
