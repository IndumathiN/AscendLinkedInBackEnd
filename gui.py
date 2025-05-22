import tkinter as tk
import tkinter.messagebox

import os
import sys
import asyncio
import traceback
import subprocess
from linkedinLogin import run_linkedin_bot  # Import your function


from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=api_key)

# Create the main window
root = tk.Tk()
root.title("My GUI")

# Create a label
label = tk.Label(root, text="Hello, GUI!")
label.pack()

# Create a button
def button_clicked():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(os.system("python linkedinLogin.py ")  )
    tkinter.messagebox.showinfo("Info", "Button Clicked!")

button = tk.Button(root, text="Click Me", command=button_clicked)
button.pack()

# Run the GUI
root.mainloop()