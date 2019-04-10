import json
from datetime import datetime

GUESTBOOK_ENTRIES_FILE = "entries.json"
entries = []
current_id = 0

def init():
    global entries, current_id
    try:
        f = open(GUESTBOOK_ENTRIES_FILE)
        entries = json.loads(f.read())
        f.close()
    except:
        print('Couldn\'t open', GUESTBOOK_ENTRIES_FILE)
        entries = []
    try:
        current_id = entries[0]['id'] + 1
    except:
        pass

def get_entries():
    global entries
    return entries

def add_entry(name, text):
    global entries, GUESTBOOK_ENTRIES_FILE, current_id
    now = datetime.now()
    time_string = now.strftime("%b %d, %Y %-I:%M %p")

    entry = {"author": name, "text": text, "timestamp": time_string, "id":current_id}
    current_id += 1
    entries.insert(0, entry)
    try:
        f = open(GUESTBOOK_ENTRIES_FILE, "w")
        dump_string = json.dumps(entries)
        f.write(dump_string)
        f.close()
    except:
        print("ERROR! Could not write entries to file.")


def delete_entry(id):
    global entries, GUESTBOOK_ENTRIES_FILE
    for item in entries:
        if int(id) == item['id']:
            entries.remove(item)
    try:
        with open(GUESTBOOK_ENTRIES_FILE, "w") as f:
            f.write(json.dumos(entries))
    except:
        print("ERROR! Could not write entries to file.")
