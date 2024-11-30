import pyodbc
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database.connection import get_connection, close_connection
from datetime import datetime

class EmployeeGUI:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Employee Portal")
        self.root.geometry("1000x600")
        self.root.config(bg="#9694FF")
        self.username = username
        self.employee_id = self.get_employee_id()
        self.create_widgets()
        
    def get_employee_id(self):
        """Get employee_id from username"""
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM Accounts WHERE username = ?", (self.username,))
                user_id = cursor.fetchone()
                if user_id:
                    cursor.execute("SELECT employee_id FROM Employees WHERE employee_id = ?", (user_id[0],))
                    employee_id = cursor.fetchone()
                    if employee_id:
                        return employee_id[0]
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error in connection or query: {e}")
        finally:
            close_connection(conn)
        return None

    def create_widgets(self):
        # Top frame containing employee info and buttons
        top_frame = Frame(self.root, bg="#ffffff", height=200)
        top_frame.pack(fill=X, padx=10, pady=5)
        top_frame.pack_propagate(False)  # Maintain fixed height

        # Left frame for employee info
        info_frame = Frame(top_frame, bg="#ffffff", width=600)
        info_frame.pack(side=LEFT, fill=BOTH, padx=20, pady=20)
        
        # Right frame for buttons
        button_frame = Frame(top_frame, bg="#ffffff")
        button_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)

        # Display employee information
        self.display_employee_info(info_frame)
        
        # Create buttons
        self.create_buttons(button_frame)

        # Bottom frame for attendance history
        history_frame = Frame(self.root, bg="#ffffff")
        history_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Label for history section
        Label(history_frame, text="Recent Attendance History", 
              font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=5)

        # Create attendance table
        self.create_attendance_table(history_frame)
        
        # Statistics frame at bottom
        stats_frame = Frame(self.root, bg="#ffffff", height=50)
        stats_frame.pack(fill=X, padx=10, pady=5)
        self.display_statistics(stats_frame)

    def display_employee_info(self, parent_frame):
        """Display employee information"""
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT full_name, department, position, hire_date, gender, birthday 
                    FROM Employees 
                    WHERE employee_id = ?
                """, (self.employee_id,))
                employee_info = cursor.fetchone()
                
                if employee_info:
                    info_data = [
                        ("Full Name:", employee_info[0]),
                        ("Department:", employee_info[1]),
                        #("Position:", employee_info[2]),
                        #("Hire Date:", employee_info[3]),
                        #("Gender:", employee_info[4]),
                        ("Birthday:", employee_info[5])
                    ]
                    
                    for i, (label_text, value) in enumerate(info_data):
                        Label(parent_frame, text=label_text, font=("Arial", 11, "bold"), 
                              bg="#ffffff", anchor="w").grid(row=i, column=0, sticky="w", pady=3)
                        Label(parent_frame, text=value, font=("Arial", 11), 
                              bg="#ffffff", anchor="w").grid(row=i, column=1, sticky="w", padx=20, pady=3)
                              
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error fetching employee info: {e}")
        finally:
            close_connection(conn)

    def create_buttons(self, parent_frame):
        """Create attendance and password buttons"""
        # Take Attendance Button
        attendance_frame = Frame(parent_frame, bg="#ffffff", width=200, height=200)
        attendance_frame.pack(side=TOP, pady=10)
        attendance_frame.pack_propagate(False)
        
        take_attendance_btn = Button(attendance_frame, text="Take\nAttendance", 
                                   font=("Arial", 14, "bold"),
                                   bg="#4CAF50", fg="white",
                                   command=self.take_attendance,
                                   width=15, height=5)
        take_attendance_btn.pack(expand=True)

        # Change Password Button
        change_pass_btn = Button(parent_frame, text="Change Password",
                               font=("Arial", 10),
                               bg="#2196F3", fg="white",
                               command=self.change_password,
                               width=15)
        change_pass_btn.pack(side=BOTTOM)

    def create_attendance_table(self, parent_frame):
        """Create and populate attendance history table"""
        table_frame = Frame(parent_frame, height=200)  # Reduced height
        table_frame.pack(fill=BOTH, expand=True)
        
        # Create Treeview with scrollbars
        self.tree_scroll_y = Scrollbar(table_frame)
        self.tree_scroll_y.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(table_frame,
                                columns=("Date", "Check In", "Check Out", "Hours", "Status"),
                                show="headings",
                                yscrollcommand=self.tree_scroll_y.set,
                                height=8)  # Limit number of visible rows

        # Configure scrollbar
        self.tree_scroll_y.config(command=self.tree.yview)

        # Configure columns
        columns = [("Date", 150), ("Check In", 150), ("Check Out", 150), 
                  ("Hours", 100), ("Status", 100)]

        for col, width in columns:
            self.tree.heading(col, text=col, anchor=CENTER)
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.pack(fill=BOTH, expand=True)
        
        # Populate table
        self.fetch_attendance_data()

    def fetch_attendance_data(self):
        """Fetch and display attendance data"""
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TOP 8 work_date, check_in_time, check_out_time, 
                            hours_worked, status 
                    FROM Attendance 
                    WHERE employee_id = ? 
                    ORDER BY work_date DESC
                """, (self.employee_id,))
                
                for row in cursor.fetchall():
                    work_date = datetime.strptime(str(row[0]), '%Y-%m-%d').strftime('%Y-%m-%d')
                    check_in = str(row[1]).split('.')[0]
                    check_out = str(row[2]).split('.')[0] if row[2] else "N/A"
                    
                    # Kiểm tra nếu hours_worked là None
                    hours_worked = f"{float(row[3]):.1f}" if row[3] is not None else "N/A"
                    
                    self.tree.insert("", "end", values=(work_date, check_in, check_out, hours_worked, row[4]))
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error fetching attendance data: {e}")
        finally:
            close_connection(conn)


    def display_statistics(self, parent_frame):
        """Display attendance statistics"""
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as total_days,
                           COUNT(CASE WHEN status = 'present' THEN 1 END) as present_days,
                           COUNT(CASE WHEN status = 'leave' THEN 1 END) as leave_days,
                           AVG(hours_worked) as avg_hours
                    FROM Attendance 
                    WHERE employee_id = ?
                """, (self.employee_id,))
                
                stats = cursor.fetchone()
                if stats:
                    stats_frame = Frame(parent_frame, bg="#ffffff")
                    stats_frame.pack(fill=X)
                    
                    stats_text = [
                        f"Total Days: {stats[0]}",
                        f"Present Days: {stats[1]}",
                        f"Leave Days: {stats[2]}",
                        f"Average Hours: {float(stats[3]):.1f}"
                    ]
                    
                    for text in stats_text:
                        Label(stats_frame, text=text, font=("Arial", 10),
                              bg="#ffffff", padx=20).pack(side=LEFT)
                        
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error calculating statistics: {e}")
        finally:
            close_connection(conn)

    def take_attendance(self):
        """Handle attendance marking"""
        try:
            now = datetime.now()
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                
                # Check if attendance already exists for today
                cursor.execute("""
                    SELECT check_in_time, check_out_time 
                    FROM Attendance 
                    WHERE employee_id = ? AND work_date = ?
                """, (self.employee_id, now.strftime('%Y-%m-%d')))
                
                attendance = cursor.fetchone()
                
                if attendance:
                    if attendance[1]:  # If check_out exists
                        messagebox.showinfo("Info", "You have already completed attendance for today.")
                    else:  # If only check_in exists
                        if attendance[0]:
                            # Parse check-in time
                            check_in = datetime.strptime(str(attendance[0]).split('.')[0], '%H:%M:%S')
                            # Calculate time difference
                            time_diff = (now - check_in).seconds / 3600
                            
                            if time_diff < 1:  # If less than 1 hour
                                messagebox.showinfo("Info", "You need to work for at least 1 hour before checking out.")
                                return

                        if messagebox.askyesno("Confirm", "Do you want to check out?"):
                            # Calculate hours worked
                            hours = (now - check_in).seconds / 3600

                            # Update attendance with check-out
                            cursor.execute("""
                                UPDATE Attendance 
                                SET check_out_time = ?, hours_worked = ? 
                                WHERE employee_id = ? AND work_date = ?
                            """, (now.strftime('%H:%M:%S'), hours, 
                                self.employee_id, now.strftime('%Y-%m-%d')))
                            conn.commit()
                            messagebox.showinfo("Success", "Check-out recorded successfully!")
                else:
                    if messagebox.askyesno("Confirm", "Do you want to check in?"):
                        # Insert new attendance record
                        cursor.execute("""
                            INSERT INTO Attendance 
                            (employee_id, work_date, check_in_time, status) 
                            VALUES (?, ?, ?, 'present')
                        """, (self.employee_id, now.strftime('%Y-%m-%d'), 
                            now.strftime('%H:%M:%S')))
                        conn.commit()
                        messagebox.showinfo("Success", "Check-in recorded successfully!")
                
                # Refresh attendance table
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.fetch_attendance_data()
            
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error recording attendance: {e}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        finally:
            close_connection(conn)



    def change_password(self):
        """Open change password dialog"""
        dialog = Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("300x200")
        dialog.config(bg="#ffffff")
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        Label(dialog, text="Current Password:", bg="#ffffff").pack(pady=5)
        current_pass = Entry(dialog, show="*")
        current_pass.pack(pady=5)
        
        Label(dialog, text="New Password:", bg="#ffffff").pack(pady=5)
        new_pass = Entry(dialog, show="*")
        new_pass.pack(pady=5)
        
        Label(dialog, text="Confirm Password:", bg="#ffffff").pack(pady=5)
        confirm_pass = Entry(dialog, show="*")
        confirm_pass.pack(pady=5)
        
        def update_password():
            if new_pass.get() != confirm_pass.get():
                messagebox.showerror("Error", "New passwords do not match!")
                return
                
            try:
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    # Verify current password
                    cursor.execute("""
                        SELECT password FROM Accounts 
                        WHERE username = ? AND password = ?
                    """, (self.username, current_pass.get()))
                    
                    if cursor.fetchone():
                        # Update password
                        cursor.execute("""
                            UPDATE Accounts 
                            SET password = ? 
                            WHERE username = ?
                        """, (new_pass.get(), self.username))
                        conn.commit()
                        messagebox.showinfo("Success", "Password updated successfully!")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Current password is incorrect!")
            except pyodbc.Error as e:
                messagebox.showerror("Error", f"Error updating password: {e}")
            finally:
                close_connection(conn)
        
        Button(dialog, text="Update Password", 
               command=update_password,
               bg="#2196F3", fg="white").pack(pady=10)

def open_employee_gui(username):
    root = Tk()
    employee_gui = EmployeeGUI(root, username)
    root.mainloop()
    