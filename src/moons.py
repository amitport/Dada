from copy import deepcopy
import numpy as np

from sklearn.utils import shuffle

from evaluation import clf_variance, central_accuracy, central_loss, accuracies
from network import line_network, synthetic_graph, true_theta_graph
from optimization import centralized_FW, regularized_local_FW, local_FW, async_regularized_local_FW, global_regularized_local_FW
from related_works import colearning
from utils import generate_models, generate_moons

import matplotlib.pyplot as plt

# set graph of nodes with local personalized data
NB_ITER = 500
N = 100
D = 20
NOISE_R = 0.05
random_state = 2017
MU = 1

V, theta_true, cluster_indexes = generate_models(nb_clust=1, nodes_per_clust=N, random_state=random_state)
_, X, Y, X_test, Y_test, _, _ = generate_moons(V, theta_true, D, random_state=random_state, sample_error_rate=NOISE_R)

# set graph
nodes, adj_matrix, similarities = synthetic_graph(X, Y, X_test, Y_test, V, theta_true)

# set callbacks for optimization analysis
callbacks = {
    'accuracy': [central_accuracy, []]
}

results = {}

nodes_copy = deepcopy(nodes)
results["centralized"] = centralized_FW(nodes_copy, D, NB_ITER, callbacks=callbacks)

nodes_copy = deepcopy(nodes)
results["regularized"] = regularized_local_FW(nodes_copy, D, NB_ITER, mu=MU, callbacks=callbacks)

nodes_copy = deepcopy(nodes)
results["async_regularized"] = async_regularized_local_FW(nodes_copy, D, NB_ITER, mu=MU, callbacks=callbacks)

nodes_copy = deepcopy(nodes)
results["local"] = local_FW(nodes_copy, D, NB_ITER, callbacks=callbacks)

nodes_copy = deepcopy(nodes)
results["global-reg"] = global_regularized_local_FW(nodes_copy, D, NB_ITER, callbacks=callbacks)

# colearning results
results["colearning"] = colearning(N, X, Y, X_test, Y_test, D, NB_ITER, adj_matrix, similarities)

# get results with true thetas
true_graph = true_theta_graph(nodes_copy, theta_true)
acc = central_accuracy(true_graph)

plt.figure(1, figsize=(18, 10))

plt.subplot(211)
plt.xlabel('nb iterations')
plt.ylabel('train accuracy')

for k, r_list in results.items():
    plt.plot(range(len(r_list)), [r['accuracy'][0] for r in r_list], label='{}'.format(k))
# add results of true thetas
plt.plot(range(len(r_list)), [acc[0]]*len(r_list), label='true-theta')
plt.legend()

plt.subplot(212)
plt.xlabel('nb iterations')
plt.ylabel('test accuracy')

for k, r_list in results.items():
    plt.plot(range(len(r_list)), [r['accuracy'][1] for r in r_list], label='{}'.format(k))
plt.plot(range(len(r_list)), [acc[1]]*len(r_list), label='true-theta')
plt.legend()

plt.show()