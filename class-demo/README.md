# Space Invaders Game

A classic Space Invaders game built with Python and Pygame.

## Features

- **Improved Gameplay**: Larger window (1024x768) for better visibility
- **Enhanced Graphics**: Bigger sprites and improved visual elements
- **Sound Effects**: Complete audio experience with:
  - Player shooting sound
  - Enemy shooting sound
  - Hit detection sound
  - Explosion effects
  - Game over sound
  - Background music (loops during gameplay)

## Controls

- **Arrow Keys**: Move left/right
- **Spacebar**: Shoot (max 3 bullets at once)
- **Any Key**: Start game or restart after game over

## Game Mechanics

- **Player**: Green ship at the bottom with 3 lives
- **Enemies**: 5 rows of invaders in different colors (different point values)
- **Shields**: Protective barriers that can be destroyed
- **Scoring**: Higher tier enemies (top rows) give more points
- **Difficulty**: Game speeds up as enemies are eliminated

## Installation & Setup

1. Make sure you have Python 3.12+ installed
2. Install dependencies:
   ```bash
   pip install pygame numpy scipy
   ```
3. Generate sound effects:
   ```bash
   python generate_sounds.py
   ```
4. Run the game:
   ```bash
   python main.py
   ```

## Sound Files

The game includes the following sound effects (generated automatically):
- `shoot.wav` - Player shooting sound
- `invader_shoot.wav` - Enemy shooting sound  
- `hit.wav` - Enemy hit sound
- `explosion.wav` - Explosion effect
- `game_over.wav` - Game over sound
- `background_music.wav` - Background music loop

## Recent Fixes

- Fixed TypeError in collision detection
- Improved game dimensions for better gameplay
- Added comprehensive sound system
- Enhanced visual elements and gameplay balance

## Game States

- **TITLE**: Initial screen, press any key to start
- **PLAYING**: Active gameplay with enemies, bullets, and scoring
- **GAME_OVER**: End screen showing final score, press any key to restart

Enjoy the game! 