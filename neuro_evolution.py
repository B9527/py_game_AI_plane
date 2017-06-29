# coding:utf-8
import math
import random

# 神经网络3层, 1个隐藏层; 4个input和1个output
network = [4, [16], 1]
# 遗传算法相关
population = 50
elitism = 0.2
random_behaviour = 0.1
mutation_rate = 0.5
mutation_range = 2
historic = 0
low_historic = False
score_sort = -1
n_child = 1


# 激活函数
def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


# random number
def random_clamped():
    return random.random() * 2 - 1


# "神经元"
class Neuron():
    def __init__(self):
        self.biase = 0
        self.weights = []

    def init_weights(self, n):
        self.weights = []
        for i in range(n):
            self.weights.append(random_clamped())

    def __repr__(self):
        return 'Neuron weight size:{}  biase value:{}'.format(len(self.weights), self.biase)


# 层
class Layer():
    def __init__(self, index):
        self.index = index
        self.neurons = []

    def init_neurons(self, n_neuron, n_input):
        self.neurons = []
        for i in range(n_neuron):
            neuron = Neuron()
            neuron.init_weights(n_input)
            self.neurons.append(neuron)

    def __repr__(self):
        return 'Layer ID:{}  Layer neuron size:{}'.format(self.index, len(self.neurons))


# 神经网络
class NeuroNetwork():
    def __init__(self):
        self.layers = []

    # input:输入层神经元数 hiddens:隐藏层 output:输出层神经元数
    def init_neuro_network(self, input, hiddens, output):
        index = 0
        previous_neurons = 0
        # input
        layer = Layer(index)
        layer.init_neurons(input, previous_neurons)
        previous_neurons = input
        self.layers.append(layer)
        index += 1
        # hiddens
        for i in range(len(hiddens)):
            layer = Layer(index)
            layer.init_neurons(hiddens[i], previous_neurons)
            previous_neurons = hiddens[i]
            self.layers.append(layer)
            index += 1
        # output
        layer = Layer(index)
        layer.init_neurons(output, previous_neurons)
        self.layers.append(layer)

    def get_weights(self):
        data = {'network': [], 'weights': []}
        for layer in self.layers:
            data['network'].append(len(layer.neurons))
            for neuron in layer.neurons:
                for weight in neuron.weights:
                    data['weights'].append(weight)
        return data

    def set_weights(self, data):
        previous_neurons = 0
        index = 0
        index_weights = 0

        self.layers = []
        for i in data['network']:
            layer = Layer(index)
            layer.init_neurons(i, previous_neurons)
            for j in range(len(layer.neurons)):
                for k in range(len(layer.neurons[j].weights)):
                    layer.neurons[j].weights[k] = data['weights'][index_weights]
                    index_weights += 1
            previous_neurons = i
            index += 1
            self.layers.append(layer)

    # 输入游戏环境中的一些条件(如敌机位置), 返回要执行的操作
    def feed_forward(self, inputs):
        for i in range(len(inputs)):
            self.layers[0].neurons[i].biase = inputs[i]

        prev_layer = self.layers[0]
        for i in range(len(self.layers)):
            # 第一层没有weights
            if i == 0:
                continue
            for j in range(len(self.layers[i].neurons)):
                sum = 0
                for k in range(len(prev_layer.neurons)):
                    sum += prev_layer.neurons[k].biase * self.layers[i].neurons[j].weights[k]
                self.layers[i].neurons[j].biase = sigmoid(sum)
            prev_layer = self.layers[i]

        out = []
        last_layer = self.layers[-1]
        for i in range(len(last_layer.neurons)):
            out.append(last_layer.neurons[i].biase)
        return out

    def print_info(self):
        for layer in self.layers:
            print(layer)


# "基因组"
class Genome():
    def __init__(self, score, network_weights):
        self.score = score
        self.network_weights = network_weights


class Generation():
    def __init__(self):
        self.genomes = []

    def add_genome(self, genome):
        i = 0
        for i in range(len(self.genomes)):
            if score_sort < 0:
                if genome.score > self.genomes[i].score:
                    break
            else:
                if genome.score < self.genomes[i].score:
                    break
        self.genomes.insert(i, genome)

    # 杂交+突变
    def breed(self, genome1, genome2, n_child):
        datas = []
        for n in range(n_child):
            data = genome1
            for i in range(len(genome2.network_weights['weights'])):
                if random.random() <= 0.5:
                    data.network_weights['weights'][i] = genome2.network_weights['weights'][i]

            for i in range(len(data.network_weights['weights'])):
                if random.random() <= mutation_rate:
                    data.network_weights['weights'][i] += random.random() * mutation_range * 2 - mutation_range
            datas.append(data)
        return datas

    # 生成下一代
    def generate_next_generation(self):
        nexts = []
        for i in range(int(elitism * population)):
            if len(nexts) < population:
                nexts.append(self.genomes[i].network_weights)

        for i in range(int(random_behaviour * population)):
            n = self.genomes[0].network_weights
            for k in range(len(n['weights'])):
                n['weights'][k] = random_clamped()
            if len(nexts) < population:
                nexts.append(n)

        max_n = 0
        while True:
            for i in range(max_n):
                childs = self.breed(self.genomes[i], self.genomes[max_n], n_child if n_child > 0 else 1)
                for c in range(len(childs)):
                    nexts.append(childs[c].network_weights)
                    if len(nexts) >= population:
                        return nexts
            max_n += 1
            if max_n >= len(self.genomes) - 1:
                max_n = 0



class Generations():
    def __init__(self):
        self.generations = []

    def first_generation(self):
        out = []
        for i in range(population):
            nn = NeuroNetwork()
            nn.init_neuro_network(network[0], network[1], network[2])
            out.append(nn.get_weights())
        self.generations.append(Generation())
        return out

    def next_generation(self):
        if len(self.generations) == 0:
            return False

        gen = self.generations[-1].generate_next_generation()
        self.generations.append(Generation())
        return gen

    def add_genome(self, genome):
        if len(self.generations) == 0:
            return False

        return self.generations[-1].add_genome(genome)


class NeuroEvolution():
    def __init__(self):
        self.generations = Generations()

    def restart(self):
        self.generations = Generations()

    def next_generation(self):
        networks = []
        if len(self.generations.generations) == 0:
            networks = self.generations.first_generation()
        else:
            networks = self.generations.next_generation()

        nn = []
        for i in range(len(networks)):
            n = NeuroNetwork()
            n.set_weights(networks[i])
            nn.append(n)

        if low_historic:
            if len(self.generations.generations) >= 2:
                genomes = self.generations.generations[len(self.generations.generations) - 2].genomes
                for i in range(genomes):
                    genomes[i].network = None

        if historic != -1:
            if len(self.generations.generations) > historic + 1:
                del self.generations.generations[0:len(self.generations.generations) - (historic + 1)]

        return nn

    def network_score(self, score, network):
        self.generations.add_genome(Genome(score, network.get_weights()))
