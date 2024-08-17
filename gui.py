from game import PokerGame
from tkinter import simpledialog, messagebox
import tkinter as tk

# GUI class
class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Texas Hold'em Poker")
        self.root.geometry("800x700")
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

        self.active_player_label = tk.Label(self.root, text=f"Active Player = {self.game.current_player_index + 1}")
        self.active_player_label.pack(pady=20)

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
                     (" (Folded)" if player.folded else "") + (" [BB]" if i == self.game.big_blind_index else "") +
                     (" [SB]" if i == self.game.small_blind_index else "") + 
                     (f" BET = ${player.current_bet}" if not player.folded and player.money > 0 else "")
            )

        community_text = "Community Cards: " + ', '.join(str(card) for card in self.game.community_cards)
        self.community_label.config(text=community_text)

        self.pot_label.config(text=f"Pot: ${self.game.pot}")
        self.active_player_label.config(text=f"Active Player = {self.game.current_player_index + 1}")
        if not self.game.get_active_player().folded:
            self.update_chat_box(f"It's {self.game.get_active_player().name}'s turn.")

        self.call_button.config(state=tk.NORMAL)
        self.raise_button.config(state=tk.NORMAL)
        self.fold_button.config(state=tk.NORMAL)
        self.check_button.config(state=tk.NORMAL)

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

        if self.game.winners is not None:
            winners = ""
            for winner in self.game.winners:
                winners += ", " + winner.name
            winners = winners[2:]
            messagebox.showinfo("Showdown", f"{winners} wins the pot of ${self.game.pot} because of {self.game.win_reason}!")
            self.game.reset_for_new_round()
            self.game.deal_hands()
            self.game.blinds()
            self.update_display()

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
        if self.game.current_stage != "Preflop":
            min_raise = self.game.big_blind

        raise_amount = simpledialog.askinteger("Raise", f"Enter raise amount (Minimum ${min_raise}, Max ${player.money}):", parent=self.root, minvalue=min_raise, maxvalue=player.money)

        if raise_amount is not None and raise_amount >= min_raise:
            total_bet = player.current_bet + raise_amount
            player.make_bet(total_bet - player.current_bet)
            self.game.highest_bet = total_bet
            player.has_acted = True  # Mark that the player has acted
            self.game.pot += raise_amount
            if player.money == 0:
                self.game.last_raiser_index = None
            else:
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
