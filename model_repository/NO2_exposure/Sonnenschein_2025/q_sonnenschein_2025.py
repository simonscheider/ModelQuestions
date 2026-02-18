from QuestionGrammar import QuestionGrammar

grammar = QuestionGrammar()

questions_tryout = [
    # 'What is that this person such that at this time is having diner for each person at this time'
    # "at this time is staying home or at this time is staying home",
    # "What is the maximum  value for each goal for each person at this timea,
    'What is the amount of PM for each time for each person in this interval of time in Rotterdam',
    'What is the averaged amount of PM for each person for this interval of time in Rotterdam',
    'What is the goal for each person at this time?',
    'What is the  route for each person from destination to home',
    'What is the averaged amount of PM for each person for this interval of time',
    'What is the sum of the amount of PM for each person for this interval of time in Rotterdam?',
    'What is the concentration of PM10 for each location for each time in Rotterdam?',
]
grammar.parsetrees(questions_tryout)