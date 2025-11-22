import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import time
import threading
import random

# --- CONFIGURAÇÕES ---
CONFIG = {
    "TANQUE_MAX": 10000,
    "BOMBA_VAZAO": 50, # Litros por ciclo de atualização
}

class SistemaUnico(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly") # Tema escuro profissional
        self.title("Painel de Controle Unificado v6.0")
        self.geometry("1100x700")
        
        # --- DADOS DO SISTEMA ---
        self.agua = 5000.0 # Começa com água para você testar já!
        self.bomba_ligada = False
        self.planta_ativa = None
        
        # Dados das plantas (Umidade de 0 a 100)
        self.plantas = {
            "Morango 🍓": 40.0,
            "Cenoura 🥕": 60.0,
            "Batata 🥔": 20.0, # Começa seca para precisar regar
            "Milho 🌽": 80.0
        }
        
        # Dicionário para guardar os componentes da tela e atualizar depois
        self.widgets_plantas = {} 

        # --- MONTAGEM DA TELA ---
        self.criar_interface()
        
        # --- THREADS (Processos paralelos) ---
        self.rodando = True
        threading.Thread(target=self.loop_fisica, daemon=True).start()
        
        # Atualização visual
        self.atualizar_tela_loop()

    def criar_interface(self):
        # Título
        ttk.Label(self, text="CENTRAL DE IRRIGAÇÃO", font=("Impact", 30), bootstyle="inverse-light").pack(pady=10, fill=X)

        # === ÁREA SUPERIOR: O TANQUE ===
        frame_tanque = ttk.Labelframe(self, text=" RESERVATÓRIO PRINCIPAL ", padding=15, bootstyle="info")
        frame_tanque.pack(pady=10, padx=20, fill=X)
        
        self.lbl_litros = ttk.Label(frame_tanque, text="5000 / 10000 L", font=("Arial", 20, "bold"), bootstyle="info")
        self.lbl_litros.pack(side=LEFT, padx=20)
        
        self.bar_agua = ttk.Progressbar(frame_tanque, maximum=CONFIG["TANQUE_MAX"], value=5000, bootstyle="info-striped", length=400)
        self.bar_agua.pack(side=LEFT, fill=X, expand=YES, padx=20)
        
        ttk.Button(frame_tanque, text="ENCHER TANQUE (+)", bootstyle="success", command=self.encher_tanque).pack(side=RIGHT)

        # === ÁREA CENTRAL: AS PLANTAS ===
        frame_plantas = ttk.Labelframe(self, text=" CONTROLE DE SETORES ", padding=15, bootstyle="primary")
        frame_plantas.pack(pady=10, padx=20, fill=BOTH, expand=YES)

        # Cria uma linha para cada planta automaticamente
        for nome_planta in self.plantas:
            linha = ttk.Frame(frame_plantas, padding=5, bootstyle="secondary")
            linha.pack(fill=X, pady=5)
            
            # Nome
            ttk.Label(linha, text=nome_planta, font=("Arial", 14, "bold"), width=15, background="#444").pack(side=LEFT, padx=10)
            
            # Barra de Umidade
            ttk.Label(linha, text="Umidade:", background="#444", foreground="white").pack(side=LEFT)
            barra = ttk.Progressbar(linha, maximum=100, value=self.plantas[nome_planta], bootstyle="warning-striped", length=300)
            barra.pack(side=LEFT, padx=10)
            
            # Texto da %
            lbl_pct = ttk.Label(linha, text=f"{self.plantas[nome_planta]:.1f}%", font=("Arial", 10, "bold"), width=6, background="#444", foreground="white")
            lbl_pct.pack(side=LEFT)
            
            # Botão de Ação
            # IMPORTANTE: O comando usa 'lambda' para saber qual botão é qual
            btn = ttk.Button(linha, text="LIGAR IRRIGAÇÃO", bootstyle="danger", width=20,
                             command=lambda p=nome_planta: self.clique_irrigar(p))
            btn.pack(side=RIGHT, padx=10)
            
            # Guarda as referências para atualizar depois
            self.widgets_plantas[nome_planta] = {
                "barra": barra,
                "texto": lbl_pct,
                "botao": btn
            }

        # === ÁREA INFERIOR: STATUS DA BOMBA ===
        self.lbl_status = ttk.Label(self, text="STATUS DO SISTEMA: AGUARDANDO COMANDO...", font=("Courier", 12), bootstyle="inverse-dark")
        self.lbl_status.pack(side=BOTTOM, fill=X, ipady=5)

    # --- LÓGICA DO BOTÃO ---
    def clique_irrigar(self, planta):
        print(f"Clicou em: {planta}") # Vai aparecer no seu terminal do VS Code
        
        if self.bomba_ligada:
            messagebox.showwarning("Ocupado", "A bomba já está ligada em outro setor!")
            return
        
        if self.agua <= 0:
            messagebox.showerror("Seca", "Tanque vazio! Encha o tanque primeiro.")
            return

        # Inicia o processo em segundo plano
        threading.Thread(target=self.processo_irrigacao, args=(planta,)).start()

    def processo_irrigacao(self, planta):
        self.bomba_ligada = True
        self.planta_ativa = planta
        self.lbl_status.config(text=f">>> BOMBA LIGADA: IRRIGANDO {planta.upper()} <<<", bootstyle="inverse-success")
        
        # Simula 4 segundos de irrigação
        for i in range(40): # 40 loops de 0.1s
            time.sleep(0.1)
            
            # Tira água do tanque
            self.agua -= 10 
            if self.agua < 0: self.agua = 0
            
            # Põe água na planta
            self.plantas[planta] += 1.5
            if self.plantas[planta] > 100: self.plantas[planta] = 100
            
        self.bomba_ligada = False
        self.planta_ativa = None
        self.lbl_status.config(text="SISTEMA PRONTO.", bootstyle="inverse-dark")
        print("Irrigação finalizada.")

    def encher_tanque(self):
        self.agua = CONFIG["TANQUE_MAX"]
        print("Tanque cheio.")

    # --- LOOP QUE ATUALIZA A TELA (10 vezes por segundo) ---
    def atualizar_tela_loop(self):
        # 1. Atualiza Tanque
        self.bar_agua['value'] = self.agua
        self.lbl_litros.config(text=f"{int(self.agua)} / {CONFIG['TANQUE_MAX']} L")
        
        # 2. Atualiza Plantas
        for planta, widgets in self.widgets_plantas.items():
            umidade = self.plantas[planta]
            
            # Atualiza a barra e o texto
            widgets['barra']['value'] = umidade
            widgets['texto'].config(text=f"{umidade:.1f}%")
            
            # Muda a cor do botão se estiver ativo
            if self.bomba_ligada and self.planta_ativa == planta:
                widgets['botao'].config(text="IRRIGANDO...", bootstyle="success", state="disabled")
            else:
                widgets['botao'].config(text="LIGAR IRRIGAÇÃO", bootstyle="danger", state="normal")
                
        # Agenda a próxima atualização
        self.after(100, self.atualizar_tela_loop)

    # --- FÍSICA (O Sol secando as plantas) ---
    def loop_fisica(self):
        while self.rodando:
            time.sleep(0.5) # A cada meio segundo
            for planta in self.plantas:
                # Seca um pouquinho
                self.plantas[planta] -= 0.1
                if self.plantas[planta] < 0: self.plantas[planta] = 0

if __name__ == "__main__":
    app = SistemaUnico()
    app.mainloop()