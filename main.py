import ctypes
import os
import sys
import pygame
import random
import math
import tkinter as tk
from PIL import Image, ImageTk
from pygame.locals import *
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 500, 650
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (WIDTH // 2)
y = (screen_height // 2) - (HEIGHT // 2)
root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
root.title("Cannon Ball Game - By SouRav")
root.resizable(False, False)
frame = tk.Frame(root, width=WIDTH, height=HEIGHT)
frame.pack()
os.environ['SDL_WINDOWID'] = str(frame.winfo_id())
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOX_COLOR = (255, 100, 100)
cannon_balls = 1
balls_to_shoot = 1
turn_completed = True
level = 1
balls_collected_this_turn = 0
game_over = False
game_over_font_size = 48
font_growing = True
font_growth_step = 1
current_font_size = game_over_font_size
game_over_animation = None
game_over_start_time = 0
OVERLAY_ALPHA = 150
game_over_sound_played = False
game_over_display_delay = 1000
game_over_trigger_time = None
restart_button = None
speed_multiplier = 1.0
paused = False

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.CannonGame")

try:
    root.iconbitmap(resource_path("assets/images/icon.ico"))

except:
    pass
cannon_sound = pygame.mixer.Sound(resource_path("assets/sounds/cannon.mp3"))
cannon_sound.set_volume(0.3)
ball_collosion_sound = pygame.mixer.Sound(resource_path("assets/sounds/ball_collision.mp3"))
ball_collosion_sound.set_volume(0.5)
game_over_sound = pygame.mixer.Sound(resource_path("assets/sounds/game_over.mp3"))
game_over_sound.set_volume(1)
ball_to_ball_collision_sound = pygame.mixer.Sound(resource_path("assets/sounds/ball_to_ball_collision.mp3"))
ball_to_ball_collision_sound.set_volume(0.5)

def load_scaled_image(path, width=None, height=None, maintain_aspect=True):

    try:
        image = pygame.image.load(resource_path(path)).convert_alpha()
        orig_width, orig_height = image.get_size()

        if maintain_aspect:

            if width and not height:
                height = int(orig_height * (width / orig_width))
            elif height and not width:
                width = int(orig_width * (height / orig_height))
            elif width and height:
                scale = min(width / orig_width, height / orig_height)
                width, height = int(orig_width * scale), int(orig_height * scale)
        return pygame.transform.smoothscale(image, (width, height))

    except Exception as e:
        placeholder = pygame.Surface((width or 50, height or 50), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 255), (0, 0, width or 50, height or 50))
        return placeholder

class Ball:

    def __init__(self, x, y, angle, speed=7):
        self.x, self.y, self.radius = x, y, 12
        self.speed = speed * speed_multiplier
        self.angle = angle
        self.dx = self.speed * math.cos(angle)
        self.dy = -self.speed * math.sin(angle)
        self.state = "flying"
        self.landed_y = cannon.beam_y
        self.return_speed = 5
        self.ball_icon = load_scaled_image("assets/images/ball.png", 24, 24)
        self.landing_time = -1

    def move(self):

        if self.state == "flying":
            self.x += self.dx
            self.y += self.dy

            if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
                self.dx *= -1

            if self.y - self.radius <= 0:
                self.dy *= -1

            if self.dy > 0 and self.y + self.radius >= cannon.beam_y:
                self.state = "landed"
                self.y = cannon.beam_y - self.radius + 4
                self.landing_time = pygame.time.get_ticks()
        elif self.state == "returning":
            target_y = cannon.beam_y - self.radius

            if self.y < target_y:
                self.y += self.return_speed

                if self.y > target_y:
                    self.y = target_y
            else:

                if abs(self.x - cannon.x) < self.return_speed:
                    balls.remove(self)
                elif self.x < cannon.x:
                    self.x += self.return_speed
                else:
                    self.x -= self.return_speed

    def draw(self, screen):
        screen.blit(self.ball_icon, self.ball_icon.get_rect(center=(int(self.x), int(self.y))))

class Box:

    def __init__(self, x, y, hits, box_type="normal"):
        self.x, self.y = x, y
        self.width, self.height = 68, 55
        self.hits = hits
        self.box_type = box_type
        self.image = self.create_box_image()

    def create_box_image(self):

        if self.box_type == "ball":
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            ball_img = load_scaled_image("assets/images/ball.png", 24, 24)
            rect = ball_img.get_rect(center=(self.width // 2, self.height // 2))
            surface.blit(ball_img, rect)
            return surface
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, BOX_COLOR, (0, 0, self.width, self.height), border_radius=5)
        pygame.draw.rect(box_surface, (200, 50, 50), (0, 0, self.width, self.height), width=2, border_radius=5)
        shadow = pygame.Surface((self.width, 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 50))
        box_surface.blit(shadow, (2, self.height - 2))
        font = pygame.font.SysFont("Arial", 24)
        txt = font.render(str(self.hits), True, WHITE)
        text_rect = txt.get_rect(center=(self.width // 2, self.height // 2))
        box_surface.blit(txt, text_rect)
        return box_surface

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def collide(self, ball):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        closest_x = max(rect.left, min(ball.x, rect.right))
        closest_y = max(rect.top, min(ball.y, rect.bottom))
        dx = ball.x - closest_x
        dy = ball.y - closest_y
        distance_squared = dx*dx + dy*dy

        if distance_squared < ball.radius * ball.radius:

            if distance_squared == 0:
                left_dist = ball.x - rect.left
                right_dist = rect.right - ball.x
                top_dist = ball.y - rect.top
                bottom_dist = rect.bottom - ball.y
                min_dist = min(left_dist, right_dist, top_dist, bottom_dist)

                if min_dist == left_dist:
                    ball.x = rect.left - ball.radius
                    ball.dx *= -1
                elif min_dist == right_dist:
                    ball.x = rect.right + ball.radius
                    ball.dx *= -1
                elif min_dist == top_dist:
                    ball.y = rect.top - ball.radius
                    ball.dy *= -1
                else:
                    ball.y = rect.bottom + ball.radius
                    ball.dy *= -1
            else:
                distance = math.sqrt(distance_squared)
                nx, ny = dx/distance, dy/distance
                overlap = ball.radius - distance
                ball.x += nx * overlap
                ball.y += ny * overlap
                dot = ball.dx * nx + ball.dy * ny
                ball.dx -= 2 * dot * nx
                ball.dy -= 2 * dot * ny
                speed = math.sqrt(ball.dx**2 + ball.dy**2)

                if speed > 0:
                    ball.dx = ball.dx / speed * ball.speed
                    ball.dy = ball.dy / speed * ball.speed

            if self.box_type == "ball":
                return "ball"
            else:
                self.hits -= 1
                self.image = self.create_box_image()
                ball_collosion_sound.play()
                return True
        return False

class Cannon:

    def __init__(self):
        self.x = WIDTH // 2
        self.beam_height = 60
        self.beam_y = HEIGHT - self.beam_height
        self.y = self.beam_y - 1
        self.moving = False
        self.target_x = WIDTH // 2
        self.move_speed = 6
        self.last_angle_deg = 0
        self.beam_image = load_scaled_image("assets/images/base.png", WIDTH, self.beam_height)
        self.cannon_image = load_scaled_image("assets/images/cannon.png", 120, 120)

    def draw(self, screen, mouse_pos):
        global line_y
        line_y = self.y - 60
        pygame.draw.line(screen, (255, 0, 0), (0, line_y), (WIDTH, line_y), 3)

        if mouse_pos[1] < self.beam_y:
            dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
            self.last_angle_deg = math.degrees(math.atan2(dy, dx))
        rotated = pygame.transform.rotate(self.cannon_image, -self.last_angle_deg)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

    def shoot(self, mouse_pos):
        global turn_completed

        if cannon_balls <= 0 or not turn_completed:
            return

        if mouse_pos[1] >= self.beam_y:
            return
        dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
        angle = math.atan2(-dy, dx)
        for i in range(cannon_balls):
            delay = i * 3
            offset_x = -i * 10 * math.cos(angle)
            offset_y = i * 10 * math.sin(angle)
            tip_x = max(12, min(WIDTH - 12, self.x + offset_x))
            tip_y = self.y + offset_y
            balls.append(DelayedBall(tip_x, tip_y, angle, delay))
        cannon_sound.play()
        turn_completed = False

    def draw_beam(self, screen):
        for x in range(0, WIDTH, self.beam_image.get_width()):
            screen.blit(self.beam_image, (x, self.beam_y))

    def move_to_target(self):
        self.target_x = max(60, min(WIDTH - 60, self.target_x))

        if abs(self.target_x - self.x) < self.move_speed:
            self.x = self.target_x
            self.moving = False
        elif self.target_x > self.x:
            self.x += self.move_speed
        else:
            self.x -= self.move_speed

class DelayedBall(Ball):

    def __init__(self, x, y, angle, delay_frames):
        super().__init__(x, y, angle)
        self.delay_frames = delay_frames
        self.started = False

    def move(self):

        if self.delay_frames > 0:
            self.delay_frames -= 1
        else:
            self.started = True
            super().move()

    def draw(self, screen):

        if self.started:
            super().draw(screen)

class Particle:

    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
cannon = Cannon()
balls, boxes, particles = [], [], []

def spawn_boxes():
    boxes.clear()
    total_positions = 6
    missing_count = random.randint(1, 2)
    positions = list(range(total_positions))
    random.shuffle(positions)
    ball_pos = positions[0]
    missing_positions = set(random.sample(positions[1:], missing_count))
    x_start = (WIDTH - total_positions * 70) // 2
    for i in range(total_positions):
        x = x_start + i * 70
        y = 100

        if i == ball_pos:
            boxes.append(Box(x, y, 1, "ball"))
        elif i not in missing_positions:
            boxes.append(Box(x, y, random.randint(level, level + 4)))

def move_boxes_down():
    global game_over, game_over_sound_played
    for box in boxes:
        box.y += 60

        if box.y + box.height >= line_y:

            if not game_over:
                game_over = True

                if not game_over_sound_played:
                    game_over_sound.play()
                    game_over_sound_played = True
            return False
    return True

def generate_new_row():
    global balls_collected_this_turn
    total_positions = 6
    missing_count = random.randint(1, 2)
    positions = list(range(total_positions))
    random.shuffle(positions)
    ball_pos = positions[0]
    missing_positions = set(random.sample(positions[1:], missing_count))
    x_start = (WIDTH - total_positions * 70) // 2
    for i in range(total_positions):
        x = x_start + i * 70
        y = 100

        if i == ball_pos:
            boxes.append(Box(x, y, 1, "ball"))
        elif i not in missing_positions:
            boxes.append(Box(x, y, random.randint(level, level + 4)))
    balls_collected_this_turn = 0
spawn_boxes()
background = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    c = 200 - int(100 * y / HEIGHT)
    pygame.draw.line(background, (c, c, 255), (0, y), (WIDTH, y))
running = True

def update():
    global running, cannon_balls, balls_to_shoot, turn_completed
    global level, balls_collected_this_turn, game_over

    if not running:
        return

    if paused:
        root.after(16, update)
        return
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            cannon.shoot(pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN and game_over:

            if event.key == pygame.K_r:
                reset_game()
    screen.blit(background, (0, 0))

    if not game_over:
        particles[:] = [p for p in particles if p.update()]

        if not cannon.moving:
            flying = [b for b in balls if b.state == "flying"]
            landed = [b for b in balls if b.state == "landed"]

            if not flying and landed:
                last = max(landed, key=lambda b: b.landing_time)
                cannon.moving = True
                cannon.target_x = last.x
                for b in landed:
                    b.state = "returning"

        if cannon.moving:
            cannon.move_to_target()

        if not cannon.moving and not balls and not turn_completed:

            if not move_boxes_down():
                pass
            else:
                level += 1
                generate_new_row()
                turn_completed = True
                cannon_balls += balls_collected_this_turn
                balls_to_shoot = 1
        for ball in balls[:]:
            ball.move()
            ball.draw(screen)

            if ball.state == "flying":
                for box in boxes[:]:
                    result = box.collide(ball)

                    if result == "ball":
                        boxes.remove(box)
                        cannon_balls += 1
                        balls_collected_this_turn += 1
                        ball_to_ball_collision_sound.play()
                        for _ in range(10):
                            particles.append(Particle(ball.x, ball.y, (255, 255, 100)))
                        break
                    elif result:
                        for _ in range(8):
                            particles.append(Particle(ball.x, ball.y, (255, 150, 150)))

                        if box.hits <= 0:
                            boxes.remove(box)
                        break
        for box in boxes:
            box.draw(screen)
        cannon.draw_beam(screen)
        cannon.draw(screen, pygame.mouse.get_pos())
        font = pygame.font.SysFont("Arial", 24)

        if cannon_balls == 1:
            screen.blit(font.render(f"Ball: {cannon_balls}", True, BLACK), (10, 10))
        elif cannon_balls > 1:
            screen.blit(font.render(f"Balls: {cannon_balls}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, BLACK), (WIDTH - 100, 10))
    for p in particles:
        p.draw(screen)

    if game_over:
        draw_game_over_screen()
    pygame.display.flip()
    root.after(16, update)

def draw_game_over_screen():
    global current_font_size, font_growing, game_over_animation, game_over_start_time
    particles.clear()
    speed_button.place_forget()
    play_pause_btn.place_forget()

    if game_over_animation is None:
        game_over_animation = {
            'overlay': pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA),
            'font_size': game_over_font_size,
            'growing': True
        }
        game_over_animation['overlay'].fill((0, 0, 0, OVERLAY_ALPHA))
        game_over_start_time = pygame.time.get_ticks()
    screen.blit(game_over_animation['overlay'], (0, 0))
    anim = game_over_animation

    if anim['growing']:
        anim['font_size'] += font_growth_step

        if anim['font_size'] >= game_over_font_size + 10:
            anim['growing'] = False
    else:
        anim['font_size'] -= font_growth_step

        if anim['font_size'] <= game_over_font_size - 5:
            anim['growing'] = True
    font = pygame.font.SysFont("Helvetica", int(anim['font_size']), bold=True)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    screen.blit(text, text_rect)
    level_font = pygame.font.SysFont("Arial", 36)
    level_text = level_font.render(f"Level: {level}", True, (255, 255, 255))
    level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    screen.blit(level_text, level_rect)
    global restart_button

    if pygame.time.get_ticks() - game_over_start_time > 10 and restart_button is None:
        restart_button = tk.Button(root, text="Restart", font=("Arial", 14), bg="#0bf43a", fg="black", bd=0, activebackground="#b2f40b",
                                command=reset_game)
        restart_button.place(x=WIDTH//2 - 50, y=HEIGHT//2 + 70, width=100, height=35)

def reset_game():
    global cannon_balls, balls_to_shoot, turn_completed, level
    global restart_button
    global balls_collected_this_turn, boxes, balls, particles, game_over
    global game_over_animation, game_over_sound_played

    if restart_button:
        restart_button.destroy()
        restart_button = None
    cannon_balls = 1
    balls_to_shoot = 1
    turn_completed = True
    level = 1
    balls_collected_this_turn = 0
    game_over = False
    game_over_animation = None
    game_over_sound_played = False
    balls.clear()
    boxes.clear()
    particles.clear()
    spawn_boxes()
    speed_button.place(x=WIDTH//2 + 200, y=HEIGHT - 35, width=40, height=25)
    play_pause_btn.place(x=WIDTH//2,y=HEIGHT//2-310 )
img_1X= Image.open(resource_path(r"assets\images\1x_speedup.png")).resize((50, 30))
icon_1X= ImageTk.PhotoImage(img_1X)
img_2X= Image.open(resource_path(r"assets\images\2x_speedup.png")).resize((40, 30))
icon_2X= ImageTk.PhotoImage(img_2X)

def toggle_speed():
    global speed_multiplier
    new_multiplier = 2.0 if speed_multiplier == 1.0 else 1.0
    for ball in balls:

        if isinstance(ball, DelayedBall) and not ball.started:
            continue
        old_speed = ball.speed

        if old_speed == 0:
            continue
        scale_factor = new_multiplier / speed_multiplier
        ball.speed *= scale_factor
        ball.dx *= scale_factor
        ball.dy *= scale_factor
    speed_multiplier = new_multiplier
    speed_button.config(image=icon_2X if speed_multiplier == 2.0 else icon_1X)
speed_button = tk.Button(root,image=icon_1X, bg="#DBD594", activebackground="#DBD594",
                                command=toggle_speed, bd=0)
speed_button.place(x=WIDTH//2 + 200, y=HEIGHT - 35, width=40, height=30, )
play_image= Image.open(resource_path(r"assets\images\play.png")).resize((20, 20))
play_icon= ImageTk.PhotoImage(play_image)
pause_image= Image.open(resource_path(r"assets\images\pause.png")).resize((15, 20))
pause_icon= ImageTk.PhotoImage(pause_image)
play_pause_btn = tk.Button(root, image=pause_icon, bg="#C4C4FF", activebackground="#C4C4FF",
                                command=None, bd=0)
play_pause_btn.place(x=WIDTH//2,y=HEIGHT//2-310 )
pause_overlay = tk.Frame(root, bg="#9696FF", width=200, height=150)
pause_overlay.place(x = WIDTH//2, y=HEIGHT//2,anchor='center')
pause_overlay.place_forget()

def resume_game():
    global paused
    paused = False
    pause_overlay.place_forget()
    play_pause_btn.config(image=pause_icon,state="normal")
continue_playing_btn = tk.Button(pause_overlay, text="Continue", font=("Arial", 15), bg="#20C107",activebackground="#20C107", fg="white",activeforeground='white',bd=0, command=resume_game)
continue_playing_btn.place(relx=0.5, rely=0.3, anchor="center")
new_playing_btn = tk.Button(pause_overlay, text="New Game", font=("Arial", 15), bg="#2937F9",activebackground="#2937F9", fg="white",activeforeground='white',bd=0, command=lambda: [resume_game(), reset_game()])
new_playing_btn.place(relx=0.5, rely=0.7, anchor="center")

def toggle_pause():
    global paused
    paused = not paused

    if paused:
        pause_overlay.place(x = WIDTH//2, y=HEIGHT//2, anchor="center")
        play_pause_btn.config(image=play_icon,state="disabled")
    else:
        pause_overlay.place_forget()
        play_pause_btn.config(image=pause_icon,state="normal")
play_pause_btn.config(command=toggle_pause)

def on_closing():
    global running, restart_button

    if restart_button:
        restart_button.destroy()
    running = False
    pygame.quit()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)
update()
root.mainloop()
