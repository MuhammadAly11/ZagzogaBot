#import "@preview/quizst:0.3.2": quiz
#let jsonpath = sys.inputs.jsonpath

#let json_data = json(jsonpath)

#show: quiz.with(
  highlight-answer: false,
  json-data: json_data,
)
