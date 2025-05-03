"""
Logger Module
Provides logging functionality for debugging and tracking game events
"""

import os
import time
import datetime
import traceback
import sys
from typing import Dict, List, Any, Optional

# Create log directory if it doesn't exist
sys.path.append("../../config")
try:
    from config.game_config import LOG_FILE_PATH
except ImportError:
    try:
        from Window_Frame_Game.config.game_config import LOG_FILE_PATH
    except ImportError:
        # Fallback value
        LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")

# Ensure log directory exists
os.makedirs(LOG_FILE_PATH, exist_ok=True)

class Logger:
    """
    A versatile logging system for tracking game events, errors and performance
    """
    
    # Log levels
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    
    # Level names for display
    LEVEL_NAMES = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARNING: "WARNING",
        ERROR: "ERROR",
        CRITICAL: "CRITICAL"
    }
    
    def __init__(self, name: str, log_level: int = INFO, console_output: bool = True, file_output: bool = True):
        """
        Initialize the logger
        
        Args:
            name: Logger name used in log files
            log_level: Minimum log level to record
            console_output: Whether to output logs to console
            file_output: Whether to save logs to file
        """
        self.name = name
        self.log_level = log_level
        self.console_output = console_output
        self.file_output = file_output
        
        # Set up log file
        if self.file_output:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(LOG_FILE_PATH, f"{self.name}_{timestamp}.log")
            
            # Create file and write header
            with open(self.log_file, 'w') as f:
                f.write(f"=== {self.name} Log Started at {timestamp} ===\n\n")
                
        # Track performance metrics
        self.performance_data = {}
        self.timers = {}
        
    def log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Log a message at the specified level
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: The log message
            context: Optional dictionary with additional context
        """
        # Skip if below current log level
        if level < self.log_level:
            return
            
        # Format timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Format log level
        level_str = self.LEVEL_NAMES.get(level, "UNKNOWN")
        
        # Format context if provided
        context_str = ""
        if context:
            context_str = " | " + " | ".join([f"{k}={v}" for k, v in context.items()])
            
        # Assemble log entry
        log_entry = f"[{timestamp}] [{level_str}] {message}{context_str}"
        
        # Output to console if enabled
        if self.console_output:
            print(log_entry)
            
        # Write to file if enabled
        if self.file_output:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry + "\n")
            except Exception as e:
                # If we can't write to the log file, at least print to console
                print(f"Error writing to log file: {e}")
                print(log_entry)
                
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a debug message"""
        self.log(self.DEBUG, message, context)
        
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log an info message"""
        self.log(self.INFO, message, context)
        
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a warning message"""
        self.log(self.WARNING, message, context)
        
    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log an error message"""
        self.log(self.ERROR, message, context)
        
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log a critical message"""
        self.log(self.CRITICAL, message, context)
        
    def exception(self, message: str, exc_info: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None):
        """
        Log an exception with traceback
        
        Args:
            message: The log message
            exc_info: The exception object (defaults to current exception in except block)
            context: Optional dictionary with additional context
        """
        if exc_info is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is None:
                # No current exception
                self.error(f"{message} (no exception info available)", context)
                return
        else:
            exc_type = type(exc_info)
            exc_value = exc_info
            exc_traceback = exc_info.__traceback__
            
        # Format traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)
        
        # Create combined context with exception info
        combined_context = {"exception_type": exc_type.__name__, "traceback": tb_text}
        if context:
            combined_context.update(context)
            
        # Log as error
        self.log(self.ERROR, message, combined_context)
        
    def start_timer(self, name: str):
        """
        Start a timer for performance measurement
        
        Args:
            name: Name of the timer
        """
        self.timers[name] = time.time()
        
    def stop_timer(self, name: str, log_level: int = DEBUG) -> float:
        """
        Stop a timer and log the elapsed time
        
        Args:
            name: Name of the timer
            log_level: Level to log the timer result at
            
        Returns:
            Elapsed time in milliseconds
        """
        if name not in self.timers:
            self.warning(f"Timer '{name}' was not started")
            return 0
            
        # Calculate elapsed time
        elapsed = (time.time() - self.timers[name]) * 1000  # Convert to ms
        
        # Store in performance data
        if name not in self.performance_data:
            self.performance_data[name] = []
        self.performance_data[name].append(elapsed)
        
        # Log the timing
        self.log(log_level, f"Timer '{name}' completed", {"elapsed_ms": f"{elapsed:.2f}"})
        
        # Clean up timer
        del self.timers[name]
        
        return elapsed
        
    def get_average_time(self, name: str) -> float:
        """
        Get the average time for a particular timer
        
        Args:
            name: Name of the timer
            
        Returns:
            Average time in milliseconds
        """
        if name in self.performance_data and self.performance_data[name]:
            return sum(self.performance_data[name]) / len(self.performance_data[name])
        return 0
        
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get a summary of all performance metrics
        
        Returns:
            Dictionary with timer names as keys and metrics as values
        """
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
        """
        Log a summary of all performance metrics
        
        Args:
            log_level: Level to log the summary at
        """
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
        """
        Change the current log level
        
        Args:
            level: New log level
        """
        self.log_level = level
        self.info(f"Log level changed to {self.LEVEL_NAMES.get(level, 'UNKNOWN')}")
        
    def enable_console_output(self, enabled: bool = True):
        """
        Enable or disable console output
        
        Args:
            enabled: Whether console output should be enabled
        """
        self.console_output = enabled
        
    def enable_file_output(self, enabled: bool = True):
        """
        Enable or disable file output
        
        Args:
            enabled: Whether file output should be enabled
        """
        # If enabling and not already enabled, create new log file
        if enabled and not self.file_output:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(LOG_FILE_PATH, f"{self.name}_{timestamp}.log")
            
            # Create file and write header
            with open(self.log_file, 'w') as f:
                f.write(f"=== {self.name} Log Continued at {timestamp} ===\n\n")
                
        self.file_output = enabled