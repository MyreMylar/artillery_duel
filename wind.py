import random


class Wind:

    def __init__(self, min_wind, max_wind):
        self.min = min_wind
        self.max = max_wind
        self.min_change = -3
        self.max_change = 3
        self.time_accumulator = 0.0

        # Set the initial value of the wind
        self.current_value = random.randint(self.min, self.max)
        self.last_change = 0
        if self.current_value > 0:
            self.last_change = 1
        if self.current_value < 0:
            self.last_change = -1

        # Set the amount of time in seconds until the wind changes
        self.time_until_wind_changes = 5.0
        
    # ------------------------------------------------------------------------------------------
    # CHALLENGE 2
    # -------------
    #
    # Randomise the amount of time in seconds until the wind changes. (GUIDELINE CHANGE 1 LINE)
    #
    #
    # Hints:
    #
    # - Use the random.uniform( your_min_value_here, your_max_value_here ) to generate random
    #   floating point numbers.
    #
    #
    # EXTRA CREDIT:
    #
    # - Figure out how to change the *amount* the wind changes by each time too.
    #   Try making it change direction more dramatically.
    # ------------------------------------------------------------------------------------------
    def change_wind(self):
        # Set the amount of time in seconds until the wind changes
        self.time_until_wind_changes = 5.0

        # Try to simulate the wind changing. Currently it is more likely to continue
        # blowing in the same direction it blew in last time (4 times out of 5).
        if self.last_change > 0:
            change_value = random.randint(-1, self.max_change)
            self.last_change = change_value
        elif self.last_change < 0:
            change_value = random.randint(self.min_change, 1)
            self.last_change = change_value
        else:
            change_value = random.randint(-1, 1)
            self.last_change = change_value
        
        self.current_value += change_value

        # Make sure the current wind value does not exceed the maximum or minimum values
        if self.current_value > self.max:
            self.current_value = self.max
        if self.current_value < self.min:
            self.current_value = self.min
        
    def update(self, time_delta):
        # The timeDelta value is the amount of time in seconds since
        # the last loop of the game. We add it to the 'accumulator'
        # to track when an amount of time has passed, in this case
        # 3 seconds
        self.time_accumulator += time_delta
        if self.time_accumulator >= self.time_until_wind_changes:
            self.time_accumulator = 0.0  # reset the time accumulator
            self.change_wind()
