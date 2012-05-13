Your Game Title
===============

Entry in PyWeek #14  <http://www.pyweek.org/14/>
URL: http://pyweek.org/e/sparkles
Team: sparkles
Members: bjorn
License: public domain


Running the Game
----------------
Note: this game was developed using pyglet version 1.1.4; you will need to have pyglet installed to run it.

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py


How to Play the Game
--------------------

Click on the grid to add or rotate a wigit.

Your goal is to hit the target with the color that matches its border.

Development notes 
-----------------

Creating a source distribution with::

   python setup.py sdist

You may also generate Windows executables and OS X applications::

   python setup.py py2exe
   python setup.py py2app

Upload files to PyWeek with::

   python pyweek_upload.py

Upload to the Python Package Index with::

   python setup.py register
   python setup.py sdist upload

