import sys
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# import simulator
from includes.simulator import *

# note: start time should be zero do not change it!
START_TIME = 0
END_TIME = 5

# bandwidth 
BW_HIGH = KBytes(12)  # 40M bit

# Default variables
PKT_SIZE = int(1450)
PKT_NUMS = int(2000)


####################### IMPLEMENT ###################
# problem 1: need to implement gamma function and plot
# hint: use `time_slice` variable
######################################################
def plot_gamma():
    time_scale = mSecond(1)  # 0.001sec or 1ms
    duration = END_TIME - START_TIME

    # given timeslice for x 
    time_slice = np.linspace(START_TIME, END_TIME, int(duration / time_scale))

    # implement gamma function and plot!
    # shape = alpha, scale = beta
    # gamma(shape, loc, scale).pdf(x)
    y1 = stats.gamma(2, 0, 2).pdf(time_slice)
    y2 = stats.gamma(2, 0, 1).pdf(time_slice)
    y3 = stats.gamma(4, 0, 2).pdf(time_slice)
    y4 = stats.gamma(6, 0, 2).pdf(time_slice)

    plt.plot(time_slice, y1, 'b', label='a=2, b=2')
    plt.plot(time_slice, y2, 'orange', label='a=2, b=1')
    plt.plot(time_slice, y3, 'green', label='a=4, b=2')
    plt.plot(time_slice, y4, 'r', label='a=6, b=2')
    plt.xlabel('time')
    plt.ylabel('bandwidth')
    plt.grid()
    plt.title('Gamma Distribution of bandwidth')

    plt.legend()
    plt.show()


def simulation():
    # packet generation with # of packets and size
    pkt_list = PacketGenerator(PKT_NUMS, PKT_SIZE)

    ############### IMPLEMENT ###########################
    # implement the base station's queue length threshold
    # default is max (length of packet_list)
    # case 1: unlimited threshold without congestion control
    # case 2: unlimited threshold with congestion control
    # case 3: limited threshold with congestion control
    #####################################################
    threshold_case_1 = len(pkt_list)  # max
    threshold_case_2 = len(pkt_list)  # max
    threshold_case_3 = 10

    # Case 1: simulator without congestion control with unlimited queue
    print("\nsimulation without congestion control")
    sim = Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=False, threshold=threshold_case_1)
    sim.execute()

    # Case 2: simulator with congestion control with unlimited queue
    print("\nsimulation with congestion control, Case 2")
    sim_cc = Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=True, threshold=threshold_case_2)
    sim_cc.execute()

    # Case 3: simulator with congestion control with queue length threshold
    print("\nsimulation with congestion control, Case 3")
    sim_cc = Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=True, threshold=threshold_case_3)
    sim_cc.execute()

    return 0


if __name__ == "__main__":
    plot_gamma()
    simulation()
