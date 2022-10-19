
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
                #print(f' left={left}, previous={previous}, i broke at right={right}')
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
    def findPercent(self):
        i=0
        #selectionOfSelection = []
        while i < len(self.allLines):
            currentLine = self.allLines[i]
            if tools.isFloat(currentLine):
                selection = []
                left = i
                #print("left is", left)
                selection.append(self.allLines[left])
                right = i+1
                while tools.isFloat(self.allLines[right]) and right<len(self.allLines):
                    selection.append(self.allLines[right])
                    right+=1
            
                if left-1 >= 0: #check if first line has one more digit
                    quickCheck = self.allLines[left - 1]
                    if tools.findEndDecimal(quickCheck)<len(quickCheck):
                        addedStr = quickCheck[tools.findEndDecimal(quickCheck):]
                        if tools.isFloat(addedStr) and "." in addedStr:
                            selection.insert(0,addedStr)
                if right <len(self.allLines): #check if next line has one more digit
                    quickCheck = self.allLines[right]
                    #print(quickCheck)
                    if tools.skipFirstDecimal(quickCheck)>0:
                        #print("here")
                        #right+=1
                        addedStr = quickCheck[:tools.skipFirstDecimal(quickCheck)]
                        #print("here", quickCheck[tools.skipFirstDecimal(quickCheck)-1])
                        if tools.isFloat(addedStr) and "." in addedStr and quickCheck[tools.skipFirstDecimal(quickCheck)-1] is not " ":
                            selection.append(addedStr)
                            
                            #need to do a quick check if there is a total line or other funds line to remove
                            if len(selection) > 2:
                                if float(selection[-1])> float(selection[-2]):
                                    selection.pop()
                                elif "現金及其他" in self.fullText:
                                    selection.pop()

                            
                            return selection
                i = right
                # selectionOfSelection.append(selection)
                # print("this is selctions ", selection)
                # print(selectionOfSelection)
                
            else:
                i+=1
        return []

    def findStockSection3(self):
        """
        rightIdx will traverse and act as an "explorer."
        1)  rightIdx will go as far as possible, until the parenthesis gap is too big. We would of course, 
            keep track of the "last valid rightIdx." Right when we realize the gap is too big, we ask,
            "hey what's the last valid ending we've seen, cuz obviously this current ending sucks
        2)  it will also "collect seashells" for the leftIdx, meaning, as rightIdx moves forward,
            it will store a list of special characters in a double ended queue (deque) that it "picks up".
        3)  After rightIdx reaches the farthest point it can... and after it collects the valuable sea shells,
            then leftIdx will now examine each sea shell, and we will store these indices. 
            Therefore, afterwards, for each rightIdx, we have a collection of indicies as follows:
            [start1, end1], [start2, end1], [start3, end1], ...[seashells_n, end1]
        4)  after leftIdx "catches up" to rightIdx, now we have "all possible indices *ENDING* at rightIdx"
        5)  we can now find keep moving rightIdx and follow the same logic of above,
            [start1, end2], [start2, end2], [start3, end2], ... [seashells_n, end2]
        """
        possible = []
        leftIdx = 0
        rightIdx = 0
        
        
        seashellBag = collections.deque([])
        endingDelimiters = [")", "小計"] # from the patterns, these represent possible endings. 
        
        newLineIdx = 0 # resets every \n so we can grab LINE by LINE. 
        newLineCount = 0 # counts number of \n we have encountered. Useful for parenthesis density.
        lastValidLine = 0 # last valid LINE -- useful for parenthesis density 
        lastValidIdx = 0 # last valid RIGHT INDEX
        while rightIdx < len(self.fullText):
            if self.fullText[rightIdx] == '\n':
                newLineCount += 1 # number of lines increase
                newLineIdx = rightIdx + 1 # new line will start at this index currLine = [newLineIdx: end]
                rightIdx += 1 # increase rightIdx and continue
                continue
            prevCurrLine = self.fullText[newLineIdx:rightIdx]
            currLine = self.fullText[newLineIdx:rightIdx+1] # substring from start of line to INCLUDING rightIdx
            nextCurrLine = self.fullText[newLineIdx:rightIdx+2] if rightIdx < len(self.fullText) - 1 else ""
            """
            prevCurrLine represents previous state. In future improvements, we can memoize this. 
            nextCurrLine represents next state. 
            ex: hihihihi)6.12345
            RightIdx logic:
                Think about it... if the PREVIOUS state does NOT contain the ending demiliter,
                and the CURRENT state DOES contain the ending delimiter, then the current rightIdx, is a stopping point.
                If we did NOT have this weird if check, then our code would render something like this:
                "hihihi)" <- valid
                "hihihi)6" <- valid
                "hihihi)6." <- valid
                "hihihi)6.1" <- valid
                .. so on. Even though we only want the first "hihihi)" to be valid ending delimiter. 
            """
            slideWindow = False
            for endingDelimiter in endingDelimiters:
                if endingDelimiter in currLine and endingDelimiter not in prevCurrLine:
                    # we have a match of ending...
                    # however, check if parenthesis density is valid
                    if newLineCount - lastValidLine <= 4:
                        # last seen parenthesis is less than 3 jumps away, not that bad. 
                        lastValidLine = newLineCount
                        lastValidIdx = rightIdx
                    else:
                        # invalid. Start sliding left pointer with the next while loop. 
                        #print(f' ending! newLineCount={newLineCount}, lastValidLine={lastValidLine}, seaShell={seashellBag}')
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
            """
            leftIdx Logic:
                6.1234 is special... but so is 6.12345, and so is 6.123456.... 
                We want the RIGHT most special character
            """
            if rightMostChar >= 0 and isNextAlsoSpecial == -1:
                # print(f' found!!={currLine} @ line={newLineCount}')
                if rightIdx+1 < len(self.fullText) and self.fullText[rightIdx+1] == '\n':
                    seashellBag.append(rightIdx+2)
                else:
                    seashellBag.append(rightIdx+1)
            # otherwise, none found. 

            
            rightIdx += 1
        # edge case: if rightIdx reaches the end, but we have "pending" possibilities in seaShells, then process the remaining.
        while seashellBag:
            leftIdx = seashellBag[0]
            if leftIdx < lastValidIdx:
                seashellBag.popleft() # leftIdx travel to next sea shell
                possible.append([leftIdx, lastValidIdx]) # INCLUSIVE brackets [leftIdx, rightIdx] as opposed to (leftIdx, rightIdx)
            else:
                break
        whatIwant =[]#sam edit
        #print(f'possible={possible}')
        for left, right in possible:
            # clean up now. 
            result = self.fullText[left:right+1].split('\n')
            cutOff = len(result)
            # cut off any with xiao ji
            for i in range(len(result)-1, -1, -1):
                if "小計" in result[i]: # note. this should temrinate immediately.  impelemtn later. 
                    cutOff = min(cutOff, i)
            result = result[:cutOff]
            # if this truly ended with xiao ji, then the next parenthesis logic shouldn't even matter.. 


            # clean up periods and invalid characters.. 
            nextParenthesis = len(result)-1
            for i in range(len(result)-1, -1, -1):
                if ")" in result[i] and nextParenthesis == -1:
                    nextParenthesis = i
                if "。" in result[i]:
                    nextsParenthesis = -1
            if nextParenthesis < len(result)-1:
                where = result[nextParenthesis].find(')')
                result = result[:nextParenthesis+1]
                if result:
                    result[-1] = result[-1][:where+1]
            result = self.mergeParenthesis(result)
            #print(f'len={len(result)},\n result={result}')
            whatIwant.append(result) #sam edit

        return whatIwant #sam edit
            

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
                # nothing here, just *assume* you can add, we will fix later. 
                result.append(line)
                sofar = [] # reset the aggregate result
                continue
            sofar.append(line) # always by default aggregate lines. 
            """
            if this line is reached, it means that there EXISTS a "(" in the string or ")" in the string. 
            """
            if sofar[-1][-1] == ")":
                """
                this if statement represents a fundamental assumption that the stock parenthesis always ends at the end...
                I doubt we will see a "(hi hi hi hi) oh hi" but only "(hi hi hi hi)" or "hihihihi )"
                """
                combined = "".join(sofar)
                # KEEP IN MIND, the variable "combined" can *span multiple lines... so combined[0] could represent lines ABOVE*
                sofar = [] # reset
                if combined[0] == "(":
                    # this type of string *cannot* be alone, since it is just two parenthesis at the front and end
                    if result:
                        result[-1] += combined 
                        # add the parenthesis to its "parent" if possible. 
                    continue
                else:
                    """
                    we clearly have an ending parenthesis, so where is the opening parenthesis? Not in the beginning!... 
                    So obviously somewhere in between.
                    """
                    result.append(combined)
        return result
