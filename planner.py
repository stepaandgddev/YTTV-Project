import json
import time
import datetime
import os

class SchedulePlanner:
    def __init__(self, schedule_file='plan.json', videos_file='videos.json'):
        self.schedule_file = schedule_file
        self.videos_file = videos_file
        self.schedule = self.load_schedule()
        self.videos = self.load_videos()
        
    def load_schedule(self):
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_videos(self):
        if os.path.exists(self.videos_file):
            with open(self.videos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_schedule(self):
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, indent=4, ensure_ascii=False)
    
    def save_videos(self):
        with open(self.videos_file, 'w', encoding='utf-8') as f:
            json.dump(self.videos, f, indent=4, ensure_ascii=False)
    
    def add_video(self, name, description, path, video_type='video'):
        video_id = str(len(self.videos))
        self.videos[video_id] = {
            "name": name,
            "description": description,
            "path": path,
            "type": video_type
        }
        self.save_videos()
        return video_id
    
    def add_schedule_item(self, date, time, video_id):
        if date not in self.schedule:
            self.schedule[date] = {}
        
        if video_id in self.videos:
            self.schedule[date][time] = {
                "name": self.videos[video_id]["name"],
                "description": self.videos[video_id]["description"],
                "videofile": self.videos[video_id]["path"],
                "video_id": video_id
            }
            self.save_schedule()
            return True
        return False
    
    def get_current_program(self):
        now = datetime.datetime.now()
        today = now.strftime("%d.%m.%Y")
        current_time = now.strftime("%H:%M")
        
        if today in self.schedule:
            for prog_time in sorted(self.schedule[today].keys()):
                if prog_time <= current_time:
                    return self.schedule[today][prog_time]
        return None
    
    def get_next_program(self):
        now = datetime.datetime.now()
        today = now.strftime("%d.%m.%Y")
        current_time = now.strftime("%H:%M")
        
        if today in self.schedule:
            for prog_time in sorted(self.schedule[today].keys()):
                if prog_time > current_time:
                    return self.schedule[today][prog_time]
        
        tomorrow = (now + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        if tomorrow in self.schedule:
            first_time = sorted(self.schedule[tomorrow].keys())[0]
            return self.schedule[tomorrow][first_time]
        
        return None
    
    def get_today_schedule(self):
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        if today in self.schedule:
            return self.schedule[today]
        return {}
    
    def delete_schedule_item(self, date, time):
        if date in self.schedule and time in self.schedule[date]:
            del self.schedule[date][time]
            if not self.schedule[date]:
                del self.schedule[date]
            self.save_schedule()
            return True
        return False
    
    def delete_video(self, video_id):
        if video_id in self.videos:
            del self.videos[video_id]
            new_videos = {}
            for i, (k, v) in enumerate(self.videos.items()):
                new_videos[str(i)] = v
            self.videos = new_videos
            self.save_videos()
            return True
        return False
    
    def get_video_by_path(self, path):
        for video_id, video in self.videos.items():
            if video['path'] == path:
                return video
        return None
    
    def create_weekly_schedule(self, start_date, program_list):
        start = datetime.datetime.strptime(start_date, "%d.%m.%Y")
        schedule = {}
        
        for i in range(7):
            date = (start + datetime.timedelta(days=i)).strftime("%d.%m.%Y")
            schedule[date] = {}
            
            for prog_time, video_id in program_list.items():
                schedule[date][prog_time] = {
                    "name": self.videos[video_id]["name"],
                    "description": self.videos[video_id]["description"],
                    "videofile": self.videos[video_id]["path"],
                    "video_id": video_id
                }
        
        return schedule
    
    def apply_weekly_schedule(self, start_date, program_list):
        weekly = self.create_weekly_schedule(start_date, program_list)
        self.schedule.update(weekly)
        self.save_schedule()
        return True

def CreatePlan(duration):
    planner = SchedulePlanner()
    
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    planner.add_schedule_item(today, "14:00", "0")
    planner.add_schedule_item(today, "15:00", "1")
    
    return planner