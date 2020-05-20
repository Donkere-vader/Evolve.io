import arcade
import random
import math 

# ARCADE GLOBAL VARIABLES
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
FULL_SCREEN = False
SCREEN_TITLE = "Evolve.io"

# GAME VARIABLES
SCREEN_PART_WIDTH = 50

# SIMULATION VARIABLES
FOOD = 200
PLAYERS = 100

POSSIBLE_STARTING_POINTS = (10, 20)
POSSIBLE_SPEED = (5, 20)
POSSIBLE_REPRODUCTION_SPEED = (1, 20)
POSSIBLE_GROWTH_FACTOR = (1, 20)
POSSIBLE_SIGHT = (1, int(SCREEN_PART_WIDTH  * 1.5))




# FUNCTION
def calculate_distane(pos: tuple, pos2: tuple) -> float:
    """ Calculates the distance between two points using the pytachoras formula a^2 + b^2 = c^2 """
    delta_x = abs(pos[0] - pos2[0])
    delta_y = abs(pos[1] - pos2[1])
    return math.sqrt(delta_x ** 2 + delta_y ** 2)

class Player(arcade.Sprite):
    """ Each player is a circle on the baord which tries to eat smaller circles """ 
    def __init__(self, color, speed, reproduction_rate, growth_factor, score, sight, pos, parent_game):
        super().__init__(
            "circle_sprite.png",
            scale=1,
            image_x=0,
            image_y=0,
            center_x=pos[0],
            center_y=pos[1]
        )

        self.color = color
        self.speed = speed
        self.reproduction_rate = reproduction_rate
        self.growth_factor = growth_factor
        self.score = score
        self.sight = sight
        self.screen_part = None
        self.parent_game = parent_game
        self.set_screen_part()

        self._set_color(self.color)
        self._set_width(self.score)
        self._set_height(self.score)

        self.change_x = random.uniform(0, self.speed)
        self.change_y = math.sqrt(self.speed ** 2 - self.change_x ** 2)
        
    def on_update(self, delta_time):
        self.set_screen_part()
        _targets_in_area = []

        # GET TARGETS IN AREA
        for y in range(-1, 2):
            _y = self.screen_part[1] + y
            if _y < 0 or _y >= len(self.parent_game.screen_parts):
                    continue

            for x in range(-1, 2):
                _x = self.screen_part[0] + x
                if _x < 0 or _x >= len(self.parent_game.screen_parts[_y]):
                    continue
            
                _targets_in_area += self.parent_game.screen_parts[_x][_y]

        # GET OPTIMAL TARGET
        target_distance = SCREEN_PART_WIDTH * 2
        target = None
        for t in _targets_in_area:
            if t.score < self.score:
                distance = calculate_distane((self.center_x, self.center_y), (t.center_x, t.center_y))
                if distance < target_distance or (type(target) == Food and type(t) == Player):
                    target_distance = distance
                    target = t
        
        self.target = target
        if target:
            self.go_to((target.center_x, target.center_y))

        if self.center_x  + self.change_x <= 0 or self.center_x + self.change_x > SCREEN_WIDTH:
            print('gaat fout, dus we draaien het om X as')
            self.change_x = self.change_x * -1

        if self.center_y  + self.change_y <= 0 or self.center_y + self.change_y > SCREEN_HEIGHT:
            print('gaat fout, dus we draaien het om Y as')
            self.change_y = self.change_y * -1

        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        

    def set_screen_part(self):
        new_screen_part = (
            int(self.center_x / SCREEN_PART_WIDTH),
            int(self.center_y / SCREEN_PART_WIDTH)
        )

        if new_screen_part != self.screen_part:
            
            if self.screen_part: # remove from old screen part
                self.parent_game.screen_parts[self.screen_part[0]][self.screen_part[1]].remove(self)
            
            # update data
            self.screen_part = new_screen_part

            print(self.change_x, self.change_y, self.center_x, self.center_y, self.screen_part)
            # add to new screen part
            self.parent_game.screen_parts[self.screen_part[0]][self.screen_part[1]].append(self)

    def reproduce(self):
        pass

    def add_score(self, add=1):
        self.score += add
        self._set_width(self.score)
        self._set_height(self.score)

    def go_to(self, pos: tuple):
        distance = calculate_distane((self.center_x, self.center_y), pos)
        delta_x = self.center_x - pos[0]
        delta_y = self.center_y - pos[1]

        try:
            mul = self.speed / distance
        except ZeroDivisionError:
            mul = 0
        self.change_x = delta_x * mul * -1
        self.change_y = delta_y * mul * -1

    def on_draw(self):
        if self.target:
            arcade.draw_line(self.center_x, self.center_y, self.target.center_x, self.target.center_y, (255, 0, 0))



class Food(arcade.Sprite):
    """ When eaten a player gains 1 point """
    def __init__(self):
        super().__init__(
            "circle_sprite.png",
            scale=1,
            image_x=0,
            image_y=0,
            center_x=random.randint(0, SCREEN_WIDTH),
            center_y=random.randint(0, SCREEN_HEIGHT)
        )

class Game(arcade.Window):
    def __init__(self):
        global SCREEN_HEIGHT, SCREEN_WIDTH
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=FULL_SCREEN)

        # SET CORRECT SCREEN DIMENSIONS
        if FULL_SCREEN:
            SCREEN_WIDTH, SCREEN_HEIGHT = self.get_size()

        # START THE SETUP
        arcade.set_background_color((255, 255, 255))
        self.setup()

    def setup(self):
        self.screen_parts = [[[] for i in range(int(SCREEN_HEIGHT / SCREEN_PART_WIDTH))] for i in range(int(SCREEN_WIDTH / SCREEN_PART_WIDTH))]

        self.players = arcade.sprite_list.SpriteList()
        self.food = arcade.sprite_list.SpriteList()

        # GENERATE PLAYERS
        for i in range(PLAYERS):
            i += 1 # get rid of the IDE warning of an unused variable
            # GENERATE RANDOM VALUES
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            speed = random.randint(POSSIBLE_SPEED[0], POSSIBLE_SPEED[1])
            reproduction_rate = random.randint(POSSIBLE_REPRODUCTION_SPEED[0], POSSIBLE_REPRODUCTION_SPEED[1])
            growth_factor = random.randint(POSSIBLE_GROWTH_FACTOR[0], POSSIBLE_GROWTH_FACTOR[1])
            score = random.randint(POSSIBLE_STARTING_POINTS[0], POSSIBLE_STARTING_POINTS[1])
            pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            sight = random.randint(POSSIBLE_SIGHT[0], POSSIBLE_SIGHT[1])

            # CREATE PLAYER
            self.players.append(
                Player(color, speed, reproduction_rate, growth_factor, score, sight, pos, self)
            )
        

    def on_update(self, delta_time):
        for player in self.players:
            player.on_update(delta_time)

    def on_draw(self):
        arcade.start_render()

        self.players.draw()
        self.food.draw()

        for player in self.players:
            player.on_draw()


if __name__ == "__main__":
    global game
    game = Game()
    arcade.run()