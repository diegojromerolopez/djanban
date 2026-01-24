class OLS(object):
    def __init__(self, *args, **kwargs): pass
    def fit(self): return RegressionResult()

class RegressionResult(object):
    def predict(self, *args, **kwargs): return []
    def summary(self): return "summary"

def add_constant(data): return data
