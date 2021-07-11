#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pygame
import random
import math
import numpy as np
from queue import PriorityQueue


# In[3]:


pygame.init()


# In[4]:


screen = pygame.display.set_mode((400,400))
pygame.display.set_caption("A-star path visualization")

icon = pygame.image.load('A-star_icon.png')
pygame.display.set_icon(icon)

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
grey = (105, 105, 105)
orange = (255, 165, 0)
indigo = (75,0,130)


class Node:
    def __init__(self , row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.neighbours = []
        self.state = white
        self.total_rows = total_rows
        self.width = width
        
    
    def get_position(self):
        return (self.row, self.col)
    
    def is_visited(self):
        return self.state == red
    
    def is_blocked(self):
        return self.state == black
    
    def is_visiting(self):
        return self.state == green
    
    def is_starting_node(self):
        return self.state == blue
    
    def is_ending_node(self):
        return self.state == orange
    
    def reset_node(self):
        self.state = white
    
    def mark_visiting(self):
        self.state = green
    
    def mark_visited(self):
        self.state = red
        
    def mark_blocked(self):
        self.state = black
    
    def mark_starting_node(self):
        self.state = blue
    
    def mark_ending_node(self):
        self.state = orange
        
    def make_path(self):
        self.state = indigo
        
    def draw_node(self, screen):
        pygame.draw.rect(screen, self.state, (self.x, self.y, self.width, self.width))
        
    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < (self.total_rows - 1) and not grid[self.row+1][self.col].is_blocked():
            self.neighbours.append(grid[self.row + 1][self.col])
            
        if self.row > 0 and not grid[self.row-1][self.col].is_blocked():
            self.neighbours.append(grid[self.row - 1][self.col])
            
        if self.col < (self.total_rows - 1) and not grid[self.row][self.col+1].is_blocked():
            self.neighbours.append(grid[self.row][self.col+1])
        if self.row > 0 and not grid[self.row][self.col-1].is_blocked():
            self.neighbours.append(grid[self.row][self.col-1])
        
        
    
    def __lt__(self, other):
        return False
        


def make_grid(rows, width):
    grid = []
    l = (width//rows)
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i,j,l,rows)
            grid[i].append(node)
            
    return grid

def draw_grid_lines(screen, rows, width):
    l = width//rows
    for i in range(rows):
        pygame.draw.line(screen, grey, (0, i*l), (width,i*l))
    for j in range(rows):
        pygame.draw.line(screen, grey, (j*l,0), (j*l, width))
            
def draw(screen, grid, rows, width):
    screen.fill(white)
    for row in grid:
        for node in row:
            node.draw_node(screen)
    
    draw_grid_lines(screen, rows, width)
    pygame.display.update()
    
def get_clicked_pos(pos, rows, width):
    l = (width//rows)
    y,x = pos
    row = y//l
    col = x//l
    
    return (row,col)


def H(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def construct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def start_algo(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    
    open_set.put((0,count,start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = H(start.get_position(), end.get_position())
    
    open_set_hash = {start}
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            construct_path(came_from, end, draw)
            end.mark_ending_node()
            return True
        
        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + H(neighbour.get_position(), end.get_position())
                
                if neighbour not in open_set_hash:
                    count +=1
                    open_set.put((f_score[neighbour],count,neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.mark_visiting()
        draw()
        
        if current != start:
            current.mark_visited()
            
    return False
                
    


def main(screen, width):
    rows = 50
    grid = make_grid(rows, width)
    
    start_node = None
    end_node = None
    
    running = True
    start = None
    end = None
    
    started = False
    
    while running:
        draw(screen, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                (row, col) = get_clicked_pos(pos, rows, width)
                node = grid[row][col]
                
                if not start and node != end:
                    start = node
                    start.mark_starting_node()
                
                elif not end and node != start:
                    end = node
                    end.mark_ending_node()
                
                elif node != end and node != start:
                    node.mark_blocked()
                
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                (row, col) = get_clicked_pos(pos, rows, width)
                node = grid[row][col]
                node.reset_node()
                
                if node == start:
                    start = None
                if node == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                
                start_algo(lambda: draw(screen, grid, rows, width) , grid, start, end)
            
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    pygame.quit()


# In[5]:


main(screen, 400)


# In[ ]:




