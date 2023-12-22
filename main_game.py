# Import python module, pygame.
import pygame
# Import mixer, so it allows us to play sounds and music.
from pygame import mixer
# Import os, so we can use this module to load images and sounds from the game's directory.
import os
# Import random to generate random numbers
import random
# CSV is a module in Python's standard library that provides functionality for working with CSV (Comma Separated Value) files.
# <== more details will be in the explanation file about what will I exactly be usign this module for^^^
import csv
# This is a custom module that contains code for creating buttons in our game that I've created in button.py file. 
# We will use this module to create clickable buttons on the game's main menu.
import button

# Initiating mixer module
mixer.init()

# Initiating pygame module
pygame.init()

# Set the screen width of the window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Define colours
BG = (25, 25, 25)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
ASH_COLOUR = (28, 28, 28)

# Set the caption to 'Green Hero'
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Green Hero')

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Define some constants and variables that will be used throughout the game
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False


# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


""" --- Musics & Sound Affects --- """
# Set the sound affect for the jumping and set its voloume to 0.05
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)

# Set the sound affect for shootings and set its voloume to 0.05
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)

# Set the sound affect for the grenade explosions and set its voloume to 0.05
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)


""" --- Load Game Menu, Buttons and Background Images --- """
# Button images
game_menu_img = pygame.image.load('img/game_menu.png')
start_img = pygame.image.load('img/start_btn.png')
quit_img = pygame.image.load('img/exit_btn.png')
restart_img = pygame.image.load('img/restart_btn.png')

# Background
galaxy_img = pygame.image.load('img/Background/sky.png')
buildings_img = pygame.image.load('img/Background/buildings.png')
jets_img = pygame.image.load('img/Background/jets.png')
meteoroids_img = pygame.image.load('img/Background/meteoroids.png')

# Create an empty list to store our tile images
img_list = []

# Loop through each tile type
for x in range(TILE_TYPES):
    # Load the tile image from the img/Tile directory
    img = pygame.image.load(f'img/Tile/{x}.png')
    # Scale the image to TILE_SIZE x TILE_SIZE
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    # Add the scaled image to our list of tile images
    img_list.append(img)

# Bullet
bullet_img = pygame.image.load('img/icons/bullet.png')

# Grenade
grenade_img = pygame.image.load('img/icons/grenade.png')

# Pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png')
ammo_box_img = pygame.image.load('img/icons/ammo_box.png')
grenade_box_img = pygame.image.load('img/icons/grenade_box.png')
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}

# Define a font
font = pygame.font.SysFont('Futura', 30)

"""
def draw_text(text, font, text_col, x, y) define a function that takes in five arguments: 
text (the string of text to be displayed), font (the font to be used), text_col (the color of the text), 
x (the x-coordinate of the top-left corner of the text), and y (the y-coordinate of the top-left corner of the text).
"""
def draw_text(text, font, text_col, x, y):
    # Render the text using the provided font and color
    img = font.render(text, True, text_col)
    # Draw the text image onto the screen at position (x, y)
    screen.blit(img, (x, y))

""" A Function that Defines the Drawings of the Background Images """
def draw_bg():
    # Fill the screen with the background color
    screen.fill(BG)
    
    # Get the width of the meteoroids and galaxy images
    width = meteoroids_img.get_width()
    width = galaxy_img.get_width()
    
    # Draw the background layers
    for x in range(5):
        # Draw the galaxy layer at a slower scroll speed than the other layers
        screen.blit(galaxy_img, ((x * width) - bg_scroll * 0.5, 0))
        
        # Draw the meteoroids layer at the same speed as the buildings layer
        screen.blit(meteoroids_img, ((x * width) - bg_scroll * 0.5, 0))
        
        # Draw the jets layer at a slightly faster scroll speed than the other layers
        screen.blit(jets_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - jets_img.get_height() - 300))
        
        # Draw the buildings layer at the fastest scroll speed
        screen.blit(buildings_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - buildings_img.get_height()))



# A function to reset level
def reset_level():
    # Clear all game entities
	enemy_group.empty()          # Remove all enemies from the enemy group
	bullet_group.empty()         # Remove all bullets from the bullet group
	grenade_group.empty()        # Remove all grenades from the grenade group
	explosion_group.empty()      # Remove all explosions from the explosion group
	item_box_group.empty()       # Remove all item boxes from the item box group
	decoration_group.empty()     # Remove all decorations from the decoration group
	water_group.empty()          # Remove all water tiles from the water group
	exit_group.empty()           # Remove all exit tiles from the exit group

	# Create an empty tile map
	data = []                    # Create an empty list named data
	for row in range(ROWS):      # Loop over the number of rows
		r = [-1] * COLS          # Create a row with COLS number of empty tiles
		data.append(r)           # Add the row to the data list

	return data                  # Return the empty tile map (data)



"""
This class defines the properties and behavior of the player's character, called "Soldier" in the game. 
It inherits from the Pygame Sprite class and includes various attributes such as character type, speed, 
ammo, grenades, health, and animation properties, as well as methods for updating the character's movement, animation, and status.
"""
class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)  # Call the parent class constructor
		self.alive = True                    # Flag to keep track of the soldier's life status
		self.char_type = char_type           # The type of the soldier (player or enemy)
		self.speed = speed                   # The soldier's movement speed
		self.ammo = ammo                     # The soldier's remaining ammo
		self.start_ammo = ammo               # The initial ammo count of the soldier
		self.shoot_cooldown = 0              # The cooldown time after shooting a bullet
		self.grenades = grenades             # The soldier's remaining grenades
		self.health = 100                    # The soldier's health points
		self.max_health = self.health        # The soldier's maximum health points
		self.direction = 1                   # The soldier's facing direction (1 = right, -1 = left)
		self.vel_y = 0                       # The vertical velocity of the soldier (for jumping)
		self.jump = False                    # Flag to indicate whether the soldier is jumping
		self.in_air = True                   # Flag to indicate whether the soldier is in the air
		self.flip = False                    # Flag to indicate whether the soldier is flipped horizontally
		self.animation_list = []             # List to hold the soldier's animation frames
		self.frame_index = 0                 # The index of the current animation frame
		self.action = 0                      # The soldier's current action (0 = idle, 1 = run, 2 = jump, etc.)
		self.update_time = pygame.time.get_ticks()  # The time when the soldier's animation was last updated

		"""
		The following are AI-specific variables used for enemy characters in the game. 
		The move_counter variable keeps track of how long an enemy has been moving in a particular direction, 
		and the vision variable defines a rectangle used to detect the player's location within a certain range. 
		The idling variable is used to determine if an enemy is idle, and the idling_counter variable keeps track of how long an enemy has been idle for.
		"""
		# AI specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		# Load all images for the characters (enemies & player)
		animation_types = ['Idle', 'Run', 'Jump', 'Death']

		# Loop through each animation type and load all frames for that animation
		for animation in animation_types:
			# Reset temporary list of images for this animation
			temp_list = []

			# Count number of image files in the folder for this animation type
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			
			# Loop through each frame in the animation and load the image
			for i in range(num_of_frames):
				# Load the images from file and scale it to the desired size
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

				# Add the images to the temporary list for this animation
				temp_list.append(img)
			# Add the temporary list of images to the overall animation list for this character
			self.animation_list.append(temp_list)

		# Set the initial image for the character to the first frame of the "Idle" animation
		self.image = self.animation_list[self.action][self.frame_index]

		# Set the position and size of the character's sprite
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()



	def update(self):
		# Update the animation of the character
		self.update_animation()

		# Check of the character is still alive
		self.check_alive()

		# Update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		# Reset movement variables
		screen_scroll = 0
		dx = 0
		dy = 0

		# Assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		# Jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		# Apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		# Check for collision
		for tile in world.obstacle_list:
			# Check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				# If the AI has hit a wall or the edge of a tile then make it turn around 
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0

			# Check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# Check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom


		# Check for collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		# Check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		# Check if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0


		# Check if going off the edges of the screen
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		# Update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		# Update scroll based on player position
		if self.char_type == 'player':
			# Check if player is near the edge of the screen
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				# Shift player position and scroll the screen
				self.rect.x -= dx
				screen_scroll = -dx
		# Return the amount of screen scroll and whether the level is complete
		return screen_scroll, level_complete



	def shoot(self):
		# Check if the player can shoot and has ammo left
		if self.shoot_cooldown == 0 and self.ammo > 0:
			# Set cooldown and create a new bullet object
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Reduce ammo
			self.ammo -= 1
			shot_fx.play()

	# Define a function to determine whether the charavter is still alive or not
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def ai(self):
		# Check if both the AI and the player are alive
		if self.alive and player.alive:
			# Check if the AI is not idling and randomly switch to idle mode
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)  # 0: idle
				self.idling = True
				self.idling_counter = 50
				
			# Check if the player is within the AI's vision
			if self.vision.colliderect(player.rect):
				# Stop moving and face the player, then shoot
				self.update_action(0)  # 0: idle
				self.shoot()
				
			else:
				# If the AI is not idling, move left or right and update its vision
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)  # 1: run
					self.move_counter += 1
					
					# Update the AI's vision based on its movement
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					
					# If the AI has moved a certain distance, change direction
					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
						
				# If the AI is idling, decrement the idle counter and switch to non-idle mode when done
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		# Scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		# Update animation
		ANIMATION_COOLDOWN = 100
		# Update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		# Check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		# If the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		# Check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			# Update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()


	# Define a function draw images
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		# Initialize an empty list to store all the obstacles in the game world
		self.obstacle_list = []

	def process_data(self, data):
		# Get the length of the level by getting the length of the first row of data
		self.level_length = len(data[0])
		# Iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				# Create a tuple with the tile image and its rectangle
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)

					# Check the type of the tile and add it to the corresponding group
					if tile >= 0 and tile <= 8:
						# Add the tile to the obstacle group
						self.obstacle_list.append(tile_data)

					elif tile >= 9 and tile <= 10:
						# Add water tile to water group
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)

					elif tile >= 11 and tile <= 14:
						# Add decoration tile to decoration group
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)

					elif tile == 15:
						# Create a player character and health bar
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)

					elif tile == 16:
						# Create an enemy character and add it to the enemy group
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)

					elif tile == 17:
						# Create an ammo box and add it to the item box group
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)

					elif tile == 18:
						# Create a grenade box and add it to the item box group
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)

					elif tile == 19:
						# Create health box and add it to the item box group
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)

					elif tile == 20:
						# Create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar


	# This method draws all obstacles in the obstacle list onto the screen.
	def draw(self):
		# Loop through all tiles in the obstacle list.
		for tile in self.obstacle_list:
			# Shift the tile's x-coordinate to create the illusion of scrolling.
			tile[1][0] += screen_scroll
			# Draw the tile onto the screen at its new position.
			screen.blit(tile[0], tile[1])


# This class represents a decoration object that can be drawn onto the screen.
class Decoration(pygame.sprite.Sprite):
    
    # This method initializes the decoration object with an image, x and y coordinates.
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Set the image of the decoration object to the specified image.
        self.image = img
        # Get the rect (bounding box) of the image and store it in self.rect.
        self.rect = self.image.get_rect()
        # Set the midtop of the rect to the center of the top edge of the tile.
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    # This method updates the position of the decoration object.
    def update(self):
        # Move the decoration object to the left by the amount of screen_scroll.
        self.rect.x += screen_scroll


# This class represents a water tile that can be drawn onto the screen.
class Water(pygame.sprite.Sprite):
	# This method initializes the water tile object with an image, x and y coordinates.
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		# Set the image of the water tile object to the specified image.
		self.image = img
		# Get the rect (bounding box) of the image and store it in self.rect.
		self.rect = self.image.get_rect()
		# Set the midtop of the rect to the center of the top edge of the tile.
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	# This method updates the position of the Water object.
	def update(self):
		self.rect.x += screen_scroll

# The Exit class is a sprite that represents the exit of a level in a Pygame game.
class Exit(pygame.sprite.Sprite):
    
    # The __init__ method is called when a new instance of the Exit class is created.
    # img: the image to use for the sprite
    # x, y: the initial position of the sprite
    def __init__(self, img, x, y):
	
        # Call the constructor of the Sprite class to initialize the sprite.
        pygame.sprite.Sprite.__init__(self)
        
        # Set the image of the sprite to the provided image.
        self.image = img
        
        # Get the bounding rectangle of the image and set the initial position of the sprite to the center-top of the rectangle.
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    # The update method is called once per frame to update the position and behavior of the sprite.
    def update(self):
        # Move the sprite horizontally by adding the screen_scroll value to its x-coordinate.
        self.rect.x += screen_scroll



# The ItemBox class is a sprite that represents a box containing items that the player can collect in a Pygame game.
class ItemBox(pygame.sprite.Sprite):
    # The __init__ method is called when a new instance of the ItemBox class is created.
    # item_type: the type of item contained in the box (e.g., Health, Ammo, Grenade)
    # x, y: the initial position of the sprite
    def __init__(self, item_type, x, y):
        # Call the constructor of the Sprite class to initialize the sprite.
        pygame.sprite.Sprite.__init__(self)
        
        # Set the item_type attribute to the provided item_type.
        self.item_type = item_type
        
        # Set the image of the sprite to the image corresponding to the item_type from the item_boxes dictionary.
        self.image = item_boxes[self.item_type]
        
        # Get the bounding rectangle of the image and set the initial position of the sprite to the center-top of the rectangle.
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    # The update method is called once per frame to update the position and behavior of the sprite.
    def update(self):
        # Move the sprite horizontally by adding the screen_scroll value to its x-coordinate.
        self.rect.x += screen_scroll
        
        # Check if the player has collided with the item box using the Pygame sprite collision detection function.
        if pygame.sprite.collide_rect(self, player):
            # If the player has collided with the item box, check what kind of box it was.
            if self.item_type == 'Health':
                # If the box contained health, increase the player's health by 25 (up to a maximum of the player's max_health attribute).
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                # If the box contained ammo, increase the player's ammo by 15.
                player.ammo += 15
            elif self.item_type == 'Grenade':
                # If the box contained grenades, increase the player's grenade count by 3.
                player.grenades += 3
            
            # After the player has picked up the box, delete the item box sprite.
            self.kill()


# The HealthBar class creates and manages a health bar, which displays the current health level of the player
class HealthBar():
    def __init__(self, x, y, health, max_health):
        # initialize the x, y, health, and max_health attributes
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update the health attribute with the new health value
        self.health = health
        # calculate the ratio of health to max_health
        ratio = self.health / self.max_health
        # draw a black rectangle as the border of the health bar
        # with a 2 pixel margin around it
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        # draw a red rectangle as the background of the health bar
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        # draw a green rectangle as the foreground of the health bar
        # with a width proportional to the health ratio
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))



class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)    # Initialize the sprite class
		self.timer = 100                       # Set the timer to 100
		self.vel_y = -11                       # Set the y velocity to -11
		self.speed = 7                         # Set the speed to 7
		self.image = grenade_img               # Set the image to the grenade image
		self.rect = self.image.get_rect()      # Get the rectangle for the image
		self.rect.center = (x, y)              # Center the rectangle on the x, y coordinates
		self.width = self.image.get_width()    # Get the width of the image
		self.height = self.image.get_height()  # Get the height of the image
		self.direction = direction             # Set the direction of the grenade


	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		# Check for collision with level
		for tile in world.obstacle_list:
			# Check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# Check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				# Check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# Check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		# Decrease the timer for the grenade and check if it has expired
		self.timer -= 1
		if self.timer <= 0:
			self.kill() # Remove the grenade from the sprite group
			grenade_fx.play() # Play explosion sound effect
			explosion = Explosion(self.rect.x, self.rect.y, 0.5) # Create explosion object
			explosion_group.add(explosion) # Add explosion object to sprite group
			# Check if the grenade has hit the player and reduce their health if true
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			# Check if the grenade has hit an enemy and reduce their health if true
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50




class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		# Call the parent class constructor
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		# Load explosion images and scale them to the given size
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		# Initialize the first image as the starting image
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		# Set the location of the explosion sprite
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		# Initialize a counter to keep track of the frames
		self.counter = 0


	def update(self):
		#scroll
		self.rect.x += screen_scroll

		# Set the speed of the animation
		EXPLOSION_SPEED = 4

		# Update the explosion animation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			# Reset the counter and update the current image index
			self.counter = 0
			self.frame_index += 1
			# If the animation is complete, delete the explosion sprite
			if self.frame_index >= len(self.images):
				self.kill()
			# Otherwise, update the current image
			else:
				self.image = self.images[self.frame_index]



class ScreenFade():
	def __init__(self, direction, colour, speed):
		# Initialize screen fade variables
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		# Initialize fade_complete variable
		fade_complete = False

		# Update fade_counter with the given speed
		self.fade_counter += self.speed

		# Check the direction of screen fade
		if self.direction == 1: #whole screen fade
			# Draw rectangles to cover the screen in order to achieve the fade effect
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))

		if self.direction == 2: #vertical screen fade down
			# Draw rectangles to cover the screen vertically to achieve the fade effect
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))

		# Check if fade is complete
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete



# Create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, ASH_COLOUR, 4)


# Create start, exit and restart buttons:
start_button = button.Button(SCREEN_WIDTH // 2 - 360, SCREEN_HEIGHT // 2 + 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT // 2 + 150, quit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
game_menu = button.Button(SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT // 2 - 250, game_menu_img, 1)

# Create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



# Create empty tile list
world_data = []

for row in range(ROWS):
    r = [-1] * COLS  # create a list of -1's with length of COLS
    world_data.append(r)  # append each row to world_data

# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:  # open level data csv file
    reader = csv.reader(csvfile, delimiter=',')  # create csv reader object
    for x, row in enumerate(reader):  # iterate through each row
        for y, tile in enumerate(row):  # iterate through each tile in the row
            world_data[x][y] = int(tile)  # add the tile value to the world_data at position (x,y)

world = World()  # create an instance of the World class
player, health_bar = world.process_data(world_data)  # use the World instance to create the player and health bar objects based on the world data


""" --- The Main Game Loop --- """
run = True
while run:
	clock.tick(FPS)
	#draw menu
	if start_game == False:
		screen.fill(BG)
		#add buttons
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if game_menu.draw(screen):
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		#update background
		draw_bg()
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		#show ammo
		draw_text('AMMO: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		#show grenades
		draw_text('GRENADES: ', font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		#update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		#show intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.shoot()
			#throw grenades
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				#reduce grenades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#check if player has completed the level
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					#load in level data and create world
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)	
		else:
			# Reset the screen scroll to 0
			screen_scroll = 0

			# Check if the death fade animation is complete
			if death_fade.fade():
				
				# If the restart button is pressed, reset the level and start the game intro
				if restart_button.draw(screen):
					# Reset the fade counter to 0
					death_fade.fade_counter = 0
					# Set the start intro flag to True to start the game intro
					start_intro = True
					# Reset the background scroll to 0
					bg_scroll = 0
					# Reset the world data by calling the reset_level function
					world_data = reset_level()

					# Load the level data from the CSV file and create a new world
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					
					# Process the new world data and create the player and health bar
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get(): # Loop through all pygame events
		# Quit game event
		if event.type == pygame.QUIT:
			run = False # Exit game loop
		# Keyboard button press event
		if event.type == pygame.KEYDOWN:
			# Move player left with A
			if event.key == pygame.K_a:
				moving_left = True
			# Move player right with D
			if event.key == pygame.K_d:
				moving_right = True
			# Player shoots with SPACE
			if event.key == pygame.K_SPACE:
				shoot = True
			# Player throws grenade with Q
			if event.key == pygame.K_q:
				grenade = True
			# Player jumps
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play() # Play jump sound effect
			# Quit game event
			if event.key == pygame.K_ESCAPE:
				run = False # Exit game loop and quit game



		# Keyboard button released
		if event.type == pygame.KEYUP: 		# check if key has been released
			if event.key == pygame.K_a: 	# check if the key released was 'a'
				moving_left = False 		# set moving_left to False
			if event.key == pygame.K_d: 	# check if the key released was 'd'
				moving_right = False 		# set moving_right to False
			if event.key == pygame.K_SPACE: # check if the key released was 'space'
				shoot = False 				# set shoot to False
			if event.key == pygame.K_q: 	# check if the key released was 'q'
				grenade = False 			# set grenade to False
				grenade_thrown = False 		# set grenade_thrown to False


	# Update the display
	pygame.display.update()

# Quit from pygame module.
pygame.quit()