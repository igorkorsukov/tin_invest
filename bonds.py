import argparse

import config as config
import modules.make_bonds_list2 as make_bonds_list
import modules.make_bonds_stat as make_bonds_stat
import modules.make_bonds_coupons as make_bonds_coupons

def main():
    parser = argparse.ArgumentParser(description='Tinkoff bonds')
    parser.add_argument('-l', '--list', action='store_true', help='Show bond list')
    parser.add_argument('-s', '--stat', action='store_true', help='Make bond stat')
    parser.add_argument('-c', '--coupons', action='store_true', help='Load bond coupons')
    args = parser.parse_args()

    if args.list:
        make_bonds_list.MakeList(config)
    elif args.stat:
        make_bonds_stat.MakeStats(config)
    elif args.coupons:
        make_bonds_coupons.MakeCoupons(config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()