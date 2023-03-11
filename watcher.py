import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print('huhu')
        if event.src_path.endswith('.py'):
            print(event.src_path + ' modified')
            os.system(f'python {sys.argv[1]}')

if __name__ == "__main__":
    path = "."
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print('Watchdog is watching for changes')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
# class MonitorFolder(FileSystemEventHandler):
#     FILE_SIZE=1000
    
#     def on_created(self, event):
#          print(event.src_path, event.event_type)
#          self.checkFolderSize(event.src_path)
   
#     def on_modified(self, event):
#         print(event.src_path, event.event_type)
#         self.checkFolderSize(event.src_path)
    
#     def on_deleted(self, event):
#         print(event.src_path, event.event_type)
               
#     def checkFolderSize(self,src_path):
#         if os.path.isdir(src_path):
#             if os.path.getsize(src_path) >self.FILE_SIZE:
#                 print("Time to backup the dir")
#         else:
#             if os.path.getsize(src_path) >self.FILE_SIZE:
#                 print("very big file, needs to be backed up")

# if __name__ == "__main__":
#     src_path = sys.argv[1]
    
#     event_handler=MonitorFolder()
#     observer = Observer()
#     observer.schedule(event_handler, path=src_path, recursive=True)
#     print("Monitoring started")
#     observer.start()
#     try:
#         while(True):
#            time.sleep(1)
           
#     except KeyboardInterrupt:
#             observer.stop()
#             observer.join()