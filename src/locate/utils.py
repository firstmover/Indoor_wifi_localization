import json

def str2dict(line):
    """
    convert raw string line of json sequence to dict
    """
    # maybe some encoding conflict
    return json.loads(line)

def dict2str(dct):
    """
    reverse conversion of str2dict
    """
    return json.dumps(dct)

def savedict(dct, outfile):
    """
    convert dct to json strind and append to file outfile
    """
    with open(outfile, "a") as o:
        o.write(json.dumps(dct) + '\n')
