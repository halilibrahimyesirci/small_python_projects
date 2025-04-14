import serial
import threading
import customtkinter as ctk
from serial.serialutil import SerialException

# COM port and baud rate settings
ser = serial.Serial('COM4', baudrate=115200, timeout=1)

def receive_from_pi():
    """Receive data from Raspberry Pi."""
    while True:
        try:
            if ser.in_waiting > 0:  # Is there incoming data?
                message = ser.readline().decode('utf-8').strip()
                received_text_area.insert(ctk.END, f"Received from Raspberry Pi: {message}\n")
                received_text_area.yview(ctk.END)
        except SerialException as e:
            print(f"SerialException: {e}")
            break

def send_message():
    """Send message."""
    message = entry.get()
    ser.write(message.encode('utf-8'))  # Send message
    sent_text_area.insert(ctk.END, f"Sent: {message}\n")
    sent_text_area.yview(ctk.END)
    entry.delete(0, ctk.END)

# customtkinter interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Raspberry Pi Communication")

frame = ctk.CTkFrame(root)
frame.pack(padx=10, pady=10)

received_label = ctk.CTkLabel(frame, text="Received Messages")
received_label.pack(padx=10, pady=5)

received_text_area = ctk.CTkTextbox(frame, wrap=ctk.WORD, width=500, height=200)
received_text_area.pack(padx=10, pady=5)

sent_label = ctk.CTkLabel(frame, text="Sent Messages")
sent_label.pack(padx=10, pady=5)

sent_text_area = ctk.CTkTextbox(frame, wrap=ctk.WORD, width=500, height=200)
sent_text_area.pack(padx=10, pady=5)

entry = ctk.CTkEntry(frame, width=300)
entry.pack(side=ctk.LEFT, padx=10, pady=10)

send_button = ctk.CTkButton(frame, text="Send", command=send_message)
send_button.pack(side=ctk.LEFT, padx=10, pady=10)

# Start receiving data in a separate thread
receive_thread = threading.Thread(target=receive_from_pi, daemon=True)
receive_thread.start()

root.mainloop()

# Close serial port when the program exits
ser.close()
