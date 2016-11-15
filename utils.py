def fit_probability_distribution(relative_frequencies_dictionary):
    """Return a probability distribution fitted to the given relative-frequencies dictionary.

    This helper function is used in various config files.
    """
    frequencies_sum = float(sum(relative_frequencies_dictionary.values()))
    probabilities = {}
    for k in relative_frequencies_dictionary.keys():
        frequency = relative_frequencies_dictionary[k]
        probability = frequency / frequencies_sum
        probabilities[k] = probability
    fitted_probability_distribution = {}
    current_bound = 0.0
    for k in probabilities:
        probability = probabilities[k]
        probability_range_for_k = (current_bound, current_bound + probability)
        fitted_probability_distribution[k] = probability_range_for_k
        current_bound += probability
    # Make sure the last bound indeed extends to 1.0
    last_bound_attributed = list(probabilities)[-1]
    fitted_probability_distribution[last_bound_attributed] = (
        fitted_probability_distribution[last_bound_attributed][0], 1.0
    )
    return fitted_probability_distribution
