import json

def handle_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        else:
            result[key] = value
    return result

json_string = '{"1": "Advisory Class", "1": "Subject Class"}'

# Use json.loads with object_pairs_hook to handle duplicate keys
data = json.loads(json_string, object_pairs_hook=handle_duplicates)

print(data)
