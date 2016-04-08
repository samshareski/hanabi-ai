from heuristics import *

from collections import deque
from enum import Enum
from numpy import random


class Hanabi:
    def __init__(self, heuristic):
        self.deck = Deck()
        self.play_area = PlayArea()
        self.discard_pile = []
        self.time = 8
        self.fuse = 3
        self.end_trigger = False
        self.turns_after_trigger = 2
        self.blown_up = False
        starting_cards = []
        for _ in range(10):
            starting_cards.append(self.deck.draw())
        self.player1 = Player(starting_cards[:5], self, heuristic)
        self.player2 = Player(starting_cards[5:], self, heuristic)
        self.player1.partner = self.player2
        self.player2.partner = self.player1

    def play(self, card):
        if not self.play_area.play(card):
            self.fuse -= 1
            if self.fuse == 0:
                self.blown_up = True
        if self.end_trigger:
            self.turns_after_trigger -= 1
            return
        else:
            return self.draw()

    def discard(self, card):
        self.discard_pile.append(card)
        self.time += 1
        if self.end_trigger:
            self.turns_after_trigger -= 1
            return
        else:
            return self.draw()

    def draw(self):
        card = self.deck.draw()
        if self.deck.is_empty():
            self.end_trigger = True
        return card

    def give_info(self, giver, info):
        recipient = giver.partner
        recipient.receive_info(info)
        self.time -= 1
        if self.end_trigger:
            self.turns_after_trigger -= 1

    def play_game(self):
        current_player = self.player1
        while not self.blown_up and self.turns_after_trigger > 0:
            current_player.perform_turn()
            current_player = current_player.partner
        return self.play_area.get_score(), self.blown_up


class Player:
    def __init__(self, starting_hand, game, heuristic):
        self.game = game
        self.timestamp = 0
        self.hand = []
        self.heuristic = heuristic(self)
        self.partner = None
        for card in starting_hand:
            self._add_to_hand(card)

    def _add_to_hand(self, card):
        self.timestamp += 1
        self.hand.append(CardInHand(card, self.timestamp))

    def perform_turn(self):
        move = self.heuristic.best_move()
        move.make_move()

    def play(self, position):
        card_in_hand = self.hand.pop(position)
        drawn_card = self.game.play(card_in_hand.card)
        if drawn_card:
            self._add_to_hand(drawn_card)

    def discard(self, position):
        card_in_hand = self.hand.pop(position)
        drawn_card = self.game.discard(card_in_hand.card)
        if drawn_card:
            self._add_to_hand(drawn_card)

    def give_info(self, info):
        self.game.give_info(self, info)

    def receive_info(self, info):
        if isinstance(info, Colour):
            for card_in_hand in self.hand:
                card_in_hand.learn_colour(info)
        else:
            for card_in_hand in self.hand:
                card_in_hand.learn_number(info)


class CardInHand:
    def __init__(self, card, timestamp):
        self.card = card
        self.possible_colours = list(Colour)
        self.possible_numbers = [1, 2, 3, 4, 5]
        self.colour = None
        self.number = None
        self.timestamp = timestamp

    def learn_colour(self, colour):
        if self.card.colour == colour:
            self.possible_colours = [colour]
            self.colour = colour
        elif colour in self.possible_colours:
            self.possible_colours.remove(colour)

    def learn_number(self, number):
        if self.card.number == number:
            self.possible_numbers = [number]
            self.number = number
        elif number in self.possible_numbers:
            self.possible_numbers.remove(number)


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

    def __eq__(self, other):
        return self.colour == other.colour and self.number == other.number


class PlayArea:
    def __init__(self):
        self.played = {Colour.white: [],
                       Colour.yellow: [],
                       Colour.green: [],
                       Colour.blue: [],
                       Colour.red: []}

    def play(self, card):
        suit = self.played[card.colour]
        if not suit:
            if card.number == 1:
                suit.append(card)
                return True
            else:
                return False
        else:
            if suit[-1].number == card.number - 1:
                suit.append(card)
                return True
            else:
                return False

    def get_score(self):
        score = 0
        for suit in self.played.values():
            if suit:
                score += suit[-1].number
        return score

    def playable_cards(self):
        playable = []
        for colour, values in self.played.items():
            if not values:
                playable.append(Card(colour, 1))
            elif values[-1].number != 5:
                playable.append(Card(colour, values[-1].number + 1))
        return playable

    def discardable_cards(self):
        discardable = []
        for colour, values in self.played.items():
            for value in values:
                discardable.append(Card(colour, value))
        return discardable

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
                           Card(Colour.red, 5)))
        random.shuffle(self.deck)

    def is_empty(self):
        return len(self.deck) == 0

    def draw(self):
        return self.deck.pop()


if __name__ == '__main__':
    total = 0
    games_failed = 0
    n_games = 100
    for _ in range(n_games):
        game = Hanabi(ProbabilisticHeurstic)
        score, fail = game.play_game()
        if fail:
            games_failed += 1
        else:
            total += score
    print(games_failed / n_games)
    print(total / (n_games - games_failed))


