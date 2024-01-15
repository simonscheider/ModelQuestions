# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from lark import Lark, tree

l = Lark(r'''
    spexperiment: measure control ("in" spatialextent)? 
    measure : quantity | amount | concept       
    control : ("for" | "from" | "to" | "of") ("each")? concept (condition)* 
    amount : "amount of" (concept  | ("(")? spexperiment (")")?)        
    condition : spr onec | compr value 
    concept : onec | twoc
    onec : object | stuff | event | space | time
    twoc : onec "pair" 
    time : "time"
    space : "space" |"location" | "height"
    spr : "within" | "touching" | "away from"
    compr : "larger than" | "less than" | "equal to"
    value : STRING 
    quantity : (quantified | aggregated) amount
    quantified : intensive | extensive
    intensive :  "proportional" | "density of" | "normalized" 
    aggregated :  "average" | "maximal" | "minimal"
    extensive : "quantified" | STRING
    object : "place" | "building" | "city" | "neighborhood" | STRING
    stuff : "noise" | "temperature" | "green" | "landcover" | STRING
    event : "trip" | "period" | "earthquake" | STRING
    spatialextent : STRING
    

    %import common.ESCAPED_STRING -> STRING
    %import common.SIGNED_NUMBER 
    %import common.WS 
    %ignore WS
    ''', start='spexperiment')



print(l.parse('proportional amount of space of green for each neighborhood in "Amsterdam"').pretty())
print(l.parse('quantified amount of space of green for each neighborhood in "Amsterdam"').pretty())
print(l.parse('average amount of space for each place for each neighborhood in "Amsterdam"').pretty())
print(l.parse('average amount of quantified amount of height of building for each neighborhood in "Amsterdam"').pretty())
print(l.parse('average amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"').pretty())

#print(l.parse('quantified amount of green for each location in "Amsterdam"'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
