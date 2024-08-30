from os import listdir
from os.path import isfile, join
from pathlib import Path
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import ttk
import os
import pickle
import PIL.Image
import pyglet
import sys
import textwrap
import tkinter as tk

startupText = " ~ Hello, stranger ~ \nIt's your first loop, hm? I'm going to need your help.\nGo ahead and find the \'In Stars And Time\' folder"

# if text goes over 46 characters per line at 48pt, it will go off image
maxLineLen = 46
textStartTuple = (320, 160)
textLineHeight = 60

backgroundColor = "#6b6b6b"

# stores the full file names of each character profile picture
bonnieFaces = []
euphrasieFaces = []
isabeuaFaces = []
loopFaces = []
mirabelleFaces = []
odileFaces = []
siffFaces = []
siffNoHatFaces = []

# First letter(s) of each character portrait
profilePicIndicator = ["B", "H", "I", "L", "M", "O", "S", "TS", "US"]

# each portrait starts with the first letter of the character's name
# so the first letter of each character is used to sort the portrait into the correct array
sortedFaces = {"B": bonnieFaces, "H": euphrasieFaces, "I": isabeuaFaces, "L": loopFaces,
               "M": mirabelleFaces, "O": odileFaces, "S": siffFaces, "TS": siffFaces, "US": siffNoHatFaces}

# map full character names to their respective first letter, allows full name to be used for looking up an array in the sortedFaces dict
selectionToFaceDict = {"Bonnie": "B", "Euphrasie": "H", "Isabeau": "I", "Loop": "L",
                       "Mirabelle": "M", "Odile": "O", "Siffrin": "S", "Siffrin Sans Hat": "US"}

# starting coordinates for where each character is placed over the textbox image
# found through scientific methods(pdn)
profileOffsetDict = {"Bonnie": (-70, 38), "Euphrasie": (-140, 30), "Isabeau": (-70, 0), "Loop": (-88, -74),
                     "Mirabelle": (-64, 26), "Odile": (-70, 0), "Siffrin": (-70, 0), "Siffrin Sans Hat": (-70, 0)}

# keep track of what character is currently selected. This should 100% be a class variable lmao
currentlySelectedCharacter = ""


# paths from game folder to profile pictures and icon
gamePath = ""
iconPath = '/www/icon/icon.png'
portraitPath = '/www/img/faces'

# path to the faces folder, created from the loaded gamePath and portraitPath variables
pathToFacesFiles = ""

# default name of the generated image
defaultName = "ISAT_textbox.png"


def onClosing():
    root.destroy()


def getResourcePath(relativePath):
    # holy hell do pyinstaller builds kerchoo without this
    try:
        basePath = sys._MEIPASS  # allows files to be found relative to the exe
    except AttributeError:
        # allow files to be found running from source
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relativePath)


def getExecutableDir():
    """Returns the directory where the executable is located."""
    if getattr(sys, 'frozen', False):  # If bundled by PyInstaller
        return Path(sys.executable).parent
    else:
        # For running in development (from .py file)
        return Path(__file__).parent

# variables for files outside the script that must be converted to relative paths


# renamed icon file
iconFile = "isat.ico"
iconFilePath = os.path.join(getExecutableDir(), iconFile)

fontFile = "VCR_OSD_MONO_1.001.ttf"
fontFilePath = getResourcePath(fontFile)
pyglet.font.add_file(fontFilePath)

isatFont = ImageFont.truetype(fontFilePath, 48)

# name of the program's save file
saveFile = "textboxGen.data"
saveFilePath = os.path.join(getExecutableDir(), saveFile)

emptyTextBox = "textbox_translucent.png"
emptyTextBoxPath = getResourcePath(emptyTextBox)


def checkForStartupFile(root):
    global pathToFacesFiles
    global gamePath
    # if there is no save file, prompt the user to make one
    if not os.path.exists(saveFile):
        topLevelPopUp = Toplevel(
            root, background="#000")
        topLevelPopUp.geometry('590x100')
        ttk.Label(topLevelPopUp, text=startupText, font=(
            'VCR OSD Mono', 12), background="#000", foreground="#FFF", justify="center").pack()
        waitVar = tk.IntVar()
        button = ttk.Button(topLevelPopUp, text="Okay!",
                            command=lambda: waitVar.set(1))
        button.pack()
        # wait until the user clicks okay
        button.wait_variable(waitVar)
        topLevelPopUp.destroy()
        while gamePath == "":
            # quitting was never an option, stardust
            gamePath = filedialog.askdirectory()
        pathToFacesFiles = gamePath + portraitPath
        # save the selected path here
        dataFile = open(saveFile, 'wb')
        pickle.dump(gamePath, dataFile)
        dataFile.close()
    else:
        dataFile = open(saveFile, 'rb')
        gamePath = pickle.load(dataFile)
        pathToFacesFiles = gamePath+portraitPath
        dataFile.close()
    createIcon(root, gamePath+iconPath)
    populateFaceLists()


def populateFaceLists():
    # get all available character options
    path = Path(pathToFacesFiles)
    # create a list of all available files in the faces folder
    allFiles = [f for f in listdir(path) if isfile(join(path, f))]
    # iterate through each character indicator and append portraits to their appropriate array
    for chara in profilePicIndicator:
        for file in allFiles:
            if file.startswith(chara):
                sortedFaces[chara].append(file)


def createIcon(root, pathToIcon):
    # out of a ridiculous amount of caution, I don't want to include any game assets here
    # so, this will load the png icon from the steam directory and convert it to a local ico file on startup
    if not os.path.exists(iconFile):
        iconPng = PIL.Image.open(pathToIcon)
        iconPng.save(iconFile, format="ICO")
    root.iconbitmap(iconFile)
    return


class viewClass:

    def __init__(self, root):

        self.currentImage = ""
        self.fileIndex = 0
        # flag to indicate if there is a generated image available to save
        self.newImageAvailable = False

        self.custom_font = font.Font(
            root,
            family=isatFont.getname()[0],
            size=12
        )

        self.root = root

        self.root.configure(bg=backgroundColor)
        style = ttk.Style()
        style.configure('TFrame', background=backgroundColor)
        style.configure('TLabel', background=backgroundColor)
        style.configure('TButton', background=backgroundColor)

        self.topFrame = ttk.Frame(root, padding=10)
        self.topFrame.grid()

        self.characterSelFrame = ttk.Frame(self.topFrame, padding=10)
        self.characterSelFrame.grid()
        self.characterSelFrame.grid(row=0, column=0)

        self.previewFrame = ttk.Frame(self.topFrame, padding=10)
        self.previewFrame.grid()
        self.previewFrame.grid(row=1, column=0)

        self.buttonFrame = ttk.Frame(self.topFrame, padding=10)
        self.buttonFrame.grid()
        self.buttonFrame.grid(row=2, column=0)

        self.savePreviewFrame = ttk.Frame(self.topFrame, padding=10)
        self.savePreviewFrame.grid()
        self.savePreviewFrame.grid(row=3, column=0)

        # top row = character selection stuff
        ttk.Label(self.characterSelFrame,
                  text="Character").grid(row=0, column=0)
        self.characterSelect = ttk.Combobox(self.characterSelFrame, value=[
                                            "Bonnie", "Euphrasie", "Isabeau", "Loop", "Mirabelle", "Odile", "Siffrin", "Siffrin Sans Hat"])
        self.characterSelect.bind(
            "<<ComboboxSelected>>", self.onCharacterSelect)
        self.characterSelect.grid(row=1, column=0)

        ttk.Label(self.characterSelFrame,
                  text="Portrait").grid(row=0, column=1)
        self.profileSelect = ttk.Combobox(self.characterSelFrame, value=[])
        self.profileSelect.bind("<<ComboboxSelected>>", self.onProfileSelect)
        self.profileSelect.grid(row=1, column=1)

        # second row has the text entry box and portrait preview
        self.textEntryBox = Text(self.previewFrame, foreground="white",
                                 background="black", height=5, width=40, font=('VCR OSD Mono', 12))
        self.textEntryBox.insert(END, "What they be saying?")
        self.textEntryBox.grid(row=0, column=0)

        ttk.Label(self.previewFrame, text="Portrait Preview").grid(
            row=1, column=0)
        self.preview = Label(self.previewFrame, background=backgroundColor)
        self.preview.grid(row=2, column=0)

        # third row is for buttons
        self.sendItButton = ttk.Button(
            self.buttonFrame, text="Generate!", command=self.makeTheRestOfTheDamnOwl)
        self.sendItButton.grid(row=0, column=0)

        self.saveItButton = ttk.Button(
            self.buttonFrame, text="Save!", command=self.saveImage)
        self.saveItButton.grid(row=0, column=1)

        # fourth row is for the generated image preview
        self.imageBox = Label(self.savePreviewFrame,
                              background=backgroundColor)
        self.imageBox.grid(row=0, column=0)

        # place a blank textbox at the bottom to look good
        baseImage = PIL.Image.open(emptyTextBoxPath)
        scaledImage = self.shrinkPreview(baseImage)
        self.placeholderTextbox = ImageTk.PhotoImage(scaledImage)
        self.imageBox.config(image=self.placeholderTextbox)

        # load game path file
        checkForStartupFile(self.root)

        # run the program
        root.mainloop()

    def shrinkPreview(self, previewImage):
        x, y = previewImage.size
        adjustedSize = (int(x/3), int(y/3))
        return previewImage.resize(adjustedSize)

    def createTextBox(self, text, portrait):
        baseImage = PIL.Image.open(emptyTextBoxPath)
        portraitTuple = profileOffsetDict[self.characterSelect.get()]
        # add desired portrait to the base image, before text to prevent the image from being on top of the text
        baseImage.paste(portrait, portraitTuple, portrait)
        # add the text to the image
        textLines = textwrap.wrap(text, width=maxLineLen)
        editedBox = ImageDraw.Draw(baseImage)

        # these values suck and need to be either adjusted, or determined dynamically
        baseX = textStartTuple[0]
        baseY = textStartTuple[1]

        # draw each line, TODO add a check for line length too, currently only 4 will really look good
        for line in textLines:
            editedBox.text((baseX, baseY), line,
                           font=isatFont, fill=(255, 255, 255))
            baseY += textLineHeight

        # draw the preview image
        scaledImage = self.shrinkPreview(baseImage)
        previewImage = ImageTk.PhotoImage(scaledImage)
        self.imageBox.config(image=previewImage)

        # prevent image from getting garbage collected
        self.imageBox.image = previewImage
        # store the current Image so it can be saved
        self.currentImage = baseImage

        # indicate that there is a new image available to be saved
        self.newImageAvailable = True

    def onCharacterSelect(self, event):
        currentlySelectedCharacter = self.characterSelect.get()
        self.profileSelect['values'] = sortedFaces[selectionToFaceDict[currentlySelectedCharacter]]

    def makeTheRestOfTheDamnOwl(self):
        file = self.profileSelect.get()
        if file == '':
            messagebox.showerror(
                title="Error", message="Stardust, you have to select a profile. It's basic stage direction")
            return
        fullPath = pathToFacesFiles + "\\" + file
        facePic = PIL.Image.open(fullPath)
        textToPrint = self.textEntryBox.get("1.0", "end-1c")
        self.createTextBox(textToPrint, facePic)

    def onProfileSelect(self, event):
        # get the full file name of the selected portrait
        file = self.profileSelect.get()
        fullPath = pathToFacesFiles + "\\" + file
        img = PIL.Image.open(fullPath)
        imgX, imgY = img.size
        resizedDimmensions = (int(imgX/2), int(imgY/2))
        img = img.resize(resizedDimmensions)
        prev = ImageTk.PhotoImage(img)
        self.preview.config(image=prev)
        self.preview.image = prev

    def saveImage(self):
        # ensure we have something to save
        if self.currentImage == '' or self.newImageAvailable == False:
            # empty save, or no change. Silently fail
            return

        savePath = filedialog.asksaveasfilename(title="Save textbox as", initialfile=defaultName,
                                                defaultextension=".png", filetypes=[("PNG", "*.png")])
        try:
            self.currentImage.save(savePath)
            self.newImageAvailable = False
        except ValueError:
            print("closed the filedialog without selecting something")


# what the fuck is organization just put everything in one file and one jank class!
root = tk.Tk()
root.title("ISAT Textbox Generator")

root.geometry("590x630")
# kick everything off
viewClass(root)
