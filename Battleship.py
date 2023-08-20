from field import Field, Cell
import random
import time
DEBUG = False
RAND_TEST = False

class PrintFields(object):
    """
    Printing game battle fields of the player and his foe.
    """
    def print_battle_field(self, player_name):
        """
        Strings combainer of two battle fields: player and his foe.
        """
        # Creating genarators of fields strings.
        your_ships = self.print_field("YOUR SHIPS:", player_name)
        enemy_ships = self.print_field("ENEMY SHIPS:", player_name)
        while True:
            # Get next string from both fields.
            str1 = next(your_ships)
            str2 = next(enemy_ships)
            if str1 and str2:
                # Print combined string.
                print(f"{str1}\t\t{str2}")
            else:
                break

    def print_field(self, tag, player_name):
        """
        String generator of single battle field.
        """
        if tag == "YOUR SHIPS:":
                field = player_name.my_fields.my_field
        else:
            field = player_name.my_fields.foe_field
        yield tag
        yield "   0 1 2 3 4 5 6 7 8 9"
        yield "______________________"
        for y in range(player_name.my_fields.height):
            str_ = f"{y}| "
            for x in range(player_name.my_fields.width):
                char = "."
                if field[x][y] != None and field[x][y].ship:
                    # The ship character
                    #char = chr(8864)
                    char = "#" #chr(10008)
                    if field[x][y].fired:
                        # The sunk ship character
                        char = "X"
                elif field[x][y] != None and field[x][y].fired:
                    # The miss character
                    char = "*"
                # Build single string
                str_ += f"{char} "
            # output the single string
            yield str_ 
        # End of generator
        yield False


class GunFire(PrintFields):

    def get_shot_x_y_auto(self):
        """
        Generate x, y coordinate for firing.
        """
        free_fire_field = []
        # Get all possible x, y coordinates
        free_fire_field = self.get_all_free_fire_fields()
        # Randomize single x, y pair
        return random.choice(free_fire_field)

    def get_all_free_fire_fields(self):
        """
        Get all possible x, y coordinates for firing.
        """
        free_for_fire_field = []
        if self.cur_enemy_ship_on_fire == []: 
        # New turn, no enemy ship on the fire from previous shot.
            # List of touples (x,y) of all evaleble field coordinates.
            victim_range = []
            for x in range(self.my_fields.width):
               for y in range(self.my_fields.height): 
                   victim_range.append((x,y))

        elif len(self.cur_enemy_ship_on_fire) == 1:
        # Was a single hit only on enemy ship.
            x_hit = self.cur_enemy_ship_on_fire[0][0]
            y_hit = self.cur_enemy_ship_on_fire[0][1]
            # Evaleble coordinates as a cross about the center.
            victim_range = [(x_hit-1,y_hit),(x_hit+1,y_hit),(x_hit,y_hit-1),(x_hit,y_hit+1)]
        else: 
            # Was a two or more hits on enemy ship.
            if len(self.cur_enemy_ship_on_fire) >= 2:
                # check x coordinat
                if self.cur_enemy_ship_on_fire[0][0] == self.cur_enemy_ship_on_fire[1][0]:
                    # vertical ship
                    victim_y_range = [t[1] for t in self.cur_enemy_ship_on_fire]
                    victim_y_range.sort()
                    victim_range = [(self.cur_enemy_ship_on_fire[0][0],victim_y_range[0] - 1),
                                    (self.cur_enemy_ship_on_fire[0][0],victim_y_range[-1] + 1)]
                else:
                    # horisontal ship
                    victim_x_range = [t[0] for t in self.cur_enemy_ship_on_fire]
                    victim_x_range.sort()
                    victim_range = [(victim_x_range[0] - 1,self.cur_enemy_ship_on_fire[1][1]),
                                    (victim_x_range[-1] + 1,self.cur_enemy_ship_on_fire[1][1])]
        # From evaleble coordinates choose possible for a fire.    
        for x,y in victim_range:                
            if self.my_fields.width > x >= 0 and self.my_fields.height > y >= 0:
                if self.my_fields.foe_field[x][y] == None or \
                    self.my_fields.foe_field[x][y].fired == False and \
                    self.my_fields.foe_field[x][y].busy == False:
                    free_for_fire_field.append((x,y))
        return free_for_fire_field       

    def the_shot(self):
        """
        The shot on enemy.
        """
        if self.__class__ == PC:
            print("\nPC TURN:")
        else:
            print("\nYOUR TURN:")
        hit =True
        while hit:
            # The turn will continue till miss.
            x_shot, y_shot = self.get_shot_x_y()
            # Check the enemy battle field for hit\miss 
            hit = self.enemy_fields.under_fire(x_shot, y_shot)
            if self.__class__ == PC and not RAND_TEST:
                # Delay for visual effect
                time.sleep(1)
            print(f"Shots on x={x_shot}, y={y_shot} : {'HIT' if hit else 'MISS'}")
            # Sign cell as fired on your foe fild.
            self.my_fields.foe_field[x_shot][y_shot] = Cell(x_shot,y_shot)
            self.my_fields.foe_field[x_shot][y_shot].fired = True
            if hit:
                # Reduce the counter of enemy live desks.
                self.enemy_fields.field_decks_count -= 1
                self.cur_enemy_ship_on_fire.append((x_shot,y_shot))
                # Sign cell as ship on your foe fild.
                self.my_fields.foe_field[x_shot][y_shot].ship = True 
                if self.__class__ == Player or DEBUG:
                    # In debug mode print also enemy battle fields.
                    self.print_battle_field(self)
                if len(self.cur_enemy_ship_on_fire) == self.enemy_fields.my_field[x_shot][y_shot].deck_live_cnt:
                    # The ship was sunk.
                    print(f"THE SHIP (len: {self.enemy_fields.my_field[x_shot][y_shot].ship_len}) WAS SUNK! ")
                    # Sign all cell about the sunked ship as not evaleble for fire.
                    self.my_fields.set_sank_ship_neighbors_busy(self.my_fields.foe_field, self.cur_enemy_ship_on_fire)
                    self.cur_enemy_ship_on_fire = []
            else:
                return
            if self.my_fields.field_decks_count == 0 or self.enemy_fields.field_decks_count == 0:
                # No ships remain in the navy. Game over.
                return


class Player(GunFire):
    """
    The player class
    """
    def __init__(self, my_fields, enemy_fields):
        # Hited but not sank enemy ship
        self.cur_enemy_ship_on_fire = []
        self.my_fields = my_fields
        self.enemy_fields = enemy_fields
        self.height = my_fields.height
        self.width = my_fields.width
 
    def get_shot_x_y_user(self):
        """
        Ask the player for a shooting coordinates
        """
        while True:
            try:
                # y is a vertical, x is a horizontal coordinates
                y_shot, _, x_shot = input("Your shot Admiral (y,x): ")
            except Exception as e:
                print(e)
                print("Please enter valueble coordinates in the format 'y x'")
            else:
                # Were received valueble coordinates. Exit the request loop.
                break
        x_shot = int(x_shot)
        y_shot = int(y_shot)
        return x_shot, y_shot  
    
    def get_shot_x_y(self):
        if RAND_TEST:
            # The random test - PC vs PC mode
            return self.get_shot_x_y_auto()
        else:
            return self.get_shot_x_y_user()


class PC(GunFire):
    """
    The PC class.
    """
    def __init__(self, my_fields, enemy_fields):
        # Hited but not sank ship
        self.cur_enemy_ship_on_fire = []
        self.my_fields = my_fields
        self.enemy_fields = enemy_fields
        self.height = my_fields.height
        self.width = my_fields.width

    def get_shot_x_y(self):
        return self.get_shot_x_y_auto()

    
class Battle(PrintFields):
    """
    The main class
    """
    def __init__(self):
        # Hited but not sank ship
        self.cur_pc_ship_on_fire = []
        self.cur_user_ship_on_fire = []
    
    
    def start(self):
        # Set up the battle field
        self.your_fields = Field(10,10)
        self.pc_fields = Field(10,10)

        #--------------->
        self.player = Player(my_fields=self.your_fields, enemy_fields=self.pc_fields)
        self.pc = PC(my_fields=self.pc_fields, enemy_fields=self.your_fields)
        self.print_battle_field(self.player)
        if DEBUG:
            print("===================DEBUG mode. The PC fields: ===============================")
            self.print_battle_field(self.pc)
        #--------------->


        while True:
            if self.your_fields.field_decks_count > 0:
                #self.shot_the_pc()
                #--------------->
                self.player.the_shot()
                #--------------->
            else:
                msg = "YOU LOSE!"
                break
            if self.pc_fields.field_decks_count > 0:
                #self.pc_fire_you()
                #--------------->
                self.pc.the_shot()
                #--------------->
            else:
                msg = "YOU WONE!"
                break

            #--------------->
            self.print_battle_field(self.player)
            if DEBUG:
                print("===================DEBUG mode. The PC fields: ===============================")
                self.print_battle_field(self.pc)
            
            #--------------->
            #self.your_fields.print_battle_field("YOUR SHIPS:",self.your_fields.my_field)
            #self.your_fields.print_battle_field("FOE SHIPS:",self.your_fields.foe_field)
            ## print PC result (DEBUG)
            #if DEBUG:
            #    self.pc_fields.print_battle_field("PC SHIPS:",self.pc_fields.my_field)
            #    self.pc_fields.print_battle_field("USER SHIPS:",self.pc_fields.foe_field)
        
        print("=================== GAME OVER ===============================")
        self.print_battle_field(self.player)
        if DEBUG:
            print("===================DEBUG mode. The PC fields: ===============================")
            self.print_battle_field(self.pc)
        print(f"{msg}")
        

if __name__ == "__main__":
    battle = Battle()
    battle.start()
