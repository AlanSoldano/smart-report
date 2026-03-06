import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

MAX_PREVIEW_ROWS = 10000

class PreviewPopup(ctk.CTkToplevel):

    def __init__(self, parent, df):
        self.df_original = df.copy()
        self.df_actual = df.copy()
        self.row_tags = {} 
        super().__init__(parent)
        self.title("Vista previa del dataset")
        self.geometry("950x550")
        self.grab_set()

        # Estado edicion
        self.editing_enabled = False
        self._sort_column = {}  # para toggle asc/desc por columna

        # -------- TITULO --------
        title = ctk.CTkLabel(
            self,
            text="Vista previa del dataset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)

        self.rows, self.cols = df.shape
        self.preview_df = df.head(MAX_PREVIEW_ROWS)

        # -------- INFO FILAS/COLUMNAS --------
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray"
        )
        self.info_label.pack(pady=(0, 10))
        self.update_info_label()

        # -------- BARRA DE BUSQUEDA --------
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Selector de columna (solo lectura)
        self.column_selector = ctk.CTkComboBox(
            control_frame,
            values=list(df.columns),
            width=150,
            state="readonly"
        )
        self.column_selector.set(df.columns[0])
        self.column_selector.pack(side="left", padx=5)
        self.column_selector.bind("<<ComboboxSelected>>", lambda e: self.update_sort_options())

        # Entrada de busqueda
        self.search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Buscar valor..."
        )
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_data)

        # Boton buscar
        search_button = ctk.CTkButton(
            control_frame,
            text="Buscar",
            width=80,
            command=self.search_data
        )
        search_button.pack(side="left", padx=5)

        # Boton reset
        reset_button = ctk.CTkButton(
            control_frame,
            text="Reset",
            width=80,
            command=self.reset_data
        )
        reset_button.pack(side="left", padx=5)

        # -------- CONTENEDOR --------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1f1f1f",
            foreground="white",
            fieldbackground="#1f1f1f",
            rowheight=28,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#2b2b2b",
            foreground="white",
            relief="flat"
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#3a3a3a")],
            foreground=[("active", "white")]
        )
        style.map(
            "Treeview",
            background=[("selected", "#2563eb")]
        )

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            table_frame,
            columns=list(self.preview_df.columns),
            show="headings",
            selectmode="none",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # --- Headers ---
        for col in self.preview_df.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self._sort_column[col] = True
            self.tree.column(col, anchor="center", width=120)

        self.tree.tag_configure("green", background="#1f3d2b")
        self.tree.tag_configure("red", background="#3d1f1f")

        for _, row in self.preview_df.iterrows():
            self.tree.insert("", "end", values=list(row))

        # Bind de verde/rojo
        self.tree.bind("<Button-1>", self.mark_green)
        self.tree.bind("<Button-3>", self.mark_red)

        # -------- BOTONES CERRAR / EDITAR / GUARDAR --------
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10, padx=20, fill="x")

        self.close_button = ctk.CTkButton(button_frame, text="Cerrar", command=self.destroy)
        self.close_button.pack(side="right", padx=5)

        # Boton edicion
        self.edit_button = ctk.CTkButton(button_frame, text="Editar fila", command=self.toggle_editing)
        self.edit_button.pack(side="right", padx=5)

        self.save_button = ctk.CTkButton(button_frame, text="Guardar copia", command=self.save_copy)
        self.save_button.pack(side="right", padx=5)

    # ----------------- TAGS -----------------
    def mark_green(self, event):
        if self.editing_enabled:
            return
        item = self.tree.identify_row(event.y)
        if item:
            row_values = tuple(str(v) for v in self.tree.item(item, "values"))
            current_tags = self.tree.item(item, "tags")
            if "green" in current_tags:
                self.tree.item(item, tags=())
                self.row_tags[row_values] = ""
            else:
                self.tree.item(item, tags=("green",))
                self.row_tags[row_values] = "green"
        self.update_info_label()

    def mark_red(self, event):
        if self.editing_enabled:
            return
        item = self.tree.identify_row(event.y)
        if item:
            row_values = tuple(str(v) for v in self.tree.item(item, "values"))
            current_tags = self.tree.item(item, "tags")
            if "red" in current_tags:
                self.tree.item(item, tags=())
                self.row_tags[row_values] = ""
            else:
                self.tree.item(item, tags=("red",))
                self.row_tags[row_values] = "red"
        self.update_info_label()

    # ----------------- ACTUALIZAR TABLA -----------------
    def update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        for _, row in df.iterrows():
            row_values = tuple(str(v) for v in row)
            tag = self.row_tags.get(row_values, "")
            self.tree.insert("", "end", values=list(row), tags=(tag,) if tag else ())
        self.update_info_label()

    def search_data(self, event=None):
        column = self.column_selector.get()
        value = self.search_entry.get().strip().lower()
        df = self.df_original.copy()
        if value == "":
            self.df_actual = df
        else:
            mask = df[column].astype(str).str.lower().str.contains(value, na=False)
            self.df_actual = df[mask]
        self.update_table(self.df_actual)

    def reset_data(self):
        self.df_actual = self.df_original.copy()
        self.update_table(self.df_actual)

    # ----------------- INFO FILAS -----------------
    def update_info_label(self):
        green_count = sum(1 for v in self.row_tags.values() if v == "green")
        red_count = sum(1 for v in self.row_tags.values() if v == "red")
        text = f"Filas: {self.rows} | Columnas: {self.cols} | Verde: {green_count} | Rojo: {red_count}"
        if len(self.df_original) > MAX_PREVIEW_ROWS:
            text += f" (mostrando primeras {MAX_PREVIEW_ROWS})"
        self.info_label.configure(text=text)

    # ----------------- ORDEN POR CLICK HEADER -----------------
    def sort_column(self, column):
        ascending = self._sort_column.get(column, True)
        try:
            self.df_actual = self.df_actual.sort_values(by=column, ascending=ascending)
        except:
            pass
        self.update_table(self.df_actual)
        self._sort_column[column] = not ascending

    # ----------------- TOGGLE EDICIÓN -----------------
    def toggle_editing(self):
        self.editing_enabled = not self.editing_enabled
        if self.editing_enabled:
            self.edit_button.configure(text="Edición activada")
            self.tree.unbind("<Button-1>")
            self.tree.unbind("<Button-3>")
            self.tree.bind("<Double-1>", self.start_cell_edit)
        else:
            self.edit_button.configure(text="Editar fila")
            self.tree.bind("<Button-1>", self.mark_green)
            self.tree.bind("<Button-3>", self.mark_red)
            self.tree.unbind("<Double-1>")

    def start_cell_edit(self, event):
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_index = int(col_id.replace("#", "")) - 1
        value = self.tree.set(row_id, column=self.preview_df.columns[col_index])

        entry = tk.Entry(self.tree)
        x, y, width, height = self.tree.bbox(row_id, col_id)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event=None):
            self.tree.set(row_id, column=self.preview_df.columns[col_index], value=entry.get())
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    # ----------------- GUARDAR COPIA -----------------
    def save_copy(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not file_path:
            return

        all_rows = []
        for child in self.tree.get_children():
            values = self.tree.item(child, "values")
            all_rows.append(values)

        new_df = pd.DataFrame(all_rows, columns=self.df_actual.columns)

        if file_path.endswith(".xlsx"):
            new_df.to_excel(file_path, index=False)
        else:
            new_df.to_csv(file_path, index=False)
        messagebox.showinfo("Guardar copia", f"Archivo guardado en {file_path}")
