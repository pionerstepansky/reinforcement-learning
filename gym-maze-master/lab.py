import gym
import gym_maze
import random
import time
import numpy as np

session_n = 100
session_len = 20000
q_param = 0.9 
size = 100

class Agent():
    def __init__(self, states_n, actions_n):
        self.states_n = states_n
        self.actions_n = actions_n
        self.actions = np.arange(actions_n)
        self.policy = np.ones([states_n, actions_n]) / actions_n

    def get_action(self, state):
        prob = self.policy[state]
        action = np.random.choice(self.actions, p=prob)
        return int(action)

    def update_policy(self, elite_sessions):
        elite_states = []
        elite_actions = []

        for session in elite_sessions:
            states, actions, total_rewards = session
            elite_states.extend(states)
            elite_actions.extend(actions)
        new_policy = np.zeros((self.states_n, self.actions_n))
        for i in range(len(elite_states)):
            new_policy[elite_states[i]][elite_actions[i]] += 1
        for i in range(self.states_n):
            if sum(new_policy[i]) == 0:
                new_policy[i] += 1 / self.actions_n
            else:
                new_policy[i] /= sum(new_policy[i])
        
        self.policy = new_policy


env = gym.make("maze-sample-"+str(size)+"x"+str(size)+"-v0")

agent = Agent(size * size, 4)

def get_state(obs):
    return int(obs[0] * size + obs[1])

def get_session(session_len):
    obs = env.reset()
    states = []
    actions = []
    total_reward = 0
    for t in range(session_len):
        state = get_state(obs)
        states.append(state)
        action = agent.get_action(state)
        actions.append(action)
        obs, reward, done, _ = env.step(action)
        total_reward += reward
        if done:
            break
    session = [states, actions, total_reward]
    return session

def get_elite_sessions(sessions, q_param):
    total_rewards = np.array([session[2] for session in sessions])
    print(np.mean(total_rewards))
    quantile = np.quantile(total_rewards, q_param)
    elite_sessions = []
    for session in sessions:
        states, actions, total_reward = session
        if total_reward > quantile:
            elite_sessions.append(session)
    return elite_sessions


for _ in range(20):
    sessions = [get_session(session_len) for _ in range(session_n)]
    elite_sessions = get_elite_sessions(sessions, q_param)
    if len(elite_sessions) > 0:
        agent.update_policy(elite_sessions)

done = False
state = env.reset()
while not done:
    state, reward, done, _ = env.step(agent.get_action(get_state(state))) 
    env.render()
    time.sleep(0.1)







