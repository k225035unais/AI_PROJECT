import pygame
import math
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Hexagonal Tic Tac Toe - AI 22K-5044 & 22K-5035sni")
clock = pygame.time.Clock()

# Game settings
GRID_SIZE = 4
HEX_RADIUS = 45
HEX_WIDTH = math.sqrt(3) * HEX_RADIUS
HEX_HEIGHT = 2 * HEX_RADIUS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (180, 180, 180)
BLUE = (50, 50, 255)
RED = (200, 0, 0)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
BIG_FONT = pygame.font.SysFont('Arial', 36)

# Game state
PLAYER_X = 'X'
PLAYER_O = 'O'
current_player = PLAYER_X
hex_states = ['' for _ in range(GRID_SIZE * GRID_SIZE)]
game_over = False
final_scores = None
restart_button = pygame.Rect(640, 20, 120, 40)

# Score tracking
total_scores = {PLAYER_X: 0, PLAYER_O: 0, 'Draws': 0}
live_trios = {PLAYER_X: 0, PLAYER_O: 0}

def hex_corner(center, i):
    angle_deg = 60 * i - 30
    angle_rad = math.radians(angle_deg)
    return (center[0] + HEX_RADIUS * math.cos(angle_rad),
            center[1] + HEX_RADIUS * math.sin(angle_rad))

def draw_hex(center, color=GREY, thickness=2):
    points = [hex_corner(center, i) for i in range(6)]
    pygame.draw.polygon(screen, color, points, thickness)

def get_grid_positions():
    positions = []
    offset_x = 200
    offset_y = 100
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = offset_x + HEX_WIDTH * col + (HEX_WIDTH / 2 if row % 2 else 0)
            y = offset_y + HEX_HEIGHT * 0.75 * row
            positions.append((x, y))
    return positions

def is_point_in_hex(point, center):
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return math.hypot(dx, dy) < HEX_RADIUS * 0.95

positions = get_grid_positions()

# 6 hex directions
hex_directions_even = [(0, 1), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, -1)]
hex_directions_odd = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, 1)]

def get_neighbor_index(index, d_row, d_col):
    row = index // GRID_SIZE
    col = index % GRID_SIZE
    new_row = row + d_row
    new_col = col + d_col
    if 0 <= new_row < GRID_SIZE:
        if row % 2 == 0:
            new_col += 0
        else:
            new_col += 1 if d_row in [1, -1] else 0
    if 0 <= new_col < GRID_SIZE and 0 <= new_row < GRID_SIZE:
        return new_row * GRID_SIZE + new_col
    return None

def count_trios(board):
    seen = set()
    scores = {PLAYER_X: 0, PLAYER_O: 0}
    for idx in range(len(board)):
        player = board[idx]
        if player == '':
            continue
        row = idx // GRID_SIZE
        col = idx % GRID_SIZE
        directions = hex_directions_even  if row % 2 == 0 else hex_directions_odd
        for dr, dc in directions:
            mid = get_neighbor_index(idx, dr, dc)
            end = get_neighbor_index(mid, dr, dc) if mid is not None else None
            if mid is not None and end is not None:
                if board[mid] == player and board[end] == player:
                    trio = tuple(sorted([idx, mid, end]))
                    if trio not in seen:
                        seen.add(trio)
                        scores[player] += 1
    return scores

def count_twos(board, player):
    seen = set()
    count = 0
    for idx in range(len(board)):
        if board[idx] != player:
            continue
        row = idx // GRID_SIZE
        directions = hex_directions_even if row % 2 == 0 else hex_directions_odd
        for dr, dc in directions:
            mid = get_neighbor_index(idx, dr, dc)
            if mid is not None and board[mid] == player:
                end = get_neighbor_index(mid, dr, dc)
                if end is not None and board[end] == '':
                    pair = tuple(sorted([idx, mid]))
                    if pair not in seen:
                        seen.add(pair)
                        count += 1
    return count

def evaluate(board):
    scores = count_trios(board)
    x_twos = count_twos(board, PLAYER_X)
    o_twos = count_twos(board, PLAYER_O)
    return (scores[PLAYER_O] * 100 + o_twos * 3) - (scores[PLAYER_X] * 100 + x_twos * 5)

def minimax(board, depth, alpha, beta, is_max):
    if depth == 0 or all(cell != '' for cell in board):
        return evaluate(board), None

    best = -float('inf') if is_max else float('inf')
    best_move = None
    player = PLAYER_O if is_max else PLAYER_X

    for i in range(len(board)):
        if board[i] == '':
            board[i] = player
            score, _ = minimax(board, depth-1, alpha, beta, not is_max)
            board[i] = ''
            if is_max:
                if score > best:
                    best = score
                    best_move = i
                alpha = max(alpha, score)
            else:
                if score < best:
                    best = score
                    best_move = i
                beta = min(beta, score)
            if beta <= alpha:
                break
    return best, best_move

def ai_move():
    global current_player, hex_states, game_over, final_scores, live_trios
    _, move = minimax(hex_states, 3, -float('inf'), float('inf'), True)
    if move is not None:
        hex_states[move] = PLAYER_O
        live_trios = count_trios(hex_states)
        current_player = PLAYER_X
        if all(cell != '' for cell in hex_states):
            game_over = True
            final_scores = live_trios.copy()
            if final_scores[PLAYER_X] > final_scores[PLAYER_O]:
                total_scores[PLAYER_X] += 1
            elif final_scores[PLAYER_X] < final_scores[PLAYER_O]:
                total_scores[PLAYER_O] += 1
            else:
                total_scores['Draws'] += 1

def reset_game():
    global hex_states, current_player, game_over, final_scores, live_trios
    hex_states = ['' for _ in range(GRID_SIZE * GRID_SIZE)]
    current_player = PLAYER_X
    game_over = False
    final_scores = None
    live_trios = {PLAYER_X: 0, PLAYER_O: 0}

# Main loop
running = True
while running:
    screen.fill(WHITE)

    for idx, pos in enumerate(positions):
        draw_hex(pos)
        if hex_states[idx] != '':
            text = FONT.render(hex_states[idx], True, BLACK)
            screen.blit(text, text.get_rect(center=pos))

    pygame.draw.rect(screen, BLUE, restart_button)
    screen.blit(FONT.render("Restart", True, WHITE), restart_button.move(15, 5))

    # Display current turn and live trio counts
    screen.blit(FONT.render(f"Turn: {current_player}", True, BLACK), (30, 20))
    screen.blit(FONT.render(f"Trios - X: {live_trios[PLAYER_X]}  O: {live_trios[PLAYER_O]}", True, BLACK), (30, 50))

    # Display scoreboard below restart
    screen.blit(FONT.render(f"Score X: {total_scores[PLAYER_X]}", True, BLACK), (640, 70))
    screen.blit(FONT.render(f"Score O: {total_scores[PLAYER_O]}", True, BLACK), (640, 100))
    screen.blit(FONT.render(f"Draws: {total_scores['Draws']}", True, BLACK), (640, 130))

    # Display final result
    if game_over and final_scores:
        msg = f"X: {final_scores[PLAYER_X]} vs O: {final_scores[PLAYER_O]}  "
        if final_scores[PLAYER_X] > final_scores[PLAYER_O]:
            msg += "X wins!"
        elif final_scores[PLAYER_X] < final_scores[PLAYER_O]:
            msg += "O wins!"
        else:
            msg += "Draw!"
        text = BIG_FONT.render(msg, True, RED)
        screen.blit(text, text.get_rect(center=(400, 550)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                reset_game()
            elif not game_over and current_player == PLAYER_X:
                for i, pos in enumerate(positions):
                    if is_point_in_hex(event.pos, pos) and hex_states[i] == '':
                        hex_states[i] = PLAYER_X
                        live_trios = count_trios(hex_states)
                        current_player = PLAYER_O
                        if all(cell != '' for cell in hex_states):
                            game_over = True
                            final_scores = live_trios.copy()
                            if final_scores[PLAYER_X] > final_scores[PLAYER_O]:
                                total_scores[PLAYER_X] += 1
                            elif final_scores[PLAYER_X] < final_scores[PLAYER_O]:
                                total_scores[PLAYER_O] += 1
                            else:
                                total_scores['Draws'] += 1
                        break

    if not game_over and current_player == PLAYER_O:
        ai_move()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
