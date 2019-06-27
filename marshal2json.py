import sys, marshal
import json

output = []
counter = 0
try:
    with open("dblp.marshal", 'rb') as f:
        while True:
            try:
                info, value = marshal.load(f)

                if info[1][0] == 'article':
                    counter += 1
                    output.append(value)

                    if counter % 10000 == 0:
                        print(counter)
            except KeyError as e:
                print("KeyError", value, info)
            except EOFError as e:
                break
finally:
    print(counter)

with open('dblp.json', 'w') as f:
    json.dump(output, f, indent=2)