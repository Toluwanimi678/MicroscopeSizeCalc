import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3

# ---------------- DATABASE ----------------
def create_database():
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        measured_size REAL,
        real_size REAL
    )
    """)

    conn.commit()
    conn.close()


def save_record(username, measured, real):
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO calculations (username, measured_size, real_size)
    VALUES (?, ?, ?)
    """, (username, measured, real))

    conn.commit()
    conn.close()


def fetch_records():
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calculations")
    data = cursor.fetchall()
    conn.close()
    return data


def delete_record(record_id):
    conn = sqlite3.connect("microscope.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calculations WHERE id=?", (record_id,))
    conn.commit()
    conn.close()


# ---------------- MAIN APP ----------------
class MicroscopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Specimen Size Calculator")
        self.root.geometry("600x500")

        # Variables
        self.username = tk.StringVar()
        self.measured_size = tk.StringVar()
        self.selected_microscope = tk.StringVar()
        self.selected_unit = tk.StringVar()
        self.image_path = tk.StringVar()

        # Data
        self.microscopes = {
            "Light Microscope (1000x)": 1000,
            "SEM (100000x)": 100000,
            "TEM (1000000x)": 1000000,
            "Stereo Microscope (50x)": 50
        }

        self.units = {
            "nm": 1e6,
            "µm": 1e3,
            "mm": 1,
            "cm": 0.1,
            "m": 0.001
        }

        self.create_widgets()

    # ---------------- UI ----------------
    def create_widgets(self):
        tk.Label(self.root, text="Username").pack()
        tk.Entry(self.root, textvariable=self.username).pack()

        tk.Label(self.root, text="Measured Size (mm)").pack()
        tk.Entry(self.root, textvariable=self.measured_size).pack()

        tk.Label(self.root, text="Microscope Type").pack()
        ttk.Combobox(self.root, textvariable=self.selected_microscope,
                     values=list(self.microscopes.keys())).pack()

        tk.Label(self.root, text="Output Unit").pack()
        ttk.Combobox(self.root, textvariable=self.selected_unit,
                     values=list(self.units.keys())).pack()

        tk.Button(self.root, text="Upload Image", command=self.upload_image).pack()
        tk.Label(self.root, textvariable=self.image_path).pack()

        tk.Button(self.root, text="Calculate", command=self.calculate).pack(pady=10)

        self.result_box = tk.Text(self.root, height=10)
        self.result_box.pack()

        tk.Button(self.root, text="View Records", command=self.show_records).pack(pady=5)

    # ---------------- IMAGE UPLOAD ----------------
    def upload_image(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file:
            self.image_path.set(file)

    # ---------------- CALCULATION ----------------
    def calculate(self):
        try:
            username = self.username.get()
            measured = float(self.measured_size.get())
            microscope = self.selected_microscope.get()
            unit = self.selected_unit.get()

            if not username:
                messagebox.showerror("Error", "Enter username")
                return

            magnification = self.microscopes[microscope]
            factor = self.units[unit]

            real_mm = measured / magnification
            final = real_mm * factor

            # Display result
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END,
                f"User: {username}\n"
                f"Measured Size: {measured} mm\n"
                f"Microscope: {microscope}\n\n"
                f"Step 1: {measured} ÷ {magnification} = {real_mm:.6f} mm\n"
                f"Step 2: {real_mm:.6f} × {factor} = {final:.6f} {unit}\n\n"
                f"Final Answer: {final:.6f} {unit}"
            )

            # Save to DB
            save_record(username, measured, real_mm)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- VIEW RECORDS ----------------
    def show_records(self):
        records = fetch_records()

        win = tk.Toplevel(self.root)
        win.title("Saved Records")

        listbox = tk.Listbox(win, width=80)
        listbox.pack()

        for r in records:
            listbox.insert(tk.END,
                f"ID:{r[0]} | User:{r[1]} | Measured:{r[2]} mm | Real:{r[3]} mm"
            )

        def delete_selected():
            selected = listbox.get(tk.ACTIVE)
            if selected:
                record_id = int(selected.split("|")[0].split(":")[1])
                delete_record(record_id)
                listbox.delete(tk.ACTIVE)

        tk.Button(win, text="Delete Selected", command=delete_selected).pack()


# ---------------- RUN ----------------
create_database()

root = tk.Tk()
app = MicroscopeApp(root)
root.mainloop()