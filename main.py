# -*- coding: utf-8 -*- 
import sys
import logging
import snake

from panda3d.core                   import Point2

from direct.showbase.ShowBase       import ShowBase
from direct.task.Task               import Task

from settings                       import *
from helpers                        import genLabelText, loadObject
from collections                    import deque
from random                         import randrange


class World( ShowBase ):
    def __init__ ( self ):
        ShowBase.__init__( self )
        self.mode           = False
        self.choose_mode    = False
        self.start = False
        self.disableMouse( )
        self.snake          = snake.Snake( body=[ (0, 1), (-1, 1), (-2, 1) ], fruit=(0, 1) )
        self.snake.gen_fruit( )

        self.escape_text    = genLabelText( "ESC  : Quit", 0 )
        self.restart_text    = genLabelText( "R  : Restart", 1 )
        self.mode_text      = genLabelText( "Press 'a' for caterpillar mode and 'd' for block mode", 3)
        self.score          = genLabelText( "SCORE: %s" % self.snake.get_score( ), 0, left=False )
        self.bricks         = deque()
        self.wall           = deque()
        self.bombs          = deque()
        with open('topscore.txt', 'r') as f:
            first_line = f.readline()
            f.close()
        self.top_score = first_line
        self.top_score_text          = genLabelText( "Top Score: %s" % self.top_score,2, left =True)

        self.accept( "escape",      sys.exit )
        self.accept( "r",       self.game_restart )

        self.accept( "arrow_up",    self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ NEG_X ] )
        self.accept( "arrow_right", self.snake.turn, [ POS_X ] )
        self.accept( "shift",       self.toggle_pause)
        self.accept( "a",       self.toggle_mode_one)
        self.accept("d",        self.toggle_mode_two)

        self.game_task      = taskMgr.add( self.game_loop, "GameLoop" )
        self.game_task.last = 0
        self.period         = 0.15
        self.timer_flag     = False
        self.pause          = False
        self.timer_start    = 0
        

    def game_loop( self, task ):
        if self.start == True:
            dt = task.time - task.last
            if self.timer_flag:
                if self.timer_start == 0:
                    self.timer_start = task.time
                timer_dt = task.time - self.timer_start
                self.update_timer(timer_dt)
                if (timer_dt >= 10.00):
                    self.check_top_score()
                    return task.done
            if not self.snake.alive: 
                self.check_top_score()
                return task.done
            if self.pause:
                return task.cont
        
            elif dt >= self.period:
                task.last = task.time
                self.check_bomb( )
                self.snake.move_forward( )
                self.snake.check_state( )
                self.update_snake( )
                self.update_fruit( )
                self.update_score( )
                return task.cont
            else:
                return task.cont

        else:
            if self.choose_mode:
                self.background     = loadObject( "background2", self.mode, scale=140, depth=200, transparency=False )
                self.gameboard      = loadObject( "background", self.mode, scale=39.5, depth=100, transparency=False )
                self.draw_snake( )
                self.make_fruit( )
                self.start = True
                self.mode_text.removeNode( )
                return task.cont

            return task.cont

    def game_restart( self ):
        for point in self.bricks:
            point.removeNode()
        for bomb in self.bombs:
            bomb.removeNode()
        self.fruit.removeNode()
        if self.timer_flag:
            self.timer.removeNode()
        self.bricks         = deque()
        self.wall           = deque()
        self.bombs           = deque()
        with open('topscore.txt', 'r') as f:
            best_score = f.readline()
            f.close()
        self.top_score = int(best_score)
        self.top_score_text.removeNode()
        self.top_score_text          = genLabelText( "Top Score: %s" % self.top_score,2, left =True)
        self.score.removeNode()
        self.taskMgr.remove("GameLoop")
        self.choose_mode    = False
        self.start          = False
        self.mode_text      = genLabelText( "Press 'a' for caterpillar mode and 'd' for block mode", 3)
        self.accept( "a",       self.toggle_mode_one)
        self.accept("d",        self.toggle_mode_two)
        self.game_task      = taskMgr.add( self.game_loop, "GameLoop" )
        self.game_task.last = 0
        self.period         = 0.15
        self.timer_flag     = False
        self.pause          = False
        self.timer_start    = 0

        self.snake          = snake.Snake( body=[ (0, 1), (-1, 1), (-2, 1) ], fruit=(0, 1) )
        self.snake.gen_fruit( )
        self.score          = genLabelText( "SCORE: %s" % self.snake.get_score( ), 0, left=False )

        self.accept( "arrow_up",    self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ NEG_X ] )
        self.accept( "arrow_right", self.snake.turn, [ POS_X ] )
        self.accept( "shift",       self.toggle_pause)





    def check_top_score(self):
        if self.snake.get_score( ) > self.top_score:
            self.top_score = self.snake.get_score( )
            logging.warning(self.top_score)
            with open('topscore.txt', 'w') as f:
                f.write(str(self.top_score))
                f.close()


    def draw_snake( self ):
        for point in self.snake.body:
            brick = loadObject( "cat", self.mode, pos=Point2( point[ X ], point[ Y ] ) )
            self.bricks.append( brick )

    def draw_wall( self ):
        for square in self.wall:
            bomb = loadObject( "bomb", self.mode, pos=Point2( square[ X ], square[ Y ] ) )
            self.bombs.append( bomb )

    def gen_wall( self ):
        while (len(self.wall) < 3):
            max_x_bomb_coord = (self.snake.fruit[X]+3) if ((self.snake.fruit[X] + 3) < MAX_X) else MAX_X-1
            max_y_bomb_coord = (self.snake.fruit[Y]+3) if ((self.snake.fruit[Y] + 3) < MAX_Y) else MAX_Y-1
           
            min_x_bomb_coord = (self.snake.fruit[X]-3) if ((self.snake.fruit[X] - 3) > MIN_X) else MIN_X+1
            min_y_bomb_coord = (self.snake.fruit[Y]-3) if ((self.snake.fruit[Y] - 3) > MIN_Y) else MIN_Y+1

            bomb = (randrange(min_x_bomb_coord , max_x_bomb_coord,1), randrange(min_y_bomb_coord, max_y_bomb_coord,1))
            #check that bomb isn't placed directly in front of snake            
            head = self.snake.body[0]
            next = ( head[X] + self.snake.vector[X], head[Y] + self.snake.vector[Y] )
            #check that bomb isn't on top of fruit
            if (next != bomb) and (bomb!=self.snake.fruit):
                self.wall.append(bomb)

    #
    def check_bomb( self ):
        head = self.snake.body[0]
        next = ( head[X] + self.snake.vector[X], head[Y] + self.snake.vector[Y] )
        for bomb in self.wall:
            if next == bomb:
                self.snake.alive = False



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
            if len(self.bombs)>0:
                for bomb in self.bombs:
                    bomb.removeNode()
                self.wall = deque()
                self.bombs = deque()

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
        randNumber = randrange(0, 10,1)
      
        if randNumber <4:
            self.fruit = loadObject( "cat", self.mode, pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.set_timer()
        elif 3< randNumber <7:
            self.fruit = loadObject( "cat1", self.mode,pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.speed_up()
        elif 6<randNumber<8:
            self.fruit = loadObject( "cat4", self.mode,pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.gen_wall( )
            self.draw_wall( )
        elif 7 < randNumber < 9:
            self.fruit = loadObject( "cat3", self.mode, pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.speed_down()
        else:
            self.fruit = loadObject( "cat2", self.mode, pos=Point2( self.snake.fruit[ X ], self.snake.fruit[ Y ] ) )
            self.change_keys()

    def update_fruit( self ):
        x, y = self.fruit.getX( ), self.fruit.getY( )
        if ( x, y ) != self.snake.fruit:
            self.fruit.setPos( self.snake.fruit[ X ], SPRITE_POS, self.snake.fruit[ Y ] )

    def update_score( self ):
        if self.score:
            self.score.removeNode( )
        self.score = genLabelText( "SCORE: %s" % self.snake.get_score( ), 0, left=False )

    def toggle_pause( self ):
        if self.pause:  self.pause = False
        else:           self.pause = True


    def toggle_mode_one( self ):
        if self.choose_mode == False:
            self.mode = True
        self.choose_mode = True
        

    def toggle_mode_two( self ):
        if self.choose_mode == False:
            self.mode = False
        self.choose_mode = True
        

    def check_start( self ):
        self.start = True


    def speed_up(self):
        if self.period >= .07 :
            self.period = self.period - .02

    def speed_down(self):
        if self.period <= .15:
            self.period = self.period + .03
    

    def set_timer(self):
        if self.timer_flag:
            self.timer.removeNode( )
        self.timer_flag = True
        self.timer = genLabelText( "TIMER: OFF" , 1, left=False )

    
   
    def update_timer( self, time):
        ttime = 10 - time
        if self.timer_flag:
            self.timer.removeNode( )
        self.timer = genLabelText( "TIMER: %s" % ttime, 1, left=False )


    def change_keys(self):
        self.accept( "arrow_up",    self.snake.turn, [ NEG_Y ] )
        self.accept( "arrow_down",  self.snake.turn, [ POS_Y ] )
        self.accept( "arrow_left",  self.snake.turn, [ POS_X ] )
        self.accept( "arrow_right", self.snake.turn, [ NEG_X ] )


                    
w   = World( )
w.run( )
