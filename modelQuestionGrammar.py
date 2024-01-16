# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from lark import Lark, tree
from rich import print

#Grammars:
footer= r'''

        %import common.ESCAPED_STRING -> STRING
        %import common.SIGNED_NUMBER -> NUMBER
        %import common.WS 
        %ignore WS
'''
spatialExperimentGrammar = r'''    
    spexperiment: measure (control)* ("in" spatialextent)? 
    measure : quantity | amount | concept  
    control : (("for" | "from" | "to" | "of") ("each")? spexperiment) | condcontrol 
    condcontrol : spr onec | compr value | "with" optimal quantified simpleamount
    amount :  simpleamount  |  relamount 
    simpleamount : "amount of" concept
    relamount : "amount of" ("(")? spexperiment (")")?     
    concept : onec | twoc
    onec : object | event | stuff | space | time
    twoc : onec "pair" 
    time : "time"
    space : "space" |"location" | "height" | "distance"
    spr : "within" | "touching" | "away from" | "west of"
    compr : "larger than" | "less than" | "equal to"    
    quantity : quantified simpleamount | aggregated relamount
    quantified : intensive | extensive
    intensive :  "proportional" | "density of" | "normalized" 
    optimal : "maximal" | "minimal"
    aggregated :  "averaged" |  optimal
    extensive : "quantified" 
    object : "place" | "building" | "city" | "neighborhood" | "hospital" | "inhabitant"| STRING
    stuff : "noise" | "temperature" | "green" | "landcover" | "health" | STRING
    event : "trip" | "period" | "earthquake" | STRING
    spatialextent : STRING
    value : NUMBER STRING
    '''

questionGrammar =  spatialExperimentGrammar + r'''
    question :  (contemporaryinference | prediction | retrodiction | projection | retrojection) ("?")?    
    factualcondition : spexperiment contemporaryreference ("is"|"are") ("such and such"|STRING)
    counterfactualcondition : spexperiment contemporaryreference ("was"|"were") ("such and such"|STRING)
    projectedcondition : spexperiment futurereference ("will be") ("such and such"|STRING)
    contemporaryinference : "What" ("is"|"are") ("the")? spexperiment contemporaryreference ("given that" ("the")?  factualcondition)?
    prediction : "What" "will be" ("the")? spexperiment futurereference "given that" ("the")?  factualcondition 
    retrodiction : "What" "could have been" ("the")? spexperiment pastreference "given that" ("the")? factualcondition 
    projection : "What" "would be" ("the")? spexperiment futurereference ("if"|"when") ("the")? counterfactualcondition 
    retrojection : "What" "should be" ("the")? spexperiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
    contemporaryreference : "now" | "currently" | "at present"
    pastreference : "earlier" | "in the past" 
    futurereference : "in the future" | "later"     
    '''

l_spEx = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='spexperiment', strict =True, keep_all_tokens=True)
print(l_spEx.parse('proportional amount of space of green for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('quantified amount of space of green for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('averaged amount of space of building for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('averaged amount of quantified amount of height of building for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('averaged amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('proportional amount of space of green west of "Ij" for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('quantified amount of building of height larger than 5 "m" for each neighborhood in "Amsterdam"'))
print(l_spEx.parse('time to hospital with minimal quantified amount of distance from each building in "Amsterdam"'))

l_questions = Lark(questionGrammar  + footer
        ,parser='earley', start='question', strict =True, keep_all_tokens=True)

print(l_questions.parse('What is the proportional amount of space of green for each neighborhood in "Amsterdam" now?'))
print(l_questions.parse('What would be the proportional amount of space of green for each neighborhood in "Amsterdam" in the future if the quantified amount of building now was such and such?'))
print(l_questions.parse('What should be the proportional amount of space of green for each neighborhood in "Amsterdam" now such that the quantified amount of health for each inhabitant in the future will be such and such?'))

#print(l.parse('quantified amount of green for each location in "Amsterdam"'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
