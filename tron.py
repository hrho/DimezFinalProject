#!/usr/bin/python3


import sys
import pygame
import os
import math
from pygame.compat import geterror
from pygame.locals import *
import random

p1Direction = 'N'
p2Direction = 'N'
comDirection = 'N'
comDirectionR = 'N'
p1Lose = False
p2Lose = False
comLose = False
start = False
p1Ready = False
p2Ready = False

def load_image(name):
    try:
        image = pygame.image.load(name)
    except pygame.error:
        print('Cannot load image: ', name)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error:
        print ('Cannot load sound %s' % name)
        raise SystemExit(str(geterror()))
    return sound

#classes for our objects

class computer(pygame.sprite.Sprite):
    def __init__(self,posx,posy):
        self.posx = posx
        self.posy = posy
        self.color = (0,255,0)

    def move(self,pixarr):
        global comDirection
        global comDirectionR
        dx = 0
        dy = 0
        moveLeft = True
        moveRight = True
        moveUp = True
        moveDown = True
        #check each direction
        #check up
        for i in range(1,15):
            if pixarr[self.posx][self.posy+i] is not (0 or 65280):
                print(pixarr[self.posx][self.posy+i])
                moveUp = False
        #check down
        for i in range(1,15):
            if pixarr[self.posx][self.posy-i] is not (0 or 65280):
                print(pixarr[self.posx][self.posy-i])
                moveDown = False
        #check left
        for i in range(1,15):
            if pixarr[self.posx+i][self.posy] is not (0 or 65280):
                print(pixarr[self.posx+i][self.posy])
                moveLeft = False
        #check right
        for i in range(1,15):
            if pixarr[self.posx-i][self.posy] is not (0 or 65280):
                print(pixarr[self.posx-i][self.posy])
                moveRight = False

        if moveUp and moveRight and moveDown and moveLeft and comDirection is not 'N': #stay on track
            comDirection = comDirection
            print("stay")
        elif moveDown:
            comDirection = 'D'
            comDirectionR = 'U'
            dx = 0
            dy = 1
            print("down")
        elif moveRight:
            comDirection = 'R'
            comDirectionR = 'L'
            dx = 1
            dy = 0
            print("Right")
        elif moveUp:
            comDirection = 'U'
            comDirectionR = 'D'
            dx = 0
            dy = -1
            print("up")
        elif moveLeft:
            comDirection = 'L'
            comDirectionR = 'R'
            dx = -1
            dy = 0
            print("left")
        else:
            print("rajan rando")
            rando = ['U','D','L','R']
            while 1:
                r = random.choice(rando)
                print("direction is: ",comDirection)
                print("directionR is: ",comDirectionR)
                if r is not comDirectionR:
                    comDirection = r
                    if r == 'U':
                        comDirectionR = 'D'
                    elif r == 'D':
                        comDirectionR = 'U'
                    elif r == 'L':
                        comDirectionR = 'R'
                    elif r == 'R':
                        comDirectionR = 'L'
                    break

            

        self.posx = self.posx + dx
        self.posy = self.posy + dy 

    def update(self,back,pixarr):
        dx = 0
        dy = 0
        global comLose

        if comDirection == 'U':
            dx = 0
            dy = -10
            self.posx = self.posx + dx
            self.posy = self.posy + dy 

            for i in range(10,0,-1):
             #   print(pixarr[self.posx][self.posy+i])
                if pixarr[self.posx][self.posy+i] is not 0:
                    print('hit')
                    comLose = True
                    break
                back.set_at((self.posx,self.posy+i),self.color)


        elif comDirection == 'D':
            dx = 0
            dy = 10
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx][self.posy-i])
                if pixarr[self.posx][self.posy-i] is not 0:
                    print('hit')
                    comLose = True
                    break
                back.set_at((self.posx,self.posy-i),self.color)

        elif comDirection == 'L':
            dx = -10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx+i][self.posy])
                if pixarr[self.posx+i][self.posy] is not 0:
                    print ('hit')
                    comLose = True
                    break
                back.set_at((self.posx+i,self.posy),self.color)

        elif comDirection == 'R':
            dx = 10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            for i in range(10,0,-1):
              #  print(pixarr[self.posx-i][self.posy])
                if pixarr[self.posx-i][self.posy] is not 0:
                    print('hit')
                    comLose = True
                    break
                back.set_at((self.posx-i,self.posy),self.color)

        return back



class player(pygame.sprite.Sprite):
    def __init__(self,posx,posy,playnum):
        self.posx = posx
        self.posy = posy
        if playnum is 1:
            self.color = (255,0,0)
        else:
            self.color = (0,0,255)

    def move1(self,key):
        global p1Direction
        dx = 0
        dy = 0
        if key == 'L':
        #    print('moving left')
            p1Direction = 'L'
            dx = 1
            dy = 0
        elif key == 'R':
         #   print('moving right')
            p1Direction = 'R'
            dx = 1
            dy = 0
        elif key == 'U':
          #  print('moving up')
            p1Direction = 'U'
            dx = 0
            dy = 1
        elif key == 'D':
          #  print('moving down')
            p1Direction = 'D'
            dx = 0
            dy = 1

        self.posx = self.posx + dx
        self.posy = self.posy + dy

    def update1(self,back,pixarr):
        dx = 0
        dy = 0
        global p1Lose
        if p1Direction == 'U':
            dx = 0
            dy = -10
            self.posx = self.posx + dx
            self.posy = self.posy + dy 

            for i in range(10,0,-1):
             #   print(pixarr[self.posx][self.posy+i])
                if pixarr[self.posx][self.posy+i] is not 0:
                    print('hit')
                    p1Lose = True
                    break
                back.set_at((self.posx,self.posy+i),self.color)


        elif p1Direction == 'D':
            dx = 0
            dy = 10
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx][self.posy-i])
                if pixarr[self.posx][self.posy-i] is not 0:
                    print('hit')
                    p1Lose = True
                    break
                back.set_at((self.posx,self.posy-i),self.color)

        elif p1Direction == 'L':
            dx = -10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx+i][self.posy])
                if pixarr[self.posx+i][self.posy] is not 0:
                    print ('hit')
                    p1Lose = True
                    break
                back.set_at((self.posx+i,self.posy),self.color)

        elif p1Direction == 'R':
            dx = 10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            for i in range(10,0,-1):
              #  print(pixarr[self.posx-i][self.posy])
                if pixarr[self.posx-i][self.posy] is not 0:
                    print('hit')
                    p1Lose = True
                    break
                back.set_at((self.posx-i,self.posy),self.color)

        return back

    def move2(self,key):
        global p2Direction
        dx = 0
        dy = 0
        if key == 'L':
        #    print('moving left')
            p2Direction = 'L'
            dx = 1
            dy = 0
        elif key == 'R':
         #   print('moving right')
            p2Direction = 'R'
            dx = 1
            dy = 0
        elif key == 'U':
          #  print('moving up')
            p2Direction = 'U'
            dx = 0
            dy = 1
        elif key == 'D':
          #  print('moving down')
            p2Direction = 'D'
            dx = 0
            dy = 1

        self.posx = self.posx + dx
        self.posy = self.posy + dy

    def update2(self,back,pixarr):
        dx = 0
        dy = 0
        global p2Lose
        if p2Direction == 'U':
            dx = 0
            dy = -10
            self.posx = self.posx + dx
            self.posy = self.posy + dy 

            for i in range(10,0,-1):
             #   print(pixarr[self.posx][self.posy+i])
                if pixarr[self.posx][self.posy+i] is not 0:
                    print('hit')
                    p2Lose = True
                    break
                back.set_at((self.posx,self.posy+i),self.color)


        elif p2Direction == 'D':
            dx = 0
            dy = 10
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx][self.posy-i])
                if pixarr[self.posx][self.posy-i] is not 0:
                    print('hit')
                    p2Lose = True
                    break
                back.set_at((self.posx,self.posy-i),self.color)

        elif p2Direction == 'L':
            dx = -10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            
            for i in range(10,0,-1):
              #  print(pixarr[self.posx+i][self.posy])
                if pixarr[self.posx+i][self.posy] is not 0:
                    print ('hit')
                    p2Lose = True
                    break
                back.set_at((self.posx+i,self.posy),self.color)

        elif p2Direction == 'R':
            dx = 10
            dy = 0
            self.posx = self.posx + dx
            self.posy = self.posy + dy
            for i in range(10,0,-1):
              #  print(pixarr[self.posx-i][self.posy])
                if pixarr[self.posx-i][self.posy] is not 0:
                    print('hit')
                    p2Lose = True
                    break
                back.set_at((self.posx-i,self.posy),self.color)

        return back


    def return_pos(self):
        return self.posx, self.posy



def main():
    #Initialize
    pygame.init()
    screen = pygame.display.set_mode((500,500))
    pygame.display.set_caption('TRON')
    pygame.mouse.set_visible(1)

    #create background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0,0,0))
   
    #display background
    screen.blit(background, (0,0))
    pygame.display.flip()

    #prepare object
    clock = pygame.time.Clock()
    p1 = player(300,300,1)
    p2 = player(200,300,2)
  #  com = computer(400,400)
    #main loop
    going = True
    global p1Ready
    global p2Ready
    
    while going and not p2Lose and not p1Lose and not comLose:
        clock.tick(60)

        pixarray = pygame.PixelArray(background)
        p1_posx,p1_posy = p1.return_pos()
        p2_posx,p2_posy = p2.return_pos()
        #handle input
        for event in pygame.event.get():
     #       if event.type == pygame.KEYUP and not (p1Ready and p2Ready):
      #          if(event.key == K_DOWN or event.key == K_UP or event.key == K_LEFT or event.key == K_RIGHT):
       #             p1Ready = True
        #            print('p1 Ready')
         #       if(event.key == K_w or event.key ==K_a or event.key == K_d or event.key == K_s):
          #          p2Ready = True
           #         print('p2 Ready')

            if event.type == QUIT:
                going = False
            elif event.type == pygame.KEYUP:
                if event.key == K_UP:
                    p1.move1('U')
                elif event.key == K_DOWN:
                    p1.move1('D')               
                elif event.key == K_LEFT:
                    p1.move1('L')
                elif event.key == K_RIGHT:
                    p1.move1('R')
                elif event.key == K_w:
                    p2.move2('U')
                elif event.key == K_a:
                    p2.move2('L')
                elif event.key == K_d:
                    p2.move2('R')
                elif event.key == K_s:
                    p2.move2('D')

                p1_posx, p1_posy = p1.return_pos()
                p2_posx,p2_posy = p2.return_pos()
   #     com.move(pixarray)
        #update players
        background = p1.update1(background,pixarray)
        background = p2.update2(background,pixarray)
     #   background = com.update(background,pixarray)
        del pixarray
        #draw 
        screen.blit(background,(0,0))
        pygame.display.flip()
        pygame.display.update()

    #print who won
    if p1Lose and p2Lose:
        print("Tie!")
    elif p2Lose:
        print("Player 1 Wins!!!!")
    elif p1Lose:
        print("Player 2 Wins!!!!")
    elif comLose:
        print("Computer loses")

    #end loop, game over
    pygame.quit()

if __name__ == '__main__':
    main()
