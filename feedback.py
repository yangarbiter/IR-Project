import sys;
import os;
import codecs;
import string;
import copy;
import http.client;
from html.parser import HTMLParser;

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

    def _getDomainName(self):
        slashIndex = self.webpageURLNoProtocal.find("/");
        self.domainName = self.webpageURLNoProtocal[ : slashIndex];

    def _getPortNumber(self):
        colonIndex = self.domainName.rfind(":");
        if colonIndex != -1:
            self.portNumber = int(self.domainName[colonIndex + 1 : ]);
            self.domainName = self.domainName[ : colonIndex];
        else:
            self.portNumber = 80;

    def _getResourcePath(self):
        slashIndex = self.webpageURLNoProtocal.find("/");
        self.resourcePath = self.webpageURLNoProtocal[slashIndex : ];
        
    def readContent(self):
        connection = http.client.HTTPConnection(self.domainName, self.portNumber);
        connection.request("GET", self.resourcePath);
        content = connection.getresponse().read(); # the variable "content" is of type "byte"
        connection.close();

        return str(content); # returns "content" of type "unicode"

class HTMLTagRemover(HTMLParser):
    def __init__(self):
        self.reset();
        self.tagRemovedContent = "";
        self.convert_charrefs = True;
        self.strict = False;

    def handle_data(self, words):
        self.tagRemovedContent += words;
    
    def handle_starttag(self, tag, attributes):
        self.tagRemovedContent += " ";

    def handle_endtag(self, tag):
        self.tagRemovedContent += " ";

    def getTagRemovedContent(self):
        return copy.deepcopy(str(self.tagRemovedContent));

class DocumentBrowser:

    def __init__(self, _content, _previousWordCount, _nextWordCount, _distanceThreshold):
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
        tagRemover = HTMLTagRemover();
        tagRemover.feed(content);
        newContent = tagRemover.getTagRemovedContent();
        return newContent;

    def _transformLowerCase(self, content):
        return content.lower();

    def _removePunctuation(self, content):
        newContent = "";
        punctuationDict = {p: True for p in string.punctuation};

        for character in content:
            if character in punctuationDict:
                newContent += " ";
            else:
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
        return isSame;

    def _findKeywords(self, keywords):
        for (i, keyword) in enumerate(keywords):
            newKeyword = self._transformLowerCase(keyword);
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

    def _fetchParagraph(self, firstIndex, lastIndex, keywordIndex):
        previousParagraph = self.documentWords[firstIndex : keywordIndex];
        nextParagraph = self.documentWords[keywordIndex + 1 : lastIndex + 1];
        return previousParagraph + nextParagraph;

    def _getKeywordParagraphs(self, keyword):
        paragraphs = [];
        subKeywords = keyword.strip().split();
        subKeywordCount = len(subKeywords);
        
        keywordIndices = self._findKeywords(subKeywords);

        for keywordIndex in keywordIndices:
            paragraphFirstIndex = keywordIndex - self.previousWordCount;
            if paragraphFirstIndex < 0:
                paragraphFirstIndex = 0;

            paragraphLastIndex = keywordIndex + subKeywordCount + self.nextWordCount - 1;
            if paragraphLastIndex >= self.documentWordCount:
                paragraphLastIndex = self.documentWordCount - 1;

            newParagraph = self._fetchParagraph(paragraphFirstIndex, paragraphLastIndex, keywordIndex);
            paragraphs.append(newParagraph);

        return paragraphs;

    def gatherFeedbackWords(self, keyword):
        paragraphs = self._getKeywordParagraphs(keyword);

        feedbackDict = {};
        for paragraph in paragraphs:
            for word in paragraph:
                wordPrimitive = self.wordPrimitiveDict[word];
                feedbackPair = (wordPrimitive, keyword);
                if feedbackPair in feedbackDict:
                    feedbackDict[feedbackPair] += 1;
                else:
                    feedbackDict[feedbackPair] = 1;

        return feedbackDict;

"""
    usage: python3 feedback.py [input_query_file_path] [output_feedback_file_path] [previous_word_count] [next_word_count] [distance_threshold]
"""

# parameter termURLPairs: [(term_1, URL_1), (term_2, URL_2), ...]
# parameter previousWordCount: A positive integer
# parameter nextWordCount: A positive integer
# parameter distanceThreshold: A positive integer
# return: ["feedback string 1", "feedback string 2", ...]
def getFeedbackTerms(termURLPairs, previousWordCount = 20, nextWordCount = 20, distanceThreshold = 3):
    allFeedbackDict = {};

    for (term, URL) in termURLPairs:
        print("Read webpage " + str(URL));
        webpageReader = WebpageReader(URL);
        content = webpageReader.readContent();

        print("Obtain feedback of the term \"" + str(term) + "\"");
        documentBrowser = DocumentBrowser(content, previousWordCount, nextWordCount, distanceThreshold);
        feedbackDict = documentBrowser.gatherFeedbackWords(term);

        for (term, count) in feedbackDict.items():
            if term in allFeedbackDict:
                allFeedbackDict[term] += count;
            else:
                allFeedbackDict[term] = count;
    
    return [term for (term, count) in sorted(allFeedbackDict.items(), reverse = True)];
