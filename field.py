
import random

class Cell(object):
    """
    Single squre on the buttlefield
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.ship = False
        self.ship_len = None
        # the number of remained live desks of the current ship
        self.deck_live_cnt = None
        self.busy = False
        self.fired = False


class Field(object):
    """
    Each player has two battlefields: my_field and foe_field (height X width)
    """
    def __init__(self, height=10, width=10):
        self.height = height
        self.width = width
        self.my_field = [[None for y in range(height)] for x in range(width)] 
        self.foe_field = [[None for y in range(height)] for x in range(width)]
        # total number of lived desks of all ships
        self.field_decks_count = 0
        # list of Navy ship length
        self.battle_ships = [5, 4, 3, 3, 3, 2]
        # Place the ships on the battlefield
        self.set_ships()

    def set_ships(self):
        """
        Place the ships
        """
        for ship_len in self.battle_ships:
            x_head, y_head, direction = self.get_ship_place(ship_len)
            for i in range(ship_len):
                if direction == "y":
                    y = y_head + i
                    x = x_head
                else:
                    x = x_head + i
                    y = y_head
                # place single desk
                self.my_field[x][y] = Cell(x,y)
                self.field_decks_count += 1
                self.my_field[x][y].ship = True
                self.my_field[x][y].busy = True
                self.my_field[x][y].ship_len = ship_len
                self.my_field[x][y].deck_live_cnt = ship_len
                # Enforce the rule: No other ships will be placed near this ship.
                self.set_neighbors_busy(self.my_field,x,y)

    def set_sank_ship_neighbors_busy(self,field, ship):
        for x,y in ship:
            self.set_neighbors_busy(field,x,y)

    def set_neighbors_busy(self,field,x_center,y_center):
        """
        Sighn the nearby cells as 'busy'.
        """
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                x = x_center + i
                y = y_center + j
                if self.width > x >= 0 and self.height > y >= 0: 
                    if field[x][y] == None:
                        field[x][y] = Cell(x,y)
                    field[x][y].busy = True

    def get_ship_place(self, ship_len)->tuple:
        all_pos:list = self.get_all_positions(ship_len)
        return random.choice(all_pos)

    def get_all_positions(self, ship_len)->list:
        pos = []
        for x in range(self.width):
            # x tested head of the ship
            x_head = x
            for y in range(self.height): 
                # y tested head of the ship
                y_head = y
                if self.my_field[x][y] != None and  self.my_field[x][y].busy:
                    # continue to the next cordinates
                    continue
                elif ship_len == 1:
                    # single length ship hasn't a direction
                    pos.append((x,y,None))
                    continue
                for direction in ["x", "y"]:
                    for i in range(ship_len - 1):
                        x = x_head
                        y = y_head
                        i += 1
                        if direction == "y":
                            y += i
                        else:
                            x += i
                        if self.width == x or self.height == y:
                            # Out of battle field.
                            break
                        if self.my_field[x][y] != None and  self.my_field[x][y].busy:
                            # There is no free position.
                            break
                        if i == ship_len-1:          
                            pos.append((x_head,y_head,direction))
        return pos

    def print_battle_field(self, tag, field):
        print(tag)
        print("   0 1 2 3 4 5 6 7 8 9")
        print("______________________")
        for y in range(self.height):
            print(f"{y}| ", end="")
            for x in range(self.width):
                char = "."
                #if field[x][y] == None:
                #    char = " "
                if field[x][y] != None and field[x][y].ship:
                    #char = chr(8864)
                    char = "1" #chr(10008)
                    if field[x][y].fired:
                        char = "X"
                elif field[x][y] != None and field[x][y].fired:
                    char = "0"

                print(f"{char} ", end="")
            print("")

    def under_fire(self, x_shot, y_shot):
        hit = False
        if self.my_field[x_shot][y_shot] != None and self.my_field[x_shot][y_shot].ship:
            # hit
            hit = True
            self.my_field[x_shot][y_shot].fired = True
        return hit
            



            


