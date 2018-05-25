import argparse, json

# Messages example
messages = [
    {'id': 'tone', 'message': 'olá mundo'},
    {'id': 'zé', 'message': '😁'},
    {'id': 'manel', 'message': 'adeus mundo!'}
]

# Following example
following = [{'id': 'antonio', 'ip': '192.168.1.69'}]

# Convert data to JSON
def dataToJson(messages, following):
    data = {}
    data['messages'] = messages
    data['following'] = following
    return json.dumps(data)

# Convert JSON to data
def JsonToData(string):
    data = json.loads(string)
    return (data['messages'], data['following'])   

# Import data from file 
def importData(filename):
    with open(f'{filename}.json') as data_file:    
        return json.load(data_file)

# Export data to file  
def exportData(data, filename):
    with open(f'{filename}.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)


if __name__== "__main__":
    parser = argparse.ArgumentParser(prog='local_storage')
    parser.add_argument('-u','--username', help = 'Your username', required = True)

    args = parser.parse_args()

    json_data = dataToJson(messages, following)
    exportData(json_data, args.username)

    data = importData(args.username)
    result_msg, result_following = JsonToData(data)

    for i in result_msg:
        print(i)

    for i in result_following:
        print(i)