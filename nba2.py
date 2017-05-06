from modes import backgrounds, chicago, jersey

import sys
import pygame
import os
import math
import zlib
import cPickle as pickle
from pygame.compat import geterror
from pygame.locals import *
import random

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

SERVER_HOST = 'ash.campus.nd.edu'
SERVER_PORT = 40053


class GameSpace:
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("NBA 2K18")
		# set game objects
		self.clock = pygame.time.Clock()
		# set variables in gs
		self.pressedKey = 0
		self.ready = 0
		self.quit = 0
		self.counted = 0
		self.mode = None
		# waiting bg screen
		tempbg = backgrounds[random.randint(0,1)]
		self.bg = pygame.image.load("images/" + tempbg['background_image'])
		self.bg = pygame.transform.scale(self.bg, tempbg['background_scale'])
		self.gameOver = 0
	def setup(self):
		self.tickNum = 0
		self.score1 = 0
		self.score2 = 0
		self.shot = Shot(self)
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.p2body = Player2Prop(self)
		self.endGame = GameOver(self)

		# background image
		self.bg = pygame.image.load("images/" + self.mode['background_image'])
		self.bg = pygame.transform.scale(self.bg, self.mode['background_scale'])
	def game_loop(self):
		if self.gameOver == 1:
			if self.score1 > 25:
				self.endGame.display(1)
			else:
				self.endGame.display(2)
			pygame.display.flip()
		elif self.ready == 1:
			# frame rate with tick
			self.clock.tick(60)
			# user inputs for slick controls
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.player2.toFire = 1
				if event.type == pygame.MOUSEBUTTONUP:
					self.player2.toFire = 0
			self.shot.tick()
			self.player1.tick()
			self.player2.tick()
			self.tickNum += 1
			for laser in self.player2.lasers:
				laser.tick()
			if self.counted == 1 and self.tickNum%3 == 0:
				laserListx = []
				laserListy = []
				laserListxm = []
				laserListym = []
				#list of shot drop to player 2
				for laser in self.player2.lasers:
					laserListx.append(laser.rect.centerx)
					laserListy.append(laser.rect.centery)
					laserListxm.append(laser.xm)
					laserListym.append(laser.ym)
				self.write(zlib.compress(pickle.dumps([self.player2.mx, self.player2.my, pickle.dumps(laserListx), pickle.dumps(laserListy), pickle.dumps(laserListxm), pickle.dumps(laserListym)])))
			self.counted = 1
			#display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.p2body.image, self.p2body.rect)
			self.screen.blit(self.player1.image, self.player1.rect)
			# lasers
			for laser in self.player2.lasers:
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			# text display, theres only 1 font?
			lt = pygame.font.Font('freesansbold.ttf', 115)
			TextS = lt.render(str(self.score1), True, (255, 0, 0))
			TextR = TextS.get_rect()
			TextS2 = lt.render(str(self.score2), True, (0, 0, 255))
			TextR2 = TextS2.get_rect()
			if self.score1 > self.score2:
				TextR.center = [TextR.size[1]/2, 50]
				TextR2.center = [TextR2.size[1]/2, 150]
			else:
				TextR.center = [TextR.size[1]/2, 150]
				TextR2.center = [TextR2.size[1]/2, 50]
			self.screen.blit(TextS2, TextR2)
			self.screen.blit(TextS, TextR)
			# player box
			self.screen.blit(self.player1.box.image, self.player1.box.rect)
			# bballs
			for ball in self.shot.drops:
				self.screen.blit(ball.image, ball.rect)
			pygame.display.flip()
			# end of kobe's game
			if self.score1 > 25 or self.score2 > 25:
				self.gameOver = 1
		else:
			self.screen.blit(self.bg, (0, 0))
			lt = pygame.font.Font('freesansbold.ttf', 50)
			TextS = lt.render("Waiting for P1...", True, (255, 255, 255))
			TextR = TextS.get_rect()
			self.screen.blit(TextS, TextR)
			pygame.display.flip()
	def write(self,data):
		pass
	def quit(self):
		pass

# gameover boyy
class GameOver(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
	def display(self, winner):
		self.gs.screen.fill((0,0,0))
		# player 1 winna
		if winner == 2:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			TextS = lt.render("YOU ARE THE NBA CHAMPION", True, (255, 255, 255))
		elif winner == 1:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			TextS = lt.render("You blew a 3-1 lead", True, (255, 255, 255))
		TextR = TextS.get_rect()
		TextR.center = [200, 300]
		self.gs.screen.blit(TextS, TextR)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gs.quit()

class Shot(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.addNew = False
		self.drops = []
	def tick(self):
		for ball in self.drops:
			ball.rect = ball.rect.move([0, 1])

class Dropshots(pygame.sprite.Sprite):
	def __init__(self, x, y, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.mode['ball_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.mode['blocker_body'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['sb_location']
# Player 1
class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.mode['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center,self.gs)
	def tick(self):
		pass
# catching balls lol
class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.mode['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0] + self.gs.mode['box_offset'][0]
		self.y = center[1] + self.gs.mode['box_offset'][1]
		self.rect.center = [self.x, self.y]

# the swatter
class Player2(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.realx = 1
		self.realy = 1
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.mode["hand_image"])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.mode['hand_location']
		self.lasers = []
		self.angle = 0
		self.orig_image = self.image
		self.toFire = 0
		self.fired = 0
	def tick(self):
		self.mx, self.my = pygame.mouse.get_pos()
		for ball in self.lasers:
			if ball.rect.center[0] < -20 or ball.rect.center[0] > 660:
				self.lasers.remove(ball)
			elif ball.rect.center[1] < -20 or ball.rect.center[1] > 500:
				self.lasers.remove(ball)
		if self.toFire == 1:
			self.realx = self.mx
			self.realy = self.my
			xSlope = self.realx - self.rect.center[0]
			ySlope = self.realy - self.rect.center[1]
			total = math.fabs(xSlope) + math.fabs(ySlope)
			if len(self.lasers) < 1:
				self.lasers.append(Laser(self.rect.center[0], self.rect.center[1], xSlope/total, ySlope/total, self.gs))
			self.toFire = 0
			self.fired = 1
		else:
		# player 2 rotates
			self.angle = math.atan2(self.my-self.rect.center[1], self.mx - self.rect.center[0])*-180/math.pi + 211.5 - self.gs.mode['angle_offset']
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = self.rect.center)
			self.toFire = 0

class Laser(pygame.sprite.Sprite):
	def __init__(self, xc=320, yc=240, xm=1, ym=1, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		xc = xc + xm*self.gs.mode['bullet_offset']
		yc = yc + ym*self.gs.mode['bullet_offset']
		self.xm = xm*10
		self.ym = ym*10
		self.image = pygame.image.load("images/" + self.gs.mode['bullet_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [xc, yc]
	def tick(self):
		self.rect = self.rect.move([self.xm, self.ym])
# distance
def dist(x1, y1, x2, y2):
	return ((y2-y1)**2 + (x2-x1)**2)**.5

def collision(ball_center, bullet_center):
	distance = dist(ball_center[0], ball_center[1], bullet_center[0], bullet_center[1])
	if distance <= 50:
		return True
	else:
		return False

class ClientConnection(Protocol):
	def __init__(self, client):
		self.client = client
	def dataReceived(self, data):
		if data == 'chicago':
			self.client.mode = chicago
			self.client.setup()
			self.client.ready = 1
		elif data == 'jersey':
			self.client.mode = jersey
			self.client.setup()
			self.client.ready = 1
		else:
			data = pickle.loads(zlib.decompress(data))
			# p1 spot
			self.client.player1.rect.center = data[0]
			self.client.player1.box.rect.center = data[1]
			# p1 score
			self.client.score1 = data[2]
			# ball locatoins
			self.client.shot.drops = []
			shotx = pickle.loads(data[3])
			shoty = pickle.loads(data[4])
			i = 0
			for x in shotx:
				self.client.shot.drops.append(Dropshots(x, shoty[i], self.client))
				i += 1
			# p2 score
			self.client.score2 = data[5]
	def connectionMade(self):
		self.transport.write('player 2 connected')
	def connectionLost(self, reason):
		reactor.stop()
	def write(self, data):
		self.transport.write(data)
	def quit(self):
		self.transport.loseConnection()

class ClientConnectionFactory(ClientFactory):
	def __init__(self,client):
		self.client = client
	def buildProtocol(self, addr):
		proto = ClientConnection(self.client)
		self.client.write = proto.write
		self.client.quit = proto.quit
		return proto
if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnectionFactory(gs))
	reactor.run()
	lc.stop()
