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
    condmodifier : "the closest" | "the smallest" | "this"
    control : (("for" | "from" | "to" | "of" | "between") ("each")? spexperiment) | condcontrol 
    condcontrol : spr onec | compr value | "with" optimal quantified simpleamount
    amount :  simpleamount  |  relamount 
    simpleamount : ("amount of")? ("(")? concept (")")?  
    relamount : ("amount of")? ("(")? spexperiment (")")?     
    concept : condmodifier? (onec | twoc)
    onec : object ("s")? | event ("s")? | stuff | space | time | onec "and" onec
    twoc : onec "pair" | "pair of" onec
    time : "time" | "travel time"
    space : "space" |"location" | "height" | "distance" | STRING
    spr : "within" | "touching" | "away from" | "west of" | STRING
    compr : "larger than" | "less than" | "equal to" | "changed to" | STRING   
    quantity : quantified simpleamount | aggregated relamount 
    quantified : intensive | extensive
    intensive :  "proportional" | "density of" ("the")? | "normalized" 
    optimal : "maximal" | "minimal"
    aggregated :  "averaged" |  optimal | "sum of" ("the")?
    extensive : "quantified" | "capacity of" ("the")? | "production of" ("the")?
    object : "lifestock" | "place" | "building" | "city" | "neighborhood" | "hospital" | "inhabitant" | "windmill" | "windfarm" | ("ethanol")? "consumer" | ("ethanol")? "producer" | "ambulance station" | "road intersection" | "language group" | "route" | STRING
    stuff :  "rain" | "air pressure" | "noise" | "temperature" | "green" | "landcover" | "health" |  "energy"| "ethanol" | "cost" | "tax" | STRING
    event : "trip" | "period" | "earthquake" | "road accident" | "event" | STRING
    spatialextent : STRING
    value : NUMBER unit | "infinite" unit | STRING  
    unit : "minutes" | "kilometers" | "meters" | "R/l" | "liters" 
    '''

questionGrammar =  spatialExperimentGrammar + r'''
    question :  (contemporary | prediction | retrodiction | projection | retrojection) ("?")?    
    factualcondition : spexperiment ("is"|"are"|"was"|"were"|"to be") ("such and such"| optimal | compr value| value | STRING)  contemporaryreference 
    counterfactualcondition : spexperiment ("was"|"were") ("such and such"| optimal | compr value| value | STRING) contemporaryreference 
    projectedcondition : spexperiment ("will be") ("such and such"| optimal | compr value | value | STRING) futurereference 
    statisticalmodel : spexperiment contemporaryreference
    transformationmodel : spexperiment contemporaryreference "given that" ("the")?  factualcondition
    contemporary : "What" ("is"|"are") ("the")? (statisticalmodel|transformationmodel) 
    prediction : "What" "will be" ("the")? spexperiment futurereference "given that" ("the")?  factualcondition 
    retrodiction : "What" "could have been" ("the")? spexperiment pastreference ("given that" | "causing") ("the")? factualcondition 
    projection : "What" "would be" ("the")? spexperiment futurereference ("if"|"when") ("the")? counterfactualcondition 
    retrojection : "What" "should be" ("the")? spexperiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
    contemporaryreference : ("starting")? ("now" | "currently" | "at present" | "from now on" | "at the end of the African humid period")
    pastreference : ("starting")? ("earlier" | "in the past" | NUMBER "years ago" | "last week")
    futurereference : ("starting")? ("in the future" | "later"   | "in 2030" | "tomorrow" | "from now on")
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
                make_png("ModelQuestions/parseTrees/"+str(get_variable_name(questions))+str(cnt) + ".png", parser, e)
                make_dot("ModelQuestions/parseTrees/"+str(get_variable_name(questions)) + str(cnt) + ".gv", parser, e)

l_spEx = Lark(spatialExperimentGrammar + footer
        ,parser='earley', start='spexperiment', strict =True, keep_all_tokens=True)

experiments = [
'proportional amount of space of green for each neighborhood in "Amsterdam"',
'quantified amount of space of green for each neighborhood in "Amsterdam"',
'averaged amount of (space of building) for each neighborhood in "Amsterdam"',
'averaged amount of quantified amount of height of building for each neighborhood in "Amsterdam"',
'averaged amount of (quantified amount of green for each location) for each neighborhood in "Amsterdam"',
'proportional amount of space of green west of "Ij" for each neighborhood in "Amsterdam"',
'quantified amount of building of height larger than 5 meters for each neighborhood in "Amsterdam"',
'quantified amount of time to hospital with minimal quantified amount of time from each building in "Rotterdam"',
'sum of amount of (energy for each windmill) for windfarm',
'location for each windmill of windfarm',
]

parsetrees(l_spEx,experiments)


l_questions = Lark(questionGrammar  + footer
        ,parser='earley', start='question', strict =True, keep_all_tokens=True)
questions =[
'What should be the location for each windmill of windfarm now so that the sum of amount of (energy for each windmill) for windfarm will be maximal in the future?',
'What would be the sum of the amount of (capacity of the amount of ethanol for each producer) for "Brazil" in 2030 if the proportional amount of (tax of amount of ethanol for each consumer) of "Brazil" was equal to 1.23 R/l from now on ?',
'What would be the averaged amount of (ethanol for each consumer) for "Brazil" in 2030 if the proportional amount of (tax of amount of ethanol for each consumer) of "Brazil" was equal to 1.23 R/l from now on?',
'What could have been the density of amount of lifestock for each location in "Sudan" 10.000 years ago given that the landcover for each location in "Sudan" was equal to "arid land" at the end of the African humid period?',
'What will be the sum of the amount of rain for each location in "Dortmund" tomorrow given that the air pressure and temperature for each location in "Germany" is such and such now?',
'What is the time to hospital with minimal quantified amount of time from each building in "Rotterdam" at present?',
'What is the proportional amount of space of green for each neighborhood in "Amsterdam" now?',
'What would be the proportional amount of space of green for each neighborhood in "Amsterdam" in the future if the quantified amount of building was such and such now?',
'What should be the proportional amount of space of green for each neighborhood in "Amsterdam" now such that the quantified amount of health for each inhabitant will be such and such in the future?',
'What is the closest ambulance station for each building in "Rotterdam" at present given that the location of each ambulance station is such and such now?',
'What will be the time from the closest ambulance station to each building in "Rotterdam" from now on given that the location of each ambulance station is such and such now?',
'What could have been the event for each road intersection pair in "Rotterdam" last week causing the travel time of this ambulance station to this road accident in "Rotterdam" to be 30 minutes now?',
'What could have been the route for each language group in "the Amazon" starting 15.000 years ago causing the location of language groups to be such and such at present?',
'What would be the sum of the production of ethanol for each producer in "Brazil" in 2030 if the proportional amount of tax for ethanol for each consumer in "Brazil" was equal to 1.23 R/l from now on',
'What would be the travel time from the closest ambulance station to each building in "Rotterdam" in the future if the travel time between this road intersection pair was infinite minutes from now on?',
'What should be the location of ambulance stations in "Rotterdam" now such that the travel time to each building from the closest ambulance station will be less than 14 minutes in the future?',
'What should be the location for each windmill of this windfarm now so that the sum of the amount of energy for each windmill of this windfarm will be maximal in the future?'
]


parsetrees(l_questions,questions)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

