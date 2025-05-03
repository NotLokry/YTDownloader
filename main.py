import customtkinter
from pytubefix import YouTube
from PIL import Image
import io
import requests
import subprocess
import os

customtkinter.set_appearance_mode("System") 

app = customtkinter.CTk(fg_color="#111111")
app.geometry("600x400")
app.resizable(False, False)
app.title("YouTube Downloader")

red_theme_color = "#FF0000"
black_theme_color1 = "#282828"
black_theme_color2 = "#1c1c1c"
radio_var = customtkinter.IntVar(value=0)
fF_size = (100,.25,.65)
fT_size = (350,.08,.22)
input_c = .25
search_c = .65
streams = []

def transition_frame(boole):
    global input_c, search_c
    if boole == False and frame.cget("height") != fF_size[0]:
        frame.video_select_frame.place_forget()
        frame.audio_select_frame.place_forget()
        frame.thumbnail.place_forget()
        frame.download_button.place_forget()
        input_c+=(fF_size[1]-fT_size[1])/10
        search_c+=(fF_size[2]-fT_size[2])/10
        height = frame.cget("height")-(fT_size[0]-fF_size[0])/10
    elif boole == True and frame.cget("height") != fT_size[0]:
        input_c-=(fF_size[1]-fT_size[1])/10
        search_c-=(fF_size[2]-fT_size[2])/10
        height = frame.cget("height")+(fT_size[0]-fF_size[0])/10
        if height == fT_size[0]:
            frame.video_select_frame.place(relx=0.175, rely=0.56, anchor=customtkinter.CENTER)
            frame.audio_select_frame.place(relx=0.825, rely=0.56, anchor=customtkinter.CENTER)
            frame.thumbnail.place(relx=0.5, rely=0.46, anchor=customtkinter.CENTER)
            frame.download_button.place(relx=0.5, rely=0.85, anchor=customtkinter.CENTER)
    else: return

    frame.configure(height=height)
    frame.input_url.place(rely=input_c)
    frame.search.place(rely=search_c)
    app.after(10, lambda: transition_frame(boole))

def add_options(video_options,audio_options):
    i1 = 0
    i2 = 0
    for stream in video_options:
        radiobutton = customtkinter.CTkRadioButton(frame.video_select_frame,text=stream.resolution,variable=radio_var,value=int(stream.itag),command=radiobutton_event,fg_color=black_theme_color2,hover_color=black_theme_color1,border_color=red_theme_color,hover=True, font=("Arial", 16,"bold"))
        radiobutton.grid(row=i1, column=0, padx=20, pady=5)
        i1+=1
    for stream in audio_options:    
        radiobutton = customtkinter.CTkRadioButton(frame.audio_select_frame, text=stream.abr, variable=radio_var, value=int(stream.itag), command=radiobutton_event, fg_color=black_theme_color2, hover_color=black_theme_color1, border_color=red_theme_color, hover=True, font=("Arial", 16,"bold"))
        radiobutton.grid(row=i2, column=0, padx=20, pady=5)
        i2+=1

def load_image(url):
    response = requests.get(url)
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    tk_image = customtkinter.CTkImage(light_image=image, size=(156, 110))
    frame.thumbnail.configure(image=tk_image)

def download():
    global streams
    itag = radio_var.get()
    stream = next((s for s in streams if int(s.itag) == itag), None)
    if stream:
        display_error_message("Downloading")
        print("Downloading:", stream.title)
        title = stream.title.replace('"', '').replace("'", "").replace(":", "").strip()
        if stream.includes_audio_track == False:
            stream.download()
            addAudio = [s for s in streams if s.mime_type =="audio/mp4"]
            if len(addAudio) != 0:
                addAudio[len(addAudio)-1].download()
                ffmpeg_path = './ffmpeg.exe'
                command = [
                    ffmpeg_path,
                    "-i", title+".mp4",
                    "-i", title+".m4a",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-shortest",
                    "-y",
                    f"output.mp4"
                ]
                subprocess.run(command, check=True)
            os.remove(title+".mp4")
            os.remove(title+".m4a")
        else:
            stream.download()
            ffmpeg_path = './ffmpeg.exe'
            command = [
                ffmpeg_path,
                "-i", title+".m4a",
                "-acodec", "libmp3lame",
                "-ab", "256k",
                "-y","output.mp3"
            ]
            subprocess.run(command, check=True)
            os.remove(title+".m4a")
        print("Download complete!")
        display_error_message("Download complete!")
    else:
        display_error_message("No option selected")
        print("No option selected")

def search():
    global streams
    url = frame.input_url.get()
    try:
        yt = YouTube(url)
        load_image(yt.thumbnail_url)
        transition_frame(True)
        video_options = yt.streams.filter(subtype='mp4',only_video=True)
        if len([stream for stream in video_options if int(stream.itag) > 300]) != 0:
            video_options = [stream for stream in video_options if int(stream.itag) > 300 and int(stream.itag) < 690]

        audio_options = yt.streams.filter(subtype='mp4',only_audio=True)
        streams = list(video_options) + list(audio_options)
        print(video_options)
        app.after(10,lambda: add_options(video_options,audio_options))
    except Exception as e:
        display_error_message("Invalid URL or video not found.")
        print("Error:", e)

def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

def display_error_message(text):
    error_message = customtkinter.CTkLabel(app, text=text, font=("Arial", 16,"bold"), text_color="#FFFFFF", fg_color="transparent")
    error_message.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
    app.after(2000, lambda: error_message.place_forget())

class InputAndSearchFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.input_url = customtkinter.CTkEntry(self,placeholder_text="Enter YouTube URL", text_color="white",width=400,border_color=red_theme_color,font=("Arial", 16,"bold"),border_width=2,corner_radius=10)
        self.input_url.place(relx=0.5, rely=0.25, anchor=customtkinter.CENTER)
        self.input_url.bind("<KeyRelease>", lambda event: transition_frame(False))

        self.search = customtkinter.CTkButton(self, text="Search", command=search,fg_color=red_theme_color,hover_color=black_theme_color1,border_color=red_theme_color,hover=True,font=("Arial", 16,"bold"),border_width=2,corner_radius=10)
        self.search.place(relx=0.5, rely=0.65, anchor=customtkinter.CENTER)

        self.thumbnail = customtkinter.CTkLabel(self, text="")

        self.video_select_frame = SelectFrame(master=self,fg_color=black_theme_color2,label_fg_color="transparent",width=125, height=20,label_text="Video",label_font=("Arial", 16,"bold"),corner_radius=15)
        self.audio_select_frame = SelectFrame(master=self,fg_color=black_theme_color2,label_fg_color="transparent",width=125, height=20,label_text="Audio",label_font=("Arial", 16,"bold"),corner_radius=15)

        self.download_button = customtkinter.CTkButton(self, text="Download", command=download,fg_color=red_theme_color,hover_color=black_theme_color1,border_color=red_theme_color,hover=True,font=("Arial", 16,"bold"),border_width=2,corner_radius=10)

class SelectFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label = customtkinter.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=20)

frame = InputAndSearchFrame(master=app, fg_color=black_theme_color1, width=500, height=100)
frame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

app.mainloop()