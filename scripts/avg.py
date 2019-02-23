#!/usr/bin/env python

import sys
from os import listdir


def proc_files(files):

    fs = []
    for f in files:
        try:
            fs.append(open(f, "r"))
        except Exception as exct:
            print("Failed to read file {:s}".format(f))
            sys.exit(1)

    done = False
    result = []
    while not done:

        index = "NONE"
        val_sum = 0

        for f in fs:
            try:
                line = f.__next__()
            except Exception:
                done = True
                break

            sline = line.split()

            assert(len(sline) == 2)

            index, value = sline
            value = float(value)

            val_sum += value

            # print(sline)

        else:
            val_avg = val_sum/len(fs)
            result.append("{:s}\t{:f}".format(index, val_avg))

    result.append("")
    return result


def proc_dirs(dirs):

    first_dir = dirs[0]

    for f in listdir(first_dir):
        avg_out = proc_files(["{:s}/{:s}".format(d, f) for d in dirs])

        with open(f, "w") as outfile:
            outfile.write("\n".join(avg_out))


def main():

    proc_dirs(sys.argv[1:])

    # proc_files(sys.argv[1:])


if __name__ == "__main__":
    main()
