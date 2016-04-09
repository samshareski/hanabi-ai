from collections import deque
from enum import Enum
from numpy import random


class Hanabi:
    def __init__(self, deck, move_search):
        self.deck = Deck(deck)
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
        self.player1 = Player(starting_cards[:5], self, move_search)
        self.player2 = Player(starting_cards[5:], self, move_search)
        self.player1.partner = self.player2
        self.player2.partner = self.player1

    def play(self, card):
        if not self.play_area.play(card):
            self.fuse -= 1
            self.discard_pile.append(card)
            if self.fuse == 0:
                self.blown_up = True
        elif card.number == 5:
            self.time = min(8, self.time + 1)
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

    def get_rare_cards(self):
        unique_cards = list(HANABI_UNIQUE_CARD_SET)
        length = 25
        rare_set_map = dict(zip(unique_cards, [0]*length))
        for card in self.discard_pile:
            rare_set_map[card] += rare_set_map[card] + 1

        rare_card_list = []
        for card, discard_count in rare_set_map.items():
            if card.number == 1:
                if discard_count == 2:
                    rare_card_list.append(card)
            elif card.number == 5:
                if discard_count == 0:
                    rare_card_list.append(card)
            else:
                if discard_count == 1:
                    rare_card_list.append(card)

        for card in self.play_area.played_cards():
            if card in rare_card_list:
                rare_card_list.remove(card)

        return rare_card_list

    def draw(self):
        if self.deck.is_empty():
            self.end_trigger = True
            return
        else:
            return self.deck.draw()

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
    def __init__(self, starting_hand, game, move_search):
        self.game = game
        self.timestamp = 0
        self.hand = []
        self.move_search = move_search
        self.partner = None
        for card in starting_hand:
            self._add_to_hand(card)

    def _add_to_hand(self, card):
        self.timestamp += 1
        self.hand.append(CardInHand(card, self.timestamp))

    def perform_turn(self):
        move = self.move_search.get_best_move(self)
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

    def __hash__(self):
        return self.colour.value * 10 + self.number


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

    def future_playable_cards(self):
        playable = []
        for colour, values in self.played.items():
            if not values:
                playable.append(Card(colour, 1))
            elif values[-1].number != 5:
                for value in range(values[-1].number, 5):
                    playable.append(Card(colour, value))
        return playable

    def discardable_cards(self):
        discardable = []
        for colour, values in self.played.items():
            for value in values:
                discardable.append(Card(colour, value))
        return discardable

    def played_cards(self):
        played = []
        for suit in self.played.values():
            for card in suit:
                played.append(card)
        return played


class Deck:
    def __init__(self, deck = None):
        if not deck:
            self.deck = deque(HANABI_CARD_SET)
            random.shuffle(self.deck)
        else:
            self.deck = deck

    def is_empty(self):
        return len(self.deck) == 0

    def draw(self):
        return self.deck.pop()


class DiscardCriteria(Enum):
    oldest = 1
    playability = 2
    future_playability = 3
    rarity = 4


class PlayCriteria(Enum):
    explicit = 1
    probabilistic = 2


class MoveSearch:
    def __init__(self, discard_criteria, play_criteria,
                 play_value, future_value, rare_value, other_value,
                 play_threshold=.75, sudden_death_threshold=.90):
        self.discard_criteria = discard_criteria
        self.play_criteria = play_criteria
        self.play_value = play_value
        self.future_value = future_value
        self.rare_value = rare_value
        self.other_value = other_value
        self.play_threshold = play_threshold
        self.sudden_death_threshold = sudden_death_threshold

    def __str__(self):
        return ' '.join([str(self.play_criteria.name), str(self.discard_criteria.name),
                        str(self.play_value), str(self.future_value), str(self.other_value), str(self.rare_value),
                        str(self.play_threshold), str(self.sudden_death_threshold)])

    def get_best_move(self, player):
        partner = player.partner
        game = player.game
        if self.play_criteria == PlayCriteria.explicit:
            best_move = self.get_explicit_play(player, game.play_area)
        else:
            best_move = self.get_probabilistic_play(player, partner, game)
        if not best_move and game.time > 0:
            best_move = self.get_best_info(player, partner, game)
        if not best_move:
            if self.discard_criteria == DiscardCriteria.oldest:
                best_move = self.oldest_discard(player)
            elif self.discard_criteria == DiscardCriteria.playability:
                best_move = self.least_playable_discard(player, partner, game)
            elif self.discard_criteria == DiscardCriteria.future_playability:
                best_move = self.least_future_playable_discard(player, partner, game)
            else:
                best_move = self.least_rare_discard(player, partner, game)
        return best_move

    def get_best_info(self, player, partner, game):
        best_move = None
        future_playable_cards = game.play_area.future_playable_cards()
        playable_cards = game.play_area.playable_cards()
        rare_cards = game.get_rare_cards()
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
        partner_hand = partner.hand
        for card_in_hand in partner_hand:
            if not card_in_hand.colour:
                if card_in_hand.card in rare_cards:
                    playable_info[card_in_hand.card.colour] += self.rare_value
                if card_in_hand.card in playable_cards:
                    playable_info[card_in_hand.card.colour] += self.play_value
                elif card_in_hand.card in future_playable_cards:
                    playable_info[card_in_hand.card.colour] += self.future_value
                else:
                    playable_info[card_in_hand.card.colour] += self.other_value
            if not card_in_hand.number:
                if card_in_hand.card in rare_cards:
                    playable_info[card_in_hand.card.number] += self.rare_value
                if card_in_hand.card in playable_cards:
                    playable_info[card_in_hand.card.number] += self.play_value
                elif card_in_hand.card in future_playable_cards:
                    playable_info[card_in_hand.card.number] += self.future_value
                else:
                    playable_info[card_in_hand.card.number] += self.other_value

        best_value = 0
        for info, value in playable_info.items():
            if value > best_value:
                best_value = value
                best_move = Move(player.give_info, info)

        return best_move

    def get_probabilistic_play(self, player, partner, game):
        best_move = None
        best_prob = 0
        if game.fuse > 1:
            threshold = self.play_threshold
        else:
            threshold = self.sudden_death_threshold

        for i, card_in_hand in enumerate(player.hand):
            prob, _, _ = self.calc_percentages(card_in_hand, player.hand, partner.hand,
                                         game.play_area, game, game.discard_pile)
            if prob >= threshold and prob > best_prob:
                best_prob = prob
                best_move = Move(player.play, i)

        return best_move

    def get_explicit_play(self, player, play_area):
        best_move = None
        playable_cards = play_area.playable_cards()
        for i, card_in_hand in enumerate(player.hand):
            if card_in_hand.colour and card_in_hand.number and card_in_hand.card in playable_cards:
                best_move = Move(player.play, i)

        return best_move

    def oldest_discard(self, player):
        oldest = 50
        best_move = None
        for i, card_in_hand in enumerate(player.hand):
            if card_in_hand.timestamp < oldest:
                oldest = card_in_hand.timestamp
                best_move = Move(player.discard, i)
        assert best_move
        return best_move

    def least_playable_discard(self, player, partner, game):
        best_move = None
        worst_prob = 2
        for i, card_in_hand in enumerate(player.hand):
            prob, _, _ = self.calc_percentages(card_in_hand, player.hand, partner.hand,
                                         game.play_area, game, game.discard_pile)
            if prob <= worst_prob:
                worst_prob = prob
                best_move = Move(player.discard, i)

        assert best_move
        return best_move

    def least_future_playable_discard(self, player, partner, game):
        best_move = None
        worst_prob = 2
        for i, card_in_hand in enumerate(player.hand):
            _, prob, _ = self.calc_percentages(card_in_hand, player.hand, partner.hand,
                                            game.play_area, game, game.discard_pile)
            if prob <= worst_prob:
                worst_prob = prob
                best_move = Move(player.discard, i)

        assert best_move
        return best_move

    def least_rare_discard(self, player, partner, game):
        best_move = None
        worst_prob = 2
        for i, card_in_hand in enumerate(player.hand):
            _, _, prob = self.calc_percentages(card_in_hand, player.hand, partner.hand,
                                            game.play_area, game, game.discard_pile)
            if prob <= worst_prob:
                worst_prob = prob
                best_move = Move(player.discard, i)

        assert best_move
        return best_move

    def calc_percentages(self, given_card_in_hand, player_hand, partner_hand, play_area, game, discard_pile):
        possible_cards = list(HANABI_CARD_SET)
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
        future_playable_cards = play_area.future_playable_cards()
        rare_cards = game.get_rare_cards()

        playable_probability = 0
        future_playable_probability = 0
        rare_card_probability = 0
        for card in possible_cards:
            if card in playable_cards:
                playable_probability += 1 / n
            if card in future_playable_cards:
                future_playable_probability += 1 / n
            if card in rare_cards:
                rare_card_probability += 1 / n

        future_playable_probability = min(1, future_playable_probability)

        return playable_probability, future_playable_probability, rare_card_probability

class Move:
    def __init__(self, move, arg):
        self.move = move
        self.arg = arg

    def make_move(self):
        self.move(self.arg)

HANABI_CARD_SET = (Card(Colour.white, 1),
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
                   Card(Colour.red, 5))

HANABI_UNIQUE_CARD_SET = (Card(Colour.white, 1),
                   Card(Colour.white, 2),
                   Card(Colour.white, 3),
                   Card(Colour.white, 4),
                   Card(Colour.white, 5),
                   Card(Colour.yellow, 1),
                   Card(Colour.yellow, 2),
                   Card(Colour.yellow, 3),
                   Card(Colour.yellow, 4),
                   Card(Colour.yellow, 5),
                   Card(Colour.green, 1),
                   Card(Colour.green, 2),
                   Card(Colour.green, 3),
                   Card(Colour.green, 4),
                   Card(Colour.green, 5),
                   Card(Colour.blue, 1),
                   Card(Colour.blue, 2),
                   Card(Colour.blue, 3),
                   Card(Colour.blue, 4),
                   Card(Colour.blue, 5),
                   Card(Colour.red, 1),
                   Card(Colour.red, 2),
                   Card(Colour.red, 3),
                   Card(Colour.red, 4),
                   Card(Colour.red, 5))


def compare_move_searches(searches, n_games):
    comparisons = len(searches)
    totals = [0] * comparisons
    maxes = [0] * comparisons
    games_failed = [0] * comparisons
    for _ in range(n_games):
        deck = deque(HANABI_CARD_SET)
        random.shuffle(deck)
        decks = [deque(deck) for _ in range(comparisons)]
        games = [Hanabi(decks[i], searches[i]) for i in range(comparisons)]
        score_fails = [game.play_game() for game in games]
        for i, (score, fail) in enumerate(score_fails):
            if fail:
                games_failed[i] += 1
            else:
                totals[i] += score
                if score > maxes[i]:
                    maxes[i] = score
    for i in range(comparisons):
        print(searches[i])
        print('\tAvg | Max | Failure Rate')
        print('\t', end='')
        print(totals[i] / (n_games - games_failed[i]), end=' | ')
        print(maxes[i], end=' | ')
        print(games_failed[i] / n_games)


if __name__ == '__main__':
    # total1 = 0
    # total2 = 0
    # max1 = 0
    # max2 = 0
    # games_failed_1 = 0
    # games_failed_2 = 0
    # n_games = 1000
    # move_search1 = MoveSearch(DiscardCriteria.oldest, PlayCriteria.explicit,
    #                           1, 1, 0, 1)
    # move_search2 = MoveSearch(DiscardCriteria.oldest, PlayCriteria.probabilistic,
    #                           1, 1, 0, 1)
    # for _ in range(n_games):
    #     deck1 = deque(HANABI_CARD_SET)
    #     random.shuffle(deck1)
    #     deck2 = deque(deck1)
    #     game1 = Hanabi(deck1, move_search1)
    #     game2 = Hanabi(deck2, move_search2)
    #     score1, fail1 = game1.play_game()
    #     if fail1:
    #         games_failed_1 += 1
    #     else:
    #         total1 += score1
    #         if score1 > max1:
    #             max1 = score1
    #     score2, fail2 = game2.play_game()
    #     if fail2:
    #         games_failed_2 += 1
    #     else:
    #         total2 += score2
    #         if score2 > max2:
    #             max2 = score2
    # print('Game 1')
    # print(games_failed_1 / n_games)
    # print(total1 / (n_games - games_failed_1))
    # print(max1)
    # print('Game 2')
    # print(games_failed_2 / n_games)
    # print(total2 / (n_games - games_failed_2))
    # print(max2)
    move_search1 = MoveSearch(DiscardCriteria.oldest, PlayCriteria.explicit,
                              1, 1, 0, 1)
    move_search2 = MoveSearch(DiscardCriteria.oldest, PlayCriteria.probabilistic,
                              1, 1, 0, 1)
    compare_move_searches([move_search1, move_search2], 100)


