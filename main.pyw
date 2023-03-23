import pygame
import random as rnd
from math import sqrt

x, y = 800, 457
dial = 30
rad = 20
width = 5
fps = 30
color_static = (0, 30, 255)
color_active = (0, 255, 30)
color_line_static = (0, 30, 255)
color_line_active = (0, 255, 30)

pygame.init()
screen = pygame.display
screen.set_mode((x, y))
clock = pygame.time.Clock()
screen.set_caption('Navigator')
surf = screen.set_mode((x, y))

settles = []
edges = []
cursor = [None, None]
user_text = ''
response = ''
black = (0, 0, 0)
white = (255, 255, 255)
font = pygame.font.Font(None, 32)

class Settle():
	def __init__(self, x, y, id):
		self.id = id
		self.x = x
		self.y = y

	def display(self):
		if self in cursor:
			pygame.draw.circle(surf, color_active, (self.x, self.y), rad)
		else:
			pygame.draw.circle(surf, color_static, (self.x, self.y), rad)
	
	def isIn(self, x, y):
		if ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5 <= rad * 2:
			return True
		else:
			return False

class Edge():
	def __init__(self, fr, to, cost):
		self.link = False
		self.fr = fr
		self.to = to
		self.cost = cost
		self.on = False
	
	def display(self):
		if self.cost != 0:
			if self.on == False and self.link.on == False:
				pygame.draw.line(surf, color_line_static, (self.fr.x, self.fr.y), (self.to.x, self.to.y), width)
			else:
				pygame.draw.line(surf, color_line_active, (self.fr.x, self.fr.y), (self.to.x, self.to.y), width)
			text = font.render(str(self.cost), True, white)
			surf.blit(text, ((self.fr.x + self.to.x) // 2 + 3, (self.fr.y + self.to.y) // 2 + 3))

class Navigator():
	@staticmethod
	def buildRoad(a, b, length):
		to_append = True
		for e in edges[a.id]:
			if e.to == b:
				e.cost = length
				to_append = False
		for e in edges[b.id]:
			if e.to == a:
				e.cost = length
				to_append = False
		if to_append:
			l = Edge(a, b, length)
			r = Edge(b, a, length)
			l.link = r
			r.link = l
			edges[a.id].append(l)
			edges[b.id].append(r)
			return 'Road has been built'
		return 'Road has been removed'
	
	@staticmethod
	def calculate(a, b):
		res = [1e9] * len(settles)
		res[b.id] = 0
		ref = [None] * len(settles)
		
		for i in range(len(settles)):
			for settle in settles:
				for e in edges[settle.id]:
					if e.cost != 0:
						if res[e.to.id] + e.cost < res[settle.id]:
							res[settle.id] = res[e.to.id] + e.cost
							ref[settle.id] = e.to.id

		if res[a.id] == 1e9:
			return 'No path found'
		else:
			cur = a.id
			while cur != b.id:
				for e in edges[cur]:
					if e.to.id == ref[cur]:
						e.on = True
						cur = e.to.id
						break
			return f'It is {res[a.id]} long'

while 1:
	clock.tick(fps)
	screen.update()
	screen.set_mode((x, y))

	for edge in edges:
		for e in edge:
			e.display()
	for settle in settles:
		settle.display()

	pygame.draw.rect(surf, black, pygame.Rect(0, 0, x, dial))
	text = font.render('cmd: ' + user_text, True, white)
	surf.blit(text, (5, 5))
	pygame.draw.rect(surf, black, pygame.Rect(0, y - 30, x, dial))
	text = font.render('out: ' + response, True, white)
	surf.blit(text, (5, y - 25))

	events = pygame.event.get()
	for event in events:
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 3:
				pos = pygame.mouse.get_pos()
				to_append = True
				for settle in settles:
					if settle.isIn(*pos):
						to_append = False
				if to_append:
					settles.append(Settle(*pos, len(settles)))
					edges.append([])
			elif event.button == 1:
				pos = pygame.mouse.get_pos()
				for settle in settles:
					if settle.isIn(*pos):
						if not settle in cursor:
							for edge in edges:
								for e in edge:
									e.on = False
							cursor[0], cursor[1] = settle, cursor[0]
							if not None in cursor:
								settle.display()
								cmd = user_text.strip().split()
								if len(cmd) > 1 and cmd[0] == 'road':
									response = Navigator.buildRoad(cursor[0], cursor[1], int(user_text.split()[1]))
								elif len(cmd) > 0 and cmd[0] == 'path':
									response = Navigator.calculate(cursor[0], cursor[1])
								else:
									response = 'Unknown command'
								cursor = [None, None]
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_BACKSPACE:
				user_text = user_text[:-1]
			else:
				user_text += event.unicode
		elif event.type == pygame.QUIT:
			pygame.quit()
