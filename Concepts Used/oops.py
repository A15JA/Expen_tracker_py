class player:
    name="najeeb"
    position="mid-feild"
    height=170

    def intro(self):
        # print("My name is", self.name, "and I play as a", self.position)
        print(f"My name is {self.name} and I play as a {self.position}")


a=player()
a.name="ayat"
a.height=181
# print(a.name, a.height)
a.intro()