class Image(object):
    @staticmethod
    def new(*args, **kwargs): return Image()
    def save(self, *args, **kwargs): pass
    def show(self, *args, **kwargs): pass
    @staticmethod
    def open(*args, **kwargs): return Image()
    def resize(self, *args, **kwargs): return self
    def crop(self, *args, **kwargs): return self
    @staticmethod
    def init(): pass
    EXTENSION = {'JPG': 'JPEG', 'JPEG': 'JPEG', 'PNG': 'PNG', 'GIF': 'GIF'}

class ImageDraw(object):
    @staticmethod
    def Draw(image): return ImageDraw()
    def text(self, *args, **kwargs): pass
    def rectangle(self, *args, **kwargs): pass

class ImageFont(object):
    @staticmethod
    def truetype(*args, **kwargs): return ImageFont()
    def getsize(self, *args, **kwargs): return (10, 10)
