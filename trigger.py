import os
import time
import threading
import tkinter as tk
from Capturevideotoimage import VideoConverter
from SendGmail import SendGmail
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# /mnt/d/my_code/CCU-project-ActionAI

class GUI():
    def __init__(self):
        print('Initialize ...')
        self.root = tk.Tk()
        self.root.title('Overwork Detection')
        self.root.resizable(False, False)
        self.root.geometry('500x250')
        self.DirPath = os.path.abspath(os.getcwd())
        self.AWSAccount = str()
        self.AWSPassword = str()
        self.CurrentWorkTime = 0
        self.CurrentVideoTime = 0
        self.WorkTimeStr = StringVar()
        self.VideoTimeStr = StringVar()
        self.CurrentDir = StringVar()
        self.CurrentVideo = StringVar()
        self.WorkTimeStr.set('Current Work Time = ' + self.SecondToStr(self.CurrentWorkTime))
        self.VideoTimeStr.set('Current Video Time = ' + self.SecondToStr(self.CurrentVideoTime))
        self.CurrentDir.set('Current Directory: ' + self.DirPath)
        self.CurrentVideo.set('Current Predice Video: ')
        
        self.PredictThread = threading.Thread(target=self.search_new_file)
        self.open_button = ttk.Button(
            self.root,
            text = 'Open a Directory',
            width = 20,
            command=self.select_dir
        )
        self.run_button = ttk.Button(
            self.root,
            text = 'Run',
            width = 20,
            command=self.run_predict_thread
        )
        self.edit_button = ttk.Button(
            self.root,
            text = 'Edit Receiver Email',
            width=20,
            command=self.edit_file
        )
        self.login_button = ttk.Button(
            self.root,
            text = 'Login AWS Email',
            width=20,
            command=self.login_AWS
        )
        self.send_button = ttk.Button(
            self.root,
            text = 'Send Email',
            width=20,
            command=self.send_email
        )

        self.WorkTimeText = ttk.Label(self.root, textvariable = self.WorkTimeStr)
        self.VideoTimeText = ttk.Label(self.root, textvariable = self.VideoTimeStr)
        self.CurrentDirText = ttk.Label(self.root, textvariable = self.CurrentDir)
        self.CurrentVideoText = ttk.Label(self.root, textvariable = self.CurrentVideo)
        self.open_button.pack(expand = False)
        self.edit_button.pack(expand = False)
        self.send_button.pack(expand = False)
        self.login_button.pack(expand = False)
        self.run_button.pack(expand = False)
        self.WorkTimeText.pack(expand = False)
        self.VideoTimeText.pack(expand = False)
        self.CurrentDirText.pack(expand = False)
        self.CurrentVideoText.pack(expand = False)

    def edit_file(self):
        top = Tk()
        top.geometry("500x500")
        EditWindow(top)
        top.mainloop()

    def SecondToStr(self, second):
        Hour = second // 3600
        Minute = second // 60 - Hour * 60
        Second = second % 60
        if Hour != 0:
            return str(Hour) + 'h ' + str(Minute) + 'm ' + str(Second) + 's'
        elif Minute != 0:
            return str(Minute) + 'm ' + str(Second) + 's'
        else:
            return str(Second) + 's'

    def add_time(self, VideoTime, WorkTime):
        self.CurrentVideoTime = self.CurrentVideoTime + VideoTime
        self.CurrentWorkTime = self.CurrentWorkTime + WorkTime
        self.WorkTimeStr.set('Current Work Time = ' + self.SecondToStr(self.CurrentWorkTime))
        self.VideoTimeStr.set('Current Video Time = ' + self.SecondToStr(self.CurrentVideoTime))

    def search_new_file(self):
        print('Starting to load Video ...')
        CurrentThread = threading.currentThread()
        while getattr(CurrentThread, "do_run", True):
            Files = os.listdir(self.DirPath)
            for file in Files:
                if (not file.startswith('(done)')) and file.endswith('.mp4'):
                    FilePath = self.DirPath + '/' + file
                    self.CurrentVideo.set('Current Predict Video: ' + str(file))
                    print(FilePath)
                    video = VideoConverter()
                    VideoTime, WorkTime = video.transform_and_predict(FilePath)

                    self.add_time(VideoTime, WorkTime)
                    print('----------------')
                    print('[VideoTime]', VideoTime)
                    print('[WorkTime]', WorkTime)
                    print('----------------')
                    os.rename(FilePath, self.DirPath + '/(done)' + file)
                    self.CurrentVideo.set('Current Predict Video: ')

            time.sleep(1)

    def select_dir(self):
        DirName = filedialog.askdirectory(
            title = 'Open a directory',
            initialdir = self.DirPath
        )
        if DirName != '':
            self.DirPath = DirName
            self.CurrentDir.set('Current Directory: ' + self.DirPath)

    def run_predict_thread(self):
        if not self.PredictThread.is_alive():
            self.PredictThread.start()

    def send_email(self):
        Receivers = open("EmailList.txt").readlines()
        for Recv in Receivers:
            print("Send to", Recv)
            SG = SendGmail(self.AWSAccount, self.AWSPassword, Recv)
            Failed = SG.send_message()
            print("Failed =", Failed)

    def login_AWS(self):
        self.CreateLoginWindow()

    def login(self):
        self.AWSAccount = self.account.get()
        self.AWSPassword = self.password.get()
        print(self.AWSAccount, self.AWSPassword)
        self.LoginWindow.destroy()

    def CreateLoginWindow(self):
        # ref: https://stackoverflow.com/questions/55560127/how-to-close-more-than-one-window-with-a-single-click
        self.LoginWindow = tk.Toplevel()
        self.LoginWindow.title("Wellcome to Login")
        self.LoginWindow.geometry('400x300')
        self.account = StringVar()
        self.account.set('xxxx@gmail.com')
        self.password = StringVar()
        ttk.Label(self.LoginWindow, text = 'user:', font = ('Arial', 14)).place(x = 50, y = 85)
        ttk.Label(self.LoginWindow, text = 'password:', font = ('Arial', 14)).place(x = 50, y = 115)
        ttk.Entry(self.LoginWindow, textvariable = self.account, font = ('Arial', 14)).place(x = 150, y = 85)
        ttk.Entry(self.LoginWindow, textvariable = self.password, font = ('Arial', 14), show='*').place(x = 150, y = 115)
        ttk.Button(self.LoginWindow, text = 'Login', command = self.login).place(x = 120, y = 170)
    
    def start(self):
        print('Starting GUI ... ')

        # run the application
        self.root.mainloop()
        self.PredictThread.do_run = False
        print('Finish')


class EditWindow(Frame):
    # http://hk.uwenku.com/question/p-hliiusca-tv.html
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Edit Eamil List")
        self.pack(fill=BOTH, expand=1)
        self.save_button = ttk.Button(
            self.master,
            text = 'Save',
            command=self.save_file
        )
        self.save_button.pack(expand=False)
        self.file_save = "EmailList.txt"

        self.text = Text(self.master, height=200, width=200)
        self.text.pack(side=LEFT, fill=Y, expand=True)

        self.scrollbar = Scrollbar(self.master, orient="vertical")
        self.scrollbar.config(command=self.text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y, expand=True)

        # change all occurances of self.listNodes to self.text
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.open_file()

    def open_file(self):
        self.text.delete("1.0", END)
        if os.path.isfile(self.file_save):
            with open(self.file_save, "r") as file:
                content = file.read()
                self.text.insert(END, content)

    def save_file(self):
        with open(self.file_save, 'w') as file:
            input = self.text.get("1.0", END)
            input = input[:-1]  # input.pop_back
            print(input, file=file, end='')

if __name__ == '__main__':
    app = GUI()
    app.start()