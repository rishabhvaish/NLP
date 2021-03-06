"""Script to compute question embeddings for given questions."""

questions_file = "scratch/complexwebq_processed.json"
embeddings_file = "glove"
output_file = "scratch/complexwebq_embeddings.pkl"
dim = 300

import pickle as pkl
import numpy as np
import json
from tqdm import tqdm

word_to_question = {}
question_lens = {}
def _add_word(word, v):
    if word not in word_to_question: word_to_question[word] = []
    word_to_question[word].append(v)
    if v not in question_lens: question_lens[v] = 0
    question_lens[v] += 1

with open(questions_file) as f:
    questions = json.load(f)
    for ii, question in enumerate(questions):
        qId, question_text = question["QuestionId"], question["QuestionKeywords"]
        for word in question_text.split():
            _add_word(word, qId)

question_emb = {r: np.zeros((dim,)) for r in question_lens}
with open(embeddings_file, encoding="utf8") as f:
    for line in tqdm(f):
        values = line.strip().split()
        word = ''.join(values[:-dim])
        vec = np.asarray(values[-dim:], dtype='float32')
        # word, vec = line.strip().split(None, 1)
        if word in word_to_question:
            for qid in word_to_question[word]:
                # question_emb[qid] += np.array([float(vv) for vv in vec.split()])
                ### embedding of each question is the sum of embeddings of its individual word
                question_emb[qid] += vec

for question in question_emb:
    question_emb[question] = question_emb[question] / question_lens[question]
print(question_emb)
pkl.dump(question_emb, open(output_file, "wb"))
