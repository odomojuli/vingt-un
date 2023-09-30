import random
import math

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def get_value(self):
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        elif self.rank == "Ace":
            return 11
        else:
            return int(self.rank)


class Deck:
    def __init__(self, num_decks=1):
        self.cards = self.generate_deck(num_decks)
        self.shuffle()
        self.cut_card_position = self.default_cut_card(num_decks)
        self.lookup_table = self.generate_lookup_table()

    def generate_deck(self, num_decks):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        return [Card(rank, suit) for suit in suits for rank in ranks for _ in range(num_decks)]

    def shuffle(self):
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def draw_card(self):
        if len(self.cards) <= self.cut_card_position:
            print("Reached the cut card. Reshuffling the deck.")
            self.cards = self.generate_deck(len(self.cards) // 52)
            self.shuffle()
        return self.cards.pop()

    def generate_lookup_table(self):
        lookup_table = {}
        for card1 in self.cards:
            for card2 in self.cards:
                hand = Hand()
                hand.add_card(card1)
                hand.add_card(card2)
                hand_str = f"{str(card1)}, {str(card2)}"
                lookup_table[hand_str] = hand.get_value()[0]
        return lookup_table

    def default_cut_card(self, num_decks):
        match num_decks:
            case math.inf:
                return 0  # Implement logic for a fixed number of hands per shoe
            case 1:
                return 26
            case 2:
                return 2 * 52 - 26
            case _:
                assert num_decks > 2 and num_decks == int(num_decks)
                return int(num_decks) * 52 - 78


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = sum(card.get_value() for card in self.cards)
        num_aces = sum(1 for card in self.cards if card.rank == "Ace")
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value, num_aces


class GameRules:
    def __init__(self, ds=False, d10=False, h17=False, ls=False, rsa=False, s17=False, toke=False):
        self.ds = ds  # Double down after splitting
        self.d10 = d10  # Double down only on two-card ten or more
        self.h17 = h17  # Dealer hits soft seventeen
        self.ls = ls  # Late surrender
        self.rsa = rsa  # Resplit aces
        self.s17 = s17  # Dealer stands on soft seventeen
        self.toke = toke  # Dealers keep their own tips


def basic_strategy(player_hand, dealer_card):
    player_value, _ = player_hand.get_value()
    dealer_value = dealer_card.get_value()

    if player_value < 12:
        return 'hit'
    elif player_value == 12:
        if dealer_value < 4 or dealer_value > 6:
            return 'hit'
        else:
            return 'stand'
    elif 13 <= player_value <= 16:
        if dealer_value > 6:
            return 'hit'
        else:
            return 'stand'
    elif player_value > 16:
        return 'stand'

def play_blackjack(num_decks=1, game_rules=GameRules(), shoe=False):
    deck = Deck(num_decks)
    player_hand = Hand()
    dealer_hand = Hand()

    player_hand.add_card(deck.draw_card())
    dealer_hand.add_card(deck.draw_card())
    player_hand.add_card(deck.draw_card())
    dealer_hand.add_card(deck.draw_card())

    print("Welcome to Blackjack!\n")
    print(f"Dealer's Visible Card: *{dealer_hand.cards[0]}* (Value: *{dealer_hand.cards[0].get_value()}*)")
    print(f"Your Hand: {[str(card) for card in player_hand.cards]}, Total: {player_hand.get_value()[0]}\n")

    while player_hand.get_value()[0] < 21:
        suggestion = basic_strategy(player_hand, dealer_hand.cards[0])
        print(f"Basic Strategy Suggests: {suggestion.upper()}")
        action = input("Do you want to 'hit', 'stand', 'split', 'double' or 'surrender'? ").lower()

        if action == 'hit':
            player_hand.add_card(deck.draw_card())
            print(f"Your Hand: {[str(card) for card in player_hand.cards]}, Total: {player_hand.get_value()[0]}\n")
        elif action == 'stand':
            break
    
    if player_hand.get_value()[0] > 21:
        print("Bust! You exceeded 21 points. You lose!")
        return

    print("\nDealer's turn:")
    print(f"Dealer's Hand: {[str(card) for card in dealer_hand.cards]}, Total: {dealer_hand.get_value()[0]}\n")

    while True:
        dealer_value, num_aces = dealer_hand.get_value()
        if dealer_value >= 17:
            if game_rules.h17 and dealer_value == 17 and num_aces:
                pass  # Dealer hits on soft 17
            elif game_rules.s17 and dealer_value == 17:
                break  # Dealer stands on soft 17
            else:
                break
        dealer_hand.add_card(deck.draw_card())
        print(f"Dealer's Hand: {[str(card) for card in dealer_hand.cards]}, Total: {dealer_hand.get_value()[0]}\n")

    if dealer_hand.get_value()[0] > 21:
        print("Dealer Bust! Dealer exceeded 21 points. You win!")
        return
    
    if dealer_hand.get_value()[0] < player_hand.get_value()[0]:
        print("Congratulations! You win!")
    elif dealer_hand.get_value()[0] > player_hand.get_value()[0]:
        print("Sorry! Dealer wins!")
    else:
        print("It's a tie!")


custom_rules = GameRules(ds=True, d10=True, h17=True, ls=True, rsa=True, s17=True, toke=True)
play_blackjack(1, game_rules=custom_rules, shoe=True)