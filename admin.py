import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, ttk

SERVER_IP = "localhost"  # Mude para o IP da sua máquina na rede do trabalho
WS_URL = f"ws://{SERVER_IP}:8000/ws/ADMIN"

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Chamados TI - ADM")
        self.root.geometry("700x450")
        
        self.current_chat_target = None
        self.ws = None
        
        self.create_widgets()
        self.connect_server()

    def create_widgets(self):
        # Container Principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lado Esquerdo: Lista de Chamados Ativos
        left_frame = ttk.LabelFrame(main_frame, text=" Chamados Pendentes ", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=250)
        
        self.calls_listbox = tk.Listbox(left_frame, font=("Arial", 10))
        self.calls_listbox.pack(fill=tk.BOTH, expand=True)
        self.calls_listbox.bind("<<ListboxSelect>>", self.on_select_call)
        
        # Lado Direito: Janela de Chat
        self.right_frame = ttk.LabelFrame(main_frame, text=" Atendimento ", padding="5")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.chat_area = tk.Text(self.right_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 10))
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        entry_frame = ttk.Frame(self.right_frame)
        entry_frame.pack(fill=tk.X)
        
        self.msg_entry = ttk.Entry(entry_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        
        send_btn = ttk.Button(entry_frame, text="Enviar", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

    def connect_server(self):
        from websocket import create_connection  # Requer: pip install websocket-client
        def listen():
            try:
                self.ws = create_connection(WS_URL)
                self.log_chat("Sistema conectado ao servidor de rede.\n")
                while True:
                    result = self.ws.recv()
                    data = json.loads(result)
                    self.root.after(0, self.handle_incoming_data, data)
            except Exception as e:
                self.log_chat(f"Erro de conexão com o servidor: {e}\n")

        threading.Thread(target=listen, daemon=True).start()

    def handle_incoming_data(self, data):
        dtype = data.get("type")
        sender = data.get("sender")
        msg = data.get("message")
        
        if dtype == "sys_status":
            self.log_chat(f"[SISTEMA] {msg}\n")
        
        elif dtype == "call":
            # Alerta sonoro básico do sistema operacional
            self.root.bell() 
            item_text = f"{sender} ({data.get('sector')})"
            if item_text not in self.calls_listbox.get(0, tk.END):
                self.calls_listbox.insert(tk.END, item_text)
            self.log_chat(f"⚠️ NOVO CHAMADO de {item_text}!\n")
            
        elif dtype == "chat":
            if self.current_chat_target == sender:
                self.log_chat(f"[{sender}]: {msg}\n")
            else:
                self.log_chat(f"💬 Nova mensagem pendente de {sender}...\n")

    def on_select_call(self, event):
        selection = self.calls_listbox.curselection()
        if selection:
            selected_text = self.calls_listbox.get(selection[0])
            # Extrai o nome da máquina antes do parêntese do setor
            self.current_chat_target = selected_text.split(" (")[0]
            self.right_frame.config(text=f" Chat com: {selected_text} ")
            self.log_chat(f"--- Histórico focado em {self.current_chat_target} ---\n")

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.current_chat_target and self.ws:
            payload = {
                "type": "chat",
                "target": self.current_chat_target,
                "sender": "Suporte TI",
                "message": msg
            }
            try:
                self.ws.send(json.dumps(payload))
                self.log_chat(f"[Você]: {msg}\n")
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao enviar: {e}")

    def log_chat(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    # Garanta que instalou: pip install websocket-client
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()