import asyncio, json, math, os, random, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT=Path(__file__).parent
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
stories=json.loads((ROOT/"stories.json").read_text(encoding="utf-8"))
from datetime import date
story=stories[date.today().toordinal()%len(stories)]
title,text=story["title"],story["text"]
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(font_path,55)
small=ImageFont.truetype(font_path,37)
random.seed(date.today().isoformat())
for i in range(6):
    im=Image.new("RGB",(720,1280),(5,8,18))
    d=ImageDraw.Draw(im)
    for y in range(1280):
        t=y/1280
        d.line([(0,y),(720,y)],fill=(int(7+13*t),int(10+4*t),int(21+8*t)))
    # Abstract ominous doorway and atmospheric lights
    x=180+i*7
    d.rectangle((x,230,x+360,1070),outline=(55,65,78),width=12)
    d.rectangle((x+20,250,x+340,1050),fill=(8,8,15))
    d.ellipse((x+285,620,x+302,637),fill=(185,30,30))
    d.text((45,75),title,font=font,fill="white",stroke_width=2,stroke_fill="black")
    d.text((45,1150),f"SAHNE {i+1}/6",font=small,fill=(195,195,205))
    im.save(OUT/f"scene{i}.png")

async def voice():
    await edge_tts.Communicate(text,"tr-TR-AhmetNeural",rate="-8%").save(str(OUT/"voice.mp3"))
asyncio.run(voice())
duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(OUT/"voice.mp3")]).decode().strip())
segment=duration/6
playlist=OUT/"slides.txt"
playlist.write_text("".join(f"file 'scene{i}.png'\nduration {segment:.4f}\n" for i in range(6))+"file 'scene5.png'\n",encoding="utf-8")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(playlist),"-i",str(OUT/"voice.mp3"),"-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-b:a","128k","-shortest",str(OUT/"video.mp4")],check=True)
(OUT/"caption.txt").write_text(title+" | Kurgusal korku hikâyesi #korku #gizem #shorts",encoding="utf-8")
print(f"Generated {OUT/'video.mp4'} ({duration:.1f}s)")
