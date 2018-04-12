################################################################################
# Author: Lake Sain-Thomason
# Date: 4/2/2018
################################################################################
import urllib2
import json
from collections import OrderedDict
import time
import sys
import socket

_max_brightness_ = 254
################################################################################
#   Initialize and print requested state
################################################################################
def main():
    # Process user input
    if len(sys.argv) != 3:
        print "Usage: <IP Address> <Username>"
        return
    url = "http://" + sys.argv[1] + "/api/" + sys.argv[2]

    # Try to obtain full state from bridge
    try: contents = urllib2.urlopen(url, None, 3).read()  # Wait for response
    except urllib2.URLError as e:
        print e.reason
        return
    except socket.timeout:
        print "Did not recieve a response from the bridge, is the user name correct and whitelisted?"
        return

    json_contents = json.loads(contents)

    # Create list of dicts containing each light and necessary attributes
    dict_list = []
    for light in json_contents['lights']:
        data = OrderedDict()
        data['name'] = json_contents['lights'][light]['name']
        data['id'] = light
        data['on'] = json_contents['lights'][light]['state']['on']
        data['brightness'] = convert_to_percent(json_contents['lights'][light]['state']['bri'])
        dict_list.append(data)

    # Print ordered list of dicts formatted appropriately
    print json.dumps(dict_list, indent=2)
    print "\n"

################################################################################
#   Print changes in lights as they occur
################################################################################

    # Recurse until the program is terminated
    while True:
        old_json_contents = json_contents
        time.sleep(1)  # Phillips documentation reccomends no more than 10 operations per second
        contents = urllib2.urlopen(url).read()
        json_contents = json.loads(contents)

        # Iterate through available lights looking for changes
        for light in json_contents['lights']:
            state = json_contents['lights'][light]['state']
            # Avoid an out of bounds index error if a light is removed
            if len(json_contents['lights']) == len(old_json_contents['lights']):
                old_state = old_json_contents['lights'][light]['state']
                for attribute in state:
                    if state[attribute] != old_state[attribute]:
                        data = OrderedDict()
                        data['id'] = light
                        if attribute == "bri":
                            data["brightness"] = convert_to_percent(state[attribute])  # Adjust brightness as requested
                        else:
                            data[attribute] = state[attribute]
                        print json.dumps(data, indent=2)


# Convert brightness value to percent
def convert_to_percent(data):
    return int((float(data) / _max_brightness_) * 100)  # Max brightness is 254


main()
