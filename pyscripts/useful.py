

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
    def findEndDecimal(self,str):
        # takes a str, and gives you the index of a decimal added at the end
        end = 0
        while end < len(str) and not self.isFloat(str[end:]):
            end += 1
        return end
    def isSpecial3(self, str):
        """
        finds the RIGHT-MOST special characters (user defined) and return index. 
        If doesn't exist return -1

        What is a special character?
        1) anything with % or 。
        2) if there exists a float AND characters
        3) dates... 
        """
        if self.isFloat(str):
            return False # Why is this false here?
        specialCharacters = ["%", "。"]
        # by the time we get here, it is guaranteed str is not just a number thanks to above if check

        # goal here is to update rightMostChar when possible. 
        # if str and (self.isFloat(str) or self.is_date(str) or str[-1] in specialCharacters):
        #     return len(str)
        """
        can optimize this.. since we are only accesing last element of string, we don't need to store whole string. 
        """
        if str and (str[-1].isdigit() or str[-1] in specialCharacters):
            return len(str)
        return -1
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
        
    






