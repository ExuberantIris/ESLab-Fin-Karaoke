import pygame

pygame.mixer.init(48000, -16, 2, 512)
pygame.mixer.music.load("../../pygame/AWholeNewWorld.wav")
print("JI")
pygame.mixer.music.play()

while True:
    pygame.time.delay(1000)