import random

import numpy as np
import pygame

from snake_game.game_state import Game
from snake_game.snake import Snake
from snake_game.neural_net import NeuralNet


class GameWithNet(NeuralNet):
    INPUT_NEURONS = 8
    paused = False
    slow_down = False
    slow_down_tick_speed = 200
    regular_tick_speed = 1
    showing_only_best = False

    def __init__(self, game, layers_list):
        self.game = game
        self.snake_dims = self.game.snake.snake_dims
        super().__init__(layers_list)

    def gen_inputs(self):
        # TODO: Fix this, maybe get a proper distance to death, as in, find the shortest distance to death based off of all the possible headings
        dir_to_food_inv = self.game.food_direction_inverse()
        # return_array = np.array([100 * self.game.snake.distance_to_death_inverse(self.game.dims, self.game.snake.heading),
        #                          100 * dir_to_food_inv[0], 100 * dir_to_food_inv[1]])


        dir_to_food_normalised = self.game.food_direction_normalised()
        return_array = np.array([
            100 * self.game.is_food_up(),
            100 * self.game.is_food_down(),
            100 * self.game.is_food_right(),
            100 * self.game.is_food_left(),
            # 100 * dir_to_food_normalised[0], 100 * dir_to_food_normalised[1],
            200 * self.game.snake.distance_to_death_inverse(self.game.dims, Snake.LEFT),
            200 * self.game.snake.distance_to_death_inverse(self.game.dims, Snake.UP),
            200 * self.game.snake.distance_to_death_inverse(self.game.dims, Snake.RIGHT),
            200 * self.game.snake.distance_to_death_inverse(self.game.dims, Snake.DOWN)
        ])

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

    def add_randomised_layer_snake_weights(self, num_output_neurons, loc=0, scale=1.0):
        input_neurons = GameWithNet.INPUT_NEURONS if not self.net else self.net[-1].shape[1]
        self.add_randomised_layer_weights(input_neurons, num_output_neurons, loc=loc, scale=scale)

    def add_randomised_layer_snake_bias(self, loc=0, scale=1.0):
        input_neurons = GameWithNet.INPUT_NEURONS if not self.net else self.net[-1].shape[1]
        self.add_randomised_layer_bias(input_neurons, loc=loc, scale=scale)

    @staticmethod
    def simulate_with_video(snake_brains, screen_width, screen_height, wait_til_close, print_inputs=False):
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))

        done = False
        one_alive = True
        while not done and (one_alive or wait_til_close):
            one_alive = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        GameWithNet.paused = not GameWithNet.paused
                    if event.key == pygame.K_s:
                        GameWithNet.slow_down = not GameWithNet.slow_down
                        for snake_brain in snake_brains:
                            snake_brain.game.tick_rate = GameWithNet.slow_down_tick_speed if GameWithNet.slow_down else GameWithNet.regular_tick_speed
                    if event.key == pygame.K_b:
                        GameWithNet.showing_only_best = not GameWithNet.showing_only_best

            screen.fill((0, 0, 0))

            # if print_inputs:
            #     print(snake_brains[0].gen_inputs())

            best_snake = snake_brains[0]
            if GameWithNet.showing_only_best:
                for snake_brain in snake_brains[1:]:
                    if snake_brain.game.score >= best_snake.game.score:
                        best_snake = snake_brain

            for snake_brain in snake_brains:
                one_alive = one_alive or snake_brain.game.snake.alive
                if not GameWithNet.paused:
                    snake_brain.update([screen_width, screen_height])

                if GameWithNet.showing_only_best and snake_brain == best_snake:
                    snake_brain.draw(screen)
                elif not GameWithNet.showing_only_best:
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
    def tournament_snake_brains(games_with_nets, num_selected):
        best_brains = []
        brain_indicies = list(range(len(games_with_nets)))

        while brain_indicies:
            brain_indicies_to_fight = []
            for _ in range(num_selected):
                brain_indicies_to_fight.append(brain_indicies.pop(random.randint(0, len(brain_indicies) - 1)))
            brain_fighting_scores = [games_with_nets[index].game.score for index in brain_indicies_to_fight]
            best_brains.append(
                games_with_nets[brain_indicies_to_fight[brain_fighting_scores.index(max(brain_fighting_scores))]]
            )

        return best_brains

    @staticmethod
    def cross_over_index_brains(games, cross_over_index):
        return_snake_brains = []
        choices = random.choices(list(range(len(games))), k=len(games))
        for snake_brain_counter in range(0, len(choices), 2):
            cross_over_snakes = (
                games[snake_brain_counter].cross_over_index_single(games[snake_brain_counter + 1],
                                                                   cross_over_index)
            )
            return_snake_brains += [*cross_over_snakes]

        if len(games) % 2 == 0:
            return_snake_brains.append(games[-1])

        return return_snake_brains

    def cross_over_uniform_single(self, other, cross_over_prob):
        net_one, net_two = super().cross_over_uniform_single(other, cross_over_prob)
        return GameWithNet(self.game.deep_copy(), net_one.net), GameWithNet(other.game.deep_copy(), net_two.net)

    @staticmethod
    def cross_over_uniform_brains(games, prob):
        return_snake_brains = []
        choices = random.choices(list(range(len(games))), k=len(games))
        for snake_brain_counter in range(0, len(choices), 2):
            cross_over_snakes = (
                games[snake_brain_counter].cross_over_uniform_single(games[snake_brain_counter + 1], prob)
            )
            return_snake_brains += [*cross_over_snakes]
        if len(games) % 2 == 0:
            return_snake_brains.append(games[-1])

        return return_snake_brains

    def draw(self, screen):
        self.game.draw(screen)

    def fresh_deep_copy(self):
        game = self.game.fresh_deep_copy()
        return GameWithNet(game, [layer.deep_copy() for layer in self.net])

    def deep_copy(self):
        game = self.game.deep_copy()
        return GameWithNet(game, [layer.deep_copy() for layer in self.net])

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
    TICK_RATE = GameWithNet.regular_tick_speed

    NUM_SNAKES = 200
    NUM_GENERATIONS = 50

    TOURNAMENT_COUNT = 2

    MUTATION_RATE = 1 / 200
    CROSS_OVER_RATE = 0.5

    all_games = []
    for snake_counter in range(NUM_SNAKES):
        game_counter = Game(snake_starting_pos,
                            (tile_width, tile_height),
                            food_starting_pos,
                            (tile_width, tile_height),
                            (SCREEN_WIDTH, SCREEN_HEIGHT),
                            TICK_RATE)

        game_with_net = GameWithNet(game_counter, layers_list=[])
        game_with_net.add_randomised_layer_snake_weights(64, loc=0, scale=1 / 25)
        game_with_net.add_randomised_layer_snake_bias(loc=0, scale=1 / 25)
        game_with_net.add_randomised_layer_snake_weights(64, loc=0, scale=1 / 25)
        game_with_net.add_randomised_layer_snake_bias(loc=0, scale=1 / 25)
        game_with_net.add_randomised_layer_snake_weights(4, loc=0, scale=1 / 25)
        game_with_net.add_randomised_layer_snake_bias(loc=0, scale=1 / 25)
        game_with_net.game.reset()

        all_games.append(game_with_net)

    best_snake, best_snake_score = None, 0

    for gen_counter in range(NUM_GENERATIONS):
        print("PERFORMING GENERATION {} / {}".format(gen_counter + 1, NUM_GENERATIONS))
        curr_games = all_games[-NUM_SNAKES:]
        GameWithNet.simulate_with_video(curr_games, 400, 400, False)

        curr_games = GameWithNet.tournament_snake_brains(curr_games, TOURNAMENT_COUNT)
        new_games_to_play = []

        for game in curr_games:
            if game.game.score >= best_snake_score:
                best_snake, best_snake_score = game.deep_copy(), game.game.score
            for _ in range(TOURNAMENT_COUNT):
                new_game_capped_one = game.deep_copy()
                new_game_capped_one.game.reset()
                new_game_capped_one.mutate_with_normal(loc=0, scale=MUTATION_RATE)
                new_game_capped_one.cap_one_value(-1, 1)

                new_games_to_play += [new_game_capped_one]

        print(best_snake_score)

        new_games_to_play = GameWithNet.cross_over_uniform_brains(new_games_to_play, CROSS_OVER_RATE)
        all_games += new_games_to_play

    # best_snake = GameWithNet.tournament_snake_brains(all_games, len(all_games))[0]
    best_snake.game.reset()
    best_snake.game.tick_rate = 50
    GameWithNet.simulate_with_video([best_snake], *best_snake.game.dims, True, True)
