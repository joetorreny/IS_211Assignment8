import random
import argparse
import time

def input_number(prompt='Please enter a number: ', minimum=0, maximum=None):
    """Read a positive number with the given prompt."""
    while True:
        try:
            number = int(input(prompt))
            if (number < minimum or
                (maximum is not None and number > maximum)):
                    print('Number is not within range: {} to {}'.format(minimum, maximum))
            else:
                break

        except ValueError:
            print('You need to enter a number')
            continue
    return number


class RolledOneException(Exception):
    pass


class Die:
    """A die to play with."""

    def __init__(self):
        self.value = random.randint(1, 6)

    def roll(self):
        """Returns the rolled dice, or raises RolledOneException if 1."""

        self.value = random.randint(1, 6)
        if self.value == 1:
            raise RolledOneException

        return self.value

    def __str__(self):
        return "Rolled " + str(self.value) + "."


class Box:
    """Temporary score box holder class."""

    def __init__(self):
        self.value = 0

    def reset(self):
        self.value = 0

    def add_dice_value(self, dice_value):
        self.value += dice_value


class Player(object):
    """Base class for different player types."""

    def __init__(self, name=None):
        self.name = name
        self.score = 0

    def add_score(self, player_score):
        """Adds player_score to total score."""

        self.score += player_score

    def __str__(self):
        """Returns player name and current score."""
        return str(self.name) + ": " + str(self.score)


class ComputerPlayer(Player):
    def __init__(self, name):
        super(ComputerPlayer, self).__init__(name)

    def keep_rolling(self, box):
        computer_decision = self.get_computer_decision(box)
        return computer_decision

    def get_computer_decision(self, box):
        current_points = box.value
        min_val = 25
        return min(min_val, 100 - self.score) > current_points


class HumanPlayer(Player):
    def __init__(self, name):
        super(HumanPlayer, self).__init__(name)

    def keep_rolling(self, box):
        """Asks the human player, if they want to keep rolling."""

        human_decision = input_number("  1 - Roll again, 0 - Hold? ", 0, 1)
        if human_decision == 1:
            return True
        else:
            return False


class PlayerFactory:

    def create_player(self, player_type):
        name = input("Enter {} name: ".format(player_type))
        if player_type == "computer":
            return ComputerPlayer(name)
        else:
            return HumanPlayer(name)


class GameManager:
    def __init__(self, player_types):
        """Initialises the game, optionally asking for human player names."""
        self.start_time = 0
        self.timed = False
        self.players = []
        for player_type in player_types:
            self.players.append(PlayerFactory().create_player(player_type))
        self.no_of_players = len(self.players)
        self.die = Die()
        self.box = Box()

    @staticmethod
    def welcome():
        """Prints a welcome message including rules."""

        print("*" * 70)
        print("Welcome to Pig Dice!" .center(70))
        print("*" * 70)
        print("The objective is to be the first to reach 100 points." .center(70))
        print("On each turn, the player will roll a die." .center(70))
        print("The die value will stored in a temporary score box." .center(70))
        print("(If the die value is 1, the player earns no points," .center(70))
        print("and the turn goes to the next player.)" .center(70))
        print("The player has an option to either roll again," .center(70))
        print("or hold. If you hold, the score in the" .center(70))
        print("temporary box will be added to your total score." .center(70))
        print(" Good luck! " .center(70, "*"))
        print(" Remember " .center(70, "*"))
        print(" Fortune favors the brave... " .center(70, "*"))
        print(" but chance favors the smart! " .center(70, "*"))
        print()
        print("let's starts" .center(70, " "))
        print()

    def decide_first_player(self):
        """Randomly chooses a player to begin, and prints who is starting."""
        self.current_player = random.randint(1, self.no_of_players) % self.no_of_players

        print('{} starts'.format(self.players[self.current_player].name))

    def next_player(self):
        """Advanced self.current_player to next player."""
        self.current_player = (self.current_player + 1) % self.no_of_players

    def previous_player(self):
        """Changes self.current_player to previous player."""

        self.current_player = (self.current_player - 1) % self.no_of_players

    def get_all_scores(self):
        """Returns a join all players scores."""

        return ', '.join(str(player) for player in self.players)

    def play_game(self):
        """Plays an entire game."""

        self.welcome()
        self.decide_first_player()
        time_up_str = ""
        max_time = 60
        while all(player.score < 100 for player in self.players):
            if self.timed and time.time() - self.start_time >= max_time:
                time_up_str = "Times Up! {} seconds has passed".format(max_time)
                break
            print('\nCurrent score --> {}'.format(self.get_all_scores()))
            print('\n*** {} to play ***'.format(self.players[self.current_player].name))
            self.box.reset()

            while self.keep_rolling():
                pass

            self.players[self.current_player].add_score(self.box.value)
            self.next_player()

        self.previous_player()
        print('\n')
        print(time_up_str)
        if self.players[0].score == self.players[1].score:
            print("draw")
        elif self.players[0].score > self.players[1].score:
            print(' {} has won '.format(self.players[0].name).center(70, '*'))
        else:
            print(' {} has won '.format(self.players[1].name).center(70, '*'))

    def keep_rolling(self):
        """Adds rolled dice to box. Returns if human/cpu wants to continue.

        If either player rolls a 1, the box value is reset, and turn ends.
        """
        try:
            dice_value = self.die.roll()
            self.box.add_dice_value(dice_value)
            print('Last roll: {}, new box value: {}'.format(dice_value, self.box.value))

            # Check if human (by asking) will keep rolling
            return self.players[self.current_player].keep_rolling(self.box)

        except RolledOneException:
            print('  Rolled one. Switching turns')
            self.box.reset()
            return False


class TimedGameProxy:
    def __init__(self, player_types, timed):
        self.game_manager = GameManager(player_types)
        self.timed = timed

    def welcome(self):
        self.game_manager.welcome()

    def play_game(self):
        if self.timed:
            self.game_manager.start_time = time.time()
            self.game_manager.timed = True
        self.game_manager.play_game()


def main():
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('--player1', type=str, default="human", help='player1 human or computer')
    parser.add_argument('--player2', type=str, default="computer", help='player2 human or computer')
    parser.add_argument('--timed', action="store_true", help='timed version')
    args = parser.parse_args()
    player1 = args.player1
    player2 = args.player2
    timed = args.timed
    players = [player1, player2]
    game = TimedGameProxy(players, timed)
    game.play_game()


if __name__ == '__main__':
    main()
