import subprocess
from apihandler import APIHandler
from ydkhandler import YDKHandler
from config import * # Import everything from config.py without having to name it every time

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption("Tracer")
        self.clock = pg.time.Clock()

        #Init utilities
        self.ydk_handler = YDKHandler()
        self.api_handler = APIHandler()

    def run(self):
        while True:
            self.handle_events()
            self.update_logic()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def update_logic(self):
        pass

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)

        pg.display.flip()

    def quit(self):
        pg.quit()
        exit()

if __name__ == '__main__':
    app = App()
    #subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    app.run()
