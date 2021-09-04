import search

import sys
from pprint import pprint

from copy import deepcopy


class hashabledict(dict):
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __lt__(self, other):
        s = len([start for start, _ in self.values() if start is None])
        o = len([start for start, _ in self.values() if start is None])
        return s > o


class PDMAProblem(search.Problem):
    def __init__(self, initial={}):
        self.initial = initial

    def actions(self, state):
        closed = [
            (start, length) for start, length in state.values() if start is not None
        ]
        open = {k: v for k, v in state.items() if v[0] is None}

        ss = set(range(0, 64))
        original = deepcopy(ss)
        for start, length in closed:
            ss = ss - set(range(start, start + length))

        actions_list = []
        for var, x in open.items():
            _, length = x

            for s in ss:
                if s + length > 64:
                    continue
                if len((original - ss).intersection(set(range(s, s + length)))) != 0:
                    continue
                actions_list.append((var, s))

        pprint(state)
        pprint(actions_list)
        return actions_list

    def result(self, state, action):
        # print(action)
        var, start = action
        _, length = state[var]
        state = deepcopy(state)
        state[var] = (start, length)
        return state

    def goal_test(self, state):
        return len([start for start, _ in state.values() if start is None]) == 0

    def path_cost(self, c, state1, action, state2):
        var, start = action
        _, length = state1[var]
        return c + length

    def heuristic(self, node):
        state = node.state
        # alignment = [0,8,16,24,32,40,48,56]
        alignment = [0, 16, 32, 48]
        s = 0

        closed = [s for s in state.values() if s[0] is not None]
        open = [s for s in state.values() if s[0] is None]

        for x in closed:
            start, _ = x
            diffs = [abs(start - align) for align in alignment]
            m = min(diffs)
            # alignment.pop(diffs.index(m))
            s += m

        starts = [start for start, _ in closed]
        s -= 16 if starts == sorted(starts) else 0

        s += sum([length for _, length in open])

        return s

    def search(self):
        return search.astar_search(self, self.heuristic)


def main():
    problem = PDMAProblem(
        hashabledict(
            {
                "a": (0, 8),
                "b": (None, 8),
                "c": (16, 8),
                "d": (None, 8),
                "e": (None, 8),
                "f": (None, 8),
                "g": (None, 8),
                "h": (None, 8),
            }
        )
    )
    # problem = PDMAProblem(
    #    hashabledict({
    #        'a': (None, 16),
    #        'b': (None, 16),
    #        'c': (None, 16),
    #        'd': (None, 16),
    #    })
    # )

    result = problem.search()
    print(result)
    print(problem)


if __name__ == "__main__":
    main()
