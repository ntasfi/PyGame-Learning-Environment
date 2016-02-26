# PLE Interface Specifications

This allows you to control games from a common interface via a learning agent.

## Initialization Arguments



**game**: `ple.game`

> This is the game we want to learn on. See game doc for required methods and attributes..



**fps**: `int`

> sets the FPS we want the game to run at. default: `30`



**frame_skip**: `int`

> frame skipping rate. 1 indicates no frame skipping. default: `1`



**num_steps**: `int`

> number of times we repeat an action. can also be done via agent logic. default: `1`



**force_fps**: `bool`

> If set to `True` we find the time needed per step in the game to achieve the required fps. The time elapsed is provided to the step function of the game, which appropriately updates the positions and elements of the game elements. Forcing the fps does not introduce a delay. If set to `False` we let `PyGame.Clock.tick_busy_loop` delay to keep the game running slower than the given fps. This limits the speed of the game. default: `True`



**display_screen**: `bool`

> if `True` the game draws the screen for each step we perform. This causes slowdown so its best to keep it off while training. *Note:* It still opens up a blank window but does not draw to it. default: `False`



**NOOP**: `pygame.constants.keyboard`

> This is the key we send an NOOP's to the game. This can be adjusted to whatever you want such that pressing it does not cause action in the game. default: `K_F15`



## Initialization Methods



**.init()**

> ``.init()`` does the following: initializes PyGame (`pygame.init`), sets the provided `game` screen (`pygame.display`) and clock (`pygame.time`) variables. It then requests the game to initialize. This should be called explicitly after instantiation of PLE.

> **Parameters:** None

> **Returns:** None



## Action and Interaction Methods



**.act()**

> Performs an action to the game and returns the reward for said action. The user must check if game has ended and reset if needed. 

> **Parameters:** **action**: a `pygame.constant.keyboard` instance. Do not need to know key instance to use. See example below.

> **Returns:** **reward**: `float` of the reward, can be large continuous values.

**Example**
```python
p = PLE(game)
p.init()

for i in range(3000):
	selection = np.random.randint(0, 4) #randomly pick an action
	action = p.getActionSet()[selection] #get the pygame.constant.keyboard instance via index.
	reward = p.act(action) #perform action

```



**.getScreenDims()**

> Returns the width and height dimensions specified by the PyGame passed to the PLE's constructor.

> **Parameters:** None.

> **Returns:** **shape**: A tuple of the screen shape (width, height).



**.game_over()**

> Indicates if the game has ended.

> **Parameters:** None.

> **Returns:** bool.



**.reset_game()**

> Resets the game to a clean initial starting state.

> **Parameters:** None.

> **Returns:** None.



**.getActionSet()**

> Returns set of legal actions to perform on the game.

> **Parameters:** None.

> **Returns:** **actions**: Returns an array of `pygame.constant.keyboard` instances used by the game to control input.



**.getFrameNumber()**

> Returns the current frame number since starting PLE.

> **Parameters:** None.

> **Returns:** `int` of frames



**.getScreenGrayscale()**

> Returns a numpy matrix with shape equal to (screen_width, screen_height). The grayscale values are calculated using the *luminance* formula. The values are rounded and set as a `np.uint8` type.

> **Parameters:** None.

> **Returns:** **screen_grayscale** A numpy matrix with size equal to screen_width and screen_height. Type is `np.uint8`.



**.getScreenRBG()**

> Returns a numpy matrix of the current screen with shape equal to (screen_width, screen_height, 3). 

> **Parameters:** None.

> **Returns:** **screen_rgb** A numpy matrix with size equal to (screen_width, screen_height, 3). Type is `np.uint8`.



**.saveScreen()**

> Saves the current screen to file. Uses `pillow.Image` for saving. Internally called `.getScreenRGB()`.

> **Parameters:** **filename**: The filename to save as. Can attach the path desired as well.

> **Returns:** None.