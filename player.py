# Player class
class Player:
    def __init__(self, name, position):
        self.name = name
        self.hand = []
        self.money = 1000  # Starting money
        self.current_bet = 0
        self.folded = False
        self.has_acted = False  # Track if the player has had a chance to act
        self.position = position

    def receive_card(self, card):
        self.hand.append(card)

    def make_bet(self, amount):
        if amount > self.money:
            amount = self.money  # All-in scenario
        self.current_bet += amount
        self.money -= amount

    def reset_for_new_round(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.has_acted = False

    def __str__(self):
        return f'{self.name}: ' + ', '.join(str(card) for card in self.hand)
