import pygame
import os
import random
import sys
import platform
import argparse
from pygame.locals import *
from tkinter import Tk, simpledialog, filedialog

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 600
SNAP_DISTANCE = 30

def get_pictures_directory():
    os_name = platform.system()
    if os_name == "Linux":
        return os.path.expanduser("~/Pictures")
    elif os_name == "Darwin":  # macOS, BSD
        return os.path.expanduser("~/Pictures")
    elif os_name == "Windows":
        return os.path.join(os.environ['USERPROFILE'], 'Pictures')
    else:
        raise Exception("Unsupported operating system")

def load_random_image(directory):
    images = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('png', 'jpg', 'jpeg')):
                images.append(os.path.join(root, file))
    if not images:
        raise FileNotFoundError("No images found in the specified directory.")
    return random.choice(images)

def create_puzzle(image_path, pieces):
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (WIN_WIDTH, WIN_HEIGHT))
    piece_width = WIN_WIDTH // pieces
    piece_height = WIN_HEIGHT // pieces

    pieces_list = []
    for x in range(pieces):
        for y in range(pieces):
            rect = pygame.Rect(x * piece_width, y * piece_height, piece_width, piece_height)
            piece_image = image.subsurface(rect)
            pieces_list.append((piece_image, rect))

    return pieces_list

def shuffle_pieces(pieces):
    positions = [piece[1].topleft for piece in pieces]
    random.shuffle(positions)
    for i, piece in enumerate(pieces):
        pieces[i] = (piece[0], piece[0].get_rect(topleft=positions[i]))
    return pieces

def is_solved(pieces, original_positions):
    for piece, original_pos in zip(pieces, original_positions):
        if piece[1].topleft != original_pos:
            return False
    return True

def snap_piece(piece, original_position):
    if abs(piece[1].x - original_position[0]) <= SNAP_DISTANCE and abs(piece[1].y - original_position[1]) <= SNAP_DISTANCE:
        piece[1].topleft = original_position

def load_custom_image():
    Tk().withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*")])  # Your fix for showing images
    if file_path:
        return file_path
    return None

def prompt_pieces_count():
    Tk().withdraw()
    pieces_count = simpledialog.askinteger("Input", "Enter the number of pieces per row/column:", minvalue=1)
    return pieces_count

def main(pieces_count):
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Jigsaw Puzzle")

    pictures_directory = get_pictures_directory()
    image_path = load_random_image(pictures_directory)
    pieces = create_puzzle(image_path, pieces_count)
    original_positions = [piece[1].topleft for piece in pieces]
    pieces = shuffle_pieces(pieces)

    dragging = False
    selected_piece = None
    offset_x = 0
    offset_y = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.mod & KMOD_CTRL:
                    if event.key == K_r:
                        pieces = shuffle_pieces(pieces)  # Reshuffle the current pieces
                    elif event.key == K_n:
                        image_path = load_random_image(pictures_directory)  # Load a new random image
                        pieces = create_puzzle(image_path, pieces_count)
                        original_positions = [piece[1].topleft for piece in pieces]
                        pieces = shuffle_pieces(pieces)
                    elif event.key == K_o:
                        custom_image_path = load_custom_image()
                        if custom_image_path:
                            image_path = custom_image_path
                            pieces = create_puzzle(image_path, pieces_count)
                            original_positions = [piece[1].topleft for piece in pieces]
                            pieces = shuffle_pieces(pieces)
                    elif event.key == K_p:
                        new_pieces_count = prompt_pieces_count()
                        if new_pieces_count:
                            pieces_count = new_pieces_count
                            pieces = create_puzzle(image_path, pieces_count)
                            original_positions = [piece[1].topleft for piece in pieces]
                            pieces = shuffle_pieces(pieces)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for piece in pieces:
                        if piece[1].collidepoint(event.pos):
                            dragging = True
                            selected_piece = piece
                            offset_x = piece[1].x - event.pos[0]
                            offset_y = piece[1].y - event.pos[1]
                            pieces.remove(piece)
                            pieces.append(piece)
                            break

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    if selected_piece:
                        original_position = original_positions[pieces.index(selected_piece)]
                        snap_piece(selected_piece, original_position)
                    selected_piece = None

            if event.type == MOUSEMOTION:
                if dragging and selected_piece:
                    selected_piece[1].x = event.pos[0] + offset_x
                    selected_piece[1].y = event.pos[1] + offset_y

        screen.fill((0, 0, 0))
        for piece in pieces:
            screen.blit(piece[0], piece[1])

        pygame.display.flip()

        if not dragging and is_solved(pieces, original_positions):
            pygame.time.wait(2000)
            image_path = load_random_image(pictures_directory)
            pieces = create_puzzle(image_path, pieces_count)
            original_positions = [piece[1].topleft for piece in pieces]
            pieces = shuffle_pieces(pieces)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Python Jigsaw Puzzle Game")
    parser.add_argument('-p', '--pieces', type=int, default=4, help='Number of pieces per row/column (default is 4)')
    args = parser.parse_args()
    
    main(args.pieces)
