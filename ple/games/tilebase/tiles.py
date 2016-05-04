import copy

import ipdb
import numpy as np
import pygame

class Tile():
    def __init__(self, reward, x=0, y=0, width=16, height=16, toggles=None):
        #switch colors
        self.colors = {}
        colors = [(253,0,253), (0, 253, 0), (0, 253, 253), (0, 0, 253), (215, 95, 0)] 
        for i in range(len(colors)):
            c = list(colors[i])
            off_color = tuple( max(0, c[j]-100) for j in range(len(c)) ) 

            self.colors[str(i)] = {
                "on": colors[i],
                "off": off_color
            }

        self.reward = 0.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.toggles = toggles
        self.enabled = False
        self.allow_enter = True
        self.visited = False
        self.image_on = None
        self.image_off = None

        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))

        self._create_block(image)
        self.image = self.image.convert()

        self.rect = self.image.get_rect()

    def toString(self, px, py):
        # Inactive Goal at [x, y] with color code 1.
        # Active Door at [x, y]
        if self.enabled == True:
            status = "Active "
        elif self.enabled == False:
            status = "Inactive "
        else:
            status = ""
        
        color = ""
        if self.toggles != None:
            color = " with color code %s" % self.toggles

        return "%s%s at [%s, %s]%s." % (status, self.name, self.x-px, self.y-py, color)


    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (1,1,1),
            (0, 0, self.width, self.height),
            0
        )

        self.image = image

    def draw(self, screen):
        if self.image_on != None and self.image_off != None:
            if self.enabled:
                self.image = self.image_on
            else:
                self.image = self.image_off

        self.rect.center = (self.x*self.width, self.y*self.height)
        screen.blit(self.image, self.rect.center)

    def on_enter(self, dx, dy, tile_map):
        raise NotImplementedError("Please add on_enter method to tile")

    def on_exit(self, tile_map):
        return 0.0

    def on_top(self, action, tile_map):
        return 0.0

    def toggle(self):
        pass

class Goal(Tile):
    
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.name = "Goal"
        self.enabled = True

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (100,100,100),
            (0, 0, self.width, self.height),
            0
        )

        flag_color = (255, 224, 0)
        self._draw_flag(image, flag_color)
        
        image = image.convert()
        self.image = image
        self.image_on = image
        
        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))
        
        pygame.draw.rect(
            image,
            (50,50,50),
            (0, 0, self.width, self.height),
            0
        )

        flag_color = (205, 170, 0)
        self._draw_flag(image, flag_color)
        self.image_off = image.convert()

    def _draw_flag(self, image, color):
        flag_width = self.height/6
        flag_height = self.height/2
        
        triangle_verticies = [
            (self.width/2 - flag_width, flag_width),
            (self.width/2 - flag_width, flag_width+flag_height),
            (flag_height*1.5, flag_width+flag_height/2)
        ]

        pygame.draw.rect(
            image,
            color,
            (self.width/2 - flag_width, self.height/2, flag_width, flag_height-flag_width/2),
            0
        )

        pygame.draw.polygon(
            image,
            color,
            triangle_verticies,
            0
        )

    def on_enter(self, dx, dy, tile_map):
        self.visited = True
        if self.enabled == True:
            self.enabled = False
            self.image = self.image_off if self.enabled else self.image_on

        return True, self.reward

class GoalToggle(Goal):
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.name = "Toggle Goal"
        self.enabled = False

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (100,100,100),
            (0, 0, self.width, self.height),
            0
        )

        self._draw_flag(image, self.colors[self.toggles]["on"])
       
        image = image.convert()
        self.image_on = image
        self.image = image
        
        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))
        
        pygame.draw.rect(
            image,
            (50,50,50),
            (0, 0, self.width, self.height),
            0
        )
        
        self._draw_flag(image, self.colors[self.toggles]["off"])
        self.image_off = image.convert()
   
    def on_enter(self, dx, dy, tile_map):
        if self.enabled:
            self.toggle()
            self.visited = True

        return True, self.reward

    def toggle(self):
        if self.visited == False:
            self.enabled = not self.enabled
            self.image = self.image_off if self.enabled else self.image_on

class Water(Tile):
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.name = "Water"

    def _small_wave_verts(self, offset_x, offset_y):
        wave = [
            ( (0.1+offset_x)*self.width, (0.2+offset_y)*self.height ),
            ( (0.25+offset_x)*self.width, (0.1+offset_y)*self.height ),
            ( (0.45+offset_x)*self.width, (0.2+offset_y)*self.height )
        ]
        
        return wave

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (1,119,238),
            (0, 0, self.width, self.height),
            0
        )

        crest_color = (0, 181, 181)

        offsets = [
            (0,0),
            (0.45, 0.15),
            (0.60, 0.7),
            (0.0, 0.6)
        ]

        for offset in offsets:
            pygame.draw.polygon(
                image,
                crest_color,
                self._small_wave_verts(offset[0], offset[1]),
                0
            )

        self.image = image.convert()

    def on_enter(self, dx, dy, tile_map):
        return True, self.reward #same as FB had it

class Block(Tile):

    def _create_bricks(self):
        brick_height = 0.1*self.height
        brick_width = 0.2*self.width
        
        rect_list = []
        for i in range(0, int(self.width/brick_width) ):
            for j in range(0, int(self.height/brick_height) ):
                rect_list.append(( 
                    (brick_width*1.25)*i, 
                    (brick_height*1.25)*j, brick_width, brick_height ))

        return rect_list

class BlockUnmoveable(Block):
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.enabled = None #so we dont use a Active/Inactive message
        self.name = "Unmoveable Block"

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (55,55,55),
            (0, 0, self.width, self.height),
            0
        )

        for rect_tuple in self._create_bricks():
            pygame.draw.rect(
                image,
                (70,70,70),
                rect_tuple,
                0
            )

        self.image = image.convert()
    
    def on_enter(self, dx, dy, tile_map):
        return False, self.reward 

class BlockMoveable(Block):
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.enabled = None #so we dont use a Active/Inactive message
        self.name = "Moveable Block"

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (183,82,16),
            (0, 0, self.width, self.height),
            0
        )

        for rect_tuple in self._create_bricks():
            pygame.draw.rect(
                image,
                (218,117,51),
                rect_tuple,
                0
            )

        self.image = image.convert()

    def on_enter(self, dx, dy, tile_map):
        nx = np.clip(self.x + dx, 0, tile_map.map_str.shape[1]-1)  
        ny = np.clip(self.y + dy, 0, tile_map.map_str.shape[0]-1)  

        obj = tile_map.map_obj[ny, nx]
        if obj == None: #the new spot is clear
            tile_map.map_obj[ny, nx] = tile_map.map_obj[self.y, self.x]
            tile_map.map_str[ny, nx] = tile_map.map_str[self.y, self.x]
            tile_map.map_obj[self.y, self.x] = None
            tile_map.map_str[self.y, self.x] = None
            self.x = nx
            self.y = ny
            return True, self.reward
        else:
            return False, self.reward

class MultiSwitch(Tile):
    def __init__(self, *args, **kwargs):
        self.color_images = []
        self.color_idx = 0
        Tile.__init__(self, *args, **kwargs)
        self.name = "Multi Switch"
        self.enabled = True if self.toggles == "A" else False

    def _create_color_block(self, color_num):
        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))
        
        pygame.draw.rect(
            image,
            (100,100,100),
            (0, 0, self.width, self.height),
            0
        )

        switch_width = self.width*0.5
        switch_height = self.height*0.75

        pygame.draw.rect(
            image,
            self.colors[color_num]["on"],
            (self.width*0.5 - switch_width*0.5, self.height*0.25, switch_width, switch_height),
            0
        )

        image = image.convert()
        
        return image

    def _create_block(self, image):
        for k,v in self.colors.iteritems():
            self.color_images.append( (k, self._create_color_block(k)) )

        self.image = self.color_images[ self.color_idx ][1]

    def on_enter(self, dx, dy, tile_map):
        return True, self.reward 

    def _toggle_all(self, tile_map):
        sel = np.where(np.char.find(tile_map.map_str, "_%s" % self.toggles) > -1)
        toggle_list = tile_map.map_obj[sel]
        _ = [ tile.toggle() for tile in toggle_list ]

    def on_top(self, action, tile_map):
        if action == True:
            self.color_idx += 1
            if self.color_idx == len(self.color_images):
                self.color_idx = 0

            if self.enabled:
                self._toggle_all(tile_map)

            self.image = self.color_images[ self.color_idx ][1]
            self.toggles = self.color_images[ self.color_idx ][0]
            
            if self.enabled:
                self._toggle_all(tile_map)

        return 0.0

class SingleSwitch(Tile):
    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.name = "SingleSwitch"

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            (100,100,100),
            (0, 0, self.width, self.height),
            0
        )

        switch_width = self.width*0.5
        switch_height = self.height*0.75

        pygame.draw.rect(
            image,
            self.colors[self.toggles]["on"],
            (self.width*0.5 - switch_width*0.5, self.height*0.25, switch_width, switch_height),
            0
        )

        image = image.convert()
        self.image_on = image 
        self.image = image

        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))
        
        pygame.draw.rect(
            image,
            (50,50,50),
            (0, 0, self.width, self.height),
            0
        )

        pygame.draw.rect(
            image,
            self.colors[self.toggles]["off"],
            (self.width*0.5 - switch_width*0.5, self.height*0.25, switch_width, switch_height),
            0
        )

        self.image_off = image.convert()

    def _toggle_all(self, tile_map):
        sel = np.where(np.char.find(tile_map.map_str, "_%s" % self.toggles) > -1)
        toggle_list = tile_map.map_obj[sel]
        _ = [ tile.toggle() for tile in toggle_list ]

    def on_enter(self, dx, dy, tile_map):
        self._toggle_all(tile_map)
        return True, self.reward 

    def toggle(self):
        self.enabled = not self.enabled
        self.image = self.image_off if self.enabled else self.image_on

class Door(Tile):

    def __init__(self, *args, **kwargs):
        Tile.__init__(self, *args, **kwargs)
        self.name = "Door"
        self.enabled = True

    def _create_block(self, image):
        pygame.draw.rect(
            image,
            self.colors[self.toggles]["on"],
            (0, 0, self.width, self.height),
            0
        )

        image = image.convert()
        self.image_on = image 
        self.image = image

        image = pygame.Surface((self.width, self.height))
        image.fill((0,0,0, 0))
        image.set_colorkey((0,0,0, 0))
        
        pygame.draw.rect(
            image,
            self.colors[self.toggles]["off"],
            (0, 0, self.width, self.height),
            0
        )

        self.image_off = image.convert()

    def toggle(self):
        self.enabled = not self.enabled
        self.image = self.image_off if self.enabled else self.image_on

    def on_enter(self, dx, dy, tile_map):
        if self.enabled:
            return False, self.reward
        else:
            return True, self.reward
