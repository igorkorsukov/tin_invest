import argparse

import config as config
import modules.make_bonds_list as make_bonds_list
import modules.make_bonds_stat as make_bonds_stat

def main():
    parser = argparse.ArgumentParser(description='Tinkoff bonds')
    parser.add_argument('-l', '--list', action='store_true', help='Show bond list')
    parser.add_argument('-s', '--stat', action='store_true', help='Show bond stat')
    args = parser.parse_args()

    if args.list:
        make_bonds_list.MakeList()
    elif args.stat:
        make_bonds_stat.MakeStats(config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()