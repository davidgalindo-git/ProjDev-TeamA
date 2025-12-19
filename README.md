# ProjDev-TeamA
# Tile-Based World Editor (Pygame)
  A modular 2D world-editing tool built with Python and Pygame.
Designed for painting tiles, navigating with a minimap, managing terrain types, and generating random worlds.
## 1. Overview
This project is a tile-based world editor.
Built using Python and Pygame.
Supports painting, panning, minimap navigation, and random world generation.
Includes a start menu, toolbar, minimap, and scrollable UI elements.
Designed with a modular architecture for easy modification and expansion.

## 2. Key Features 
### 2.1 World Interaction  
Fixed-size tile grid (100 × 80).  
Integer-based terrain types:  
Water  
Grass  
Dirt/Mountain  
Sand  
Stone  
Produceral world generation using OpenSimplex noise:  
Radial fallof to force islands shapes  
Height thresholds for terrain assignment  
Automatic sand generation on coastlines  

### 2.2 User Interface
Start screen with clickable buttons.
Toolbar for selecting:
Terrain types
Brush sizes
Scrollable toolbar for many options.
Minimap showing:
World overview
Current camera viewport

### 2.3 Minimap
Real-time scaled overwiew of the entire world.
Color-coded by terrain type.

### 2.4 Painting System
Left-click painting  
Continuous painting while dragging.  
Square brush sizes :  
1  2  4  8  16   

## 3. Controls

Left Click → Paint tile  
Left Click + Drag → Continuous painting  
Toolbar Buttons → Select terrain / brush  
Time button → Play/pause time  
Window Close Button → Quit the program  

## 4. Project Structure

<img width="541" height="592" alt="Screen Shot 21 11 2025 at 10 25" src="https://github.com/user-attachments/assets/d8da5da3-fac8-4973-b0c8-8968643e9fbb" />

### 4.1 Module Explanations

main.py  
The primary game loop.  
Handles all input (painting, panning, minimap interaction).  
Controls app states (START → GAME).  
Manages rendering and event flow.  
config_cg.py  
Stores constants, sizes, colors, button configs.  
assets/loader_cg.py  
Loads raw image assets.  
Scales assets according to tile size.  
world/world_state_cg.py  
Core world class.  
Holds grid, camera position, brush and terrain state.  
Handles paint operations.  
world/generation_cg.py  
Generates a random world grid.  
rendering/draw_world_cg.py  
Draws every tile and world layer.  
Applies camera offsets.  
ui/toolbar_cg.py  
Draws the toolbar.  
Detects toolbar clicks.  
Handles brush/terrain selection.  
ui/minimap_cg.py  
Renders minimap.  
Processes clicks and drag for camera navigation.  
ui/start_screen_cg.py  
Displays the start menu.  
Handles start button interactions.

## 5. Installation & Setup
### 5.1 Requirements
Python 3.9+
Pygame  
numpy  
opensimplex

### 5.2 Install Dependencies
pip install pygame numpy opensimplex

### 5.3 Run the Program
python main.py

## 6. How the System Works
### 6.1 App States
START → Shows start screen buttons.
GAME → Active world editing mode.

### 6.2 Painting Tiles
Mouse position is converted into grid coordinates using:
grid_x = (mouse_x + camera_x) // tile_size
grid_y = (mouse_y + camera_y) // tile_size

### 6.3 Camera Movement

Right-click dragging calculates delta between frames.
Camera offset is clamped to stay inside world boundaries.

### 6.4 Minimap Navigation

Handles:
Click → Move camera
Drag → Continuous camera movement
Drag anchor (DRAG_START) for smooth scrolling

### 6.5  Toolbar Interaction

Buttons define:
Terrain type
Brush size
Scroll offset stores toolbar position.

## 7. Future Improvements (Not Yet Implemented)

Save / Load world to file.
Undo / redo system.
Multi-layer world (background, objects, decorations).
Export map as image or JSON tilemap.
Add animated tiles.
More advanced brushes.
Add sound effects and UI animations.

## 8. License

This project is open for personal, educational, and non-commercial use.
Feel free to modify and expand it.




