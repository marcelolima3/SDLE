import argparse, json


# Convert data to JSON
def __dataToJson(messages, following):
    data = {}
    data['messages'] = messages
    data['following'] = following
    return json.dumps(data)


# Convert JSON to data
def __JsonToData(string):
    data = json.loads(string)
    return (data['messages'], data['following'])


# Import data from file
def __importData(filename):
    try:
        with open(filename + '.json') as data_file:
            data = json.load(data_file)
            data_file.close()
            return data
    except Exception:
        pass


# Export data to file
def __exportData(data, filename):
    with open(filename + '.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)
    outfile.close()


# load all data from file
def read_data(db_file):
    data = __importData(db_file)
    if data:
        return __JsonToData(data)

    return ([], [])


# save all data to the file
def save_data(messages, following, db_file):
    data = __dataToJson(messages, following)
    __exportData(data, db_file)
