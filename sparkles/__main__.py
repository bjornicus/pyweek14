import pyglet
import time
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import key

COLOR_COMPONENT_MAX = 16.0
SQUARE_SIZE = 20

class Vector2d(object):
    def __init__(self, x, y):
        super(Vector2d, self).__init__()
        self.x = x
        self.y = y

UP = Vector2d(0,1)
DOWN = Vector2d(0,-1)
LEFT = Vector2d(-1,0)
RIGHT = Vector2d(1,0)

things = []
window = None
thing_generator = None
label = None


def draw_gridlines(width, height):
    glColor4f(0.1, 0.1, 0.1, 0.5)
    for x in range(0, width, SQUARE_SIZE):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2i', (x, 0, x, height))
        )

    for y in range(0, height, SQUARE_SIZE):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2i', (0, y, width, y))
        )

def draw_cells():
    for stream in filter(lambda x: isinstance(x, ColorStream), things):
        stream.draw_stream()
    for sink in filter(lambda x: isinstance(x, ColorSink), things):
        sink.draw_sink()

def update_things():
    # reset all of the sinks
    sinks = filter(lambda x: isinstance(x, ColorSink), things)
    streams = filter(lambda x: isinstance(x, ColorStream), things)
    map(lambda sink: sink.reset_sources(), sinks)
    map(lambda stream: stream.clear_sink(), streams)

    recompute_graph()
        
    # now that all of the streams are connected up, 
    # do a pass to make sure they have the colors right
    map(lambda thing: thing.update_color(), things)

def recompute_graph(): 
    # follow the graph from each of the color sources to its eventual terminating sink
    # and connect each source to the next sink
    for source in filter(lambda x: isinstance(x, ColorStreamSource), things):
        visitcount = 0
        next_sink = find_next_sink(source.x, source.y, source.output_direction)
        while next_sink is not None:
            visitcount += 1
            if visitcount > len(things):
                raise AbortException("ABORT!")
            if isinstance(next_sink, ColorStreamSource):
                raise AbortException("ABORT!")
            source.set_sink(next_sink)
            next_sink.add_source(source)
            if isinstance(next_sink, ColorStream):
                source = next_sink
                if source.active:
                    next_sink = find_next_sink(source.x, source.y, source.output_direction)
                else:
                    next_sink = None
            else:
                next_sink = None            

def find_next_sink(x, y, direction):
    candidates = []
    #sinks = filter(lambda t: isinstance(t, ColorSink), things)
    sinks = things
    def xmin(thing1, thing2):
        if abs(x - thing1.x) < abs(x - thing2.x):
            return thing1
        return thing2
    def ymin(thing1, thing2):
        if abs(y - thing1.y) < abs(y - thing2.y):
            return thing1
        return thing2

    reduce_function = xmin
    if direction is RIGHT:
        candidates = filter(lambda sink: sink.y == y and sink.x > x, sinks)
    elif direction is LEFT:
        candidates = filter(lambda sink: sink.y == y and sink.x < x, sinks)
    elif direction is UP:
        candidates = filter(lambda sink: sink.x == x and sink.y > y, sinks)
        reduce_function = ymin
    elif direction is DOWN:
        candidates = filter(lambda sink: sink.x == x and sink.y < y, sinks)
        reduce_function = ymin

    if len(candidates) == 0:
        return None
    
    return reduce(reduce_function, candidates)


class Color(object):
    def __init__(self, r, g, b):
        super(Color, self).__init__()
        self.r = r
        self.g = g
        self.b = b

class Thing(object):
    def __init__(self, x, y):
        super(Thing, self).__init__()
        self.x = x
        self.y = y
        self.color = Color(0, 0, 0)
        self.glcolor = (0, 0, 0, 1)

    def update_color(self):
        pass

    def update_gl_color(self):
        self.glcolor = (
                self.color.r/COLOR_COMPONENT_MAX, 
                self.color.g/COLOR_COMPONENT_MAX, 
                self.color.b/COLOR_COMPONENT_MAX,
                1
                )


class ColorStream(Thing):
    def __init__(self, x, y):
        super(ColorStream, self).__init__(x, y)
        self.output_direction = LEFT
        self.sink = None
        self.active = False

    def clear_sink(self):
        self.sink = None        

    def set_sink(self, sink):
        self.sink = sink

    def rotate(self):
        sequence = [UP,RIGHT,DOWN,LEFT,UP]
        next_direction = sequence.index(self.output_direction) + 1
        self.output_direction = sequence[next_direction]

    def unrotate(self):
        sequence = [UP,LEFT,DOWN,RIGHT,UP]
        next_direction = sequence.index(self.output_direction) + 1
        self.output_direction = sequence[next_direction]


    def draw_stream(self):
        if not self.active:
            return
        offset = SQUARE_SIZE/2
        x1 = self.x+offset
        y1 = self.y+offset
        if self.sink is not None:
            x2 = self.sink.x+offset
            y2 = self.sink.y+offset
        else:
            x2 = x1 + self.output_direction.x*window.width
            y2 = y1 + self.output_direction.y*window.height
        for i in range(1,4): 
            width = i*2
            alpha = 1-(i)/10.0
            glcolor = self.glcolor[:3] + (alpha,)
            glColor4f(*glcolor)
            glLineWidth(width)
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v2i', (x1,y1, x2,y2) ))

        glLineWidth(1)
        glColor4f(1, 1, 1, 1)

    
class ColorStreamSource(ColorStream):
    def __init__(self, x, y, output_direction, color):
        super(ColorStreamSource, self).__init__(x, y)
        self.output_direction = output_direction
        self.color = color
        self.update_gl_color()
        self.active = True

class ColorSink(Thing):
    def __init__(self, x, y):
        super(ColorSink, self).__init__(x, y)
        self.reset_sources()
        self.reset_color()

    def draw_sink(self):
        x1 = self.x
        x2 = x1 + SQUARE_SIZE
        y1 = self.y
        y2 = y1 + SQUARE_SIZE
        self.draw_fill(x1,y1, x2,y2)
        self.draw_border(x1,y1, x2,y2)

    def draw_fill(self, x1,y1, x2,y2):
        glColor4f(*self.glcolor)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (x1,y1, x1,y2, x2,y2, x2,y1))
        )
        glColor4f(1, 1, 1, 1)

    def draw_border(self, x1,y1, x2,y2):
        glColor4f(*self.glborder_color)
        glBegin(GL_LINE_STRIP)
        glVertex2f(x1,y1)
        glVertex2f(x1,y2)
        glVertex2f(x2,y2)
        glVertex2f(x2,y1)
        glVertex2f(x1,y1)
        glEnd()
        glColor4f(1, 1, 1, 1)

    def update_color(self):
        pass

    def update(self):
        pass

    def add_source(self, source):
        pass

    def reset_sources(self):
        self.sources = []

    def reset_color(self):
        self.glcolor = (0.5, 0.5, 0.5, 1)
        self.glborder_color = (1,1,1, 0.5)

class Target(ColorSink):
    def __init__(self, x, y, target_color):
        super(Target, self).__init__(x, y)
        self.target_color = target_color
        self.glborder_color = (
                self.target_color.r/COLOR_COMPONENT_MAX, 
                self.target_color.g/COLOR_COMPONENT_MAX, 
                self.target_color.b/COLOR_COMPONENT_MAX,
                1
                )
    def draw_sink(self):
        glLineWidth(2)
        super(Target, self).draw_sink()
        glLineWidth(1)

    def add_source(self, source):
        self.active = True
        if source not in self.sources:
            self.sources.append(source)

    def update_color(self):
        count = len(self.sources)
        self.color = Color(0,0,0)
        # make sure any parents are already updated
        map(lambda stream: stream.update_color(), 
                filter(lambda thing: isinstance(thing, ColorStream), self.sources)
                )
        for source in self.sources:
            self.color = Color( self.color.r + source.color.r,
                           self.color.g + source.color.g,
                           self.color.b + source.color.b )
        t = self.target_color
        c = self.color
        if t.r == c.r and t.g == c.g and t.b == c.b:
            global label
            label = pyglet.text.Label('You Win!',
                      font_name='Times New Roman',
                      font_size=36,
                      x=window.width//2, y=3*window.height//4,
                      anchor_x='center', anchor_y='center')

        self.update_gl_color()


class Wall(ColorSink):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y)
    def update_color(self):
        pass
    def draw_border(self, x1,y1,x2,y2):
        pass

class Wigit(ColorSink, ColorStream):
    def __init__(self, x, y):
        super(Wigit, self).__init__(x, y)

    def add_source(self, source):
        self.active = True
        if source not in self.sources:
            self.sources.append(source)

    def rotate(self):
        super(Wigit, self).rotate()
        #TODO don't point back at any sources (keep rotating)

    def update_color(self):
        count = len(self.sources)
        self.color = Color(0,0,0)
        # make sure any parents are already updated
        map(lambda stream: stream.update_color(), 
                filter(lambda thing: isinstance(thing, ColorStream), self.sources)
                )
        if count == 1:
            source = self.sources[0]
            if self.output_direction == source.output_direction:
                c = source.color
                self.color = Color(c.r/2, c.g/2, c.b/2)
            else:
                self.color = source.color
        elif count > 1:
            color = Color(0,0,0)
            for source in self.sources:
                color = Color( color.r + source.color.r,
                               color.g + source.color.g,
                               color.b + source.color.b )
            self.color = color
        self.update_gl_color()


    def clear_sink(self):
        super(Wigit, self).clear_sink()
        self.active = False

    def reset_sources(self):
        super(Wigit, self).reset_sources()

def load_level():
    global window
    things.append(ColorStreamSource(
            window.width/4, -SQUARE_SIZE, 
            UP,
            Color(COLOR_COMPONENT_MAX, 0, 0)
            ))
    things.append(ColorStreamSource(
            window.width/2, -SQUARE_SIZE, 
            UP,
            Color(0,COLOR_COMPONENT_MAX,0)
            ))
    things.append(ColorStreamSource(
            3*window.width/4, -SQUARE_SIZE, 
            UP,
            Color(0, 0, COLOR_COMPONENT_MAX)
            ))
    attenuator = Wigit(window.width/2, window.height/4)
    attenuator.output_direction = UP
    things.append(attenuator)
    things.append(Target(
            window.width/2, window.height/2,
            Color(COLOR_COMPONENT_MAX/2, 
                  COLOR_COMPONENT_MAX/4, 
                  COLOR_COMPONENT_MAX/2)
            ))

class AbortException(Exception):
    pass

def main():
    """ your app starts here
    """
    global window
    global thing_generator
    window = pyglet.window.Window()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    thing_generator = lambda x, y: Wigit(x, y)

    load_level()
    update_things()

    @window.event
    def on_draw():
        window.clear()
        draw_gridlines(window.width, window.height)
        draw_cells()
        global label
        if label is not None:
            label.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        x = x - x%SQUARE_SIZE
        y = y - y%SQUARE_SIZE

        def try_to_rotate(thing):
            if not isinstance(thing, ColorStream):
                return
            for i in range(4):
                try:
                    thing.rotate()
                    recompute_graph()
                    break
                except AbortException:
                    pass

        if button == mouse.LEFT:
            f = lambda t: t.x == x and t.y == y
            selected_things = filter(f, things)
            if len(selected_things) == 0:
                new_thing = thing_generator(x,y)
                things.append(new_thing)
                try_to_rotate(new_thing)
                rollback = lambda : things.remove(new_thing)
            else: 
                try_to_rotate(selected_things[0])

        if button == mouse.RIGHT:
            f = lambda t: t.x == x and t.y == y
            selected_things = filter(f, things)
            for thing in selected_things:
                things.remove(thing)

        try:
            update_things()
        except AbortException:
            rollback()
            update_things()


    @window.event
    def on_key_press(symbol, modifiers):
        global thing_generator
        if symbol == key.S:
            thing_generator = lambda x, y: ColorStreamSource(
                    x,y, 
                    UP,
                    Color(COLOR_COMPONENT_MAX, 0, COLOR_COMPONENT_MAX)
                    )
        elif symbol == key.W:
            thing_generator = lambda x, y: Wall(x, y)
        elif symbol == key.T:
            thing_generator = lambda x, y: Target(x, y, Color(COLOR_COMPONENT_MAX, 0, 0))
        elif symbol == key.A:
            thing_generator = lambda x, y: Wigit(x, y)
        elif symbol == key.D:
            print " ------- "
            dump_things()

    pyglet.app.run()

def dump_things():
    for thing in things:
        print thing.x,thing.y, ' - ', thing

def draw_square(x,y):
    glColor4f(1,1,1,1)
    x2 = x + SQUARE_SIZE
    y2 = y + SQUARE_SIZE

    pyglet.graphics.draw(4, pyglet.gl.GL_LINES,
            ('v2i', (x,y, x,y2, x2,y2, x2,y))
    )

if __name__ == "__main__":
    main()
