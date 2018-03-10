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
python challenge.py [<url_index>]

Example:
$ python challenge.py
or
$ python challenge.py 2
~~~~~~~~~~~~

Solution logic:
1. Request the API data and process it into one dictionary object.
2. Loop over all the menus to find which ones are parents (lack of "parent_id" key).
3. Using recursion, get the depth of the longest branch starting at a parent node, and get all its children.
4. Classify menus between "valid_menus" (parent is not in children and max depth is <= 4) and "invalid_menus".
"""

import sys

import requests

URL = {
    '1': 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1',
    '2': 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=2'
}


def get_api_data(url_index):
    """
    Fetches the API data from all the pages and processes it into a dictionary.

    :param str url_index: URL index
    :return list: List of all the menu dictionaries
    """

    page = 1
    menus = []

    while True:
        r = requests.get(URL[url_index] + f'&page={page}').json()
        if r.get('menus') == []:
            break
        else:
            menus += r['menus']
            page += 1

    return menus


def find_parents(menus):
    """
    Finds parent menus (menus with no "parent_id" key).

    :param list menus: List of menu dictionaries
    :return list: List of menu dictionaries that are parents
    """

    parents = []

    for menu in menus:
        parent = menu.get('parent_id')
        if parent is None:
            parents.append(menu)

    return parents


def get_children(menus, parents):
    """
    Finds all the children of parent menus.

    :param list menus: List of menu dictionaries
    :param list parents: List of parent menu dictionaries
    :return list: List of branches (parent menus with their children)
    """

    menus_dict = {menu['id']: menu for menu in menus} # Indexes the menus list to a dictionary with the IDs as keys to easily traverse it

    branches = []

    for parent in parents:
        max_depth, children = _get_max_depth(menus_dict, parent['id'], parent['child_ids'])

        branches.append({
            'root_id': parent['id'],
            'children': list(children),
            'max_depth': max_depth
        })

    return branches


def _get_max_depth(menus, parent, children):
    """
    Gets the maximum depth and list of children of a parent node recursively.

    :param dict menus: Dictionary of menu dictionaries
    :param int parent: ID of the parent menu (root of branch)
    :param list children: List of the IDs of all the children of the next node
    :return int: Maximum depth of a parent menu
    :return list: List of all children of the parent node
    """
    
    all_children = set()
    all_children.update(children)

    if children == []: # The case where we've reached a leaf
        return 0, all_children
    elif parent in children: # The case of a cyclical reference
        return 1, all_children
    else:
        depths = {}
        for child in children:
            depths[child], new_children = _get_max_depth(menus, parent, menus[child]['child_ids']) # Gets the depth of each child
            all_children.update(new_children)

        return max(depths.values()) + 1, all_children


def validate_menus(branches):
    """
    Validates parent menus as valid if there is no cyclical reference and if the maximum depth is at most 4.

    :param list branches: List of menu branches (parent menus with all their children)
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
        url_index = sys.argv[1] # Gets the url from the command line call
    except IndexError:
        url_index = '1' # If no url index is provided, uses url index 1

    try:
        menus = get_api_data(url_index)
    except KeyError:
        print('URL index can only be 1 or 2.')
        sys.exit()
    
    parents = find_parents(menus)
    branches = get_children(menus, parents)
    classification = validate_menus(branches)
    print(classification)

if __name__ == '__main__':
    main()
