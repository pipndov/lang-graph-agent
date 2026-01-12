"""
Main Application Entry Point for Tic Tac Toe Game
Implements the main game loop and event handling
"""

import pygame
from game import GameController
from constants import FPS, STATE_MENU, STATE_PLAYING, STATE_GAME_OVER


def main():
    """
    Main application entry point and game loop.
    
    This function orchestrates the entire game execution:
    1. Initializes pygame
    2. Creates and configures the game controller
    3. Runs the main event loop at FPS=60
    4. Handles all user input (clicks, keyboard)
    5. Updates game state each frame
    6. Renders the current game state
    7. Handles menu navigation and mode selection
    8. Properly cleans up resources on exit
    
    The game loop continues until the user closes the window or presses ESC.
    """
    
    # Initialize pygame
    pygame.init()
    
    # Create game controller (instantiates all game components)
    game_controller = GameController()
    
    # Initialize clock for FPS control
    clock = pygame.time.Clock()
    
    # Main game loop flag
    running = True
    
    # Main event loop - runs at FPS=60
    while running:
        # Handle pygame events
        for event in pygame.event.get():
            # Handle window close button
            if event.type == pygame.QUIT:
                running = False
            
            # Handle keyboard input
            elif event.type == pygame.KEYDOWN:
                # ESC key to quit
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Menu navigation
                if game_controller.game_state == STATE_MENU:
                    # Press 1 for human vs AI mode
                    if event.key == pygame.K_1:
                        game_controller.start_game('human_vs_ai')
                    
                    # Press 2 for human vs human mode
                    elif event.key == pygame.K_2:
                        game_controller.start_game('human_vs_human')
                
                # Game over navigation
                elif game_controller.game_state == STATE_GAME_OVER:
                    # Press SPACE to return to menu
                    if event.key == pygame.K_SPACE:
                        game_controller.return_to_menu()
            
            # Handle mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only process clicks during gameplay
                if game_controller.game_state == STATE_PLAYING:
                    # Call game controller's handle_click method with mouse position
                    game_controller.handle_human_move(event.pos)
        
        # Update game state each frame
        game_controller.update_game_state()
        
        # Render current game state
        game_controller.render()
        
        # Control frame rate to FPS=60
        clock.tick(FPS)
    
    # Clean up resources on exit
    game_controller.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
