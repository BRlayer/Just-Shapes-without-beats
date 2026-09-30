"""
Just Shapes without Beats
Made by BR_Creator
"""

import tkinter as tk
import random
import math
import time


WIDTH, HEIGHT = 800, 600
FPS           = 60
PLAYER_SIZE   = 18
PLAYER_SPEED  = 5
INVINCIBLE_FRAMES = 45
MAX_LIVES     = 4

DASH_SPEED    = 22
DASH_DURATION = 10
DASH_COOLDOWN = 35

TRAIL_MAX_AGE    = 18
AVALANCHE_EVERY  = 30
AVALANCHE_WARN   = 5

PASS = 13579

BG_COLOR       = "#0a0012"
PLAYER_COLOR   = "#ff2d78"
PLAYER_OUTLINE = "#ff80b0"
DANGER_COLOR   = "#ff3030"
DANGER_OUTLINE = "#ff8888"
WARN_COLOR     = "#ffaa00"
BURST_WARN     = "#00ff88"
WAVE_WARN      = "#ff00ff"
TEXT_COLOR     = "#ffffff"
DIM_COLOR      = "#440033"
LIFE_COLOR     = "#ff2d78"
SCORE_COLOR    = "#00ffcc"
DASH_COLOR     = "#00eeff"
AVAL_COLOR     = "#ff6600"
BOSS_COLOR     = "#cc00ff"
BOSS_OUTLINE   = "#ff88ff"
BOSS_HP_COLOR  = "#cc00ff"
BOSS_HP_BG     = "#220033"
RLASER_WARN  = "#ff8800"
SPIRAL_WARN  = "#00ffaa"
SHOCK_WARN   = "#ff00ff"
CROSS_WARN   = "#ffff00"

class Obstacle:
    def __init__(self, canvas, otype, **kwargs):
        self.canvas     = canvas
        self.otype      = otype
        self.alive      = True
        self.warn_timer = kwargs.get("warn_time", 40)
        self.lifetime   = kwargs.get("lifetime", 90)
        self.age        = 0
        self.ids        = []
        self._init(**kwargs)

    def _init(self, **kwargs): pass

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer + self.lifetime:
            self.alive = False

    def draw(self): pass
    def collides(self, px, py): return False

    def delete(self):
        for i in self.ids:
            try: self.canvas.delete(i)
            except Exception: pass
        self.ids = []

    @property
    def active(self): return self.age > self.warn_timer
    def _wb(self): return (self.age // 5) % 2 == 0


class BeamH(Obstacle):
    def _init(self, **kwargs):
        self.y  = kwargs.get("y", HEIGHT // 2)
        self.th = kwargs.get("thickness", 30)

    def draw(self):
        self.delete()
        if not self.alive: return
        t = self.th
        if self.active:
            self.ids = [self.canvas.create_rectangle(0, self.y-t//2, WIDTH, self.y+t//2,
                fill=DANGER_COLOR, outline=DANGER_OUTLINE, width=2, tags="obs")]
        elif self._wb():
            self.ids = [self.canvas.create_rectangle(0, self.y-t//2, WIDTH, self.y+t//2,
                fill="", outline=WARN_COLOR, width=2, tags="obs")]

    def collides(self, px, py):
        return self.active and abs(py - self.y) < self.th//2 + PLAYER_SIZE//2


class BeamV(Obstacle):
    def _init(self, **kwargs):
        self.x  = kwargs.get("x", WIDTH // 2)
        self.th = kwargs.get("thickness", 30)

    def draw(self):
        self.delete()
        if not self.alive: return
        t = self.th
        if self.active:
            self.ids = [self.canvas.create_rectangle(self.x-t//2, 0, self.x+t//2, HEIGHT,
                fill=DANGER_COLOR, outline=DANGER_OUTLINE, width=2, tags="obs")]
        elif self._wb():
            self.ids = [self.canvas.create_rectangle(self.x-t//2, 0, self.x+t//2, HEIGHT,
                fill="", outline=WARN_COLOR, width=2, tags="obs")]

    def collides(self, px, py):
        return self.active and abs(px - self.x) < self.th//2 + PLAYER_SIZE//2


class Ball(Obstacle):
    def _init(self, **kwargs):
        self.x      = float(kwargs.get("x", -30))
        self.y      = float(kwargs.get("y", HEIGHT//2))
        self.speed  = kwargs.get("speed", 2.5)
        self.radius = kwargs.get("radius", 18)
        self.tx = WIDTH//2; self.ty = HEIGHT//2

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer + self.lifetime: self.alive = False
        if self.active:
            dx = self.tx - self.x; dy = self.ty - self.y
            d = math.hypot(dx, dy) or 1
            self.x += self.speed*dx/d; self.y += self.speed*dy/d

    def update_target(self, px, py): self.tx=px; self.ty=py

    def draw(self):
        self.delete()
        if not self.alive: return
        r = self.radius
        if self.active:
            self.ids = [self.canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r,
                fill=DANGER_COLOR, outline=DANGER_OUTLINE, width=2, tags="obs")]
        elif self._wb():
            self.ids = [self.canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r,
                fill="", outline=WARN_COLOR, width=2, tags="obs")]

    def collides(self, px, py):
        return self.active and math.hypot(px-self.x, py-self.y) < self.radius+PLAYER_SIZE//2


class CircleWave(Obstacle):
    def _init(self, **kwargs):
        self.cx   = kwargs.get("cx", WIDTH//2)
        self.cy   = kwargs.get("cy", HEIGHT//2)
        self.maxr = kwargs.get("max_radius", max(WIDTH, HEIGHT))
        self.th   = kwargs.get("thickness", 35)
        self.speed_mult = kwargs.get("speed_mult", 0.75)
        self.radius = 0

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer + self.lifetime: self.alive = False
        if self.active:
            self.radius = ((self.age - self.warn_timer) / self.lifetime) * self.maxr * self.speed_mult

    def draw(self):
        self.delete()
        if not self.alive: return
        ids = []
        if self.active:
            r=self.radius; t=self.th
            ids.append(self.canvas.create_oval(
                self.cx-r-t, self.cy-r-t, self.cx+r+t, self.cy+r+t,
                fill="", outline=WAVE_WARN, width=t, tags="obs"))
        elif self._wb():
            s = 14
            ids.append(self.canvas.create_oval(
                self.cx-s, self.cy-s, self.cx+s, self.cy+s,
                fill="", outline=WAVE_WARN, width=3, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx-s-6, self.cy, self.cx+s+6, self.cy,
                fill=WAVE_WARN, width=2, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx, self.cy-s-6, self.cx, self.cy+s+6,
                fill=WAVE_WARN, width=2, tags="obs"))
        self.ids = ids

    def collides(self, px, py):
        if not self.active: return False
        d = math.hypot(px-self.cx, py-self.cy)
        r=self.radius; t=self.th
        return r-t-PLAYER_SIZE < d < r+t+PLAYER_SIZE


class DangerZone(Obstacle):
    def _init(self, **kwargs):
        self.rx=kwargs.get("rx",100); self.ry=kwargs.get("ry",100)
        self.rw=kwargs.get("rw",120); self.rh=kwargs.get("rh",80)

    def draw(self):
        self.delete()
        if not self.alive: return
        if self.active:
            self.ids=[self.canvas.create_rectangle(
                self.rx, self.ry, self.rx+self.rw, self.ry+self.rh,
                fill=DANGER_COLOR, outline=DANGER_OUTLINE, width=2, tags="obs")]
        elif (self.age//6)%2==0:
            self.ids=[self.canvas.create_rectangle(
                self.rx, self.ry, self.rx+self.rw, self.ry+self.rh,
                fill="", outline=WARN_COLOR, width=2, tags="obs")]

    def collides(self, px, py):
        return (self.active and
                self.rx-PLAYER_SIZE < px < self.rx+self.rw+PLAYER_SIZE and
                self.ry-PLAYER_SIZE < py < self.ry+self.rh+PLAYER_SIZE)


class LaserDiag(Obstacle):
    def _init(self, **kwargs):
        self.slope  = kwargs.get("slope", 1)
        self.offset = kwargs.get("offset", 0)
        self.th     = kwargs.get("thickness", 28)

    def draw(self):
        self.delete()
        if not self.alive: return
        y0=self.offset; y1=self.offset+self.slope*WIDTH
        if self.active:
            self.ids=[self.canvas.create_line(0, y0, WIDTH, y1,
                fill=DANGER_COLOR, width=self.th, tags="obs")]
        elif self._wb():
            self.ids=[self.canvas.create_line(0, y0, WIDTH, y1,
                fill=WARN_COLOR, width=2, tags="obs")]

    def collides(self, px, py):
        if not self.active: return False
        dist = abs(self.slope*px - py + self.offset) / math.sqrt(self.slope**2+1)
        return dist < self.th//2+PLAYER_SIZE//2


class BallBurst(Obstacle):
    def _init(self, **kwargs):
        self.cx    = kwargs.get("cx", WIDTH//2)
        self.cy    = kwargs.get("cy", HEIGHT//2)
        self.count = kwargs.get("count", 6)
        self.speed = kwargs.get("speed", 3.0)
        self.radius= kwargs.get("radius", 14)
        angs = [2*math.pi*i/self.count for i in range(self.count)]
        self.balls=[{"x":float(self.cx),"y":float(self.cy),
                     "dx":math.cos(a)*self.speed,"dy":math.sin(a)*self.speed} for a in angs]

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer+self.lifetime: self.alive=False
        if self.active:
            for b in self.balls:
                b["x"]+=b["dx"]; b["y"]+=b["dy"]

    def draw(self):
        self.delete()
        if not self.alive: return
        r=self.radius; ids=[]
        if self.active:
            for b in self.balls:
                ids.append(self.canvas.create_oval(
                    b["x"]-r, b["y"]-r, b["x"]+r, b["y"]+r,
                    fill=DANGER_COLOR, outline=DANGER_OUTLINE, width=2, tags="obs"))
        elif self._wb():
            s = 12
            pts = [self.cx, self.cy-s, self.cx+s, self.cy+s, self.cx-s, self.cy+s]
            ids.append(self.canvas.create_polygon(pts,
                fill="", outline=BURST_WARN, width=2, tags="obs"))
            ids.append(self.canvas.create_oval(
                self.cx-5, self.cy-5, self.cx+5, self.cy+5,
                fill=BURST_WARN, outline="", tags="obs"))
        self.ids=ids

    def collides(self, px, py):
        if not self.active: return False
        r=self.radius
        return any(math.hypot(px-b["x"],py-b["y"])<r+PLAYER_SIZE//2 for b in self.balls)


class RotatingLaser(Obstacle):
    def _init(self, **kwargs):
        self.cx        = kwargs.get("cx", WIDTH//2)
        self.cy        = kwargs.get("cy", HEIGHT//2)
        self.angle     = kwargs.get("start_angle", 0.0)
        self.rot_speed = kwargs.get("rot_speed", 0.035)
        self.th        = kwargs.get("thickness", 18)
        self.length    = max(WIDTH, HEIGHT) * 1.5
        self.turns     = kwargs.get("turns", 1.5)
        self.total_rot = self.turns * 2 * math.pi

    def tick(self):
        self.age += 1
        if self.active:
            self.angle += self.rot_speed
        total_frames = int(self.total_rot / abs(self.rot_speed))
        if self.age > self.warn_timer + total_frames:
            self.alive = False

    def draw(self):
        self.delete()
        if not self.alive: return
        ids = []
        if self.active:
            ex = self.cx + math.cos(self.angle) * self.length
            ey = self.cy + math.sin(self.angle) * self.length
            ids.append(self.canvas.create_line(
                self.cx, self.cy, ex, ey,
                fill="#660000", width=self.th+10, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx, self.cy, ex, ey,
                fill=DANGER_COLOR, width=self.th, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx, self.cy, ex, ey,
                fill="#ffaaaa", width=max(2, self.th//3), tags="obs"))
        elif self._wb():
            arc_len = BOSS_SIZE + 55
            for step in range(10):
                a = self.angle + step * (0.18 if self.rot_speed > 0 else -0.18)
                ex = self.cx + math.cos(a) * (arc_len + step*4)
                ey = self.cy + math.sin(a) * (arc_len + step*4)
                r2 = max(3, 7 - step//2)
                ids.append(self.canvas.create_oval(
                    ex-r2, ey-r2, ex+r2, ey+r2,
                    fill=RLASER_WARN, outline="", tags="obs"))
            a_tip = self.angle + 9 * (0.18 if self.rot_speed > 0 else -0.18)
            ex = self.cx + math.cos(a_tip) * (arc_len + 36)
            ey = self.cy + math.sin(a_tip) * (arc_len + 36)
            ids.append(self.canvas.create_oval(ex-9, ey-9, ex+9, ey+9,
                fill=RLASER_WARN, outline="", tags="obs"))
            ids.append(self.canvas.create_oval(
                self.cx-14, self.cy-14, self.cx+14, self.cy+14,
                fill="", outline=RLASER_WARN, width=3, tags="obs"))
            ids.append(self.canvas.create_text(
                self.cx, self.cy - BOSS_SIZE - 18, text="!! LASER !!",
                font=("Courier",10,"bold"), fill=RLASER_WARN, tags="obs"))
        self.ids = ids

    def collides(self, px, py):
        if not self.active: return False
        dx = math.cos(self.angle); dy = math.sin(self.angle)
        vx = px - self.cx; vy = py - self.cy
        t = vx*dx + vy*dy
        if t < 0: return False
        perp = abs(vx*dy - vy*dx)
        return perp < self.th//2 + PLAYER_SIZE//2


class BossSpiral(Obstacle):
    def _init(self, **kwargs):
        self.cx      = kwargs.get("cx", WIDTH//2)
        self.cy      = kwargs.get("cy", HEIGHT//2)
        self.speed   = kwargs.get("speed", 5.0)
        self.radius  = kwargs.get("radius", 10)
        self.arms    = kwargs.get("arms", 10)
        self.rate    = kwargs.get("rate", 10)
        self.projectiles = []
        self.angle   = 0.0

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer + self.lifetime: self.alive = False
        if self.active:
            if (self.age - self.warn_timer) % self.rate == 0:
                for arm in range(self.arms):
                    a = self.angle + (2*math.pi*arm/self.arms)
                    self.projectiles.append({
                        "x": float(self.cx), "y": float(self.cy),
                        "dx": math.cos(a)*self.speed,
                        "dy": math.sin(a)*self.speed
                    })
                self.angle += 0.18
            for p in self.projectiles:
                p["x"] += p["dx"]; p["y"] += p["dy"]
            self.projectiles = [p for p in self.projectiles
                                 if -50 < p["x"] < WIDTH+50 and -50 < p["y"] < HEIGHT+50]

    def draw(self):
        self.delete()
        if not self.alive: return
        r = self.radius; ids = []
        if self.active:
            for p in self.projectiles:
                ids.append(self.canvas.create_oval(
                    p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r,
                    fill=BOSS_COLOR, outline=BOSS_OUTLINE, width=1, tags="obs"))
        elif self._wb():
            for arm in range(self.arms):
                for step in range(4):
                    a = (self.age * 0.12) + (2*math.pi*arm/self.arms) + step*0.45
                    dist = BOSS_SIZE + 12 + step*14
                    ex = self.cx + math.cos(a)*dist
                    ey = self.cy + math.sin(a)*dist
                    r2 = 6 - step
                    ids.append(self.canvas.create_oval(
                        ex-r2, ey-r2, ex+r2, ey+r2,
                        fill=SPIRAL_WARN, outline="", tags="obs"))
            ids.append(self.canvas.create_oval(
                self.cx-12, self.cy-12, self.cx+12, self.cy+12,
                fill="", outline=SPIRAL_WARN, width=2, tags="obs"))
            ids.append(self.canvas.create_text(
                self.cx, self.cy - BOSS_SIZE - 18, text="!! ESPIRAL !!",
                font=("Courier",10,"bold"), fill=SPIRAL_WARN, tags="obs"))
        self.ids = ids

    def collides(self, px, py):
        if not self.active: return False
        r = self.radius
        return any(math.hypot(px-p["x"],py-p["y"]) < r+PLAYER_SIZE//2
                   for p in self.projectiles)


class BossShockwave(Obstacle):
    def _init(self, **kwargs):
        self.cx    = kwargs.get("cx", WIDTH//2)
        self.cy    = kwargs.get("cy", HEIGHT//2)
        self.th    = kwargs.get("thickness", 20)
        self.count = kwargs.get("count", 3)
        self.gap   = kwargs.get("gap", 60)
        self.maxr  = max(WIDTH, HEIGHT) * 1.5
        self.radius = 0

    def tick(self):
        self.age += 1
        if self.age > self.warn_timer + self.lifetime: self.alive = False
        if self.active:
            self.radius = ((self.age - self.warn_timer) / self.lifetime) * self.maxr * 0.6

    def draw(self):
        self.delete()
        if not self.alive: return
        ids = []
        if self.active:
            t = self.th
            for i in range(self.count):
                r = max(0, self.radius - i * self.gap)
                if r <= 0: continue
                ids.append(self.canvas.create_oval(
                    self.cx-r-t, self.cy-r-t, self.cx+r+t, self.cy+r+t,
                    fill="", outline=BOSS_OUTLINE, width=t, tags="obs"))
        elif self._wb():
            for i in range(self.count):
                s = BOSS_SIZE + 8 + i*18
                ids.append(self.canvas.create_oval(
                    self.cx-s, self.cy-s, self.cx+s, self.cy+s,
                    fill="", outline=SHOCK_WARN, width=3, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx-12, self.cy, self.cx+12, self.cy,
                fill=SHOCK_WARN, width=3, tags="obs"))
            ids.append(self.canvas.create_line(
                self.cx, self.cy-12, self.cx, self.cy+12,
                fill=SHOCK_WARN, width=3, tags="obs"))
            label_y = self.cy - BOSS_SIZE - self.count*18 - 14
            ids.append(self.canvas.create_text(
                self.cx, label_y, text="!! ONDA !!",
                font=("Courier",10,"bold"), fill=SHOCK_WARN, tags="obs"))
        self.ids = ids

    def collides(self, px, py):
        if not self.active: return False
        d = math.hypot(px-self.cx, py-self.cy)
        t = self.th
        for i in range(self.count):
            r = self.radius - i*self.gap
            if r > 0 and r-t-PLAYER_SIZE < d < r+t+PLAYER_SIZE:
                return True
        return False


class BossCross(Obstacle):
    def _init(self, **kwargs):
        self.cx  = kwargs.get("cx", WIDTH//2)
        self.cy  = kwargs.get("cy", HEIGHT//2)
        self.th  = kwargs.get("thickness", 22)
        self.rot = kwargs.get("rot", 0.0)

    def draw(self):
        self.delete()
        if not self.alive: return
        ids = []
        angles = [self.rot + a for a in [0, math.pi/2, math.pi/4, 3*math.pi/4]]
        if self.active:
            for a in angles:
                ex = self.cx + math.cos(a)*max(WIDTH,HEIGHT)
                ey = self.cy + math.sin(a)*max(WIDTH,HEIGHT)
                ex2= self.cx - math.cos(a)*max(WIDTH,HEIGHT)
                ey2= self.cy - math.sin(a)*max(WIDTH,HEIGHT)
                ids.append(self.canvas.create_line(
                    ex2, ey2, ex, ey,
                    fill=DANGER_COLOR, width=self.th, tags="obs"))
        elif self._wb():
            line_end = BOSS_SIZE + 70
            for a in angles:
                ex = self.cx + math.cos(a)*line_end
                ey = self.cy + math.sin(a)*line_end
                ex2= self.cx - math.cos(a)*line_end
                ey2= self.cy - math.sin(a)*line_end
                ids.append(self.canvas.create_line(
                    ex2, ey2, ex, ey,
                    fill=CROSS_WARN, width=3, tags="obs"))
                ids.append(self.canvas.create_oval(
                    ex-7, ey-7, ex+7, ey+7,
                    fill=CROSS_WARN, outline="", tags="obs"))
                ids.append(self.canvas.create_oval(
                    ex2-7, ey2-7, ex2+7, ey2+7,
                    fill=CROSS_WARN, outline="", tags="obs"))
            ids.append(self.canvas.create_oval(
                self.cx-10, self.cy-10, self.cx+10, self.cy+10,
                fill=CROSS_WARN, outline="", tags="obs"))
            ids.append(self.canvas.create_text(
                self.cx, self.cy - line_end - 16, text="!! CRUZ !!",
                font=("Courier",10,"bold"), fill=CROSS_WARN, tags="obs"))
        self.ids = ids

    def collides(self, px, py):
        if not self.active: return False
        angles = [self.rot + a for a in [0, math.pi/2, math.pi/4, 3*math.pi/4]]
        for a in angles:
            dx = math.cos(a); dy = math.sin(a)
            vx = px-self.cx; vy = py-self.cy
            perp = abs(vx*dy - vy*dx)
            if perp < self.th//2 + PLAYER_SIZE//2:
                return True
        return False


def lerp_col(c1, c2, t):
    t=max(0.,min(1.,t))
    r1,g1,b1=int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2=int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))


class GameBase:
    def __init__(self, root, canvas, mode):
        self.root   = root
        self.canvas = canvas
        self.mode   = mode
        self.keys   = set()
        self.state  = "playing"

        self.px = self.py = float(WIDTH//2)
        self.lives        = MAX_LIVES
        self.score        = 0
        self.frame        = 0
        self.invincible   = 0
        self.obstacles    = []
        self.difficulty   = 1.0

        self.dashing       = False
        self.dash_frames   = 0
        self.dash_cooldown = 0
        self.dash_dx = self.dash_dy = 0.0
        self.trail   = []

        self.last_score_time = time.time()

        root.bind("<KeyPress>",   lambda e: self._on_keypress(e))
        root.bind("<KeyRelease>", lambda e: self._on_keyrelease(e))
        root.bind("<space>",      lambda e: self._try_dash())
        root.bind("<Shift_L>",    lambda e: self._try_dash())
        root.bind("<Shift_R>",    lambda e: self._try_dash())
        self.admin = AdminPanel(canvas, self)
        root.bind("<Button-1>", lambda e: self.admin.handle_click(e.x, e.y))

    def _on_keypress(self, e):
        self.keys.add(e.keysym)
        if e.keysym == ADMIN_KEY:
            self.admin.toggle()
        elif self.admin.visible:
            self.admin.handle_key(e.keysym)

    def _on_keyrelease(self, e):
        self.keys.discard(e.keysym)

    def _try_dash(self):
        # FIX 3: Permitir dash también en los estados de la secuencia final
        allowed = ("playing", "split_laser_warn", "split_laser", "final_countdown")
        if self.state not in allowed: return
        if self.dashing or self.dash_cooldown > 0: return
        dx = dy = 0.0
        if "Left"  in self.keys or "a" in self.keys: dx -= 1.0
        if "Right" in self.keys or "d" in self.keys: dx += 1.0
        if "Up"    in self.keys or "w" in self.keys: dy -= 1.0
        if "Down"  in self.keys or "s" in self.keys: dy += 1.0
        if dx == 0.0 and dy == 0.0: dy = -1.0
        mag = math.hypot(dx, dy)
        self.dash_dx = dx / mag
        self.dash_dy = dy / mag
        self.dashing = True
        self.dash_frames = DASH_DURATION

    def _handle_input(self):
        if self.admin.visible: return
        self.trail.append({"x":self.px,"y":self.py,"age":0})
        if self.dashing:
            self.px+=self.dash_dx*DASH_SPEED; self.py+=self.dash_dy*DASH_SPEED
            self.dash_frames-=1
            if self.dash_frames<=0:
                self.dashing=False; self.dash_cooldown=DASH_COOLDOWN
        else:
            if self.dash_cooldown>0: self.dash_cooldown-=1
            spd=PLAYER_SPEED
            if "Left"  in self.keys or "a" in self.keys: self.px-=spd
            if "Right" in self.keys or "d" in self.keys: self.px+=spd
            if "Up"    in self.keys or "w" in self.keys: self.py-=spd
            if "Down"  in self.keys or "s" in self.keys: self.py+=spd
        self.px=max(PLAYER_SIZE,min(WIDTH -PLAYER_SIZE,self.px))
        self.py=max(PLAYER_SIZE,min(HEIGHT-PLAYER_SIZE,self.py))
        for p in self.trail: p["age"]+=1
        self.trail=[p for p in self.trail if p["age"]<TRAIL_MAX_AGE]

    def _update_obstacles(self):
        for obs in self.obstacles:
            if isinstance(obs,Ball): obs.update_target(self.px,self.py)
            obs.tick()
        self.obstacles=[o for o in self.obstacles if o.alive]

    def _check_collisions(self):
        if self.dashing: return
        if self.invincible>0: self.invincible-=1; return
        for obs in self.obstacles:
            if obs.collides(self.px,self.py): self._hit(); return

    def _hit(self):
        self.lives-=1; self.invincible=INVINCIBLE_FRAMES
        if self.lives<=0: self._game_over()

    def _game_over(self):
        self.state="gameover"
        for obs in self.obstacles: obs.delete()
        self.obstacles=[]

    def _draw_bg(self):
        self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=BG_COLOR,outline="")
        for x in range(0,WIDTH,40): self.canvas.create_line(x,0,x,HEIGHT,fill="#160020")
        for y in range(0,HEIGHT,40): self.canvas.create_line(0,y,WIDTH,y,fill="#160020")

    def _draw_player(self):
        r=PLAYER_SIZE
        for p in self.trail:
            ratio=1.0-p["age"]/TRAIL_MAX_AGE
            if ratio<=0: continue
            tr=max(2,int(r*ratio*0.85))
            if self.dashing:
                iv=int(ratio*200)
                col="#{:02x}{:02x}{:02x}".format(0,min(255,iv+55),min(255,iv+55))
            else:
                iv=int(ratio*160)
                col="#{:02x}{:02x}{:02x}".format(min(255,iv+75),0,min(255,iv//2+40))
            self.canvas.create_oval(p["x"]-tr,p["y"]-tr,p["x"]+tr,p["y"]+tr,fill=col,outline="")

        blink=self.invincible>0 and (self.invincible//5)%2==0
        if blink: return
        if self.dashing:
            self.canvas.create_oval(self.px-r-7,self.py-r-7,self.px+r+7,self.py+r+7,
                fill="",outline=DASH_COLOR,width=5)
            self.canvas.create_oval(self.px-r,self.py-r,self.px+r,self.py+r,
                fill=DASH_COLOR,outline="#ffffff",width=2)
        else:
            self.canvas.create_oval(self.px-r-4,self.py-r-4,self.px+r+4,self.py+r+4,
                fill="",outline="#880040",width=4)
            self.canvas.create_oval(self.px-r,self.py-r,self.px+r,self.py+r,
                fill=PLAYER_COLOR,outline=PLAYER_OUTLINE,width=2)

    def _draw_lives_and_dash(self, lives_override=None):
        lives = lives_override if lives_override is not None else self.lives
        for i in range(MAX_LIVES):
            cx=20+i*30
            self.canvas.create_oval(cx,12,cx+18,30,
                fill=LIFE_COLOR if i<lives else DIM_COLOR,outline="")
        bx,by,bl=20,HEIGHT-22,150
        self.canvas.create_text(bx,by-14,text="DASH [SPACE/SHIFT]",
            font=("Courier",9),fill=DASH_COLOR,anchor="w")
        self.canvas.create_rectangle(bx,by,bx+bl,by+10,fill="#002233",outline=DASH_COLOR,width=1)
        if self.dashing: fw,fc=bl,"#ffffff"
        else:
            fw=int(bl*(1-self.dash_cooldown/DASH_COOLDOWN))
            fc=DASH_COLOR if self.dash_cooldown==0 else "#005577"
        if fw>0: self.canvas.create_rectangle(bx,by,bx+fw,by+10,fill=fc,outline="")
        st="¡DASH!" if self.dashing else ("LISTO" if self.dash_cooldown==0 else f"{self.dash_cooldown//FPS+1}s")
        self.canvas.create_text(bx+bl+8,by+5,text=st,font=("Courier",9,"bold"),
            fill=DASH_COLOR if self.dash_cooldown==0 else "#556677",anchor="w")

    def _run_go_anim(self, extra_lines=None):
        if self.state!="gameover": return
        self._go_frame+=1
        f=self._go_frame
        self.canvas.delete("all")
        self._draw_bg()
        if f<=20:
            a=int(200*(1-f/20))
            self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,
                fill="#{:02x}0000".format(min(255,a+55)),outline="")
        ty_target=HEIGHT//2-85
        if f<=20: ty=HEIGHT+60
        else:
            prog=min(1.0,(f-20)/25); ease=1-(1-prog)**3
            ty=HEIGHT+60-(HEIGHT+60-ty_target)*ease
        self.canvas.create_text(WIDTH//2+4,ty+4,text="GAME OVER",
            font=("Courier",52,"bold"),fill="#330000")
        self.canvas.create_text(WIDTH//2,ty,text="GAME OVER",
            font=("Courier",52,"bold"),fill=DANGER_COLOR)
        if f>=42:
            lw=min(WIDTH-80,int((f-42)*28))
            if lw>0:
                self.canvas.create_line(
                    WIDTH//2-lw//2,HEIGHT//2-22,WIDTH//2+lw//2,HEIGHT//2-22,
                    fill=DANGER_COLOR,width=2)
        if f>=52:
            self.canvas.create_text(WIDTH//2,HEIGHT//2+8,
                text=f"TIEMPO: {self.score}s",
                font=("Courier",20,"bold"),
                fill=lerp_col("#000000",SCORE_COLOR,min(1.0,(f-52)/14)))
        if extra_lines and f>=70:
            for i,(txt,col) in enumerate(extra_lines):
                self.canvas.create_text(WIDTH//2,HEIGHT//2+48+i*36,text=txt,
                    font=("Courier",14),
                    fill=lerp_col("#000000",col,min(1.0,(f-70-i*14)/14)))
        if f>=108:
            pulse=int(180+75*math.sin(time.time()*3))
            bc="#{:02x}{:02x}{:02x}".format(pulse,pulse,pulse)
            self.canvas.create_text(WIDTH//2,HEIGHT//2+148,
                text="[ CLICK PARA INTENTARLO DE NUEVO ]", # ERROR -> no funciona
                font=("Courier",14,"bold"),fill=bc)
        self.root.after(1000//FPS, lambda: self._run_go_anim(extra_lines))


class NormalMode(GameBase):
    def __init__(self, root, canvas, back_cb):
        super().__init__(root, canvas, "normal")
        self.back_cb        = back_cb
        self.avalanche_timer  = 0
        self.next_avalanche   = AVALANCHE_EVERY * FPS
        self.avalanche_warn   = False
        self.avalanche_active = False
        canvas.bind("<Button-1>", self._on_click)
        self._loop()

    def _on_click(self, _):
        if self.state == "gameover": self.back_cb()

    def _loop(self):
        if self.state != "playing": return
        self.frame+=1
        now=time.time()
        if now-self.last_score_time>=1.0:
            self.score+=1; self.last_score_time=now
        self.difficulty=1.0+(self.score/10)*0.4
        self._handle_input()
        self._tick_avalanche()
        self._spawn_obstacles()
        self._update_obstacles()
        self._check_collisions()
        self._render()
        self.root.after(1000//FPS, self._loop)

    def _tick_avalanche(self):
        self.avalanche_timer+=1
        if self.avalanche_timer==self.next_avalanche-AVALANCHE_WARN*FPS:
            self.avalanche_warn=True
        if self.avalanche_timer>=self.next_avalanche:
            self.avalanche_warn=False; self.avalanche_active=True
            self._launch_avalanche()
            interval=max(15*FPS,int(AVALANCHE_EVERY*FPS/(1+self.score/120)))
            self.next_avalanche=self.avalanche_timer+interval
            self.root.after(2000,lambda: setattr(self,"avalanche_active",False))

    def _launch_avalanche(self):
        d=self.difficulty
        for y in [HEIGHT*i//5 for i in range(1,5)]:
            self.obstacles.append(BeamH(self.canvas,"beam_h",
                y=y,thickness=int(16+d*3),warn_time=28,lifetime=55))
        for x in [WIDTH//4,WIDTH//2,3*WIDTH//4]:
            self.obstacles.append(BeamV(self.canvas,"beam_v",
                x=x,thickness=int(16+d*3),warn_time=28,lifetime=55))
        self.obstacles.append(CircleWave(self.canvas,"cw",
            cx=WIDTH//2,cy=HEIGHT//2,max_radius=max(WIDTH,HEIGHT),
            thickness=int(28+d*5),warn_time=28,lifetime=100))
        for cx,cy in [(0,0),(WIDTH,0),(0,HEIGHT),(WIDTH,HEIGHT)]:
            self.obstacles.append(BallBurst(self.canvas,"burst",
                cx=cx,cy=cy,count=5,speed=3+d*0.5,radius=14,
                warn_time=18,lifetime=120))

    def _spawn_obstacles(self):
        if self.avalanche_active: return
        d=self.difficulty; lvl=int(d)
        base=max(18,int(90/d))
        if self.frame%base==0:
            pool=["beam_h","beam_v"]
            if lvl>=2: pool+=["ball","burst"]
            if lvl>=3: pool+=["circle_wave","laser"]
            if lvl>=4: pool+=["zone","beam_h","beam_v"]
            self._spawn_one(random.choice(pool),d)
        if lvl>=2 and self.frame%(base*2)==base:
            self._spawn_one(random.choice(["beam_h","beam_v","ball"]),d)
        if lvl>=3 and self.frame%(base*3)==base*2:
            for _ in range(2):
                self._spawn_one(random.choice(["ball","burst","laser"]),d)

    def _spawn_one(self,kind,d):
        t=int(20+d*5); lt=lambda b:max(20,int(b/d+20))
        if kind=="beam_h":
            self.obstacles.append(BeamH(self.canvas,"beam_h",
                y=random.randint(t,HEIGHT-t),thickness=t,warn_time=35,lifetime=lt(60)))
        elif kind=="beam_v":
            self.obstacles.append(BeamV(self.canvas,"beam_v",
                x=random.randint(t,WIDTH-t),thickness=t,warn_time=35,lifetime=lt(60)))
        elif kind=="ball":
            side=random.choice(["L","R","T","B"])
            x=-30 if side=="L" else WIDTH+30 if side=="R" else random.randint(0,WIDTH)
            y=-30 if side=="T" else HEIGHT+30 if side=="B" else random.randint(0,HEIGHT)
            self.obstacles.append(Ball(self.canvas,"ball",
                x=x,y=y,speed=2.0+d*0.8,radius=18,warn_time=15,lifetime=lt(180)))
        elif kind=="burst":
            self.obstacles.append(BallBurst(self.canvas,"burst",
                cx=random.randint(60,WIDTH-60),cy=random.randint(60,HEIGHT-60),
                count=int(4+d),speed=2.5+d*0.4,radius=13,warn_time=25,lifetime=lt(120)))
        elif kind=="circle_wave":
            self.obstacles.append(CircleWave(self.canvas,"cw",
                cx=random.randint(80,WIDTH-80),cy=random.randint(80,HEIGHT-80),
                max_radius=max(WIDTH,HEIGHT),thickness=int(22+d*4),
                warn_time=40,lifetime=lt(130)))
        elif kind=="laser":
            slope=random.choice([1,-1])
            px0=random.randint(0,WIDTH); py0=random.randint(0,HEIGHT)
            self.obstacles.append(LaserDiag(self.canvas,"laser",
                slope=slope,offset=py0-slope*px0,thickness=int(22+d*3),
                warn_time=35,lifetime=lt(60)))
        elif kind=="zone":
            rw=random.randint(70,int(200+d*20)); rh=random.randint(50,int(150+d*15))
            self.obstacles.append(DangerZone(self.canvas,"zone",
                rx=random.randint(0,max(1,WIDTH-rw)),
                ry=random.randint(0,max(1,HEIGHT-rh)),
                rw=rw,rh=rh,warn_time=40,lifetime=lt(80)))

    def _render(self):
        self.canvas.delete("all")
        self._draw_bg()
        for obs in self.obstacles: obs.draw()
        self._draw_player()
        self._draw_hud()
        if self.avalanche_warn: self._draw_aval_warning()

    def _draw_hud(self):
        self._draw_lives_and_dash()
        self.canvas.create_text(WIDTH-10,10,text=f"SCORE: {self.score}s",
            font=("Courier",14,"bold"),fill=SCORE_COLOR,anchor="ne")
        lvl=int(self.difficulty); bw=int((self.difficulty%1)*120+10)
        self.canvas.create_text(WIDTH-10,32,text=f"LVL {lvl}",
            font=("Courier",11),fill=WARN_COLOR,anchor="ne")
        self.canvas.create_rectangle(WIDTH-130,45,WIDTH-10,52,fill="#330022",outline="")
        self.canvas.create_rectangle(WIDTH-130,45,WIDTH-130+bw,52,fill=WARN_COLOR,outline="")
        fl=self.next_avalanche-self.avalanche_timer; sl=max(0,math.ceil(fl/FPS))
        if sl<=10:
            self.canvas.create_text(WIDTH//2,18,
                text=f"!! AVALANCHA EN {sl}s !!",
                font=("Courier",11,"bold"),
                fill=AVAL_COLOR if sl<=AVALANCHE_WARN else "#885500")

    def _draw_aval_warning(self):
        pulse=int(128+127*math.sin(time.time()*8))
        col="#{:02x}{:02x}{:02x}".format(min(255,pulse+55),80,0)
        self.canvas.create_text(WIDTH//2,HEIGHT//2,
            text="!! AVALANCHA !!",font=("Courier",42,"bold"),fill=col)

    def _game_over(self):
        super()._game_over()
        aval_count=max(0,int(self.avalanche_timer//(AVALANCHE_EVERY*FPS)))
        self._go_frame=0
        self._run_go_anim([
            (f"NIVEL ALCANZADO: {int(self.difficulty)}", WARN_COLOR),
            (f"AVALANCHAS SUPERADAS: {aval_count}", AVAL_COLOR),
        ])


BOSS_MAX_HP   = 100
BOSS_SIZE     = 45
BOSS_X        = WIDTH  // 2
BOSS_Y        = HEIGHT // 2
MINI_HP            = 6
COMPANION_HP       = 5
MINIBOSS_TIME      = 70
COMPANION_COOLDOWN = 25 * FPS

MINIBOSS_COLOR    = "#ff6600"
MINIBOSS_OUTLINE  = "#ffaa44"
COMPANION_COLOR   = "#aa00ff"
COMPANION_OUTLINE = "#dd88ff"


class SubEntity:
    def __init__(self, canvas, x, y, hp, color, outline, size=28):
        self.canvas  = canvas
        self.x       = float(x)
        self.y       = float(y)
        self.hp      = hp
        self.max_hp  = hp
        self.color   = color
        self.outline = outline
        self.size    = size
        self.alive   = True
        self.hit_flash = 0
        self.hit_cd    = 0
        self.pulse     = 0.0
        self.ids       = []

    def tick(self): self.pulse += 0.1
    def delete(self):
        for i in self.ids:
            try: self.canvas.delete(i)
            except: pass
        self.ids = []

    def draw(self):
        self.delete()
        if not self.alive: return
        r = self.size
        p = math.sin(self.pulse)
        self.ids.append(self.canvas.create_oval(
            self.x-r-5, self.y-r-5, self.x+r+5, self.y+r+5,
            fill="", outline="#220011", width=6))
        if self.hit_flash > 0:
            c = "#{:02x}{:02x}{:02x}".format(255, 255, 255)
        else:
            c = self.color
        self.ids.append(self.canvas.create_oval(
            self.x-r, self.y-r, self.x+r, self.y+r,
            fill=c, outline=self.outline, width=3))
        self.ids.append(self.canvas.create_oval(
            self.x-7, self.y-6+int(p*2), self.x+7, self.y+6+int(p*2),
            fill="#ffffff", outline=""))
        bar_w = r*2; bar_y = self.y + r + 8
        self.canvas.create_rectangle(
            self.x-r, bar_y, self.x+r, bar_y+5, fill="#330000", outline="")
        hp_w = int(bar_w * max(0, self.hp/self.max_hp))
        if hp_w > 0:
            self.canvas.create_rectangle(
                self.x-r, bar_y, self.x-r+hp_w, bar_y+5, fill=self.color, outline="")

    def try_damage(self, px, py, dashing):
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if not dashing or not self.alive: return False
        if self.hit_cd == 0 and math.hypot(px-self.x, py-self.y) < self.size + PLAYER_SIZE:
            self.hp -= 1
            self.hit_flash = 10
            self.hit_cd    = DASH_COOLDOWN + DASH_DURATION
            if self.hp <= 0:
                self.alive = False
            return True
        return False

    def update(self):
        if self.hit_flash > 0: self.hit_flash -= 1
        self.tick()


class Miniboss(SubEntity):
    def __init__(self, canvas, x, y, difficulty=1):
        super().__init__(canvas, x, y, MINI_HP, MINIBOSS_COLOR, MINIBOSS_OUTLINE, size=32)
        self.difficulty = difficulty
        self.attack_timer = 0

    def get_attacks(self, canvas):
        self.attack_timer += 1
        attacks = []
        interval = max(90, int(150 / self.difficulty))
        if self.attack_timer % interval == 0:
            roll = random.random()
            if roll < 0.4:
                attacks.append(BallBurst(canvas, "burst",
                    cx=self.x, cy=self.y,
                    count=5, speed=2.8, radius=12,
                    warn_time=25, lifetime=110))
            elif roll < 0.7:
                attacks.append(BeamH(canvas, "beam_h",
                    y=self.y, thickness=22, warn_time=30, lifetime=50))
            else:
                attacks.append(CircleWave(canvas, "cw",
                    cx=self.x, cy=self.y,
                    max_radius=max(WIDTH, HEIGHT), thickness=22,
                    warn_time=30, lifetime=100))
        return attacks


class Companion(SubEntity):
    def __init__(self, canvas, x, y, difficulty=2):
        super().__init__(canvas, x, y, COMPANION_HP, COMPANION_COLOR, COMPANION_OUTLINE, size=24)
        self.difficulty = difficulty
        self.attack_timer = random.randint(0, 60)

    def get_attacks(self, canvas):
        self.attack_timer += 1
        attacks = []
        interval = max(120, int(180 / self.difficulty))
        if self.attack_timer % interval == 0:
            roll = random.random()
            if roll < 0.5:
                attacks.append(BallBurst(canvas, "burst",
                    cx=self.x, cy=self.y,
                    count=4, speed=2.5, radius=11,
                    warn_time=25, lifetime=100))
            else:
                attacks.append(BeamV(canvas, "beam_v",
                    x=self.x, thickness=20, warn_time=30, lifetime=45))
        return attacks


class BossFightMode(GameBase):
    def __init__(self, root, canvas, back_cb):
        super().__init__(root, canvas, "boss")
        self.back_cb  = back_cb

        self.start_time     = time.time()
        self.damage_taken   = 0
        self.dashes_used    = 0
        self.boss_hits      = 0
        self.phases_cleared = 0

        self.boss_hp        = BOSS_MAX_HP
        self.boss_phase     = 1
        self.boss_alive     = True
        self.boss_pulse     = 0.0
        self.boss_hit_flash = 0
        self.boss_hit_cd    = 0
        self.damage_numbers = []

        self.attack_timer   = 0

        self.miniboss    = None
        self.companions  = []

        self.in_transition      = False
        self.transition_phase   = 0
        self.transition_cleared = False
        self.miniboss_timer     = 0
        self.miniboss_failed    = False
        self.companion_cd       = {2: 0, 3: 0}

        self.death_frame    = 0
        self.death_angle    = 0.0
        self.final_hits     = 0
        self.final_timer    = 0
        self.zoom           = 1.0
        self.zoom_cx        = float(WIDTH//2)
        self.zoom_cy        = float(HEIGHT//2)

        self.alarm_phase    = 0.0

        canvas.bind("<Button-1>", self._on_click)
        self._loop()

    def _hit(self):
        self.damage_taken += 1
        super()._hit()

    def _try_dash(self):
        # FIX 3: contar dashes también en secuencia final
        allowed = ("playing", "split_laser_warn", "split_laser", "final_countdown")
        if self.state not in allowed: return
        if self.dashing or self.dash_cooldown > 0: return
        self.dashes_used += 1
        # Llamar directamente a la lógica de dash (no a super que filtra por state)
        dx = dy = 0.0
        if "Left"  in self.keys or "a" in self.keys: dx -= 1.0
        if "Right" in self.keys or "d" in self.keys: dx += 1.0
        if "Up"    in self.keys or "w" in self.keys: dy -= 1.0
        if "Down"  in self.keys or "s" in self.keys: dy += 1.0
        if dx == 0.0 and dy == 0.0: dy = -1.0
        mag = math.hypot(dx, dy)
        self.dash_dx = dx / mag
        self.dash_dy = dy / mag
        self.dashing = True
        self.dash_frames = DASH_DURATION

    def _on_click(self, _):
        if self.state in ("gameover","won"): self.back_cb()

    def _loop(self):
        if self.state not in ("playing",): return
        if getattr(self, 'admin', None) and self.admin.visible:
            self.root.after(1000//FPS, self._loop); return
        self.frame += 1
        now = time.time()
        if now - self.last_score_time >= 1.0:
            self.score += 1
            self.last_score_time = now

        self.boss_pulse += 0.08
        self.alarm_phase += 0.12

        self._handle_input()

        if self.in_transition:
            self._tick_transition()
        else:
            self._update_phase()
            self._tick_attacks()
            self._tick_companions()

        self._update_obstacles()
        self._check_collisions()
        self._check_entity_damage()
        self._tick_damage_numbers()

        if self.boss_alive and self.boss_hp <= 0 and not self.in_transition:
            self.boss_alive = False
            self._start_death_sequence()
            return

        self._render()
        self.root.after(1000 // FPS, self._loop)

    def _update_phase(self):
        ratio = self.boss_hp / BOSS_MAX_HP
        new_phase = 1 if ratio > 0.66 else 2 if ratio > 0.33 else 3
        if new_phase > self.boss_phase and not self.in_transition:
            self.boss_phase = new_phase
            self._start_transition(new_phase)
            return
        self.difficulty = 1.0 + (3 - ratio * 2)

        p = self.boss_phase
        if p in self.companion_cd and self.companion_cd[p] > 0:
            self.companion_cd[p] -= 1

        if self.boss_phase == 2 and not self.companions and self.companion_cd.get(2,0) == 0:
            if self.boss_hp <= int(BOSS_MAX_HP * 0.50):
                self._spawn_companion()

        if self.boss_phase == 3 and len(self.companions) < 2 and self.companion_cd.get(3,0) == 0:
            if self.boss_hp <= int(BOSS_MAX_HP * 0.20):
                needed = 2 - len(self.companions)
                for _ in range(needed):
                    self._spawn_companion()

    def _spawn_companion(self):
        offsets = [(-180, -80), (180, -80)]
        ox, oy = offsets[len(self.companions) % 2]
        c = Companion(self.canvas,
                      BOSS_X + ox, BOSS_Y + oy,
                      difficulty=self.boss_phase)
        self.companions.append(c)

    def _start_transition(self, to_phase):
        self.in_transition      = True
        self.transition_phase   = to_phase
        self.transition_cleared = False
        self.miniboss_timer     = 0
        self.miniboss_failed    = False
        for obs in self.obstacles: obs.delete()
        self.obstacles = []
        self.companions = []
        diff = 1.0 if to_phase == 2 else 1.8
        mx = BOSS_X + random.choice([-220, 220])
        my = BOSS_Y + random.choice([-100, 100])
        self.miniboss = Miniboss(self.canvas, mx, my, difficulty=diff)

    def _tick_transition(self):
        if self.miniboss is None: return
        self.miniboss_timer += 1
        time_left = max(0, MINIBOSS_TIME - self.miniboss_timer // FPS)
        self.miniboss.update()
        if self.miniboss.alive:
            attacks = self.miniboss.get_attacks(self.canvas)
            self.obstacles.extend(attacks)
            if self.miniboss_timer >= MINIBOSS_TIME * FPS and not self.miniboss_failed:
                self.miniboss_failed = True
                if self.miniboss: self.miniboss.delete()
                self.miniboss = None
                for obs in self.obstacles: obs.delete()
                self.obstacles = []
                self.in_transition = False
                self.boss_hp = int(BOSS_MAX_HP * (0.66 if self.transition_phase == 2 else 0.33)) - 1
        else:
            if not self.transition_cleared:
                self.transition_cleared = True
                self.lives = min(MAX_LIVES, self.lives + 1)
                self.phases_cleared += 1
                self.miniboss.delete()
                self.miniboss = None
                for obs in self.obstacles: obs.delete()
                self.obstacles = []
                self.in_transition = False
                self.boss_hp = int(BOSS_MAX_HP * (0.66 if self.transition_phase == 2 else 0.33)) - 1
        self._miniboss_time_left = time_left

    def _tick_attacks(self):
        self.attack_timer += 1
        p = self.boss_phase
        interval = {1: 185, 2: 210, 3: 130}[p]

        if self.attack_timer % interval == 0:
            self._launch_attack()

        if p == 3:
            if self.attack_timer % 150 == 75:
                self.obstacles.append(BossShockwave(self.canvas, "shockwave",
                    cx=BOSS_X, cy=BOSS_Y, count=3, gap=50, th=18,
                    warn_time=25, lifetime=120))

    def _launch_attack(self):
        p = self.boss_phase
        pool_1 = ["rotating_laser", "cross", "shockwave", "burst"]
        pool_2 = ["rotating_laser", "cross", "shockwave", "burst",
                  "beams", "burst", "cross"]
        pool_3 = ["rotating_laser", "cross", "shockwave", "burst",
                  "beams", "all_beams", "double_laser", "zone_sweep",
                  "homing_burst", "burst", "BossSpiral"]
        pool = {1: pool_1, 2: pool_2, 3: pool_3}[p]
        choice = random.choice(pool)

        if choice == "rotating_laser":
            turns = 1 + (p - 1) * 0.5
            speed = 0.030 + p * 0.006
            self.obstacles.append(RotatingLaser(self.canvas, "rlaser",
                cx=BOSS_X, cy=BOSS_Y,
                start_angle=random.uniform(0, 2*math.pi),
                rot_speed=random.choice([speed, -speed]),
                turns=turns, thickness=20+p*3, warn_time=40, lifetime=9999))
        elif choice == "cross":
            self.obstacles.append(BossCross(self.canvas, "cross",
                cx=BOSS_X, cy=BOSS_Y,
                thickness=18+p*4,
                rot=random.uniform(0, math.pi/4),
                warn_time=35, lifetime=55))
        elif choice == "shockwave":
            self.obstacles.append(BossShockwave(self.canvas, "shockwave",
                cx=BOSS_X, cy=BOSS_Y,
                count=1+p, gap=55, th=22, warn_time=30, lifetime=120))
        elif choice == "burst":
            self.obstacles.append(BallBurst(self.canvas, "burst",
                cx=BOSS_X, cy=BOSS_Y,
                count=6+p*2 - 2, speed=2.8+p*0.4, radius=12,
                warn_time=25, lifetime=140))
        elif choice == "beams":
            for y in [HEIGHT // 3, HEIGHT * 2 // 3]:
                self.obstacles.append(BeamH(self.canvas, "beam_h",
                    y=y, thickness=22, warn_time=28, lifetime=50))
        elif choice == "homing_burst":
            for _ in range(4):
                side = random.choice(["L","R","T","B"])
                x = -30 if side=="L" else WIDTH+30 if side=="R" else random.randint(0,WIDTH)
                y = -30 if side=="T" else HEIGHT+30 if side=="B" else random.randint(0,HEIGHT)
                self.obstacles.append(Ball(self.canvas, "ball",
                    x=x, y=y, speed=3.0, radius=14, warn_time=22, lifetime=180))
        elif choice == "double_laser":
            speed = 0.04
            for sign in [1, -1]:
                self.obstacles.append(RotatingLaser(self.canvas, "rlaser",
                    cx=BOSS_X, cy=BOSS_Y,
                    start_angle=random.uniform(0, 2*math.pi),
                    rot_speed=sign*speed,
                    turns=1.5, thickness=16, warn_time=38, lifetime=9999))
        elif choice == "zone_sweep":
            for rx in [30, WIDTH//2+30]:
                self.obstacles.append(DangerZone(self.canvas, "zone",
                    rx=rx, ry=50,
                    rw=WIDTH//2-60, rh=HEIGHT-100,
                    warn_time=38, lifetime=55))
        elif choice == "all_beams":
            for y in [HEIGHT*i//5 for i in range(1,5)]:
                self.obstacles.append(BeamH(self.canvas, "beam_h",
                    y=y, thickness=20, warn_time=28, lifetime=50))
            self.obstacles.append(RotatingLaser(self.canvas, "rlaser",
                cx=BOSS_X, cy=BOSS_Y,
                start_angle=0, rot_speed=0.05, turns=2,
                thickness=20, warn_time=35, lifetime=9999))

    def _tick_companions(self):
        dead_this_tick = 0
        for c in self.companions:
            c.update()
            if c.alive:
                attacks = c.get_attacks(self.canvas)
                self.obstacles.extend(attacks)
            else:
                dead_this_tick += 1
                c.delete()
        self.companions = [c for c in self.companions if c.alive]
        if dead_this_tick > 0 and self.boss_phase in self.companion_cd:
            self.companion_cd[self.boss_phase] = COMPANION_COOLDOWN

    def _check_entity_damage(self):
        if self.boss_hit_cd > 0:
            self.boss_hit_cd -= 1

        if (self.boss_alive and self.dashing and not self.in_transition
                and self.boss_hit_cd == 0):
            if math.hypot(self.px-BOSS_X, self.py-BOSS_Y) < BOSS_SIZE + PLAYER_SIZE:
                dmg = 5
                self.boss_hp = max(0, self.boss_hp - dmg)
                self.boss_hits += 1
                self.boss_hit_flash = 12
                self.boss_hit_cd    = DASH_COOLDOWN + DASH_DURATION
                self.damage_numbers.append({
                    "x": BOSS_X + random.randint(-20,20),
                    "y": BOSS_Y - BOSS_SIZE - 10,
                    "age": 0, "val": dmg, "src": "boss"
                })
                dx = self.px - BOSS_X; dy = self.py - BOSS_Y
                mag = math.hypot(dx,dy) or 1
                self.dash_dx = dx/mag; self.dash_dy = dy/mag

        if self.miniboss and self.miniboss.alive:
            hit = self.miniboss.try_damage(self.px, self.py, self.dashing)
            if hit:
                self.damage_numbers.append({
                    "x": self.miniboss.x, "y": self.miniboss.y - 36,
                    "age": 0, "val": 1, "src": "mini"
                })
                dx = self.px - self.miniboss.x; dy = self.py - self.miniboss.y
                mag = math.hypot(dx,dy) or 1
                self.dash_dx = dx/mag; self.dash_dy = dy/mag

        for c in self.companions:
            if c.alive:
                hit = c.try_damage(self.px, self.py, self.dashing)
                if hit:
                    self.damage_numbers.append({
                        "x": c.x, "y": c.y - 32,
                        "age": 0, "val": 1, "src": "comp"
                    })
                    dx = self.px - c.x; dy = self.py - c.y
                    mag = math.hypot(dx,dy) or 1
                    self.dash_dx = dx/mag; self.dash_dy = dy/mag

    def _tick_damage_numbers(self):
        for n in self.damage_numbers: n["age"] += 1
        self.damage_numbers = [n for n in self.damage_numbers if n["age"] < 45]
        if self.boss_hit_flash > 0: self.boss_hit_flash -= 1

    def _start_death_sequence(self):
        self.state = "dying"
        for obs in self.obstacles: obs.delete()
        self.obstacles = []
        self.companions = []
        self.death_frame = 0
        self._run_death_sequence()

    def _run_death_sequence(self):
        if self.state not in ("dying", "split_laser_warn", "split_laser",
                              "final_countdown"):
            return
        self.death_frame += 1
        f = self.death_frame

        self.canvas.delete("all")
        self._draw_boss_bg()

        # ── FASE 1: Boss explota ──────────────────────────────────────
        if self.state == "dying":
            shake = 0
            if f < 40:
                shake = int(6 * math.sin(f * 1.5)) if f > 10 else 0
            bx = BOSS_X + shake
            by = BOSS_Y + random.randint(-shake, shake) if shake > 0 else BOSS_Y

            if f > 10:
                for _ in range(f // 8):
                    a = random.uniform(0, 2*math.pi)
                    d = random.randint(10, min(200, f*4))
                    px_ = BOSS_X + math.cos(a)*d
                    py_ = BOSS_Y + math.sin(a)*d
                    r_ = random.randint(3, 12)
                    col = random.choice([BOSS_COLOR, BOSS_OUTLINE, "#ffffff", DANGER_COLOR])
                    self.canvas.create_oval(px_-r_, py_-r_, px_+r_, py_+r_, fill=col, outline="")

            if f > 45:
                alpha = min(255, int((f-45) * 12))
                c = "#{:02x}{:02x}{:02x}".format(alpha, alpha, alpha)
                self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=c,outline="")

            self._draw_boss_at(bx, by, override_color="#ffffff" if f > 50 else None)
            self._draw_player()
            self._draw_hud()

            if f >= 65:
                self.state = "split_laser_warn"
                self.death_frame = 0
                self.root.after(1000//FPS, self._run_death_sequence)
                return

        # ── FASE 2: Aviso del rayo final (FIX 1: _handle_input activo) ──
        elif self.state == "split_laser_warn":
            # FIX 1: el jugador puede moverse para esquivar
            self._handle_input()
            self.alarm_phase += 0.12

            sep = int(f * 1.5)
            self._draw_boss_half(BOSS_X - sep, BOSS_Y, "left")
            self._draw_boss_half(BOSS_X + sep, BOSS_Y, "right")

            # El ángulo apunta hacia donde estaba el jugador al inicio, luego se congela
            self.death_angle = math.atan2(
                self.py - BOSS_Y, self.px - BOSS_X)
            if (f // 6) % 2 == 0:
                ex = BOSS_X + math.cos(self.death_angle) * max(WIDTH,HEIGHT)
                ey = BOSS_Y + math.sin(self.death_angle) * max(WIDTH,HEIGHT)
                ex2= BOSS_X - math.cos(self.death_angle) * max(WIDTH,HEIGHT)
                ey2= BOSS_Y - math.sin(self.death_angle) * max(WIDTH,HEIGHT)
                self.canvas.create_line(ex2,ey2,ex,ey,
                    fill="#ff4400", width=3)

            self.canvas.create_text(WIDTH//2, 40,
                text="!! ESQUIVA EL RAYO FINAL !!",
                font=("Courier", 16, "bold"), fill="#ff4400")

            self._draw_player()
            self._draw_lives_and_dash()

            if f >= 48:
                # Congelar ángulo justo antes de disparar
                self._frozen_death_angle = self.death_angle
                self.state = "split_laser"
                self.death_frame = 0
                self.root.after(1000//FPS, self._run_death_sequence)
                return

        # ── FASE 3: Rayo activo (FIX 1 + FIX 2) ─────────────────────
        elif self.state == "split_laser":
            # FIX 1: el jugador puede moverse para esquivar
            self._handle_input()
            self.alarm_phase += 0.12

            sep = min(120, int(48 * 1.5))
            self._draw_boss_half(BOSS_X - sep, BOSS_Y, "left")
            self._draw_boss_half(BOSS_X + sep, BOSS_Y, "right")

            # Usar ángulo congelado para que el jugador pueda esquivarlo moviéndose
            angle = getattr(self, "_frozen_death_angle", self.death_angle)
            ex = BOSS_X + math.cos(angle) * max(WIDTH,HEIGHT)
            ey = BOSS_Y + math.sin(angle) * max(WIDTH,HEIGHT)
            ex2= BOSS_X - math.cos(angle) * max(WIDTH,HEIGHT)
            ey2= BOSS_Y - math.sin(angle) * max(WIDTH,HEIGHT)
            self.canvas.create_line(ex2,ey2,ex,ey, fill="#440000", width=40)
            self.canvas.create_line(ex2,ey2,ex,ey, fill=DANGER_COLOR, width=22)
            self.canvas.create_line(ex2,ey2,ex,ey, fill="#ffaaaa", width=6)

            # FIX 2: el rayo verifica colisión en múltiples frames (no solo f==5)
            # y mata aunque el jugador esté en dash (no se puede esquivar con invencibilidad)
            # Solo aplica daño una vez por disparo usando un flag
            if f <= 12 and not getattr(self, "_laser_hit_done", False):
                dx_ = math.cos(angle); dy_ = math.sin(angle)
                vx = self.px - BOSS_X; vy = self.py - BOSS_Y
                perp = abs(vx*dy_ - vy*dx_)
                if perp < 22 + PLAYER_SIZE//2:
                    self._laser_hit_done = True
                    # FIX 2: mata sin importar estado (ni dash ni invencibilidad)
                    self.lives = max(0, self.lives - 1)
                    self.damage_taken += 2
                    self.invincible = INVINCIBLE_FRAMES * 3  # flash largo para indicar el daño
                    if self.lives <= 0:
                        self._game_over()
                        return

            self._draw_player()
            self._draw_lives_and_dash()

            if f >= 90:
                self._laser_hit_done = False  # reset para posibles reuses
                self.state = "final_countdown"
                self.death_frame = 0
                self.final_timer = 20 * FPS
                self.final_hits = 0
                self.zoom = 1.0
                for obs in self.obstacles: obs.delete()
                self.obstacles = []
                self.root.after(1000//FPS, self._run_death_sequence)
                return

        # ── FASE 4: Cuenta atrás 3 golpes (FIX 3: _handle_input activo) ──
        elif self.state == "final_countdown":
            # FIX 3: el jugador puede moverse y hacer dash normalmente
            self._handle_input()
            self.alarm_phase += 0.12
            self.final_timer -= 1

            if self.final_timer <= 0 and self.final_hits < 5:
                self._game_over(); return

            target_zoom = 1.0 + self.final_hits * 0.4
            self.zoom += (target_zoom - self.zoom) * 0.05
            self.zoom_cx += (BOSS_X - self.zoom_cx) * 0.02
            self.zoom_cy += (BOSS_Y - self.zoom_cy) * 0.02

            alarm = abs(math.sin(self.alarm_phase * 0.5))
            alarm_v = int(alarm * 60)
            self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,
                fill="#{:02x}0000".format(alarm_v), outline="")

            self._draw_boss_split_dead()

            if self.death_frame % 90 == 0:
                self.obstacles.append(BallBurst(self.canvas,"burst",
                    cx=BOSS_X, cy=BOSS_Y,
                    count=6, speed=2.5, radius=11,
                    warn_time=25, lifetime=90)) # EDIT -> 100

            self._update_obstacles()
            self._check_collisions()

            # Detectar golpe al boss partido con dash
            if self.dashing:
                for bx_off in [-min(120, int(48*1.5)), min(120, int(48*1.5))]:
                    bxp = BOSS_X + bx_off
                    if math.hypot(self.px-bxp, self.py-BOSS_Y) < 30 + PLAYER_SIZE:
                        if self.boss_hit_cd <= 0:
                            self.final_hits += 1
                            self.boss_hit_flash = 15
                            self.boss_hit_cd = 25
                            self.damage_numbers.append({
                                "x": bxp, "y": BOSS_Y-40,
                                "age": 0, "val": "FINAL!", "src": "final"
                            })
                            dx = self.px-bxp; dy = self.py-BOSS_Y
                            mag = math.hypot(dx,dy) or 1
                            self.dash_dx=dx/mag; self.dash_dy=dy/mag
                            self.dash_frames=8
                            if self.final_hits >= 5:
                                self._victory(); return
            if self.boss_hit_cd > 0: self.boss_hit_cd -= 1

            self._draw_player()
            self._tick_damage_numbers()

            secs = math.ceil(self.final_timer / FPS)
            pulse = int(128 + 127 * math.sin(self.alarm_phase))
            col = "#{:02x}0000".format(min(255, pulse+100))
            self.canvas.create_text(WIDTH//2, 28,
                text=f"GOLPÉALO 5 VECES — {secs}s",
                font=("Courier", 18, "bold"), fill=col)
            self.canvas.create_text(WIDTH//2, 56,
                text=f"GOLPES: {self.final_hits} / 5",
                font=("Courier", 14, "bold"), fill="#ffaa00")
            self._draw_lives_and_dash()
            for n in self.damage_numbers:
                if n["age"] < 45:
                    ratio = 1-n["age"]/45
                    fy = n["y"] - n["age"]*0.6
                    self.canvas.create_text(int(n["x"]), int(fy),
                        text=str(n["val"]) if n["src"]!="final" else "FINAL!",
                        font=("Courier", 12, "bold"),
                        fill=lerp_col("#ffff00","#ff4400",1-ratio))

        self.root.after(1000//FPS, self._run_death_sequence)

    def _render(self):
        self.canvas.delete("all")
        self._draw_boss_bg()
        self._draw_boss_at(BOSS_X, BOSS_Y)
        if self.miniboss: self.miniboss.draw()
        for c in self.companions: c.draw()
        for obs in self.obstacles:
            if obs.active: obs.draw()
        for obs in self.obstacles:
            if not obs.active: obs.draw()
        self._draw_player()
        self._draw_hud()
        self._draw_damage_numbers()
        self._render_admin_overlay()
        if self.in_transition and self.miniboss and self.miniboss.alive:
            pulse = int(180 + 75*math.sin(time.time()*4))
            c = "#{:02x}{:02x}00".format(pulse, pulse//2)
            tl = getattr(self, "_miniboss_time_left", MINIBOSS_TIME)
            tc = "#ff4400" if tl <= 15 else "#ffcc00" if tl <= 35 else c
            self.canvas.create_text(WIDTH//2, 40,
                text=f"!! MINIJEFE — {self.miniboss.hp} HP — {tl}s !!",
                font=("Courier", 13, "bold"), fill=tc)
            self.canvas.create_text(WIDTH//2, 58,
                text="Mátalo a tiempo: +1 vida",
                font=("Courier", 10), fill="#88ff44")

    def _draw_boss_bg(self):
        self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=BG_COLOR,outline="")
        for x in range(0,WIDTH,40): self.canvas.create_line(x,0,x,HEIGHT,fill="#1a0030")
        for y in range(0,HEIGHT,40): self.canvas.create_line(0,y,WIDTH,y,fill="#1a0030")
        if self.boss_alive:
            phase_ratio = 1 - self.boss_hp/BOSS_MAX_HP
            aura_r = int(80 + 30*math.sin(self.boss_pulse) + phase_ratio*40)
            for i in range(3):
                r_ = aura_r - i*15
                if r_ > 0:
                    alpha = int((3-i)*25 * (1+phase_ratio))
                    col = "#{:02x}{:02x}{:02x}".format(
                        min(255,alpha*2), 0, min(255,alpha*4))
                    self.canvas.create_oval(
                        BOSS_X-r_,BOSS_Y-r_,BOSS_X+r_,BOSS_Y+r_,
                        fill=col,outline="")

    def _draw_boss_at(self, bx, by, override_color=None):
        r = BOSS_SIZE
        pulse = math.sin(self.boss_pulse)
        phase_colors = {1:BOSS_COLOR, 2:"#ff4499", 3:"#ff0000"}
        bc = override_color or phase_colors.get(self.boss_phase, BOSS_COLOR)
        self.canvas.create_oval(bx-r-8,by-r-8,bx+r+8,by+r+8,
            fill="",outline="#440055",width=8)
        self.canvas.create_oval(bx-r,by-r,bx+r,by+r,
            fill=bc,outline=BOSS_OUTLINE,width=3)
        if self.boss_hit_flash > 0:
            fi = self.boss_hit_flash/12
            fv = int(fi*255)
            fc = "#{:02x}{:02x}{:02x}".format(fv,fv,fv)
            self.canvas.create_oval(bx-r,by-r,bx+r,by+r,fill=fc,outline="")
        angle_off = self.boss_pulse*0.5
        pts=[]
        for i in range(3):
            a=angle_off+2*math.pi*i/3
            pr=int(r*0.55+pulse*4)
            pts+=[bx+math.cos(a)*pr,by+math.sin(a)*pr]
        self.canvas.create_polygon(pts,fill="",outline="#ffffff",width=2)
        eye_off=int(14+pulse*2)
        for ex_ in [bx-eye_off, bx+eye_off]:
            self.canvas.create_oval(ex_-5,by-8,ex_+5,by+2,fill="#ffffff",outline="")

    def _draw_boss_half(self, bx, by, side):
        r = BOSS_SIZE//2 + 4
        col = "#ff2200"
        self.canvas.create_oval(bx-r,by-r,bx+r,by+r,fill=col,outline="#ff8800",width=2)
        eye_x = bx + (8 if side=="right" else -8)
        self.canvas.create_oval(eye_x-4,by-5,eye_x+4,by+3,fill="#ffffff",outline="")

    def _draw_boss_split_dead(self):
        sep = min(120, int(48*1.5))
        self._draw_boss_half(BOSS_X-sep, BOSS_Y, "left")
        self._draw_boss_half(BOSS_X+sep, BOSS_Y, "right")
        if self.boss_hit_flash > 0:
            for bxp in [BOSS_X-sep, BOSS_X+sep]:
                r=BOSS_SIZE//2+4
                fv=int(self.boss_hit_flash/15*255)
                fc="#{:02x}{:02x}{:02x}".format(fv,fv,fv)
                self.canvas.create_oval(bxp-r,BOSS_Y-r,bxp+r,BOSS_Y+r,fill=fc,outline="")

    def _draw_damage_numbers(self):
        for n in self.damage_numbers:
            ratio=1.0-n["age"]/45
            fy=n["y"]-n["age"]*0.6
            col=lerp_col("#ffff00","#ff4400",1-ratio)
            self.canvas.create_text(int(n["x"]),int(fy),
                text=f"-{n['val']}" if n["src"]!="final" else "FINAL!",
                font=("Courier",int(10+ratio*6),"bold"),fill=col)

    def _draw_hud(self):
        self._draw_lives_and_dash()
        self.canvas.create_text(WIDTH-10,10,text=f"TIEMPO: {self.score}s",
            font=("Courier",13,"bold"),fill=SCORE_COLOR,anchor="ne")
        fase_col={1:BOSS_COLOR,2:"#ff4499",3:"#ff0000"}.get(self.boss_phase,BOSS_COLOR)
        label = "TRANSICIÓN" if self.in_transition else f"FASE {self.boss_phase}"
        self.canvas.create_text(WIDTH-10,30,text=label,
            font=("Courier",12,"bold"),fill=fase_col,anchor="ne")
        bar_x,bar_y,bar_w=WIDTH//2-150,HEIGHT-20,300
        bar_h=12
        self.canvas.create_text(WIDTH//2,bar_y-28,
            text="DASH sobre el boss para dañarlo",
            font=("Courier",8),
            fill=DASH_COLOR if self.dashing else "#335544")
        self.canvas.create_text(WIDTH//2,bar_y-14,text="BOSS HP",
            font=("Courier",9,"bold"),fill=BOSS_COLOR)
        self.canvas.create_rectangle(bar_x,bar_y,bar_x+bar_w,bar_y+bar_h,
            fill=BOSS_HP_BG,outline=BOSS_COLOR,width=1)
        hp_w=int(bar_w*max(0,self.boss_hp/BOSS_MAX_HP))
        if hp_w>0:
            hp_col={1:BOSS_COLOR,2:"#ff4499",3:"#ff0000"}.get(self.boss_phase,BOSS_COLOR)
            self.canvas.create_rectangle(bar_x,bar_y,bar_x+hp_w,bar_y+bar_h,
                fill=hp_col,outline="")
        for i,th in enumerate([66,33]):
            tx=bar_x+int(bar_w*th/100)
            self.canvas.create_line(tx,bar_y,tx,bar_y+bar_h,fill="#ffffff",width=1)

    def _victory(self):
        self.state = "won"
        for obs in self.obstacles: obs.delete()
        self.obstacles = []
        self.companions = []
        total_time = int(time.time() - self.start_time)
        self._go_frame = 0
        self._victory_stats = {
            "time": total_time,
            "damage": self.damage_taken,
            "dashes": self.dashes_used,
            "boss_hits": self.boss_hits,
            "phases": self.phases_cleared,
        }
        self._run_victory_anim()

    def _run_victory_anim(self):
        if self.state != "won": return
        self._go_frame += 1
        f = self._go_frame
        self.canvas.delete("all")
        self._draw_boss_bg()

        if f <= 15:
            a = int(220*(1-f/15))
            c = "#{:02x}{:02x}{:02x}".format(a,a,a)
            self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=c,outline="")

        ty_target = HEIGHT//2 - 130
        if f <= 15: ty = HEIGHT+60
        else:
            prog=min(1.0,(f-15)/20); ease=1-(1-prog)**3
            ty=HEIGHT+60-(HEIGHT+60-ty_target)*ease

        self.canvas.create_text(WIDTH//2+4,ty+4,text="¡BOSS DERROTADO!",
            font=("Courier",38,"bold"),fill="#330066")
        self.canvas.create_text(WIDTH//2,ty,text="¡BOSS DERROTADO!",
            font=("Courier",38,"bold"),fill=BOSS_COLOR)

        if f >= 38:
            lw=min(WIDTH-80,int((f-38)*28))
            if lw>0:
                self.canvas.create_line(WIDTH//2-lw//2,HEIGHT//2-90,
                    WIDTH//2+lw//2,HEIGHT//2-90,fill=BOSS_COLOR,width=2)

        st = self._victory_stats
        stats = [
            (f"TIEMPO TOTAL:         {st['time']}s",             SCORE_COLOR,  48),
            (f"DAÑO RECIBIDO:        {st['damage']} golpes",     DANGER_COLOR, 72),
            (f"DASHES USADOS:        {st['dashes']}",            DASH_COLOR,   96),
            (f"GOLPES AL BOSS:       {st['boss_hits']}",         BOSS_COLOR,  120),
            (f"MINIJEFES DERROTADOS: {st['phases']} / 2",        WARN_COLOR,  144),
            (f"FASES COMPLETADAS:    3 / 3",                     "#00ff88",   168),
        ]
        for txt, col, dy in stats:
            start_f = 50 + (dy - 48)//8
            if f >= start_f:
                alpha = min(1.0, (f-start_f)/14)
                self.canvas.create_text(WIDTH//2, HEIGHT//2-90+dy,
                    text=txt, font=("Courier",12,"bold"),
                    fill=lerp_col("#000000",col,alpha))

        if f >= 40:
            for i in range(8):
                a=2*math.pi*i/8+f*0.025
                sx=WIDTH//2+math.cos(a)*200
                sy=HEIGHT//2+math.sin(a)*100
                pr=int(4+3*math.sin(f*0.12+i))
                self.canvas.create_oval(sx-pr,sy-pr,sx+pr,sy+pr,fill=BOSS_COLOR,outline="")

        if f >= 140:
            pulse=int(180+75*math.sin(time.time()*3))
            bc="#{:02x}{:02x}{:02x}".format(pulse,pulse,pulse)
            self.canvas.create_text(WIDTH//2,HEIGHT//2+105,
                text="[ CLICK PARA VOLVER AL MENU ]",
                font=("Courier",13,"bold"),fill=bc)

        self.root.after(1000//FPS, self._run_victory_anim)

    def _game_over(self):
        super()._game_over()
        self._go_frame = 0
        self._run_go_anim([
            (f"FASE ALCANZADA: {self.boss_phase}", BOSS_COLOR),
            (f"DAÑO RECIBIDO: {self.damage_taken} golpes", DANGER_COLOR),
        ])

    def _render_admin_overlay(self):
        self.admin.draw_if_visible()


# ─────────────────────────────────────────────
# PANEL DE ADMINISTRADOR (EXPANDIDO)
# ─────────────────────────────────────────────
ADMIN_KEY = "minus"

ADMIN_VARS = [
    ("PLAYER_SIZE",      "Tamaño jugador (radio)",
     "Radio en píxeles del jugador",                       6, 40,   1,   "int"),
    ("PLAYER_SPEED",     "Velocidad jugador",
     "Píxeles por frame que se mueve el jugador",          1, 20,   1,   "int"),
    ("DASH_SPEED",       "Velocidad dash",
     "Píxeles/frame durante el dash",                      5, 60,   1,   "int"),
    ("DASH_DURATION",    "Duración dash (frames)",
     "Cuántos frames dura el dash antes de parar",         3, 30,   1,   "int"),
    ("DASH_COOLDOWN",    "Cooldown dash (frames)",
     "Frames hasta poder volver a hacer dash (60=1s)",     10, 180, 5,   "int"),
    ("INVINCIBLE_FRAMES","Frames invencible al golpe",
     "Invencibilidad temporal tras recibir daño",          10, 180, 5,   "int"),
    ("MAX_LIVES",        "Vidas máximas",
     "Vidas máximas que puede tener el jugador",           1, 100,   1,   "int"), 
    ("TRAIL_MAX_AGE",    "Duración del rastro (frames)",
     "Cuántos frames dura el rastro de movimiento",        5, 60,   1,   "int"),
    ("BOSS_MAX_HP",      "HP del boss",
     "Puntos de vida totales del boss",                    20, 300, 5,   "int"),
    ("BOSS_SIZE",        "Tamaño del boss (radio)",
     "Radio en píxeles del cuerpo del boss",               20, 120, 5,   "int"),
    ("MINI_HP",          "HP del minijefe",
     "Golpes necesarios para matar al minijefe",           1, 20,   1,   "int"),
    ("MINIBOSS_TIME",    "Tiempo minijefe (segundos)",
     "Segundos disponibles para matar al minijefe",        10, 180, 5,   "int"),
    ("COMPANION_HP",     "HP del acompañante",
     "Golpes para matar a cada acompañante",               1, 15,   1,   "int"),
    ("COMPANION_COOLDOWN","Cooldown acompañante (frames)",
     "Frames de espera antes de que reaparezca (60=1s)",   60, 3600,60,  "int"),
    ("AVALANCHE_EVERY",  "Cada X seg avalancha (normal)",
     "Segundos entre avalanchas en modo normal",           5, 120,  5,   "int"),
    ("FPS",              "FPS del juego",
     "Fotogramas por segundo (velocidad global)",          10, 120, 5,   "int"),
]

ADMIN_ATTACKS = [
    ("BeamH",        "Rayo horizontal",    "Un rayo que cruza la pantalla horizontalmente"),
    ("BeamV",        "Rayo vertical",      "Un rayo que cruza la pantalla verticalmente"),
    ("CircleWave",   "Onda circular",      "Onda expansiva desde el centro"),
    ("BallBurst",    "Ráfaga de bolas",    "Bolas disparadas en todas direcciones"),
    ("RotatingLaser","Láser rotatorio",    "Láser que gira alrededor del boss"),
    ("BossSpiral",   "Espiral del boss",   "Espiral de proyectiles en fase boss"),
    ("BossShockwave","Onda de choque boss","Anillos concéntricos expansivos"),
    ("BossCross",    "Cruz del boss",      "Rayos en cruz/X que cubren la pantalla"),
    ("DangerZone",   "Zona de peligro",    "Rectángulo de peligro en flancos"),
    ("Ball",         "Bola perseguidora",  "Bola que sigue al jugador"),
]

ADMIN_SPAWNS = [
    ("Miniboss",    "Minijefe",       MINIBOSS_COLOR,   "Aparece un minijefe en posición aleatoria"),
    ("Companion",   "Acompañante",    COMPANION_COLOR,  "Aparece un acompañante cerca del boss"),
    ("Ball_x5",     "x5 Bolas",       DANGER_COLOR,     "5 bolas perseguidoras desde los bordes"),
    ("Avalanche",   "Avalancha NOW",  AVAL_COLOR,       "Lanza la avalancha de inmediato"),
    ("CrossBeams",  "Cruz de rayos",  WARN_COLOR,       "Rayos horizontales y verticales cruzados"),
    ("LaserGrid",   "Cuadrícula láser", "#ff8844",      "Cuadrícula de láseres diagonales"),
]

_SESSION_LOG = []

def _log(msg, col="#aaaaaa"):
    _SESSION_LOG.append({"t": time.time(), "msg": msg, "col": col})
    if len(_SESSION_LOG) > 80:
        _SESSION_LOG.pop(0)


class AdminPanel:
    PW = 620; PH = 520
    PX = (WIDTH  - PW) // 2
    PY = (HEIGHT - PH) // 2

    BG      = "#0a0018"
    BORDER  = "#aa00ff"
    HEADER  = "#cc00ff"
    SEL     = "#2a0044"
    SEL_BD  = "#ff00ff"
    TXT     = "#dddddd"
    DIM     = "#554466"
    VAL_COL = "#00ffcc"
    BTN_ATK = "#ff4400"
    BTN_ATK2= "#ffaa00"
    TAB_ACT = "#cc00ff"
    TAB_IN  = "#220033"
    LIVE_G  = "#00ff88"
    LIVE_R  = "#ff3030"
    LIVE_Y  = "#ffcc00"
    LIVE_B  = "#00ccff"

    TABS = ["📊VARS", "👁ESTADO", "💥ATAQUES", "🧬SPAWN", "🗺MAPA/LOG"]

    def __init__(self, canvas, game_ref):
        self.canvas   = canvas
        self.game     = game_ref
        self.visible  = False
        self.tab      = 0
        self.sel      = 0
        self.scroll   = 0
        self.ids      = []
        self.atk_sel  = set()
        self._msg     = ""
        self._msg_age = 0
        self._frozen_ids = []
        self._map_scroll = 0

        g = globals()
        self._vals = {key: g.get(key, 0) for key, *_ in ADMIN_VARS}

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self._freeze_game()
            self._draw()
        else:
            self._unfreeze_game()
            self._clear()

    def _freeze_game(self):
        self._clear_frozen()
        c = self.canvas
        i1 = c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000022", outline="",
                                  stipple="gray50")
        i2 = c.create_text(WIDTH//2, 14, text="⏸  JUEGO EN PAUSA — PANEL ADMIN ABIERTO",
                           font=("Courier", 9, "bold"), fill="#aa00ff")
        self._frozen_ids = [i1, i2]

    def _unfreeze_game(self):
        self._clear_frozen()

    def _clear_frozen(self):
        for i in self._frozen_ids:
            try: self.canvas.delete(i)
            except: pass
        self._frozen_ids = []

    def _clear(self):
        for i in self.ids:
            try: self.canvas.delete(i)
            except: pass
        self.ids = []

    def draw_if_visible(self):
        if not self.visible: return
        self._freeze_game()
        self._draw()

    def _draw(self):
        self._clear()
        c = self.canvas
        px, py, pw, ph = self.PX, self.PY, self.PW, self.PH

        def add(method, *args, **kw):
            i = getattr(c, method)(*args, **kw)
            self.ids.append(i); return i

        add("create_rectangle", px-4, py-4, px+pw+4, py+ph+4, fill="#000000", outline="")
        add("create_rectangle", px, py, px+pw, py+ph, fill=self.BG, outline=self.BORDER, width=2)
        add("create_rectangle", px, py, px+pw, py+40, fill="#130025", outline="")
        add("create_text", px+pw//2, py+20,
            text="⚙  PANEL DE ADMINISTRADOR  ⚙",
            font=("Courier", 13, "bold"), fill=self.HEADER)
        add("create_text", px+pw-8, py+20, text=f"[{ADMIN_KEY}]",
            font=("Courier", 8), fill=self.DIM, anchor="e")
        add("create_text", px+8, py+20,
            text=f"modo:{self.game.mode if hasattr(self.game,'mode') else '?'}",
            font=("Courier", 8), fill=self.DIM, anchor="w")

        tab_w = (pw - 16) // len(self.TABS)
        for i, t in enumerate(self.TABS):
            tx = px + 8 + i*(tab_w+1)
            is_act = (i == self.tab)
            add("create_rectangle", tx, py+42, tx+tab_w-1, py+60,
                fill=self.TAB_ACT if is_act else self.TAB_IN,
                outline=self.BORDER if is_act else self.DIM)
            add("create_text", tx+tab_w//2, py+51, text=t,
                font=("Courier", 8, "bold"),
                fill="#ffffff" if is_act else self.DIM)

        if self._msg and self._msg_age < 100:
            ratio = min(1.0, (100-self._msg_age)/30)
            col = lerp_col(self.DIM, self.VAL_COL, ratio)
            add("create_text", px+pw//2, py+64,
                text=self._msg, font=("Courier", 8, "bold"), fill=col)
            self._msg_age += 1
        else:
            self._msg = ""

        add("create_line", px+8, py+67, px+pw-8, py+67, fill="#330044")

        if   self.tab == 0: self._draw_vars(px, py, pw, ph)
        elif self.tab == 1: self._draw_live(px, py, pw, ph)
        elif self.tab == 2: self._draw_attacks(px, py, pw, ph)
        elif self.tab == 3: self._draw_spawn(px, py, pw, ph)
        elif self.tab == 4: self._draw_map_log(px, py, pw, ph)

        add("create_line", px+8, py+ph-26, px+pw-8, py+ph-26, fill="#220033")
        hints = {
            0: "↑↓ Navegar  ←→ Cambiar valor  Enter Aplicar  Tab Pestaña",
            1: "Botones de acción rápida  Tab Pestaña",
            2: "Click para lanzar ataque  Tab Pestaña",
            3: "Click para spawnear entidad  Tab Pestaña",
            4: "Minimap + log de eventos  ↑↓ Scroll log  Tab Pestaña",
        }
        add("create_text", px+pw//2, py+ph-13,
            text=hints[self.tab], font=("Courier", 7), fill=self.DIM)

    def _draw_vars(self, px, py, pw, ph):
        c = self.canvas
        def add(m, *a, **k): i=getattr(c,m)(*a,**k); self.ids.append(i); return i

        top = py+72; row_h=40; vis=10
        max_sc = max(0, len(ADMIN_VARS)-vis)
        self.scroll = max(0, min(self.scroll, max_sc))

        for idx in range(vis):
            vi = idx+self.scroll
            if vi >= len(ADMIN_VARS): break
            key, label, desc, vmin, vmax, step, _ = ADMIN_VARS[vi]
            ry = top + idx*row_h
            sel = (vi == self.sel)

            add("create_rectangle", px+8, ry, px+pw-8, ry+row_h-2,
                fill=self.SEL if sel else self.BG,
                outline=self.SEL_BD if sel else "#1a0028")
            add("create_text", px+16, ry+row_h//2, text=f"{vi+1:02d}",
                font=("Courier",7), fill=self.DIM, anchor="w")
            add("create_text", px+40, ry+10, text=label,
                font=("Courier",9,"bold"),
                fill="#ffffff" if sel else self.TXT, anchor="w")
            add("create_text", px+40, ry+24, text=desc,
                font=("Courier",7), fill=self.DIM, anchor="w")

            val = self._vals.get(key, vmin)
            pct = (val-vmin)/max(1,vmax-vmin)
            bx = px+pw-200; by_=ry+16; bw=80
            add("create_rectangle", bx, by_, bx+bw, by_+8, fill="#1a0028", outline="#330044")
            if pct > 0:
                add("create_rectangle", bx, by_, bx+int(bw*pct), by_+8,
                    fill=lerp_col("#0066aa", self.VAL_COL, pct), outline="")
            ac = "#ff00ff" if sel else self.DIM
            add("create_text", px+pw-115, ry+14, text="◀", font=("Courier",11,"bold"), fill=ac)
            add("create_text", px+pw-18,  ry+14, text="▶", font=("Courier",11,"bold"), fill=ac)
            add("create_rectangle", px+pw-110, ry+8, px+pw-25, ry+26,
                fill="#1a0028" if not sel else "#2a0044", outline="#330044")
            add("create_text", px+pw-68, ry+17, text=str(val),
                font=("Courier",10,"bold"), fill=self.VAL_COL)

        if len(ADMIN_VARS) > vis and max_sc > 0:
            sx=px+pw-5; st=top; sb=top+vis*row_h; sh=sb-st
            th=max(18, int(sh*vis/len(ADMIN_VARS)))
            ty=st+int((sh-th)*self.scroll/max_sc)
            add("create_rectangle", sx, st, sx+4, sb, fill="#1a0028", outline="")
            add("create_rectangle", sx, ty, sx+4, ty+th, fill=self.BORDER, outline="")

        by2=py+ph-52
        add("create_rectangle", px+pw//2-110, by2, px+pw//2+110, by2+22,
            fill="#1a002a", outline=self.BORDER)
        add("create_text", px+pw//2, by2+11, text="↵  APLICAR TODOS LOS CAMBIOS AL JUEGO",
            font=("Courier",8,"bold"), fill=self.HEADER)

    def _draw_live(self, px, py, pw, ph):
        c   = self.canvas
        g   = self.game
        def add(m, *a, **k): i=getattr(c,m)(*a,**k); self.ids.append(i); return i

        top = py+72; col_w=(pw-24)//2

        def stat_row(lx, ly, label, val_str, col, bar_pct=None, bar_col=None, editable=False):
            add("create_rectangle", lx, ly, lx+col_w, ly+34, fill="#0f0020", outline="#220033")
            lbl_s = ("✏ " if editable else "  ") + label
            add("create_text", lx+8, ly+8, text=lbl_s,
                font=("Courier",8), fill=self.DIM if not editable else "#aaaaff", anchor="w")
            add("create_text", lx+col_w-8, ly+8, text=val_str,
                font=("Courier",9,"bold"), fill=col, anchor="e")
            if bar_pct is not None:
                bx2=lx+8; bw2=col_w-16; bhy=ly+22
                add("create_rectangle", bx2, bhy, bx2+bw2, bhy+5, fill="#1a0028", outline="")
                if bar_pct > 0:
                    add("create_rectangle", bx2, bhy,
                        bx2+int(bw2*min(1,bar_pct)), bhy+5, fill=bar_col or col, outline="")

        lx0 = px+8; lx1 = px+16+col_w
        ly  = top

        add("create_text", lx0+col_w//2, ly-2, text="── JUGADOR ──",
            font=("Courier",9,"bold"), fill=self.LIVE_B)
        ly += 14

        lives_pct = g.lives/MAX_LIVES if hasattr(g,"lives") else 0
        lives_col = self.LIVE_G if lives_pct>0.5 else self.LIVE_Y if lives_pct>0.25 else self.LIVE_R
        stat_row(lx0, ly, "Vidas", f"{g.lives if hasattr(g,'lives') else '?'} / {MAX_LIVES}",
                 lives_col, lives_pct, lives_col, editable=True)
        ly += 38

        invic = getattr(g,"invincible",0)
        stat_row(lx0, ly, "Invencibilidad", f"{invic}f" if invic>0 else "—",
                 self.LIVE_Y if invic>0 else self.DIM, invic/max(1,INVINCIBLE_FRAMES), self.LIVE_Y)
        ly += 38

        dash_cd = getattr(g,"dash_cooldown",0)
        dashing = getattr(g,"dashing",False)
        stat_row(lx0, ly, "Dash",
                 "★ACTIVO" if dashing else (f"CD:{dash_cd}" if dash_cd>0 else "LISTO"),
                 self.VAL_COL if dashing else (self.LIVE_Y if dash_cd>0 else self.LIVE_G),
                 1.0-dash_cd/max(1,DASH_COOLDOWN), self.VAL_COL)
        ly += 38

        stat_row(lx0, ly, "Pos jugador",
                 f"({int(getattr(g,'px',0))},{int(getattr(g,'py',0))})", self.DIM)
        ly += 38

        stat_row(lx0, ly, "Obstáculos", str(len(getattr(g,"obstacles",[]))),
                 self.LIVE_Y if len(getattr(g,"obstacles",[]))>8 else self.LIVE_G)
        ly += 38

        elapsed = int(time.time() - getattr(g,"start_time",time.time()))
        stat_row(lx0, ly, "Tiempo partida", f"{elapsed//60:02d}:{elapsed%60:02d}", self.LIVE_B)
        ly += 38

        diff = getattr(g,"difficulty",1.0)
        stat_row(lx0, ly, "Dificultad", f"{diff:.2f}x", self.LIVE_Y, (diff-1)/4, self.LIVE_R)

        add("create_text", lx1+col_w//2, top-2, text="── BOSS / MODO ──",
            font=("Courier",9,"bold"), fill=self.HEADER)
        ry2 = top+14

        if hasattr(g,"boss_hp"):
            bhp_pct = g.boss_hp/max(1,BOSS_MAX_HP)
            bhp_col = self.LIVE_G if bhp_pct>0.66 else self.LIVE_Y if bhp_pct>0.33 else self.LIVE_R
            stat_row(lx1, ry2, "Boss HP", f"{g.boss_hp} / {BOSS_MAX_HP}",
                     bhp_col, bhp_pct, bhp_col, editable=True)
            ry2 += 38

            phase_col = {1:self.LIVE_G, 2:self.LIVE_Y, 3:self.LIVE_R}.get(g.boss_phase, self.DIM)
            stat_row(lx1, ry2, "Fase boss", f"FASE {g.boss_phase} / 3", phase_col)
            ry2 += 38

            stat_row(lx1, ry2, "Golpes al boss", str(getattr(g,"boss_hits",0)), self.LIVE_B)
            ry2 += 38

            stat_row(lx1, ry2, "Daño recibido", str(getattr(g,"damage_taken",0)),
                     self.LIVE_R if getattr(g,"damage_taken",0)>3 else self.LIVE_Y)
            ry2 += 38

            stat_row(lx1, ry2, "Acompañantes", str(len(getattr(g,"companions",[]))),
                     self.LIVE_Y if getattr(g,"companions",[]) else self.DIM)
            ry2 += 38

            in_tr = getattr(g,"in_transition",False)
            mini  = getattr(g,"miniboss",None)
            if in_tr and mini:
                stat_row(lx1, ry2, "Minijefe HP", f"{mini.hp} / {MINI_HP}",
                         self.LIVE_R, mini.hp/max(1,MINI_HP), self.LIVE_R)
            else:
                stat_row(lx1, ry2, "Transición", "ACTIVA" if in_tr else "No",
                         self.LIVE_Y if in_tr else self.DIM)
            ry2 += 38

            stat_row(lx1, ry2, "Dashes usados", str(getattr(g,"dashes_used",0)), self.LIVE_B)
        else:
            stat_row(lx1, ry2, "Score", str(getattr(g,"score",0)), self.LIVE_B)
            ry2 += 38
            aval_t = getattr(g,"avalanche_timer",0)
            next_a = getattr(g,"next_avalanche",AVALANCHE_EVERY*FPS)
            frames_left = max(0, next_a - aval_t)
            secs_left = math.ceil(frames_left / FPS)
            stat_row(lx1, ry2, "Próx. avalancha", f"{secs_left}s",
                     self.LIVE_R if secs_left<=5 else self.LIVE_Y,
                     1.0 - frames_left/max(1,next_a), self.LIVE_R)
            ry2 += 38
            stat_row(lx1, ry2, "Nivel actual", f"{int(diff)} ({diff:.2f}x)",
                     self.LIVE_Y, (diff-1)/4, self.LIVE_R)

        btn_y = py+ph-74
        add("create_text", px+pw//2, btn_y-10, text="─── ACCIONES RÁPIDAS ───",
            font=("Courier",8,"bold"), fill=self.DIM)

        actions_row1 = [
            ("+1 Vida",      "#00aa44", "give_life"),
            ("-1 Vida",      "#aa0000", "take_life"),
            ("God Mode",     "#ffcc00", "god_mode"),
            ("Normalizar",   "#0055aa", "normalize"),
            ("Full Vidas",   "#00ff88", "full_lives"),
        ]
        actions_row2 = [
            ("Boss -10 HP",  "#aa00ff", "boss_dmg"),
            ("Boss +10 HP",  "#005544", "boss_heal"),
            ("Boss -50 HP",  "#ff00ff", "boss_dmg50"),
            ("Matar obs",    "#ff4400", "kill_obs"),
            ("Teleport cen.","#00ccff", "teleport_center"),
        ]
        bw3 = (pw-16) // 5
        for row_idx, actions in enumerate([actions_row1, actions_row2]):
            for i,(lbl,col3,act) in enumerate(actions):
                bx3 = px+8+i*bw3
                by3 = btn_y + row_idx*26
                add("create_rectangle", bx3, by3, bx3+bw3-2, by3+22, fill="#0f0020", outline=col3)
                add("create_text", bx3+bw3//2, by3+11, text=lbl, font=("Courier",6,"bold"), fill=col3)

        self._live_actions_r1 = actions_row1
        self._live_actions_r2 = actions_row2
        self._live_btn_y = btn_y
        self._live_bw = bw3

    def _draw_attacks(self, px, py, pw, ph):
        c = self.canvas
        def add(m,*a,**k): i=getattr(c,m)(*a,**k); self.ids.append(i); return i

        top=py+72; cols=2; col_w=(pw-24)//2; row_h=46

        for idx,(atk_cls,lbl,desc) in enumerate(ADMIN_ATTACKS):
            col=idx%cols; row=idx//cols
            bx=px+8+col*(col_w+8); by=top+row*row_h
            sel=atk_cls in self.atk_sel
            add("create_rectangle", bx, by, bx+col_w, by+row_h-4,
                fill="#200015" if sel else "#100018",
                outline=self.BTN_ATK if sel else "#440044", width=2 if sel else 1)
            icon = {"BeamH":"═","BeamV":"║","CircleWave":"◎","BallBurst":"✦",
                    "RotatingLaser":"↺","BossSpiral":"🌀","BossShockwave":"◉",
                    "BossCross":"✚","DangerZone":"▭","Ball":"●"}.get(atk_cls,"?")
            add("create_text", bx+14, by+row_h//2, text=icon, font=("Courier",14),
                fill=self.BTN_ATK if sel else self.BTN_ATK2)
            add("create_text", bx+32, by+12, text=lbl, font=("Courier",9,"bold"),
                fill=self.BTN_ATK if sel else self.BTN_ATK2, anchor="w")
            add("create_text", bx+32, by+26, text=desc, font=("Courier",7), fill=self.DIM, anchor="w")
            if sel:
                add("create_text", bx+col_w-6, by+row_h//2, text="✓",
                    font=("Courier",12,"bold"), fill=self.BTN_ATK, anchor="e")

        btn_y = top + (len(ADMIN_ATTACKS)//cols + 1)*row_h
        add("create_text", px+pw//2, btn_y+2,
            text="Click = lanzar    Selección múltiple no disponible en esta versión",
            font=("Courier",7), fill=self.DIM)

    def _draw_spawn(self, px, py, pw, ph):
        c = self.canvas
        g = self.game
        def add(m,*a,**k): i=getattr(c,m)(*a,**k); self.ids.append(i); return i

        top = py+72; cols=2; col_w=(pw-24)//2; row_h=52

        add("create_text", px+pw//2, top-4,
            text="── Entidades y eventos especiales ──",
            font=("Courier",9,"bold"), fill=self.HEADER)

        for idx,(spawn_id, lbl, col3, desc) in enumerate(ADMIN_SPAWNS):
            sc = idx%cols; row = idx//cols
            bx = px+8+sc*(col_w+8); by = top+14+row*row_h
            add("create_rectangle", bx, by, bx+col_w, by+row_h-4, fill="#100020", outline=col3, width=1)
            add("create_text", bx+8, by+14, text=lbl, font=("Courier",10,"bold"), fill=col3, anchor="w")
            add("create_text", bx+8, by+30, text=desc, font=("Courier",7), fill=self.DIM, anchor="w")

        fy = top + 14 + (len(ADMIN_SPAWNS)//cols + 1)*row_h + 4
        if hasattr(g,"boss_phase"):
            add("create_text", px+pw//2, fy, text="─── FASE DEL BOSS ───",
                font=("Courier",9,"bold"), fill=self.DIM)
            fby = fy+18
            for fi, (flbl, fcol) in enumerate([
                ("FASE 1 (66%HP)", BOSS_COLOR),
                ("FASE 2 (33%HP)", "#ff4499"),
                ("FASE 3 (1%HP)",  "#ff0000"),
            ]):
                fbx = px+8+fi*(pw//3-4)
                add("create_rectangle", fbx, fby, fbx+pw//3-8, fby+22, fill="#120018", outline=fcol)
                add("create_text", fbx+(pw//3-8)//2, fby+11, text=flbl,
                    font=("Courier",7,"bold"), fill=fcol)

        sy = fy + (50 if hasattr(g,"boss_phase") else 0) + 8
        add("create_text", px+pw//2, sy, text="─── VELOCIDAD DEL JUEGO ───",
            font=("Courier",9,"bold"), fill=self.DIM)
        speed_btns = [
            ("0.25x SLOW",  "#6688ff", "speed_025"),
            ("0.5x",        "#88aaff", "speed_050"),
            ("NORMAL 1x",   "#aaaaaa", "speed_100"),
            ("1.5x TURBO",  "#ffaa44", "speed_150"),
            ("2x RAPIDO",   "#ff6600", "speed_200"),
        ]
        sbw = (pw-16)//len(speed_btns)
        for i,(slbl,scol,sact) in enumerate(speed_btns):
            sbx = px+8+i*sbw; sby = sy+14
            add("create_rectangle", sbx, sby, sbx+sbw-2, sby+22, fill="#0a0018", outline=scol)
            add("create_text", sbx+sbw//2, sby+11, text=slbl, font=("Courier",6,"bold"), fill=scol)

        self._spawn_btn_top = top+14
        self._spawn_row_h = row_h
        self._spawn_cols = cols
        self._spawn_col_w = col_w
        self._spawn_phase_fy = fy
        self._spawn_phase_fby = fy+18 if hasattr(g,"boss_phase") else None
        self._spawn_speed_btns = speed_btns
        self._spawn_speed_y = sy+14
        self._spawn_speed_bw = sbw

    def _draw_map_log(self, px, py, pw, ph):
        c = self.canvas
        g = self.game
        def add(m,*a,**k): i=getattr(c,m)(*a,**k); self.ids.append(i); return i

        top = py+72
        MAP_W = 240; MAP_H = 180
        mx = px+12; my = top+14
        add("create_rectangle", mx-2, my-16, mx+MAP_W+2, my+MAP_H+2, fill="#000000", outline=self.BORDER)
        add("create_text", mx+MAP_W//2, my-8, text="MINIMAP", font=("Courier",8,"bold"), fill=self.BORDER)
        add("create_rectangle", mx, my, mx+MAP_W, my+MAP_H, fill="#0a000f", outline="")

        for gx in range(0, MAP_W, MAP_W//8):
            add("create_line", mx+gx, my, mx+gx, my+MAP_H, fill="#160020")
        for gy in range(0, MAP_H, MAP_H//6):
            add("create_line", mx, my+gy, mx+MAP_W, my+gy, fill="#160020")

        def map_x(wx): return mx + int(wx * MAP_W / WIDTH)
        def map_y(wy): return my + int(wy * MAP_H / HEIGHT)

        for obs in getattr(g,"obstacles",[]):
            try:
                if hasattr(obs,"x") and hasattr(obs,"y"):
                    ox,oy = map_x(obs.x), map_y(obs.y)
                    col = "#ff4444" if obs.active else "#884444"
                    add("create_oval", ox-3,oy-3,ox+3,oy+3, fill=col, outline="")
                elif hasattr(obs,"y") and hasattr(obs,"th") and obs.otype=="beam_h":
                    omy = map_y(obs.y)
                    col = DANGER_COLOR if obs.active else WARN_COLOR
                    add("create_line", mx, omy, mx+MAP_W, omy, fill=col, width=2)
                elif hasattr(obs,"x") and hasattr(obs,"th") and obs.otype=="beam_v":
                    omx = map_x(obs.x)
                    col = DANGER_COLOR if obs.active else WARN_COLOR
                    add("create_line", omx, my, omx, my+MAP_H, fill=col, width=2)
                elif hasattr(obs,"cx") and hasattr(obs,"cy"):
                    ox,oy = map_x(obs.cx), map_y(obs.cy)
                    add("create_oval", ox-2,oy-2,ox+2,oy+2, fill="#ff00ff", outline="")
                elif hasattr(obs,"rx") and hasattr(obs,"ry"):
                    rx1,ry1 = map_x(obs.rx), map_y(obs.ry)
                    rx2,ry2 = map_x(obs.rx+obs.rw), map_y(obs.ry+obs.rh)
                    col = DANGER_COLOR if obs.active else WARN_COLOR
                    add("create_rectangle", rx1,ry1,rx2,ry2, fill="",outline=col)
            except Exception:
                pass

        if hasattr(g,"boss_hp"):
            bx_m,by_m = map_x(BOSS_X), map_y(BOSS_Y)
            add("create_oval", bx_m-6,by_m-6,bx_m+6,by_m+6, fill=BOSS_COLOR, outline=BOSS_OUTLINE, width=1)

        if hasattr(g,"miniboss") and g.miniboss and g.miniboss.alive:
            mmx,mmy = map_x(g.miniboss.x), map_y(g.miniboss.y)
            add("create_oval", mmx-4,mmy-4,mmx+4,mmy+4, fill=MINIBOSS_COLOR, outline="")

        for comp in getattr(g,"companions",[]):
            cmx,cmy = map_x(comp.x), map_y(comp.y)
            add("create_oval", cmx-3,cmy-3,cmx+3,cmy+3, fill=COMPANION_COLOR, outline="")

        ppx,ppy = map_x(getattr(g,"px",WIDTH//2)), map_y(getattr(g,"py",HEIGHT//2))
        add("create_oval", ppx-5,ppy-5,ppx+5,ppy+5, fill=PLAYER_COLOR, outline=PLAYER_OUTLINE, width=1)
        add("create_line", ppx-7,ppy,ppx+7,ppy, fill=PLAYER_COLOR, width=1)
        add("create_line", ppx,ppy-7,ppx,ppy+7, fill=PLAYER_COLOR, width=1)

        ley_y = my+MAP_H+6
        legend = [(PLAYER_COLOR,"Jugador"),(BOSS_COLOR,"Boss"),(DANGER_COLOR,"Obstáculo"),(MINIBOSS_COLOR,"Minijefe")]
        for li,(lc,lt) in enumerate(legend):
            lbx = mx + li*(MAP_W//4)
            add("create_oval", lbx, ley_y, lbx+7, ley_y+7, fill=lc, outline="")
            add("create_text", lbx+10, ley_y+3, text=lt, font=("Courier",6), fill=self.DIM, anchor="w")

        sy = my + MAP_H + 24; stats_w = MAP_W
        add("create_text", mx+stats_w//2, sy, text="ESTADÍSTICAS DE SESIÓN",
            font=("Courier",8,"bold"), fill=self.LIVE_B)
        sy += 14
        add("create_rectangle", mx, sy, mx+stats_w, sy+70, fill="#0a000f", outline="#220033")
        sess_stats = [
            ("Obstáculos activos", str(len(getattr(g,"obstacles",[]))), self.LIVE_Y),
            ("Score/Tiempo",       f"{getattr(g,'score',0)}s", self.LIVE_B),
            ("Dificultad actual",  f"{getattr(g,'difficulty',1.0):.2f}x", self.LIVE_Y),
            ("Frames totales",     str(getattr(g,"frame",0)), self.DIM),
        ]
        for si,(slbl,sval,scol) in enumerate(sess_stats):
            add("create_text", mx+4, sy+4+si*16, text=slbl, font=("Courier",7), fill=self.DIM, anchor="w")
            add("create_text", mx+stats_w-4, sy+4+si*16, text=sval, font=("Courier",7,"bold"), fill=scol, anchor="e")

        lx = px+12+MAP_W+14; lw = pw - MAP_W - 38
        add("create_rectangle", lx-2, my-16, lx+lw+2, my+MAP_H+2, fill="#000000", outline=self.BORDER)
        add("create_text", lx+lw//2, my-8, text="LOG DE EVENTOS", font=("Courier",8,"bold"), fill=self.BORDER)
        add("create_rectangle", lx, my, lx+lw, my+MAP_H, fill="#050010", outline="")

        filter_y = my+MAP_H+4
        add("create_text", lx+lw//2, filter_y+6, text="↑↓ para scrollear el log", font=("Courier",7), fill=self.DIM)

        vis_lines = 14
        log_entries = _SESSION_LOG
        max_scroll = max(0, len(log_entries) - vis_lines)
        self._map_scroll = max(0, min(self._map_scroll, max_scroll))
        start_idx = max(0, len(log_entries) - vis_lines - self._map_scroll)
        end_idx   = min(len(log_entries), start_idx + vis_lines)

        for li, entry in enumerate(log_entries[start_idx:end_idx]):
            ely = my + 4 + li*12
            elapsed = int(time.time() - entry["t"])
            ts = f"+{elapsed:3d}s" if elapsed < 3600 else "long"
            add("create_text", lx+4, ely, text=ts, font=("Courier",6), fill="#554466", anchor="w")
            add("create_text", lx+38, ely, text=entry["msg"][:30],
                font=("Courier",7,"bold"), fill=entry["col"], anchor="w")

        if not log_entries:
            add("create_text", lx+lw//2, my+MAP_H//2, text="Sin eventos registrados",
                font=("Courier",8), fill=self.DIM)

        if len(log_entries) > vis_lines:
            sbx = lx+lw-4; sbt = my; sbb = my+MAP_H; sbh = sbb-sbt
            th2 = max(14, int(sbh*vis_lines/len(log_entries)))
            ty2 = sbt+int((sbh-th2)*(max_scroll-self._map_scroll)/max(1,max_scroll))
            add("create_rectangle", sbx, sbt, sbx+4, sbb, fill="#110022", outline="")
            add("create_rectangle", sbx, ty2, sbx+4, ty2+th2, fill=self.BORDER, outline="")

        clr_y = my+MAP_H+4
        add("create_rectangle", lx+lw-68, clr_y, lx+lw, clr_y+16, fill="#200010", outline="#882222")
        add("create_text", lx+lw-34, clr_y+8, text="Limpiar log", font=("Courier",6), fill="#aa4444")
        self._log_clear_rect = (lx+lw-68, clr_y, lx+lw, clr_y+16)

    def handle_key(self, keysym):
        if not self.visible: return
        if keysym == "Tab":
            self.tab = (self.tab+1) % len(self.TABS)
        elif self.tab == 0:
            if   keysym in ("Up","w"):   self._nav(-1)
            elif keysym in ("Down","s"): self._nav(+1)
            elif keysym in ("Left","a"): self._change_val(-1)
            elif keysym in ("Right","d"):self._change_val(+1)
            elif keysym == "Return":     self._apply_all()
        elif self.tab == 4:
            if   keysym in ("Up","w"):   self._map_scroll = max(0, self._map_scroll+1)
            elif keysym in ("Down","s"): self._map_scroll = max(0, self._map_scroll-1)
        self._draw()

    def _nav(self, d):
        self.sel = max(0, min(len(ADMIN_VARS)-1, self.sel+d))
        if self.sel < self.scroll:         self.scroll -= 1
        if self.sel >= self.scroll+10:     self.scroll += 1

    def handle_click(self, x, y):
        if not self.visible: return
        px, py, pw, ph = self.PX, self.PY, self.PW, self.PH

        tab_w = (pw-16)//len(self.TABS)
        for i in range(len(self.TABS)):
            tx = px+8+i*(tab_w+1)
            if tx<=x<=tx+tab_w-1 and py+42<=y<=py+60:
                self.tab=i; self._draw(); return

        if self.tab==0:
            top=py+72; row_h=40; vis=10
            for idx in range(vis):
                vi=idx+self.scroll
                if vi>=len(ADMIN_VARS): break
                ry=top+idx*row_h
                if px+8<=x<=px+pw-8 and ry<=y<=ry+row_h-2:
                    self.sel=vi
                    if px+pw-120<=x<=px+pw-100: self._change_val(-1)
                    elif px+pw-24<=x<=px+pw-8:  self._change_val(+1)
                    self._draw(); return
            by2=py+ph-52
            if px+pw//2-110<=x<=px+pw//2+110 and by2<=y<=by2+22:
                self._apply_all(); self._draw(); return

        elif self.tab==1:
            if hasattr(self,"_live_btn_y"):
                bw3=self._live_bw; btn_y=self._live_btn_y
                for row_idx, actions in enumerate([self._live_actions_r1, self._live_actions_r2]):
                    for i,(_,_,act) in enumerate(actions):
                        bx3=self.PX+8+i*bw3
                        by3=btn_y+row_idx*26
                        if bx3<=x<=bx3+bw3-2 and by3<=y<=by3+22:
                            self._do_live_action(act); self._draw(); return

        elif self.tab==2:
            top=py+72; cols=2; col_w=(pw-24)//2; row_h=46
            for idx,(atk_cls,*_) in enumerate(ADMIN_ATTACKS):
                col=idx%cols; row=idx//cols
                bx=px+8+col*(col_w+8); by=top+row*row_h
                if bx<=x<=bx+col_w and by<=y<=by+row_h-4:
                    self.atk_sel={atk_cls}
                    self._launch_selected()
                    self._draw(); return

        elif self.tab==3:
            top=self._spawn_btn_top; row_h=self._spawn_row_h
            cols=self._spawn_cols; col_w=self._spawn_col_w
            for idx,(spawn_id,*_) in enumerate(ADMIN_SPAWNS):
                sc=idx%cols; row=idx//cols
                bx=px+8+sc*(col_w+8); by=top+row*row_h
                if bx<=x<=bx+col_w and by<=y<=by+row_h-4:
                    self._do_spawn(spawn_id); self._draw(); return
            if hasattr(self.game,"boss_phase") and self._spawn_phase_fby:
                fby = self._spawn_phase_fby
                for fi,(phase_val,fhp) in enumerate([(67,1),(34,2),(1,3)]):
                    fbx = px+8+fi*(pw//3-4)
                    if fbx<=x<=fbx+pw//3-8 and fby<=y<=fby+22:
                        self._force_boss_phase(phase_val); self._draw(); return
            if hasattr(self,"_spawn_speed_btns"):
                for i,(_,_,sact) in enumerate(self._spawn_speed_btns):
                    sbx = px+8+i*self._spawn_speed_bw; sby = self._spawn_speed_y
                    if sbx<=x<=sbx+self._spawn_speed_bw-2 and sby<=y<=sby+22:
                        self._do_speed(sact); self._draw(); return

        elif self.tab==4:
            if hasattr(self,"_log_clear_rect"):
                lx1,ly1,lx2,ly2 = self._log_clear_rect
                if lx1<=x<=lx2 and ly1<=y<=ly2:
                    _SESSION_LOG.clear()
                    self._msg="🗑 Log limpiado"; self._msg_age=0
                    self._draw(); return

    def _do_live_action(self, act):
        g = self.game
        if act=="give_life":
            g.lives = min(MAX_LIVES, g.lives+1)
            self._msg=f"❤ +1 vida → {g.lives}/{MAX_LIVES}"
            _log(f"+1 vida → {g.lives}/{MAX_LIVES}", self.LIVE_G)
        elif act=="take_life":
            g.lives = max(0, g.lives-1)
            self._msg=f"💔 -1 vida → {g.lives}/{MAX_LIVES}"
            _log(f"-1 vida → {g.lives}/{MAX_LIVES}", self.LIVE_R)
        elif act=="god_mode":
            g.invincible=9999
            self._msg="✨ God mode (9999 frames)"
            _log("God mode activado", "#ffcc00")
        elif act=="normalize":
            g.invincible=0; g.dashing=False; g.dash_cooldown=0
            self._msg="🔄 Estado normalizado"
            _log("Estado normalizado", self.LIVE_B)
        elif act=="full_lives":
            g.lives=MAX_LIVES
            self._msg=f"❤❤❤ Full vidas ({MAX_LIVES})"
            _log(f"Full vidas: {MAX_LIVES}", self.LIVE_G)
        elif act=="boss_dmg":
            if hasattr(g,"boss_hp"):
                g.boss_hp=max(0,g.boss_hp-10)
                self._msg=f"⚔ Boss -10 HP → {g.boss_hp}"
                _log(f"Boss -10HP → {g.boss_hp}", BOSS_COLOR)
            else: self._msg="No hay boss activo"
        elif act=="boss_dmg50":
            if hasattr(g,"boss_hp"):
                g.boss_hp=max(0,g.boss_hp-50)
                self._msg=f"💥 Boss -50 HP → {g.boss_hp}"
                _log(f"Boss -50HP → {g.boss_hp}", "#ff00ff")
            else: self._msg="No hay boss activo"
        elif act=="boss_heal":
            if hasattr(g,"boss_hp"):
                g.boss_hp=min(BOSS_MAX_HP,g.boss_hp+10)
                self._msg=f"💊 Boss +10 HP → {g.boss_hp}"
                _log(f"Boss +10HP → {g.boss_hp}", self.LIVE_G)
            else: self._msg="No hay boss activo"
        elif act=="kill_obs":
            n=len(g.obstacles)
            for o in g.obstacles: o.delete()
            g.obstacles=[]
            self._msg=f"🗑 {n} obstáculos eliminados"
            _log(f"Eliminados {n} obstáculos", AVAL_COLOR)
        elif act=="teleport_center":
            g.px = float(WIDTH//2); g.py = float(HEIGHT//2); g.trail = []
            self._msg="🎯 Teletransportado al centro"
            _log("Teletransport → centro", DASH_COLOR)
        self._msg_age=0

    def _do_spawn(self, spawn_id):
        g = self.game; canvas = g.canvas
        if spawn_id == "Miniboss":
            if not hasattr(g,"miniboss"):
                self._msg = "Solo disponible en Boss Fight"; return
            mx = BOSS_X + random.choice([-220,220]); my = BOSS_Y + random.choice([-100,100])
            if g.miniboss is None:
                g.miniboss = Miniboss(canvas, mx, my, difficulty=g.difficulty)
                _log("Minijefe spawneado", MINIBOSS_COLOR); self._msg = "🎯 Minijefe spawnado"
            else: self._msg = "Ya hay un minijefe activo"
        elif spawn_id == "Companion":
            if not hasattr(g,"companions"):
                self._msg = "Solo disponible en Boss Fight"; return
            ox,oy = random.choice([(-180,-80),(180,-80),(-180,80),(180,80)])
            c = Companion(canvas, BOSS_X+ox, BOSS_Y+oy, difficulty=max(1,g.boss_phase if hasattr(g,"boss_phase") else 1))
            g.companions.append(c)
            _log("Acompañante spawneado", COMPANION_COLOR); self._msg = "👾 Acompañante spawneado"
        elif spawn_id == "Ball_x5":
            for _ in range(5):
                side = random.choice(["L","R","T","B"])
                x = -30 if side=="L" else WIDTH+30 if side=="R" else random.randint(0,WIDTH)
                y = -30 if side=="T" else HEIGHT+30 if side=="B" else random.randint(0,HEIGHT)
                g.obstacles.append(Ball(canvas,"ball",x=x,y=y,
                    speed=2.5+g.difficulty*0.5,radius=16,warn_time=18,lifetime=200))
            _log("x5 bolas spawneadas", DANGER_COLOR); self._msg = "🎱 x5 bolas spawneadas"
        elif spawn_id == "Avalanche":
            if hasattr(g,"_launch_avalanche"):
                g._launch_avalanche(); _log("Avalancha forzada", AVAL_COLOR); self._msg = "🌊 Avalancha lanzada"
            else: self._msg = "No disponible en este modo"
        elif spawn_id == "CrossBeams":
            for y in [HEIGHT//4, HEIGHT//2, 3*HEIGHT//4]:
                g.obstacles.append(BeamH(canvas,"beam_h",y=y,thickness=24,warn_time=28,lifetime=55))
            for x in [WIDTH//4, WIDTH//2, 3*WIDTH//4]:
                g.obstacles.append(BeamV(canvas,"beam_v",x=x,thickness=24,warn_time=28,lifetime=55))
            _log("Cruz de rayos lanzada", WARN_COLOR); self._msg = "✚ Cruz de rayos activa"
        elif spawn_id == "LaserGrid":
            for slope, offset_frac in [(1,0),(1,0.4),(-1,0),(-1,0.4)]:
                off = int(HEIGHT*offset_frac) + random.randint(-30,30)
                g.obstacles.append(LaserDiag(canvas,"laser",slope=slope,offset=off,
                    thickness=22,warn_time=30,lifetime=60))
            _log("Cuadrícula láser activa", "#ff8844"); self._msg = "⚡ Cuadrícula láser"
        self._msg_age=0

    def _force_boss_phase(self, hp_pct):
        g = self.game
        if not hasattr(g,"boss_hp"): return
        new_hp = max(1, int(BOSS_MAX_HP * hp_pct / 100))
        g.boss_hp = new_hp
        new_phase = 1 if new_hp > BOSS_MAX_HP*0.66 else 2 if new_hp > BOSS_MAX_HP*0.33 else 3
        g.boss_phase = new_phase; g.in_transition = False
        _log(f"Fase forzada → {new_phase} (HP:{new_hp})", BOSS_COLOR)
        self._msg = f"⚡ Fase {new_phase} forzada (HP:{new_hp})"; self._msg_age = 0

    def _do_speed(self, sact):
        global FPS
        speeds = {"speed_025":15, "speed_050":30, "speed_100":60, "speed_150":90, "speed_200":120}
        if sact in speeds:
            FPS = speeds[sact]
            _log(f"FPS cambiado → {FPS}", "#ffaa44"); self._msg = f"⏱ FPS → {FPS}"; self._msg_age = 0

    def _change_val(self, d):
        if self.sel>=len(ADMIN_VARS): return
        key,_,_,vmin,vmax,step,_ = ADMIN_VARS[self.sel]
        val=max(vmin,min(vmax,self._vals.get(key,vmin)+d*step))
        self._vals[key]=val; globals()[key]=val
        _log(f"{key} → {val}", self.VAL_COL)
        self._msg=f"✓ {key} = {val}"; self._msg_age=0

    def _apply_all(self):
        g2=globals()
        for k,v in self._vals.items():
            if k in g2: g2[k]=v
        _log("Todas las variables aplicadas", self.HEADER)
        self._msg="✓ Todos los cambios aplicados"; self._msg_age=0

    def _launch_selected(self):
        if not self.game: return
        g=self.game; canvas=g.canvas; cx,cy=BOSS_X,BOSS_Y; launched=[]
        for atk_cls in self.atk_sel:
            obs=None
            if atk_cls=="BeamH":
                obs=BeamH(canvas,"beam_h",y=random.randint(80,HEIGHT-80),thickness=28,warn_time=35,lifetime=55)
            elif atk_cls=="BeamV":
                obs=BeamV(canvas,"beam_v",x=random.randint(80,WIDTH-80),thickness=28,warn_time=35,lifetime=55)
            elif atk_cls=="CircleWave":
                obs=CircleWave(canvas,"cw",cx=cx,cy=cy,max_radius=max(WIDTH,HEIGHT),thickness=24,warn_time=30,lifetime=110)
            elif atk_cls=="BallBurst":
                obs=BallBurst(canvas,"burst",cx=cx,cy=cy,count=8,speed=3.0,radius=12,warn_time=28,lifetime=140)
            elif atk_cls=="RotatingLaser":
                obs=RotatingLaser(canvas,"rlaser",cx=cx,cy=cy,
                    start_angle=random.uniform(0,2*math.pi),rot_speed=random.choice([0.04,-0.04]),
                    turns=1.5,thickness=22,warn_time=40,lifetime=9999)
            elif atk_cls=="BossSpiral":
                obs=BossSpiral(canvas,"spiral",cx=cx,cy=cy,speed=5.0,arms=10,rate=20,warn_time=20,lifetime=500)
            elif atk_cls=="BossShockwave":
                obs=BossShockwave(canvas,"shockwave",cx=cx,cy=cy,count=3,gap=55,th=20,warn_time=30,lifetime=120)
            elif atk_cls=="BossCross":
                obs=BossCross(canvas,"cross",cx=cx,cy=cy,thickness=20,rot=random.uniform(0,math.pi/4),warn_time=35,lifetime=60)
            elif atk_cls=="DangerZone":
                obs=DangerZone(canvas,"zone",rx=40,ry=60,rw=WIDTH-80,rh=HEIGHT-120,warn_time=38,lifetime=55)
            elif atk_cls=="Ball":
                obs=Ball(canvas,"ball",x=random.choice([0,WIDTH]),y=random.randint(0,HEIGHT),
                    speed=3.2,radius=14,warn_time=18,lifetime=200)
            if obs:
                g.obstacles.append(obs); launched.append(atk_cls)
        if launched:
            _log(f"Ataque: {', '.join(launched)}", self.BTN_ATK)
            self._msg=f"💥 {', '.join(launched)}"; self._msg_age=0


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Just Shapes and Beats — Tkinter")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.current_mode = None
        self._show_menu()

    def _clear_binds(self):
        for seq in ("<KeyPress>","<KeyRelease>","<space>","<Shift_L>","<Shift_R>"):
            try: self.root.unbind(seq)
            except Exception: pass
        self.canvas.unbind("<Button-1>")

    def _show_menu(self):
        self._clear_binds()
        self.current_mode = None
        self._menu_frame = 0
        self._draw_menu()

    def _draw_menu(self):
        f = self._menu_frame = getattr(self,"_menu_frame",0)+1
        self.canvas.delete("all")
        self.canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=BG_COLOR,outline="")
        for x in range(0,WIDTH,40): self.canvas.create_line(x,0,x,HEIGHT,fill="#160020")
        for y in range(0,HEIGHT,40): self.canvas.create_line(0,y,WIDTH,y,fill="#160020")

        self.canvas.create_text(WIDTH//2+3,HEIGHT//2-123,
            text="JUST SHAPES WITHOUT BEATS",font=("Courier",34,"bold"),fill="#330011")
        self.canvas.create_text(WIDTH//2,HEIGHT//2-120,
            text="JUST SHAPES WITHOUT BEATS",font=("Courier",34,"bold"),fill=PLAYER_COLOR)
        self.canvas.create_text(WIDTH//2,HEIGHT//2-76,
            text="TKINTER EDITION",font=("Courier",13),fill=DIM_COLOR)

        t = time.time()
        pulse_n = int(180+75*math.sin(t*2.5))
        col_n = "#{:02x}{:02x}{:02x}".format(min(255,pulse_n),50,100)
        self.canvas.create_rectangle(WIDTH//2-160,HEIGHT//2-20,WIDTH//2+160,HEIGHT//2+30,
            fill="#1a0028",outline=col_n,width=2)
        self.canvas.create_text(WIDTH//2,HEIGHT//2+5,
            text="▶  MODO NORMAL",font=("Courier",18,"bold"),fill=col_n,tags="btn_normal")

        pulse_b = int(180+75*math.sin(t*2.5+math.pi))
        col_b = "#{:02x}{:02x}{:02x}".format(min(255,pulse_b//2+80),0,min(255,pulse_b))
        self.canvas.create_rectangle(WIDTH//2-160,HEIGHT//2+50,WIDTH//2+160,HEIGHT//2+100,
            fill="#150025",outline=col_b,width=2)
        self.canvas.create_text(WIDTH//2,HEIGHT//2+75,
            text="💀  BOSS FIGHT",font=("Courier",18,"bold"),fill=col_b,tags="btn_boss")

        pulse_s = int(180+75*math.sin(t*2.0+1.2))
        col_s = "#{:02x}{:02x}{:02x}".format(0, min(255,pulse_s//2+60), min(255,pulse_s//2+60))
        self.canvas.create_rectangle(WIDTH//2-80,HEIGHT//2+108,WIDTH//2+80,HEIGHT//2+130,
            fill="#0a1a1a",outline=col_s,width=1)
        self.canvas.create_text(WIDTH//2,HEIGHT//2+119,
            text="⚙  CONFIGURACIÓN",font=("Courier",10,"bold"),fill=col_s,tags="btn_settings")

        self.canvas.create_text(WIDTH//2,HEIGHT//2+145,
            text="WASD/Flechas = Mover   SPACE/SHIFT = Dash   ESC = Salir",
            font=("Courier",9),fill=DIM_COLOR)
        self.canvas.create_text(WIDTH//2,HEIGHT//2+162,
            text=f"Panel Admin: tecla [{ADMIN_KEY}]  (5 pestañas: VARS, ESTADO, ATAQUES, SPAWN, MAPA/LOG)",
            font=("Courier",7),fill="#553355")
        self.canvas.create_text(WIDTH//2,HEIGHT//2+178,
            text="Normal — Aviso NARANJA=rayo  MAGENTA=onda  VERDE=rafaga",
            font=("Courier",7),fill="#553355")
        self.canvas.create_text(WIDTH//2,HEIGHT//2+192,
            text="Boss — NARANJA=laser  VERDE=espiral  MAGENTA=onda  AMARILLO=cruz",
            font=("Courier",7),fill="#553355")

        self.canvas.tag_bind("btn_normal","<Button-1>",lambda e: self._start_normal())
        self.canvas.tag_bind("btn_boss",  "<Button-1>",lambda e: self._start_boss())
        self.canvas.tag_bind("btn_settings","<Button-1>",lambda e: self._show_settings())
        self.canvas.bind("<Button-1>", self._menu_click)

        if self.current_mode is None:
            self.root.after(50, self._draw_menu)

    def _menu_click(self, event):
        if event.y > HEIGHT//2-20 and event.y < HEIGHT//2+30: self._start_normal()
        elif event.y > HEIGHT//2+50 and event.y < HEIGHT//2+100: self._start_boss()
        elif event.y > HEIGHT//2+108 and event.y < HEIGHT//2+130: self._show_settings()

    def _start_normal(self):
        if self.current_mode is not None: return
        self._clear_binds()
        _log("=== Inicio Modo Normal ===", "#00ff88")
        self.current_mode = NormalMode(self.root, self.canvas, self._show_menu)

    def _start_boss(self):
        if self.current_mode is not None: return
        self._clear_binds()
        _log("=== Inicio Boss Fight ===", BOSS_COLOR)
        self.current_mode = BossFightMode(self.root, self.canvas, self._show_menu)

    def _show_settings(self):
        global ADMIN_KEY
        win = tk.Toplevel(self.root)
        win.title("Configuración")
        win.configure(bg="#0a0012")
        win.resizable(False, False)
        win.geometry("380x240")
        tk.Label(win, text="⚙  CONFIGURACIÓN",
            font=("Courier",14,"bold"), fg="#cc00ff", bg="#0a0012").pack(pady=12)
        tk.Label(win, text="Tecla para abrir el panel Admin:",
            font=("Courier",9), fg="#dddddd", bg="#0a0012").pack()
        frame = tk.Frame(win, bg="#0a0012"); frame.pack(pady=6)
        var = tk.StringVar(value=ADMIN_KEY)
        entry = tk.Entry(frame, textvariable=var, width=10,
            font=("Courier",12,"bold"), bg="#1a0030", fg="#00ffcc",
            insertbackground="#00ffcc", justify="center")
        entry.pack(side="left", padx=4)
        def capture_key(e): var.set(e.keysym); return "break"
        entry.bind("<KeyPress>", capture_key)
        tk.Label(win, text="(pulsa la tecla deseada en el campo de arriba)",
            font=("Courier",8), fg="#665577", bg="#0a0012").pack()
        tk.Label(win, text="Panel tiene 5 pestañas: VARS · ESTADO · ATAQUES · SPAWN · MAPA/LOG",
            font=("Courier",7), fg="#443355", bg="#0a0012").pack(pady=2)
        def save():
            global ADMIN_KEY
            ADMIN_KEY = var.get() or "minus"
            win.destroy()
        tk.Button(win, text="GUARDAR",
            font=("Courier",10,"bold"), bg="#330055", fg="#cc00ff",
            activebackground="#550088", relief="flat", command=save).pack(pady=14)
        tk.Label(win, text=f"Tecla actual: {ADMIN_KEY}",
            font=("Courier",8), fg="#665577", bg="#0a0012").pack()


if __name__=="__main__":
    root=tk.Tk()
    App(root)
    root.mainloop()
