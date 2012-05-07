import pyglet
from pyglet.gl import *
from pyglet.window import mouse

class Grid(object):
    def __init__(self, width, height, square_size):
        self.width = width
        self.height = height
        self.square_size = square_size
        self.x_count = width/square_size
        self.y_count = height/square_size
        self.selected = (10, 20)

    def draw(self):
        glColor4f(0.3, 0.3, 0.3, 5)
        for x in range(0, self.width, self.square_size):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (x, 0, x, self.height))
            )

        for y in range(0, self.height, self.square_size):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (0, y, self.width, y))
            )

        glColor4f(1, 0, 0, 0.5)
        x1 = self.selected[0] * self.square_size
        x2 = x1 + self.square_size
        y1 = self.selected[1] * self.square_size
        y2 = y1 + self.square_size

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (x1,y1, x1,y2, x2,y2, x2,y1))
        )
        glColor4f(1, 1, 1, 1)

    def set_selected(self, x, y):
        self.selected = (x/self.square_size, y/self.square_size)

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
