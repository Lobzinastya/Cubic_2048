import random
import numpy as np

possibilities = [(-1,0,0), (1,0,0), (0, 1, 0), (0,-1,0), (0,0,-1), (0,0,1)]
d = 3


class Game():
    def __init__(self, d=4):
        self.values = np.zeros([d, d, d], dtype='int')
        for _ in range(d + 1):
            self.add()
        self.score = 0
        self.end = False
        self.d = d

    def add(self, fill_value_strict=None):
        ''' В пустые клетки добавляется новое число, 3 или 9, с вероятностями 7/8 и 1/8,
        если принудительно не передано другое число
        '''
        ind_0 = np.argwhere(self.values == 0)
        if len(ind_0) > 0:

            rand_ind = random.choice(ind_0.tolist())
            if fill_value_strict is not None:
                fill_value = fill_value_strict
            else:
                fill_value = random.choices([2, 4], weights=[7 / 8, 1 / 8], k=1)[0]
            self.values[tuple(rand_ind)] = fill_value

        else:
            print('No empty spaces')

    def pretty(self):
        ''' Симпатичный вывод на печать'''
        print('Total score:', self.score)
        tabs = len(str(self.values.max()))
        for i in range(self.d):

            for k in range(self.d):
                for j in range(self.d):
                    print(f'{self.values[k, i, j]: >{tabs}}', end=' ')
                print(' | ', end='')
            print('\n', end='')
        print()

    def play(self):
        step = 1
        while not self.end:

            button = input().strip()
            self.update(button)
            if self.values.max() == 2048:
                ans = input('You got 2048! Do you want to continue? Y/N: ').strip().upper()
                if ans == 'Y':
                    break
            self.is_finished()
            self.pretty()
            step += 1

        if self.end:
            print(f'*GAME OVER*. \nFinal score {self.score}')

    def update(self, button):
        s = self.values.copy()
        match button:
            case 'a':
                # left
                self.shake_x()
            case 'd':
                # right
                self.shake_x(-1)
            case 'w':
                # up
                self.shake_y()
            case 's':
                # down
                self.shake_y(-1)
            case 'q':
                # front
                self.shake_z()
            case 'e':
                # rear
                self.shake_z(-1)

        changed = not ((self.values == s).all())
        if changed:
            self.add()

    def shake_x(self, direction=1):
        "shaking left (direction =1) or right (direction = -1)"
        for k in range(self.d):
            for i in range(self.d):
                sc, self.values[k, i, ::direction] = self.shake(self.values[k, i, ::direction], self.d)
                self.score += sc

    def shake_y(self, direction=1):
        "shaking up (direction =1) or down (direction = -1)"
        for k in range(self.d):
            for i in range(self.d):
                sc, temp = self.shake(self.values[k].T[i, ::direction], self.d)
                self.values[k, ::direction, i] = temp
                self.score += sc

    def shake_z(self, direction=1):
        "shaking front\to you (direction =1) or rear\back\from you (direction = -1)"
        for i in range(self.d):
            for j in range(self.d):
                sc, self.values[::direction, i, j] = self.shake(self.values[::direction, i, j], self.d)
                self.score += sc

    def is_finished(self):
        "Check if there is possible moves, updating bool self.end"
        is_empty = not (self.values == 0).any()
        if is_empty:
            is_possible = False
            k = 0
            while k < self.d and not is_possible:
                i = 0
                while i < self.d and not is_possible:
                    j = 0
                    while j < self.d and not is_possible:
                        neigb = []
                        for ii, jj, kk in possibilities:
                            i_n, j_n, k_n = i + ii, j + jj, k + kk
                            if 0 <= i_n < self.d and 0 <= j_n < self.d and 0 <= k_n < self.d:
                                neigb.append(self.values[k_n, i_n, j_n])

                        if self.values[k, i, j] in neigb:
                            is_possible = True
                        j += 1
                    i += 1
                k += 1
            if not is_possible:
                self.end = True

    @staticmethod
    def shake(vi, d=d):
        'Shaking one line to the left (from right to left)'
        vi = vi[vi > 0]
        result = []
        l = len(vi)
        sc = 0
        for ii in range(l):
            if ii <= l - 2 and vi[ii] == vi[ii + 1]:
                new = vi[ii] * 2
                result.append(new)
                sc += new
                vi[ii + 1] = 0
            elif vi[ii] == 0:
                pass
            else:
                result.append(vi[ii])
        result += [0] * (d - len(result))
        return sc, result




