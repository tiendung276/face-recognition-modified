import pyodbc
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from database.connection import get_connection, close_connection

class AdminGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System - Admin")
        self.root.geometry("1200x600")
        self.root.config(bg="#9694FF")
        self.create_widgets()
                
    def create_widgets(self):
        # Create main frames
        details_frame = Frame(self.root, bg="#ffffff", pady=20, padx=20)
        details_frame.pack(fill=X, padx=10, pady=5)

        table_frame = Frame(self.root, bg="#ffffff")
        table_frame.pack(fill=BOTH, expand=True, padx=20, pady=30)

        # Employee Details Section (Top)
        labels = ["Full Name:", "Position:", "Department:", "Hire Date:", 
                  "Status:", "Gender:", "Birthday:"]
        entries = []

        for i, label_text in enumerate(labels):
            row = i // 3
            col = i % 3

            label = Label(details_frame, text=label_text, font=("Arial", 12), 
                          bg="#ffffff", anchor="e")
            label.grid(row=row, column=col*2, padx=5, pady=5, sticky="e")

            entry = Entry(details_frame, font=("Arial", 12), width=20)
            entry.grid(row=row, column=col*2+1, padx=5, pady=5, sticky="w")
            entries.append(entry)

        # Assign entries to named variables for easier access
        self.full_name_entry, self.position_entry, self.department_entry, self.hire_date_entry, \
        self.status_entry, self.gender_entry, self.birthday_entry = entries

        # Buttons Frame
        buttons_frame = Frame(details_frame, bg="#ffffff")
        buttons_frame.grid(row=3, column=0, columnspan=6, pady=10)

        self.add_button = Button(buttons_frame, text="Add Employee", font=("Arial", 11),
                                 bg="#27ae60", fg="white", padx=20, command=self.add_employee)
        self.add_button.pack(side=LEFT, padx=5)

        self.edit_button = Button(buttons_frame, text="Save Changes", font=("Arial", 11),
                                  bg="#f39c12", fg="white", padx=20, command=self.save_changes)
        self.edit_button.pack(side=LEFT, padx=5)

        self.delete_button = Button(buttons_frame, text="Delete Employee", font=("Arial", 11),
                                    bg="#e74c3c", fg="white", padx=20, command=self.delete_employee)
        self.delete_button.pack(side=LEFT, padx=5)

        self.clear_button = Button(buttons_frame, text="Clear Fields", font=("Arial", 11),
                                   bg="#95a5a6", fg="white", padx=20, command=self.clear_fields)
        self.clear_button.pack(side=LEFT, padx=5)

        # Employee Table Section (Bottom)
        self.tree_scroll_y = Scrollbar(table_frame)
        self.tree_scroll_y.pack(side=RIGHT, fill=Y)

        self.tree_scroll_x = Scrollbar(table_frame, orient='horizontal')
        self.tree_scroll_x.pack(side=BOTTOM, fill=X)

        self.tree = ttk.Treeview(table_frame,
                                 columns=("ID", "Full Name", "Department", "Position", 
                                          "Hire Date", "Status", "Birthday", "Gender"),
                                 show="headings",
                                 yscrollcommand=self.tree_scroll_y.set,
                                 xscrollcommand=self.tree_scroll_x.set)

        # Configure scrollbars
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        # Configure column headings
        columns = [("ID", 80), ("Full Name", 200), ("Department", 150), 
                   ("Position", 150), ("Hire Date", 100), ("Status", 100),
                   ("Birthday", 100), ("Gender", 100)]

        for col, width in columns:
            self.tree.heading(col, text=col, anchor=CENTER)
            self.tree.column(col, width=width, anchor=CENTER)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.show_selected_data)

        self.fetch_and_update_employee_table()

    def show_selected_data(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            entries = [self.full_name_entry, self.position_entry, self.department_entry,
                    self.hire_date_entry, self.status_entry, self.birthday_entry,
                    self.gender_entry]
            self.clear_fields()
            for entry, value in zip(entries, values[1:]):
                entry.insert(0, value)
    
    def fetch_and_update_employee_table(self):
        """Update employee data in the table"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        employees = self.fetch_all_employees()
        if employees:
            for emp in employees:
                self.tree.insert("", "end", values=(emp['employee_id'], emp['full_name'], 
                                                    emp['department'], emp['position'], 
                                                    emp['hire_date'], emp['status'],
                                                    emp['birthday'], emp['gender']))

    def fetch_all_employees(self):
        """Fetch all employees from the database"""
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Employees")
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                employees = [dict(zip(column_names, row)) for row in rows]
                return employees
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error in connection or query: {e}")
        finally:
            close_connection(conn)

    def add_employee(self):
        """Insert a new employee"""
        data = {
            'full_name': self.full_name_entry.get(),
            'department': self.department_entry.get(),
            'position': self.position_entry.get(),
            'hire_date': self.hire_date_entry.get(),
            'status': self.status_entry.get(),
            'gender': self.gender_entry.get(),
            'birthday': self.birthday_entry.get()
        }
        self.insert_employee(data)

    def insert_employee(self, data):
        try:
            conn = get_connection()
            if conn:
                # Format dates before insert
                data['hire_date'] = self.format_date(data['hire_date'])
                data['birthday'] = self.format_date(data['birthday'])
                if not data['hire_date'] or not data['birthday']:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                    return
                cursor = conn.cursor()
                columns = ', '.join(data.keys())
                values = ', '.join(['?'] * len(data))
                insert_query = f"INSERT INTO Employees ({columns}) VALUES ({values})"
                cursor.execute(insert_query, *data.values())
                conn.commit()
                messagebox.showinfo("Success", "Employee record inserted successfully.")
                self.fetch_and_update_employee_table()
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error in connection or query: {e}")
        finally:
            close_connection(conn)

    def save_changes(self):
        """Save changes made to an employee"""
        selected_item = self.tree.selection()
        if selected_item:
            data = {
                'full_name': self.full_name_entry.get(),
                'department': self.department_entry.get(),
                'position': self.position_entry.get(),
                'hire_date': self.hire_date_entry.get(),
                'status': self.status_entry.get(),
                'gender': self.gender_entry.get(),
                'birthday': self.birthday_entry.get()
            }
            condition = {'employee_id': self.tree.item(selected_item[0])['values'][0]}
            self.update_employee(data, condition)

    def update_employee(self, data, condition):
        try:
            conn = get_connection()
            if conn:
                data['hire_date'] = self.format_date(data['hire_date'])
                data['birthday'] = self.format_date(data['birthday'])
                if not data['hire_date'] or not data['birthday']:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                    return
                cursor = conn.cursor()
                set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
                update_query = f"UPDATE Employees SET {set_clause} WHERE {where_clause}"
                cursor.execute(update_query, *data.values(), *condition.values())
                conn.commit()
                messagebox.showinfo("Success", "Employee record updated successfully.")
                self.fetch_and_update_employee_table()
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error in connection or query: {e}")
        finally:
            close_connection(conn)
            
    def format_date(self, date_str):
        try:
            # Chuyển string thành datetime object
            from datetime import datetime
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except:
            return None
        
    def delete_employee(self):
        """Delete selected employee"""
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item[0])['values'][0]
            self.delete_employee_from_db(employee_id)

    def delete_employee_from_db(self, employee_id):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                delete_query = f"DELETE FROM Employees WHERE employee_id = ?"
                cursor.execute(delete_query, (employee_id,))
                conn.commit()
                messagebox.showinfo("Success", "Employee record deleted successfully.")
                self.fetch_and_update_employee_table()
        except pyodbc.Error as e:
            messagebox.showerror("Error", f"Error in connection or query: {e}")
        finally:
            close_connection(conn)

    def clear_fields(self):
        """Clear all input fields"""
        self.full_name_entry.delete(0, END)
        self.position_entry.delete(0, END)
        self.department_entry.delete(0, END)
        self.hire_date_entry.delete(0, END)
        self.status_entry.delete(0, END)
        self.gender_entry.delete(0, END)
        self.birthday_entry.delete(0, END)

def open_admin_gui():
    root = Tk()
    admin_gui = AdminGUI(root)
    root.mainloop()
