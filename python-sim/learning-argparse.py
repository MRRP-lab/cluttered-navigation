import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--num", "-n", help="arbitrary integer value", type=int)
parser.add_argument("-b", "--flipbool", help="boolean: default false", action="store_true")

args = parser.parse_args()

print(args.num)
if (args.flipbool):
    print("tru!")
else:
    print("nada")

