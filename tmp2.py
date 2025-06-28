import sacn
import time
import pygame
import os
import threading
import array

# main.py uvicorn tmp2:app --reload    
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import re

# Start MPV with socket for control
#os.system("mpv  ./static/1.mp3 --no-video  --input-ipc-server=&")
time.sleep(1)

# Ask for playback time
#os.system("""echo '{ "command": ["get_property", "playback-time"] }' """)


def hhmmss_to_mmss(time_str):
    parts = time_str.split(":")
    if len(parts) == 3:
        return f"{parts[1]}:{parts[2]}"
    elif len(parts) == 2:
        return time_str
    else:
        return "00:00"  # fallback

# Example usage
original = "00:03:42"






app = FastAPI()

# Allow all CORS origins for development (configure securely in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/audio")
async def get_audio():
    file_path = "static/1.mp3"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=file_path)
    return {"error": "File not found"}


script = {}
"""
script["00:05"] = "1,"
script["00:20"] = "2,"
script["00:30"] = "2,1"
"""
@app.post("/play")
async def play_now(request: Request):
    data = await request.json()
    script.update(data)
   
    print(script) 
    
    process = subprocess.Popen(
        ["mpv", "./static/1.mp3", ""],  # example command
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        text=True,                 # shorthand for universal_newlines=True
        encoding='utf-8',          # force UTF-8 decoding
        errors='replace'           # avoid crash on weird characters
    )

    # Print each line as it comes
    for line in process.stdout:
        #converted = hhmmss_to_mmss(original)
    
        # Match the current time using regex
        match = re.search(r"A:\s*(\d{2}:\d{2}:\d{2})", line.strip())

        if match:
            current_time = match.group(1)

            current_time =hhmmss_to_mmss(current_time)
            print(current_time)  # ➜ 00:00:00

            if current_time in script:
                print(script[current_time])
                data = [0] * 5*7
                for i in range(1,5):
                    if str(i) in script[current_time]:
                    
                        num = i
                        if num>1:
                            num = (num-1)*7
                        else:
                            num -= 1
                        
                        data[num] = 255
                        data[num+1] = 255
                        
                        data[num+2] = 255
                        
                        data[num+3] =0
                        data[num+4] = 0
                        data[num+5] = 0
                        data[num+6] = 0
                        

                    else:
                        num = i
                        if num>1:
                            num = (num-1)*7
                        
                        data[num+1] = 0
                        
                        data[num+2] = 0
                        
                        data[num+3] = 0
                        
                        data[num+4] = 0

                        data[num+5] = 0
                        data[num+6] = 0
                        data[num+7] = 0

                print(data)

                sender[universe].dmx_data = data + [0] * (512 - 5*7)    
            time.sleep(0.1)

        else:
            print("No match")

    
    #pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
   # pygame.init()
    
    #pygame.mixer.music.load("static/1.mp3")
    # Schedule to run in 3 seconds


   # while pygame.mixer.music.get_busy():
      #  pygame.time.Clock().tick(10) 

   # play_music("static/1.mp3")
    #monitor_music()
    return {"success": "Played"}

#timer = threading.Timer(3.0, say_hello)
#timer.start()

# Create sACN sender
sender = sacn.sACNsender()
sender.start()

universe = 1
sender.activate_output(universe)
sender[universe].destination = "192.168.1.87"  # your eDMX1 IP

def format_time(seconds):
    minutes = (seconds // 1000) // 60
    seconds = (seconds // 1000) % 60
    formatted_time = f"{minutes:02}:{seconds:02}"
    mins = int(seconds // 60)
    secs = int(seconds % 60)#f"{mins:02}:{secs:02}"
    return formatted_time

def play_music(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

 
    pygame.mixer.music.play()


def monitor_music():
    
    #print(f"Now playing: {os.path.basename(file_path)}")
    start_time = time.time()

    try:
        while pygame.mixer.music.get_busy():
            
            current_time = pygame.mixer.music.get_pos()
     
        
            print(f"\r⏱️ {format_time(current_time)}", end="")
            
            if format_time(current_time) in script:
                print(script[format_time(current_time)])
                data = [0] * 5*7
                for i in range(1,5):
                    if str(i) in script[format_time(current_time)]:
                 
                        num = i
                        if num>1:
                            num = (num-1)*7
                        else:
                            num -= 1
                     
                        data[num] = 255
                        data[num+1] = 255
                        
                        data[num+2] = 255
                        
                        data[num+3] =0
                        data[num+4] = 0
                        data[num+5] = 0
                        data[num+6] = 0
                      

                    else:
                        num = i
                        if num>1:
                            num = (num-1)*7
                       
                        data[num+1] = 0
                        
                        data[num+2] = 0
                        
                        data[num+3] = 0
                        
                        data[num+4] = 0

                        data[num+5] = 0
                        data[num+6] = 0
                        data[num+7] = 0

                print(data)

                sender[universe].dmx_data = data + [0] * (512 - 5*7)    
            time.sleep(0.1)
         
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("\nStopped by user.")

# Replace with your own audio file



# Convert RGBW into proper order for SAN04 controller
def map_color(r, g, b, w=255):
    return [r, g, b, w]  # channel 1-4: R, G, B, W

# Prepare one fixture's full 7-channel DMX packet
def build_fixture_packet(r, g, b, w=255, strobe=0, function=150, speed=100):
    return map_color(r, g, b, w) + [strobe, function, speed]

# Example color steps using dimming and effects
color_sequence = [
    build_fixture_packet(255, 0, 0, 255, 0, 150, 50),   # Red + Gradient effect slow
    build_fixture_packet(0, 255, 0, 255, 30, 160, 100), # Green + Pulse effect medium
    build_fixture_packet(0, 0, 255, 255, 100, 200, 255),# Blue + Wave effect fast
    build_fixture_packet(0, 0, 0, 0, 0, 0, 0)           # Off
]




# Example usage:
# Creates a timer that ticks every 0.5s for 120 BPM
#timer = MusicTimer(bpm=120)
#timer.start()



def say_hello():

    
    thread = threading.Thread(target=monitor_music, daemon=True)
    thread.start()
   
  
   # dmx_data = [0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 255, 0, 150, 50]
    #sender[universe].dmx_data = dmx_data
  #  print(f"Sent DMX Data (first 14 channels): {dmx_data[:14]}")
   # timer = threading.Timer(3.0, say_hello)
   # timer.start()

