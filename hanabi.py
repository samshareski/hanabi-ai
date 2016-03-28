from collections import deque
from enum import Enum
from numpy import random


class Colour(Enum):
    white = 1
    yellow = 2
    green = 3
    blue = 4
    red = 5


class Card:
    def __init__(self, colour, number):
        self.colour = colour
        self.number = number

    def __str__(self):
        return '{} {}'.format(self.colour.name, self.number)


class Deck:
    def __init__(self):
        self.deck = deque((Card(Colour.white, 1),
                           Card(Colour.white, 1),
                           Card(Colour.white, 1),
                           Card(Colour.white, 2),
                           Card(Colour.white, 2),
                           Card(Colour.white, 3),
                           Card(Colour.white, 3),
                           Card(Colour.white, 4),
                           Card(Colour.white, 4),
                           Card(Colour.white, 5),
                           Card(Colour.yellow, 1),
                           Card(Colour.yellow, 1),
                           Card(Colour.yellow, 1),
                           Card(Colour.yellow, 2),
                           Card(Colour.yellow, 2),
                           Card(Colour.yellow, 3),
                           Card(Colour.yellow, 3),
                           Card(Colour.yellow, 4),
                           Card(Colour.yellow, 4),
                           Card(Colour.yellow, 5),
                           Card(Colour.green, 1),
                           Card(Colour.green, 1),
                           Card(Colour.green, 1),
                           Card(Colour.green, 2),
                           Card(Colour.green, 2),
                           Card(Colour.green, 3),
                           Card(Colour.green, 3),
                           Card(Colour.green, 4),
                           Card(Colour.green, 4),
                           Card(Colour.green, 5),
                           Card(Colour.blue, 1),
                           Card(Colour.blue, 1),
                           Card(Colour.blue, 1),
                           Card(Colour.blue, 2),
                           Card(Colour.blue, 2),
                           Card(Colour.blue, 3),
                           Card(Colour.blue, 3),
                           Card(Colour.blue, 4),
                           Card(Colour.blue, 4),
                           Card(Colour.blue, 5),
                           Card(Colour.red, 1),
                           Card(Colour.red, 1),
                           Card(Colour.red, 1),
                           Card(Colour.red, 2),
                           Card(Colour.red, 2),
                           Card(Colour.red, 3),
                           Card(Colour.red, 3),
                           Card(Colour.red, 4),
                           Card(Colour.red, 4),
                           Card(Colour.red, 6)))
        random.shuffle(self.deck)

    def is_empty(self):
        return len(self.deck) == 0

    def draw(self):
        return self.deck.pop()


if __name__ == '__main__':
    deck = Deck()

    while not deck.is_empty():
        print(deck.draw())
