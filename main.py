# -*- coding: utf-8 -*- 

import sys
import snake

from panda3d.core                   import Point2

from direct.showbase.ShowBase       import ShowBase
from direct.task.Task               import Task

from settings                       import *
from helpers                        import genLabelText, loadObject
from collections                    import deque
from random         import randrange

class World( ShowBase ):
    def __init__ ( self ):
        ShowBase.__init__( self )

        self.disableMouse( )
        self.snake          = snake.Snake( body=[ (0, 1), (-1, 1), (-2, 1) ], fruit=(0, 1) )
        self.snake.gen_fruit( )

        self.background     = loadObject( "background", scale=9000, depth=200, transparency=False )
        self.gameboard      = loadObject( "background", scale=39.5, depth=100, transparency=False )
        self.escape_text    = genLabelText( "ESC  : Quit", 0 )
        self.pause_text     = genLabelText( "SPACE: Pause", 1)
        self.score          = genLabelText( "SCORE: %s" % self.snake.get_score( ), 0, left=False )
        self.bricks         = deque( )
        

        self.draw_snake( )
        self.accept( "escape",      sys.exit )
        self.accept( "enter",       self.restart )
        self.accept( "arrow_up",    self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ NEG_X ] )
        self.accept( "arrow_right", self.snake.turn, [ POS_X ] )
        self.accept( "space",       self.toggle_pause )

        self.game_task      = taskMgr.add( self.game_loop, "GameLoop" )
        self.game_task.last = 0
        self.period         = 0.15
        self.timer_flag     = False
        self.pause          = False
        self.timer_start    = 0
        self.make_fruit( )

    def game_loop( self, task ):
        dt = task.time - task.last
        if self.timer_flag:
            if self.timer_start == 0:
                self.timer_start = task.time
            timer_dt = task.time - self.timer_start
            self.update_timer(timer_dt)
            if (timer_dt >= 10.00):
                return task.done
        if not self.snake.alive: 
            return task.done
        if self.pause:
            return task.cont
    
        elif dt >= self.period:
            task.last = task.time
            self.snake.move_forward( )
            self.snake.check_state( )
            self.update_snake( )
            self.update_fruit( )
            self.update_score( )
            return task.cont
        else:
            return task.cont


    def draw_snake( self ):
        for point in self.snake.body:
            brick = loadObject( "cat", pos=Point2( point[ X ], point[ Y ] ) )
            self.bricks.append( brick )

    def update_snake( self ):
        try:
            for i in xrange( len( self.snake.body ) ):
                point   = self.snake.body[ i ]
                brick   = self.bricks[ i ]
                brick.setPos( point[ X ], SPRITE_POS, point[ Y ] )
        except IndexError:
            self.reset()
            new_head    = self.fruit
            self.make_fruit( )
            self.bricks.appendleft( new_head )
 

    def reset(self):
        #self.period         = 0.15
        if self.timer_flag:
            self.timer.removeNode( )
        self.timer_flag = False
        self.timer_start = 0 
        self.accept( "arrow_up",    self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ NEG_X ] )
        self.accept( "arrow_right", self.snake.turn, [ POS_X ] )

    def make_fruit( self ):
        randNumber = randrange(0,4,1)
      
        if randNumber == 0:
            self.fruit = loadObject( "cat", pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.set_timer()
        elif randNumber == 1:
            self.fruit = loadObject( "cat1", pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.speed_up()
        elif randNumber == 2:
            self.fruit = loadObject( "cat2", pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.speed_down()
        else:
            self.fruit = loadObject( "cat3", pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.change_keys()

    def update_fruit( self ):
        x, y = self.fruit.getX( ), self.fruit.getY( )
        if ( x, y ) != self.snake.fruit:
            self.fruit.setPos( self.snake.fruit[ X ], SPRITE_POS, self.snake.fruit[ Y ] )

    def update_score( self ):
        if self.score:
            self.score.removeNode( )
        self.score = genLabelText( "Score: %s" % self.snake.get_score( ), 0, left=False )

    def toggle_pause( self ):
        if self.pause:  self.pause = False
        else:           self.pause = True


    def speed_up(self):
        if self.period >= .07 :
            self.period = self.period - .03

    def speed_down(self):
        if self.period <= .15:
            self.period = self.period + .03
    

    def set_timer(self):
        if self.timer_flag:
            self.timer.removeNode( )
        self.timer_flag = True
        self.timer = genLabelText( "TIMER: OFF" , 1, left=False )

    
   
    def update_timer( self, time):
        if self.timer_flag:
            self.timer.removeNode( )
        self.timer = genLabelText( "TIMER: %s" % time, 1, left=False )


    def change_keys(self):
        self.accept( "arrow_up",    self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ POS_X ] )
        self.accept( "arrow_right", self.snake.turn, [ NEG_X ] )


                    
w   = World( )
w.run( )
