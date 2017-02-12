import json



lst0 = json.load(open("topic_keys.json"))
lst1 = json.load(open("topic_keys_lift.json"))

for t in lst0[14][:2]:
    print([x for x, f in t.items()][:30])



print("-" * 200)

for t in lst1[14][0:2]:
    print(t)
