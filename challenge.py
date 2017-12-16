# -*- coding: utf-8 -*-

"""
Shopify Challenge for the Software Engineering Intern (Summer 2018) position in Montreal.
Candidate: Radu Raicea (www.raduraicea.com)

Challenge link: https://backend-challenge-summer-2018.herokuapp.com
~~~~~~~~~~~~

Dependencies:
- Python 3.6+ (for f-strings)
- requests

External libraries can be installed with: [sudo] pip3 install <library1_name> [<library2_name> ...]

This script is called with the following format:
python challenge.py [<url>]

Example:
$ python challenge.py
or
$ python challenge.py https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=2
~~~~~~~~~~~~

Solution logic:
1. Request the API data and process it into one dictionary object.
2. Loop over all the menus to find which ones are parents (lack of "parent_id" key).
3. Using a depth-first traversal algorithm on the parent nodes, create new menu dictionary objects
   matching the desired output format (containing the "root_id" and "children" keys).
4. Insert each new menu dictionary into "valid_menus" if the "root_id" value is not in the "children"
   list (no cyclical reference), and if the maximum depth is not greater than 4. Otherwise, insert
   it into "invalid_menus".

Note:
A single node (root node) is considered to have a depth of 0. A depth of 4 requires the path to have 5 nodes and 4 edges.
Depth 0: O
Depth 1: O--O
Depth 4: O--O--O--O--O
"""

import json
import sys

import requests

DEFAULT_URL = 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1'


def get_api_data(url):
    """
    Fetches the API data from all the pages and processes it into a dictionary.

    :param str url: URL like https://domain.com/challenges.json?id=1
    :return dict: Dictionary (with keys being the id of the menu) of all the menu dictionaries
    """

    page = 1
    menus = []

    while True:
        r = requests.get(url + f'&page={page}').json()
        if r['menus'] == []:
            break
        else:
            menus += r['menus']
            page += 1

    menus_dict = {menu['id']: menu for menu in menus} # The key to each menu is its id

    return menus_dict


def find_parents(menus):
    """
    Finds parent menus (menus with no "parent_id" key).

    :param dict menus: Dictionary of menu dictionaries
    :return list: List of dictionaries of menus that are parents
    """

    parents = []

    for menu in menus.values():
        parent = menu.get('parent_id')
        if parent is None:
            parents.append(menu)

    return parents


def get_children(menus, parents):
    """
    Uses a depth-first traversal algorithm to find all the children of parent menus.

    :param dict menus: Dictionary of menu dictionaries
    :param list parents: List of parent menu dictionaries
    :return list: List of branches (parent menus with their children)
    """

    branches = []

    for parent in parents:
        visited = set()
        stack = []
        stack.extend(parent['child_ids'])

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                not_visited_children = set(menus[node]['child_ids']) - visited
                stack.extend(not_visited_children)

        branches.append({
            'root_id': parent['id'],
            'children': list(visited),
            'max_depth': _get_max_depth(menus, parent['id'], parent['child_ids'])
        })

    return branches


def _get_max_depth(menus, parent, children):
    """
    Gets the maximum depth of a node recursively.

    :param dict menus: Dictionary of menu dictionaries
    :param int parent: ID of the parent menu
    :param list children: List of the IDs of all the children of the next node to compute the depth of
    :return int: Maximum depth of a parent menu
    """
    
    if children == []:
        return 0
    elif parent in children: # The case of a cyclical reference
        return 1
    else:
        depths = {}
        for child in children:
            depths[child] = _get_max_depth(menus, parent, menus[child]['child_ids']) # Gets the depth of each child

        return max(depths.values()) + 1


def validate_parents(branches):
    """
    Validates parent menus as valid if there is no cyclical reference and if the depth is at most 4.

    :param list branches: List of menu branches (parent menus with their children)
    :return dict: Dictionary with a list of valid menus and a list with invalid menus
    """
    
    classification = {
        'valid_menus': [],
        'invalid_menus': []
    }

    for branch in branches:
        if branch.pop('max_depth') <= 4 and branch['root_id'] not in branch['children']:
            classification['valid_menus'].append(branch)
        else:
            classification['invalid_menus'].append(branch)

    return classification


def main():
    try:
        url = sys.argv[1] # Gets the url from the command line call
    except IndexError:
        url = DEFAULT_URL # If no url is provided, uses the default url

    try:
        menus = get_api_data(url)
    except json.JSONDecodeError: # Raises an exception if the response from the url is not a JSON
        print('URL entered does not return a JSON object. Try https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1')
        sys.exit()


    parents = find_parents(menus)
    branches = get_children(menus, parents)
    classification = validate_parents(branches)
    print(classification)
    # print(f'{json.dumps(classification, sort_keys=True, indent=4)}\n')

if __name__ == '__main__':
    main()
