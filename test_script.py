import os
from lark import Lark
from lark import tree

#grammar
footer = r'''
%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
'''

spatialExperimentGrammar = r'''
    spexperiment: measure (control)* ("in" spatialextent)?
    measure : quantity | amount | concept
    condmodifier : "the closest" | "the smallest" | "this" | "maximum" | "minimum"
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
    compr : "larger than" | "less than" | "equal to" | "changed to" | "below" | STRING
    quantity : quantified simpleamount | aggregated relamount
    quantified : intensive | extensive
    intensive :  "proportional" | "density of" ("the")? | "normalized"
    optimal : "maximal" | "minimal"
    aggregated :  "averaged" |  optimal | "sum of" ("the")?
    extensive : "quantified" | "capacity of" ("the")? | "production of" ("the")?
    object : "lifestock" | "place" | "building" | "city" | "neighborhood" | "hospital" | "inhabitant" | "windmill" | "windfarm" | ("ethanol")? "consumer" | ("ethanol")? "producer" | "ambulance station" | "road intersection" | "language group" | "route" | "sensor location"| "the world’s economy"|STRING
    stuff :  "rain" | "soil"| "water" | "air pressure" | "noise" | "temperature" | "green" | "landcover" | "health" |  "energy"| "ethanol" | "cost" | "tax" | "CO2 emissions" | "NO2" | "PM10" | "PM2.5" | "gas extraction" | "Texelhopper busstops" | "road speeds" | STRING
    event : "trip" | "period" | "earthquake" | "road accident" | "event" | STRING
    spatialextent : STRING
    value : NUMBER unit | "infinite" unit | STRING  | NUMBER | relativechange
    unit : "minutes" | "kilometers" | "meters" | "R/l" | "liters" | "C" | "µg/m³" |
    relativechange : ("increased"|"decreased"|"doubled"|"halved") ("by" NUMBER ("percent")?)?
    '''

questionGrammar = spatialExperimentGrammar + r'''
    question : (contemporary | prediction | retrodiction | projection | retrojection) ("?")?
    factualcondition : spexperiment ("is"|"are"|"was"|"were"|"to be"|"being") ("such and such"| optimal | compr value| value | STRING)  contemporaryreference
    counterfactualcondition : spexperiment ("was"|"were") ("such and such"| optimal | compr value| value | STRING) contemporaryreference
    projectedcondition : spexperiment ("will be"|"being") ("such and such"| optimal | compr value | value | STRING) futurereference
    statisticalmodel : spexperiment contemporaryreference
    transformationmodel : spexperiment contemporaryreference "given that" ("the")?  factualcondition
    contemporary : "What" ("is"|"are") ("the")? (statisticalmodel|transformationmodel)
    prediction : "What" "will be" ("the")? spexperiment futurereference "given that" ("the")?  factualcondition
    retrodiction : "What" "could have been" ("the")? spexperiment pastreference ("given that" | "causing") ("the")? factualcondition
    projection : "What" "would be" ("the")? spexperiment futurereference ("if"|"when") ("the")? counterfactualcondition
    retrojection : "What" "should" ("have")? ("be"|"been") ("the")? spexperiment contemporaryreference ("so"|"such") "that" ("the")? projectedcondition
    contemporaryreference : ("starting")? ("now" | "currently" | "at present" | "today" | "from now on" | "this summer" | "at the end of the African humid period")
    pastreference : ("starting")? ("earlier" | "in the past" | NUMBER "years ago" | "last week" | "yesterday")
    futurereference : ("starting")? ("in the future" | "later" | "in 2030" | "tomorrow" | "from now on" | "in 20 years" |"this summer")
    '''

#build parser
parser = Lark(questionGrammar + footer, parser='earley', start='question', keep_all_tokens=True)

#question
#question = 'What should be the amount of green for each neighborhood in "Amsterdam" now so that the proportional amount of NO2 will be below 20 µg/m³ this summer?'
#question = 'What would be the averaged amount of travel time between Texelhopper busstops in "Texel" in the future if the road speeds were increased by 20 percent today?'
question = 'What would be the proportional amount of earthquakes for each location in "Groningen" in 2030 if the amount of gas extraction were halved today?'

#parser
try:
    parsed_tree = parser.parse(question)
    print("\nParsed successfully Parse tree:\n")
    print(parsed_tree.pretty())
    output_folder = "parseTreesCasper"

    out_file = os.path.join(output_folder, "parse_tree.png")
    tree.pydot__tree_to_png(parsed_tree, out_file)

except Exception as e:
    print("\n Parsing failed.")
    print(e)
