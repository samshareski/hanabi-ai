from hanabi import Card, Colour


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
            playable_info = {Colour.white: 0,
                             Colour.yellow: 0,
                             Colour.green: 0,
                             Colour.blue: 0,
                             Colour.red: 1,
                             1: 0,
                             2: 0,
                             3: 0,
                             4: 0,
                             5: 0}
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