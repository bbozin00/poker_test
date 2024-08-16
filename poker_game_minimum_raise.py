import random
import tkinter as tk
from tkinter import simpledialog, messagebox

# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Card class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank} of {self.suit}'

# Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

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

# Game class
class PokerGame:
    def __init__(self):
        self.players = [Player(f'Player {i+1}', i) for i in range(4)]
        self.deck = Deck()
        self.pot = 0
        self.small_blind = 10
        self.big_blind = self.small_blind * 2
        self.community_cards = []
        self.current_bet = 0
        self.current_stage = 'Preflop'
        self.current_player_index = 0
        self.highest_bet = 0
        self.last_raiser_index = None  # Track the last player who raised
        self.big_blind_index = 1  # Index of the big blind player

    def reset_for_new_round(self):
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.current_stage = 'Preflop'
        self.highest_bet = 0
        self.last_raiser_index = None
        self.current_player_index = 0
        for player in self.players:
            player.reset_for_new_round()

    def deal_hands(self):
        for player in self.players:
            player.receive_card(self.deck.deal_card())
            player.receive_card(self.deck.deal_card())

    def deal_community_cards(self, number):
        for _ in range(number):
            self.community_cards.append(self.deck.deal_card())

    def blinds(self):
        # Small blind
        self.players[0].make_bet(self.small_blind)
        self.pot += self.small_blind

        # Big blind
        self.players[1].make_bet(self.big_blind)
        self.pot += self.big_blind
        self.highest_bet = self.big_blind
        self.current_player_index = 2  # Start with the player after the big blind

    def all_players_acted(self):
        # All players have acted, and either called or folded
        return all(player.has_acted or player.folded for player in self.players if player.money > 0)

    def remaining_active_players(self):
        return [player for player in self.players if not player.folded]

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

        self.current_bet = 0
        self.highest_bet = 0
        for player in self.players:
            player.current_bet = 0
            player.has_acted = False  # Reset action tracking for the next stage

        # Start with the first active player for the new stage
        self.current_player_index = self.find_next_active_player_index(start_index=0)

    def find_next_active_player_index(self, start_index):
        for i in range(len(self.players)):
            index = (start_index + i) % len(self.players)
            if not self.players[index].folded and self.players[index].money > 0:
                return index
        return start_index  # Fallback, should not happen if there are active players

    def end_hand_early(self, winner):
        winner.money += self.pot
        messagebox.showinfo("Winner", f"{winner.name} wins the pot of ${self.pot} because all others folded!")
        self.reset_for_new_round()
        self.deal_hands()
        self.blinds()

    def showdown(self):
        active_players = self.remaining_active_players()
        winner = max(active_players, key=lambda p: sum(ord(c.rank) for c in p.hand))
        winner.money += self.pot
        messagebox.showinfo("Showdown", f"{winner.name} wins the pot of ${self.pot}!")
        self.reset_for_new_round()
        self.deal_hands()
        self.blinds()

    def get_active_player(self):
        return self.players[self.current_player_index]

    def next_player(self):
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if not self.players[self.current_player_index].folded and self.players[self.current_player_index].money > 0:
                break

        if self.preflop_action_complete():
            self.next_stage()

# GUI class
class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Texas Hold'em Poker")
        self.root.geometry("800x600")
        self.game = PokerGame()

        self.create_widgets()

    def create_widgets(self):
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=20)

        self.players_frame = tk.Frame(self.root)
        self.players_frame.pack(pady=20)

        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(pady=20)

        self.community_frame = tk.Frame(self.root)
        self.community_frame.pack(pady=20)

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(pady=20)

        self.players_labels = []
        for i in range(4):
            label = tk.Label(self.players_frame, text=f'Player {i+1}:')
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.players_labels.append(label)

        self.community_label = tk.Label(self.community_frame, text="Community Cards: ")
        self.community_label.pack(pady=10)

        self.pot_label = tk.Label(self.root, text="Pot: $0")
        self.pot_label.pack(pady=10)

        self.call_button = tk.Button(self.action_frame, text="Call", command=self.call_action)
        self.call_button.grid(row=0, column=0, padx=10)

        self.raise_button = tk.Button(self.action_frame, text="Raise", command=self.raise_action)
        self.raise_button.grid(row=0, column=1, padx=10)

        self.fold_button = tk.Button(self.action_frame, text="Fold", command=self.fold_action)
        self.fold_button.grid(row=0, column=2, padx=10)

        self.check_button = tk.Button(self.action_frame, text="Check", command=self.check_action)
        self.check_button.grid(row=0, column=3, padx=10)

        self.chat_box = tk.Text(self.chat_frame, height=10, width=50)
        self.chat_box.pack(pady=10)
        self.chat_box.insert(tk.END, "Game started...\n")

        self.start_round()

    def update_display(self):
        for i, player in enumerate(self.game.players):
            self.players_labels[i].config(
                text=f'{player.name}: ' + ', '.join(str(card) for card in player.hand) + f" | Money: ${player.money}" +
                     (" (Folded)" if player.folded else "")
            )

        community_text = "Community Cards: " + ', '.join(str(card) for card in self.game.community_cards)
        self.community_label.config(text=community_text)

        self.pot_label.config(text=f"Pot: ${self.game.pot}")
        if not self.game.get_active_player().folded:
            self.update_chat_box(f"It's {self.game.get_active_player().name}'s turn.")

        # Disable/Enable actions based on the current state
        active_player = self.game.get_active_player()
        if active_player.folded:
            self.call_button.config(state=tk.DISABLED)
            self.raise_button.config(state=tk.DISABLED)
            self.fold_button.config(state=tk.DISABLED)
            self.check_button.config(state=tk.DISABLED)
        else:
            if active_player.current_bet == self.game.highest_bet:
                self.check_button.config(state=tk.NORMAL)
                self.call_button.config(state=tk.DISABLED)
            else:
                self.check_button.config(state=tk.DISABLED)
                self.call_button.config(state=tk.NORMAL)

    def update_chat_box(self, message):
        self.chat_box.insert(tk.END, f"{message}\n")
        self.chat_box.see(tk.END)  # Automatically scroll to the end

    def call_action(self):
        player = self.game.get_active_player()
        amount_to_call = self.game.highest_bet - player.current_bet

        # Ensure the call doesn't exceed the player's stack
        if amount_to_call > player.money:
            amount_to_call = player.money

        player.make_bet(amount_to_call)
        player.has_acted = True  # Mark that the player has acted
        self.game.pot += amount_to_call
        self.update_chat_box(f"{player.name} calls.")

        # After the call, check if the action should proceed to the next stage
        self.game.next_player()
        self.update_display()

    def raise_action(self):
        player = self.game.get_active_player()
        min_raise = self.game.big_blind * 2  # Minimum raise is the value of 2 big blinds
        raise_amount = simpledialog.askinteger("Raise", f"Enter raise amount (Minimum ${min_raise}, Max ${player.money}):", parent=self.root, minvalue=min_raise, maxvalue=player.money)

        if raise_amount is not None and raise_amount >= min_raise:
            total_bet = player.current_bet + raise_amount
            player.make_bet(total_bet - player.current_bet)
            self.game.highest_bet = total_bet
            player.has_acted = True  # Mark that the player has acted
            self.game.pot += raise_amount
            self.game.last_raiser_index = self.game.current_player_index  # Update the last raiser
            self.update_chat_box(f"{player.name} raises by ${raise_amount}.")
            self.game.next_player()
            self.update_display()

    def fold_action(self):
        player = self.game.get_active_player()
        player.folded = True
        player.has_acted = True  # Mark that the player has acted (by folding)
        self.update_chat_box(f"{player.name} folds.")
        remaining_players = self.game.remaining_active_players()
        if len(remaining_players) == 1:
            self.game.end_hand_early(remaining_players[0])
        else:
            self.game.next_player()
            self.update_display()

    def check_action(self):
        player = self.game.get_active_player()
        if player.current_bet == self.game.highest_bet:
            player.has_acted = True  # Mark that the player has acted
            self.update_chat_box(f"{player.name} checks.")
            self.game.next_player()
            self.update_display()
        else:
            messagebox.showwarning("Invalid Action", "You cannot check when there's a bet to call!")

    def start_round(self):
        self.game.reset_for_new_round()
        self.game.deal_hands()
        self.game.blinds()
        self.update_display()

if __name__ == '__main__':
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
