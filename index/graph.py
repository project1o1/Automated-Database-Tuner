import matplotlib.pyplot as plt

def plot_graph(y):
    for i, yi in enumerate(y):
        plt.plot(y[:i+1], 'r')
        plt.pause(0.1)
        plt.draw()
    plt.ioff()
    plt.show()

# plot_graph(list(range(1, 15)))
