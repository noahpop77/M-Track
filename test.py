from datetime import datetime, timedelta

def lp_decay(current_lp, last_played, banked_days):
    """Calculates the LP decay for League of Legends, taking into account the decay bank and delayed decay.
    
    Args:
    current_lp (int): The current amount of LP.
    last_played (str): A string representing the date and time of the last game played, in the format "YYYY-MM-DD HH:MM:SS".
    banked_days (int): The number of banked days.
    
    Returns:
    int: The amount of LP after decay.
    """
    
    # Define the decay rate per day (in LP).
    decay_rate = 50
    
    # If there are banked days, decay is delayed until all banked days are used up.
    if banked_days > 0:
        # Calculate the number of days since the last game played, but don't subtract any banked days.
        last_played_date = datetime.strptime(last_played, "%Y-%m-%d %H:%M:%S")
        days_since_last_played = (datetime.now() - last_played_date).days
        
        # Use up banked days first.
        if banked_days >= days_since_last_played:
            banked_days -= days_since_last_played
            days_since_last_played = 0
        else:
            days_since_last_played -= banked_days
            banked_days = 0
        
        # Calculate the amount of LP lost due to decay.
        lp_lost = decay_rate * days_since_last_played
        
        # Calculate the new amount of LP.
        new_lp = max(current_lp - lp_lost, 0)
        
        return new_lp, banked_days
    
    # If there are no banked days, decay starts immediately.
    else:
        # Calculate the number of days since the last game played.
        last_played_date = datetime.strptime(last_played, "%Y-%m-%d %H:%M:%S")
        days_since_last_played = (datetime.now() - last_played_date).days
        
        # Calculate the amount of LP lost due to decay.
        lp_lost = decay_rate * days_since_last_played
        
        # Calculate the new amount of LP.
        new_lp = max(current_lp - lp_lost, 0)
        
        # Update the banked days.
        banked_days = min(days_since_last_played, 28)  # Cap the banked days at 28.
        
        return new_lp, banked_days

current_lp = 90
last_played = "2023-03-01 14:30:00"
banked_days = 5

# Play a ranked game.
# ...

# Update the LP and banked days.
new_lp, banked_days = lp_decay(current_lp, last_played, banked_days)

print("New LP:", new_lp)
print("Banked days:", banked_days)