import pyodbc
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database.connection import get_connection, close_connection
from admin_GUI import open_admin_gui
from employee_GUI import open_employee_gui

def authenticate_user(username, password):
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            query = "SELECT role FROM Accounts WHERE username = ? AND password = ? AND status = 'active'"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                role = result[0]
                if role == 'admin':
                    # messagebox.showinfo("Login Success", "Welcome Admin!")
                    root.destroy()
                    open_admin_gui() 
                elif role == 'employee':
                    #messagebox.showinfo("Login Success", "Welcome Employee!")
                    root.destroy()
                    open_employee_gui(username) 
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    finally:
        close_connection(conn)


def on_login_button_click():
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
    else:
        authenticate_user(username, password)

root = Tk()

X = 800
Y = 600
root.title("Employee Management System - Login")
root.geometry(f"{X}x{Y}") 
root.config(bg="#563A9C")

login_frame = Frame(root, bg="#ffffff", padx=40, pady=30, bd=2, relief="solid")
login_frame.place(relx=0.5, rely=0.5, anchor="center") 

login_label = Label(login_frame, text="Login", font=("Arial", 30, "bold"), bg="#ffffff", fg="#6A42C2")
login_label.grid(row=0, column=0, columnspan=2, pady=20)

username_label = Label(login_frame, text="Username:", font=("Arial", 14), bg="#ffffff", fg="#6A42C2")
username_label.grid(row=1, column=0, pady=10, padx=10, sticky="e")  # Right align the label

username_entry = Entry(login_frame, font=("Arial", 14), width=30, bd=2, relief="solid")
username_entry.grid(row=1, column=1, pady=10, padx=10)

password_label = Label(login_frame, text="Password:", font=("Arial", 14), bg="#ffffff", fg="#6A42C2")
password_label.grid(row=2, column=0, pady=10, padx=10, sticky="e")  # Right align the label

password_entry = Entry(login_frame, font=("Arial", 14), width=30, bd=2, relief="solid", show="*")
password_entry.grid(row=2, column=1, pady=10, padx=10)

login_button = Button(login_frame, text="Login", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", relief="solid", bd=0, width=20, command=on_login_button_click)
login_button.grid(row=3, column=0, columnspan=2, pady=20)

username_entry.bind("<Return>", lambda event: on_login_button_click()) # nhan Enter cung co the dang nhap
password_entry.bind("<Return>", lambda event: on_login_button_click())

login_frame.grid_columnconfigure(0, weight=1)
login_frame.grid_columnconfigure(1, weight=2)

root.mainloop()
