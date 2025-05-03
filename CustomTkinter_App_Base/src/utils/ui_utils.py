import time
import threading
from tkinter import messagebox


class UIUtils:
    @staticmethod
    def run_progress_animation(progress_bar, value_label, progress_var, duration=5):
        def _progress_animation():
            progress = 0
            running = True
            while progress < 1 and running:
                progress += 0.01
                if progress > 1:
                    progress = 1
                
                # Update progress bar in the main thread
                progress_bar.after(10, lambda p=progress: UIUtils._update_progress(
                    progress_bar, value_label, p))
                time.sleep(duration / 100)
            
            progress_var.set(False)
        
        thread = threading.Thread(target=_progress_animation)
        thread.daemon = True
        thread.start()
        return thread
    
    @staticmethod
    def _update_progress(progress_bar, value_label, progress_value):
        progress_bar.set(progress_value)
        percentage = int(progress_value * 100)
        value_label.configure(text=f"{percentage}%")
    
    @staticmethod
    def show_message(title, message):
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title, message):
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)