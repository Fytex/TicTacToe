from numpy import full
from itertools import cycle, chain
from random import choice, randint
from os import system

'''
This game is 0-index however it prints out as 1-index

'''


class RoomAlreadyInUse(Exception):
    pass


class GameFinished(Exception):
    pass


class Draw(GameFinished):
    pass


class Win(GameFinished):
    pass


class Player:

    def __init__(self, name, draw, computer=False, mode=None):
        self.name = name
        self.draw = draw
        self.last_play = (None, None)
        self.computer = computer
        self.mode = mode

    def play(self, table=None):

        if self.computer:
            last_play = getattr(ComputerPlays(table, self.draw), self.mode)()
        else:
            play = int(input(f'\n{self.name}: ')) - 1

            if 0 > play or play > 8:
                raise KeyError('Room not found')

            last_play = divmod(play, 3)

        self.last_play = last_play
        return last_play


class ComputerPlays:

    __slots__ = ('table', 'draw')

    def __init__(self, table, draw):
        self.table = table
        self.draw = draw

    def _get_empty_rooms(self):
        table_chain = chain.from_iterable(self.table)
        return [idx for idx, room in enumerate(table_chain) if not room]

    def _ai_play(self, impossible=False):
        computer_draw = self.draw

        winning_lines = [{0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 4, 8},
                         {2, 4, 6}, {0, 3, 6}, {1, 4, 7}, {2, 5, 8}]

        table = {idx: draw for idx, draw in enumerate(chain.from_iterable(self.table))}

        enemy_lines = []

        for line in winning_lines:
            rooms = [(idx, table[idx]) for idx in line]

            empty_idxs = [idx for idx, draw in rooms if not draw]
            used_drawings = {draw for _, draw in rooms if draw}

            if len(empty_idxs) != 1:
                continue

            if len(used_drawings) != 1:
                continue

            empty_idx_position = divmod(empty_idxs.pop(), 3)
            draw = used_drawings.pop()

            if draw == computer_draw:
                return empty_idx_position
            else:
                enemy_lines.append(empty_idx_position)

        block_enemy = enemy_lines and enemy_lines.pop()

        if block_enemy:
            return block_enemy

        if not table[4]:  # middle play
            return (1, 1)

        corners = (0, 2, 6, 8)

        for corner in corners:

            if not table[corner]:
                return divmod(corner, 3)

    def random(self):
        table_idx = self._get_empty_rooms()
        return divmod(choice(table_idx), 3)

    '''
    `self._ai_play() or self.random()` sometimes there is no A.I. play to do
    '''

    def easy(self):
        return self.random()

    def medium(self):
        return self._ai_play() or self.random() if randint(0, 2) > 0 else self.random()

    def hard(self):
        return self._ai_play() or self.random() if randint(0, 4) > 0 else self.random()

    def impossible(self):
        return self._ai_play() or self.random()


class TicTacToe:

    def __init__(self, player_one, player_two, first_playing=None):
        self.table = full((3, 3), None)

        players = (player_one, player_two) if player_one is first_playing else (
            player_two, player_one)

        self.player_cycle = cycle(players)
        self.current_player = None
        self.plays_count = 0

    def __str__(self):
        rows = []
        for num, row in enumerate(self.table):
            num = num and num*3
            rows.append(' | '.join(str(draw) if draw else str(idx+num+1)
                                   for idx, draw in enumerate(row)))

        return '\n----------\n'.join(rows)

    def next_player(self):
        self.current_player = next_player = next(self.player_cycle)
        return next_player

    def computer_play(self):
        return self.current_player.play(self.table)

    def play(self, restart_play=False):

        if not restart_play:
            current_player = self.next_player()

        else:
            current_player = self.current_player

        if not current_player.computer:
            row, column = current_player.play()
            room_used = self.table[row][column]

            if room_used:
                raise RoomAlreadyInUse('This room is already in use')
        else:
            row, column = self.computer_play()

        self.table[row][column] = current_player.draw
        self.plays_count += 1

        if self.check():
            msg = f'Ohhh, you lost!' if current_player.computer else f'Nice {current_player.name}, you won!'
            raise Win(msg)

        if self.plays_count == 9:
            raise Draw('Tie...')

        return self

    def check(self):

        table = self.table
        current_player = self.current_player
        player_draw = current_player.draw
        row, column = current_player.last_play

        if all(elem == player_draw for elem in table[row]) or all(elem == player_draw for elem in list(zip(*table))[column]):
            return True

        # if row+column is pair then we must check obliqual lines; Note: 0-Index
        index = row+column
        if index % 2:
            return

        table_chain = chain.from_iterable(table)
        first_obliqual = (0, 4, 8)
        second_obliqual = (2, 4, 6)

        def equal_elements(*args):
            for idx, element in enumerate(table_chain):
                if idx in args:
                    yield element == player_draw

        if index == 4:  # check both obliqual lines
            return all(equal_elements(*first_obliqual)) or all(equal_elements(*second_obliqual))

        return all(equal_elements(index, 4, 8-index))


def get_computer():
    modes = ['easy', 'medium', 'hard', 'impossible']

    while True:
        mode = int(
            input('Game difficulty: \n1 - Easy\n2 - Medium\n3 - Hard\n4 - Impossible\n\nSelect Number: '))

        if 0 < mode < 4:
            mode = modes[mode - 1]
            break

    return Player('Computer', 'O', True, mode)


if __name__ == '__main__':

    with_computer = ~bool(int(input('How many players? (1/2): ')) - 1)
    player_one = Player(input('Player 1 (name): '), 'X')
    player_two = get_computer() if with_computer else Player(input('Player 2 (name): '), 'O')

    restart_game = False
    first_playing = cycle([player_one, player_two])

    while True:

        game = TicTacToe(player_one, player_two, next(first_playing))

        restart_play = False

        try:
            while True:
                system('cls||clear')

                if restart_play:
                    print('Select a valid number')

                print('\n\n' + str(game))

                try:
                    game.play(restart_play)

                except (KeyError, RoomAlreadyInUse):

                    restart_play = True

                else:
                    restart_play = False

        except GameFinished as exc:
            # system('cls||clear')
            print('\n\n' + str(game))
            print('\n\n' + str(exc))
            restart_game = input('\nDo you wanna play again? \'yes\' to continue\n').lower() in [
                'yes', 'y']

            if restart_game:
                player_one.draw, player_two.draw = player_two.draw, player_one.draw
            else:
                break
