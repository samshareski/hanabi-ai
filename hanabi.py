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


class Heuristic:
    def __init__(self, player):
        self.player = player
        self.play_moves = [
            Move(player.play, 0),
            Move(player.play, 1),
            Move(player.play, 2),
            Move(player.play, 3),
            Move(player.play, 4)
        ]
        self.discard_moves = [
            Move(player.discard, 0),
            Move(player.discard, 1),
            Move(player.discard, 2),
            Move(player.discard, 3),
            Move(player.discard, 4),
        ]
        self.give_colour_moves = [
            Move(player.give_info, Colour.white),
            Move(player.give_info, Colour.yellow),
            Move(player.give_info, Colour.green),
            Move(player.give_info, Colour.blue),
            Move(player.give_info, Colour.red)
        ]
        self.give_number_moves = [
            Move(player.give_info, 1),
            Move(player.give_info, 2),
            Move(player.give_info, 3),
            Move(player.give_info, 4),
            Move(player.give_info, 5)
        ]

    def best_move(self):
        raise NotImplementedError


class SimpleHeuristic(Heuristic):
    def __init__(self, player):
        super(SimpleHeuristic, self).__init__(player)

    def best_move(self):
        best_move = None
        player_hand = self.player.hand
        oldest = 50
        for i, card_in_hand in enumerate(player_hand):
            if card_in_hand.timestamp < oldest:
                oldest = card_in_hand.timestamp
                best_move = Move(self.player.discard, i)

        playable_cards = self.player.game.play_area.playable_cards()
        if self.player.game.time > 0:
            playable_info = {Colour.white : 0,
                             Colour.yellow : 0,
                             Colour.green : 0,
                             Colour.blue : 0,
                             Colour.red : 1,
                             1 : 0,
                             2 : 0,
                             3 : 0,
                             4 : 0,
                             5 : 0}
            partner_hand = self.player.partner.hand
            for card_in_hand in partner_hand:
                if card_in_hand.card in playable_cards:
                    if not card_in_hand.colour:
                        playable_info[card_in_hand.card.colour] += 1
                    if not card_in_hand.number:
                        playable_info[card_in_hand.card.number] += 1

            best_value = 0
            for info, value in playable_info.items():
                if value > best_value:
                    best_value = value
                    best_move = Move(self.player.give_info, info)

        for i, card_in_hand in enumerate(self.player.hand):
            if card_in_hand.colour and card_in_hand.number and card_in_hand.card in playable_cards:
                best_move = Move(self.player.play, i)

        return best_move


class ProbabilisticHeurstic(Heuristic):
    def __init__(self, player):
        super(ProbabilisticHeurstic, self).__init__(player)
        self.threshold = 0.70
        self.sudden_death_threshold = 0.80
        self.whole_deck = [Card(Colour.white, 1),
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
                           Card(Colour.red, 5)]

    def best_move(self):
        player_hand = self.player.hand
        oldest = 50
        # for i, card_in_hand in enumerate(player_hand):
        #     if card_in_hand.timestamp < oldest:
        #          oldest = card_in_hand.timestamp
        #          best_move = Move(self.player.discard, i)

        playable_cards = self.player.game.play_area.playable_cards()
        if self.player.game.time > 0:
            playable_info = {Colour.white: 0,
                             Colour.yellow: 0,
                             Colour.green: 0,
                             Colour.blue: 0,
                             Colour.red: 0,
                             1: 0,
                             2: 0,
                             3: 0,
                             4: 0,
                             5: 0}
            partner_hand = self.player.partner.hand
            for card_in_hand in partner_hand:
                if not card_in_hand.colour:
                    if card_in_hand.card in playable_cards:
                        playable_info[card_in_hand.card.colour] += 2
                    else:
                        playable_info[card_in_hand.card.colour] += 1
                if not card_in_hand.number:
                    if card_in_hand.card in playable_cards:
                        playable_info[card_in_hand.card.number] += 2
                    else:
                        playable_info[card_in_hand.card.number] += 1

            best_value = 0
            for info, value in playable_info.items():
                if value > best_value:
                    best_value = value
                    best_move = Move(self.player.give_info, info)

        if self.player.game.fuse > 1:
            threshold = self.threshold
        else:
            threshold = self.sudden_death_threshold
        best_prob = 0
        worst_prob = 1
        threshold_met = False
        for i, card_in_hand in enumerate(self.player.hand):
            prob = self.calc_percentages(card_in_hand, self.player.hand, self.player.partner.hand,
                                         self.player.game.play_area, self.player.game.discard_pile)
            if prob >= threshold and prob > best_prob:
                threshold_met = True
                best_prob = prob
                best_move = Move(self.player.play, i)
            elif not threshold_met and prob < worst_prob and self.player.game.time == 0:
                 worst_prob = prob
                 best_move = Move(self.player.discard, i)

        return best_move

    def calc_percentages(self, given_card_in_hand, player_hand, partner_hand, play_area, discard_pile):
        possible_cards = list(self.whole_deck)
        for card_in_hand in partner_hand:
            possible_cards.remove(card_in_hand.card)
        for card_in_hand in player_hand:
            if not card_in_hand == given_card_in_hand and card_in_hand.colour and card_in_hand.number:
                possible_cards.remove(card_in_hand.card)
        for card in discard_pile:
            possible_cards.remove(card)
        for suit in play_area.played.values():
            for card in suit:
                possible_cards.remove(card)
        possible_cards = list(filter(lambda card: card.colour in given_card_in_hand.possible_colours,
                                     possible_cards))
        possible_cards = list(filter(lambda card: card.number in given_card_in_hand.possible_numbers,
                                     possible_cards))
        n = len(possible_cards)
        playable_cards = play_area.playable_cards()
        playable_probability = 0
        for card in possible_cards:
            if card in playable_cards:
                playable_probability += 1 / n

        return playable_probability


class Move:
    def __init__(self, move, arg):
        self.move = move
        self.arg = arg

    def make_move(self):
        self.move(self.arg)


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


