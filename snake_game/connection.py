import numpy as np


class Connection:
    def __init__(self, array, activation=None):
        self.array = array
        self.activation = activation

    def forward_pass(self, input):
        output = np.matmul(input, self.array)

        if self.activation == "relu":
            output = np.multiply(output, output >= 0)

        return output

    def __add__(self, other):
        self.array += other.array

    @property
    def shape(self):
        return self.array.shape


if __name__ == "__main__":
    test_connection = Connection(np.random.normal(loc=-1, size=(4, 10)))
    inp = np.random.normal(size=(25, 4))

    # print(test_connection.forward_pass(inp))

    test_connection.activation = "relu"
    # print(test_connection.forward_pass(inp))
