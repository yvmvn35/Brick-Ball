import tkinter as tk


class PlayComponent(object):  #base class,contains the common features and functions of the game components.
    def __init__(self, canvas, item): #initializing method
        self.item = item
        self.canvas = canvas

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def position(self):
        return self.canvas.coords(self.item)

    def delete(self):
        self.canvas.delete(self.item)


class Paddle(PlayComponent):
    def __init__(self, canvas, x, y):
        self.height = 5
        self.width = 100
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,  #shape and appearence
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='green')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball): #setting ball to the paddle
        self.ball = ball

    def move(self, dist):   #a method used to move the paddle component a certain distance
        coord = self.position()
        width = self.canvas.winfo_width()
        if coord[2] + dist <= width and coord[0] + dist >= 0:
            super(Paddle, self).move(dist, 0)
            if self.ball is not None:
                self.ball.move(dist, 0)


class Brick(PlayComponent):
    colorArray = {1: 'lightsteelblue', 2: 'royalblue', 3: 'blue'} #colors of bricks

    def __init__(self, canvas, x, y, hits):
        self.width = 60
        self.height = 20
        self.hits = hits
        color = Brick.colorArray[hits]
        item = canvas.create_rectangle(x - self.width / 2, #shape and appearance
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tag='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):  #a method that controls the number of hits to be reduced when hit
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.colorArray[self.hits])


class Ball(PlayComponent):
    def __init__(self, canvas, x, y):
        self.radius = 6
        self.speed = 8
        self.direction = [-1, 1]
        item = canvas.create_oval(x - self.radius,  #shape and appearance
                                  y - self.radius,
                                  x + self.radius,
                                  y + self.radius,
                                  fill='red')
        super(Ball, self).__init__(canvas, item)

    def update(self):  #a method that controls movement and updating position(location)
        coord = self.position()
        width = self.canvas.winfo_width()
        if coord[1] <= 0:
            self.direction[1] *= -1
        if coord[2] >= width or coord[0] <= 0:
            self.direction[0] *= -1     #a check is made that changes direction when the ball hits the frame boundaries
                                        #calculating movement of the ball
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def intersect(self, components): #a method that controls the interaction of the ball with other components.
        coord = self.position()
        x = (coord[0] + coord[2]) * 0.5

        if len(components) == 1:
            component = components[0]
            coord = component.position()
            if x < coord[0]:
                self.direction[0] = -1
            elif x > coord[2]:
                self.direction[0] = 1
            else:
                self.direction[1] *= -1
        elif len(components) > 1:
            self.direction[1] *= -1

        for component in components:
            if isinstance(component, Brick):
                component.hit()
                Game.brick_counter += 1 #a loop that hits the brick components it interacts with, increasing the score


class Game(tk.Frame):  #the Game class derived from the Frame class in tkinter. It contains the main logic and functions of the game
    brick_counter = 0  #a class variable that tracks the number of bricks in the game

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 1000
        self.height = 400

        self.canvas = tk.Canvas(self, bg='cornsilk',
                                width=self.width,
                                height=self.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 320)
        self.items[self.paddle.item] = self.paddle

        for x in range(100, self.width - 100, 60):
            self.display_brick(x + 20, 50, 2) #a loop describing the locations and properties of brick components
            self.display_brick(x + 20, 70, 1)
            self.display_brick(x + 20, 120, 1)

        self.hud = None
        self.init_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-30))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(30))
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.brick_counter_label = tk.Label(self, text='Bricks: 0')
        self.brick_counter_label.place(relx=1.0, anchor='ne', x=-10, y=10)

    def init_game(self):
        self.update_lives_text()
        self.display_ball()
        self.text = self.draw_text(self.width / 2, self.height / 2, 'Press "S" for start')
        self.canvas.bind('<s>', lambda _: self.start_game())

    def on_canvas_resize(self, event): #a method that is called when the playground is resized
        scale_x = event.width / self.width
        scale_y = event.height / self.height
        self.width = event.width
        self.height = event.height
        self.canvas.scale("all", 0, 0, scale_x, scale_y)

    def display_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def display_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='50'): #a method that creates a text component and displays it on the screen
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<s>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self): #a loop that updates the ball component and continues the game loop
        self.verify_inter()
        num_bricks = len(self.canvas.find_withtag('brick'))

        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(self.width / 2, self.height / 2, "You Win!")
        elif self.ball.position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives == 0: #a control structure that reduces the number of lives or ends the game when the ball component hits the frame boundaries

                self.draw_text(self.width / 2, self.height / 2, "You Lost.Game Over!")
            else:
                self.after(1000, self.init_game())
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def verify_inter(self): #a method that controls components that interact with the ball component
        ball_coords = self.ball.position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.intersect(objects)
        self.update_brick_counter()

    def update_brick_counter(self):
        text = 'Bricks: %s' % Game.brick_counter
        self.brick_counter_label.config(text=text)



if __name__ == '__main__':    #main control center
    root = tk.Tk()
    root.title('Bricking Ball By Yaman Yeniceli')
    game = Game(root)
    game.mainloop()
