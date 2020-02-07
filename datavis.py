import pickle
from SALib.analyze import sobol
import matplotlib.pyplot as plt
from itertools import combinations
import numpy as np

plt.rcParams['figure.figsize'] = 7, 5

data_fireline = pickle.load(open("data_fireline.p", "rb"))
data_ext = pickle.load(open("data_ext.p", "rb"))

def plot_index(s, params, i, title='', filename=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')
    plt.tight_layout()
    plt.savefig('images/' + filename)

problem_fireline = {
    'num_vars': 5,
    'names': ['fire_spread_param', 'number_firefighters', 'fire_line_margin','cut_down_amount','firefighter_response_delay'],
    'bounds': [[0.003, 0.006], [1, 20], [1, 5], [100, 555],[1,5]]
}

problem_ext = {
    'num_vars': 4,
    'names': ['fire_spread_param', 'number_firefighters', 'extinguish_difficulty', 'firefighter_response_delay'], 
    'bounds': [[0.003, 0.006], [1, 20], [1, 5], [1, 5]]
}

Si_fireline = sobol.analyze(problem_fireline, data_fireline['Percentage lost'].as_matrix(), print_to_console=True)
Si_ext = sobol.analyze(problem_ext, data_ext['Percentage lost'].as_matrix(), print_to_console=True)

# First order
plot_index(Si_fireline, problem_fireline['names'], '1', 'First order sensitivity_fireline', 'FOSfirelines.png')
plt.show()

# Second order
plot_index(Si_fireline, problem_fireline['names'], '2', 'Second order sensitivity_fireline', 'SOSfirelines.png')
plt.show()

# Total order
plot_index(Si_fireline, problem_fireline['names'], 'T', 'Total order sensitivity_fireline', 'TOSfirelines.png')
plt.show()


# First order
plot_index(Si_ext, problem_ext['names'], '1', 'First order sensitivity_ext', 'FOSext.png')
plt.show()

# Second order
plot_index(Si_ext, problem_ext['names'], '2', 'Second order sensitivity_ext', 'SOSext.png')
plt.show()

# Total order
plot_index(Si_ext, problem_ext['names'], 'T', 'Total order sensitivity_ext', 'TOSext.png')
plt.show()