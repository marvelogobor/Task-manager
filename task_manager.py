from datetime import datetime, time, date
import json
import os
import tempfile

class Task_manager:
    def __init__(self, cache_file="task_manager.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = os.path.join(base_dir, tempfile.gettempprefix()) 
        os.makedirs(self.cache_dir, exist_ok=True)

        self.cache_file = os.path.join(self.cache_dir, cache_file)

        self.task = self._load_tasks()
        self.next_task = (
            max((t.get('task_id', 0) for t in self.task.values()), default=0) + 1
        )


    def _load_tasks(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    return {int(k): v for k, v in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_tasks(self):
        with open(self.cache_file, 'w') as f:
            json.dump({str(k): v for k, v in self.task.items()}, f, indent=2)

    def add_task(self, name, priority=None, end_time=None):
        now = datetime.now()
        if end_time:
            hours, minutes = map(int, end_time.split(":"))
            end_time = datetime.combine(date.today(), time(hour=hours, minute=minutes)).time()
        else:
            hours, minutes = map(int, now.strftime("%H:%M").split(":"))
            end_time = datetime.combine(date.today(), time(hour=hours, minute=minutes)).time()

        self.task[self.next_task] = {
            'task_id': self.next_task,
            'name': name,
            'priority': priority,
            'date_added': now.strftime("%Y-%m-%d %H:%M"),
            'end_time': end_time.strftime("%H:%M")
        }

        self.next_task += 1
        self._save_tasks()

    def edit_task_data(self, task_id, new_name=None, new_priority=None, new_end_time=None):
        if task_id in self.task:
            if new_name:
                self.task[task_id]['name'] = new_name
            if new_priority:
                self.task[task_id]['priority'] = new_priority
            if new_end_time:
                hours, minutes = map(int, new_end_time.split(":"))
                end_time = datetime.combine(date.today(), time(hour=hours, minute=minutes)).time()
                self.task[task_id]['end_time'] = end_time.strftime("%H:%M")
            self._save_tasks()
            return True
        return False

    def delete_task(self, task_id):
        if task_id in self.task:
            del self.task[task_id]
            self._save_tasks()
            return True
        return False

    def view_task(self):
        now = datetime.now()
        view = []
        for task_id, tsk in self.task.items():
            hours, minutes = map(int, tsk['end_time'].split(":"))
            end_datetime = datetime.combine(date.today(), time(hour=hours, minute=minutes))
            diff = end_datetime - now
            remaining_seconds = max(diff.total_seconds(), 0)
            remaining_hrs = remaining_seconds // 3600
            remaining_mins = (remaining_seconds % 3600) // 60
            view.append({
                'task_id': task_id,
                'name': tsk['name'],
                'priority': tsk['priority'],
                'date_added': tsk['date_added'],
                'end_time': tsk['end_time'],
                'remaining_time': f"{int(remaining_hrs)} hrs {int(remaining_mins)} mins"
            })
        return view

    def get_temp_file_location(self):
        return self.cache_file
