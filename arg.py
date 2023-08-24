import argparse


class Args:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--rub', type=float, default=0)
        self.parser.add_argument('--usd', type=float, default=0)
        self.parser.add_argument('--eur', type=float, default=0)
        self.parser.add_argument('--period', type=int, default=1)
        self.parser.add_argument('--debug', choices={'0', 'false', 'False', 'n', 'N', '1', 'true', 'True', 'y', 'Y'},
                                 default='0', type=str)

    def get_args(self):
        return self.parser.parse_args()