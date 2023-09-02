import pygame as pg
import sys
import random
from tetris_blocks import O_B, I_B, J_B, S_B, Z_B, L_B, T_B

#TODO: implement scoring
RES = [300,600]
SIZE = 30
VERT = 10
HOR = 20
C_LEFT = [3,0]
MARGIN = 1
FPS = 60


def create_border():
        bottom = pg.Rect(0,RES[1], RES[0], 1)
        left = pg.Rect(0,0, 1, RES[1])
        right = pg.Rect(RES[0]+SIZE, 0, 1, RES[1])
        return [bottom, left, right]

borders = create_border()

def move_down(lines: dict):
    for i in range(HOR-1,0, -1):
        if i > 1:
            lines[i] = lines[i-1]
        else:
            lines[i].clear()

class DeadBlocks:
    def __init__(self, screen):
        self.dead_blocks = [] #what we render
        self.screen = screen
        self.cubes = [] #individual cells of dead_blocks for collisions
        self.lines = {
           i: [] for i in range(1, HOR)  
        } # for tracking the lines that are full

    # Fucking hell
    def check_lines(self):
        temp_lines = {
           i: [] for i in range(1, HOR)  
        }
        i_tracker = HOR-1
        down_steps = 0
        cleared = False
        score = 0
        #print(f'Lines: {self.lines}\n')
        for i in range(HOR-1, 0, -1):
            line = self.lines[i]
            if len(line) == VERT:
                #print(f'Full line, deleting cubes: {line}\n')
                for cube in line:
                    for shp in self.dead_blocks:
                        shp.find_delete(cube)
                down_steps += 1
                cleared = True
                score += 1
            if not cleared:
                if down_steps > 0:
                    #print(f'Moving cubes in line down: {line} by {down_steps} steps')
                    for cube in line:
                        cube.move_ip((0, down_steps*SIZE))
                    #print(f'Line is now: {line}\n')
                
                temp_lines[i_tracker] = line
                i_tracker -= 1
            elif cleared:
                #print(f'Clearing a line {line}, it will not be in line no more!')
                cleared = False
        self.lines = temp_lines.copy()
        if score == 1:
            score = 100
        elif score == 2:
            score = 300
        elif score == 3:
            score = 750
        else:
            score *= 400
        return score
        #print(f'New Lines: {self.lines}\n')
                    
    def add(self, block):
        self.dead_blocks.append(block)
        for cube in block.block_rects:
            self.cubes.append(cube)
            if cube not in self.lines[cube.y//SIZE]:
                self.lines[cube.y//SIZE].append(cube)
           

    def unpack(self):
        rects = [rect for key, value in self.lines.items() for rect in value]
        return rects

    def render(self):
        if len(self.dead_blocks) > 0:
            for b in self.dead_blocks:
                b.render()
            # rects = self.unpack()
            # for r in rects:
            #     pg.draw.rect(self.screen, 'grey', r)
    
#TODO: Implement hard-drop
class Shape:
    def __init__(self, s_type, shapes, color, screen):
        self.s_type = s_type
        self.shapes = shapes
        self.curr_block = shapes[0]
        self.block_rects = []
        self.length = len(shapes)
        self.rotation = 0
        self.top_x = 3
        self.top_y = 0
        self.color = color
        self.screen = screen
        self.falling = True
        self.touching = False

    def __repr__(self):
        data = {
            'type': self.s_type,
            'current': self.curr_block,
        }
        return str(data)

    def create_block(self):
        temp_y = self.top_y
        for y in self.curr_block:
            temp_x = self.top_x
            for x in y[0]:
                if x == '#':
                    cube = pg.Rect(temp_x*SIZE + MARGIN, temp_y*SIZE, SIZE, SIZE)
                    self.block_rects.append(cube)
                temp_x += 1
            temp_y += 1
        self.on_screen = True
        #print(self.block_rects)
    
    def find_delete(self, rect):
        if rect in self.block_rects:
            #print(self.block_rects)
            #print(f'Removing: {rect}')
            self.block_rects.remove(rect)
            return True
            #print('deleted a cube in a shape!')
            #print(self.block_rects)

    def delete(self, rect: pg.Rect):
        self.block_rects.remove(rect)

    def move(self, stp, col_objs):
        if self.falling:
            temp = []
            for r in self.block_rects:
                #self.top_y += SIZE
                temp.append(r.move((stp*SIZE,0)))
            if self.checkCollision(temp, col_objs, 'x'):
                pass
                #print('Collision Horizontally!')
            else:
                self.block_rects = temp[:]
                self.top_x += stp

    def rotate(self, col_objs):
        # add collision checks
        if not self.touching:
            self.rotation += 1
            #print(f'Rotation: {self.rotation}')
            self.curr_block = self.shapes[(self.rotation%self.length)]
            #print(f'{self.curr_block}')
            topleft = self.block_rects[0]
            #print(topleft)
            self.top_y = topleft.top//SIZE
            #almost similar to create_block
            track_x = False
            track_y = False
            temp_y = self.top_y
            temp_block = []
            for y in self.curr_block:
                temp_x = self.top_x
                for x in y[0]:
                    if x == '#':
                        xpos = temp_x*SIZE + MARGIN
                        ypos = temp_y*SIZE
                        if xpos >= RES[0]:
                            track_x = True
                        if ypos >= RES[1]:
                            track_y = True
                        cube = pg.Rect(xpos, ypos, SIZE, SIZE)
                        temp_block.append(cube)
                    temp_x += 1
                temp_y += 1
            if track_x:
                _holder = []
                for r in temp_block:
                    _holder.append(r.move((-SIZE,0)))
                self.block_rects = _holder[:]
                self.top_x -= 1
            elif track_y:
                _holder = []
                for r in temp_block:
                    _holder.append(r.move((0,-SIZE)))
                self.block_rects = _holder[:]
                self.top_y -= 1
            else:
                y_collision, x_collision = self.checkCollision(temp_block, col_objs, 'y'), self.checkCollision(temp_block, col_objs, 'x')
                if y_collision and x_collision:
                    self.rotation -= 1
                    self.curr_block = self.shapes[(self.rotation%self.length)]
                elif y_collision:
                    self.rotation -= 1
                    self.curr_block = self.shapes[(self.rotation%self.length)]
                elif x_collision:
                    self.rotation -= 1
                    self.curr_block = self.shapes[(self.rotation%self.length)]
                else:
                    self.block_rects = temp_block

    def move_down(self):
        temp = []
        for r in self.block_rects:
            temp.append(r.move((0,SIZE)))
        self.block_rects = temp[:]

    def fall(self, col_objs):
        self.checkCollision(self.block_rects, col_objs)
        if self.falling:
            temp = []
            for r in self.block_rects:
                #self.top_y += SIZE
                temp.append(r.move((0,SIZE)))
            if self.checkCollision(temp, col_objs):
                #print('Collision')
                self.falling = False
            else:
                self.block_rects = temp[:]

    def checkCollision(self, block, col_objs, plane='y'):
        for r in block:
            res = r.collideobjects(col_objs)
            if res:
                if plane == 'y':
                    self.falling = False
                else:
                    self.touching = True
                return True
            self.touching = False
            #return False

    def render(self):
        for cube in self.block_rects:
            pg.draw.rect(self.screen, self.color, cube, 13)

class Game:
    BLOCKS = [
        [O_B, 'blue', 'O'],
        [I_B, 'green', 'I'],
        [J_B, 'orange', 'J'],
        [L_B, 'brown', 'L'],
        [S_B, 'red', 'S'],
        [Z_B, 'yellow', 'Z'],
        [T_B, 'purple', 'T'],
    ]
    def __init__(self):
        pg.init()
        self.FPS = 60
        self.RES = [300,600]
        self.clock = pg.time.Clock()
        pg.display.set_caption('tetris')
        self.screen = pg.display.set_mode(self.RES)
        self.font = pg.font.SysFont('Verdana', 20)
        self.fpsText = self.font.render(str(round(self.clock.get_fps())), True, (0,0,0))
        self.paused = False
        self.vert_colli = [borders[0]]
        self.hor_border = [borders[1], borders[2]]
        _ = random.choice(self.BLOCKS)
        self.live_block = Shape(_[2], _[0], _[1], self.screen)
        self.live_block.create_block()
        self.dead_blocks = DeadBlocks(self.screen)
        #movement
        self.x_movement = [False, False] #left, right
        self.y_movement = [False, False] #soft-drop, hard-drop
        self.score = 0
        self.score_text = self.font.render(str(self.score), True, (250, 128, 114))

    def setShape(self):
        shpe_color = random.choice(self.BLOCKS)
        shape = Shape(shpe_color[2], shpe_color[0], shpe_color[1], self.screen)
        self.live_block = shape
        self.live_block.create_block()

    def renderScore(self):
        self.score_text = self.font.render(str(self.score), True, (250, 128, 114))
        self.screen.blit(self.score_text, (RES[0]-(SIZE*2), 0))

    def renderFPStext(self):
        self.fpsText = self.font.render(str(round(self.clock.get_fps(),2)), True, (127,127,127))
        self.screen.blit(self.fpsText, (0,0))

    def processInput(self):
        for e in pg.event.get():
            match e.type:
                case pg.QUIT:
                    pg.quit()
                    sys.exit()
                case pg.KEYDOWN:
                    match e.key:
                        case pg.K_UP:
                            if self.live_block.falling and not self.paused:
                                self.live_block.rotate(borders+self.dead_blocks.unpack())
                        case pg.K_LEFT:
                            if not self.paused:
                                self.x_movement[0] = True
                                #self.live_block.move(-1, borders[1:] + self.dead_blocks.cubes)
                        case pg.K_RIGHT:
                            if not self.paused:
                                self.x_movement[1] = True
                                #self.live_block.move(1, borders[1:] + self.dead_blocks.cubes)
                        case pg.K_ESCAPE:
                            self.paused = not self.paused
                        case pg.K_DOWN:
                            if not self.paused:
                                self.y_movement[0] = True
                        case pg.K_r:
                            pass
                case pg.KEYUP:
                    match e.key:
                        case pg.K_LEFT:
                            if not self.paused:
                                self.x_movement[0] = False
                        case pg.K_RIGHT:
                            if not self.paused:
                                self.x_movement[1] = False
                        case pg.K_DOWN:
                            if not self.paused:
                                self.y_movement[0] = False

                            

    def drawGrid(self):
        temp_x = SIZE
        y1, y2 = 0, 600
        for ver in range(VERT - 1):
            pg.draw.lines(self.screen, 'blue', True, [(temp_x, y1), (temp_x, y2)])
            temp_x += SIZE
        temp_y = SIZE
        x1, x2 = 0, 300
        for hor in range(HOR - 1):
            pg.draw.lines(self.screen, 'blue', True, [(x1, temp_y), (x2, temp_y)])
            temp_y += SIZE

    def run(self):
        running = True
        frame = 0
        #print(self.live_block)
        while running:
            #check input
            self.screen.fill('black')
            #self.processInput()
            if frame%5 == 0:
                if self.x_movement[0]:
                    self.live_block.move(-1, borders[1:] + self.dead_blocks.unpack())
                if self.x_movement[1]:
                    self.live_block.move(1, borders[1:] + self.dead_blocks.unpack())
                if self.y_movement[0]:
                    self.live_block.fall(borders[0:1] + self.dead_blocks.unpack())
            # CHANGE
            if frame == self.FPS//2 and self.live_block.falling and not self.paused:
                self.live_block.fall(borders[0:1] + self.dead_blocks.unpack())
                #print(self.dead_blocks.dead_blocks)
                frame = 0
            self.processInput()
            if self.live_block.falling == False:
                self.dead_blocks.add(self.live_block)
                self.score += self.dead_blocks.check_lines()
                self.setShape()
            
            #Render here
            self.renderFPStext()
            self.renderScore()
            
            self.live_block.render()
            self.dead_blocks.render()
            self.drawGrid()

            pg.display.flip()
            self.clock.tick(self.FPS)
            if not self.paused:
                frame += 1
            if frame > 60:
                frame = 0

Game().run()


