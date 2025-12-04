import pygame
import asyncio
import random

from Pitch import freq_to_pitch, Pitch, PitchWithOctave

# Initialize Pygame
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 30)
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Scatter Plot")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# Data storage
points = []  # list of (x, y)
SHIFT_PIXELS = 10  # how much to move left each update
POINT_RADIUS = 5

# Axis ranges for y-values
Y_MIN, Y_MAX = 0, 500

PITCH_RANGE_MIN = PitchWithOctave(Pitch.C, 2)
PITCH_RANGE_MAX = PitchWithOctave(Pitch.B, 4) #inclusive
pitch_data = {}

PURPLE = (66, 81, 116)
OTHER_PURPLE = (204, 137, 183)
YELLOW = (187, 255, 85)

def transform_coords(x, y):
    """Convert data coordinates to screen coordinates."""
    screen_y = HEIGHT - int((y - Y_MIN) / (Y_MAX - Y_MIN) * HEIGHT)  # invert y-axis
    return x, screen_y

def UpdatePlot(y):
    """Add a new point and scroll existing points left."""
    # Shift all existing points left
    for i in range(len(points)):
        points[i] = (points[i][0] - SHIFT_PIXELS, points[i][1])
    # Remove points that moved off screen
    while points and points[0][0] < 0:
        points.pop(0)
    # Add new point at the right edge
    points.append((WIDTH / 2, y))

    make_init_window()
    # Draw points
    for px, py in points:
        sx, sy = transform_coords(px, py)
        #pygame.draw.circle(screen, RED, (sx, sy), POINT_RADIUS)
        try:
            pitch = freq_to_pitch(py)
            real_top, real_width = pitch_data[pitch]
        except:
            continue
        rect_value = pygame.Rect(px - SHIFT_PIXELS, real_top, SHIFT_PIXELS, real_width)
        pygame.draw.rect(screen, YELLOW, rect_value)
        
        if px == points[-1][0]:
            text_surface = my_font.render(f"{pitch}", False, (0, 0, 0))
            screen.blit(text_surface, (WIDTH/2 + 3, real_top - real_width / 2))
    pygame.display.flip()

async def add_points():
    """Simulate async incoming data."""
    random.seed()
    while True:
        await asyncio.sleep(0.05)
        # y = random.uniform(Y_MIN, Y_MAX)
        # UpdatePlot(y)

def make_init_window():
    screen.fill(WHITE)
    # Draw axes
    pygame.draw.line(screen, BLACK, (0, HEIGHT), (WIDTH, HEIGHT), 2)
    pygame.draw.line(screen, BLACK, (0, 0), (0, HEIGHT), 2)
    pygame.draw.line(screen, BLACK, (WIDTH / 2 - 0.5, 0), (WIDTH / 2 - 0.5, HEIGHT), 1)

    this_color = PURPLE
    interval = int(PITCH_RANGE_MAX) - int(PITCH_RANGE_MIN) + 1
    for i, pitch in enumerate(PitchWithOctave.reversed_inclusive_range(PITCH_RANGE_MIN, PITCH_RANGE_MAX)):
        if pitch.is_natural():
            this_color = OTHER_PURPLE
        else:
            this_color = PURPLE

        rect_data = pygame.Rect(
            0, 
            i * HEIGHT / interval, 
            WIDTH, 
            HEIGHT / interval + 1
        )
        pygame.draw.rect(screen, this_color, rect_data)

        if pitch[0] == Pitch.E:
            y_val = (i)* HEIGHT / interval
            pygame.draw.line(screen, BLACK, (0, y_val), (WIDTH, y_val), 1)
        elif pitch[0] == Pitch.B:
            y_val = (i)* HEIGHT / interval
            pygame.draw.line(screen, BLACK, (0, y_val), (WIDTH, y_val), 2)

        pitch_data[pitch] = (i * HEIGHT / interval, HEIGHT / interval + 1)

async def main_loop():
    """Pygame event loop running inside asyncio."""
    make_init_window()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        await asyncio.sleep(0)
    pygame.quit()

async def _test_main():
    asyncio.gather(main_loop(), add_points())

    while True:
        await asyncio.sleep(1)  # keep alive loop
if __name__ == "__main__":
    asyncio.run(_test_main())