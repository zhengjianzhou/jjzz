#!/usr/bin/env python3
# pyinstaller --onefile --windowed --icon=icon.icns --add-data "pyImageView.py:." pyImageView.py
import sys, os
from pathlib import Path
from PIL import Image
import pygame
from pygame.locals import *
import time
import random
import tkinter as tk
from tkinter import filedialog
import pillow_heif
import shutil
import tempfile
import atexit
# Register HEIF/HEIC format with Pillow
pillow_heif.register_heif_opener()

SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.heic'}

def get_first_image_dimensions(folder_path):
    folder = Path(folder_path)
    for file in sorted(folder.iterdir()):
        if file.suffix.lower() in SUPPORTED_FORMATS:
            with Image.open(file) as img:
                return img.size  # returns (width, height)
    return None  # No supported image found

global THUMB_WIDTH
global THUMB_HEIGHT
THUMB_WIDTH = 128 *2
THUMB_HEIGHT = 192 *2
PERCOL_x2 = 8

class FileUndoManager:
    def __init__(self):
        self.trash_stack = []  # Stack to track deleted files
        self.tmp_dir = os.path.join(tempfile.gettempdir(), "pyimageview_undo_trash")

        # Ensure temp dir exists
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Register cleanup on app exit
        atexit.register(self.cleanup)

    def delete_file(self, filepath, idx):
        if not os.path.isfile(filepath):
            return

        filename = os.path.basename(filepath)
        tmp_path = os.path.join(self.tmp_dir, filename)

        # Avoid filename collisions in tmp
        i = 1
        while os.path.exists(tmp_path):
            tmp_path = os.path.join(self.tmp_dir, f"{filename}_{i}")
            i += 1

        shutil.move(filepath, tmp_path)
        self.trash_stack.append((tmp_path, filepath, idx))

    def undo_delete(self):
        if not self.trash_stack:
            return None, 0

        tmp_path, original_path, idx = self.trash_stack.pop()
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.move(tmp_path, original_path)
        return original_path, idx

    def cleanup(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

delete_manager = FileUndoManager()

def set_thumbnail_size(folder):
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    global THUMB_WIDTH
    global THUMB_HEIGHT
    xy = get_first_image_dimensions(folder)
    if xy:
        x, y = xy
        THUMB_WIDTH = int(screen_width/PERCOL_x2)
        THUMB_HEIGHT = int(screen_width/PERCOL_x2 * y / x)

thumbnail_cache = {}
full_image_cache = {}

def get_images(folder):
    return [f for f in sorted(Path(folder).iterdir()) if f.suffix.lower() in SUPPORTED_FORMATS]

def create_thumbnail(path):
    global THUMB_WIDTH
    global THUMB_HEIGHT
    if path in thumbnail_cache:
        return thumbnail_cache[path]
    img = Image.open(path)
    img.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))
    thumb_surface = pygame.Surface((THUMB_WIDTH, THUMB_HEIGHT))
    thumb_surface.fill((0, 0, 0))
    mode = img.mode
    size = img.size
    data = img.tobytes()
    img_surface = pygame.image.fromstring(data, size, mode)
    x = (THUMB_WIDTH - size[0]) // 2
    y = (THUMB_HEIGHT - size[1]) // 2
    thumb_surface.blit(img_surface, (x, y))
    thumbnail_cache[path] = thumb_surface
    return thumb_surface

def load_full_image(path):
    if path in full_image_cache:
        return full_image_cache[path]
    img = Image.open(path).convert("RGBA")
    full_image_cache[path] = img
    return img

def scale_image_to_fit(img, max_width, max_height):
    iw, ih = img.size
    scale = min(max_width / iw, max_height / ih)
    new_size = (int(iw * scale), int(ih * scale))
    return img.resize(new_size, Image.LANCZOS)

def clamp_scroll(scroll, min_scroll, max_scroll):
    return max(min_scroll, min(max_scroll, scroll))

def ensure_visible(selected, cols, scroll_y, max_scroll, win_h):
    sel_row = selected // cols
    sel_top = sel_row * THUMB_HEIGHT
    sel_bottom = sel_top + THUMB_HEIGHT
    if sel_top - scroll_y < 0:
        scroll_y = clamp_scroll(sel_top, 0, max_scroll)
    elif sel_bottom - scroll_y > win_h:
        scroll_y = clamp_scroll(sel_bottom - win_h, 0, max_scroll)
    return scroll_y

def next_image(selected, images_len, step=1):
    return (selected + step) % images_len if images_len > 0 else 0

def prev_image(selected, images_len):
    return (selected - 1) % images_len if images_len > 0 else 0

def select_folder():
    root = tk.Tk()
    root.withdraw()
    home_dir = os.path.expanduser("~")
    return filedialog.askdirectory(initialdir=home_dir, title="Select Folder Containing Images")

# Move this before pygame.init to prevent macOS crash
if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = select_folder()
    if not folder:
        sys.exit(0)
if folder == '.':
    folder = os.getcwd()

pygame.init()
pygame.key.set_repeat(600, 100)
screen = pygame.display.set_mode(pygame.display.list_modes()[0], FULLSCREEN)
clock = pygame.time.Clock()

set_thumbnail_size(folder)

images = get_images(folder)
selected = 0
scroll_y = 0
in_image_view = False
slideshow_mode = None
slideshow_last_time = 0
slideshow_delay = 2
slideshow_order = []
slideshow_index = 0
last_click_time = 0
double_click_interval = 0.35
running = True

while running:
    screen.fill((0, 0, 0))
    win_w, win_h = screen.get_size()
    cols = max(1, win_w // THUMB_WIDTH)
    rows = (len(images) + cols - 1) // cols
    max_scroll = max(0, rows * THUMB_HEIGHT - win_h)

    if not in_image_view:
        for idx, img_path in enumerate(images):
            col = idx % cols
            row = idx // cols
            x = col * THUMB_WIDTH
            y = row * THUMB_HEIGHT - scroll_y
            if y + THUMB_HEIGHT < 0 or y > win_h:
                continue
            thumb = create_thumbnail(img_path)
            screen.blit(thumb, (x, y))

        if images:
            sel_col = selected % cols
            sel_row = selected // cols
            sel_x = sel_col * THUMB_WIDTH
            sel_y = sel_row * THUMB_HEIGHT - scroll_y
            pygame.draw.rect(screen, (255, 255, 0), (sel_x, sel_y, THUMB_WIDTH, THUMB_HEIGHT), 4)

    else:
        if images:
            img_path = images[selected]
            pil_img = load_full_image(img_path)
            scaled_img = scale_image_to_fit(pil_img, win_w, win_h)
            mode = scaled_img.mode
            size = scaled_img.size
            data = scaled_img.tobytes()
            img_surface = pygame.image.fromstring(data, size, mode)
            x = (win_w - size[0]) // 2
            y = (win_h - size[1]) // 2
            screen.fill((0, 0, 0))
            screen.blit(img_surface, (x, y))

    pygame.display.flip()
    clock.tick(60)
    now = time.time()

    if slideshow_mode is not None and now - slideshow_last_time >= slideshow_delay and images:
        slideshow_last_time = now
        slideshow_index = (slideshow_index + 1) % len(slideshow_order)
        selected = images.index(slideshow_order[slideshow_index])

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.iconify()
            delete_manager.cleanup()
            running = False

        elif event.type == KEYDOWN:
            if event.key in (K_ESCAPE, K_q, K_RSUPER):
                if slideshow_mode is not None:
                    slideshow_mode = None
                    in_image_view = False
                    scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)
                elif in_image_view:
                    in_image_view = False
                    scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)
                else:
                    pygame.display.iconify()
                    running = False

            elif event.key in [K_u]:
                try:
                    file_undeleted, idx = delete_manager.undo_delete()
                    if file_undeleted:
                        images.insert(idx, file_undeleted)
                except:
                    pass

            elif event.key in (K_x, K_DELETE, K_RALT):
                if images:
                    file_to_delete = images[selected]
                    try:
                        # os.remove(file_to_delete)
                        delete_manager.delete_file(file_to_delete, selected)
                        images.remove(file_to_delete)
                        thumbnail_cache.pop(file_to_delete, None)
                        full_image_cache.clear()
                        if slideshow_mode is not None and file_to_delete in slideshow_order:
                            slideshow_order.remove(file_to_delete)
                            if slideshow_index >= len(slideshow_order):
                                slideshow_index = 0
                            if slideshow_order:
                                selected = images.index(slideshow_order[slideshow_index])
                            else:
                                selected = 0
                                in_image_view = False
                                slideshow_mode = None
                        if selected >= len(images):
                            selected = max(0, len(images) - 1)
                    except Exception as e:
                        pass

            elif event.key in [K_SPACE, K_RETURN, K_RSHIFT]:
                if slideshow_mode is not None:
                    slideshow_mode = None
                    in_image_view = False
                    scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)
                else:
                    in_image_view = not in_image_view
                    if not in_image_view:
                        scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)

            elif event.key in (K_r, K_s) and not in_image_view and slideshow_mode is None:
                slideshow_mode = 'random' if event.key == K_r else 'sequential'
                in_image_view = True
                slideshow_last_time = now
                slideshow_index = 0
                if slideshow_mode == 'random':
                    slideshow_order = images[:]
                    random.shuffle(slideshow_order)
                else:
                    slideshow_order = images[:]
                # Start slideshow from current selected image if sequential
                if slideshow_mode == 'sequential':
                    if images[selected] in slideshow_order:
                        slideshow_index = slideshow_order.index(images[selected])
                    else:
                        slideshow_index = 0
                selected = images.index(slideshow_order[slideshow_index])

            elif in_image_view and slideshow_mode is None:
                if event.key in (K_RIGHT, K_DOWN):
                    selected = next_image(selected, len(images))
                elif event.key in (K_LEFT, K_UP):
                    selected = prev_image(selected, len(images))

            elif not in_image_view:

               if event.key == K_RIGHT:
                   selected = (selected + 1) % len(images)
               elif event.key == K_LEFT:
                   selected = (selected - 1) % len(images)
               elif event.key == K_DOWN:
                   selected = min(len(images) - 1, selected + cols)
               elif event.key in[K_TAB, K_t, K_BACKSLASH]:
                   random.shuffle(images)
               elif event.key == K_UP:
                   selected = max(0, selected - cols)
               elif event.key in [K_a, K_QUOTE]:  # Page Up
                   selected = max(0, selected - (cols * (win_h // THUMB_HEIGHT)))
               elif event.key in [K_z, K_SLASH]:  # Page Down
                   selected = min(len(images) - 1, selected + (cols * (win_h // THUMB_HEIGHT)))
               elif event.key in [K_SEMICOLON]:  # 10x Page Up
                   selected = max(0, selected - (10 * cols * (win_h // THUMB_HEIGHT)))
               elif event.key in [K_PERIOD]:  # 10x Page Down
                   selected = min(len(images) - 1, selected + (10 * cols * (win_h // THUMB_HEIGHT)))
               elif event.key in [K_l]:  # 100x Page Up
                   selected = max(0, selected - (100 * cols * (win_h // THUMB_HEIGHT)))
               elif event.key in [K_COMMA]:  # 100x Page Down
                   selected = min(len(images) - 1, selected + (100 * cols * (win_h // THUMB_HEIGHT)))
               scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)

        elif event.type == MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 1:
                if not in_image_view:
                    col = mx // THUMB_WIDTH
                    row = (my + scroll_y) // THUMB_HEIGHT
                    idx = row * cols + col
                    if 0 <= idx < len(images):
                        if now - last_click_time < double_click_interval and idx == selected:
                            in_image_view = True
                            slideshow_mode = None
                        else:
                            selected = idx
                            scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)
                        last_click_time = now
                else:
                    if now - last_click_time < double_click_interval:
                        in_image_view = False
                        slideshow_mode = None
                        scroll_y = ensure_visible(selected, cols, scroll_y, max_scroll, win_h)
                    last_click_time = now
            elif event.button == 4:
                if not in_image_view:
                    scroll_y = clamp_scroll(scroll_y - THUMB_HEIGHT // 4, 0, max_scroll)
                elif slideshow_mode is None:
                    selected = prev_image(selected, len(images))
            elif event.button == 5:
                if not in_image_view:
                    scroll_y = clamp_scroll(scroll_y + THUMB_HEIGHT // 4, 0, max_scroll)
                elif slideshow_mode is None:
                    selected = next_image(selected, len(images))

pygame.quit()

