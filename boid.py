from typing import List
import random
import pygame
import math
from pygame.locals import *

class Vector2:
    def __init__(self, x = 0, y = 0) -> None:
        self.x = x
        self.y = y

    def distance(self, other) -> float:
        return (self - other).mag()

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)
    
    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def mag(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def normalize(self):
        mag = self.mag()
        if mag != 0:
            self.x /= mag
            self.y /= mag
        
    def set_mag(self, mag):
        self.normalize()
        self.x *= mag
        self.y *= mag

    def limit(self, max_speed):
        if self.mag() > max_speed:
            self.normalize()
            self.x *= max_speed
            self.y *= max_speed

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
class Obstacle:
    def __init__(self, screen: pygame.Surface) -> None:
        self.x = 5
        self.y = 5
        self.pos: Vector2 = Vector2(random.randrange(0, screen.get_width()), random.randrange(0, screen.get_height()))
    def draw(self, screen: pygame.Surface) -> None:
        rect = Rect( self.pos.x, self.pos.y, 5, 5)
        pygame.draw.rect (screen , 'red', rect, 0)

class Boid:
    def __init__(self, screen: pygame.Surface, debug=False) -> None:
        self.vel: Vector2 = Vector2(random.randrange(10, 40), random.randrange(10, 40))
        self.pos: Vector2 = Vector2(random.randrange(0, screen.get_width()), random.randrange(0, screen.get_height()))
        self.max_speed = 10
        
        self.separation_radius = 25
        self.separation_force = 1

        self.alignment_radius = 50
        self.alignment_force = 1
        
        self.cohesion_radius = 70
        self.cohesion_force = 1

        self.debug = debug

    def update(self, obstacles: List[Obstacle], boids: List['Boid'], screen: pygame.Surface) -> None:
        acc = self.flock(boids, obstacles) 
        self.vel += acc
        self.vel.set_mag(self.max_speed)
        self.pos += self.vel
        self.teleport(screen)

    def teleport(self, screen) -> None:
        if self.pos.x > screen.get_width():
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = screen.get_width()
        if self.pos.y > screen.get_height():
            self.pos.y = 0
        elif self.pos.y < 0:
            self.pos.y = screen.get_height()

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, 'white', (int(self.pos.x), int(self.pos.y)), 5)

        if self.debug:
            pygame.draw.circle(screen, 'green', (int(self.pos.x), int(self.pos.y)), self.cohesion_radius, 1)
            pygame.draw.circle(screen, 'blue', (int(self.pos.x), int(self.pos.y)), self.alignment_radius, 1)
            pygame.draw.circle(screen, 'red', (int(self.pos.x), int(self.pos.y)), self.separation_radius, 1)            

    def flock(self, boids: List["Boid"], obstacles: List[Obstacle]) -> Vector2:
        separation = []
        alignment = []
        cohesion = []
        obstaclesList = []
        obstacleResult = Vector2()

        for boid in boids:
            for obstacle in obstacles:
                d = self.distanceObstacle(obstacle)
                if d < self.separation_radius:
                    obstaclesList.append(boid)
            if boid == self: continue
            d = self.distance(boid)
            if d < self.separation_radius:
                separation.append(boid)
            elif d < self.alignment_radius:
                alignment.append(boid)
            elif d < self.cohesion_radius:
                cohesion.append(boid)
        

            

        return self.alignment(alignment) + self.separation(separation) + self.cohesion(cohesion) + self.separationObstacle(obstaclesList)

    def cohesion(self, boids: List["Boid"]) -> Vector2:
        result = Vector2()
        total = len(boids)

        for boid in boids:
            result += (boid.pos - self.pos)

        if total > 0:
            result /= total
            result -= self.vel
            result *= self.cohesion_force
            result.normalize()
            return result
        return result

    def alignment(self, boids: List["Boid"]) -> Vector2:
        result = Vector2()
        total = len(boids)

        for boid in boids:
            result += boid.vel
        
        if total > 0:
            result /= total
            result -= self.vel
            result *= self.alignment_force
            result.normalize()
            return result
        return result


    def moveAwayObstacle(self, obstacle: Obstacle) -> Vector2:
        distance = Vector2()
        numClose = 0


        numClose += 1
        diff = self.pos - obstacle.pos

        if diff.x >= 0:
            diff.x = math.sqrt(self.separation_radius) - diff.x
        elif diff.x < 0:
            diff.x = -math.sqrt(self.separation_radius) - diff.x

        if diff.y >= 0:
            diff.y = math.sqrt(self.separation_radius) - diff.y
        elif diff.y < 0:
            diff.y = -math.sqrt(self.separation_radius) - diff.y

        distance += diff

        if numClose == 0:
            return
        return self.vel - distance / 5

    def separationObstacle(self, obstacles: List[Obstacle])-> Vector2:
        result = Vector2()
        total = len(obstacles)

        for obstacle in obstacles:
            result += (self.pos - obstacle.pos)

        if total > 0:
            result /= total
            result -= self.vel
            result *= self.separation_force
            result.normalize()
            return result
        return result

    def separation(self, boids: List["Boid"]) -> Vector2:
        result = Vector2()
        total = len(boids)

        for boid in boids:
            result += (self.pos - boid.pos)

        if total > 0:
            result /= total
            result -= self.vel
            result *= self.separation_force
            result.normalize()
            return result
        return result


    def distance(self, other: 'Boid') -> float:
        return self.pos.distance(other.pos)

    def distanceObstacle(self, other: Obstacle) -> float:
        return self.pos.distance(other.pos)
    
