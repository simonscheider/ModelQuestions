# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from lark import Lark, tree
from rich import print
import sys

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
    space : "space" |"location" | "height" | "distance" | STRING
    spr : "within" | "touching" | "away from" | "west of" | STRING
    compr : "larger than" | "less than" | "equal to" | STRING   
    quantity : quantified simpleamount | aggregated relamount 
    quantified : intensive | extensive
    intensive :  "proportional" | "density of" | "normalized" 
    optimal : "maximal" | "minimal"
    aggregated :  "averaged" |  optimal | "sum of" ("the")?
    extensive : "quantified" | "cost of" ("the")?
    object : "place" | "building" | "city" | "neighborhood" | "hospital" | "inhabitant" | "windmill" | "windfarm"| "consumer"| STRING
    stuff : "noise" | "temperature" | "green" | "landcover" | "health" |  "energy"| "ethanol"| STRING
    event : "trip" | "period" | "earthquake" | STRING
    spatialextent : STRING
    value : NUMBER STRING
    '''

questionGrammar =  spatialExperimentGrammar + r'''
    question :  (contemporaryinference | prediction | retrodiction | projection | retrojection) ("?")?    
    factualcondition : spexperiment contemporaryreference ("is"|"are") ("such and such"| "maximal" | "minimal" | compr value| STRING)
    counterfactualcondition : spexperiment contemporaryreference ("was"|"were") ("such and such"| "maximal" | "minimal" | compr value| STRING)
    projectedcondition : spexperiment futurereference ("will be") ("such and such"| "maximal" | "minimal" | compr value| STRING)
    statisticalmodel : spexperiment contemporaryreference
    transformationmodel : spexperiment contemporaryreference "given that" ("the")?  factualcondition
    contemporaryinference : "What" ("is"|"are") ("the")? (statisticalmodel|transformationmodel) 
    prediction : "What" "will be" ("the")? spexperiment futurereference "given that" ("the")?  factualcondition 
    retrodiction : "What" "could have been" ("the")? spexperiment pastreference "given that" ("the")? factualcondition 
    projection : "What" "would be" ("the")? spexperiment futurereference ("if"|"when") ("the")? counterfactualcondition 
    retrojection : "What" "should be" ("the")? spexperiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
    contemporaryreference : "now" | "currently" | "at present"
    pastreference : "earlier" | "in the past" 
    futurereference : "in the future" | "later"     
    '''


def make_png(filename,parser, sentence):
        tree.pydot__tree_to_png(parser.parse(sentence), filename)


def make_dot(filename,parser, sentence):
        tree.pydot__tree_to_dot(parser.parse(sentence), filename)

def get_variable_name(variable):
    for name in globals():
        if id(globals()[name]) == id(variable):
            return name
    for name in locals():
        if id(locals()[name]) == id(variable):
            return name
    return None
def parsetrees(parser, questions):
        cnt = 0
        for e in questions:
                cnt += 1
                print(parser.parse(e))
                make_png(str(get_variable_name(questions))+str(cnt) + ".png", parser, e)

l_spEx = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='spexperiment', strict =True, keep_all_tokens=True)

experiments = [
'proportional amount of space of green for each neighborhood in "Amsterdam"',
'quantified amount of space of green for each neighborhood in "Amsterdam"',
'averaged amount of space of building for each neighborhood in "Amsterdam"',
'averaged amount of quantified amount of height of building for each neighborhood in "Amsterdam"',
'averaged amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"',
'proportional amount of space of green west of "Ij" for each neighborhood in "Amsterdam"',
'quantified amount of building of height larger than 5 "m" for each neighborhood in "Amsterdam"',
'time to hospital with minimal quantified amount of time from each building in "Rotterdam"',
'sum of amount of (energy for each windmill) for windfarm',
'location for each windmill of windfarm'
]

parsetrees(l_spEx,experiments)


l_questions = Lark(questionGrammar  + footer
        ,parser='earley', start='question', strict =True, keep_all_tokens=True)
questions =[
'What should be the location for each windmill of windfarm now so that the sum of amount of (energy for each windmill) for windfarm in the future will be maximal?',
'What would be the sum of the amount of (ethanol for each consumer) for "Brazil" in the future if the cost of the amount of (ethanol for each consumer) for "Brazil" was equal to 1.23 R/l now?'

# print(l_questions.parse('What is the proportional amount of space of green for each neighborhood in "Amsterdam" now?'))
# print(l_questions.parse('What would be the proportional amount of space of green for each neighborhood in "Amsterdam" in the future if the quantified amount of building now was such and such?'))
# print(l_questions.parse('What should be the proportional amount of space of green for each neighborhood in "Amsterdam" now such that the quantified amount of health for each inhabitant in the future will be such and such?'))
]
#print(l.parse('quantified amount of green for each location in "Amsterdam"'))

parsetrees(l_questions,questions)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

