# Just Shapes & Beats — Tkinter Edition

A fan-made recreation of the hit rhythm-action game **Just Shapes and Beats** built entirely in Python with Tkinter. Navigate through waves of geometric obstacles and defeat powerful bosses—all without the music!

## 🎮 Game Modes

### 🎯 Normal Mode
Survive escalating waves of attacks as difficulty increases over time:
- **Horizontal & Vertical Beams** — Lasers that sweep across the screen
- **Circle Waves** — Expanding circular danger zones
- **Ball Bursts** — Projectiles firing in all directions
- **Homing Balls** — Chase you down relentlessly
- **Diagonal Lasers** — Cutting beams at various angles
- **Danger Zones** — Static rectangular hazards
- **Avalanches** — Massive coordinated attacks every 30 seconds

Track your **score** (in seconds survived), **level**, and **remaining lives**.

### 💀 Boss Fight
A three-phase intense battle against a powerful boss with unique attacks:

**Phase 1 (66% HP)** — Single rotations and basic patterns
- Rotating Lasers
- Cross patterns
- Shockwaves
- Ball bursts

**Phase 2 (33% HP)** — Increased complexity with miniboss encounter
- Boss Spirals
- Multiple laser rotations
- Homing attacks
- Companion entities appear

**Phase 3 (1% HP)** — Maximum difficulty with multiple companions
- All previous attacks at higher speed
- Coordinated companion attacks
- Zone sweeps
- Ultimate patterns

Defeat the boss by **dashing directly into it** while it's active. Survive the **final laser split sequence** and land three final hits to win!

## 🎮 Controls

| Action | Key |
|--------|-----|
| **Move Up** | `W` or `↑` |
| **Move Down** | `S` or `↓` |
| **Move Left** | `A` or `←` |
| **Move Right** | `D` or `→` |
| **Dash/Attack** | `SPACE` or `SHIFT` |
| **Open Admin Panel** | `-` (minus key) |
| **Quit Game** | `ESC` |

**Movement Speed:** 5 pixels/frame  
**Dash Speed:** 22 pixels/frame (lasts 10 frames, cooldown 45 frames)

## ✨ Features

### Admin Panel (Press `-`)
An in-game developer console with **5 tabs**:

1. **📊 VARS** — Adjust all game parameters in real-time
   - Player size, speed, dash mechanics
   - Boss HP and size
   - Enemy difficulty scaling
   - Invincibility frames
   - *Changes apply instantly without restarting*

2. **👁 ESTADO (Status)** — Live game statistics
   - Player lives and invincibility status
   - Dash cooldown and active state
   - Boss HP, phase, companion count
   - Damage taken, time elapsed
   - Quick action buttons (heal, god mode, teleport, etc.)

3. **💥 ATAQUES (Attacks)** — Launch specific attack patterns
   - Click to spawn any obstacle type
   - Test attack combinations
   - Includes all normal and boss attacks

4. **🧬 SPAWN** — Create entities and events
   - Spawn minibosses and companions
   - Trigger avalanches manually
   - Test enemy patterns
   - Control game speed (0.25x to 2x)
   - Force boss phases

5. **🗺 MAPA/LOG (Map + Log)** — Visual monitoring
   - **Minimap** showing obstacles, boss, player position
   - **Session Log** tracking all events
   - Game statistics display
   - Scroll through event history

### Difficulty Scaling
- **Normal Mode:** Difficulty increases by 1.0x every 10 seconds (base formula: `1.0 + (score/10) × 0.4`)
- **Boss Mode:** Dynamic difficulty based on boss HP remaining

### Visual Polish
- **Trail effect** behind the player showing movement history
- **Color-coded warnings** for incoming attacks
- **Invincibility flashing** when taking damage
- **Animated player** with dash aura and effects
- **Pulsing boss aura** that intensifies as HP decreases
- **Grid background** for aesthetic retro feel

### Player Mechanics
- **Max Lives:** 4 (configurable)
- **Invincible Frames:** 45 frames of temporary immunity after getting hit
- **Trail Duration:** 18 frames of movement history displayed
- **Dash Mechanics:** Can dash in any direction (defaults to up if no direction pressed)

## 🎯 Game Balance

### Normal Mode Obstacles
| Obstacle | Behavior | Spawn Frequency |
|----------|----------|-----------------|
| BeamH | Horizontal sweep | Common (Level 1+) |
| BeamV | Vertical sweep | Common (Level 1+) |
| Ball | Homing projectile | Level 2+ |
| BallBurst | 5-shot explosion | Level 2+ |
| CircleWave | Expanding ring | Level 3+ |
| LaserDiag | Diagonal cutting beam | Level 3+ |
| DangerZone | Rectangular danger area | Level 4+ |

### Boss Mode
- **Mini-boss encounters** between phases (70 seconds to defeat)
- **Companion spawning** in phases 2 & 3 (after 50% and 20% HP respectively)
- **Phase transitions** automatic based on boss HP thresholds
- **Attack interval scaling** — Faster attacks in higher phases

## 📊 Statistics Tracking

The game tracks:
- **Score/Time:** Seconds survived
- **Damage Taken:** Number of hits received
- **Dashes Used:** Total dashes executed
- **Boss Hits:** Total damage dealt to boss (boss mode only)
- **Phases Cleared:** Minibosses defeated
- **Difficulty Multiplier:** Current scaling factor

## ⚙️ Configuration

All game variables can be adjusted through the Admin Panel or modified in `JSAB.py`:

```python
# Core gameplay
WIDTH, HEIGHT = 800, 600
FPS = 60
MAX_LIVES = 4

# Player
PLAYER_SIZE = 18
PLAYER_SPEED = 5
DASH_SPEED = 22
DASH_DURATION = 10
DASH_COOLDOWN = 45
INVINCIBLE_FRAMES = 45

# Boss
BOSS_MAX_HP = 100
BOSS_SIZE = 45
MINI_HP = 6
COMPANION_HP = 5
MINIBOSS_TIME = 70
```

## 🎨 Color Scheme

| Element | Color |
|---------|-------|
| Background | `#0a0012` (deep purple) |
| Player | `#ff2d78` (hot pink) |
| Danger (Active) | `#ff3030` (red) |
| Warning (Inactive) | `#ffaa00` (orange) |
| Wave | `#ff00ff` (magenta) |
| Burst | `#00ff88` (green) |
| Boss | `#cc00ff` (purple) |
| Dash Ready | `#00eeff` (cyan) |
| Score | `#00ffcc` (aqua) |

## 🚀 Installation & Running

### Requirements
- Python 3.7+
- Tkinter (usually included with Python)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/BRlayer/Just-Shapes-without-beats.git
cd Just-Shapes-without-beats

# Run the game
python JSAB.py
```

### First Time Tips
1. **Start with Normal Mode** to learn the mechanics
2. **Press `-` to open Admin Panel** and explore different settings
3. **Test attacks** in the Admin Panel to understand patterns
4. **Try Boss Mode** once comfortable with Normal Mode
5. **Use God Mode** in Admin Panel to practice specific attack types

## 🎓 Educational Value

This project demonstrates:
- **Game loop architecture** in Tkinter
- **Collision detection** with geometric shapes
- **State machine design** for game modes
- **Real-time parameter adjustment** for game balancing
- **Complex UI panel systems** with tabs and interactions
- **Physics calculations** for homing and rotating entities
- **Performance optimization** with sprite management

## 🐛 Known Limitations

- No audio/music (hence "without beats"!)
- Single player only
- Resolution locked at 800×600
- Tkinter performance may vary on older systems

## 🛣️ Future Enhancements

Potential improvements:
- [ ] Music and sound effects
- [ ] Keyboard rebinding in settings menu
- [ ] Difficulty presets (Easy, Normal, Hard, Insane)
- [ ] Leaderboard/high score tracking
- [ ] Additional boss types
- [ ] Particle effects system
- [ ] Custom level editor

## 📝 License

This is a fan project inspired by the original **Just Shapes and Beats** by Colin Ware. Created for educational purposes.

## 🙏 Credits

- **Original Game:** Just Shapes and Beats by Colin Ware
- **Recreation:** BR_Creator
- **Built With:** Python + Tkinter

---

**Enjoy dodging! 🎮**
