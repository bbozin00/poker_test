import random

# Card class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = VALUE[rank]

    def __str__(self):
        return f'{self.rank} of {self.suit}'

# Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

    def draw(self, number):
        cards = []
        for i in range(number):
            cards.append(self.deal_card())

        return cards

    def remove_cards(self, cards):
        cards_left = []
        for card in self.cards:
            shouldAdd = True
            for c in cards:
                if card.rank == c.rank and card.suit == c.suit:
                    shouldAdd = False
                    break
            if shouldAdd:
                cards_left.append(card)
        
        self.cards = cards_left


# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

VALUE = {
"2": 2,
"3": 3,
"4": 4,
"5": 5,
"6": 6,
"7": 7,
"8": 8,
"9": 9,
"10": 10,
"J": 11,
"Q": 12,
"K": 13,
"A": 14
}