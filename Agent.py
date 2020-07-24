import random
import numpy as np
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter
from LakeMonsterSim import LakeMonsterSim


LR = 1e-3
sim = LakeMonsterSim()
sim.restart()
goal_steps = 2000
score_requirement = 10
initial_runs = 10000

tempGameMemory = []

def random_games():
    for episode in range(5):
        sim.restart()
        sim.render(True)
        sim.start(goal_steps,randomMovement)
        print(sim.reward)
            
def randomMovement(dist, goblinDist, angle):
    global tempGameMemory
    
    x = random.random()*2-1
    y = random.random()*2-1
    action = (x,y)
    observation = [dist, goblinDist, angle]
    tempGameMemory.append([observation,action])
    return action
    
def initial_population():
    global tempGameMemory
    training_data = []
    scores = []
    accepted_scores = []
    for i in range(initial_runs):
        tempGameMemory = []
        
        sim.restart()
        sim.render(False)
        sim.start(goal_steps,randomMovement)
        score = sim.reward
        scores.append(score)
        if(score >= score_requirement):
            accepted_scores.append(score)
            for data in tempGameMemory:
                training_data.append([data[0],data[1]])
        if i%(initial_runs/10)==0:
            print(i/(initial_runs/10)*10,"%")

    saved_data = np.array(training_data)
    np.save('saved_data.npy', saved_data)
    print("Mean of accepted scores: ",mean(accepted_scores))
    print("Median of accepted scores: ",median(accepted_scores))
    print("Number of accepted scores: ",len(accepted_scores))

    return training_data
            
def create_neural_network(input_size):
    network = input_data(shape=[None, input_size, 1], name='input')

    network = fully_connected(network, 128, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 512, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 128, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 2, activation='softmax')
    network = regression(network, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')
    
    model = tflearn.DNN(network, tensorboard_dir='log')

    return model

def train_model(training_data, model=False):
    X = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]),1)
    y = [i[1] for i in training_data]

    if not model:
        model = create_neural_network(input_size=len(X[0]))

    model.fit({'input':X},{'targets':y}, n_epoch=5, snapshot_step=500, show_metric=True, run_id='openaistuff')

    return model

def modelMovement(dist, goblinDist, angle):
    global tempGameMemory, model
    observation = [dist, goblinDist, angle]
    action = model.predict(np.array(observation).reshape(-1,len(observation),1))
    print(action)
    x = action[0][0]
    y = action[0][1]
    tempGameMemory.append([observation,action])
    return (x,y)

def test_model():
    global tempGameMemory
    scores = []
    for i in range(10):
        tempGameMemory = []
        sim.restart()
        sim.render(True)
        sim.start(goal_steps,modelMovement)
        score = sim.reward
        scores.append(score)

        
    
training_data = initial_population()
model = train_model(training_data)
test_model()


        


