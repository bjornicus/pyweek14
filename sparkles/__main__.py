import pyglet
from pyglet.gl import *

class Grid(object):
    def __init__(self, width, height, square_size):
        self.width = width
        self.height = height
        self.square_size = square_size

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

        glColor4f(1, 1, 1, 1)

def main():
    """ your app starts here
    """
    window = pyglet.window.Window()

    label = pyglet.text.Label('whining',
                          font_name='Times New Roman',
                          font_size=16,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

    grid = Grid(window.width, window.height, 20)

    @window.event
    def on_draw():
        window.clear()
        label.draw()
        grid.draw()


    pyglet.app.run()


if __name__ == "__main__":
    main()
