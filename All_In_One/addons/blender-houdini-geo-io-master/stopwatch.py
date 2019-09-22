import time

class Stopwatch:
	def __init__(self):
		self.start = time.time()
		self.last_t = self.start

	def check(self, msg):
		t = time.time()
		print('{msg}\t\ttotal:{ts:.2f} \t\trap:{rap:.2f}'.format(
			msg=msg,
			ts=t - self.start,
			rap=t - self.last_t
		))
		self.last_t = t
