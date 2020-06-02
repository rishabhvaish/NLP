import json

in_files = ["downloads/WebQSP/data/WebQSP.train.json", "downloads/WebQSP/data/WebQSP.test.json"]
out_json = "scratch/webq_entityID.json"

topicEntityMidDict = {}
for fil in in_files:
    data = json.load(open(fil, encoding="utf8"))
    for question in data["Questions"]:
        ID = question["QuestionId"]
        for parse in question["Parses"]:
            topicEntityMidDict[ID] = parse["TopicEntityMid"]
json.dump(topicEntityMidDict, open(out_json, "w"))