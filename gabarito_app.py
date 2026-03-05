import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import qrcode
import barcode
from barcode.writer import ImageWriter
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Editor Visual de Gabaritos")
        self.geometry("1300x750")

        self.logo_path = None
        self.logo_image = None
        self.qr_image = None
        self.barcode_image = None

        # ================= SIDEBAR PROFISSIONAL =================

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # ================= MAIN FRAME =================

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Topo com Logo e Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="  Image Example",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Função para ativar botão selecionado
        def select_menu(btn):
            self.btn_inicio.configure(fg_color="transparent")
            self.modelos_btn.configure(fg_color="transparent")

            btn.configure(fg_color=("gray75", "gray25"))

        # Botão Início
        self.btn_inicio = ctk.CTkButton(
            self.sidebar,
            text=" Início",
            height=40,
            anchor="w",
            corner_radius=0,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda: [select_menu(self.btn_inicio), self.show_home()]
        )
        self.btn_inicio.grid(row=1, column=0, sticky="ew")

        # Botão Modelos
        self.modelos_btn = ctk.CTkButton(
            self.sidebar,
            text=" Modelos de Gabaritos",
            height=40,
            anchor="w",
            corner_radius=0,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda: [select_menu(self.modelos_btn), self.show_editor()]
        )
        self.modelos_btn.grid(row=2, column=0, sticky="ew")

        # Rodapé (System Option)
        self.appearance_mode = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Light", "Dark", "System"],
            command=ctk.set_appearance_mode
        )
        self.appearance_mode.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # Define Home como ativo inicial
        select_menu(self.btn_inicio)
        # So marcar o botao nao renderiza a tela; precisamos chamar a view inicial.
        self.show_home()

    # ================= HOME =================

    def show_home(self):
        self.clear_main()

        ctk.CTkLabel(self.main_frame,
                     text="Sistema Independente de Gabaritos",
                     font=("Arial", 28)).pack(pady=60)

        ctk.CTkLabel(self.main_frame,
                     text="Obrigado por usar o sistema.\n\n"
                          "Novos recursos avançados serão implementados em breve.",
                     font=("Arial", 18),
                     justify="center").pack()

    # ================= EDITOR =================

    def show_editor(self):
        self.clear_main()

        self.main_frame.grid_columnconfigure(1, weight=1)

        config = ctk.CTkFrame(self.main_frame, width=300)
        config.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        preview_frame = ctk.CTkFrame(self.main_frame)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        # CONFIG
        ctk.CTkLabel(config, text="Configuração", font=("Arial", 18)).pack(pady=10)

        self.qtd_questoes = ctk.CTkEntry(config, placeholder_text="Qtd questões")
        self.qtd_questoes.pack(pady=5)
        self.qtd_questoes.bind("<KeyRelease>", lambda e: self.update_preview())

        self.alternativas = ctk.CTkOptionMenu(
            config,
            values=["4 Alternativas", "5 Alternativas"],
            command=lambda e: self.update_preview()
        )
        self.alternativas.pack(pady=5)

        self.identificacao = ctk.CTkOptionMenu(
            config,
            values=["Nenhuma", "QRCode", "Código de Barras"],
            command=lambda e: self.update_preview()
        )
        self.identificacao.pack(pady=5)

        self.texto_instrucao = ctk.CTkTextbox(config, height=70)
        self.texto_instrucao.pack(pady=5)
        self.texto_instrucao.bind("<KeyRelease>", lambda e: self.update_preview())

        self.posicao_instrucao = ctk.CTkOptionMenu(
            config,
            values=["Topo", "Rodapé"],
            command=lambda e: self.update_preview()
        )
        self.posicao_instrucao.pack(pady=5)

        ctk.CTkButton(config, text="Salvar Modelo",command=self.save_model).pack(pady=5)

        ctk.CTkButton(config, text="Carregar Modelo", command=self.load_model).pack(pady=5)

        # CANVAS
        self.canvas = ctk.CTkCanvas(preview_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ctk.CTkScrollbar(preview_frame, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.configure(scrollregion=(0, 0, 900, 1200))

        self.update_preview()

    # ================= PREVIEW =================

    def update_preview(self):
        self.canvas.delete("all")

        width = 800
        height = 1100

        self.canvas.create_rectangle(50, 50, width, height)

        y = 80

        # Identificação visual
        tipo_id = self.identificacao.get()

        if tipo_id == "QRCode":
            qr = qrcode.make("IDENTIFICACAO-XXXX")
            qr = qr.resize((100, 100))
            self.qr_image = ImageTk.PhotoImage(qr)
            self.canvas.create_image(width - 80, 120, image=self.qr_image)

        elif tipo_id == "Código de Barras":
            code = barcode.get('code128', "1234567890",
                               writer=ImageWriter())
            filename = "barcode_temp"
            code.save(filename)
            img = Image.open(filename + ".png")
            img = img.resize((200, 80))
            self.barcode_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(width - 150, 120,
                                     image=self.barcode_image)

        # Questões
        qtd = self.qtd_questoes.get()
        qtd = int(qtd) if qtd.isdigit() else 0

        alternativas = 4 if "4" in self.alternativas.get() else 5
        letras = ["A", "B", "C", "D", "E"][:alternativas]

        colunas = 2 if qtd <= 40 else 3

        for i in range(qtd):
            col = i % colunas
            row = i // colunas

            x = 100 + col * 220
            y_q = y + row * 25

            self.canvas.create_text(x, y_q,
                                    text=f"{i+1}.", anchor="w")

            for j, letra in enumerate(letras):
                self.canvas.create_oval(x + 30 + j*25,
                                        y_q - 7,
                                        x + 45 + j*25,
                                        y_q + 8)
                self.canvas.create_text(x + 38 + j*25,
                                        y_q,
                                        text=letra)

        # Instrução
        texto = self.texto_instrucao.get("0.0", "end").strip()

        if texto:
            if self.posicao_instrucao.get() == "Rodapé":
                self.canvas.create_text(width/2,
                                        height - 40,
                                        text=texto,
                                        width=600)
            else:
                self.canvas.create_text(width/2,
                                        60,
                                        text=texto,
                                        width=600)

    # ================= JSON =================

    def save_model(self):
        data = {
            "qtd": self.qtd_questoes.get(),
            "alternativas": self.alternativas.get(),
            "identificacao": self.identificacao.get(),
            "instrucao": self.texto_instrucao.get("0.0", "end"),
            "posicao": self.posicao_instrucao.get()
        }

        file = filedialog.asksaveasfilename(defaultextension=".json")
        if file:
            with open(file, "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Sucesso", "Modelo salvo!")

    def load_model(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            with open(file) as f:
                data = json.load(f)

            self.qtd_questoes.delete(0, "end")
            self.qtd_questoes.insert(0, data["qtd"])
            self.alternativas.set(data["alternativas"])
            self.identificacao.set(data["identificacao"])
            self.texto_instrucao.delete("0.0", "end")
            self.texto_instrucao.insert("0.0", data["instrucao"])
            self.posicao_instrucao.set(data["posicao"])

            self.update_preview()

            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")

            if bbox:
                self.canvas.configure(scrollregion=bbox)

    # ================= UTILS =================

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
