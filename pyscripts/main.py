from re import I, template
from TemplateParser import TemplateParser
from useful import UsefulTools
tools =UsefulTools()
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
template1Parser = TemplateParser(r"C:\Users\research1\Desktop\Orien Python\TaiwanPdfStockParsing\pdfs\test1.pdf")
#template1Parser.printText(withLines=True)

desiredLength = len(template1Parser.findPercent())
possibleNames = template1Parser.findStockSection3() # gets line by line stock section, as an array

desiredNames = []
for name in possibleNames:
    if len(name)== desiredLength:
        desiredNames.append(name)
        #possibleNames.remove(name)


possibleNames.clear()
if len(desiredNames)>1:#need a new criteria for identitfying the correct list of names
    i = 0

    for name in desiredNames:
        b= True
        for str in name:
            period = str.find(".")
            slash = str.find("/")

            if period>=0: #should take out numbers
                #desiredNames.remove(name) # idk why this isnt working
                b =False
                #print("I broke at this str", str)
                #print("I broke on this name", name)
                break
            if slash >= 0: #looking to take out dates
                if tools.isFloat(str[slash+1:slash+2]):
                    b=False
                    break
        if b:
            possibleNames.append(name)
        #print("i is ", i)
        i+=1
else:
    possibleNames.append(desiredNames[0])

print("START FROM HERE")
print(template1Parser.findPercent())
for result in possibleNames:
    print(f'len={len(result)},\n result={result}')
#print(desiredNames)
