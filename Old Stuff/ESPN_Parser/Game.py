import re

# Holds the data for a gane
class Game:

    # Constructor
    def __init__(self, pbp_data):

        # Find home and visitor team; set code
        for play in pbp_data:
            m = re.search(r"t(?P<visitor>\d+)", play[2])
            if m:
                self.Visitor = int(m.group("visitor"))
                m = re.search(r"t(?P<home>\d+)", play[3])
                self.Home = int(m.group("home"))
                self.Code = int(str(self.Visitor).zfill(4) + str(self.Home).zfill(4))
                break
        self.Current_Qrt = 1
        self.Visitor_Pts = 0
        self.Home_Pts = 0


    # Sets the quarter if a new one occurs
    def Set_Quarter(self, play):
        m = re.match(r"(?P<qrt>\d)(?:st|nd|rd|th) Quarter Play-by-Play", play[0])
        if m:
            self.Current_Qrt = int(m.group("qrt"))


    # Sets the point totals
    def Check_Points(self, play):
        visitor = re.match(r"\b\d+\b", play[2])
        home = re.match(r"\b\d+\b", play[3])
        if visitor and int(visitor.group(0)) > self.Visitor_Pts:
            self.Visitor_Pts = int(visitor.group(0))
        if home and int(home.group(0)) > self.Home_Pts:
            self.Home_Pts = int(home.group(0))