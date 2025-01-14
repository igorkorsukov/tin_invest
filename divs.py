import argparse

import divs_config as config
import modules.make_divs_stat as make_divs_stat

def main():
    parser = argparse.ArgumentParser(description='divs')
    parser.add_argument('-s', '--stat', action='store_true', help='Make divs stat')

    args = parser.parse_args()

    if args.stat:
        make_divs_stat.MakeStats(config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()