
import pandas as pd
import PyPDF2
import collections
import heapq
from useful import UsefulTools

tools = UsefulTools() # global tools object. 

class TemplateParser:
    def __init__(self, fileName):
        pdfFileObj = open(fileName, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        self.allLines = pdfReader.pages[0].extractText().split('\n') # gets first page and splits by new line
        self.fullText = pdfReader.pages[0].extractText() # gets raw text. 
    def printText(self, withLines=False):
        if withLines:
            for index, line in enumerate(self.allLines):
                print(f'line={index} {line}')
            return
        print(self.fullText)


    def findStockSection(self):
        hintIdx = self.fullText.find('小計')
        i = hintIdx
        while i >= 0 and self.fullText[i] != '%':
            i -= 1
        print(self.fullText[i+2:hintIdx+2]) # + 2 due to the percent
        percentIdx = i # i now contains percentIdx (where the percent is)
        usefulStuff = self.fullText[i+2:hintIdx+2].split('\n')
        # self.getAllNumbers(splitted)


        # once we get all the characters, let's combine the parenthesis together. 
        characterLines = self.getAllCharacters(usefulStuff)
        mergedLines = self.mergeParenthesis(characterLines)
    def findStockSection2(self):
        # first find the leftmost window character
        i = 0 # search with index i
        possible = []
        while i < len(self.allLines):
            currentLine = self.allLines[i]

            if tools.isSpecial2(currentLine) or tools.isPercentAlone(currentLine) or "。" in currentLine:
                print(f'i found something! {i}, currentLine is {currentLine}')
                possible.append(i)
            if "。" in currentLine or currentLine[-1].isdigit():
                print(f'i found something! {i}, currentLine is {currentLine}')
                if i+1 < len(self.allLines):
                    possible.append(i+1)
            i += 1
        print(f'here are the possible index for left={possible}')
        sections = [] # add possbile stuff in here!
        for left in possible:
            right = left+1 # right represents current line index. 
            # begin sliding window 
            previous = left
            rightMostParen = -1
            while right < len(self.allLines):
                currentLine = self.allLines[right]
                # go character by character, count parenthesis, stop at ending parenthesis.
                # print(f'currentLine={currentLine}') 
                if "小計" in currentLine:
                    sections.append([left, right-1, len(self.allLines[right-1])])
                if "(" in currentLine or ")" in currentLine:
                    # print(f'left={left}, right={right}, previous={previous}')
                    if right - previous > 3:
                        # bad case
                        # print(f' left={left}, previous={previous}, i broke at right={right}')
                        sections.append([left, previous, rightMostParen])
                        break
                    previous = right # update previous. 
                    rightMostParen = currentLine.find(")")
                right += 1
            # edge case, we dont see paren anymore... 
            
            if right == len(self.allLines):
                print(f' left={left}, previous={previous}, i broke at right={right}')
                sections.append([left, previous, rightMostParen])

        print(sections)
        finalResults = []
        for section in sections:
            start, end, rightMostParen = section # extracts the 2 info in each array. [[start, end], [s2, e2]]
            
            desiredSection = self.allLines[start:end+1]
            fci = tools.skipFirstDecimal(desiredSection[0])
            decimalIdx = desiredSection[0].find("。")
            # BUG FIX THE DATE STUFF. TEST12.PDF
            desiredSection[0] = desiredSection[0][fci:]
            if decimalIdx != -1:
                desiredSection[0] = desiredSection[0][decimalIdx+1:]
            desiredSection[-1] = desiredSection[-1][:rightMostParen+1]

            finalResult= self.mergeParenthesis(desiredSection)
            finalResults.append(finalResult)
        
        for finalResult in finalResults:
            print(f'len(finalResult)={len(finalResult)} finalResult=')
            for f in finalResult:
                print(f' {f}')

    def findStockSection3(self):
        """
        endingIdx will traverse and act as an "explorer."
        1) endingIdx will go as far as possible, until the parenthesis gap is too big. We would of course, 
            keep track of the "last valid endingIdx." 
        2) it will also "collect seashells" for the startIdx, meaning, it will store a list of special characters
            that it "picks up".
        3) After endingIdx reaches the farthest point it can... and after it collects the valuable sea shells,
            then startingIdx will now examine each sea shell, and we will store these indices. 
            Therefore, afterwards, for each endingIdx, we have a collection of indicies as follows:
            [start1, end1], [start2, end1], [start3, end1], ...[seashells_n, end1]
        4) after startingIdx catches up to endingIdx, now we have "all possible indices ENDING at endingIdx"
        5) we can now find other endingIdx and follow the same logic of above,
            [start1, end2], [start2, end2], [start3, end2], ... [seashells_n, end2]
        """
        possible = []
        leftIdx = 0
        rightIdx = 0
        
        
        seashellBag = collections.deque([])
        endingDelimiters = [")", "小計"]
        
        newLineIdx = 0 # resets every \n
        newLineCount = 0 # counts number of \n we have encountered. Useful for parenthesis density.
        lastValidLine = 0 # last valid LINE -- useful for parenthesis density 
        lastValidIdx = 0 # last valid RIGHT INDEX
        while rightIdx < len(self.fullText):
            if self.fullText[rightIdx] == '\n':
                print(currLine)
                newLineCount += 1
                newLineIdx = rightIdx + 1
                rightIdx += 1
                continue
            currLine = self.fullText[newLineIdx:rightIdx+1] # substring from start of line to INCLUDING rightIdx
            prevCurrLine = self.fullText[newLineIdx:rightIdx]
            nextCurrLine = self.fullText[newLineIdx:rightIdx+2] if rightIdx < len(self.fullText) - 1 else ""
            slideWindow = False
            for endingDelimiter in endingDelimiters:
                if endingDelimiter in currLine and endingDelimiter not in prevCurrLine:
                    # we have a match of ending...
                    # however, check if parenthesis density is valid
                    if newLineCount - lastValidLine <= 3:
                        lastValidLine = newLineCount
                        lastValidIdx = rightIdx
                    else:
                        print(f' ending! newLineCount={newLineCount}, lastValidLine={lastValidLine}, seaShell={seashellBag}')
                        slideWindow = True
            while slideWindow and seashellBag:
                leftIdx = seashellBag[0]
                if leftIdx < lastValidIdx:
                    seashellBag.popleft() # leftIdx travel to next sea shell
                    possible.append([leftIdx, lastValidIdx]) # INCLUSIVE brackets [leftIdx, rightIdx] as opposed to (leftIdx, rightIdx)
                else:
                    break
            if slideWindow:
                lastValidLine = newLineCount
                lastValidIdx = rightIdx
            # collecting seashell logic
            rightMostChar = tools.isSpecial3(currLine)
            isNextAlsoSpecial = tools.isSpecial3(nextCurrLine)
            if rightMostChar >= 0 and isNextAlsoSpecial == -1:
                print(f' found!!={currLine} @ line={newLineCount}')
                if rightIdx+1 < len(self.fullText) and self.fullText[rightIdx+1] == '\n':
                    seashellBag.append(rightIdx+2)
                else:
                    seashellBag.append(rightIdx+1)
            # otherwise, none found. 

            
            rightIdx += 1
        print(f'possible={possible}')
        for left, right in possible:
            print(f'  maybe...\n{self.fullText[left:right+1]}')

    def getAllNumbers(self, usefulStuff):
        for stuff in usefulStuff:
            if tools.isFloat(stuff):
                print(stuff)

    def getAllCharacters(self, usefulStuff):
        # returns array of all characters, INCLUDING those which are garbled with a decimal in front
        result = []
        for line in usefulStuff:
            if tools.isFloat(line):
                # if the current line by itself is a decimal, then of course no characters are in here
                continue
            # if this line is reached, we have reached our first non-float. 
            firstNonDecimalIdx = tools.skipFirstDecimal(line)
            result.append(line[firstNonDecimalIdx:])
        return result

    def mergeParenthesis(self, lines):
        result = []
        sofar = []
        for line in lines:
            if "(" not in line and ")" not in line:
                # nothing here, just assume you can add
                result.append(line)
                sofar = [] # reset
                continue
            sofar.append(line)
            if sofar[-1][-1] == ")":
                combined = "".join(sofar)
                sofar = [] # reset
                if combined[0] == "(":
                    # this type of string cannot be alone, since it is just two parenthesis at the front and end
                    if result:
                        result[-1] += combined
                    continue
                else:
                    result.append(combined)
        return result
            

            
            


    


    
        