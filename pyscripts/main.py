
from TemplateParser import TemplateParser
"""
Notes:
test1, stock name starts rght after a period. 
test2, stock name srats after percent on new line
test5, stock names start after % on new line
test6, doesn't end with xiao ji
test19 stock names start after a period on a new line... 

All files either end with ) or end with xiao ji... 

Algorithm:
1) find the number of stocks, by identifying the stock percentages. 
2) find all possible "wrapping combinations," 
in other words:
find all possible 'starting' indices (this is defined by the user, meaning, what do you define as special and 'worth' consideration?)
and all 'ending' indices which we only have 2: the ')' symbol, and the xiao ji symbol. 

Catch:
let's say we have a starting index, and the ending index... the issue is... we want within the starting and ending index a LOT 
of parenthesis. Therefore, essentially, we are trying to find the best starting/ending index, between which contains the MOST
ending parenthesis density. 
"""
template1Parser = TemplateParser('../pdfs/test17.pdf')
template1Parser.printText(withLines=True)
template1Parser.findStockSection3() # gets line by line stock section, as an array

