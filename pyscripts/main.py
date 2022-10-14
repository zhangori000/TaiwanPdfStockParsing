
from TemplateParser import TemplateParser
template1Parser = Template1Parser('../pdfs/test1.pdf')
template1Parser.printText(withLines=True)
template1Parser.findStockSection2() # gets line by line stock section, as an array
