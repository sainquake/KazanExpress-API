import json
import os
from datetime import datetime

def readData(name):
    if not os.path.isfile(name): 
        print("File path {} does not exist...".format(name))
        return None
    else:
        with open(name, 'r', encoding='utf8') as f: 
            j = json.load(f)
            f.close()
        return j
        
def writeData(name,data):
    if data!=None:
        if not os.path.isdir(name.split("/")[0]):
            os.mkdir(name.split("/")[0])
        with open(name, 'w', encoding='utf8') as outfile: 
            json.dump(data, outfile, indent=4, ensure_ascii=False)
            outfile.close()
    else:
        print(f'Data for {name} is none ')
        
def getNow():
    out = {}
    out['timestamp_ms'] = round(datetime.now().timestamp()*1000)
    out['redable'] = datetime.fromtimestamp(out['timestamp_ms']/1000).strftime("%Y-%m-%d %H:%M:%S")
    out['timestamp'] = round(datetime.now().timestamp())
    
    return out