import time
class Logger:
    def __init__(self, logFile=time.time(), change_fileInterval=None):
        self.f = open(f"{logFile}.txt", "a")
        self.change_fileInterval = change_fileInterval

    def log(self, text):
        self.f.write(f"{text}  time: {time.time()}\n")

    def end(self):
        self.f.close()
