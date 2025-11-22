#!/usr/bin/env python3
"""
Tic-Tac-Toe on MX Keypad

A simple two-player tic-tac-toe game using the 3x3 grid of LCD buttons.
Players take turns placing X and O. Press P1 to restart after game over.
"""

import sys
from io import BytesIO
from PIL import Image, ImageDraw
from logilinux import Library, DeviceType, MXKeypadButton, ButtonEvent, EventType

# Game state
board = [None] * 9  # None, 'X', or 'O'
current_player = 'X'
game_over = False
winner = None

def check_winner():
    """Check if there's a winner. Returns 'X', 'O', 'TIE', or None."""
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return 'TIE' if all(board) else None

def render_cell(cell_value, is_winner=False):
    """Render a single cell image (90x90)."""
    img = Image.new('RGB', (90, 90), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    color = (100, 255, 100) if is_winner else (200, 200, 200)
    
    if cell_value == 'X':
        # Draw X
        margin = 15
        draw.line([(margin, margin), (90-margin, 90-margin)], fill=color, width=8)
        draw.line([(90-margin, margin), (margin, 90-margin)], fill=color, width=8)
    elif cell_value == 'O':
        # Draw O
        margin = 15
        draw.ellipse([margin, margin, 90-margin, 90-margin], outline=color, width=8)
    
    # Border
    draw.rectangle([0, 0, 89, 89], outline=(100, 100, 100), width=2)
    
    return img

def render_all(device):
    """Render all 9 cells."""
    winning_cells = []
    if winner and winner != 'TIE':
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if board[a] == winner:
                winning_cells = [a, b, c]
                break
    
    for i in range(9):
        img = render_cell(board[i], i in winning_cells)
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        device.set_key_image(i, buffer.getvalue())

def on_event(event, device):
    """Handle button presses."""
    global current_player, game_over, winner, board
    
    if not isinstance(event, ButtonEvent) or event.type != EventType.BUTTON_PRESS:
        return
    
    button = event.get_mx_keypad_button()
    
    # P1 to restart
    if button == MXKeypadButton.P1_LEFT and game_over:
        board = [None] * 9
        current_player = 'X'
        game_over = False
        winner = None
        render_all(device)
        print("New game!")
        return
    
    # Grid buttons (0-8)
    if button.name.startswith('GRID_') and not game_over:
        idx = int(button.name.split('_')[1])
        
        if board[idx] is None:
            board[idx] = current_player
            
            # Check winner
            winner = check_winner()
            if winner:
                game_over = True
                print(f"{'Tie!' if winner == 'TIE' else f'{winner} wins!'} Press P1 to restart.")
            else:
                current_player = 'O' if current_player == 'X' else 'X'
            
            render_all(device)

def main():
    print("=== Tic-Tac-Toe ===")
    
    lib = Library()
    device = lib.find_device(DeviceType.MX_KEYPAD)
    
    if not device or not device.has_lcd():
        print("No MX Keypad found!")
        return 1
    
    if not device.initialize():
        print("Failed to initialize!")
        return 1
    
    render_all(device)
    device.set_event_callback(lambda e: on_event(e, device))
    device.start_monitoring()
    
    print("Game started! X goes first. Press P1 to restart.")
    
    try:
        import time
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nGame ended.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
