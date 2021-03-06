import numpy as np
import copy

EPSILON = 10 ** -7


class SparseMatrix:
    def __init__(self, size, b, data=None, columns=False, from_matrix=None):
        self.size = size
        self.b = b
        self.data = [[] for i in range(self.size)]

        if from_matrix:
            self.__store_from_matrix__(from_matrix)

        if data:
            if columns:
                self.__store_as_columns__(data)
            else:
                self.__store__(data)

    def __store__(self, a):
        for line in a:
            self.append_element(line[1], [line[0], line[2]])

    def __store_as_columns__(self, a):
        for line in a:
            self.append_element(line[2], [line[0], line[1]])

    def __store_from_matrix__(self, a):
        for i in range(self.size):
            for j in range(self.size):
                self.append_element(i, [a[i][j], j])


    def insert_element(self, line, element):
        self.data[line].insert(self.get_index_of_insertion(self.data[line], element[1]), element)

    def append_element(self, line, element):
        pos = self.search_index(self.data[line], element[1])
        if pos != -1:
            self.data[line][pos][0] += element[0]
        else:
            self.data[line].insert(self.get_index_of_insertion(self.data[line], element[1]), copy.deepcopy(element))

    def get_index_of_insertion(self, line, column):
        size = len(line)

        if size == 0:
            return 0

        left = 0
        right = size - 1
        mid = 0
        while left < right:
            mid = (left + right) // 2
            if line[mid][1] == column:
                return mid + 1

            if column < line[mid][1]:
                right = mid - 1
            else:
                left = mid + 1

        return left + 1 if column > line[left][1] else left

    def dot_product(self, i, j, other):
        # result = self.basic_scalar_product(i, j, other)
        #
        # result = self.binary_scalar_product(i, j, other)

        result = self.merge_dot_product(i, j, other)

        return result

    def binary_dot_product(self, i, j, other):
        result = 0
        line1 = self.data[i]
        line2 = other.data[j]
        for element1 in line1:
            index = other.search_index(line2, element1[1])
            if index != -1:
                result += element1[0] * line2[index][0]
        return result

    def merge_dot_product(self, i, j, other):
        result = 0

        line1 = self.data[i]
        line2 = other.data[j]

        i = 0
        j = 0
        n = len(line1)
        m = len(line2)
        while i < n and j < m:
            c1 = line1[i][1]
            c2 = line2[j][1]

            if c1 == c2:
                result += line1[i][0] * line2[j][0]
                i += 1
                j += 1
            elif c1 > c2:
                j += 1
            else:
                i += 1
        return result

    def basic_dot_product(self, i, j, other):
        result = 0
        for k1 in range(len(self.data[i])):
            for k2 in range(len(other.data[j])):
                if self.data[i][k1][1] == other.data[j][k2][1]:
                    result += self.data[i][k1][0] * other.data[j][k2][0]
        return result

    def search_index(self, line, column):
        size = len(line)

        left = 0
        right = size - 1
        mid = 0
        while left <= right:
            mid = (left + right) // 2
            if line[mid][1] == column:
                return mid

            if column < line[mid][1]:
                right = mid - 1
            else:
                left = mid + 1

        return -1

    def verify(self, num=10):
        for i in range(len(self)):
            if len(self.data[i]) > num:
                raise Exception("More than {} elements on line ".format(num) + str(i))

    def multiply_vector(self, v):
        result = np.array([])

        for line in self.data:
            s = 0
            for element in line:
                s += element[0] * v[element[1]]
            result = np.append(result, s)

        return result

    def __eq__(self, other):
        for i in range(len(self.data)):
            for element in self.data[i]:
                pos = other.search_index(other.data[i], element[1])
                if (pos != -1 and abs(element[0] - other.data[i][pos][0]) > EPSILON) or pos == -1:
                    return False

        for i in range(len(other.data)):
            for element in other.data[i]:
                pos = self.search_index(self.data[i], element[1])
                if (pos != -1 and abs(element[0] - self.data[i][pos][0]) > EPSILON) or pos == -1:
                    return False

        return True

    def __sub__(self, other):
        # diff = np.linalg.norm([x - y for x, y in zip(self.b, other.b)])
        diff = 0
        for i in range(len(self.data)):
            for element in self.data[i]:
                pos = other.search_index(other.data[i], element[1])
                if pos != -1:
                    diff += np.linalg.norm(element[0] - other.data[i][pos][0])
                else:
                    print("error")
                    diff += np.linalg.norm(element[0])

        for i in range(len(other.data)):
            for element in other.data[i]:
                pos = self.search_index(self.data[i], element[1])
                if pos != -1:
                    diff += np.linalg.norm(element[0] - self.data[i][pos][0])
                else:
                    print("error")
                    diff += np.linalg.norm(element[0])

        return diff

    def __add__(self, other):
        result = SparseMatrix(self.size, [0 for i in range(self.size)])

        result.b = [x + y for x, y in zip(self.b, other.b)]

        for i in range(len(self)):
            for element in self.data[i]:
                result.append_element(i, element)

        for i in range(len(other)):
            for element in other.data[i]:
                result.append_element(i, element)

        return result

    def __mul__(self, other):
        result = SparseMatrix(self.size, [0 for i in range(self.size)])

        for i in range(len(self)):
            for j in range(len(other)):
                product = self.dot_product(i, j, other)
                if product != 0:
                    result.append_element(i, [product, j])

        return result

    def __str__(self):
        str1 = ""
        for i in range(len(self.data)):
            for element in self.data[i]:
                str1 += str((element[0], i, element[1])) + "\n"

        return str1

    def __len__(self):
        return len(self.data)

    def solve_Gauss_Sidel(self, epsilon, threshold, kmax):
        for i in range(len(self.data)):
            ok = False
            for j in range(len(self.data[i])):
                if i == self.data[i][j][1] and self.data[i][j][0] > epsilon:
                    ok = True
                    break
            if not ok:
                raise Exception("Matricea are 0 pe diagonala.")

        solution = np.zeros((self.size, ))
        tmp = self.b
        for k in range(kmax):
            print(k)
            for i in range(self.size):
                bi = self.b[i]
                big_sum = 0

                aii = 0
                for j in range(len(self.data[i])):
                    if self.data[i][j][1] == i:
                        aii = self.data[i][j][0]
                    else:
                        big_sum += self.data[i][j][0] * solution[self.data[i][j][1]]

                solution[i] = (bi - big_sum) / aii

            if np.linalg.norm(tmp - solution) < epsilon:
                break
            if np.linalg.norm(tmp - solution) > threshold:
                raise Exception("Divergenta!")
            tmp = np.array(solution)

        return solution
