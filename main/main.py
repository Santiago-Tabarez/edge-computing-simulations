import time

import os

import psutil

from controller.game_controller import create_game, calculate_coal_payoff, shapley_value_payoffs, how_much_rev_paym, \
    save_game
from utils.yaml_data_reader import YAMLDataReader


def main():
    folder_path = '../games to process/'
    yaml_games_data = YAMLDataReader.read_yaml_files(folder_path)

    for game_data in yaml_games_data:

        start_sim = time.time()
        games = create_game(game_data)
        print("Total amount games: ", len(games))

        for game in games:
            start_game = time.time()

            for current_coalition in game.coalitions:
                calculate_coal_payoff(game, current_coalition)
                # print("players", current_coalition.players)
                # print("utilities", current_coalition.utilities)

            game.gran_coalition.shapley_value = shapley_value_payoffs(game)

            # print("Shapley value is (fair payoff vector):", game.gran_coalition.shapley_value, "\n")
            # print("Capacity:", sum(game.gran_coalition.allocation), "\n")
            # print("Resources split", game.gran_coalition.allocation, "\n")

            how_much_rev_paym(game, game.gran_coalition.shapley_value, sum(game.gran_coalition.allocation))

            # print("Revenues array:", res[0], "\n")
            # print("Payments array:", res[1], "\n")

            print(game)
            # checking if the calculation of payments and revenues is correct
            print("Checking the correctness of the revenues and payments vectors...\n")

            if abs(sum(game.gran_coalition.allocation) * game.price_cpu - sum(
                    game.gran_coalition.payments)) > 0.001 or abs(
                    sum(game.gran_coalition.revenues) - sum(game.gran_coalition.revenues)) > 0.001:
                print("ERROR: the sum of single payments (for each players) or revenues don't match the total "
                      "payment/revenues!")
            else:
                print("Total payment and sum of single payments and revenues are correct!\n")

            print("Total memory used by the process: ", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, "MB")
            print("Time required for the game: ", round(time.time() - start_game), "seconds")
            print("Estimated time for current file to complete simulation: ", (time.time() - start_game) * len(games),
                  "seconds")

            save_game(game)

        print("Total memory used by the process: ", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, "MB")
        print("Time required for the simulation: ", round(time.time() - start_sim), "seconds")


if __name__ == '__main__':
    main()
