import pygame
import asyncio
import random
import time
from Pitch import freq_to_pitch, Pitch, PitchWithOctave

my_font, screen = None, None
WIDTH, HEIGHT = 600, 400
# Initialize Pygame
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# Data storage
points = []  # list of (x, y)
SHIFT_PIXELS = 5  # how much to move left each update
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

def UpdatePlot(y = -1):
    """Add a new point and scroll existing points left."""
    # Shift all existing points left
    for i in range(len(points)):
        points[i] = (points[i][0] - SHIFT_PIXELS, points[i][1])
    # Remove points that moved off screen
    while points and points[0][0] < 0:
        points.pop(0)
    # Add new point at the right edge
    if (y >= 0):
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

TICK_MS = 50 #ms
MARGIN = 200 # 容錯空間
screen_half_unit_span = WIDTH / 2 / SHIFT_PIXELS
time_half_span = TICK_MS * screen_half_unit_span
MS_TO_LENGTH_UNIT = SHIFT_PIXELS / TICK_MS
BASE_TIME = 0

base_time = time.time_ns() / 1_000_000
thing = []
new_point = []
import json
with open("AWholeNewWorld.json", "r") as f:
    thing = json.load(f)

def update_plot_prime():
    cur_time_ms = pygame.mixer.music.get_pos()
    print(cur_time_ms)
    most_left_time = cur_time_ms - time_half_span - MARGIN
    most_right_time = cur_time_ms + time_half_span + MARGIN

    make_init_window()
    pop_num = 0
    for data in thing:
        if data["time"] + data["duration"] < most_left_time:
            pop_num += 1
            continue
        elif data["time"] > most_right_time:
            break

        pitch = PitchWithOctave.from_str(data["pitch"])
        real_top, real_width = pitch_data[pitch]

        offset_unit = (data["time"] - cur_time_ms) * MS_TO_LENGTH_UNIT
        start = WIDTH / 2 + offset_unit
        width = data["duration"] * MS_TO_LENGTH_UNIT

        rect_value = pygame.Rect(start, real_top, width, real_width)
        pygame.draw.rect(screen, YELLOW, rect_value)
    
    pygame.draw.line(screen, BLACK, (WIDTH / 2, 0), (WIDTH/2, HEIGHT), 1)

    if pop_num > 0:
        for i in range(pop_num):
            thing.pop(0)
        # if px == points[-1][0]:
        #     text_surface = my_font.render(f"{pitch}", False, (0, 0, 0))
        #     screen.blit(text_surface, (WIDTH/2 + 3, real_top - real_width / 2))
    pygame.display.flip()

async def add_points():
    """Simulate async incoming data."""
    random.seed()
    UpdatePlot(0)
    while True:
        #UpdatePlot()
        await asyncio.sleep(0.05)
        # y = random.uniform(Y_MIN, Y_MAX)
        # UpdatePlot(y)

async def add_points_prime():
    """Simulate async incoming data."""
    random.seed()
    pygame.mixer.init()
    pygame.mixer.music.load("AWholeNewWorld.mp3")
    pygame.mixer.music.play()
    while True:
        update_plot_prime()
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
    global my_font, screen
    pygame.init()
    pygame.font.init()
    my_font = pygame.font.SysFont('Arial', 30)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Scrolling Scatter Plot")

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