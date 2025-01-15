from config.settings import * 
import pygame

def select_mode(window):

    titleFont = pygame.font.SysFont(None, 36)
    font = pygame.font.SysFont(None, 30)
    selected_mode = None

    while selected_mode is None:
        window.fill(COLOR_BACKGROUND)
        title_text = titleFont.render("Select Game Mode", True, COLOR_TEXT)
        normal_text = font.render("1. Normal Mode", True, COLOR_TEXT)
        a_star_text = font.render("2. A* Mode", True, COLOR_TEXT)
        learning_text = font.render("3. Learning Mode", True, COLOR_TEXT)

        # Display options
        window.blit(title_text, (WIDTH // 2, HEIGHT // 2 - 100))
        window.blit(normal_text, (WIDTH // 2, HEIGHT // 2 - 50))
        window.blit(a_star_text, (WIDTH // 2, HEIGHT // 2))
        window.blit(learning_text, (WIDTH // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        # Check for input to select mode
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_mode = NORMAL_MODE
                    print("Normal mode selected")
                elif event.key == pygame.K_2:
                    selected_mode = A_STAR_MODE
                    print("A* Search mode selected")
                elif event.key == pygame.K_3:
                    selected_mode = LEARNING_MODE
                    print("Learning model mode selected")

    return selected_mode