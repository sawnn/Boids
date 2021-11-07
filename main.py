from typing import List
import pygame
from boid import Obstacle

from boid import Boid

class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.pause = False
        self.fullscreen = False
        self.boids: List[Boid] = [Boid(self.screen) for _ in range(50)]
        self.boids.append(Boid(self.screen, True))
        self.obstacles: List[Obstacle] = [Obstacle(self.screen) for _ in range(20)]

    def handling_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                    self.running = False
                case pygame.KEYDOWN if event.key == pygame.K_p:
                    self.pause = not self.pause
                case pygame.KEYDOWN if event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        modes = pygame.display.list_modes(
                            depth=0, flags=pygame.FULLSCREEN, display=0)
                        self.last_window_size = self.screen.get_size()
                        pygame.event.post(pygame.event.Event(
                            pygame.VIDEORESIZE, size=modes[0] if len(modes) > 0 else (1920, 1080)))
                    else:
                        pygame.event.post(pygame.event.Event(
                            pygame.VIDEORESIZE, size=self.last_window_size))
                case pygame.VIDEORESIZE:
                    size = (max(event.size[0], 720), max(event.size[1], 500))
                    type = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
                    self.screen = pygame.display.set_mode(size, type)

    def update(self):
        for boid in self.boids:
            boid.update(self.obstacles, self.boids, self.screen)

    def display(self):
        self.screen.fill('#222222')
        for boid in self.boids:
            boid.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handling_events()
            if self.pause:
                continue
            self.update()
            self.display()
            self.clock.tick(60)


pygame.init()
screen = pygame.display.set_mode((1080, 720), pygame.RESIZABLE)
game = Game(screen)
game.run()

pygame.quit()