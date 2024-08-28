from hand_evaluation import find_winner
from deck import Deck
from player import Player
from tkinter import messagebox

# Game class
class PokerGame:
    def __init__(self):
        self.players = [Player(f'Player {i+1}', i) for i in range(4)]
        self.deck = Deck()
        self.round = 0
        self.pot = 0
        self.small_blind = 10
        self.big_blind = self.small_blind * 2
        self.community_cards = []
        self.current_bet = 0
        self.current_stage = 'Preflop'
        self.current_player_index = 0
        self.highest_bet = 0
        self.last_raiser_index = None  # Track the last player who raised
        self.big_blind_index = 2  # Index of the big blind player
        self.small_blind_index = 1
        self.dealer_index = -1

    def reset_for_new_round(self):
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.current_stage = 'Preflop'
        self.highest_bet = 0
        self.last_raiser_index = None
        self.round += 1
        self.dealer_index += 1
        self.set_next_small_blind_index()
        self.set_next_big_blind_index()
        self.set_next_current_player_index()
        self.winners = None
        self.win_reason = ""
        for player in self.players:
            player.reset_for_new_round()

    def set_next_big_blind_index(self):
        self.big_blind_index = (self.small_blind_index + 1) % len(self.players)
        while self.players[self.big_blind_index].money == 0:
            self.big_blind_index = (self.big_blind_index + 1) % len(self.players)

    def set_next_small_blind_index(self):
        self.small_blind_index = (self.dealer_index + 1) % len(self.players)
        while self.players[self.small_blind_index].money == 0:
            self.small_blind_index = (self.small_blind_index - 1) % len(self.players)

    def set_next_current_player_index(self):
        self.current_player_index = (self.big_blind_index + 1) % len(self.players)
        while self.players[self.current_player_index].money == 0:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def deal_hands(self):
        for player in self.remaining_alive_players():
            player.receive_card(self.deck.deal_card())
            player.receive_card(self.deck.deal_card())
    
    def deal_community_cards(self, number):
        for _ in range(number):
            self.community_cards.append(self.deck.deal_card())

    def blinds(self):
        # Small blind
        self.players[self.big_blind_index - 1].make_bet(self.small_blind)
        self.pot += self.small_blind

        # Big blind
        self.players[self.big_blind_index].make_bet(self.big_blind)
        self.pot += self.big_blind
        self.highest_bet = self.big_blind

    def all_players_acted(self):
        # All players have acted, and either called or folded
        return all(player.has_acted or player.folded for player in self.players if player.money > 0)

    def remaining_active_players(self):
        return [player for player in self.players if not player.folded and len(player.hand) > 0]
    
    def remaining_alive_players(self):
        return [player for player in self.players if player.money > 0]

    def preflop_action_complete(self):
        # Preflop action is complete if:
        # 1. All players have acted.
        # 2. The action has returned to the last raiser, and they have had their turn.
        if self.last_raiser_index is not None:
            return self.current_player_index == self.last_raiser_index and self.all_players_acted()
        else:
            return self.all_players_acted()

    def next_stage(self):
        if self.preflop_action_complete() and self.current_stage == 'Preflop':
            self.current_stage = 'Flop'
            self.deal_community_cards(3)  # Flop
        elif self.current_stage == 'Flop':
            self.current_stage = 'Turn'
            self.deal_community_cards(1)  # Turn
        elif self.current_stage == 'Turn':
            self.current_stage = 'River'
            self.deal_community_cards(1)  # River
        elif self.current_stage == 'River' and self.all_players_acted():
            self.showdown()
            return

        money_players = len([player for player in self.remaining_active_players() if player.money > 0])
        if money_players == 0 or money_players == 1:
            self.next_stage()
            return

        self.current_bet = 0
        self.highest_bet = 0
        for player in self.players:
            player.current_bet = 0
            player.has_acted = False  # Reset action tracking for the next stage

        # Start with the first active player for the new stage
        self.set_next_current_player_index()

        return self.current_stage 
    
    def find_next_active_player_index(self, start_index):
        for i in range(len(self.players)):
            index = (start_index + i) % len(self.players)
            if not self.players[index].folded and self.players[index].money > 0:
                return index
        return start_index  # Fallback, should not happen if there are active players

    def end_hand_early(self, winner: Player):
        winner.money += self.pot
        messagebox.showinfo("Winner", f"{winner.name} wins the pot of ${self.pot} because all others folded!")
        self.reset_for_new_round()
        self.deal_hands()
        self.blinds()

    def showdown(self):
        active_players = self.remaining_active_players()
        winners, reason = find_winner(active_players, self.community_cards)
        for winner in winners:
            winner.money += self.pot / len(winners)
        self.winners = winners
        self.win_reason = reason

    def get_active_player(self):
        return self.players[self.current_player_index]

    def next_player(self):
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            player = self.players[self.current_player_index]
            if player.has_acted or (not player.folded and player.money > 0):
                break

        if self.preflop_action_complete():
            self.next_stage()
