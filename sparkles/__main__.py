import pyglet
from pyglet.gl import *
from pyglet.window import mouse

COLOR_COMPONENT_MAX = 16.0

class Grid(object):
    def __init__(self, width, height, square_size):
        super(Grid, self).__init__()
        self.width = width
        self.height = height
        self.square_size = square_size
        self.x_count = width/square_size
        self.y_count = height/square_size
        #print self.x_count, self.y_count
        self.selected = Vector2d(10, 20)
        self.cells = {}
        for x in range(self.x_count):
            for y in range(self.y_count):
                self.cells[x,y] = []
        self.cells[15,5].append(ColorStreamSource(-1,0, COLOR_COMPONENT_MAX,0,0 ))
        self.cells[30,1].append(ColorStreamSource(0,1, 0, 0, COLOR_COMPONENT_MAX))
        self.cells[5,15].append(ColorStreamSource(1,0, 0, COLOR_COMPONENT_MAX,0 ))
        self.cells[2,20].append(ColorStreamSource(0,-1, 0, COLOR_COMPONENT_MAX, COLOR_COMPONENT_MAX))
        self.cells[10,5].append(ColorSink())

    def draw(self):
        self.draw_gridlines()
        self.draw_selected_square()
        self.draw_cells()

    def draw_cells(self):
        for x in range(self.x_count):
            for y in range(self.y_count):
                for item in self.cells[x,y]:
                    if isinstance(item, ColorStream):
                        self.update_colorstream(x, y, item)
                    if isinstance(item, ColorSink):
                        self.draw_colorsink(x, y)

    def draw_colorsink(self, x, y):
        glColor4f(0.5, 0.5, 0.5, 1)
        x1 = x * self.square_size
        x2 = x1 + self.square_size
        y1 = y * self.square_size
        y2 = y1 + self.square_size

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (x1,y1, x1,y2, x2,y2, x2,y1))
        )
        glColor4f(1, 1, 1, 1)

    def update_colorstream(self, x, y, stream):
        x1 = x*self.square_size + self.square_size/2
        y1 = y*self.square_size + self.square_size/2
        stop = False
        while (not stop and x > 0 and x < self.x_count and y > 0 and y < self.y_count):
            x += stream.output_direction.x
            y += stream.output_direction.y
            if not self.cells.has_key((x,y)):
                break
            for item in self.cells[x,y]:
                if isinstance(item, ColorSink):
                    stop = True
        x2 = x*self.square_size + self.square_size/2
        y2 = y*self.square_size + self.square_size/2
        stream.origin = Vector2d(x1,y1)
        stream.end = Vector2d(x2,y2)
        stream.draw()

    def draw_selected_square(self):
        glColor4f(1, 0, 0, 0.5)
        x1 = self.selected.x * self.square_size
        x2 = x1 + self.square_size
        y1 = self.selected.y * self.square_size
        y2 = y1 + self.square_size

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (x1,y1, x1,y2, x2,y2, x2,y1))
        )
        glColor4f(1, 1, 1, 1)

    def draw_gridlines(self):
        glColor4f(0.1, 0.1, 0.1, 0.5)
        for x in range(0, self.width, self.square_size):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (x, 0, x, self.height))
            )

        for y in range(0, self.height, self.square_size):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (0, y, self.width, y))
            )

    def set_selected(self, x, y):
        self.selected = Vector2d(x/self.square_size, y/self.square_size)
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
        self.r_gl = 0
        self.g_gl = 0
        self.b_gl = 0
        self.origin = Vector2d(0,0)
        self.end = Vector2d(0,0)

    def update_gl_colors(self):
        self.r_gl = r/COLOR_COMPONENT_MAX
        self.g_gl = g/COLOR_COMPONENT_MAX
        self.b_gl = b/COLOR_COMPONENT_MAX

    def draw(self):
        for i in range(1,4): 
            width = i*2
            alpha = 1-(i)/10.0
            glColor4f(self.r_gl, self.g_gl, self.b_gl, alpha)
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
        self.r_gl = r/COLOR_COMPONENT_MAX
        self.g_gl = g/COLOR_COMPONENT_MAX
        self.b_gl = b/COLOR_COMPONENT_MAX

class ColorSink(object):
    pass

def main():
    """ your app starts here
    """
    window = pyglet.window.Window()

    label = pyglet.text.Label('WINNING!',
                          font_name='Times New Roman',
                          font_size=16,
                          x=window.width//2, y=window.height - 20,
                          anchor_x='center', anchor_y='center')

    grid = Grid(window.width, window.height, 20)
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
            grid.set_selected(x,y)

    pyglet.app.run()


if __name__ == "__main__":
    main()
