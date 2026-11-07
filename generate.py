import asyncio, json, math, random, subprocess
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

BASE=Path(__file__).parent
OUT=BASE/"output"
OUT.mkdir(exist_ok=True)
story=json.loads((BASE/"stories.json").read_text(encoding="utf-8"))[date.today().toordinal()%len(json.loads((BASE/"stories.json").read_text(encoding="utf-8")))]
title, narration=story["title"],story["text"]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
large=ImageFont.truetype(fontfile,48)
medium=ImageFont.truetype(fontfile,35)
random.seed(date.today().isoformat())

# Six deliberately different illustrations; no external image API or fees.
def scene(i):
    im=Image.new("RGB",(720,1280),(9,13,23))
    d=ImageDraw.Draw(im)
    for y in range(1280):
        d.line((0,y,720,y),fill=(int(6+y/160),int(10+y/220),int(20+y/150)))
    if i==0: # apartment hallway
        for x in (40,160,560,680):
            d.line((x,200,360,1150),fill=(65,70,83),width=9)
        d.rectangle((240,310,480,920),outline=(112,111,113),width=15)
        d.ellipse((340,100,380,140),fill=(240,210,135))
    elif i==1: # note beneath door
        d.rectangle((80,180,640,990),outline=(90,85,88),width=18)
        d.polygon([(220,1000),(520,1000),(555,1140),(195,1140)],fill=(185,170,141))
        d.text((235,1045),"ISIGI ACMA",font=medium,fill=(105,28,30))
    elif i==2: # phone with caller ID
        d.rounded_rectangle((145,210,575,1020),radius=60,fill=(28,34,48),outline=(118,129,146),width=12)
        d.text((207,390),"GELEN ARAMA",font=medium,fill="white")
        d.text((190,510),"BENIM NUMARAM",font=medium,fill=(231,221,213))
        d.ellipse((300,760,420,880),fill=(45,145,93))
    elif i==3: # dark kitchen
        d.rectangle((80,600,640,970),fill=(25,29,37))
        d.rectangle((90,360,290,610),outline=(82,86,94),width=10)
        d.rectangle((430,360,630,610),outline=(82,86,94),width=10)
        d.ellipse((305,700,420,770),outline=(160,168,176),width=8)
        for x in (280,360,440): d.text((x,220),"?",font=large,fill=(178,48,50))
    elif i==4: # light switches on
        d.polygon([(340,190),(30,1080),(690,1080)],fill=(80,75,56))
        d.ellipse((290,140,430,270),fill=(240,219,155))
        d.rectangle((90,900,630,1100),fill=(23,22,27))
    else: # two shadows
        for x in (205,475):
            d.ellipse((x-70,350,x+70,510),fill=(3,4,8))
            d.polygon([(x-85,490),(x+85,490),(x+125,1120),(x-125,1120)],fill=(3,4,8))
        d.line((0,1160,720,1160),fill=(95,88,89),width=7)
    d.text((35,65),title,font=large,fill=(245,239,236),stroke_width=2,stroke_fill=(0,0,0))
    d.text((35,1170),f"SAHNE {i+1}/6",font=medium,fill=(220,210,210))
    im.save(OUT/f"scene{i}.png")

for i in range(6): scene(i)
async def synth():
    # Try a softer female narrator first; fallback to male if unavailable.
    for voice in ("tr-TR-EmelNeural","tr-TR-AhmetNeural"):
        try:
            await edge_tts.Communicate(narration,voice,rate="-12%",pitch="-3Hz").save(str(OUT/"voice.mp3"))
            return
        except Exception:
            pass
    raise RuntimeError("Turkish narration service unavailable")
asyncio.run(synth())
duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(OUT/"voice.mp3")]).decode())
segment=duration/6
(OUT/"slides.txt").write_text("".join(f"file 'scene{i}.png'\nduration {segment:.4f}\n" for i in range(6))+"file 'scene5.png'\n",encoding="utf-8")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(OUT/"slides.txt"),"-i",str(OUT/"voice.mp3"),"-vf","fps=30,scale=720:1280,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-b:a","128k","-shortest",str(OUT/"video.mp4")],check=True)
(OUT/"caption.txt").write_text(title+" | Kurgusal korku hikayesi #korku #gizem #shorts",encoding="utf-8")
print("Created:",OUT/"video.mp4")
