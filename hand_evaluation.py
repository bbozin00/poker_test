from collections import Counter
from itertools import combinations
import copy
from deck import Deck

def get_hand_ranking(hand):
    """Return the hand ranking and the sorted ranks for comparison."""
    ranks = sorted([card.value for card in hand], reverse=True)
    is_flush = len(set(card.suit for card in hand)) == 1
    rank_counts = Counter(ranks)
    is_straight = len(rank_counts) == 5 and (ranks[0] - ranks[-1] == 4)

    if is_straight and is_flush:
        return (8, ranks), "Straight flush"
    if 4 in rank_counts.values():
        return (7, ranks), "Four of a kind"
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return (6, ranks), "Full house"
    if is_flush:
        return (5, ranks), "Flush"
    if is_straight:
        return (4, ranks), "Straight"
    if 3 in rank_counts.values():
        return (3, ranks), "Three of a kind"
    if list(rank_counts.values()).count(2) == 2:
        return (2, ranks), "Two pair"
    if 2 in rank_counts.values():
        return (1, ranks), "One pair"
    return (0, ranks), "High card"

def best_hand(cards):
    """Determine the best hand from given cards."""
    best = max(combinations(cards, 5), key=get_hand_ranking)
    return get_hand_ranking(best)

def find_winner(players, community_cards):
    """Return the player with the best hand."""
    best_rank = (-1, [])
    winners = []
    reason = ""
    
    for player in players:
        combined_cards = player.hand + community_cards
        player_best_hand, reason = best_hand(combined_cards)
        if player_best_hand > best_rank:
            best_rank = player_best_hand
            winners = [player]
        elif player_best_hand == best_rank:
            winners.append(player)
    
    return winners, reason

def calculate_win_probability(player_hand, community_cards, opponent_hands, num_simulations=1000):
    """Calculate the win probability of a given hand with community cards against multiple opponents."""
    wins = 0
    ties = 0
    
    for _ in range(num_simulations):
        deck = Deck()
    
        # Remove the known cards from the deck (player's hand, community cards, and opponent hands)
        known_cards = player_hand + community_cards
        for opponent_hand in opponent_hands:
            known_cards += opponent_hand
        deck.remove_cards(known_cards)
        # Simulate remaining community cards
        remaining_cards = deck.draw(5 - len(community_cards))
        final_community_cards = community_cards + remaining_cards
        
        # Calculate the best hand for the player
        player_best = best_hand(player_hand + final_community_cards)
        
        # Calculate the best hands for all opponents
        opponent_bests = [best_hand(opponent_hand + final_community_cards) for opponent_hand in opponent_hands]
        
        # Determine if the player's hand is the best
        if all(player_best > opponent_best for opponent_best in opponent_bests):
            wins += 1
        elif all(player_best == opponent_best for opponent_best in opponent_bests):
            ties += 1
    
    # Return win probability as a percentage
    win_probability = wins / num_simulations
    tie_probability = ties / num_simulations
    return win_probability, tie_probability
