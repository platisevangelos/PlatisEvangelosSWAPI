#!/usr/bin/env python3

# must be installed: run requirements.txt
import requests
from datetime import datetime
# already installed with python as a default
import json, sys, os

# our search function with variable length of inputs
def search(*argv):
    # we fix a bit the inputs
    argv = list(argv)[0]
    # the first argument is the  search string
    input = str(argv[0])
    # the last argument is the long options parameter 
    # if no long option is passed then it is simply giberish and will have no effect
    w=str(argv[-1][2:])
    if w != "world":
        w = " "
    # this is the flag that indicates if we should sent a querry or not
    ask = True
    # this flag will become usefull in case we need to execute a querry
    # it will show if we found the desired person or not in the database
    found = False
    # we check if cache file exists and contains this search
    # if this is true, then we won't execute the querry
    cache = {}
    if os.path.exists(os.path.join(sys.path[0], "cache.json")):
        with open(os.path.join(sys.path[0], "cache.json"), 'r') as f:
            cache = json.load(f)
            if str(input+"."+w) in cache:
                ask = False
    if ask == False:
        # if it is cached, we can simply print fron the dictionary
        print(cache.get(str(input+"."+w)))
    else:
        # if it is not cached, we must execute a querry 
        resp = requests.get('https://swapi.dev/api/people/')
        # this is the buffer where the output will be saved
        out = []
        if resp.status_code == 200: # if the querry executted with no problems
            # the response of the querry in dictionary format is taken
            # the 'results' key contains a list of all the  people
            res = json.loads(resp.content)['results']
            # after itterating all the elements of the list
            for el in res:
                # we are looking for the one that contains part of the search string
                if input.lower() in el['name'].lower():
                    # we raise the flag
                    found = True
                    # and save the desired data
                    out.append("Name :" + el['name'])
                    out.append("\nHeight: " + el['height'])
                    out.append("\nMass: " + el['mass'])
                    out.append("\nBirth Year: " + el['birth_year'])
                    # if we also want information about the homeworld
                    if w =="world":
                        # lower the flag, we are not done yet
                        found =  False
                        out.append("\n\nHomeworld\n----------------\n")
                        # execute a second querry for the respective link
                        resp2 = requests.get(el['homeworld'])
                        # if and the second querry was succesfull
                        if resp2.status_code == 200:
                            # now we are ok, raise the flag again
                            found = True
                            # get the json content in dictionarry form
                            res2 = json.loads(resp2.content)
                            # and append the extra information
                            out.append("Name: " + res2['name'])
                            out.append("\nPopulation: " + res2['population'] + "\n")
                            # calculate the length of day and the length of the year on the planet surface
                            out.append("\nOn " + res2['name'] + ", 1 year on earth is " + str(round(int(res2['orbital_period'])/365,2)) + " years and 1 day is " + str(round(int(res2['rotation_period'])/24,2)) + " days.")
                    # since you found what you wanted, break the loop
                    break
        # if we  didn't find anything  during the querry
        if found == False: 
            out.append("The force is not strong within you")
        # make the output a one big string, then print it and cache it
        print(''.join(out))
        out.append("\n\n\n\ncached: " + str(datetime.now()))
        cache[str(input+"."+w)] = str(''.join(out))
        with open(os.path.join(sys.path[0], "./cache.json"), 'w+') as f:
            json.dump(cache, f)

# our cache function
def cache(*argv):
    # we fix a bit the inputs
    argv = list(argv)[0]
    # the first argument is the command
    input = str(argv[0][2:])
    # if we are asked to show the search history
    if input == "show":
        # we check if cache file exists
        # if this is true, we show each dictionary element
        cache = {}
        if os.path.exists(os.path.join(sys.path[0], "cache.json")):
            with open(os.path.join(sys.path[0], "cache.json"), 'r') as f:
                cache = json.load(f)
                # for each element in the cache
                for el in list(cache.keys()):
                    # split the key to get the search string and the long options of the search, that are seperated by '.'
                    buf = el.split('.')
                    print("===================================================================")
                    print("Search: " + buf[0] + "    parameters: " + buf[1])
                    print("\nResult:\n------\n" + cache.get(el))
                    print("===================================================================\n\n")
        else:
            # if there is no cache file
            print("The cache is empty")
    # if we are asked to clean the search history 
    elif input == "clean":
        # if the cache file exists, delete it
        if os.path.exists(os.path.join(sys.path[0], "cache.json")):
            os.remove(os.path.join(sys.path[0], "cache.json"))

# when the program is called parse the arguments/options and call the desired function
if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2:])


# disclaimer: I don't have experience with the os.getopt module, which is a better alternative for this case
