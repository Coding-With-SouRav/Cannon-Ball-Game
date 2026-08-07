
### Core Gameplay Features:
1. **Cannon Mechanics**:
   - Rotatable cannon that aims at mouse position
   - Multi-ball shooting capability (shoots multiple balls with spread pattern)
   - Cannon movement to collect landed balls

2. **Physics System**:
   - Realistic ball trajectory with gravity simulation
   - Elastic collisions with walls and boxes
   - Ball-to-box collision detection and response

3. **Box System**:
   - Numbered boxes requiring multiple hits to break
   - Special "ball boxes" that provide extra ammunition
   - Procedural box generation with random positions and values

4. **Progression System**:
   - Increasing difficulty levels
   - Box hit points scale with level
   - Ball collection mechanic for ammo replenishment

5. **Particle Effects**:
   - Visual feedback for collisions
   - Dynamic particle physics (size, speed, lifetime)

### UI Elements:
1. **Main Game Elements**:
   - Cannon (rotates to follow mouse)
   - Balls (yellow spheres with trajectory physics)
   - Boxes (red containers with hit counter)
   - Beam/platform at bottom (cannon base)

2. **Game Info Panel**:
   - Ball counter (top-left)
   - Level indicator (top-right)
   - Red line indicating danger zone for boxes

3. **Control Buttons**:
   - **Speed Toggle** (bottom-right): Switches between 1x and 2x game speed
   - **Play/Pause** (top-center): Toggles game state
   - **Restart** (center): Appears on game over screen

4. **Pause Menu**:
   - Semi-transparent blue overlay
   - Continue button (resumes game)
   - New Game button (restarts from level 1)

5. **Game Over Screen**:
   - Pulsating "Game Over" text animation
   - Final level display
   - Semi-transparent dark overlay
   - Automatic restart button appearance

### Technical Features:
1. **Resource Management**:
   - Cross-platform asset loading
   - Error handling for missing assets
   - Windows-specific taskbar icon configuration

2. **Multi-system Integration**:
   - Pygame for game rendering/physics
   - Tkinter for window management
   - PIL for image processing

3. **Audio System**:
   - Distinct sounds for different events:
     - Cannon firing
     - Box collisions
     - Ball collection
     - Game over

4. **Visual Enhancements**:
   - Box shadows for depth
   - Gradient sky background
   - Smooth image scaling
   - Animated text effects

5. **Game States**:
   - Ball flight physics
   - Ball return mechanics
   - Box movement sequence
   - Level transition logic

### Game Flow:
1. Aim cannon with mouse
2. Click to shoot balls
3. Break boxes to earn balls
4. Survive as boxes descend each turn
5. Game over when boxes reach red line
6. Restart or adjust settings via UI buttons

The game combines physics-based puzzle mechanics with arcade-style progression, featuring polished visuals, responsive controls, and satisfying feedback systems. The embedded Tkinter/Pygame hybrid approach provides a stable window container with high-performance rendering.

# DEMO VIDEO


https://github.com/user-attachments/assets/9f3c8ceb-e59e-4441-8380-b2584e7dbc3e


