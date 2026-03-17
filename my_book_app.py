import json
import threading
import tkinter as tk
from tkinter import messagebox
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "http://127.0.0.1:5001/books"

# ===== THEME (BLACK / WHITE / RED) =====
APP_BG = "#0f0f0f"
CARD_BG = "#1a1a1a"
ACCENT = "#e63946"
TEXT = "#ffffff"
SUBTEXT = "#aaaaaa"
BORDER = "#2a2a2a"

CARD_COLUMNS = 2


def load_books_from_api():
    request = Request(API_URL, headers={"Accept": "application/json"})
    with urlopen(request, timeout=5) as response:
        payload = json.load(response)

    return payload.get("books", [])


def fetch_books():
    btn_load.config(state="disabled")
    status_var.set("Loading books...")
    threading.Thread(target=_fetch_books_worker, daemon=True).start()


def _fetch_books_worker():
    try:
        books = load_books_from_api()
    except HTTPError as error:
        root.after(0, lambda: show_fetch_error(f"API error {error.code}"))
        return
    except URLError:
        root.after(0, lambda: show_fetch_error("API not running"))
        return
    except Exception as error:
        root.after(0, lambda: show_fetch_error(str(error)))
        return

    root.after(0, lambda: display_books(books))


def show_fetch_error(message):
    btn_load.config(state="normal")
    status_var.set("Error")
    messagebox.showerror("Error", message)


def format_price(value):
    try:
        return f"{float(value):,.2f} THB"
    except:
        return "N/A"


def display_books(books):
    for widget in content_frame.winfo_children():
        widget.destroy()

    summary_var.set(f"{len(books)} Books")
    status_var.set("Loaded")

    for i, book in enumerate(books):
        row = i // CARD_COLUMNS
        col = i % CARD_COLUMNS

        card = tk.Frame(
            content_frame,
            bg=CARD_BG,
            bd=1,
            relief="flat",
            highlightbackground=ACCENT,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # TITLE
        tk.Label(
            card,
            text=book.get("title", ""),
            font=("Segoe UI", 13, "bold"),
            bg=CARD_BG,
            fg=TEXT,
            wraplength=300,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # AUTHOR
        tk.Label(
            card,
            text=f"by {book.get('author', '-')}",
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=SUBTEXT,
        ).pack(anchor="w")

        # PRICE
        tk.Label(
            card,
            text=format_price(book.get("price")),
            font=("Segoe UI", 12, "bold"),
            bg=CARD_BG,
            fg=ACCENT,
            pady=10,
        ).pack(anchor="w")

        # ID + URL (เล็กๆ)
        tk.Label(
            card,
            text=f"ID: {book.get('id')}",
            font=("Segoe UI", 8),
            bg=CARD_BG,
            fg="#666",
        ).pack(anchor="w")

    btn_load.config(state="normal")


# ===== UI SETUP =====
root = tk.Tk()
root.title("Book Inventory")
root.geometry("1000x720")
root.configure(bg=APP_BG)

# HEADER
header = tk.Label(
    root,
    text="BOOK COLLECTION",
    font=("Segoe UI", 26, "bold"),
    bg=APP_BG,
    fg=TEXT,
)
header.pack(pady=(20, 5))

subheader = tk.Label(
    root,
    text="Powered by Book API",
    font=("Segoe UI", 10),
    bg=APP_BG,
    fg=SUBTEXT,
)
subheader.pack()

# TOOLBAR
toolbar = tk.Frame(root, bg=APP_BG)
toolbar.pack(fill="x", padx=30, pady=20)

btn_load = tk.Button(
    toolbar,
    text="REFRESH",
    command=fetch_books,
    bg="#111",
    fg=TEXT,
    activebackground=ACCENT,
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    padx=20,
    pady=10,
    relief="flat",
)
btn_load.pack(side="left")

summary_var = tk.StringVar(value="-")
status_var = tk.StringVar(value="Ready")

tk.Label(
    toolbar,
    textvariable=summary_var,
    bg=APP_BG,
    fg=TEXT,
    font=("Segoe UI", 10, "bold"),
).pack(side="left", padx=20)

tk.Label(
    toolbar,
    textvariable=status_var,
    bg=APP_BG,
    fg=SUBTEXT,
).pack(side="right")

# SCROLL AREA
container = tk.Frame(root, bg=APP_BG)
container.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(container, bg=APP_BG, highlightthickness=0)
scrollbar = tk.Scrollbar(container, command=canvas.yview)

content_frame = tk.Frame(canvas, bg=APP_BG)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", on_configure)

canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.after(200, fetch_books)
root.mainloop()