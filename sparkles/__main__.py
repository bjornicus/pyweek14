import pyglet
from pyglet.gl import *
from pyglet.window import mouse

COLOR_COMPONENT_MAX = 16.0
SQUARE_SIZE = 20

class Grid(object):
    def __init__(self, width, height):
        super(Grid, self).__init__()
        self.width = width
        self.height = height
        self.x_count = width/SQUARE_SIZE
        self.y_count = height/SQUARE_SIZE
        self.cells = {}
        for x in range(self.x_count):
            for y in range(self.y_count):
                self.cells[x,y] = None
        self.cells[15,5] = ColorStreamSource(-1,0, COLOR_COMPONENT_MAX,0,0 )
        self.cells[30,1] = ColorStreamSource(0,1, 0, 0, COLOR_COMPONENT_MAX)
        self.cells[5,15] = ColorStreamSource(1,0, 0, COLOR_COMPONENT_MAX,0 )
        self.cells[2,20] = ColorStreamSource(0,-1, 0, COLOR_COMPONENT_MAX, COLOR_COMPONENT_MAX)
        self.update()

    def draw(self):
        self.draw_gridlines()
        self.draw_cells()

    def draw_cells(self):
        f = lambda x: isinstance(x, ColorStream)
        for stream in filter(f, self.cells.itervalues()):
            stream.draw()
        f = lambda x: isinstance(x, ColorSink)
        for stream in filter(f, self.cells.itervalues()):
            stream.draw()

    def update(self):
        f = lambda x: isinstance(x, ColorSink)
        for sink in filter(f, self.cells.itervalues()):
            sink.sources = []
            sink.update()
        for (coords, item) in self.cells.iteritems():
            if isinstance(item, ColorStream):
                self.update_colorstream(coords[0], coords[1], item)

    def update_colorstream(self, x, y, stream):
        x1 = x*SQUARE_SIZE + SQUARE_SIZE/2
        y1 = y*SQUARE_SIZE + SQUARE_SIZE/2
        stop = False
        while (not stop and x > 0 and x < self.x_count and y > 0 and y < self.y_count):
            x += stream.output_direction.x
            y += stream.output_direction.y
            if not self.cells.has_key((x,y)):
                break
            item = self.cells[x,y]
            if isinstance(item, ColorSink):
                item.add_source(stream)
                stop = True
        x2 = x*SQUARE_SIZE + SQUARE_SIZE/2
        y2 = y*SQUARE_SIZE + SQUARE_SIZE/2
        stream.origin = Vector2d(x1,y1)
        stream.end = Vector2d(x2,y2)

    def draw_gridlines(self):
        glColor4f(0.1, 0.1, 0.1, 0.5)
        for x in range(0, self.width, SQUARE_SIZE):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (x, 0, x, self.height))
            )

        for y in range(0, self.height, SQUARE_SIZE):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (0, y, self.width, y))
            )

    def handle_left_click(self, x, y):
        square = Vector2d(x/SQUARE_SIZE, y/SQUARE_SIZE)
        square_location = Vector2d(square.x*SQUARE_SIZE, square.y*SQUARE_SIZE)
        sink = ColorCollector(square_location)
        self.cells[square.x, square.y] = sink
        self.update()

    def handle_right_click(self, x, y):
        square = Vector2d(x/SQUARE_SIZE, y/SQUARE_SIZE)
        self.cells[square.x, square.y] = None
        self.update()

class Vector2d(object):
    def __init__(self, x, y):
        super(Vector2d, self).__init__()
        self.x = x
        self.y = y

class ColorStream(object):
    def __init__(self, x_out, y_out):
        super(ColorStream, self).__init__()
        self.output_direction = Vector2d(x_out, y_out)
        self.r = 0
        self.g = 0
        self.b = 0
        self.color = (0, 0, 0 )
        self.origin = Vector2d(0,0)
        self.end = Vector2d(0,0)

    def update_gl_color(self):
        self.color = (
                self.r/COLOR_COMPONENT_MAX, 
                self.g/COLOR_COMPONENT_MAX, 
                self.b/COLOR_COMPONENT_MAX
                )

    def draw(self):
        for i in range(1,4): 
            width = i*2
            alpha = 1-(i)/10.0
            color = self.color + (alpha,)
            glColor4f(*color)
            glLineWidth(width)
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (self.origin.x, self.origin.y, self.end.x, self.end.y))
            )

        glLineWidth(1)
        glColor4f(1, 1, 1, 1)

    
class ColorStreamSource(ColorStream):
    def __init__(self, x_out, y_out, r, g, b):
        super(ColorStreamSource, self).__init__(x_out, y_out)
        self.r = r
        self.g = g
        self.b = b
        self.update_gl_color()

class ColorSink(object):
    def __init__(self, location):
        super(ColorSink, self).__init__()
        self.location = location
        self.color = (0.5, 0.5, 0.5, 1)
        self.sources = []

    def draw(self):
        glColor4f(*self.color)
        x1 = self.location.x
        x2 = x1 + SQUARE_SIZE
        y1 = self.location.y
        y2 = y1 + SQUARE_SIZE

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (x1,y1, x1,y2, x2,y2, x2,y1))
        )
        glColor4f(1, 1, 1, 1)

    def update(self):
        pass

    def add_source(self, source):
        pass

class ColorCollector(ColorSink):
    def __init__(self, location):
        super(ColorCollector, self).__init__(location)

    def add_source(self, source):
        if not source in self.sources:
            self.sources.append(source)
        self.update()

    def update(self):
        r = 0.1
        g = 0.1
        b = 0.1
        for source in self.sources:
            r += source.r
            g += source.g
            b += source.b
        self.color = (r, g, b, 1.0)


def main():
    """ your app starts here
    """
    window = pyglet.window.Window()

    label = pyglet.text.Label('WINNING!',
                          font_name='Times New Roman',
                          font_size=16,
                          x=window.width//2, y=window.height - 20,
                          anchor_x='center', anchor_y='center')

    grid = Grid(window.width, window.height)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    @window.event
    def on_draw():
        window.clear()
        label.draw()
        grid.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:
            grid.handle_left_click(x,y)
        if button == mouse.RIGHT:
            grid.handle_right_click(x,y)

    pyglet.app.run()


if __name__ == "__main__":
    main()
