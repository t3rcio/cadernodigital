import tkinter as tk
import google.generativeai as genai
import os
import os.path
import sys
import threading
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from datetime import datetime
from docx import Document

from settings import FORMAT_DATE, LOG_FILENAME, FORMAT_DATE_TIME, GOOGLE_API_KEY as GEMINI_API_KEY

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Chave da API Gemini não encontrada. Verifique seu arquivo .env ou variáveis de ambiente.")
    sys.exit(1)

def extract_text_from_image_gemini(image_path, user_prompt="Extraia todo o texto visível na imagem."):
    conteudo = ''    
    documento = Document()
    arquivo_docx = '~/{}.docx'.format(datetime.now().strftime(FORMAT_DATE_TIME))
    saida = os.path.expanduser(arquivo_docx)
    
    if not GEMINI_API_KEY:
        return "Erro: Chave da API Gemini não configurada."
    if not os.path.exists(image_path):
        return f"Erro: Arquivo de imagem não encontrado em {image_path}"

    try:
        print(f"Processando imagem: {image_path}")
        print(f"Prompt: {user_prompt}")

        generation_config = {
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        image_file = genai.upload_file(path=image_path)
        print(f"Arquivo '{image_file.name}' enviado com sucesso. URI: {image_file.uri}")

        prompt_parts = [user_prompt, image_file]
        response = model.generate_content(prompt_parts)
        extracted_text = ""
        if response and response.parts:
            extracted_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            if not extracted_text and hasattr(response, 'text'):
                extracted_text = response.text
        elif hasattr(response, 'text'):
             extracted_text = response.text
        
        conteudo = extracted_text.strip() if extracted_text else "Nenhum texto encontrado ou resposta vazia."
        for p in conteudo.split('\n'):
            documento.add_paragraph(p)
        
        documento.save(saida)
        print("Documento salvo!")
        return conteudo

    except Exception as e:
        print(f"Erro durante a extração de texto com Gemini: {e}")
        return f"Erro na API: {str(e)}"

# --- Classe da Aplicação Tkinter ---
class OCRApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("OCR com Gemini")
        self.root.geometry("600x550") # Ajuste o tamanho conforme necessário

        self.image_path = None
        self.pil_image = None
        self.tk_image = None
        self.extracted_text_content = None # Para armazenar o texto extraído

        # Botão de Seleção de Imagem (Centralizado)
        self.btn_select_image = tk.Button(self.root, text="Selecionar Imagem", command=self.select_image)
        self.btn_select_image.pack(pady=(20, 5)) # Espaçamento superior maior

        # Label para o caminho do arquivo (Centralizado)
        self.lbl_file_path = tk.Label(self.root, text="Nenhuma imagem selecionada", wraplength=400)
        self.lbl_file_path.pack(pady=(0,10))

        # Canvas para miniatura da imagem (Centralizado)
        self.canvas_image_preview = tk.Canvas(self.root, width=250, height=180, bg="lightgrey", relief=tk.SUNKEN)
        self.canvas_image_preview.pack(pady=5)
        self.lbl_preview_instruction = self.canvas_image_preview.create_text(
            125, 90, text="Pré-visualização da Imagem", fill="grey", width=230, justify=tk.CENTER
        )

        # Frame para o prompt
        prompt_frame = tk.Frame(self.root, pady=10)
        prompt_frame.pack(fill=tk.X, padx=20) # Adiciona padding horizontal

        lbl_prompt = tk.Label(prompt_frame, text="Prompt para Gemini:")
        lbl_prompt.pack(side=tk.LEFT, padx=(0,5))

        self.entry_prompt = tk.Entry(prompt_frame)
        self.entry_prompt.insert(0, "Extraia todo o texto desta imagem.")
        self.entry_prompt.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # # Botão de Extração (Centralizado)
        # self.btn_extract = tk.Button(self.root, text="Extrair Texto (OCR)", command=self.start_ocr_thread, state=tk.DISABLED)
        # self.btn_extract.pack(pady=15)

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=10)

        bottom_buttons_frame = tk.Frame(self.root)
        bottom_buttons_frame.pack(pady=10)

        self.btn_generate_doc = tk.Button(bottom_buttons_frame, text="Gerar Documento", command=self.start_ocr_thread)
        self.btn_generate_doc.pack(side=tk.LEFT, padx=10)

        self.btn_close = tk.Button(bottom_buttons_frame, text="Fechar", command=self.root.destroy)
        self.btn_close.pack(side=tk.LEFT, padx=10)

        self.lbl_status = tk.Label(self.root, text="", fg="blue")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=10)


    def select_image(self):
        path = filedialog.askopenfilename(
            title="Selecione um arquivo de imagem",
            filetypes=(("Arquivos de Imagem", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*"))
        )
        if path:
            self.image_path = path
            self.lbl_file_path.config(text=os.path.basename(path))
            #self.btn_extract.config(state=tk.NORMAL)
            self.display_image_preview(path)
            self.lbl_status.config(text="")
            self.extracted_text_content = None # Limpa texto anterior            
        else:
            self.image_path = None # Garante que image_path seja None
            self.lbl_file_path.config(text="Nenhuma imagem selecionada")
            #self.btn_extract.config(state=tk.DISABLED)
            self.clear_image_preview()
            self.extracted_text_content = None

    def display_image_preview(self, image_path):
        try:
            self.pil_image = Image.open(image_path)
            canvas_w = self.canvas_image_preview.winfo_width()
            canvas_h = self.canvas_image_preview.winfo_height()
            if canvas_w <= 1 or canvas_h <= 1: # Canvas pode não ter sido desenhado ainda
                canvas_w, canvas_h = 250, 180 # Usa valores padrão

            img_w, img_h = self.pil_image.size
            ratio = min(canvas_w/img_w, canvas_h/img_h)
            new_w, new_h = int(img_w * ratio), int(img_h * ratio)
            
            resized_image = self.pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized_image)
            
            self.canvas_image_preview.delete("all")
            self.canvas_image_preview.create_image(canvas_w/2, canvas_h/2, anchor=tk.CENTER, image=self.tk_image)

        except Exception as e:
            print(f"Erro ao carregar pré-visualização da imagem: {e}")
            self.clear_image_preview(error=True)

    def clear_image_preview(self, error=False):
        self.canvas_image_preview.delete("all")
        canvas_w = self.canvas_image_preview.winfo_width() or 250
        canvas_h = self.canvas_image_preview.winfo_height() or 180
        message = "Erro ao carregar imagem" if error else "Pré-visualização da Imagem"
        self.lbl_preview_instruction = self.canvas_image_preview.create_text(
            canvas_w/2, canvas_h/2, text=message, fill="grey", width=canvas_w-20, justify=tk.CENTER
        )
        self.tk_image = None

    def start_ocr_thread(self):
        if not self.image_path:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return
        
        if not GEMINI_API_KEY:
            messagebox.showerror("Erro de Configuração", "A chave da API Gemini não foi configurada. Verifique seu arquivo .env.")
            return

        user_prompt = self.entry_prompt.get() or "Extraia todo o texto desta imagem."
        
        # self.btn_extract.config(state=tk.DISABLED)
        self.btn_select_image.config(state=tk.DISABLED)
        self.btn_generate_doc.config(state=tk.DISABLED) # Desabilita durante processamento
        self.lbl_status.config(text="Processando, por favor aguarde...", fg="blue")
        self.extracted_text_content = None # Limpa antes de nova extração

        thread = threading.Thread(target=self.run_ocr, args=(self.image_path, user_prompt))
        thread.daemon = True
        thread.start()

    def run_ocr(self, image_path, user_prompt):
        success = True
        texto = ''
        try:
            texto = extract_text_from_image_gemini(image_path, user_prompt)            
        except Exception as e:
            success = False
            texto = f"Erro inesperado na thread de OCR: {e}"
            print(texto)
        self.root.after(0, self.update_gui_with_result, texto, success)

    def update_gui_with_result(self, text, success=True):
        # self.btn_extract.config(state=tk.NORMAL)
        self.btn_select_image.config(state=tk.NORMAL)
        
        if success:
            self.extracted_text_content = text
            if "Erro:" in text or "Nenhum texto encontrado" in text: # Checagem interna da função Gemini
                self.lbl_status.config(text=text if text else "Falha na extração.", fg="orange")
                self.btn_generate_doc.config(state=tk.DISABLED)
                if "Erro:" in text:
                     messagebox.showwarning("OCR", text)
            else:
                self.lbl_status.config(text="Extração Concluída!", fg="green")
                self.btn_generate_doc.config(state=tk.NORMAL) # Habilita botão
                messagebox.showinfo("Sucesso", "Documento gerado!")
        else:
            self.extracted_text_content = None
            self.lbl_status.config(text="Erro na extração.", fg="red")
            self.btn_generate_doc.config(state=tk.DISABLED)
            messagebox.showerror("Erro de OCR", text)

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror(
            "Erro de Configuração da API",
            "A chave da API Gemini (GEMINI_API_KEY ou GOOGLE_API_KEY) não foi encontrada.\n"
            "Por favor, configure-a no arquivo .env ou como variável de ambiente.\n"
            "O programa será encerrado."
        )
        root_temp.destroy()
        exit()

    main_window = tk.Tk()
    app = OCRApp(main_window)
    main_window.mainloop()