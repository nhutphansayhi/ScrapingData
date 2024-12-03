from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from threading import Thread
from rich.console import Console
import time

console = Console()

def task(progress, task_id, duration):
    """Hàm giả lập một công việc."""
    for i in range(100):
        time.sleep(duration / 100)  # Mô phỏng thời gian xử lý
        progress.update(task_id, advance=1)

def main():
    # Tạo Progress để quản lý và hiển thị tiến trình
    with Progress(console=console) as progress:
        # Tạo danh sách các task
        tasks = [
            {"desc": "Task 1", "duration": 5},
            {"desc": "Task 2", "duration": 7},
            {"desc": "Task 3", "duration": 4},
            {"desc": "Task 4", "duration": 6},
        ]

        # Tạo các task trong Progress
        task_ids = [
            progress.add_task(task["desc"], total=100) for task in tasks
        ]

        # Tạo và khởi động các thread
        threads = [
            Thread(target=task, args=(progress, task_ids[i], tasks[i]["duration"]))
            for i in range(len(tasks))
        ]
        for t in threads:
            t.start()

        # Đợi tất cả các thread hoàn thành
        for t in threads:
            t.join()

if __name__ == "__main__":
    main()