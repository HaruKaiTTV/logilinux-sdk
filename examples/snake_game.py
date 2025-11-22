#!/usr/bin/env python3
"""
Snake Game on MX Keypad

A classic Snake game running on the MX Keypad's 3x3 grid of LCD displays.
Each of the 9 physical buttons acts as a 3x3 grid of cells, creating a 
total 9x9 game board.

Controls:
- P1 (left button): Rotate snake left (counterclockwise)
- P2 (right button): Rotate snake right (clockwise)

The snake moves automatically at 10 FPS, wrapping around edges.
Eat green food cells to grow. Game over if snake hits itself.
"""

import logging
import sys
import time
import random
from io import BytesIO
from dataclasses import dataclass
from typing import List, Tuple, Set

from PIL import Image, ImageDraw

from logilinux import (
    Library,
    DeviceType,
    MXKeypadButton,
    ButtonEvent,
    EventType,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Game constants
GRID_SIZE = 9  # Total game board is 9x9
CELL_SIZE = 3  # Each physical button is 3x3 subcells
BUTTON_GRID = 3  # Physical buttons are in 3x3 layout
LCD_SIZE = 90  # Each LCD is 90x90 pixels
SUBCELL_PIXELS = LCD_SIZE // CELL_SIZE  # 30 pixels per subcell
FPS = 10
FRAME_TIME = 1.0 / FPS

# Colors
COLOR_BACKGROUND = (0, 0, 0)
COLOR_SNAKE_HEAD = (100, 150, 255)
COLOR_SNAKE_BODY = (50, 100, 200)
COLOR_FOOD = (0, 255, 0)
COLOR_GRID_LINE = (30, 30, 30)

# Directions (dx, dy)
DIR_UP = (0, -1)
DIR_RIGHT = (1, 0)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIRECTIONS = [DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT]


@dataclass
class Position:
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class SnakeGame:
    def __init__(self, device):
        self.device = device
        self.running = True
        self.game_over = False
        
        # Snake state
        self.snake: List[Position] = [Position(4, 4)]  # Start in center
        self.direction_idx = 1  # Start moving right
        self.grow_pending = 0
        
        # Track which buttons need redrawing
        self.dirty_buttons: Set[int] = set(range(9))
        
        # Button state cache (9 images, one per physical button)
        self.button_images = [None] * 9
        
        # Food (initialize after dirty_buttons)
        self.food: Position = None
        self.spawn_food()
        
        logger.info("=== Snake Game ===")
        logger.info("Controls:")
        logger.info("  P1 (left): Turn left")
        logger.info("  P2 (right): Turn right")
        logger.info(f"Snake starts at center, moving right")
        logger.info(f"Game running at {FPS} FPS")
    
    def spawn_food(self):
        """Spawn food at random empty position."""
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            pos = Position(x, y)
            
            # Check if position is empty
            if pos not in self.snake:
                self.food = pos
                # Mark button containing food as dirty
                button_idx = self.pos_to_button(pos)
                self.dirty_buttons.add(button_idx)
                logger.info(f"Food spawned at ({x}, {y})")
                break
    
    def pos_to_button(self, pos: Position) -> int:
        """Convert game position (0-8, 0-8) to button index (0-8)."""
        button_x = pos.x // CELL_SIZE
        button_y = pos.y // CELL_SIZE
        return button_y * BUTTON_GRID + button_x
    
    def pos_to_subcell(self, pos: Position) -> Tuple[int, int]:
        """Convert game position to subcell within a button (0-2, 0-2)."""
        subcell_x = pos.x % CELL_SIZE
        subcell_y = pos.y % CELL_SIZE
        return subcell_x, subcell_y
    
    def rotate_left(self):
        """Rotate snake direction counterclockwise."""
        self.direction_idx = (self.direction_idx - 1) % 4
        logger.info(f"Turned left, new direction: {DIRECTIONS[self.direction_idx]}")
    
    def rotate_right(self):
        """Rotate snake direction clockwise."""
        self.direction_idx = (self.direction_idx + 1) % 4
        logger.info(f"Turned right, new direction: {DIRECTIONS[self.direction_idx]}")
    
    def update(self):
        """Update game state (move snake, check collisions)."""
        if self.game_over:
            return
        
        # Calculate new head position
        direction = DIRECTIONS[self.direction_idx]
        head = self.snake[0]
        new_head = Position(
            (head.x + direction[0]) % GRID_SIZE,  # Wraparound
            (head.y + direction[1]) % GRID_SIZE
        )
        
        # Check self-collision
        if new_head in self.snake:
            self.game_over = True
            logger.info("GAME OVER! Snake hit itself.")
            logger.info(f"Final length: {len(self.snake)}")
            self.dirty_buttons = set(range(9))  # Redraw all for game over
            return
        
        # Mark old head and new head positions as dirty
        old_head_button = self.pos_to_button(head)
        new_head_button = self.pos_to_button(new_head)
        self.dirty_buttons.add(old_head_button)
        self.dirty_buttons.add(new_head_button)
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.grow_pending += 1
            logger.info(f"Food eaten! Length: {len(self.snake)}, Growing: +1")
            self.spawn_food()
        
        # Remove tail (unless growing)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            old_tail = self.snake.pop()
            tail_button = self.pos_to_button(old_tail)
            self.dirty_buttons.add(tail_button)
    
    def render_button(self, button_idx: int) -> Image.Image:
        """Render a single button (3x3 subcells)."""
        img = Image.new('RGB', (LCD_SIZE, LCD_SIZE), COLOR_BACKGROUND)
        draw = ImageDraw.Draw(img)
        
        # Draw grid lines
        for i in range(1, CELL_SIZE):
            line_pos = i * SUBCELL_PIXELS
            draw.line([(line_pos, 0), (line_pos, LCD_SIZE)], fill=COLOR_GRID_LINE, width=1)
            draw.line([(0, line_pos), (LCD_SIZE, line_pos)], fill=COLOR_GRID_LINE, width=1)
        
        # Calculate button's top-left position in game coordinates
        button_x = (button_idx % BUTTON_GRID) * CELL_SIZE
        button_y = (button_idx // BUTTON_GRID) * CELL_SIZE
        
        # Draw all game elements in this button's 3x3 region
        for local_y in range(CELL_SIZE):
            for local_x in range(CELL_SIZE):
                game_x = button_x + local_x
                game_y = button_y + local_y
                pos = Position(game_x, game_y)
                
                # Calculate pixel coordinates for this subcell
                px = local_x * SUBCELL_PIXELS
                py = local_y * SUBCELL_PIXELS
                
                # Draw snake
                if pos in self.snake:
                    if pos == self.snake[0]:
                        color = COLOR_SNAKE_HEAD
                    else:
                        color = COLOR_SNAKE_BODY
                    
                    # Draw subcell with small margin
                    margin = 2
                    draw.rectangle(
                        [px + margin, py + margin, 
                         px + SUBCELL_PIXELS - margin, py + SUBCELL_PIXELS - margin],
                        fill=color
                    )
                
                # Draw food
                elif pos == self.food:
                    # Draw circular food
                    margin = 4
                    draw.ellipse(
                        [px + margin, py + margin,
                         px + SUBCELL_PIXELS - margin, py + SUBCELL_PIXELS - margin],
                        fill=COLOR_FOOD
                    )
        
        # Game over overlay
        if self.game_over:
            # Red tint overlay
            overlay = Image.new('RGBA', (LCD_SIZE, LCD_SIZE), (255, 0, 0, 80))
            img.paste(overlay, (0, 0), overlay)
        
        return img
    
    def render(self):
        """Render only dirty buttons to LCD."""
        if not self.dirty_buttons:
            return
        
        for button_idx in list(self.dirty_buttons):
            img = self.render_button(button_idx)
            self.button_images[button_idx] = img
            
            # Convert to JPEG
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            jpeg_data = buffer.getvalue()
            
            # Upload to device
            self.device.set_key_image(button_idx, jpeg_data)
        
        self.dirty_buttons.clear()
    
    def on_event(self, event):
        """Handle button events."""
        if not isinstance(event, ButtonEvent):
            return
        
        if event.type != EventType.BUTTON_PRESS:
            return
        
        # Get the button enum from the event
        button = event.get_mx_keypad_button()
        
        if button == MXKeypadButton.P1_LEFT:
            self.rotate_left()
        elif button == MXKeypadButton.P2_RIGHT:
            self.rotate_right()
    
    def run(self):
        """Main game loop."""
        try:
            # Initial render
            logger.info("Rendering initial game state...")
            self.render()
            logger.info("Game started! Use P1/P2 to control snake.")
            
            last_update = time.time()
            
            while self.running:
                current_time = time.time()
                
                # Update game state at fixed rate
                if current_time - last_update >= FRAME_TIME:
                    self.update()
                    self.render()
                    last_update = current_time
                    
                    if self.game_over:
                        logger.info("Press Ctrl+C to exit")
                        # Keep running to show game over state
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            logger.info("\nGame interrupted by user")
        finally:
            self.running = False


def main():
    logger.info("=== MX Keypad Snake Game ===")
    logger.info("Searching for MX Keypad...")
    
    lib = Library()
    device = lib.find_device(DeviceType.MX_KEYPAD)
    
    if not device:
        logger.error("No MX Keypad found!")
        return 1
    
    logger.info(f"✓ Found device: {device.info.name}")
    logger.info(f"  Path: {device.info.device_path}")
    logger.info(f"  Vendor ID: 0x{device.info.vendor_id:04x}")
    logger.info(f"  Product ID: 0x{device.info.product_id:04x}")
    
    if not device.has_lcd():
        logger.error("Device does not support LCD displays!")
        return 1
    
    logger.info("Initializing LCD displays...")
    if not device.initialize():
        logger.error("Failed to initialize device!")
        return 1
    
    # Create and run game
    game = SnakeGame(device)
    device.set_event_callback(game.on_event)
    device.start_monitoring()
    
    logger.info("✓ Monitoring started")
    logger.info("")
    
    game.run()
    
    logger.info("✓ Game ended")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
