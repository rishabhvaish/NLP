"""Script to read WebQuestionsSP json file and extract required fields.

Output will be a json list of questions with the following fields:
    - QuestionId
    - QuestionText (processed)
    - QuestionKeywords (after removing wh-words, stopwords)
    - OracleEntities (from annotations)
    - Answers -- List of dicts with fields "freebaseID" and "text"
"""

import json
import nltk
nltk.download('stopwords')
nltk.download("punkt")
import os
import io

from nltk.corpus import stopwords as SW

import sys

out_json = "scratch/complexwebq_processed.json"
in_files = ["complexwebq_train", "complexwebq_dev"]
topicEntityMidDict = json.load(open("scratch/webq_entityID.json", encoding="utf8"))
stopwords = set(SW.words("english"))
stopwords.add("'s")

def extract_keywords(text):
    """Remove wh-words and stop words from text."""
    return u" ".join([token for token in nltk.word_tokenize(text)
        if token not in stopwords and token.isalnum()])

def get_answers(question):
    """extract unique answers from question parses."""
    answers = set()
    ### add answers-answer_id and answers-answer
    for answer in question["answers"]:
        answers.add((answer["answer_id"], answer["answer"]))
    return answers

def get_TopicEntityMid(ID):
    topicEntityMid = topicEntityMidDict[ID]
    return topicEntityMid

def get_entities(ID, question):
    """extract oracle entities from question parses."""
    entities = set()
    topicEntityName = question["composition_answer"]
    topicEntityMid = get_TopicEntityMid(ID)
    entities.add((topicEntityMid, topicEntityName))
    return entities

def process_question(question):
    question = question.lower()
    return question

questions = []
for fil in in_files:
    data = json.load(open(fil, encoding="utf8"))
    for question in data:
        ID = question["webqsp_ID"]
        ### question["question"] is the NLQ, while machine_question is not
        processedQ = process_question(question["question"])
        q_obj = {
            "QuestionId": question["ID"],
            "WebQID": question["webqsp_ID"],
            "QuestionText": processedQ,
            "QuestionKeywords": extract_keywords(processedQ),
            "OracleEntities": [
                {"freebaseId": "<fb:" + entity[0] + ">", "text": entity[1]}
                for entity in get_entities(ID, question)
            ],
            "Answers": [
                {"freebaseId": "<fb:" + answer[0] + ">"
                 if answer[0].startswith("m.") or answer[0].startswith("g.") else answer[0],
                 "text": answer[1]}
                for answer in get_answers(question)
            ]
        }
        questions.append(q_obj)
print(len(questions))
json.dump(questions, open(out_json, "w"))
