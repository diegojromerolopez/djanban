class MockChart(object):
    def __init__(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass
    def render(self, *args, **kwargs): return "svg"
    def render_data_uri(self, *args, **kwargs): return "data:image/svg+xml;base64,..."

class Line(MockChart): pass
class HorizontalBar(MockChart): pass
class Bar(MockChart): pass
class Pie(MockChart): pass
class DateLine(MockChart): pass
class StackedBar(MockChart): pass
class Config(object): pass
