from model import ForestFire
from agents import FireFighter
import matplotlib.pyplot as plt
import numpy as np

# for the extinguish only

num_samples = 20
simulation_time = 50
repetitions = 50

fire_spread_param = 0.005
number_firefighters = 0
extinguish_difficulty = 2
firefighter_response_delay = 2



data = np.zeros((num_samples, simulation_time, repetitions))
for n in range(num_samples):
    for r in range(repetitions):
        ff = ForestFire(fire_spread_param=fire_spread_param[n],
                        firefighter_strategy=FireFighter.extinguish,
                        number_firefighters=number_firefighters,
                        extinguish_difficulty=extinguish_difficulty,
                        firefighter_response_delay=firefighter_response_delay)
        for t in range(simulation_time):
            ff.step()
            data[n][t][r] = ff.percentage_lost()

mean = np.zeros((num_samples, simulation_time))
error = np.zeros((num_samples, simulation_time))

for n in range(num_samples):
    for t in range(simulation_time):
        mean[n][t] = np.mean(data[n][t])
        error[n][t] = np.std(data[n][t])

for n in range(num_samples):
    x = np.linspace(0, simulation_time - 1, simulation_time)
    plt.plot(x, mean[n], label=str(fire_spread_param[n]))
    plt.fill_between(x, y1=mean[n]-error[n]/2, y2=mean[n]+error[n]/2, alpha=0.3)
# plt.errorbar(fire_spread_param, mean[:, -1], yerr=error[:, -1] / 2, fmt='o')

plt.legend()
plt.show()