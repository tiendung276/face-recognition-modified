import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyodbc

# Database connection string
server = r"desktop-5cqeviu"  # Replace with your actual server name
driver_name = "SQL Server"  # Replace with the actual driver installed on your machine
database_name = "QuanLyNhanSu"
username = "sa"
password = "123456"

connection_str = f"""
    DRIVER={{{driver_name}}};
    SERVER={server};
    DATABASE={database_name};
    UID={username};
    PWD={password};
"""

root = tk.Tk()
root.title("Manage PhongBan Table")
root.geometry("600x400")

# Cấu hình Grid để cho phép cửa sổ thay đổi kích thước
root.grid_rowconfigure(2, weight=1)  # Cho phép Treeview mở rộng theo chiều dọc
root.grid_columnconfigure(0, weight=1)  # Cho phép Treeview mở rộng theo chiều ngang
root.grid_columnconfigure(1, weight=1)

# Labels and entries for MaPB and TenPB
label_ma_pb = tk.Label(root, text="MaPB:")
label_ma_pb.grid(row=0, column=0, padx=10, pady=10, sticky="w")
entry_ma_pb = tk.Entry(root)
entry_ma_pb.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

label_ten_pb = tk.Label(root, text="TenPB:")
label_ten_pb.grid(row=1, column=0, padx=10, pady=10, sticky="w")
entry_ten_pb = tk.Entry(root)
entry_ten_pb.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

# Treeview to display data in a table
columns = ("MaPB", "TenPB")
treeview = ttk.Treeview(root, columns=columns, show="headings")
treeview.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

treeview.heading("MaPB", text="MaPB")
treeview.heading("TenPB", text="TenPB")

# Fetch data from the database and display it in the Treeview
def fetch_data():
    try:
        # Establish the connection
        conn = pyodbc.connect(connection_str)
        cursor = conn.cursor()

        # Fetch data from PhongBan
        cursor.execute("SELECT MaPB, TenPB FROM PhongBan")
        rows = cursor.fetchall()

        # Clear existing data in the treeview
        for row in treeview.get_children():
            treeview.delete(row)

        for row in rows:
            formatted_row = (row[0], row[1].strip() if row[1] else "No Data")  # Clean TenPB data
            treeview.insert("", "end", values=formatted_row)

        conn.close()
    except pyodbc.Error as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

# Insert data into the database
def insert_data():
    ma_pb = entry_ma_pb.get()
    ten_pb = entry_ten_pb.get()

    if ma_pb and ten_pb:
        try:
            # Convert MaPB to integer
            ma_pb_int = str(ma_pb)

            # Establish the connection
            conn = pyodbc.connect(connection_str)
            cursor = conn.cursor()

            # Insert query
            insert_query = "INSERT INTO PhongBan (MaPB, TenPB) VALUES (?, ?)"
            cursor.execute(insert_query, ma_pb_int, ten_pb)

            # Commit the changes
            conn.commit()
            conn.close()

            # Clear the entry fields
            entry_ma_pb.delete(0, tk.END)
            entry_ten_pb.delete(0, tk.END)

            # Refresh the data in Treeview
            fetch_data()

            messagebox.showinfo("Success", "Data inserted successfully!")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid MaPB (integer).")
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error inserting data: {e}")
    else:
        messagebox.showerror("Input Error", "Please fill in all fields.")

# Edit data in the database (popup window)
def edit_data():
    selected_item = treeview.selection()
    if selected_item:
        ma_pb = treeview.item(selected_item)["values"][0]
        ten_pb = treeview.item(selected_item)["values"][1]

        # Create a new window for editing
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Data")
        edit_window.geometry("400x250")

        # Labels and entries for MaPB and TenPB
        label_ma_pb_edit = tk.Label(edit_window, text="MaPB:")
        label_ma_pb_edit.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_ma_pb_edit = tk.Entry(edit_window)
        entry_ma_pb_edit.insert(0, str(ma_pb))  # Pre-fill the entry
        entry_ma_pb_edit.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        label_ten_pb_edit = tk.Label(edit_window, text="TenPB:")
        label_ten_pb_edit.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry_ten_pb_edit = tk.Entry(edit_window)
        entry_ten_pb_edit.insert(0, ten_pb)  # Pre-fill the entry
        entry_ten_pb_edit.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Update function
        def update_data():
            new_ma_pb = entry_ma_pb_edit.get()
            new_ten_pb = entry_ten_pb_edit.get()

            if new_ma_pb and new_ten_pb:
                try:
                    new_ma_pb_int = str(new_ma_pb)

                    # Update query
                    conn = pyodbc.connect(connection_str)
                    cursor = conn.cursor()
                    update_query = "UPDATE PhongBan SET TenPB = ? WHERE MaPB = ?"
                    cursor.execute(update_query, new_ten_pb, new_ma_pb_int)
                    conn.commit()
                    conn.close()

                    # Refresh the data in Treeview
                    fetch_data()
                    edit_window.destroy()

                    messagebox.showinfo("Success", "Data updated successfully!")

                except ValueError:
                    messagebox.showerror("Input Error", "Please enter a valid MaPB (integer).")
                except pyodbc.Error as e:
                    messagebox.showerror("Database Error", f"Error updating data: {e}")
            else:
                messagebox.showerror("Input Error", "Please fill in all fields.")

        # Cancel function
        def cancel_edit():
            edit_window.destroy()

        # Buttons for Update and Cancel
        button_update = tk.Button(edit_window, text="Update", command=update_data)
        button_update.grid(row=2, column=0, padx=10, pady=20)

        button_cancel = tk.Button(edit_window, text="Cancel", command=cancel_edit)
        button_cancel.grid(row=2, column=1, padx=10, pady=20)

    else:
        messagebox.showerror("Selection Error", "Please select a row to edit.")

# Delete data
def delete_data():
    selected_item = treeview.selection()
    if selected_item:
        ma_pb = treeview.item(selected_item)["values"][0]
        result = messagebox.askyesno("Delete Data", f"Are you sure you want to delete MaPB: {ma_pb}?")
        if result:
            try:
                conn = pyodbc.connect(connection_str)
                cursor = conn.cursor()
                delete_query = "DELETE FROM PhongBan WHERE MaPB = ?"
                cursor.execute(delete_query, ma_pb)
                conn.commit()
                conn.close()

                # Refresh the data in Treeview
                fetch_data()

                messagebox.showinfo("Success", "Data deleted successfully!")

            except pyodbc.Error as e:
                messagebox.showerror("Database Error", f"Error deleting data: {e}")
    else:
        messagebox.showerror("Selection Error", "Please select a row to delete.")
# Buttons for Insert, Edit, and Delete
button_insert = tk.Button(root, text="Insert Data", command=insert_data)
button_insert.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

button_edit = tk.Button(root, text="Edit Data", command=edit_data)
button_edit.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

button_delete = tk.Button(root, text="Delete Data", command=delete_data)
button_delete.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# Load data initially
fetch_data()

root.mainloop()
