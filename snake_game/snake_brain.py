import random
from pprint import pprint

import numpy as np
import pygame

from snake_game.helper_functions import random_square

from snake_game.game_state import Game
from snake_game.snake import Snake
from snake_game.connection import Connection
from snake_game.neural_net import NeuralNet, Layer


class GameWithNet(NeuralNet):
    INPUT_NEURONS = 8

    def __init__(self, game, net=[]):
        self.game = game
        super().__init__(net)

    def gen_inputs(self):
        return_array = np.array([self.game.snake.distance_to_death(self.game.dims),
                         int(self.game.snake.is_food_left(self.game.food)),
                         int(self.game.snake.is_food_right(self.game.food)),
                         int(self.game.snake.is_food_ahead(self.game.food)),
                         self.game.snake.heading[0] == 1,
                         self.game.snake.heading[0] == -1,
                         self.game.snake.heading[1] == 1,
                         self.game.snake.heading == -1])

        if return_array.shape[0] != GameWithNet.INPUT_NEURONS:
            raise Exception("You've made an error changing GameWithNet")
        return return_array.transpose()

    def gen_output_for_game(self):
        return self.gen_output(self.gen_inputs())

    def evaluate(self):
        outputs = self.gen_output_for_game()
        return outputs.argmax()

    def update(self, screen_dims):
        option = self.evaluate()
        if option == 0:
            self.game.snake.change_heading(Snake.UP)
        elif option == 1:
            self.game.snake.change_heading(Snake.DOWN)
        elif option == 2:
            self.game.snake.change_heading(Snake.RIGHT)
        elif option == 3:
            self.game.snake.change_heading(Snake.LEFT)
        self.game.update(screen_dims)

    def add_randomised_layer_snake(self, layer_type, num_output_neurons, loc=0, scale=1):
        input_neurons = GameWithNet.INPUT_NEURONS if not self.net else self.net[-1].shape[1]
        self.add_randomised_layer(layer_type, input_neurons, num_output_neurons, loc=loc, scale=scale)

    @staticmethod
    def simulate_with_video(snake_brains, screen_width, screen_height, wait_til_close):
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))

        done = False
        one_alive = True
        while not done and (one_alive or wait_til_close):
            one_alive = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            screen.fill((0, 0, 0))

            for snake_brain in snake_brains:
                one_alive = one_alive or snake_brain.game.snake.alive
                snake_brain.update([screen_width, screen_height])
                snake_brain.draw(screen)
            pygame.display.flip()

        return snake_brains

    @staticmethod
    def simulate_no_video(snake_brains, screen_width, screen_height):
        while True in [snake_brain.game.snake.alive for snake_brain in snake_brains]:
            for snake_brain in snake_brains:
                snake_brain.update([screen_width, screen_height])

        return snake_brains

    @staticmethod
    def tournament_snake_brains(snake_brains, num_selected):
        best_brains = []

        brain_indicies = list(range(len(snake_brains)))

        while brain_indicies:
            brain_indicies_to_fight = []
            for _ in range(num_selected):
                brain_indicies_to_fight.append(brain_indicies.pop(random.randint(0, len(brain_indicies) - 1)))

            brain_fighting_scores = [snake_brains[index].game.score for index in brain_indicies_to_fight]

            # print(snake_brains[91])
            best_brains.append(
                snake_brains[brain_indicies_to_fight[brain_fighting_scores.index(max(brain_fighting_scores))]]
            )
            # best_brains.append(brains_to_fight.index(max([brain.game.score for brain in brains_to_fight])))

        return best_brains


    def draw(self, screen):
        self.game.draw(screen)

    def fresh_deep_copy(self):
        return GameWithNet(self.game.fresh_deep_copy(), self.net.deep_copy())

    def __str__(self):
        return_str = ""
        return_str += str(self.game)
        return_str += "\n"
        return_str += str(self.net)

    def __repr__(self):
        return repr(self.net)


if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
    tile_width, tile_height = 10, 10
    snake_starting_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    food_starting_pos = (50, 50)
    TICK_RATE = 100

    game = Game(snake_starting_pos,
                (tile_width, tile_height),
                food_starting_pos,
                (tile_width, tile_height),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                TICK_RATE)

    game_with_net = GameWithNet(game)
    game_with_net.add_randomised_layer_snake(Layer.WEIGHTS, 16, scale=1/25)
    game_with_net.add_randomised_layer_snake(Layer.WEIGHTS, 4, scale=1/25)

    # print(game_with_net.net[0].shape)

    # output = game_with_net.gen_output_for_game()
    # print(output)

    game_with_net.simulate_with_video([game_with_net], 400, 400, True)

class Brain:
    NUM_INPUTS = 8

    def __init__(self, game=None, connections=[]):
        self.game = Game((0, 0), (10, 10), (250, 250), (10, 10), (400, 400)) if not game else game

        self.compiled = False

        self.connections = connections

    def gen_inputs(self):
        return np.array([self.game.snake.distance_to_death((self.game.dims[0], self.game.dims[1])) / max(
            self.game.dims[0], self.game.dims[1]),
                         int(self.game.snake.is_food_left(self.game.food)),
                         int(self.game.snake.is_food_right(self.game.food)),
                         int(self.game.snake.is_food_ahead(self.game.food)),
                         self.game.snake.heading[0] == 1,
                         self.game.snake.heading[0] == -1,
                         self.game.snake.heading[1] == 1,
                         self.game.snake.heading == -1]).transpose()

    def add_zero_connections(self, num_output_neurons):
        input_neurons = Brain.NUM_INPUTS if not self.connections else self.connections[-1].shape[1]
        self.connections.append(Connection(np.zeros((input_neurons, num_output_neurons))))

    def add_connections(self, connection):
        self.connections.append(connection)

    @staticmethod
    def normal_add_to_connections(connection, mean=0, std=1):
        connection.array += np.random.normal(loc=mean, scale=std, size=connection.shape)

    def randomly_initialise_connections(self, mean=0, std=1):
        for connection in self.connections:
            self.normal_add_to_connections(connection, mean=mean, std=std)

    def gen_outputs(self):
        layer_output_values = self.gen_inputs()
        for connection in self.connections:
            layer_output_values = connection.forward_pass(layer_output_values)

        return layer_output_values

    def evaluate(self):
        outputs = self.gen_outputs()
        return outputs.argmax()

    def update(self, screen_dims):
        option = self.evaluate()
        if option == 0:
            self.game.snake.change_heading(Snake.UP)
        elif option == 1:
            self.game.snake.change_heading(Snake.DOWN)
        elif option == 2:
            self.game.snake.change_heading(Snake.RIGHT)
        elif option == 3:
            self.game.snake.change_heading(Snake.LEFT)
        self.game.update(screen_dims)

    def draw(self, screen):
        self.game.draw(screen)

    def fresh_deep_copy(self):
        return Brain(self.game.fresh_deep_copy(), self.connections)


# def rank_snake_brains(snake_brains):
#     # TODO: Actually make this work
#     ranks =  []
#     snake_brains_copy = np.copy(snake_brains)
#
#     while snake_brains_copy:
#         scores = np.asarray([snake_brain.game.score for snake_brain in snake_brains])
#         max_score = np.max(scores)
#
#         # ranks.append(((max_score, np.asarray(range(scores.shape[0]))[scores == max_score])))
#
#         snake_brains_copy = snake_brains_copy[]
#
#     return

def tournament_snake_brains(snake_brains, num_selected):
    best_brains = []

    brain_indicies = list(range(len(snake_brains)))

    while brain_indicies:
        brain_indicies_to_fight = []
        for _ in range(num_selected):
            brain_indicies_to_fight.append(brain_indicies.pop(random.randint(0, len(brain_indicies) - 1)))

        brain_fighting_scores = [snake_brains[index].game.score for index in brain_indicies_to_fight]

        # print(snake_brains[91])
        best_brains.append(
            snake_brains[brain_indicies_to_fight[brain_fighting_scores.index(max(brain_fighting_scores))]]
        )
        # best_brains.append(brains_to_fight.index(max([brain.game.score for brain in brains_to_fight])))

    return best_brains


def crossover_single_two_brains(snake_brain_one, snake_brain_two, crossover_ratio):
    # Crossover ratio, so that if = 0.3, 0.3 kept by first, and 0.7 left kept by right
    # will crossover each weights matrix

    pass


def crossover_single_point(snake_brains, crossover_index):
    new_snake_brains = []

    while len(new_snake_brains) < len(snake_brains):
        new_snake_brains.append(random.choices(snake_brains, k=2))


def add_weights_to_brain(snake_brain, connections_array):
    # connections is a list of connections
    # new_snake_brain = Brain(snake_brain.game)
    # new_snake_brain.game.snake.pos = (new_snake_brain.game.dims[0] // 2, new_snake_brain.game.dims[1] // 2)
    # new_snake_brain.game.food.pos = random_square(new_snake_brain.game.dims[0],
    #                                               new_snake_brain.game.dims[1],
    #                                               new_snake_brain.game.food.food_dims[0],
    #                                               new_snake_brain.game.food.food_dims[1])

    brain_copy = snake_brain.fresh_deep_copy()

    for snake_connection, connection in zip(brain_copy.connections, connections_array):
        snake_connection.array += connection

    return brain_copy


def mutate_random_weights_brain(snake_brain, mean=0, std=1):
    connections_to_add = []
    brain_copy = snake_brain.fresh_deep_copy()
    for connection in brain_copy.connections:
        connections_to_add.append(np.random.normal(loc=mean, scale=std, size=connection.shape))

    return add_weights_to_brain(brain_copy, connections_to_add)


def mutate_random_weights_brains_list(snake_brains_to_mutate, mean=0, std=1):
    mutated_brains = []
    for snake_brain in snake_brains_to_mutate:
        brain_copy = snake_brain.fresh_deep_copy()
        mutated_brains.append(mutate_random_weights_brain(brain_copy, mean=mean, std=std))

    return mutated_brains


def simulate_with_video(snake_brains, screen_width, screen_height, wait_til_close):
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))

    done = False
    one_alive = True
    while not done and (one_alive or wait_til_close):
        one_alive = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((0, 0, 0))

        for snake_brain in snake_brains:
            one_alive = one_alive or snake_brain.game.snake.alive
            snake_brain.update([screen_width, screen_height])
            snake_brain.draw(screen)
        pygame.display.flip()

    return snake_brains


def simulate_no_video(snake_brains, screen_width, screen_height):
    while True in [snake_brain.game.snake.alive for snake_brain in snake_brains]:
        for snake_brain in snake_brains:
            snake_brain.update([screen_width, screen_height])

    return snake_brains


def simulate(snake_brains, screen_width, screen_height, video=False, wait_til_close=True):
    if video:
        brains = simulate_with_video(snake_brains, screen_width, screen_height, wait_til_close=wait_til_close)
    else:
        brains = simulate_no_video(snake_brains, screen_width, screen_height)

    return brains


def sim_generation(snake_brains, screen_width, screen_height, video=False, wait_til_close=True, tournament_count=2,
                   mutate="normal", **kwargs):
    new_brains = simulate(snake_brains, screen_width, screen_height, video=video, wait_til_close=wait_til_close)
    new_brains = tournament_snake_brains(new_brains, tournament_count)

    if mutate == "normal":
        if "mean" not in kwargs or "std" not in kwargs:
            raise Exception
        else:
            new_brains += mutate_random_weights_brains_list(new_brains, **kwargs)

    print(max([brain.game.score for brain in snake_brains]))

    for brain in new_brains:
        brain.game.reset()

    return new_brains

# SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
#
# if __name__ == "__main__":
#     TICK_RATE = 1
#
#     NUM_SNAKES = 200
#     snake_brains = []
#
#     for generation_counter in range(NUM_SNAKES):
#         tile_width = 10
#         tile_height = 10
#         # snake_starting_pos = random_square(SCREEN_WIDTH, SCREEN_HEIGHT, tile_width, tile_height)
#         snake_starting_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
#         food_starting_pos = random_square(SCREEN_WIDTH, SCREEN_HEIGHT, tile_width, tile_height)
#         snake_brains.append(Brain(
#             Game(snake_starting_pos,
#                  (tile_width, tile_height),
#                  food_starting_pos,
#                  (tile_width, tile_height),
#                  (SCREEN_WIDTH, SCREEN_HEIGHT),
#                  TICK_RATE), connections=[]))
#
#         snake_brains[-1].add_zero_connections(8)
#         snake_brains[-1].add_zero_connections(8)
#         snake_brains[-1].add_zero_connections(4)
#         snake_brains[-1].randomly_initialise_connections(mean=0, std=10)
#
#     GENERATIONS_TO_SIMULATE = 1000
#
#     for generation_counter in range(GENERATIONS_TO_SIMULATE):
#         print("Simulating generation {} / {}".format(generation_counter + 1, GENERATIONS_TO_SIMULATE))
#         snake_brains = sim_generation(snake_brains, SCREEN_WIDTH, SCREEN_HEIGHT, video=True, wait_til_close=False,
#                                       tournament_count=2, mutate="normal", mean=0, std=0.1)
#         # snake_brains = simulate(snake_brains, SCREEN_WIDTH, SCREEN_HEIGHT, video=True)
#
#     best_snake = tournament_snake_brains(snake_brains, len(snake_brains))[0]
#     best_snake.game.reset()
#     best_snake.game.tick_rate = 100
#     simulate([best_snake], SCREEN_WIDTH, SCREEN_HEIGHT, video=True, wait_til_close=True)
