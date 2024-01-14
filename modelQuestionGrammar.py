# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from lark import Lark, tree

l = Lark(r'''
    spexperiment: ("(")? measure ("for" | "from" | "to") ("each")? control ("in" spatialextent)? (")")?
    measure : (quantity | amount | concept) 
    control : concept (condition)* ("of" spexperiment)?
    amount : "amount of" concept ("with" quantity)*
    condition : spr onec | compr value 
    concept : onec | twoc
    onec : object | stuff | event | space | time
    twoc : onec "pair" 
    time : "time"
    space : ("space" |"location" | "height")
    spr : "within" | "touching" | "away from"
    compr : "larger than" | "less than" | "equal to"
    value : STRING 
    quantity : ("quantified" | "proportional") amount
    aggr : 
    object : "place" | "building" | "city" | "neighborhood"
    stuff : "noise" | "temperature" | "green" | "landcover"
    event : "trip" | "period" | "earthquake"
    spatialextent : placename
    placename : STRING

    %import common.ESCAPED_STRING -> STRING
    %import common.SIGNED_NUMBER 
    %import common.WS 
    %ignore WS
    ''', start='spexperiment')



print(l.parse('proportional amount of space for green of landcover for each location in "Amsterdam"').pretty())


#print(l.parse('quantified amount of green for each location in "Amsterdam"'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
