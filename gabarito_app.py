import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema Independente de Gabaritos")
        self.geometry("1200x700")

        self.logo_path = None
        self.logo_image = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.home_btn = ctk.CTkButton(self.sidebar, text="Home", command=self.show_home)
        self.home_btn.pack(padx=20, pady=10)

        self.modelos_btn = ctk.CTkButton(self.sidebar, text="Modelos de Gabaritos",
                                         command=self.show_modelos)
        self.modelos_btn.pack(padx=20, pady=10)

        # Main area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.show_home()

    # ================= HOME =================

    def show_home(self):
        self.clear_main()

        title = ctk.CTkLabel(self.main_frame,
                             text="Bem-vindo ao Sistema Independente de Gabaritos",
                             font=("Arial", 26))
        title.pack(pady=50)

        msg = ctk.CTkLabel(
            self.main_frame,
            text="Agradecemos por utilizar nosso sistema.\n\n"
                 "Em breve novos recursos serão implementados.",
            font=("Arial", 18),
            justify="center"
        )
        msg.pack(pady=20)

    # ================= MODELOS =================

    def show_modelos(self):
        self.clear_main()

        resposta = messagebox.askyesno("Criar Modelo",
                                       "Deseja criar um novo modelo de gabarito?")
        if resposta:
            self.show_configuracao()

    # ================= CONFIG =================

    def show_configuracao(self):
        self.clear_main()

        self.main_frame.grid_columnconfigure(1, weight=1)

        # Frame esquerdo (config)
        config_frame = ctk.CTkFrame(self.main_frame, width=300)
        config_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        # Frame direito (preview)
        preview_frame = ctk.CTkFrame(self.main_frame)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        # ======= CONFIGURAÇÕES =======

        ctk.CTkLabel(config_frame, text="Configuração do Modelo",
                     font=("Arial", 18)).pack(pady=10)

        self.qtd_questoes = ctk.CTkEntry(config_frame,
                                         placeholder_text="Quantidade de questões")
        self.qtd_questoes.pack(pady=5)
        self.qtd_questoes.bind("<KeyRelease>", lambda e: self.atualizar_preview())

        self.identificacao = ctk.CTkOptionMenu(
            config_frame,
            values=["Código de Barras", "QRCode"],
            command=lambda e: self.atualizar_preview()
        )
        self.identificacao.pack(pady=5)

        self.texto_instrucao = ctk.CTkTextbox(config_frame, height=80)
        self.texto_instrucao.pack(pady=5)
        self.texto_instrucao.bind("<KeyRelease>", lambda e: self.atualizar_preview())

        self.posicao_instrucao = ctk.CTkOptionMenu(
            config_frame,
            values=["Topo", "Rodapé"],
            command=lambda e: self.atualizar_preview()
        )
        self.posicao_instrucao.pack(pady=5)

        ctk.CTkButton(config_frame, text="Inserir Logo",
                      command=self.select_logo).pack(pady=5)

        ctk.CTkButton(config_frame, text="Atualizar Preview",
                      command=self.atualizar_preview).pack(pady=10)

        # ======= CANVAS PREVIEW =======

        self.canvas = ctk.CTkCanvas(preview_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.atualizar_preview()

    # ================= PREVIEW =================

    def atualizar_preview(self):
        self.canvas.delete("all")

        largura = 700
        altura = 900

        self.canvas.create_rectangle(20, 20, largura, altura, outline="black")

        y = 40

        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            img = Image.open(self.logo_path)
            img = img.resize((100, 100))
            self.logo_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(60, y + 50, image=self.logo_image)
        y += 120

        # Campos fixos
        self.canvas.create_text(200, y, text="Escola: XXXXXX", anchor="w")
        y += 20
        self.canvas.create_text(200, y, text="Endereço: XXXXXX", anchor="w")
        y += 20
        self.canvas.create_text(200, y, text="Sala: XXXXXX", anchor="w")
        y += 40

        # Identificação
        self.canvas.create_text(200, y,
                                text=f"Identificação: {self.identificacao.get()}",
                                anchor="w")
        y += 40

        # Questões
        qtd = self.qtd_questoes.get()
        if qtd.isdigit():
            qtd = int(qtd)
        else:
            qtd = 0

        colunas = 2
        linha_altura = 25
        x_inicial = 60

        for i in range(qtd):
            coluna = i % colunas
            linha = i // colunas

            x = x_inicial + coluna * 300
            y_questao = y + linha * linha_altura

            self.canvas.create_text(x, y_questao,
                                    text=f"{i + 1}.",
                                    anchor="w")

            for j, letra in enumerate(["A", "B", "C", "D"]):
                self.canvas.create_oval(x + 30 + j * 30,
                                        y_questao - 7,
                                        x + 45 + j * 30,
                                        y_questao + 8)
                self.canvas.create_text(x + 38 + j * 30,
                                        y_questao,
                                        text=letra)

        # Instrução
        texto = self.texto_instrucao.get("0.0", "end").strip()

        if texto:
            if self.posicao_instrucao.get() == "Rodapé":
                self.canvas.create_text(350, altura - 30,
                                        text=texto,
                                        width=600)
            else:
                self.canvas.create_text(350, 30,
                                        text=texto,
                                        width=600)

    # ================= LOGO =================

    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path = path
            self.atualizar_preview()

    # ================= UTILS =================

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
