"""Script to process STAGG links into format for retrieving subgraphs.

Filters any non-top entity which has overlapping span with a higher ranked
entity and any non-top entity which has score lower than MIN_SCORE.
"""

questions_file = "scratch/complexwebq_processed.json"
link_files = ["train_links_raw", "test_links_raw"]
entity_file = "freebase_2hops/all_entities"
output = "scratch/stagg_linked_questions_complexwebQ.txt"

MIN_SCORE = 10.

import json
from tqdm import tqdm

def _convert_freebase_id(x):
    return "<fb:" + x[1:].replace("/", ".") + ">"

def _overlap(span, spans):
    for sp in spans:
        if max(sp[0], span[0]) < min(sp[1], span[1]):
            return True
    return False

def _filter_links(links):
    f_links = [links[0][:2]]
    spans_covered = [links[0][2:]]
    for item in links[1:]:
        if float(item[1]) < MIN_SCORE: continue
        if _overlap(item[2:], spans_covered): continue
        f_links.append(item[:2])
        spans_covered.append(item[2:])
    return f_links

def find_all_qID(webQID):
    return [k for k, v in question_ids.items() if v == webQID]

entities = set()
with open(entity_file) as f:
    for line in tqdm(f):
        entities.add(line.strip())

question_ids = {}
with open(questions_file) as f:
    all_questions = json.load(f)
    for q in all_questions:
        question_ids[q["QuestionId"]] = q["WebQID"]

entity_map = {qID: [] for qID in question_ids}
f_out = open(output, "w")
for fil in link_files:
    with open(fil) as f:
        for line in f:
            (webQID, surface, start,
             length, fId, fsurface, score) = line.strip().split("\t")
            if _convert_freebase_id(fId) not in entities: continue
            qIDList = find_all_qID(webQID)
            for qID in qIDList:
                if qID in entity_map:
                    entity_map[qID].append([fId, score, start, start + length])
print(entity_map)

with open(output, "w") as f_out:
    for (qID, links) in entity_map.items():
        webQID = question_ids[qID]
        if not links:
            f_out.write("%s\t%s\t\n" % (qID, webQID))
            continue
        link_str = ",".join(
            "%s=%s" % (_convert_freebase_id(fId), score)
            for fId, score in _filter_links(links))
        f_out.write("%s\t%s\t%s\n" % (qID, webQID, link_str))
