import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import csv


class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Combiner")
        self.root.geometry("650x520")
        self.root.resizable(True, True)
        self.files = []
        self._build_ui()

    def _build_ui(self):
        # ── Title ──────────────────────────────────────────────
        tk.Label(self.root, text="File Combiner", font=("Helvetica", 16, "bold")).pack(pady=(14, 2))
        tk.Label(self.root, text="Select .txt or .csv files to merge into one output file.",
                 fg="gray").pack(pady=(0, 10))

        # ── File list frame ────────────────────────────────────
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                  selectmode=tk.EXTENDED, height=12,
                                  font=("Courier", 10), activestyle="dotbox")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # ── File buttons ───────────────────────────────────────
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=16, pady=6)

        tk.Button(btn_frame, text="➕  Add Files", width=14, command=self.add_files).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="⬆  Move Up",   width=14, command=self.move_up).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="⬇  Move Down", width=14, command=self.move_down).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="🗑  Remove",    width=14, command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="Clear All",     width=10, command=self.clear_all).pack(side=tk.LEFT)

        # ── Options ────────────────────────────────────────────
        opt_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=8)
        opt_frame.pack(fill=tk.X, padx=16, pady=(4, 6))

        # Separator option (text files)
        tk.Label(opt_frame, text="Text file separator:").grid(row=0, column=0, sticky="w")
        self.separator_var = tk.StringVar(value="newline")
        sep_choices = ttk.Combobox(opt_frame, textvariable=self.separator_var, width=18, state="readonly",
                                   values=["newline", "blank line", "--- filename ---", "none"])
        sep_choices.grid(row=0, column=1, sticky="w", padx=(6, 20))

        # CSV header option
        self.skip_header_var = tk.BooleanVar(value=True)
        tk.Checkbutton(opt_frame, text="Skip header row in subsequent CSV files",
                       variable=self.skip_header_var).grid(row=0, column=2, sticky="w")

        # Output encoding
        tk.Label(opt_frame, text="Encoding:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.encoding_var = tk.StringVar(value="utf-8")
        enc_box = ttk.Combobox(opt_frame, textvariable=self.encoding_var, width=18, state="readonly",
                               values=["utf-8", "utf-8-sig", "latin-1", "ascii"])
        enc_box.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=(6, 0))

        # ── Combine button ─────────────────────────────────────
        tk.Button(self.root, text="💾  Combine & Save", font=("Helvetica", 11, "bold"),
                  bg="#2e7d32", fg="white", activebackground="#1b5e20", activeforeground="white",
                  padx=10, pady=6, command=self.combine_files).pack(pady=(4, 14))

        # ── Status bar ─────────────────────────────────────────
        self.status_var = tk.StringVar(value="No files added yet.")
        tk.Label(self.root, textvariable=self.status_var, fg="gray",
                 anchor="w", relief=tk.SUNKEN).pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

    # ── Helpers ────────────────────────────────────────────────

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select text or CSV files",
            filetypes=[("Text & CSV files", "*.txt *.csv"), ("Text files", "*.txt"),
                       ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert(tk.END, os.path.basename(p))
        self._update_status()

    def remove_selected(self):
        for idx in reversed(self.listbox.curselection()):
            self.listbox.delete(idx)
            del self.files[idx]
        self._update_status()

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.files.clear()
        self._update_status()

    def move_up(self):
        sel = list(self.listbox.curselection())
        if not sel or sel[0] == 0:
            return
        for idx in sel:
            self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
            label = self.listbox.get(idx)
            self.listbox.delete(idx)
            self.listbox.insert(idx - 1, label)
        self.listbox.selection_clear(0, tk.END)
        for idx in sel:
            self.listbox.selection_set(idx - 1)

    def move_down(self):
        sel = list(self.listbox.curselection())
        if not sel or sel[-1] == len(self.files) - 1:
            return
        for idx in reversed(sel):
            self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
            label = self.listbox.get(idx)
            self.listbox.delete(idx)
            self.listbox.insert(idx + 1, label)
        self.listbox.selection_clear(0, tk.END)
        for idx in sel:
            self.listbox.selection_set(idx + 1)

    def _update_status(self):
        n = len(self.files)
        self.status_var.set(f"{n} file(s) queued." if n else "No files added yet.")

    # ── Core logic ─────────────────────────────────────────────

    def combine_files(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add at least one file first.")
            return

        # Determine file type by majority extension
        exts = [os.path.splitext(f)[1].lower() for f in self.files]
        is_csv = exts.count(".csv") > exts.count(".txt")

        default_ext = ".csv" if is_csv else ".txt"
        out_path = filedialog.asksaveasfilename(
            title="Save combined file as",
            defaultextension=default_ext,
            filetypes=[("CSV file", "*.csv"), ("Text file", "*.txt"), ("All files", "*.*")]
        )
        if not out_path:
            return

        encoding = self.encoding_var.get()
        skip_header = self.skip_header_var.get()
        separator = self.separator_var.get()

        try:
            if out_path.endswith(".csv"):
                self._combine_csv(out_path, encoding, skip_header)
            else:
                self._combine_text(out_path, encoding, separator)

            messagebox.showinfo("Done", f"Files combined successfully!\n\nSaved to:\n{out_path}")
            self.status_var.set(f"Saved → {os.path.basename(out_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    def _combine_csv(self, out_path, encoding, skip_header):
        with open(out_path, "w", newline="", encoding=encoding) as out_file:
            writer = None
            for i, path in enumerate(self.files):
                file_enc = encoding
                with open(path, "r", newline="", encoding=file_enc, errors="replace") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if not rows:
                    continue
                if writer is None:
                    writer = csv.writer(out_file)
                    writer.writerows(rows)          # write header + data for first file
                else:
                    start = 1 if skip_header and len(rows) > 1 else 0
                    writer.writerows(rows[start:])

    def _combine_text(self, out_path, encoding, separator):
        sep_map = {
            "newline": "\n",
            "blank line": "\n\n",
            "none": "",
        }
        with open(out_path, "w", encoding=encoding) as out_file:
            for i, path in enumerate(self.files):
                with open(path, "r", encoding=encoding, errors="replace") as f:
                    content = f.read()
                if i > 0:
                    if separator == "--- filename ---":
                        out_file.write(f"\n\n--- {os.path.basename(path)} ---\n\n")
                    else:
                        out_file.write(sep_map.get(separator, "\n"))
                out_file.write(content)
                # Ensure file ends with newline before next chunk
                if content and not content.endswith("\n") and separator != "none":
                    out_file.write("\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCombinerApp(root)
    root.mainloop()
