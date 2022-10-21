from genericpath import isfile
from re import I, template
from TemplateParser import TemplateParser
from useful import UsefulTools
tools =UsefulTools()
import pandas as pd
import os
"""
Notes:
test1, stock name starts rght after a period. 
test2, stock name srats after percent on new line
test5, stock names start after % on new line
test6, doesn't end with xiao ji
test14, 
    IshareBonds1-3Treasury bonds. 
    This is an example where allowing for 4 jumps included something erroneous at the end. We can filter it out. 
test15, 
    has s1 within the name... many length 10s
test16, Lipper. example.
    needed to increase parenthesis density count...
    ETF 500 guy.
test17, 8.612022.8.31, 8.31 should still be counted as special character... fix by braodening definition of special chracter
test18, it ends with xiaoji, but there exists other parenthesis right after it. 
    possbile bug: after xiaoji, or after ending, there exists MANY parenthesis... for now, that is super rare. 
    we can simply cut out anything with xiaoji in it... 
test19 stock names start after a period on a new line... 

All files either end with ) or end with xiao ji... 

Algorithm:
1) find the number of stocks, by identifying the stock percentages. 
2) find all possible "wrapping combinations," 
in other words:
find all possible 'starting' indices (this is defined by the user, meaning, what do you define as special and 'worth' consideration?)
and all 'ending' indices which we only have 2: the ')' symbol, and the xiao ji symbol. 

Summary:
let's say we have a starting index, and the ending index... the issue is... we want within the starting and ending index a LOT 
of parenthesis. Therefore, essentially, we are trying to find the best starting/ending index, between which contains the MOST
ending parenthesis density. 

the following tests have similar names remaining:
test6
test11
test13

"""
np_dict = {"Fund_Name":[],"Stock_Name":[],"Fund_Percent":[]}
directory = r"C:\Users\research1\Desktop\AB"
for fileName in os.listdir(directory):
    #print(fileName)
    f = os.path.join(directory, fileName)
    if os.path.isfile(f):
        #print(f)
        template1Parser = TemplateParser(f)
        percent = template1Parser.findPercent()
        result = template1Parser.findStockSection3()
        if len(percent) - len(result) == 1:
            result.append(" ")
        np_dict["Fund_Percent"]+= percent
        np_dict["Stock_Name"] +=result
        for i in range(len(result)):
            np_dict["Fund_Name"].append(fileName[:-4])
output = pd.DataFrame(np_dict)
excelLocation = r"C:\Users\research1\Desktop\AB\新增資料夾\output.xlsx"
output.to_excel(excelLocation)
#print(output)
# print(f'len={len(result)},\n result={result}')
# print("len=",len(template1Parser.findPercent()),percent)
#print(template1Parser.findStockSection3())
#template1Parser.printText(withLines=True)

