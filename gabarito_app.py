import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import requests
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema Independente de Gabaritos")
        self.geometry("1000x600")

        self.logo_path = None

        # ===== Layout Principal =====
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.sidebar.grid_rowconfigure(10, weight=1)

        self.home_btn = ctk.CTkButton(self.sidebar, text="Home", command=self.show_home)
        self.home_btn.grid(row=1, column=0, padx=20, pady=10)

        self.modelos_btn = ctk.CTkButton(self.sidebar, text="Modelos de Gabaritos",
                                         command=self.show_modelos)
        self.modelos_btn.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_option = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self.change_appearance
        )
        self.appearance_option.grid(row=11, column=0, padx=20, pady=20)

        # Área principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.show_home()

    # ========================
    # HOME
    # ========================
    def show_home(self):
        self.clear_main()

        title = ctk.CTkLabel(self.main_frame,
                             text="Bem-vindo ao Sistema Independente de Gabaritos",
                             font=("Arial", 24))
        title.pack(pady=40)

        msg = ctk.CTkLabel(
            self.main_frame,
            text="Agradecemos por utilizar nosso sistema.\n\n"
                 "Em breve novos recursos serão implementados\n"
                 "para tornar a geração de gabaritos ainda mais completa.",
            font=("Arial", 16),
            justify="center"
        )
        msg.pack(pady=20)

    # ========================
    # MODELOS
    # ========================
    def show_modelos(self):
        self.clear_main()

        resposta = messagebox.askyesno("Criar Modelo",
                                       "Deseja criar um novo modelo de gabarito?")

        if resposta:
            self.show_configuracao()

    # ========================
    # CONFIGURAÇÃO
    # ========================
    def show_configuracao(self):
        self.clear_main()

        title = ctk.CTkLabel(self.main_frame,
                             text="Configuração do Modelo",
                             font=("Arial", 22))
        title.pack(pady=20)

        # Quantidade de questões
        self.qtd_questoes = ctk.CTkEntry(self.main_frame,
                                         placeholder_text="Quantidade de questões")
        self.qtd_questoes.pack(pady=10)

        # Tipo identificação
        self.identificacao = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Código de Barras", "QRCode"]
        )
        self.identificacao.pack(pady=10)

        # Texto instrução
        self.texto_instrucao = ctk.CTkTextbox(self.main_frame, height=80, width=400)
        self.texto_instrucao.pack(pady=10)
        self.texto_instrucao.insert("0.0", "Digite aqui a instrução ou observação...")

        # Posição instrução
        self.posicao_instrucao = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Topo", "Rodapé"]
        )
        self.posicao_instrucao.pack(pady=10)

        # Logo
        logo_btn = ctk.CTkButton(self.main_frame, text="Inserir Logo (Arquivo)",
                                 command=self.select_logo)
        logo_btn.pack(pady=5)

        logo_url_btn = ctk.CTkButton(self.main_frame, text="Inserir Logo (URL)",
                                     command=self.download_logo)
        logo_url_btn.pack(pady=5)

        # Visualizar PDF
        visualizar_btn = ctk.CTkButton(self.main_frame,
                                       text="Visualizar Modelo em PDF",
                                       command=self.gerar_pdf_preview)
        visualizar_btn.pack(pady=20)

    # ========================
    # FUNÇÕES AUXILIARES
    # ========================
    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path = path
            messagebox.showinfo("Logo", "Logo carregada com sucesso!")

    def download_logo(self):
        url = ctk.CTkInputDialog(text="Digite a URL da imagem:", title="Download Logo")
        link = url.get_input()

        if link:
            try:
                response = requests.get(link)
                img = Image.open(BytesIO(response.content))
                path = "logo_temp.png"
                img.save(path)
                self.logo_path = path
                messagebox.showinfo("Logo", "Logo baixada com sucesso!")
            except:
                messagebox.showerror("Erro", "Não foi possível baixar a imagem.")

    def gerar_pdf_preview(self):
        qtd = self.qtd_questoes.get()
        tipo_id = self.identificacao.get()
        instrucao = self.texto_instrucao.get("0.0", "end")

        if not qtd.isdigit():
            messagebox.showerror("Erro", "Quantidade de questões inválida.")
            return

        doc = SimpleDocTemplate("preview_modelo.pdf")
        elementos = []
        estilos = getSampleStyleSheet()

        elementos.append(Paragraph("<b>MODELO DE GABARITO</b>", estilos["Title"]))
        elementos.append(Spacer(1, 0.5 * cm))

        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            elementos.append(RLImage(self.logo_path, width=4*cm, height=4*cm))
            elementos.append(Spacer(1, 0.5 * cm))

        # Campos fixos (fase atual)
        elementos.append(Paragraph("Escola: XXXXXX", estilos["Normal"]))
        elementos.append(Paragraph("Endereço: XXXXXX", estilos["Normal"]))
        elementos.append(Paragraph("Sala: XXXXXX", estilos["Normal"]))
        elementos.append(Spacer(1, 0.5 * cm))

        # Identificação
        elementos.append(Paragraph(f"Identificação: {tipo_id}", estilos["Normal"]))
        elementos.append(Spacer(1, 0.5 * cm))

        # Questões
        elementos.append(Paragraph(f"Quantidade de Questões: {qtd}", estilos["Normal"]))
        elementos.append(Spacer(1, 1 * cm))

        # Instrução
        elementos.append(Paragraph(instrucao, estilos["Normal"]))

        doc.build(elementos)

        messagebox.showinfo("PDF", "Preview gerado como preview_modelo.pdf")

    def change_appearance(self, modo):
        ctk.set_appearance_mode(modo)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
