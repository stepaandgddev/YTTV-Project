import os
import time
import obsws_python as obs
import subprocess
import json
import datetime
import random
from planner import SchedulePlanner

PORT = 4455
PASSWORD = ""
VIDEO_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vid")
SOURCE_NAME = "Media"
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080

def get_video_info(video_path):
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                return {
                    'width': int(stream.get('width', 0)),
                    'height': int(stream.get('height', 0)),
                    'duration': float(stream.get('duration', 0))
                }
        return None
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def play_video(cl, video_path, scene_name):
    video_info = get_video_info(video_path)
    
    if video_info:
        duration_sec = video_info['duration']
        original_width = video_info['width']
        original_height = video_info['height']
        
        scale_x = TARGET_WIDTH / original_width
        scale_y = TARGET_HEIGHT / original_height
        
        cl.set_input_settings(
            name=SOURCE_NAME,
            settings={
                "local_file": video_path,
                "looping": False,
                "restart_on_activate": True
            },
            overlay=True
        )
        
        time.sleep(0.5)
        
        try:
            response = cl.get_scene_item_id(scene_name=scene_name, source_name=SOURCE_NAME)
            item_id = response.scene_item_id
            
            cl.set_scene_item_transform(
                scene_name=scene_name,
                item_id=item_id,
                transform={
                    "positionX": 0,
                    "positionY": 0,
                    "scaleX": scale_x,
                    "scaleY": scale_y
                }
            )
            
            print(f"Size set: {TARGET_WIDTH}x{TARGET_HEIGHT} (scale: {scale_x:.2f}x{scale_y:.2f})")
                
        except Exception as e:
            print(f"Error setting transform: {e}")
    else:
        print("Could not determine video size")
        duration_sec = 60
        cl.set_input_settings(
            name=SOURCE_NAME,
            settings={
                "local_file": video_path,
                "looping": False,
                "restart_on_activate": True
            },
            overlay=True
        )
    
    return duration_sec

def get_videos_from_folder():
    return [os.path.join(VIDEO_FOLDER, f) for f in os.listdir(VIDEO_FOLDER) 
            if f.endswith(('.mp4', '.mkv'))]

def generate_schedule(planner, videos):
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.datetime.now()
    
    shuffled_videos = videos.copy()
    random.shuffle(shuffled_videos)
    
    planner.schedule[today] = {}
    
    current_minutes = current_time.hour * 60 + current_time.minute
    
    if current_time.minute > 30:
        current_minutes = ((current_time.hour + 1) % 24) * 60
    
    video_index = 0
    total_minutes = 0
    
    while total_minutes < 1440:
        if video_index >= len(shuffled_videos):
            random.shuffle(shuffled_videos)
            video_index = 0
        
        video_path = shuffled_videos[video_index]
        video_name = os.path.basename(video_path)
        
        video_info = get_video_info(video_path)
        if video_info:
            duration_minutes = video_info['duration'] / 60
        else:
            duration_minutes = 1
        
        total_minutes += duration_minutes
        
        hours = int((current_minutes + total_minutes) // 60) % 24
        minutes = int((current_minutes + total_minutes) % 60)
        
        time_str = f"{hours:02d}:{minutes:02d}"
        
        video_id = None
        for vid, data in planner.videos.items():
            if data['path'] == video_name:
                video_id = vid
                break
        
        if video_id is None:
            video_id = planner.add_video(
                name=video_name.replace('.mp4', '').replace('.mkv', ''),
                description="Auto added video",
                path=video_name
            )
        
        planner.add_schedule_item(today, time_str, video_id)
        
        video_index += 1
    
    planner.save_schedule()
    print(f"Created continuous schedule for the whole day from {len(shuffled_videos)} videos")

def ensure_schedule_exists(planner, videos):
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    
    if today not in planner.schedule or not planner.schedule[today]:
        print("Schedule missing, creating new one...")
        generate_schedule(planner, videos)
        return True
    
    return True

def get_current_playing(planner, videos):
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    if today in planner.schedule:
        sorted_times = sorted(planner.schedule[today].keys())
        for i, time_slot in enumerate(sorted_times):
            if time_slot <= current_time:
                if i + 1 < len(sorted_times):
                    next_time = sorted_times[i + 1]
                else:
                    next_time = None
                
                video_file = planner.schedule[today][time_slot]['videofile']
                for v in videos:
                    if os.path.basename(v) == video_file:
                        return v, time_slot, next_time
    
    return None, None, None

videos = get_videos_from_folder()

if not videos:
    print("Video files not found!")
    exit()

cl = obs.ReqClient(host='localhost', port=PORT, password=PASSWORD, timeout=3)

print("Successfully connected to OBS. Starting broadcast automation...")

cl.start_stream()

planner = SchedulePlanner()

today = datetime.datetime.now().strftime("%d.%m.%Y")
ensure_schedule_exists(planner, videos)

RestartVideo = 'OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART'

current_video, current_time, next_time = get_current_playing(planner, videos)

if current_video:
    print(f"Currently should play: {os.path.basename(current_video)} (start at {current_time})")
    if next_time:
        print(f"Next video at {next_time}")
else:
    print("No active programs in schedule")
    current_video = videos[0]

video_index = 0
for i, v in enumerate(videos):
    if os.path.basename(v) == os.path.basename(current_video):
        video_index = i
        break

last_day = today
last_played = None

try:
    while True:
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        
        if today != last_day:
            print(f"New day: {today}")
            ensure_schedule_exists(planner, videos)
            last_day = today
        
        ensure_schedule_exists(planner, videos)
        
        current_video, current_time, next_time = get_current_playing(planner, videos)
        
        if current_video:
            video_name = os.path.basename(current_video)
            if video_name != last_played:
                print(f"\nCurrently playing: {video_name} (start at {current_time})")
                if next_time:
                    print(f"Next video at {next_time}")
                last_played = video_name
            
            current_scene = cl.get_current_program_scene()
            scene_name = current_scene.current_program_scene_name
            
            cl.set_input_settings(
                name=SOURCE_NAME,
                settings={
                    "local_file": current_video,
                    "looping": False,
                    "restart_on_activate": True
                },
                overlay=True
            )
            
            time.sleep(1)
            cl.trigger_media_input_action(SOURCE_NAME, RestartVideo)
            
            video_info = get_video_info(current_video)
            if video_info:
                duration_sec = video_info['duration']
            else:
                duration_sec = 60
            
            print(f"Duration: {duration_sec:.2f} sec.")
            
            if next_time:
                next_time_obj = datetime.datetime.strptime(next_time, "%H:%M")
                now = datetime.datetime.now()
                next_time_full = now.replace(hour=next_time_obj.hour, minute=next_time_obj.minute, second=0, microsecond=0)
                
                if next_time_full < now:
                    next_time_full = next_time_full + datetime.timedelta(days=1)
                
                wait_seconds = (next_time_full - now).total_seconds()
                
                if wait_seconds > 0 and wait_seconds < 3600:
                    print(f"Waiting until next video ({int(wait_seconds)} sec)...")
                    time.sleep(wait_seconds)
                else:
                    time.sleep(duration_sec)
            else:
                time.sleep(duration_sec)
        else:
            print("No active programs, waiting...")
            time.sleep(60)

except KeyboardInterrupt:
    print("\nAutomation stopped by user.")
    cl.stop_stream()