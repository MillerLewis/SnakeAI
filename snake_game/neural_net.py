from functools import reduce

import numpy as np


class InvalidNetType(TypeError):
    pass


class Layer:
    BIAS = "bias"
    WEIGHTS = "weights"
    types = [BIAS, WEIGHTS]

    def __init__(self, array, type):
        self.array = array
        if type not in Layer.types:
            raise InvalidNetType
        self.type = type

    def forward_pass(self, inp):
        if inp == Layer.WEIGHTS:
            return np.matmul(inp, self.array)
        elif inp == Layer.BIAS:
            return inp + self.array

    def mutate_with_normal(self, mean=0, std=1):
        self.array += np.random.normal(loc=mean, scale=std, size=self.array.shape)

    def cross_over(self, other, cross_over_indices):
        if self.array.shape != other.array.shape:
            raise ValueError("Layers need to be same shape")

        cross_over_indices = list(sorted(cross_over_indices, reverse=True))
        first_array = np.empty(self.array.shape)
        second_array = np.empty(other.array.shape)
        rolling_index = 0

        cross_over_choice = 0
        indicies = cross_over_indices[0]

        for row_index in range(len(self.array)):
            for column_index in range(len(self.array[row_index])):
                if isinstance(indicies, list):
                    indicies = first_array.shape[1] * indicies[0] + indicies[1]

                if cross_over_indices and rolling_index >= indicies:
                    cross_over_choice += 1
                    indicies = cross_over_indices.pop()

                if cross_over_choice % 2 == 0:
                    first_array[row_index][column_index] = self.array[row_index][column_index]
                    second_array[row_index][column_index] = other.array[row_index][column_index]

                else:
                    first_array[row_index][column_index] = other.array[row_index][column_index]
                    second_array[row_index][column_index] = self.array[row_index][column_index]

                rolling_index += 1

        return Layer(first_array, self.type), Layer(second_array, other.type)

    def __str__(self):
        return str(self.array)

    def __repr__(self):
        return repr(self.array)


class NeuralNet:
    def __init__(self, net=[]):
        self.net = net

    def add_layer(self, layer):
        self.net.append(layer)

    def gen_output(self, inp):
        for layer in self.net:
            inp = layer.forward_pass(inp)

    def mutate_with_normal(self, mean=0, std=1):
        for layer in self.net:
            layer.mutate_with_normal(mean=mean, std=std)

    def cross_over(self, other, cross_over_indices_list):
        new_self_net = NeuralNet()
        new_other_net = NeuralNet()
        # list of multiple crossover indicies
        if len(self.net) != len(other.net) or len(self.net) != len(cross_over_indices_list):
            raise ValueError("Net's need to be same length and crossover indicies needs to be same length")
        for counter, (self_layer, other_layer) in enumerate(zip(self.net, other.net)):
            self_layer_to_add, other_layer_to_add = self_layer.cross_over(other_layer, cross_over_indices_list[counter])
            new_self_net.add_layer(self_layer_to_add)
            new_other_net.add_layer(other_layer_to_add)

        return new_self_net, new_other_net

    def __str__(self):
        return_str = ""
        for layer in self.net:
            return_str += str(layer) + "\n"
        return return_str

    def __repr__(self):
        return_repr = ""
        for layer in self.net:
            return_repr += repr(layer) + "\n"
        return return_repr


if __name__ == "__main__":
    first_net_first_layer = Layer(np.zeros(shape=(4, 4)), type=Layer.WEIGHTS)
    first_net_second_layer = Layer(np.ones(shape=(3, 3)), type=Layer.WEIGHTS)

    first_net = NeuralNet([first_net_first_layer, first_net_second_layer])

    second_net_first_layer = Layer(2 * np.ones(shape=(4, 4)), type=Layer.WEIGHTS)
    second_net_second_layer = Layer(3 * np.ones(shape=(3,3)), type=Layer.WEIGHTS)

    second_net = NeuralNet([second_net_first_layer, second_net_second_layer])

    print(first_net)
    print()
    print(second_net)

    third_net, fourth_net = first_net.cross_over(second_net, [[5], [6]])

    print(third_net)
    print()
    print(fourth_net)

    # print(first_layer.cross_over(second_layer, [[1, 2]])[0])
