# thanks to @edersantana and @fchollet for suggestions & help.

import numpy as np
from ple import PLE  # our environment
from ple.games.catcher import Catcher

from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import SGD

from example_support import ExampleAgent, ReplayMemory, loop_play_forever


class Agent(ExampleAgent):
    """
        Our agent takes 1D inputs which are flattened.
        We define a full connected model below.
    """

    def __init__(self, *args, **kwargs):
        ExampleAgent.__init__(self, *args, **kwargs)

        self.state_dim = self.env.getGameStateDims()
        self.state_shape = np.prod((num_frames,) + self.state_dim)
        self.input_shape = (batch_size, self.state_shape)

    def build_model(self):
        model = Sequential()
        model.add(Dense(
            input_dim=self.state_shape, output_dim=256, activation="relu", init="he_uniform"
        ))
        model.add(Dense(
            512, activation="relu", init="he_uniform"
        ))
        model.add(Dense(
            self.num_actions, activation="linear", init="he_uniform"
        ))

        model.compile(loss=self.q_loss, optimizer=SGD(lr=self.lr))

        self.model = model


def nv_state_preprocessor(state):
    """
        This preprocesses our state from PLE. We rescale the values to be between
        0,1 and -1,1.
    """
    # taken by inspection of source code. Better way is on its way!
    max_values = np.array([128.0, 20.0, 128.0, 128.0])
    state = np.array([state.values()]) / max_values

    return state.flatten()

if __name__ == "__main__":
    # this takes about 15 epochs to converge to something that performs decently.
    # feel free to play with the parameters below.

    # training parameters
    num_epochs = 15
    num_steps_train = 15000  # steps per epoch of training
    num_steps_test = 3000
    update_frequency = 4  # step frequency of model training/updates

    # agent settings
    batch_size = 32
    num_frames = 4  # number of frames in a 'state'
    frame_skip = 2
    # percentage of time we perform a random action, help exploration.
    epsilon = 0.15
    epsilon_steps = 30000  # decay steps
    epsilon_min = 0.1
    lr = 0.01
    discount = 0.95  # discount factor
    rng = np.random.RandomState(24)

    # memory settings
    max_memory_size = 100000
    min_memory_size = 1000  # number needed before model training starts

    epsilon_rate = (epsilon - epsilon_min) / epsilon_steps

    # PLE takes our game and the state_preprocessor. It will process the state
    # for our agent.
    game = Catcher(width=128, height=128)
    env = PLE(game, fps=60, state_preprocessor=nv_state_preprocessor)

    agent = Agent(env, batch_size, num_frames, frame_skip, lr,
                  discount, rng, optimizer="sgd_nesterov")
    agent.build_model()

    memory = ReplayMemory(max_memory_size, min_memory_size)

    env.init()

    for epoch in range(1, num_epochs + 1):
        steps, num_episodes = 0, 0
        losses, rewards = [], []
        env.display_screen = False

        # training loop
        while steps < num_steps_train:
            episode_reward = 0.0
            agent.start_episode()

            while env.game_over() == False and steps < num_steps_train:
                state = env.getGameState()
                reward, action = agent.act(state, epsilon=epsilon)
                memory.add([state, action, reward, env.game_over()])

                if steps % update_frequency == 0:
                    loss = memory.train_agent_batch(agent)

                    if loss is not None:
                        losses.append(loss)
                        epsilon = np.max(epsilon_min, epsilon - epsilon_rate)

                episode_reward += reward
                steps += 1

            if num_episodes % 5 == 0:
                print "Episode {:01d}: Reward {:0.1f}".format(num_episodes, episode_reward)

            rewards.append(episode_reward)
            num_episodes += 1
            agent.end_episode()

        print "\nTrain Epoch {:02d}: Epsilon {:0.4f} | Avg. Loss {:0.3f} | Avg. Reward {:0.3f}".format(epoch, epsilon, np.mean(losses), np.sum(rewards) / num_episodes)

        steps, num_episodes = 0, 0
        losses, rewards = [], []

        # display the screen
        env.display_screen = True

        # slow it down so we can watch it fail!
        env.force_fps = False

        # testing loop
        while steps < num_steps_test:
            episode_reward = 0.0
            agent.start_episode()

            while env.game_over() == False and steps < num_steps_test:
                state = env.getGameState()
                reward, action = agent.act(state, epsilon=0.05)

                episode_reward += reward
                steps += 1

                # done watching after 500 steps.
                if steps > 500:
                    env.force_fps = True
                    env.display_screen = False

            if num_episodes % 5 == 0:
                print "Episode {:01d}: Reward {:0.1f}".format(num_episodes, episode_reward)

            rewards.append(episode_reward)
            num_episodes += 1
            agent.end_episode()

        print "Test Epoch {:02d}: Best Reward {:0.3f} | Avg. Reward {:0.3f}".format(epoch, np.max(rewards), np.sum(rewards) / num_episodes)

    print "\nTraining complete. Will loop forever playing!"
    loop_play_forever(env, agent)
