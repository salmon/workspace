import difflib, os, sys

class SortDiff(object):
    def __init__(self):
        pass

    @staticmethod
    def sort_differ_buffers(result, origin_filename):
        if not os.path.isfile(origin_filename):
            return 0
        with open(origin_filename) as f:
            lines = f.readlines()
            lines.sort()
        result.sort()
        diff = difflib.context_diff(result, lines)
        if diff:
            sys.stderr.write()
            return 1
        return 0

    @staticmethod
    def filter(self):
        pass

if __name__ == "__main__":
    SortDiff.sort_differ_buffers()

