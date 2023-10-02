import random


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.art = self.generate_ascii_art()

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def get_value(self):
        return (
            10
            if self.rank in ["Jack", "Queen", "King"]
            else 11
            if self.rank == "Ace"
            else int(self.rank)
        )
    
    def generate_ascii_art(self):
        rank_str = self.rank[0] if self.rank != '10' else '10'
        suit_str = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}[self.suit]
        return [
            "┌───────┐",
            f"| {rank_str:<2}    |",
            "|       |",
            f"|   {suit_str}   |",
            "|       |",
            f"|    {rank_str:>2} |",
            "└───────┘"
        ]
    
    def display_ascii_art(self):
        for line in self.art:
            print(line)


class Deck:
    def __init__(self, num_decks=1):
        self.cards = self.generate_deck(num_decks)
        random.shuffle(self.cards)  # Replaced custom shuffle with python provided
        self.cut_card_position = self.default_cut_card(num_decks)
        self.lookup_table = self.generate_lookup_table()

    def generate_deck(self, num_decks):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
            "Ace",
        ]
        return [
            Card(rank, suit)
            for _ in range(num_decks)
            for suit in suits
            for rank in ranks
        ]

    def draw_card(self):
        if not self.cards or len(self.cards) <= self.cut_card_position:
            self.refresh_deck()
        return self.cards.pop()


    def refresh_deck(self):
        print("Reached the cut card. Reshuffling the deck.")
        self.cards = self.generate_deck(len(self.cards) // 52 or 1)  # Ensure we always generate at least one deck of cards.
        random.shuffle(self.cards)

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
        return {1: 26, 2: 78}.get(num_decks, max(0, int(num_decks) * 52 - 78))


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value, aces = sum(
            card.get_value() if card.rank != "Ace" else 1 for card in self.cards
        ), sum(card.rank == "Ace" for card in self.cards)
        return (value + 10) if value <= 11 and aces else value, aces
    
    def display_ascii_art(self):
        if not self.cards: return
        hand_art = [''] * 7  # As each card has 7 lines of ASCII art
        for card in self.cards:
            for i in range(7):
                hand_art[i] += card.art[i] + "  "
        print("\n".join(hand_art))


class GameRules:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def basic_strategy(player_hand, dealer_card):
    player_value, _ = player_hand.get_value()
    dealer_value = dealer_card.get_value()
    if player_value < 12:
        return "hit"
    if player_value == 12:
        return "hit" if dealer_value < 4 or dealer_value > 6 else "stand"
    if 13 <= player_value <= 16:
        return "hit" if dealer_value > 6 else "stand"
    return "stand"


def play_blackjack(num_decks=1, game_rules=GameRules(), shoe=False):
    deck, player_hand, dealer_hand = Deck(num_decks), Hand(), Hand()

    while True:
        player_hand.__init__()
        dealer_hand.__init__()
        
        player_hand.add_card(deck.draw_card())
        dealer_hand.add_card(deck.draw_card())
        player_hand.add_card(deck.draw_card())
        dealer_hand.add_card(deck.draw_card())
        
        print("Welcome to Blackjack!\n")
        print("Dealer's Visible Card: ")
        dealer_hand.cards[0].display_ascii_art()
        print(f"\n(Value: *{dealer_hand.cards[0].get_value()}*)")
        print("Your Hand:")
        player_hand.display_ascii_art()
        print(f"\nTotal: {player_hand.get_value()[0]}\n")
        
        while player_hand.get_value()[0] < 21:
            suggestion = basic_strategy(player_hand, dealer_hand.cards[0])
            print(f"Basic Strategy Suggests: {suggestion.upper()}")
            action = input("Do you want to 'hit', 'stand', 'split', 'double' or 'surrender'? ").lower()

            if action == 'hit':
                player_hand.add_card(deck.draw_card())
                print("Your New Hand:")
                player_hand.display_ascii_art()
                print(f"\nTotal: {player_hand.get_value()[0]}\n")
            elif action == 'stand':
                break

        if player_hand.get_value()[0] > 21:
            print("Bust! You exceeded 21 points. You lose!")
        else:
            print("\nDealer's turn:")
            print("Dealer's Hand:")
            dealer_hand.display_ascii_art()

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
                print("\nDealer's New Hand:")
                dealer_hand.display_ascii_art()
                print(f"\nTotal: {dealer_hand.get_value()[0]}\n")

            if dealer_hand.get_value()[0] > 21:
                print("Dealer Bust! Dealer exceeded 21 points. You win!")
            elif dealer_hand.get_value()[0] < player_hand.get_value()[0]:
                print("Congratulations! You win!")
            elif dealer_hand.get_value()[0] > player_hand.get_value()[0]:
                print("Sorry! Dealer wins!")
            else:
                print("It's a tie!")

        if input("Do you want to continue playing with the current deck? (y/n): ").lower() != 'y':
            break


custom_rules = GameRules(ds=True, d10=True, h17=True, ls=True, rsa=True, s17=True, toke=True)
play_blackjack(1, game_rules=custom_rules, shoe=True)