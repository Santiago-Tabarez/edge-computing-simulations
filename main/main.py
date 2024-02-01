import time

import os

import psutil

from controller.dao import save_simulation, save_game
from controller.game_controller import create_game, calculate_coal_payoff, shapley_value_payoffs, how_much_revenue_payment
from utils.yaml_data_reader import YAMLDataReader


def main():
    folder_path = '../games to process/'
    yaml_games_data = YAMLDataReader.read_yaml_files(folder_path)

    for game_data in yaml_games_data:

        start_sim = time.time()
        sim = create_game(game_data)
        print("Total amount games: ", len(sim.games))
        save_simulation(sim)
        game_num = 1
        for game in sim.games:
            start_game = time.time()

            for current_coalition in game.coalitions:
                calculate_coal_payoff(game, current_coalition)

            game.gran_coalition.shapley_value = shapley_value_payoffs(game)
            how_much_revenue_payment(game, game.gran_coalition.shapley_value, sum(game.gran_coalition.allocation))
            save_game(game, sim)

            # print(game)
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

            print("Estimated time for current file to complete simulation: ",
                  (time.time() - start_game) * (len(sim.games) - game_num),
                  "seconds")

            game_num += 1

        print("Total memory used by the process: ", psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, "MB")
        print("Time required for the simulation: ", round(time.time() - start_sim), "seconds")


if __name__ == '__main__':
    main()
