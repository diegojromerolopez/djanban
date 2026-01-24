class SimpleExpSmoothing(object):
    def __init__(self, *args, **kwargs): pass
    def fit(self, *args, **kwargs): return SmoothingResult()

class Holt(SimpleExpSmoothing): pass

class SmoothingResult(object):
    def forecast(self, steps=1): return [0]*steps
