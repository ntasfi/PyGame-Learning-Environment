import time
import numpy as np
from PLE import PLE
from examples.waterworld import WaterWorld

game = WaterWorld(num_creeps=10)
p = PLE(game, fps=30, frame_skip=1, num_steps=1, display_screen=False)

print "Initial information..."
print "getActionSet", p.getActionSet()
print "game_over", p.game_over()
print "lives", p.lives()
print "getScreenRGB.shape", p.getScreenRGB().shape, "getScreenRGB.dtype", p.getScreenRGB().dtype
print "getScreenGrayscale.shape", p.getScreenGrayscale().shape, "getScreenGrayscale.dtype", p.getScreenGrayscale().dtype
print "saveScreen", p.saveScreen("test.png")
print 'getScreenDims', p.getScreenDims()
print "_getReward", p._getReward()

raw_input("Press Enter to continue...")

def fake_work():
	sleep_amount = np.random.random_sample()/100.0
	time.sleep(sleep_amount)
	return sleep_amount

for i in range(3000):
	t_0 = time.time()
	work_time = fake_work()
	s = np.random.randint(0, 4)
	a = p.getActionSet()[s]
	r = p.act(a)

	if i % 100 == 0:
		print "Saving screen to file"
		p.saveScreen("test.png")

	if i % 300 == 0:
		print "Resetting game!"
		p.reset_game()

	time_per_tick = time.time() - t_0
	print "FPS: %0.5f. Reward: %d. frame_count: %d. Time per tick: %0.5f. work_time: %0.5f" % ( 
		p.game.clock.get_fps(),
		r, 
		p.frame_count, 
		time_per_tick,
		work_time
	)

	
	
