import os
from itertools import chain, combinations

import yaml


class YAMLDataReader:

    # all_permutation([0,1,2]) --> () (0,) (1,) (2,) (0,1) (0,2) (1,2) (0,1,2)
    # TODO This should be somewhere else
    @staticmethod
    def all_permutations(iterable):
        s = list(iterable)
        return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))

    @staticmethod
    def read_yaml_files(folder_path):
        yaml_files = [f for f in os.listdir(folder_path) if f.endswith('.yaml') or f.endswith('.yml')]
        data_list = []

        for file in yaml_files:
            with open(os.path.join(folder_path, file), 'r') as stream:
                try:
                    data = yaml.safe_load(stream)
                    data_list.append(data)
                except yaml.YAMLError as exc:
                    print(f"Error in processing file {file}: {exc}")

        return data_list















# This function returns the permutations, including which players are real time players
# players_number = total amount of players
# number_of_rt_players = real time players, this kind of player have bigger utility
# if number_of_rt_players equals None then half of players are rt players
"""
    def feasible_permutations(players_number, number_of_rt_players):
    set_players = []

    if number_of_rt_players is None:
        # one half rt and the other half nrt
        number_of_rt_players = round((players_number - 1) / 2)
    # assign type to players
    for i in range(players_number):
        # valid only for SPs
        # SPs NRT
        if i != 0 and number_of_rt_players > 0:
            set_players.append((i, "rt"))
            number_of_rt_players -= 1
        # SPs NRT
        elif i != 0:
            set_players.append((i, "nrt"))
        # NO
        else:
            set_players.append((i, "NO"))

    perms = _all_permutations(set_players)

    return perms
"""