import numpy as np
from collections import deque

# keras and model related
from keras.models import Sequential
from keras.layers.core import Dense, Flatten
from keras.layers.convolutional import Convolution2D
from keras.optimizers import SGD, Adam, RMSprop
import theano.tensor as T


class ExampleAgent():
    """
        Implements a DQN-ish agent. It has replay memory and epsilon decay. It is missing model freezing. The models are sensitive to the parameters and if applied to other games must be tinkered with.

    """

    def __init__(self, env, batch_size, num_frames,
                 frame_skip, lr, discount, rng, optimizer="adam", frame_dim=None):

        self.env = env
        self.batch_size = batch_size
        self.num_frames = num_frames
        self.frame_skip = frame_skip
        self.lr = lr
        self.discount = discount
        self.rng = rng

        if optimizer == "adam":
            opt = Adam(lr=self.lr)
        elif optimizer == "sgd":
            opt = SGD(lr=self.lr)
        elif optimizer == "sgd_nesterov":
            opt = SGD(lr=self.lr, nesterov=True)
        elif optimizer == "rmsprop":
            opt = RMSprop(lr=self.lr, rho=0.9, epsilon=0.003)
        else:
            raise ValueError("Unrecognized optmizer")

        self.optimizer = opt

        self.frame_dim = self.env.getScreenDims() if frame_dim is None else frame_dim
        self.state_shape = (num_frames,) + self.frame_dim
        self.input_shape = (batch_size,) + self.state_shape

        self.state = deque(maxlen=num_frames)
        self.actions = self.env.getActionSet()
        self.num_actions = len(self.actions)
        self.model = None

    def q_loss(self, y_true, y_pred):
        # assume clip_delta is 1.0
        # along with sum accumulator.
        diff = y_true - y_pred
        _quad = T.minimum(abs(diff), 1.0)
        _lin = abs(diff) - _quad
        loss = 0.5 * _quad ** 2 + _lin
        loss = T.sum(loss)

        return loss

    def build_model(self):

        model = Sequential()
        model.add(Convolution2D(
            16, 8, 8, input_shape=(self.num_frames,) + self.frame_dim,
            subsample=(4, 4), activation="relu", init="he_uniform"
        ))
        model.add(Convolution2D(
            16, 4, 4, subsample=(2, 2), activation="relu", init="he_uniform"
        ))
        model.add(Convolution2D(
            32, 3, 3, subsample=(1, 1), activation="relu", init="he_uniform"
        ))
        model.add(Flatten())
        model.add(Dense(
            512, activation="relu", init="he_uniform"
        ))
        model.add(Dense(
            self.num_actions, activation="linear", init="he_uniform"
        ))

        model.compile(loss=self.q_loss, optimizer=self.optimizer)

        self.model = model

    def predict_single(self, state):
        """
            model is expecting a batch_size worth of data. We only have one states worth of
            samples so we make an empty batch and set our state as the first row.
        """
        states = np.zeros(self.input_shape)
        states[0, ...] = state.reshape(self.state_shape)

        return self.model.predict(states)[0]  # only want the first value

    def _argmax_rand(self, arr):
        # picks a random index if there is a tie
        return self.rng.choice(np.where(arr == np.max(arr))[0])

    def _best_action(self, state):
        q_vals = self.predict_single(state)

        return self._argmax_rand(q_vals)  # the action with the best Q-value

    def act(self, state, epsilon=1.0):
        self.state.append(state)

        action = self.rng.randint(0, self.num_actions)
        if len(self.state) == self.num_frames:  # we havent seen enough frames
            _state = np.array(self.state)

            if self.rng.rand() > epsilon:
                action = self._best_action(_state)  # exploit

        reward = 0.0
        for i in range(self.frame_skip):  # we repeat each action a few times
            # act on the environment
            reward += self.env.act(self.actions[action])

        reward = np.clip(reward, -1.0, 1.0)

        return reward, action

    def start_episode(self, N=3):
        self.env.reset_game()  # reset
        for i in range(self.rng.randint(N)):
            self.env.act(self.env.NOOP)  # perform a NOOP

    def end_episode(self):
        self.state.clear()


class ReplayMemory():

    def __init__(self, max_size, min_size):
        self.min_replay_size = min_size
        self.memory = deque(maxlen=max_size)

    def __len__(self):
        return len(self.memory)

    def add(self, transition):
        self.memory.append(transition)

    def train_agent_batch(self, agent):
        if len(self.memory) > self.min_replay_size:
            states, targets = self._random_batch(agent)  # get a random batch
            return agent.model.train_on_batch(states, targets)  # ERR?
        else:
            return None

    def _random_batch(self, agent):
        inputs = np.zeros(agent.input_shape)
        targets = np.zeros((agent.batch_size, agent.num_actions))

        seen = []
        idx = agent.rng.randint(
            0,
            high=len(
                self.memory) -
            agent.num_frames -
            1)

        for i in range(agent.batch_size):
            while idx in seen:
                idx = agent.rng.randint(0, high=len(
                    self.memory) - agent.num_frames - 1)

            states = np.array([self.memory[idx + j][0]
                               for j in range(agent.num_frames + 1)])
            art = np.array([self.memory[idx + j][1:]
                            for j in range(agent.num_frames)])

            actions = art[:, 0].astype(int)
            rewards = art[:, 1]
            terminals = art[:, 2]

            state = states[:-1]
            state_next = states[1:]

            inputs[i, ...] = state.reshape(agent.state_shape)
            # we could make zeros but pointless.
            targets[i] = agent.predict_single(state)
            Q_prime = np.max(agent.predict_single(state_next))

            targets[i, actions] = rewards + \
                (1 - terminals) * (agent.discount * Q_prime)

            seen.append(idx)

        return inputs, targets


def loop_play_forever(env, agent):
    # our forever play loop
    try:
        # slow it down
        env.display_screen = True
        env.force_fps = False

        while True:
            agent.start_episode()
            episode_reward = 0.0
            while env.game_over() == False:
                state = env.getGameState()
                reward, action = agent.act(state, epsilon=0.05)
                episode_reward += reward

            print "Agent score {:0.1f} reward for episode.".format(episode_reward)
            agent.end_episode()

    except KeyboardInterrupt:
        print "Exiting out!"
