import os
import time
import datetime
import traceback
import sys
from typing import Dict, List, Any, Optional

sys.path.append("../../config")
try:
    from config.game_config import LOG_FILE_PATH
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import LOG_FILE_PATH
    except ImportError:
        LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")

os.makedirs(LOG_FILE_PATH, exist_ok=True)

class Logger:
    
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    
    LEVEL_NAMES = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARNING: "WARNING",
        ERROR: "ERROR",
        CRITICAL: "CRITICAL"
    }
    
    def __init__(self, name: str, log_level: int = INFO, console_output: bool = True, file_output: bool = True):
        self.name = name
        self.log_level = log_level
        self.console_output = console_output
        self.file_output = file_output
        
        if self.file_output:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(LOG_FILE_PATH, f"{self.name}_{timestamp}.log")
            
            with open(self.log_file, 'w') as f:
                f.write(f"=== {self.name} Log Started at {timestamp} ===\n\n")
                
        self.performance_data = {}
        self.timers = {}
        
    def log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None):
        if level < self.log_level:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        level_str = self.LEVEL_NAMES.get(level, "UNKNOWN")
        
        context_str = ""
        if context:
            context_str = " | " + " | ".join([f"{k}={v}" for k, v in context.items()])
            
        log_entry = f"[{timestamp}] [{level_str}] {message}{context_str}"
        
        if self.console_output:
            print(log_entry)
            
        if self.file_output:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry + "\n")
            except Exception as e:
                print(f"Error writing to log file: {e}")
                print(log_entry)
                
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log(self.DEBUG, message, context)
        
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log(self.INFO, message, context)
        
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log(self.WARNING, message, context)
        
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log(self.ERROR, message, context)
        
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.log(self.CRITICAL, message, context)
        
    def exception(self, message: str, exc_info: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None):
        if exc_info is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is None:
                self.error(f"{message} (no exception info available)", context)
                return
        else:
            exc_type = type(exc_info)
            exc_value = exc_info
            exc_traceback = exc_info.__traceback__
            
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)
        
        combined_context = {"exception_type": exc_type.__name__, "traceback": tb_text}
        if context:
            combined_context.update(context)
            
        self.log(self.ERROR, message, combined_context)
        
    def start_timer(self, name: str):
        self.timers[name] = time.time()
        
    def stop_timer(self, name: str, log_level: int = DEBUG) -> float:
        if name not in self.timers:
            self.warning(f"Timer '{name}' was not started")
            return 0
            
        elapsed = (time.time() - self.timers[name]) * 1000
        
        if name not in self.performance_data:
            self.performance_data[name] = []
        self.performance_data[name].append(elapsed)
        
        self.log(log_level, f"Timer '{name}' completed", {"elapsed_ms": f"{elapsed:.2f}"})
        
        del self.timers[name]
        
        return elapsed
        
    def get_average_time(self, name: str) -> float:
        if name in self.performance_data and self.performance_data[name]:
            return sum(self.performance_data[name]) / len(self.performance_data[name])
        return 0
        
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        summary = {}
        
        for name, times in self.performance_data.items():
            if not times:
                continue
                
            summary[name] = {
                "avg_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "count": len(times)
            }
            
        return summary
        
    def log_performance_summary(self, log_level: int = INFO):
        summary = self.get_performance_summary()
        
        if not summary:
            self.log(log_level, "No performance data available")
            return
            
        self.log(log_level, "Performance Summary:")
        
        for name, metrics in summary.items():
            self.log(log_level, f"  {name}: avg={metrics['avg_ms']:.2f}ms, "
                              f"min={metrics['min_ms']:.2f}ms, "
                              f"max={metrics['max_ms']:.2f}ms, "
                              f"count={metrics['count']}")
                              
    def set_log_level(self, level: int):
        self.log_level = level
        self.info(f"Log level changed to {self.LEVEL_NAMES.get(level, 'UNKNOWN')}")
        
    def enable_console_output(self, enabled: bool = True):
        self.console_output = enabled
        
    def enable_file_output(self, enabled: bool = True):
        if enabled and not self.file_output:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(LOG_FILE_PATH, f"{self.name}_{timestamp}.log")
            
            with open(self.log_file, 'w') as f:
                f.write(f"=== {self.name} Log Continued at {timestamp} ===\n\n")
                
        self.file_output = enabled