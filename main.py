import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from datetime import datetime
from preview_popup import PreviewPopup
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class SmartReportApp:

    def __init__(self, root):
        self.column_checkboxes = []
        self.root = root
        self.root.title("SmartReport")
        self.root.geometry("900x650")

        self.file_path = None
        self.df = None

        self.main_frame = ctk.CTkScrollableFrame(root, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="").pack(pady=30)

        self.title_label = ctk.CTkLabel(self.main_frame, 
        text="SmartReport",
        font=ctk.CTkFont(size=34, weight="bold"))

        self.title_label.pack(pady=(10, 5))

        self.subtitle = ctk.CTkLabel(self.main_frame,
        text="Generador automático de reportes inteligentes",
        font=ctk.CTkFont(size=15),
        text_color="gray")

        self.subtitle.pack(pady=(0, 30))

        self.file_container = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#1f1f1f")
        self.file_container.pack(pady=10)

        self.file_label = ctk.CTkLabel(self.file_container, 
        text="Ningún archivo seleccionado",
        font=ctk.CTkFont(size=13))

        self.file_label.pack(padx=25, pady=12)

        # -------- CONTENEDOR DE BOTONES --------
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=40)

        # Boton PDF
        self.generate_button = ctk.CTkButton(self.buttons_frame, 
        text="Generar PDF", 
        width=180, height=60,
        corner_radius=15, 
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#2563eb", hover_color="#1e4ed8",
        command=self.generate_report)

        self.generate_button.grid(row=0, column=0, padx=20)

        # Boton HTML
        self.generate_html_button = ctk.CTkButton(self.buttons_frame, 
        text="Generar HTML", 
        width=180, height=60,
        corner_radius=15, 
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#2563eb", hover_color="#1e4ed8",
        command=self.generate_html_report)

        self.generate_html_button.grid(row=0, column=1, padx=20)

        # Seleccionar archivo
        self.load_button = ctk.CTkButton(self.buttons_frame, 
        text="Seleccionar archivo", 
        width=180, height=60,
        corner_radius=15, 
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#2563eb", hover_color="#1e4ed8",
        command=self.load_file)

        self.load_button.grid(row=0, column=2, padx=20)

        # Preview
        self.preview_button = ctk.CTkButton(self.buttons_frame, 
        text="Preview", 
        width=180, height=60,
        corner_radius=15, 
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#2563eb", hover_color="#1e4ed8",
        command=self.open_preview_popup)

        self.preview_button.grid(row=0, column=3, padx=20)

        self.progress = ctk.CTkProgressBar(self.main_frame, height=12, corner_radius=20)
        self.progress.pack(pady=40, fill="x", padx=200)
        self.progress.set(0)

        # -------- COLUMN SELECTOR --------
        self.column_selector_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.column_selector_frame.pack(fill="x", padx=60, pady=(0, 20))

        self.selector_title = ctk.CTkLabel(self.column_selector_frame,
        text="Seleccionar columnas numéricas a analizar",
        font=ctk.CTkFont(size=14, weight="bold"))
        self.selector_title.pack(pady=(10, 5))

        self.checkbox_container = ctk.CTkScrollableFrame(self.column_selector_frame, height=150)
        self.checkbox_container.pack(fill="x", padx=20, pady=10)

    # -----------------------------------
    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[
            ("Todos los archivos", "*.*"),
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Archivos CSV", "*.csv"),
            ("Archivos JSON", "*.json")
        ])
        if not self.file_path:
            return
        try:
            extension = os.path.splitext(self.file_path)[1].lower()
            if extension in [".xlsx", ".xls"]:
                self.df = pd.read_excel(self.file_path)
            elif extension == ".csv":
                try:
                    self.df = pd.read_csv(self.file_path, sep=None, engine="python", encoding="utf-8")
                except:
                    self.df = pd.read_csv(self.file_path, sep=None, engine="python", encoding="latin-1")
            elif extension == ".json":
                self.df = pd.read_json(self.file_path)
            else:
                messagebox.showerror("Error", "Formato no soportado.")
                return

            self.file_label.configure(text=f"📊 {os.path.basename(self.file_path)}")

        except Exception as e:
            messagebox.showerror("Error al leer archivo", str(e))

        # Limpiar checkboxes anteriores
        for widget in self.checkbox_container.winfo_children():
            widget.destroy()
        self.column_checkboxes.clear()

        # Detectar columnas numéricas
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()

        # Configurar 2 columnas
        self.checkbox_container.grid_columnconfigure(0, weight=1)
        self.checkbox_container.grid_columnconfigure(1, weight=1)

        for i, col in enumerate(numeric_columns):
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(self.checkbox_container, text=col, variable=var)
            row = i // 2
            column = i % 2
            checkbox.grid(row=row, column=column, sticky="w", padx=20, pady=6)
            self.column_checkboxes.append((col, var))

    # -----------------------------------
    def open_preview_popup(self):
        if self.df is None:
            messagebox.showerror("Error", "Primero cargá un archivo.")
            return
        PreviewPopup(self.root, self.df)

    # -----------------------------------
    def generate_html_report(self):

        if self.df is None:
            messagebox.showerror("Error", "Primero cargá un archivo.")
            return

        numeric_columns = [col for col, var in self.column_checkboxes if var.get()]

        if not numeric_columns:
            messagebox.showerror("Error", "No seleccionaste ninguna columna.")
            return

        self.generate_html_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.progress.set(0.1)
        self.root.update()

        try:
            os.makedirs("reports_html", exist_ok=True)
            html_path = f"reports_html/Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

            html_content = f"""
            <html>
            <head>
            <meta charset="UTF-8">
            <title>SmartReport</title>

            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">

            <style>
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                background: radial-gradient(circle at top, #1e293b, #0f172a 70%);
                color: white;
            }}

            .container {{
                max-width: 1200px;
                margin: auto;
                padding: 60px 40px;
            }}

            .hero {{
                text-align: center;
                margin-bottom: 80px;
            }}

            .hero h1 {{
                font-size: 60px;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(90deg, #10b981, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .hero p {{
                font-size: 18px;
                color: #9ca3af;
                margin-top: 20px;
            }}

            .stats-bar {{
                margin-top: 35px;
                display: inline-flex;
                gap: 40px;
                background: rgba(255,255,255,0.05);
                padding: 18px 40px;
                border-radius: 60px;
                backdrop-filter: blur(12px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.6);
            }}

            .stat-item {{
                text-align: center;
            }}

            .stat-item span {{
                display: block;
                font-size: 13px;
                color: #9ca3af;
            }}

            .stat-item strong {{
                font-size: 22px;
                color: #10b981;
            }}

            .column-card {{
                background: #1f2937;
                padding: 40px;
                border-radius: 22px;
                margin-bottom: 70px;
                box-shadow: 0 30px 70px rgba(0,0,0,0.6);
            }}

            .column-card h2 {{
                font-size: 28px;
                margin-bottom: 30px;
                color: #10b981;
            }}

            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 25px;
                margin-bottom: 35px;
            }}

            .metric-card {{
                background: #111827;
                padding: 22px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            }}

            .metric-card span {{
                font-size: 13px;
                color: #9ca3af;
            }}

            .metric-card h3 {{
                margin-top: 12px;
                font-size: 22px;
                color: #10b981;
            }}

            .insight-box {{
                background: linear-gradient(135deg, #065f46, #064e3b);
                padding: 28px;
                border-radius: 18px;
                margin-bottom: 35px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            }}

            .insight-box h4 {{
                margin-top: 0;
                font-size: 18px;
                color: #34d399;
            }}

            .status-badge {{
                display: inline-block;
                padding: 8px 18px;
                border-radius: 30px;
                font-size: 12px;
                font-weight: bold;
                margin-top: 15px;
            }}

            .stable {{ background: #065f46; }}
            .warning {{ background: #92400e; }}
            .danger {{ background: #7f1d1d; }}

            img {{
                max-width: 750px;
                display: block;
                margin: 45px auto;
                border-radius: 18px;
                box-shadow: 0 25px 60px rgba(0,0,0,0.7);
            }}
            </style>
            </head>
            <body>
            <div class="container">

            <div class="hero">
                <h1>SmartReport</h1>
                <p>Plataforma avanzada de análisis automático de datos</p>

                <div class="stats-bar">
                    <div class="stat-item">
                        <span>Filas Analizadas</span>
                        <strong>{self.df.shape[0]}</strong>
                    </div>
                    <div class="stat-item">
                        <span>Columnas Totales</span>
                        <strong>{self.df.shape[1]}</strong>
                    </div>
                    <div class="stat-item">
                        <span>Columnas Procesadas</span>
                        <strong>{len(numeric_columns)}</strong>
                    </div>
                </div>
            </div>
            """

            total_columns = len(numeric_columns)

            for i, column in enumerate(numeric_columns):

                self.progress.set(0.2 + 0.7 * (i / total_columns))
                self.root.update()

                total = self.df[column].sum()
                promedio = self.df[column].mean()
                minimo = self.df[column].min()
                maximo = self.df[column].max()
                std = self.df[column].std()

                q1 = self.df[column].quantile(0.25)
                q3 = self.df[column].quantile(0.75)
                iqr = q3 - q1

                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outliers = self.df[
                    (self.df[column] < lower_bound) |
                    (self.df[column] > upper_bound)
                ]

                outlier_count = len(outliers)

                if outlier_count == 0:
                    status = "Distribución estable"
                    badge_class = "stable"
                elif outlier_count < len(self.df) * 0.05:
                    status = "Leve presencia de atípicos"
                    badge_class = "warning"
                else:
                    status = "Alta dispersión detectada"
                    badge_class = "danger"

                html_content += f"""
                <div class="column-card">
                    <h2>{column}</h2>

                    <div class="metrics-grid">
                        <div class="metric-card"><span>Total</span><h3>{round(total,2)}</h3></div>
                        <div class="metric-card"><span>Promedio</span><h3>{round(promedio,2)}</h3></div>
                        <div class="metric-card"><span>Mínimo</span><h3>{round(minimo,2)}</h3></div>
                        <div class="metric-card"><span>Máximo</span><h3>{round(maximo,2)}</h3></div>
                        <div class="metric-card"><span>Desv. Est.</span><h3>{round(std,2)}</h3></div>
                    </div>

                    <div class="insight-box">
                        <h4>Insight Automático</h4>
                        Valores atípicos: <b>{outlier_count}</b><br>
                        Rango IQR: {round(iqr,2)}<br>
                        Límite inferior: {round(lower_bound,2)}<br>
                        Límite superior: {round(upper_bound,2)}<br>
                        <div class="status-badge {badge_class}">{status}</div>
                    </div>
                """

                # Histograma
                plt.figure()
                self.df[column].plot(kind='hist', bins=20, color="#10b981")
                plt.title(f"Distribución de {column}")
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                html_content += f'<img src="data:image/png;base64,{img_b64}"/>'

                # Boxplot
                plt.figure()
                self.df.boxplot(column=column)
                plt.title(f"Boxplot de {column}")
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                html_content += f'<img src="data:image/png;base64,{img_b64}"/>'

                html_content += "</div>"

            html_content += "</div></body></html>"

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.progress.set(1)
            self.root.update()
            messagebox.showinfo("Éxito", f"HTML generado:\n{html_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.generate_html_button.configure(state="normal")
            self.load_button.configure(state="normal")
            self.progress.set(0)

    # -----------------------------------
    def generate_report(self):
        if self.df is None:
            messagebox.showerror("Error", "Primero cargá un archivo.")
            return

        numeric_columns = [col for col, var in self.column_checkboxes if var.get()]
        if not numeric_columns:
            messagebox.showerror("Error", "No seleccionaste ninguna columna.")
            return

        self.generate_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.progress.set(0.1)
        self.root.update()

        try:
            os.makedirs("reports_pdf", exist_ok=True)
            pdf_path = f"reports_pdf/Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("<b>SmartReport</b>", styles["Title"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Filas: {self.df.shape[0]} | Columnas: {self.df.shape[1]}", styles["Normal"]))
            elements.append(Spacer(1, 20))

            total_columns = len(numeric_columns)

            for i, column in enumerate(numeric_columns):
                self.progress.set(0.2 + 0.7*(i/total_columns))
                self.root.update()

                elements.append(Paragraph(f"<b>Columna: {column}</b>", styles["Heading2"]))
                elements.append(Spacer(1, 12))

                total = self.df[column].sum()
                promedio = self.df[column].mean()
                minimo = self.df[column].min()
                maximo = self.df[column].max()
                std = self.df[column].std()

                data = [
                    ["Métrica", "Valor"],
                    ["Total", round(total, 2)],
                    ["Promedio", round(promedio, 2)],
                    ["Mínimo", round(minimo, 2)],
                    ["Máximo", round(maximo, 2)],
                    ["Desviación estándar", round(std, 2)]
                ]

                table = Table(data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.grey),
                    ("GRID", (0,0), (-1,-1), 0.5, colors.black),
                    ("ALIGN",(1,1),(-1,-1),"CENTER")
                ]))

                elements.append(table)
                elements.append(Spacer(1, 20))

                # Histograma
                plt.figure()
                self.df[column].plot(kind='hist', bins=20)
                plt.title(f"Distribución de {column}")
                plt.xlabel(column)
                plt.ylabel("Frecuencia")

                buffer = BytesIO()
                plt.savefig(buffer, format="png", bbox_inches="tight")
                plt.close()
                buffer.seek(0)

                elements.append(Image(buffer, width=4*inch, height=3*inch))
                elements.append(PageBreak())

            doc.build(elements)

            self.progress.set(1)
            self.root.update()
            messagebox.showinfo("Éxito", f"PDF generado:\n{pdf_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.generate_button.configure(state="normal")
            self.load_button.configure(state="normal")
            self.progress.set(0)


# -----------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = SmartReportApp(root)
    root.mainloop()
