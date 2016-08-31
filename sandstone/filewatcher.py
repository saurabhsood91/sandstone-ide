from watchdog.observers import Observer
import watchdog

class Filewatcher(watchdog.events.FileSystemEventHandler):
    """
    Starts a watchdog instance to watch over the filesystem
    Handles events - CREATE, REMOVE,MOVE
    """
    watched_directories = []

    def __init__(self):
        print 'Watchdog instance started'

    def add_directory_to_watch(self, directory):
        if directory not in self.watched_directories:
            self.watched_directories.append(directory)
        # Add the watcher
        observer = Observer()
        observer.schedule(self, directory, recursive=False)
        observer.start()

    def remove_directory_to_watch(self, directory):
        if directory in self.watched_directories:
            self.watched_directories.remove(directory)
        # TODO remove the watchers if needed

    def on_created(self, event):
        """
        Event Handler when a file is created
        """
        print 'File created in %s' % (event.src_path)

    def on_deleted(self, event):
        """
        Event Handler when a file is deleted
        """
        print 'File deleted in %s' % (event.src_path)

    def on_moved(self, event):
        """
        Event Handler when a file is moved
        """
        print 'File moved from %s to %s' % (event.src_path, event.dest_path)
