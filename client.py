import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox

SERVER_IP = "localhost"  # Mude para o IP do seu servidor na rede local
HOSTNAME = socket.gethostname()  # Pega o nome real do computador automaticamente

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Suporte TI - {HOSTNAME}")
        self.root.geometry("400(350")
        self.root.resizable(False, False)
        
        self.ws = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informações de Identificação
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Computador: {HOSTNAME}", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Campo para Setor
        sector_frame = ttk.Frame(main_frame)
        sector_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(sector_frame, text="Seu Setor:").pack(side=tk.LEFT, padx=(0, 5))
        self.sector_entry = ttk.Entry(sector_frame, width=20)
        self.sector_entry.pack(side=tk.LEFT)
        self.sector_entry.insert(0, "Recepção") # Valor padrão
        
        # Botão Gigante de Chamado de Presença
        self.call_btn = tk.Button(
            main_frame, text="🆘 SOLICITAR TI NO SETOR", 
            bg="#d9534f", fg="white", font=("Arial", 12, "bold"),
            relief=tk.RAISED, command=self.trigger_call
        )
        self.call_btn.pack(fill=tk.X, height=45, pady=(0, 15))
        
        # Área do Chat simplificado
        chat_frame = ttk.LabelFrame(main_frame, text=" Comunicação Direta ", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_area = tk.Text(chat_frame, state=tk.DISABLED, height=8, wrap=tk.WORD, font=("Arial", 9))
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        msg_frame = ttk.Frame(chat_frame)
        msg_frame.pack(fill=tk.X)
        self.msg_entry = ttk.Entry(msg_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_chat_message())
        
        self.send_btn = ttk.Button(msg_frame, text="Enviar", command=self.send_chat_message, state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT)

    def trigger_call(self):
        sector = self.sector_entry.get().strip()
        if not sector:
            messagebox.showwarning("Aviso", "Por favor, digite o seu setor antes de chamar.")
            return
            
        # Desabilita o botão para evitar cliques repetidos (Spam)
        self.call_btn.config(state=tk.DISABLED, bg="#999999", text="CHAMADO ENVIADO...")
        self.sector_entry.config(state=tk.DISABLED)
        
        # Conecta no WebSocket dinamicamente passando o ID
        client_id = f"{HOSTNAME}-{sector}"
        ws_url = f"ws://{SERVER_IP}:8000/ws/{client_id}"
        
        def connect():
            from websocket import create_connection
            try:
                self.ws = create_connection(ws_url)
                # Envia o pacote de Chamado
                payload = {
                    "type": "call",
                    "sender": HOSTNAME,
                    "sector": sector,
                    "message": "Solicitou presença no setor."
                }
                self.ws.send(json.dumps(payload))
                self.log_chat("[SISTEMA]: Chamado enviado para o Técnico. Aguarde no local.\n")
                self.send_btn.config(state=tk.NORMAL)
                
                # Loop para escutar a resposta do chat do Admin
                while True:
                    result = self.ws.recv()
                    data = json.loads(result)
                    if data.get("type") == "chat":
                        self.log_chat(f"[TI - {data.get('sender')}]: {data.get('message')}\n")
                        
            except Exception as e:
                self.log_chat(f"[ERRO]: Sem conexão com o servidor da TI. {e}\n")
                self.root.after(0, self.reset_call_button)

        threading.Thread(target=connect, daemon=True).start()

    def send_chat_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.ws:
            payload = {
                "type": "chat",
                "sender": HOSTNAME,
                "message": msg
            }
            try:
                self.ws.send(json.dumps(payload))
                self.log_chat(f"[Você]: {msg}\n")
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                self.log_chat(f"[ERRO]: Falha ao enviar mensagem: {e}\n")

    def reset_call_button(self):
        self.call_btn.config(state=tk.NORMAL, bg="#d9534f", text="🆘 SOLICITAR TI NO SETOR")
        self.sector_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.DISABLED)

    def log_chat(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop() 