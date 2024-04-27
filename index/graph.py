import matplotlib.pyplot as plt
import random
def plot_graph(y):
    for i, yi in enumerate(y):
        plt.plot(y[:i+1], 'r')
        plt.xlabel('Batch Number')
        plt.ylabel('Cost of execution') 
        plt.text(.01, .99, 'Normal Cost'+str(yi), ha='right', va='top')
        plt.text(.01, 1.5, 'Indexed Cost'+str(yi+random.random()*random.randint(1, 10)), ha='right', va='top')
        plt.pause(0.1)
        plt.draw()
    plt.ioff()
    plt.show()

# plot_graph(list(range(1, 15)))
