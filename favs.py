

from tinkoff.invest import Client

TOKEN = os.environ["INVEST_TOKEN"]

def main():

    parser = argparse.ArgumentParser(description='Tinkoff bonds')
    parser.add_argument('--only_new', action='store_true', help='Only new bonds')
    args = parser.parse_args()

    with Client(TOKEN) as client:

        allbonds = client.instruments.bonds()
        

if __name__ == "__main__":
    main()