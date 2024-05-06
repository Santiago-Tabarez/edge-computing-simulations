class CPUCost:

    @staticmethod
    def linear_interpolation_weighted_price(min_cpu_price, max_cpu_price, min_cores_hosted, max_cores_hosted,
                                            allocation):
        price_per_unit = max_cpu_price - (
                (allocation - min_cores_hosted) / (max_cores_hosted - min_cores_hosted)) * (
                                 max_cpu_price - min_cpu_price)

        return price_per_unit * allocation

    # Will return the total cpu cost for a game
    # Grand coalition should be created before calling this function
    @staticmethod
    def get_total_cpu_cost(game):

        total_allocation = sum(game.grand_coalition.allocation)
        if game.min_cpu_price == game.max_cpu_price:
            p_cpu = game.min_cpu_price * total_allocation
        else:

            p_cpu = CPUCost.linear_interpolation_weighted_price(game.min_cpu_price, game.max_cpu_price,
                                                                game.min_cores_hosted,
                                                                game.max_cores_hosted, total_allocation)
        return p_cpu
