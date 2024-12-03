import time

from rich.progress import Progress

with Progress() as progress:

    task1 = progress.add_task("[red]Loading...", total=1000)

    while not progress.finished:
        progress.update(task1, advance=15)
        time.sleep(0.02)
    
    print("may gay!")