import pyglet
from pyglet.gl import *

def main():
	""" your app starts here
	"""
	window = pyglet.window.Window()

	label = pyglet.text.Label('whining',
                          font_name='Times New Roman',
                          font_size=16,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

	@window.event
	def on_draw():
		window.clear()
		label.draw()

		glColor4f(0.3, 0.8, 0.8, 1)
		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (0, 0, window.width, window.height))
		)

		glColor4f(1, 1, 1, 1)
		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                    ('v2i', (0, window.height, window.width, 0))
		)

	pyglet.app.run()
