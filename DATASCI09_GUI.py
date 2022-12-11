import glob
import os
import shutil
import subprocess
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk

root = tk.Tk()
root.resizable(False, False)
apps = []
import shutil

#Title Bar
root.title('DATA_SCIENCE_09_CARLOS_LUMACAD_MINANO_REODICA')

def addBloodSmearImage():
    for widget in frame.winfo_children():
        widget.destroy()     
    filename = filedialog.askopenfilename(initialdir="Dataset/", title="Select File",
                                          filetypes=(("pictures", "*.jpg"), ("executables", "*.exe")))
    
    # Delete previous images
    imglist = glob.glob("Results/*.jpg", recursive=False)
    for img in imglist:
        os.remove(img)
        
    # Delete previous cropped
    top = "Results/Cropped"
    if os.path.exists(top):
        shutil.rmtree(top, ignore_errors=True)

    os.makedirs(top)
    
    # Save image
    line = "Results/"+ filename[filename.rfind("-master/")+8:filename.rfind("/img")]+filename[filename.rfind('-'):]
    line2 = "Results/" + filename[filename.rfind("/"):]
    shutil.copyfile(filename, line)
    shutil.copyfile(filename, line2)
    
    
    with open("Test_detect.txt", 'w', encoding = 'utf-8') as f:
        f.write(line+'\n')
    
    # Display Image
    img_resized = Image.open(line).resize((972, 648))
    img = ImageTk.PhotoImage(img_resized)
    panel = Label(frame, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
    root.mainloop()

def preprocessImage():
    # Input Image 
    with open('Test_detect.txt') as f:
        # line = f.readlines()
        temp = f.read().splitlines()
        line = temp[0][temp[0].rfind('/'):]
    
    for child in frame.winfo_children():
        child.destroy()  
        
    if(not "_PROCESSED" in line):
        image = cv2.imread(temp[0])
        
        #Laplacian/Sharpening
        kernel = np.array([[0, -1, 0],
                        [-1, 5,-1],
                        [0, -1, 0]])
        image_sharp = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

        #Histogram Equalization 
        lab_img = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_img)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(l)
        updated_lab_img2 = cv2.merge((clahe_img,a,b))
        CLAHE_img = cv2.cvtColor(updated_lab_img2, cv2.COLOR_LAB2BGR)
        
        #Saving Images                         
        image_path = "Results" + line.replace(".jpg","")+"_PROCESSED.jpg"
        cv2.imwrite(image_path, CLAHE_img)
    
        with open("Test_detect.txt", 'w', encoding = 'utf-8') as f:
            f.write("Program/" + image_path+ '\n')
    
        #Replace IMG and Rerender GUI
        img_resized = Image.open(image_path).resize((972, 648))
        img = ImageTk.PhotoImage(img_resized)
        panel = Label(frame, image = img)
        panel.pack(side = "bottom", fill = "both", expand = "yes")
        root.mainloop()
    else:
        image_path = "Results" + line
        img_resized = Image.open(image_path).resize((972, 648))
        img = ImageTk.PhotoImage(img_resized)
        panel = Label(frame, image = img)
        panel.pack(side = "bottom", fill = "both", expand = "yes")
        root.mainloop()

    
def detectInfectedCells():
    for app in apps:
        os.startfile(app)

    #Input Preprocessed Image
    with open('Test_detect.txt') as f:
        # line = f.readlines()
        temp = f.read().splitlines()
        line = temp[0][temp[0].rfind('/'):]
    
    changed = line[:line.rfind(".")] + "_DETECTED.jpg"
    
    #If the image haven't undergone Malaria detection
    if not os.path.exists("Results"+changed):
        #CMDLine code to run the YOLOv4 model
        subprocess.run("darknet detector test Program/Test_detect.data Program/Cfg/yolov4-malaria.cfg Program/Weights/yolov4-malaria.weights -ext_output -dont_show -out Program/Results/Yolov4_result.json < Program/Test_detect.txt", shell=True, cwd="C:\darknet-master")
        #Java program to draw the bounding box coordinates for each detected infected cell so that it may be displayed in the GUI
        subprocess.run("java draw_predicted", shell=True)
        #Java program to generate the cropped image for each detected infected cell, in preparation for further classification
        subprocess.run("java crop_images_yolo", shell=True)

        #Save directory information of the Cropped IMGS to txt file
        imglist = glob.glob("Results/Cropped/*.jpg", recursive=False)
        with open("Test_classify.txt", 'w', encoding = 'utf-8') as f:
            for img in imglist:
                img = img.replace("\\", "/")
                f.write("Program/"+img+'\n')
            f.write("\n\n\n\n")
        
    #Replace IMG and Rerender GUI
    for child in frame.winfo_children():
        child.destroy()  
    img_resized = Image.open("Results"+changed).resize((972, 648))
    img = ImageTk.PhotoImage(img_resized)
    panel = Label(frame, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
    root.mainloop()

def classifyLifeCycle():
    #Input Cropped Images
    with open('Test_detect.txt') as f:
        # line = f.readlines()
        temp = f.read().splitlines()
        line = temp[0][temp[0].rfind('/'):]
    
    #If the detected image haven't undergone Life-cycle stage classification
    if not os.path.exists("Results"+line.replace(".jpg","")+"_CYCLE.jpg"):
        #CMDLine code to run the Darknet53 model for Life-cycle Stage classification
        subprocess.run("darknet classifier test Program/Test_cycle.data Program/Cfg/Darknet53_Cyclev2.cfg Program/Weights/Darknet53_Cycle.weights -ext_output -dont_show -out < Program/Test_classify.txt > Program/Results/Cycle_result.txt", shell=True, cwd="C:\darknet-master")
        #Java program to draw the bounding box coordinates for each detected infected cell, labelled according to their predicted Life-cycle stage classification
        subprocess.run("java draw_LCS")
        
    #Replace IMG and Rerender GUI
    for child in frame.winfo_children():
        child.destroy()  
    img_resized = Image.open("Results"+line.replace(".jpg","")+"_CYCLE.jpg").resize((972, 648))
    img = ImageTk.PhotoImage(img_resized)
    panel = Label(frame, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
    root.mainloop()
    
def classifyParasiteType():
    #Input Cropped Images
    with open('Test_detect.txt') as f:
        # line = f.readlines()
        temp = f.read().splitlines()
        line = temp[0][temp[0].rfind('/'):]
    
    #If the detected image haven't undergone Parasite Type classification
    if not os.path.exists("Results"+line.replace(".jpg","")+"_TYPE.jpg"):
        #CMDLine code to run the Darknet53 model for Parasite Type classification
        subprocess.run("darknet classifier test Program/Test_type.data Program/Cfg/Darknet53_Type.cfg Program/Weights/Darknet53_Type.weights -ext_output -dont_show -out < Program/Test_classify.txt > Program/Results/Type_result.txt", shell=True, cwd="C:\darknet-master")
        #Java program to draw the bounding box coordinates for each detected infected cell, labelled according to their predicted Parasite type classification
        subprocess.run("java draw_PT")
    
    #Replace IMG and Rerender GUI
    for child in frame.winfo_children():
        child.destroy()  
    img_resized = Image.open("Results"+line.replace(".jpg","")+"_TYPE.jpg").resize((972, 648))
    img = ImageTk.PhotoImage(img_resized)
    panel = Label(frame, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
    root.mainloop()
    
#CANVAS canvas = tk.Canvas(root, height=500, width=1000, bg="#D7A8C4") create_text(500, 50,
canvas = tk.Canvas(root, height=900, width=1350, bg="#D7A8C4")
canvas.pack()

canvas.create_text(670, 50, text="Detection and Classification of Plasmodium Parasites using Darknet with YOLO", fill="black", font=('Times 20 bold'))
canvas.pack()

canvas.create_text(670, 80, text="Carlos, Lumacad, Minano, Reodica. 2022", fill="black", font=('Times 20 italic bold'))
canvas.pack()

#FRAMES
frame = tk.Frame(root, bg="white")
frame.place(width=972, height=630, x=189, y=200)

#Buttons
openFile = tk.Button(root, text="Open File", padx=10, pady=5, fg="white", bg="#9E6999", command = addBloodSmearImage)
openFile.pack()

preprocess = tk.Button(root, text="Preprocess Image", padx=10, pady=5, fg="white", bg="#9E6999", command = preprocessImage)
preprocess.pack()

detect = tk.Button(root, text="Predict Image", padx=10, pady=5, fg="white", bg="#9E6999", command = detectInfectedCells)
detect.pack()

classifyLCS = tk.Button(root, text="Classify Life Cycle Stage", padx=10, pady=5, fg="white", bg="#9E6999", command = classifyLifeCycle)
classifyLCS.pack()

classifyType = tk.Button(root, text="Classify Parasite Type", padx=10, pady=5, fg="white", bg="#9E6999", command = classifyParasiteType)
classifyType.pack()


# Set the position of button to coordinate (100, 20)
openFile.place(x=290, y=120)
preprocess.place(x=400, y=120)
detect.place(x=565, y=120)
classifyLCS.place(x=705, y=120)
classifyType.place(x=910, y=120)


root.mainloop()

