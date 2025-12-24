import pygame
import json
import asyncio
import os
import gc
from Pitch import freq_to_pitch, Pitch, PitchWithOctave
import threading
    

# --- Constants ---
WIDTH, HEIGHT = 1024, 768
FPS = 60
NOTE_SPEED = 200
NOW_LINE_X = 300
COUNTDOWN_TIME = 3000

# Colors
BG_DARK = (20, 24, 35)
GRID_LINE = (50, 55, 70)
NOTE_TARGET = (64, 158, 255)
NOTE_ACTIVE = (100, 200, 255)
USER_TRAIL_HIT = (255, 215, 0)
USER_TRAIL_MISS = (255, 50, 50)
USER_HEAD = (255, 255, 255)
TEXT_COLOR = (240, 240, 240)
LYRIC_COLOR = (255, 255, 100)
BUTTON_COLOR = (50, 200, 50)
BUTTON_HOVER_COLOR = (70, 220, 70)
PAUSE_COLOR = (255, 200, 0)

# Game States
STATE_IDLE = 0
STATE_COUNTDOWN = 1
STATE_PLAYING = 2
STATE_PAUSED = 3
STATE_FINISHED = 4

class KaraokeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, 512)
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Karaoke Game - A Whole New World (Manual Sync Mode)")
        
        self.clock = pygame.time.Clock()
        
        try:
            self.font = pygame.font.SysFont('Microsoft JhengHei', 18, bold=True)
            self.lyric_font = pygame.font.SysFont('Microsoft JhengHei', 40, bold=True)
            self.score_font = pygame.font.SysFont('Arial', 36, bold=True)
            self.countdown_font = pygame.font.SysFont('Arial', 120, bold=True)
            self.result_font = pygame.font.SysFont('Arial', 60, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 30, bold=True)
            self.hint_font = pygame.font.SysFont('Arial', 24, bold=True)
        except:
            self.font = pygame.font.Font(None, 20)
            self.lyric_font = pygame.font.Font(None, 40)
            self.score_font = pygame.font.Font(None, 36)
            self.countdown_font = pygame.font.Font(None, 120)
            self.result_font = pygame.font.Font(None, 60)
            self.button_font = pygame.font.Font(None, 30)
            self.hint_font = pygame.font.Font(None, 24)

        self.load_song_data()
        self.load_lyrics()

        self.state = STATE_IDLE
        self.running = True
        self.start_ticks = 0
        self.current_game_time = 0
        self.game_start_timestamp = 0
        self.paused_time = 0
        self.pause_start = 0
        
        self.current_user_freq = 0
        self.current_user_pitch = None
        self.score = 0
        self.user_history = []

        self.min_pitch = PitchWithOctave(Pitch.F, 2)
        self.max_pitch = PitchWithOctave(Pitch.F, 4)
        self.pitch_list = list(PitchWithOctave.inclusive_range(self.min_pitch, self.max_pitch))
        
        self.grid_top = 120
        self.grid_bottom = HEIGHT - 100
        self.grid_h = self.grid_bottom - self.grid_top
        self.row_h = self.grid_h / len(self.pitch_list)
        
        self.pitch_y_map = {}
        for i, p in enumerate(self.pitch_list):
            y = self.grid_bottom - (i + 1) * self.row_h
            self.pitch_y_map[p] = y

        self.background_surface = pygame.Surface((WIDTH, HEIGHT))
        self.pre_draw_static_background()

        self.last_lyric_text = ""
        self.cached_lyric_surf = None
        self.cached_lyric_shadow = None

        self.restart_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60)

        self.music_file = None
        for filename in ["AWholeNewWorld.mp3"]:
            if os.path.exists(filename):
                self.music_file = filename
                break  

        pygame.mixer.music.load(self.music_file)
        self.music_thread = threading.Thread(target=self.play_music)
        self.paused = False
        self.delay_time = 0

    def play_music(self):
        pygame.mixer.music.play()
        while True:
            pygame.time.delay(50)
    
    def pre_draw_static_background(self):
        self.background_surface.fill(BG_DARK)
        for p in self.pitch_list:
            y = self.get_y(p)
            color = GRID_LINE
            if not p.is_natural():
                pygame.draw.rect(self.background_surface, (30, 35, 45), (0, y, WIDTH, self.row_h))
            pygame.draw.line(self.background_surface, color, (0, y + self.row_h), (WIDTH, y + self.row_h), 1)
            
            if p[0] == Pitch.C or p[0] == Pitch.F:
                lbl = self.font.render(f"{p}", True, (80, 80, 100))
                self.background_surface.blit(lbl, (5, y + 5))

    def load_song_data(self):
        self.notes = []
        self.last_note_end_time = 0
        try:
            if not os.path.exists("AWholeNewWorld.json"): return
            with open("AWholeNewWorld.json", "r") as f:
                raw = json.load(f)
            for item in raw:
                end_t = item["time"] + item["duration"]
                self.notes.append({
                    "time": item["time"],
                    "duration": item["duration"],
                    "pitch": PitchWithOctave.from_str(item["pitch"]),
                    "end_time": end_t
                })
                if end_t > self.last_note_end_time:
                    self.last_note_end_time = end_t
            self.notes.sort(key=lambda x: x["time"])
            print(f"✓ Loaded {len(self.notes)} notes (duration: {self.last_note_end_time/1000:.1f}s)")
        except Exception as e:
            print(f"JSON Error: {e}")
            self.notes = []

    def load_lyrics(self):
        self.lyrics = [
            {"time": 16830, "text": "I can show you the world"},
            {"time": 20979, "text": "shining, shimmering, splendid"},
            {"time": 25124, "text": "Tell me princess"},
            {"time": 26923, "text": "now when did you last"},
            {"time": 29277, "text": "let your heart decide?"},
            {"time": 31332, "text": "--"},
            {"time": 33405, "text": "I can open your eyes"},
            {"time": 37442, "text": "take you wonder by wonder"},
            {"time": 41485, "text": "over, sideways and under"},
            {"time": 44498, "text": "on a magic carpet ride"},
            {"time": 48274, "text": "A whole new world"},
            {"time": 52453, "text": "a new fantastic"},
            {"time": 54178, "text": "point of view"},
            {"time": 55873, "text": "No one to tell us no"},
            {"time": 58808, "text": "or where to go"},
            {"time": 61021, "text": "or say we're only dreaming"},
            {"time": 63988, "text": "A whole new world"},
            {"time": 67158, "text": "a dazzling place"},
            {"time": 69345, "text": "I never know"},
            {"time": 71551, "text": "But when I way up here"},
            {"time": 74729, "text": "it's crystal-clear"},
            {"time": 76697, "text": "that now I'm in a"},
            {"time": 78900, "text": "whole new world with you"},
        ]

    def start(self):
        # Game start
        self.score = 0
        self.user_history = []
        self.state = STATE_COUNTDOWN
        self.start_ticks = pygame.time.get_ticks()
        self.paused_time = 0
        
        self.load_song_data()
        gc.collect()

    def back_to_title(self):
        pygame.mixer.music.stop()
        self.paused = False
       
        self.state = STATE_IDLE
        self.score = 0
        self.user_history = []
        self.current_game_time = 0
        self.paused_time = 0
        
        self.load_song_data()
        gc.collect()
        print("Returned to Title Screen")

    def update_user_input(self, freq, time):
        self.current_user_freq = freq
        self.current_time = time
        if freq > 0:
            try:
                self.current_user_pitch = freq_to_pitch(freq)
            except:
                self.current_user_pitch = None
        else:
            self.current_user_pitch = None

    def get_y(self, pitch):
        return self.pitch_y_map.get(pitch)

    def draw_background(self):
        self.screen.blit(self.background_surface, (0, 0))
        pygame.draw.line(self.screen, (200, 200, 200), (NOW_LINE_X, self.grid_top), (NOW_LINE_X, self.grid_bottom), 3)

    def draw_control_hints(self):
        hints = []
        if self.state == STATE_IDLE:
            hints = [
                "Press SPACE to Start",
                f"Music file: {self.music_file if self.music_file else 'NOT FOUND'}",
            ]
        elif self.state == STATE_COUNTDOWN:
            hints = [
                "Get ready to play music manually!",
            ]
        elif self.state == STATE_PLAYING:
            time_min = int(self.current_game_time / 60000)
            time_sec = int((self.current_game_time % 60000) / 1000)
            hints = [
                f"Time: {time_min:02d}:{time_sec:02d}",
                "P: Pause/Resume | R: Return to Title | ESC: Quit",
            ]
        elif self.state == STATE_PAUSED:
            hints = [
                "⏸ PAUSED",
                "P: Resume | R: Return to Title",
            ]
        
        y_offset = 10
        for hint in hints:
            surf = self.hint_font.render(hint, True, TEXT_COLOR)
            rect = surf.get_rect(center=(WIDTH/2, y_offset + 15))
            self.screen.blit(surf, rect)
            y_offset += 30

    def draw_lyrics(self, t):
        line = ""
        for l in self.lyrics:
            if t >= l["time"]:
                line = l["text"]
            else:
                break
        
        if line != self.last_lyric_text:
            self.last_lyric_text = line
            if line:
                self.cached_lyric_surf = self.lyric_font.render(line, True, LYRIC_COLOR)
                self.cached_lyric_shadow = self.lyric_font.render(line, True, (0,0,0))
            else:
                self.cached_lyric_surf = None

        if self.cached_lyric_surf:
            rect = self.cached_lyric_surf.get_rect(center=(WIDTH/2, HEIGHT - 50))
            self.screen.blit(self.cached_lyric_shadow, (rect.x+2, rect.y+2))
            self.screen.blit(self.cached_lyric_surf, rect)

    def draw_game_over_screen(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200)
        s.fill((0,0,0))
        self.screen.blit(s, (0,0))
        
        # title
        title = self.result_font.render("SONG FINISHED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/2 - 80))
        self.screen.blit(title, title_rect)
        
        # score
        score_txt = self.result_font.render(f"Final Score: {self.score}", True, USER_TRAIL_HIT)
        score_rect = score_txt.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.screen.blit(score_txt, score_rect)
        
        # button
        mouse_pos = pygame.mouse.get_pos()
        btn_color = BUTTON_HOVER_COLOR if self.restart_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        pygame.draw.rect(self.screen, btn_color, self.restart_btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255,255,255), self.restart_btn_rect, 2, border_radius=10)
        
        btn_txt = self.button_font.render("MAIN MENU", True, (255, 255, 255))
        btn_txt_rect = btn_txt.get_rect(center=self.restart_btn_rect.center)
        self.screen.blit(btn_txt, btn_txt_rect)

    def process(self):
        self.clock.tick(FPS)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
                return False
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if self.state == STATE_IDLE or self.state == STATE_FINISHED:
                        self.start()
                
                # pause/resume
                elif e.key == pygame.K_p:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                        self.pause_start = pygame.time.get_ticks()
                        print("⏸ Paused")
                    elif self.state == STATE_PAUSED:
                        pause_duration = pygame.time.get_ticks() - self.pause_start
                        self.paused_time += pause_duration
                        self.state = STATE_PLAYING
                        print("▶ Resumed")
                
                # return to menu
                elif e.key == pygame.K_r:
                    if self.state in [STATE_PLAYING, STATE_PAUSED, STATE_FINISHED]:
                        self.back_to_title()
                
                # exit
                elif e.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == STATE_FINISHED:
                    if self.restart_btn_rect.collidepoint(e.pos):
                        self.back_to_title()

        self.draw_background()
        current_ticks = pygame.time.get_ticks()

        if self.state == STATE_IDLE:
            
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(150)
            s.fill(BG_DARK)
            self.screen.blit(s, (0,0))
            
            title = self.result_font.render("Main Menu", True, (100, 200, 255))
            title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/2 - 120))
            self.screen.blit(title, title_rect)
            
            instructions = [
                "Press SPACE to start countdown",
                "Controls: P=Pause | R=Title | ESC=Quit",
            ]
            
            y = HEIGHT/2 - 40
            for line in instructions:
                surf = self.hint_font.render(line, True, TEXT_COLOR)
                rect = surf.get_rect(center=(WIDTH/2, y))
                self.screen.blit(surf, rect)
                y += 35
            
            pygame.display.flip()
            return True

        elif self.state == STATE_COUNTDOWN:
            elapsed = current_ticks - self.start_ticks
            remain = (COUNTDOWN_TIME - elapsed) / 1000.0
            
            if remain <= 0:
                self.state = STATE_PLAYING
                self.game_start_timestamp = current_ticks
                print("\n" + "="*50)
                print("PLAY YOUR MUSIC NOW!")
                print("="*50 + "\n")
                self.music_thread.start()
            else:
                num_str = str(int(remain) + 1)
                txt = self.countdown_font.render(num_str, True, (255, 200, 50))
                rect = txt.get_rect(center=(WIDTH/2, HEIGHT/2))
                
                hint = self.hint_font.render("Get ready to play music!", True, TEXT_COLOR)
                hint_rect = hint.get_rect(center=(WIDTH/2, HEIGHT/2 + 120))
                
                self.screen.blit(txt, rect)
                self.screen.blit(hint, hint_rect)
                pygame.display.flip()
                return True

        elif self.state == STATE_PLAYING:
            DELAY = 792#528
            #self.current_game_time = pygame.mixer.music.get_pos()
            self.current_game_time = current_ticks - self.game_start_timestamp - self.paused_time - DELAY
            self.current_game_time = 0 if self.current_game_time < 0 else self.current_game_time

            # if self.paused:
            #     pygame.mixer.music.unpause()
            #     self.paused = False
                
            if self.current_game_time > self.last_note_end_time + 2000:
                self.state = STATE_FINISHED
                print("■ Song finished")
        
        elif self.state == STATE_PAUSED:
            # pygame.mixer.music.pause()
            # self.paused = True
            pass

        is_hitting_now = False
        to_draw_notes = []

        if self.state in [STATE_PLAYING, STATE_PAUSED, STATE_FINISHED]:
            for note in self.notes:
                if note["end_time"] < self.current_game_time - 2000: continue
                if note["time"] > self.current_game_time + 4000: break

                start_x = NOW_LINE_X + (note["time"] - self.current_game_time) / 1000.0 * NOTE_SPEED
                width = (note["duration"] / 1000.0) * NOTE_SPEED
                y = self.get_y(note["pitch"])
                
                if y is not None:
                    rect = pygame.Rect(start_x, y, width, self.row_h - 1)
                    if self.state == STATE_PLAYING:
                        if note["time"] <= self.current_game_time - self.delay_time <= note["end_time"]:
                            if self.current_user_pitch:
                                #convert pitch to MIDI index
                                user_pitch_val = int(self.current_user_pitch)
                                target_pitch_val = int(note["pitch"])
                        
                                if abs(user_pitch_val - target_pitch_val) <= 1:
                                    is_hitting_now = True
                                    note["hit"] = True
                            #if self.current_user_pitch == note["pitch"]:
                                #is_hitting_now = True
                                #note["hit"] = True
                    to_draw_notes.append((rect, note))

            if self.state == STATE_PLAYING and self.current_user_pitch:
                aroundFs3 = [
                    PitchWithOctave(Pitch.E, 3), PitchWithOctave(Pitch.F, 3), 
                    PitchWithOctave(Pitch.Fs, 3), PitchWithOctave(Pitch.G, 3), PitchWithOctave(Pitch.Gs, 3)
                ]
                if (self.delay_time == 0 and self.current_user_pitch in aroundFs3 and self.current_game_time >= 16830 - DELAY - 500):
                    print(self.delay_time)
                    self.delay_time = self.current_game_time - 16830
                self.user_history.append((self.current_game_time - self.delay_time, self.current_user_pitch, is_hitting_now))
                if is_hitting_now:
                    self.score += 1

            cutoff = self.current_game_time - (NOW_LINE_X / NOTE_SPEED * 1000) - 200
            self.user_history = [h for h in self.user_history if h[0] > cutoff]

            for rect, note in to_draw_notes:
                color = NOTE_TARGET
                if note["time"] <= self.current_game_time <= note["end_time"]:
                    color = NOTE_ACTIVE
                pygame.draw.rect(self.screen, color, rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 1, border_radius=4)

            for h_time, h_pitch, h_hit in self.user_history:
                t_diff = self.current_game_time - h_time
                tx = NOW_LINE_X - (t_diff / 1000.0) * NOTE_SPEED
                ty = self.get_y(h_pitch)
                if ty is not None and tx > -20:
                    trail_color = USER_TRAIL_HIT if h_hit else USER_TRAIL_MISS
                    t_rect = pygame.Rect(tx, ty + 4, 5, self.row_h - 8)
                    pygame.draw.rect(self.screen, trail_color, t_rect)

            if self.state == STATE_PLAYING and self.current_user_pitch:
                hy = self.get_y(self.current_user_pitch)
                if hy is not None:
                    head_color = USER_TRAIL_HIT if is_hitting_now else USER_TRAIL_MISS
                    pygame.draw.circle(self.screen, head_color, (NOW_LINE_X, int(hy + self.row_h/2)), int(self.row_h/2 - 2))

            self.draw_lyrics(self.current_game_time)
            
            # score and current state
            score_surf = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surf, (WIDTH - 200, 70))
            
            # pause
            if self.state == STATE_PAUSED:
                pause_surf = self.countdown_font.render("||", True, PAUSE_COLOR)
                pause_rect = pause_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
                
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(100)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                self.screen.blit(pause_surf, pause_rect)

        # control
        self.draw_control_hints()

        if self.state == STATE_FINISHED:
            self.draw_game_over_screen()

        pygame.display.flip()
        return True

    def quit(self):
        pygame.quit()
