import json

file = open("Switches_json_output_examples.json")
output = json.load(file)
print(len(output))
print(output[0].keys())
print(output[0]["node_id"])
print(output[0]["info"].keys())
print(json.dumps(output[0]["info"]["tempStatus"]))
