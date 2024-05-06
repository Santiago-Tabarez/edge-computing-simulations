from itertools import combinations, chain, permutations


class CombinationsAndPermutations:

    @staticmethod
    def all_combinations(iterable):
        s = list(iterable)
        return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))

    @staticmethod
    def all_permutations(iterable):
        s = list(iterable)
        return list(chain.from_iterable(permutations(s, r) for r in range(1, len(s) + 1)))

