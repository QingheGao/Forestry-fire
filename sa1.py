from SALib.sample import saltelli
from SALib.analyze import sobol
from mesa.batchrunner import BatchRunner
from model import ForestFire
import pickle

problem = {
    'num_vars': 5,
    'names': ['fire_spread_param', 'number_firefighters', 'fire_line_margin', 'cut_down_amount',
              'firefighter_response_delay'],
    'bounds': [[0.003, 0.006], [1, 20], [1, 5], [100, 555], [1, 5]]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 100
max_steps = 50
distinct_samples = 10

# Set the outputs
model_reporters = {"Percentage lost": lambda m: m.percentage_lost(),
                   "Burnout time": lambda m: m.burnout_time
                   }

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples)

# READ NOTE BELOW CODE
batch = BatchRunner(ForestFire,
                    max_steps=max_steps,
                    variable_parameters={name: [] for name in problem['names']},
                    model_reporters=model_reporters)

count = 0
for i in range(replicates):
    for vals in param_values:
        # Change parameters that should be integers
        vals = list(vals)
        vals[1] = int(vals[1])
        vals[2] = int(vals[2])
        vals[3] = int(vals[3])
        vals[4] = int(vals[4])

        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        count += 1

        # clear_output()
        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

data = batch.get_model_vars_dataframe()
pickle.dump(data, open('data_fireline.p', 'wb'))
print(data)
