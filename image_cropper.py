from tkinter import *
import os
from PIL import Image, ImageTk

from tkinter import filedialog



PATH = './export/'

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 700


class Application(Frame):
    def __init__(self, parent):
        self.parent = parent
        self.supportedImageFormets = ["jpg", "png"]
        Frame.__init__(self,parent)
        self.pack(fill=BOTH, expand=True)

        self.create_Menu()
        self.create_widgets()

        self.currOpenedFolder = None
        self.imageList = []
        self.imagePointer = -1
        self.imageDim = (640, 480)
        self.imageAnchorPonits = (-1, -1)  #will be initialized later

        self.cropedPointsList = []     

        self.cropStates = [False, False]  
        self.pointsObj = [] 

    def create_Menu(self):
        self.menuBar = Menu(self)

        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open folder", command=self.selectFolder)
        self.fileMenu.add_separator()

        self.fileMenu.add_command(label="Open an image", command=self.selectImageFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.exitProgram)

        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        root.config(menu=self.menuBar)

    def create_widgets(self):
        self.viewWindow = Canvas(self, bg="white")
        self.viewWindow.pack(side=TOP, fill=BOTH, expand=True)

    def selectFolder(self):
        path = filedialog.askdirectory()
        self.currOpenedFolder = path
        files = os.listdir(path)
        for f in files:
            extension = f.split(".")[-1]
            if extension in self.supportedImageFormets:
                self.imageList.append(f)
        self.imagePointer = 0
        self.cropedPointsList = [[(0, 0), self.imageDim] for _ in self.imageList ]        
        self.renderImage()


    

    def selectImageFile(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                            title = "Select a File",
                                            filetypes = (("Image Files", "*.jpg"),("Image Files", "*.png")))
        print(filename)
        

    def renderImage(self):
        imageFile = Image.open(self.currOpenedFolder + "/" + self.imageList[self.imagePointer])
        imageFile = imageFile.resize(self.imageDim)
        imageFile = ImageTk.PhotoImage(imageFile)

        self.viewWindow.image = imageFile
        self.imageAnchorPonits = (self.parent.winfo_width() // 2 - self.imageDim[0] // 2, self.parent.winfo_height() // 2 - self.imageDim[1]  // 2)
        self.viewWindow.create_image(self.imageAnchorPonits, anchor=NW, image=imageFile, tags="bg_img")

    def onKeyPress(self, event):
        if event.keycode == 39:
            if len(self.imageList) - 1 > self.imagePointer:
                self.imagePointer += 1
        if event.keycode == 37:
            if self.imagePointer > 0:
                self.imagePointer += -1
        if event.keycode == 13: #enter

            im = Image.open(self.currOpenedFolder + "/" + self.imageList[self.imagePointer])
            im = im.resize(self.imageDim)
            x1, y1 = self.cropedPointsList[self.imagePointer][0]
            x2, y2 = self.cropedPointsList[self.imagePointer][1]
            

            im = im.crop((x1, y1, x2, y2))

            im.save(PATH + "croped." + self.imageList[self.imagePointer])
            
        self.cropStates = [False, False]

        self.renderImage()
        self.cleanUpDraws()
        
    def cleanUpDraws(self):
        for p in self.pointsObj:
            self.viewWindow.delete(p)

    def onMouseClick(self, event):
        x, y = event.x, event.y
        img_x, img_y = x - self.imageAnchorPonits[0], y - self.imageAnchorPonits[1]

        if img_x < 0 or img_y < 0:
            return
        if img_x > self.imageDim[0] or img_y > self.imageDim[1]:
            return


        print('{}, {}'.format(img_x, img_y))

        if self.cropStates[0] == False and self.cropStates[1] == False:
            self.cropedPointsList[self.imagePointer] = [( img_x, img_y  ), self.imageDim, [x, y]]
            self.cropStates[0] = True
            p = self.drawPoint((x, y))
            self.pointsObj.append(p)

        elif self.cropStates[0] == True:
            self.cropedPointsList[self.imagePointer][1] = (img_x, img_y)
            self.cropedPointsList[self.imagePointer][2].append(x)
            self.cropedPointsList[self.imagePointer][2].append(y)
 
 

            p = self.drawPoint((x, y))
            self.pointsObj.append(p)
            # self.drawRect(self.cropedPointsList[self.imagePointer][2])

    
    def drawPoint(self, point):
        x, y = point
        r = 5
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        self.viewWindow.create_oval(x0, y0, x1, y1, fill="red")

    def drawRect(self, coords):
        x1, y1, x2, y2 = coords
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        self.viewWindow.create_rectangle(x1, y1, width, height, outline="blue")






    def exitProgram(self):
        os._exit(0)

root = Tk()
root.title("Photo Zone")
root.wm_state('zoomed')

app = Application(root)

root.bind("<Key>", app.onKeyPress)
root.bind("<ButtonRelease>", app.onMouseClick)
root.mainloop()