from dateutil.parser import parse

import string
class UsefulTools:
    def isFloat(self, element):
        try:
            float(element)
            return True
        except ValueError:
            return False
    def skipFirstDecimal(self, str):
        # takes a str, and gives you the index of first non decimal character
        end = 0
        while end < len(str) and self.isFloat(str[:end+1]):
            end += 1
        return end
    def isSpecial2(self, str):
        # check if decimal exists in there, and if date exists int here. 
        if self.isFloat(str):
            return False
        for i in range(1, len(str)):
            part1 = str[:i]
            if self.isFloat(part1) or self.is_date(part1):
                return True
        return False
    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try: 
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False


    def isSpecial(self, str):
        if self.isFloat(str):
            return False
        # to make it simple, 
        idxOfFirstDecimal = str.find('.') # -1 if not found
        # if never find decimal, quit
        if idxOfFirstDecimal == -1:
            return False
        isFirstFloat = self.isFloat(str[:idxOfFirstDecimal+3]) # 2 sig figs. 
        if not isFirstFloat:
            # if first charactes are not float, quit. 
            return False
        if len(str[idxOfFirstDecimal+3:]) > 4:
            # edge case for percents 12.34%
            return True
        return False
    def isPercentAlone(self, str):
        if len(str) == 1 and str[0] == '%':
            return True
        
    