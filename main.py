import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import io
import json
import pprint
# load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)





#Render
def renderLatex(latex):
    fig = plt.figure(figsize=(4, 1))
    fig.patch.set_alpha(0)

    plt.axis("off")

    try:
        # Attempt to render LaTeX
        plt.text(0.5, 0.5, f"${latex}$",
                 fontsize=24, ha="center", va="center")
    except Exception as e:
        # If invalid LaTeX, show placeholder instead
        plt.text(0.5, 0.5, "Invalid LaTeX",
                 fontsize=16, ha="center", va="center")

    # Save figure to image
    buf = io.BytesIO()
    try:
        plt.savefig(buf, format="png", dpi=200, bbox_inches="tight", pad_inches=0.1)
    except Exception as e:
        # This catches parse errors that happen during save
        buf = io.BytesIO()  # empty buffer
        plt.close(fig)
        return Image.new("RGBA", (200, 50), (255, 255, 255, 0))

    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)


previewUpdateJob = None  

def updatePreview(event=None):
    global previewUpdateJob

    if previewUpdateJob is not None:
        root.after_cancel(previewUpdateJob)

    previewUpdateJob = root.after(500, renderPreview)

def renderPreview():
    global previewUpdateJob
    latex = latexText.get("1.0", tk.END).strip()
    if not latex:
        return

    image = renderLatex(latex)
    photo = ImageTk.PhotoImage(image)
    previewLabel.config(image=photo)
    previewLabel.image = photo  # prevent GC

    previewUpdateJob = None  # reset job


root = tk.Tk()
root.title("Texbind")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

latexText = tk.Text(root, font=("Consolas", 14), undo=True)
latexText.grid(row=0, column=0, sticky="nsew")
latexText.bind("<KeyRelease>", updatePreview)


def getNumberLength(line):
    print(line)
    idx = 0
    for c in line:
        if not c == " ":
            idx += 1
        else:
            return int(idx)
    return int(idx)
def getStart(line,params):
    count = 0
    for i in range(1,len(line)):
        if line[len(line)-i] == " " and i != 0 and line[len(line)-i-1] != " ":
            count += 1
        if i== len(line)-1 and line[len(line)-i] != " ":
            if count+1 == params:
                return -1
        if count == params:
            return len(line)-i
    
    return None
        
        
def indexToFull(idx):
    return str(latexText.index("insert")[0])+"."+str(idx)

def keybind(event,command,params,spacer=None):
    print(command,params,spacer)

    if latexText.tag_ranges("sel"):
        
        first = int(latexText.index("sel.first").split(".")[1])
        last = int(latexText.index("sel.last").split(".")[1])
    else:
        if getStart(latexText.get(indexToFull(0), latexText.index("insert")),params) == None:
            return 
        first = getStart(latexText.get(indexToFull(0), latexText.index("insert")),params)+1
        last = int(latexText.index("insert").split(".")[1])
    latexText.insert(indexToFull(first),command)
    first += len(command)
    last += len(command)
    
    print(first,last)
    for i in range(params):
        latexText.insert(indexToFull(first),r"{")  
        first += 1
        last += 1
        line = latexText.get(indexToFull(first), indexToFull(last))
        if line[0] == " ":
            line = line[1:]
            latexText.delete(indexToFull(first))
            first += 1
            last += 1
        numLength = getNumberLength(line)
        first += numLength
        last +=  numLength
        latexText.insert(indexToFull(first),r"}")
        first += 1
        last += 1
        if spacer and not i+1 == params:
            latexText.insert(indexToFull(first),spacer)
            first += 1
            last += 1
    latexText.mark_set("insert", indexToFull(last))



for key, value in config["keybinds"].items():
    root.bind(key, lambda event, v=value: keybind(event, v["command"], v["params"], v["spacer"]))

def redo(event=None):
    try:
        latexText.edit_redo()
    except tk.TclError:
        pass
    return "break"

latexText.bind("<Control-Shift-z>", redo)

def paste(event=None):
    try:
        latexText.event_generate("<<Paste>>")
    except tk.TclError:
        pass
    return "break"

latexText.bind("<Control-v>", paste)

def copy(event=None):
    latexText.event_generate("<<Copy>>")
    return "break"

latexText.bind("<Control-c>", copy)


previewLabel = tk.Label(root, bg="white")
previewLabel.grid(row=0, column=1, sticky="nsew")

latexText.insert(
    "1.0",
    r"123 456 789"
)


root.update_idletasks()
root.deiconify()
root.state("normal")

updatePreview()
root.mainloop()