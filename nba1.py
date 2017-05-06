from teams import chicago, jersey

import sys
import pygame
import os
import math
import zlib
import cPickle as pickle
from pygame.compat import geterror
from pygame.locals import *
import random

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.task import LoopingCall

SERVER_PORT = 40053


class GameSpace:
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("NBA 2K18")
		# set game objects
		self.clock = pygame.time.Clock()
		self.menu = Menu(self)
		# set variables in gs
		self.counter = 0
		self.pressedKey = 0
		self.connected = False
		self.quit = 0
		self.counted = False
		self.team = None
		self.waitString = "Waiting for player 2 to connect brah"
		self.gameOver = 0
	def setup(self):
		self.score1 = 0
		self.score2 = 0
		self.scoreCount = 0
		self.shot = Shot(self)
		self.player1 = Player1(self)
		self.player2 = Player2(self)
		self.p2body = Player2Prop(self)
		self.endGame = GameOver(self)

		# background image
#		self.bg = pygame.Surface(screen.get_size())
#		self.bg = bg.convert()
#		bg.fill((0,0,0))
		self.bg = pygame.image.load("images/" + self.team['background_image'])
		self.bg = pygame.transform.scale(self.bg, self.team['background_scale'])

	def game_loop(self):
		if self.gameOver == 1:
			self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, self.score1, pickle.dumps([]), pickle.dumps([]), self.score2])))
			if self.score1 > 25:
				self.endGame.display(1)
			else:
				self.endGame.display(2)
			pygame.display.flip()
		elif self.connected and self.team != None:
			self.counter+=1
			for bullet in self.player2.lasers:
				for ball in self.shot.drops:
					if collision(ball.rect.center, bullet.rect.center):
						self.shot.drops.remove(ball)
						self.player2.lasers.remove(bullet)
						# 2 blocks = a point
						if self.scoreCount % 2 == 1:
							self.score2 += 1
						self.scoreCount += 1
						break
			for ball in self.shot.drops:
				if collision(ball.rect.center, [self.player1.rect.center[0] + self.team['catcher_offset'][0], self.player1.rect.center[1] + self.team['catcher_offset'][1]]):
					self.shot.drops.remove(ball)
					self.score1 += 1
			# frame rate with tick
			self.clock.tick(60)
			# user inputs for slick controls
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit()
				if event.type == KEYDOWN:
					if event.key == 275:
						self.player1.Moving = "R"
					elif event.key == 276:
						self.player1.Moving = "L"
					self.pressedKey += 1
				if event.type == KEYUP:
					self.pressedKey -= 1
					if self.pressedKey == 0:
						self.player1.Moving = "N"
			self.shot.tick()
			self.player1.tick()
			self.player2.tick()
			for laser in self.player2.lasers:
				laser.tick()
			if self.counted and self.counter%3 == 0:
				shotx = []
				shoty = []
				#list of shot drop to player 2
				for drop in self.shot.drops:
					shotx.append(drop.rect.center[0])
					shoty.append(drop.rect.center[1])
				self.write(zlib.compress(pickle.dumps([self.player1.rect.center, self.player1.box.rect.center, self.score1, pickle.dumps(shotx), pickle.dumps(shoty), self.score2])))
			self.counted = True
			#display game object
			self.screen.blit(self.bg, (0,0))
			self.screen.blit(self.p2body.image, self.p2body.rect)
			self.screen.blit(self.player1.image, self.player1.rect)
			# lasers
			for laser in self.player2.lasers:
				self.screen.blit(laser.image, laser.rect)
			self.screen.blit(self.player2.image, self.player2.rect)
			# text display, theres only 1 font?
			lt = pygame.font.Font('freesansbold.ttf', 70)
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
		else: # waiting to connect to p2
			self.menu.display()
			pygame.display.flip()
	def write(self,data):
		pass
	def quit(self):
		pass

class Menu(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		# choosing teams
		self.chicagoButton = pygame.image.load("images/chiBulls.png")
		self.jerseyButton = pygame.image.load("images/bklNets.png")

		self.chicagoRect = self.chicagoButton.get_rect()
		self.jerseyRect = self.jerseyButton.get_rect()

		self.chicagoRect.center = [200, 300]
		self.jerseyRect.center = [400, 300]
		self.circleCenter = None
	def display(self):
		mx, my = pygame.mouse.get_pos()
		self.gs.screen.fill((0, 0, 0))
		lt = pygame.font.Font('freesansbold.ttf', 50)
		TextS = lt.render("Select your team", True, (255, 255, 255))
		TextR = TextS.get_rect()
		self.gs.screen.blit(TextS, TextR)
		message = pygame.font.Font('freesansbold.ttf', 20)
		messageS = message.render(self.gs.waitString, True, (255, 255, 255))
		messageR = messageS.get_rect()
		messageR.center = 450, 460
		self.gs.screen.blit(messageS, messageR)

		# highlight button
		if dist(mx, my, self.chicagoRect.centerx, self.chicagoRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (255, 0, 0), [self.chicagoRect.centerx, self.chicagoRect.centery], 50, 0)
		elif dist(mx, my, self.jerseyRect.centerx, self.jerseyRect.centery)<25:
			pygame.draw.circle(self.gs.screen, (255, 0, 0), [self.jerseyRect.centerx, self.jerseyRect.centery], 50, 0)
		elif self.circleCenter != None:
			pygame.draw.circle(self.gs.screen, self.color, self.circleCenter, 50, 0)
		#display button
		self.gs.screen.blit(self.chicagoButton, self.chicagoRect)
		self.gs.screen.blit(self.jerseyButton, self.jerseyRect)
		# user click check
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.gs.quit()
			elif event.type == pygame.MOUSEBUTTONUP:
				if dist(mx, my, self.chicagoRect.centerx, self.chicagoRect.centery) < 25:
					self.circleCenter = [self.chicagoRect.centerx, self.chicagoRect.centery]
					self.color(148, 0, 211)
					self.gs.team = chicago
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('chicago')
				elif dist(mx, my, self.jerseyRect.centerx, self.jerseyRect.centery) < 25:
					self.circleCenter = [self.jerseyRect.centerx, self.jerseyRect.centery]
					self.color = (0, 255, 0)
					self.gs.team = jersey
					self.gs.setup()
					if self.gs.connected:
						self.gs.write('jersey')

# gameover boyy
class GameOver(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
	def display(self, winner):
		self.gs.screen.fill((0,0,0))
		# player 1 winna
		if winner == 1:
			lt = pygame.font.Font('freesansbold.ttf', 30)
			TextS = lt.render("YOU ARE THE NBA CHAMPION", True, (255, 255, 255))
		elif winner == 2:
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
		self.drops = []
		self.created = False
	def tick(self):
		create = random.randint(1, 10)
		if create == 7:
			self.created = Dropshots(self.gs)
			self.drops.append(self.created)
		for ball in self.drops:
			ball.rect = ball.rect.move([0, 1])

class Dropshots(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team['ball_image'])
		self.rect = self.image.get_rect()
		self.x = random.randint(30, 610)
		self.rect.center = [self.x, -20]
class Player2Prop(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team['blocker_body'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.team['sb_location']
# Player 1
class Player1(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team['player_image'])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.team['player_start']
		self.Moving = "N"
		self.box = Box(self.rect.center, self.gs)
	def tick(self):
		# move player
		if self.Moving == "R":
			self.rect = self.rect.move([5, 0])
			self.box.rect = self.box.rect.move([5, 0])
		elif self.Moving == "L":
			self.rect = self.rect.move([-5, 0])
			self.box.rect = self.box.rect.move([-5, 0])
		if self.rect.center[0] < self.gs.team['max_player_left']:
			self.rect.center = [self.gs.team['max_player_left'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0] + self.gs.team['box_offset'][0], self.rect.center[1] + self.gs.team['box_offset'][1]]
		elif self.rect.center[0] > self.gs.team['max_player_right']:
			self.rect.center = [self.gs.team['max_player_right'], self.rect.center[1]]
			self.box.rect.center = [self.rect.center[0] + self.gs.team['box_offset'][0], self.rect.center[1] + self.gs.team['box_offset'][1]]

# catching balls lol
class Box(pygame.sprite.Sprite):
	def __init__(self, center, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team['box_image'])
		self.rect = self.image.get_rect()
		self.x = center[0] + self.gs.team['box_offset'][0]
		self.y = center[1] + self.gs.team['box_offset'][1]
		self.rect.center = [self.x, self.y]

# the swatter
class Player2(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.mx = 1
		self.my = 1
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team["hand_image"])
		self.rect = self.image.get_rect()
		self.rect.center = self.gs.team['hand_location']
		self.lasers = []
		self.angle = 0
		self.orig_image = self.image
	def tick(self):
		for ball in self.lasers:
			if ball.rect.center[0] < -20 or ball.rect.center[0] > 660:
				self.lasers.remove(ball)
			elif ball.rect.center[1] < -20 or ball.rect.center[1] > 500:
				self.lasers.remove(ball)
		# player 2 rotates
		self.angle = math.atan2(self.my-self.rect.center[1], self.mx - self.rect.center[0])*-180/math.pi + 211.5 - self.gs.team['angle_offset']
		self.image = pygame.transform.rotate(self.orig_image, self.angle)
		self.rect = self.image.get_rect(center = self.rect.center)

class Laser(pygame.sprite.Sprite):
	def __init__(self, x, y, xm, ym, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.xm = xm
		self.ym = ym
		self.gs = gs
		self.image = pygame.image.load("images/" + self.gs.team['bullet_image'])
		self.rect = self.image.get_rect()
		self.rect.center = [x,y]
	def tick(self):
		self.rect = self.rect.move([self.xm, self.ym])
# distance
def dist(x1, y1, x2, y2):
	return ((y2-y1)**2 + (x2-x1)**2)**.5

def collision(ball_center, catcher_point):
	distance = dist(ball_center[0], ball_center[1], catcher_point[0], catcher_point[1])
	if distance <= 25:
		return True
	else:
		return False

class ServerConnection(Protocol):
	def __init__(self, addr, client):
		self.addr = addr
		self.client = client
	def dataReceived(self, data):
		if data == 'player 2 connected':
			self.client.connected = True
			self.client.waitString = "player 2 connected"
			if self.client.team != None:
				self.transport.write(self.client.team['name'])
		else:
			self.client.player2.lasers = []
			data = pickle.loads(zlib.decompress(data))
			# player 2's rotatos
			self.client.player2.mx = data[0]
			self.client.player2.my = data[1]
			data[2] = pickle.loads(data[2])
			data[3] = pickle.loads(data[3])
			data[4] = pickle.loads(data[4])
			data[5] = pickle.loads(data[5])
			#sync laser
			i = 0
			for x in data[2]:
				self.client.player2.lasers.append(Laser(data[2][i], data[3][i], data[4][i], data[5][i], self.client))
				i += 1
	def connectionLost(self, reason):
		reactor.stop()
	def write(self, data):
		self.transport.write(data)
	def quit(self):
		self.transport.loseConnection()
class ServerConnectionFactory(Factory):
	def __init__(self, client):
		self.client = client
	def buildProtocol(self, addr):
		proto = ServerConnection(addr, self.client)
		self.client.write = proto.write
		self.client.quit = proto.quit
		return proto
if __name__ == '__main__':
	gs = GameSpace()
	lc = LoopingCall(gs.game_loop)
	lc.start(1/60)
	reactor.listenTCP(SERVER_PORT, ServerConnectionFactory(gs))
	reactor.run()
	lc.stop()

