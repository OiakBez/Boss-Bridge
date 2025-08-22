import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
import sys
from PIL import Image, ImageTk
import datetime
import traceback

# Configuração do tema da aplicação
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BossBridgeSystem:
    def __init__(self):
        try:
            self.root = ctk.CTk()
            self.root.title("Boss Bridge - Sistema de Conexões")
            self.root.geometry("1200x700")
            self.root.resizable(True, True)
            
            # Inicializar banco de dados
            self.init_db()
            
            # Variáveis de controle
            self.current_user = None
            self.user_type = None
            self.user_name = None
            
            # Mostrar tela de login inicialmente
            self.show_login_screen()
            
        except Exception as e:
            print(f"Erro durante a inicialização: {str(e)}")
            print(traceback.format_exc())
            input("Pressione Enter para sair...")
            sys.exit(1)
    
    def init_db(self):
        """Inicializa o banco de dados SQLite com todas as tabelas necessárias"""
        try:
            self.conn = sqlite3.connect('boss_bridge.db')
            self.cursor = self.conn.cursor()
            
            # Tabela de usuários (investidores)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_completo TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    genero TEXT,
                    senha TEXT NOT NULL,
                    numero TEXT,
                    imagem_perfil TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de empresas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cnpj TEXT UNIQUE NOT NULL,
                    nome_empresa TEXT NOT NULL,
                    razao_social TEXT NOT NULL,
                    logradouro TEXT,
                    numero_endereco TEXT,
                    complemento TEXT,
                    cidade TEXT,
                    estado TEXT,
                    cep TEXT,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    imagem_perfil TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de conexões entre usuários and empresas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS conexoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    empresa_id INTEGER,
                    data_conexao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pendente',
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (empresa_id) REFERENCES empresas (id)
                )
            ''')
            
            # Tabela de mensagens
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    remetente_id INTEGER,
                    destinatario_id INTEGER,
                    tipo_remetente TEXT,
                    tipo_destinatario TEXT,
                    mensagem TEXT,
                    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lida INTEGER DEFAULT 0
                )
            ''')
            
            # Tabela de notificações
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    tipo_usuario TEXT,
                    titulo TEXT,
                    mensagem TEXT,
                    data_notificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lida INTEGER DEFAULT 0
                )
            ''')
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Erro ao inicializar o banco de dados: {str(e)}")
            print(traceback.format_exc())
            raise
    
    def hash_password(self, password):
        """Cria hash da senha para armazenamento seguro"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def show_login_screen(self):
        """Exibe a tela de login"""
        try:
            self.clear_window()
            
            # Frame principal
            login_frame = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
            login_frame.pack(expand=True, fill="both", padx=200, pady=100)
            
            # Título
            title_label = ctk.CTkLabel(
                login_frame, 
                text="BOSS BRIDGE", 
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(40, 20))
            
            subtitle_label = ctk.CTkLabel(
                login_frame, 
                text="Conectando Investidores e Empresas",
                font=ctk.CTkFont(size=16),
                text_color="#FFFFFF"
            )
            subtitle_label.pack(pady=(0, 40))
            
            # Formulário de login
            form_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
            form_frame.pack(pady=20, padx=40, fill="x")
            
            email_label = ctk.CTkLabel(form_frame, text="Email:", text_color="#FFFFFF")
            email_label.pack(anchor="w", pady=(10, 5))
            email_entry = ctk.CTkEntry(form_frame, placeholder_text="Seu email", width=300)
            email_entry.pack(pady=5, fill="x")
            
            senha_label = ctk.CTkLabel(form_frame, text="Senha:", text_color="#FFFFFF")
            senha_label.pack(anchor="w", pady=(10, 5))
            senha_entry = ctk.CTkEntry(form_frame, placeholder_text="Sua senha", show="*", width=300)
            senha_entry.pack(pady=5, fill="x")
            
            # Botões
            buttons_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
            buttons_frame.pack(pady=30)
            
            login_button = ctk.CTkButton(
                buttons_frame, 
                text="Entrar", 
                command=lambda: self.login(email_entry.get(), senha_entry.get()),
                width=120,
                fg_color="#1E90FF",
                hover_color="#0078D7"
            )
            login_button.pack(pady=10)
            
            register_button = ctk.CTkButton(
                buttons_frame, 
                text="Criar Conta", 
                command=self.show_register_options,
                width=120,
                fg_color="#2B2B2B",
                border_color="#1E90FF",
                border_width=2,
                text_color="#1E90FF",
                hover_color="#1E1E1E"
            )
            register_button.pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao exibir tela de login: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar a tela de login.")
    
    def show_register_options(self):
        """Exibe as opções de registro (usuário ou empresa)"""
        try:
            self.clear_window()
            
            # Frame principal
            options_frame = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
            options_frame.pack(expand=True, fill="both", padx=200, pady=100)
            
            # Título
            title_label = ctk.CTkLabel(
                options_frame, 
                text="Criar Conta", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(40, 20))
            
            subtitle_label = ctk.CTkLabel(
                options_frame, 
                text="Selecione o tipo de conta que deseja criar",
                font=ctk.CTkFont(size=16),
                text_color="#FFFFFF"
            )
            subtitle_label.pack(pady=(0, 40))
            
            # Opções
            buttons_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
            buttons_frame.pack(pady=50)
            
            user_button = ctk.CTkButton(
                buttons_frame, 
                text="Investidor", 
                command=self.show_user_register,
                width=200,
                height=50,
                fg_color="#1E90FF",
                hover_color="#0078D7",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            user_button.pack(pady=20)
            
            empresa_button = ctk.CTkButton(
                buttons_frame, 
                text="Empresa", 
                command=self.show_empresa_register,
                width=200,
                height=50,
                fg_color="#1E90FF",
                hover_color="#0078D7",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            empresa_button.pack(pady=20)
            
            back_button = ctk.CTkButton(
                buttons_frame, 
                text="Voltar", 
                command=self.show_login_screen,
                width=120,
                fg_color="#2B2B2B",
                border_color="#1E90FF",
                border_width=2,
                text_color="#1E90FF",
                hover_color="#1E1E1E"
            )
            back_button.pack(pady=30)
            
        except Exception as e:
            print(f"Erro ao exibir opções de registro: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar as opções de registro.")
    
    def show_user_register(self):
        """Exibe o formulário de registro de usuário"""
        try:
            self.clear_window()
            
            # Frame principal com scroll
            main_frame = ctk.CTkScrollableFrame(self.root, fg_color="#2B2B2B")
            main_frame.pack(expand=True, fill="both", padx=50, pady=50)
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame, 
                text="Cadastro de Investidor", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Formulário
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(pady=20, padx=40, fill="x")
            
            # Nome completo
            nome_label = ctk.CTkLabel(form_frame, text="Nome Completo:", text_color="#FFFFFF")
            nome_label.grid(row=0, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            nome_entry = ctk.CTkEntry(form_frame, placeholder_text="Seu nome completo", width=300)
            nome_entry.grid(row=0, column=1, pady=(10, 5), sticky="ew")
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email:", text_color="#FFFFFF")
            email_label.grid(row=1, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            email_entry = ctk.CTkEntry(form_frame, placeholder_text="Seu email", width=300)
            email_entry.grid(row=1, column=1, pady=(10, 5), sticky="ew")
            
            # Gênero
            genero_label = ctk.CTkLabel(form_frame, text="Gênero:", text_color="#FFFFFF")
            genero_label.grid(row=2, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            genero_var = ctk.StringVar(value="Selecione")
            genero_option = ctk.CTkOptionMenu(
                form_frame, 
                variable=genero_var,
                values=["Masculino", "Feminino", "Outro", "Prefiro não informar"]
            )
            genero_option.grid(row=2, column=1, pady=(10, 5), sticky="w")
            
            # Número
            numero_label = ctk.CTkLabel(form_frame, text="Número:", text_color="#FFFFFF")
            numero_label.grid(row=3, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            numero_entry = ctk.CTkEntry(form_frame, placeholder_text="Seu número de telefone", width=300)
            numero_entry.grid(row=3, column=1, pady=(10, 5), sticky="ew")
            
            # Senha
            senha_label = ctk.CTkLabel(form_frame, text="Senha:", text_color="#FFFFFF")
            senha_label.grid(row=4, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            senha_entry = ctk.CTkEntry(form_frame, placeholder_text="Crie uma senha", show="*", width=300)
            senha_entry.grid(row=4, column=1, pady=(10, 5), sticky="ew")
            
            # Confirmar senha
            confirmar_label = ctk.CTkLabel(form_frame, text="Confirmar Senha:", text_color="#FFFFFF")
            confirmar_label.grid(row=5, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            confirmar_entry = ctk.CTkEntry(form_frame, placeholder_text="Confirme sua senha", show="*", width=300)
            confirmar_entry.grid(row=5, column=1, pady=(10, 5), sticky="ew")
            
            # Configurar peso das colunas
            form_frame.columnconfigure(1, weight=1)
            
            # Botões
            buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            buttons_frame.pack(pady=30)
            
            register_button = ctk.CTkButton(
                buttons_frame, 
                text="Concluir Cadastro", 
                command=lambda: self.register_user(
                    nome_entry.get(),
                    email_entry.get(),
                    genero_var.get(),
                    numero_entry.get(),
                    senha_entry.get(),
                    confirmar_entry.get()
                ),
                width=150,
                fg_color="#1E90FF",
                hover_color="#0078D7"
            )
            register_button.pack(pady=10, side="left", padx=10)
            
            back_button = ctk.CTkButton(
                buttons_frame, 
                text="Voltar", 
                command=self.show_register_options,
                width=120,
                fg_color="#2B2B2B",
                border_color="#1E90FF",
                border_width=2,
                text_color="#1E90FF",
                hover_color="#1E1E1E"
            )
            back_button.pack(pady=10, side="left", padx=10)
            
        except Exception as e:
            print(f"Erro ao exibir formulário de usuário: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar o formulário de cadastro.")
    
    def show_empresa_register(self):
        """Exibe o formulário de registro de empresa"""
        try:
            self.clear_window()
            
            # Frame principal com scroll
            main_frame = ctk.CTkScrollableFrame(self.root, fg_color="#2B2B2B")
            main_frame.pack(expand=True, fill="both", padx=50, pady=50)
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame, 
                text="Cadastro de Empresa", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Formulário
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(pady=20, padx=40, fill="x")
            
             # CNPJ
            cnpj_label = ctk.CTkLabel(form_frame, text="CNPJ:", text_color="#FFFFFF")
            cnpj_label.grid(row=0, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            cnpj_entry = ctk.CTkEntry(form_frame, placeholder_text="CNPJ da empresa", width=300)
            cnpj_entry.grid(row=0, column=1, pady=(10, 5), sticky="ew")
            
            # Nome da empresa
            nome_empresa_label = ctk.CTkLabel(form_frame, text="Nome da Empresa:", text_color="#FFFFFF")
            nome_empresa_label.grid(row=1, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            nome_empresa_entry = ctk.CTkEntry(form_frame, placeholder_text="Nome fantasia", width=300)
            nome_empresa_entry.grid(row=1, column=1, pady=(10, 5), sticky="ew")
            
            # Razão social
            razao_social_label = ctk.CTkLabel(form_frame, text="Razão Social:", text_color="#FFFFFF")
            razao_social_label.grid(row=2, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            razao_social_entry = ctk.CTkEntry(form_frame, placeholder_text="Razão social", width=300)
            razao_social_entry.grid(row=2, column=1, pady=(10, 5), sticky="ew")
            
            # Logradouro
            logradouro_label = ctk.CTkLabel(form_frame, text="Logradouro:", text_color="#FFFFFF")
            logradouro_label.grid(row=3, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            logradouro_entry = ctk.CTkEntry(form_frame, placeholder_text="Rua, Avenida, etc.", width=300)
            logradouro_entry.grid(row=3, column=1, pady=(10, 5), sticky="ew")
            
            # Número do endereço
            numero_endereco_label = ctk.CTkLabel(form_frame, text="Número:", text_color="#FFFFFF")
            numero_endereco_label.grid(row=4, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            numero_endereco_entry = ctk.CTkEntry(form_frame, placeholder_text="Número do endereço", width=300)
            numero_endereco_entry.grid(row=4, column=1, pady=(10, 5), sticky="ew")
            
            # Complemento
            complemento_label = ctk.CTkLabel(form_frame, text="Complemento:", text_color="#FFFFFF")
            complemento_label.grid(row=5, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            complemento_entry = ctk.CTkEntry(form_frame, placeholder_text="Complemento", width=300)
            complemento_entry.grid(row=5, column=1, pady=(10, 5), sticky="ew")
            
            # Cidade
            cidade_label = ctk.CTkLabel(form_frame, text="Cidade:", text_color="#FFFFFF")
            cidade_label.grid(row=6, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            cidade_entry = ctk.CTkEntry(form_frame, placeholder_text="Cidade", width=300)
            cidade_entry.grid(row=6, column=1, pady=(10, 5), sticky="ew")
            
            # Estado
            estado_label = ctk.CTkLabel(form_frame, text="Estado:", text_color="#FFFFFF")
            estado_label.grid(row=7, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            estado_entry = ctk.CTkEntry(form_frame, placeholder_text="Estado", width=300)
            estado_entry.grid(row=7, column=1, pady=(10, 5), sticky="ew")
            
            # CEP
            cep_label = ctk.CTkLabel(form_frame, text="CEP:", text_color="#FFFFFF")
            cep_label.grid(row=8, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            cep_entry = ctk.CTkEntry(form_frame, placeholder_text="CEP", width=300)
            cep_entry.grid(row=8, column=1, pady=(10, 5), sticky="ew")
            
            # Email
            email_label = ctk.CTkLabel(form_frame, text="Email:", text_color="#FFFFFF")
            email_label.grid(row=9, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            email_entry = ctk.CTkEntry(form_frame, placeholder_text="Email da empresa", width=300)
            email_entry.grid(row=9, column=1, pady=(10, 5), sticky="ew")
            
            # Senha
            senha_label = ctk.CTkLabel(form_frame, text="Senha:", text_color="#FFFFFF")
            senha_label.grid(row=10, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            senha_entry = ctk.CTkEntry(form_frame, placeholder_text="Crie uma senha", show="*", width=300)

            # Confirmar senha
            confirmar_label = ctk.CTkLabel(form_frame, text="Confirmar Senha:", text_color="#FFFFFF")
            confirmar_label.grid(row=11, column=0, sticky="w", pady=(10, 5), padx=(0, 10))
            confirmar_entry = ctk.CTkEntry(form_frame, placeholder_text="Confirme sua senha", show="*", width=300)
            confirmar_entry.grid(row=11, column=1, pady=(10, 5), sticky="ew")
            
            # Configurar peso das colunas
            form_frame.columnconfigure(1, weight=1)
            
            # Botões
            buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            buttons_frame.pack(pady=30)
            
            register_button = ctk.CTkButton(
                buttons_frame, 
                text="Concluir Cadastro", 
                command=lambda: self.register_empresa(
                    cnpj_entry.get(),
                    nome_empresa_entry.get(),
                    razao_social_entry.get(),
                    logradouro_entry.get(),
                    numero_endereco_entry.get(),
                    complemento_entry.get(),
                    cidade_entry.get(),
                    estado_entry.get(),
                    cep_entry.get(),
                    email_entry.get(),
                    senha_entry.get(),
                    confirmar_entry.get()
                ),
                width=150,
                fg_color="#1E90FF",
                hover_color="#0078D7"
            )
            register_button.pack(pady=10, side="left", padx=10)
            
            back_button = ctk.CTkButton(
                buttons_frame, 
                text="Voltar", 
                command=self.show_register_options,
                width=120,
                fg_color="#2B2B2B",
                border_color="#1E90FF",
                border_width=2,
                text_color="#1E90FF",
                hover_color="#1E1E1E"
            )
            back_button.pack(pady=10, side="left", padx=10)
            
        except Exception as e:
            print(f"Erro ao exibir formulário de empresa: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar o formulário de cadastro.")
    
    def register_user(self, nome, email, genero, numero, senha, confirmar_senha):
        """Registra um novo usuário no banco de dados"""
        try:
            # Validações
            if not nome or not email or not senha or not confirmar_senha:
                messagebox.showerror("Erro", "Todos os campos obrigatórios devem ser preenchidos!")
                return
            
            if senha != confirmar_senha:
                messagebox.showerror("Erro", "As senhas não coincidem!")
                return
            
            if genero == "Selecione":
                messagebox.showerror("Erro", "Selecione um gênero!")
                return
            
            # Verificar se email já existe
            self.cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if self.cursor.fetchone():
                messagebox.showerror("Erro", "Este email já está cadastrado!")
                return
            
            # Hash da senha
            hashed_password = self.hash_password(senha)
            
            # Inserir no banco de dados
            self.cursor.execute(
                "INSERT INTO users (nome_completo, email, genero, numero, senha) VALUES (?, ?, ?, ?, ?)",
                (nome, email, genero, numero, hashed_password)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Conta criada com sucesso! Você já pode fazer login.")
            self.show_login_screen()
            
        except Exception as e:
            print(f"Erro ao registrar usuário: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro ao criar a conta: {str(e)}")
    
    def register_empresa(self, cnpj, nome_empresa, razao_social, logradouro, numero_endereco, 
                        complemento, cidade, estado, cep, email, senha, confirmar_senha):
        """Registra uma nova empresa no banco de dados"""
        try:
            # Validações
            if not cnpj or not nome_empresa or not razao_social or not email or not senha or not confirmar_senha:
                messagebox.showerror("Erro", "Todos os campos obrigatórios devem be preenchidos!")
                return
            
            if senha != confirmar_senha:
                messagebox.showerror("Erro", "As senhas não coincidem!")
                return
            
            # Verificar se CNPJ já existe
            self.cursor.execute("SELECT id FROM empresas WHERE cnpj = ?", (cnpj,))
            if self.cursor.fetchone():
                messagebox.showerror("Erro", "Este CNPJ já está cadastrado!")
                return
            
            # Verificar se email já existe
            self.cursor.execute("SELECT id FROM empresas WHERE email = ?", (email,))
            if self.cursor.fetchone():
                messagebox.showerror("Erro", "Este email já está cadastrado!")
                return
            
            # Hash da senha
            hashed_password = self.hash_password(senha)
            
            # Inserir no banco de dados
            self.cursor.execute(
                """INSERT INTO empresas 
                (cnpj, nome_empresa, razao_social, logradouro, numero_endereco, 
                 complemento, cidade, estado, cep, email, senha) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (cnpj, nome_empresa, razao_social, logradouro, numero_endereco, 
                 complemento, cidade, estado, cep, email, hashed_password)
            )
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Conta criada com sucesso! Você já pode fazer login.")
            self.show_login_screen()
            
        except Exception as e:
            print(f"Erro ao registrar empresa: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro ao criar a conta: {str(e)}")
    
    def login(self, email, senha):
        """Realiza o login do usuário ou empresa"""
        try:
            if not email or not senha:
                messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
                return
            
            hashed_password = self.hash_password(senha)
            
            # Verificar se é um usuário
            self.cursor.execute("SELECT id, nome_completo FROM users WHERE email = ? AND senha = ?", 
                               (email, hashed_password))
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = user[0]
                self.user_type = "user"
                self.user_name = user[1]
                self.show_main_menu()
                return
            
            # Verificar se é uma empresa
            self.cursor.execute("SELECT id, nome_empresa FROM empresas WHERE email = ? AND senha = ?", 
                               (email, hashed_password))
            empresa = self.cursor.fetchone()
            
            if empresa:
                self.current_user = empresa[0]
                self.user_type = "empresa"
                self.user_name = empresa[1]
                self.show_main_menu()
                return
            
            messagebox.showerror("Erro", "Email ou senha incorretos!")
            
        except Exception as e:
            print(f"Erro ao fazer login: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro durante o login: {str(e)}")
    
    def show_main_menu(self):
        """Exibe o menu principal após o login"""
        try:
            self.clear_window()
            
            # Configurar layout principal
            self.root.grid_rowconfigure(1, weight=1)
            self.root.grid_columnconfigure(1, weight=1)
            
            # Barra lateral
            sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0, fg_color="#1E1E1E")
            sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
            sidebar_frame.grid_rowconfigure(7, weight=1)
            
            # Logo
            logo_label = ctk.CTkLabel(
                sidebar_frame, 
                text="BOSS BRIDGE", 
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#1E90FF"
            )
            logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            
            # Bem-vindo
            welcome_label = ctk.CTkLabel(
                sidebar_frame, 
                text=f"Olá, {self.user_name}",
                font=ctk.CTkFont(size=14),
                text_color="#FFFFFF"
            )
            welcome_label.grid(row=1, column=0, padx=20, pady=(0, 20))
            
            # Botões da sidebar
            buttons = [
                ("Início", self.show_dashboard),
                ("Meu Perfil", self.show_profile),
                ("Conexões", self.show_connections),
                ("Conversas", self.show_conversations),
                ("Configurações", self.show_settings),
            ]
            
            for i, (text, command) in enumerate(buttons, start=2):
                button = ctk.CTkButton(
                    sidebar_frame, 
                    text=text, 
                    command=command,
                    fg_color="transparent",
                    text_color="#FFFFFF",
                    hover_color="#2B2B2B",
                    anchor="w",
                    height=40
                )
                button.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            
            # Botão Sair
            logout_button = ctk.CTkButton(
                sidebar_frame, 
                text="Sair", 
                command=self.logout,
                fg_color="#2B2B2B",
                border_color="#FF5555",
                border_width=2,
                text_color="#FF5555",
                hover_color="#1E1E1E",
                height=40
            )
            logout_button.grid(row=8, column=0, padx=10, pady=20, sticky="ew")
            
            # Área de conteúdo
            self.content_frame = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
            self.content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
            
            # Mostrar dashboard por padrão
            self.show_dashboard()
            
        except Exception as e:
            print(f"Erro ao exibir menu principal: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar o menu principal.")
    
    def show_dashboard(self):
        """Exibe o dashboard com estatísticas e notificações"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Dashboard", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Estatísticas
            stats_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
            stats_frame.pack(pady=10, padx=20, fill="x")
            
            # Obter estatísticas do banco de dados
            if self.user_type == "user":
                # Conexões do usuário
                self.cursor.execute("SELECT COUNT(*) FROM conexoes WHERE user_id = ? AND status = 'aceita'", 
                                   (self.current_user,))
                conexoes = self.cursor.fetchone()[0]
                
                # Mensagens não lidas
                self.cursor.execute("SELECT COUNT(*) FROM mensagens WHERE destinatario_id = ? AND tipo_destinatario = 'user' AND lida = 0", 
                                   (self.current_user,))
                mensagens = self.cursor.fetchone()[0]
                
                # Notificações não lidas
                self.cursor.execute("SELECT COUNT(*) FROM notificacoes WHERE usuario_id = ? AND tipo_usuario = 'user' AND lida = 0", 
                                   (self.current_user,))
                notificacoes = self.cursor.fetchone()[0]
                
                stats_data = [
                    ("Conexões Ativas", conexoes, "#1E90FF"),
                    ("Mensagens Não Lidas", mensagens, "#00BFFF"),
                    ("Notificações", notificacoes, "#4682B4")
                ]
            
            else:  # Empresa
                # Conexões da empresa
                self.cursor.execute("SELECT COUNT(*) FROM conexoes WHERE empresa_id = ? AND status = 'aceita'", 
                                   (self.current_user,))
                conexoes = self.cursor.fetchone()[0]
                
                # Mensagens não lidas
                self.cursor.execute("SELECT COUNT(*) FROM mensagens WHERE destinatario_id = ? AND tipo_destinatario = 'empresa' AND lida = 0", 
                                   (self.current_user,))
                mensagens = self.cursor.fetchone()[0]
                
                # Notificações não lidas
                self.cursor.execute("SELECT COUNT(*) FROM notificacoes WHERE usuario_id = ? AND tipo_usuario = 'empresa' AND lida = 0", 
                                   (self.current_user,))
                notificacoes = self.cursor.fetchone()[0]
                
                stats_data = [
                    ("Conexões Ativas", conexoes, "#1E90FF"),
                    ("Mensagens Não Lidas", mensagens, "#00BFFF"),
                    ("Notificações", notificacoes, "#4682B4")
                ]
            
            # Exibir estatísticas
            for i, (title, value, color) in enumerate(stats_data):
                stat_frame = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=10)
                stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
                
                title_label = ctk.CTkLabel(
                    stat_frame, 
                    text=title,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FFFFFF"
                )
                title_label.pack(pady=(15, 5))
                
                value_label = ctk.CTkLabel(
                    stat_frame, 
                    text=str(value),
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#FFFFFF"
                )
                value_label.pack(pady=(5, 15))
            
            stats_frame.columnconfigure((0, 1, 2), weight=1)
            
            # Atividades recentes
            activities_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E")
            activities_frame.pack(pady=20, padx=20, fill="both", expand=True)
            
            activities_label = ctk.CTkLabel(
                activities_frame, 
                text="Atividades Recentes",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#1E90FF"
            )
            activities_label.pack(pady=(15, 10))
            
            # Obter atividades recentes
            if self.user_type == "user":
                self.cursor.execute('''
                    SELECT 'Nova conexão com ' || e.nome_empresa, data_conexao 
                    FROM conexoes c 
                    JOIN empresas e ON c.empresa_id = e.id 
                    WHERE c.user_id = ? 
                    ORDER BY data_conexao DESC 
                    LIMIT 5
                ''', (self.current_user,))
            else:
                self.cursor.execute('''
                    SELECT 'Nova conexão com ' || u.nome_completo, data_conexao 
                    FROM conexoes c 
                    JOIN users u ON c.user_id = u.id 
                    WHERE c.empresa_id = ? 
                    ORDER BY data_conexao DESC 
                    LIMIT 5
                ''', (self.current_user,))
            
            atividades = self.cursor.fetchall()
            
            if atividades:
                for atividade, data in atividades:
                    activity_frame = ctk.CTkFrame(activities_frame, fg_color="#2B2B2B")
                    activity_frame.pack(pady=5, padx=10, fill="x")
                    
                    activity_label = ctk.CTkLabel(
                        activity_frame, 
                        text=atividade,
                        font=ctk.CTkFont(size=14),
                        text_color="#FFFFFF"
                    )
                    activity_label.pack(side="left", padx=10, pady=5)
                    
                    date_label = ctk.CTkLabel(
                        activity_frame, 
                        text=data.split()[0],  # Mostrar apenas a data
                        font=ctk.CTkFont(size=12),
                        text_color="#CCCCCC"
                    )
                    date_label.pack(side="right", padx=10, pady=5)
            else:
                no_activity_label = ctk.CTkLabel(
                    activities_frame, 
                    text="Nenhuma atividade recente",
                    font=ctk.CTkFont(size=14),
                    text_color="#CCCCCC"
                )
                no_activity_label.pack(pady=20)
                
        except Exception as e:
            print(f"Erro ao exibir dashboard: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar o dashboard.")

    def show_profile(self):
        """Exibe o perfil do usuário ou empresa"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Meu Perfil", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Frame principal com scroll
            profile_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#2B2B2B")
            profile_frame.pack(pady=10, padx=20, fill="both", expand=True)
            
            # Foto de perfil
            photo_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
            photo_frame.pack(pady=20)
            
            # Placeholder para imagem (seria implementado com upload real)
            photo_placeholder = ctk.CTkLabel(
                photo_frame, 
                text="📷",
                font=ctk.CTkFont(size=40),
                width=100,
                height=100,
                fg_color="#1E1E1E",
                corner_radius=50
            )
            photo_placeholder.pack()
            
            upload_button = ctk.CTkButton(
                photo_frame, 
                text="Alterar Foto",
                width=120,
                height=30,
                fg_color="#1E1E1E",
                border_color="#1E90FF",
                border_width=1,
                text_color="#1E90FF",
                hover_color="#2B2B2B"
            )
            upload_button.pack(pady=10)
            
            # Obter dados do perfil
            if self.user_type == "user":
                self.cursor.execute(
                    "SELECT nome_completo, email, genero, numero, data_criacao FROM users WHERE id = ?",
                    (self.current_user,)
                )
                user_data = self.cursor.fetchone()
                
                if user_data:
                    nome, email, genero, numero, data_criacao = user_data
                    
                    info_frame = ctk.CTkFrame(profile_frame, fg_color="#1E1E1E", corner_radius=10)
                    info_frame.pack(pady=10, padx=20, fill="x")
                    
                    fields = [
                        ("Nome Completo", nome),
                        ("Email", email),
                        ("Gênero", genero),
                        ("Número", numero),
                        ("Data de Criação", data_criacao)
                    ]
                    
                    for i, (label, value) in enumerate(fields):
                        field_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                        field_frame.pack(pady=10, padx=20, fill="x")
                        
                        label_widget = ctk.CTkLabel(
                            field_frame, 
                            text=label + ":",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color="#1E90FF",
                            width=150,
                            anchor="w"
                        )
                        label_widget.pack(side="left")
                        
                        value_widget = ctk.CTkLabel(
                            field_frame, 
                            text=value or "Não informado",
                            font=ctk.CTkFont(size=14),
                            text_color="#FFFFFF",
                            anchor="w"
                        )
                        value_widget.pack(side="left", padx=(10, 0))
            
            else:  # Empresa
                self.cursor.execute(
                    """SELECT cnpj, nome_empresa, razao_social, logradouro, numero_endereco, 
                    complemento, cidade, estado, cep, email, data_criacao 
                    FROM empresas WHERE id = ?""",
                    (self.current_user,)
                )
                empresa_data = self.cursor.fetchone()
                
                if empresa_data:
                    (cnpj, nome_empresa, razao_social, logradouro, numero_endereco, 
                     complemento, cidade, estado, cep, email, data_criacao) = empresa_data
                    
                    info_frame = ctk.CTkFrame(profile_frame, fg_color="#1E1E1E", corner_radius=10)
                    info_frame.pack(pady=10, padx=20, fill="x")
                    
                    fields = [
                        ("CNPJ", cnpj),
                        ("Nome da Empresa", nome_empresa),
                        ("Razão Social", razao_social),
                        ("Endereço", f"{logradouro}, {numero_endereco}"),
                        ("Complemento", complemento),
                        ("Cidade", cidade),
                        ("Estado", estado),
                        ("CEP", cep),
                        ("Email", email),
                        ("Data de Criação", data_criacao)
                    ]
                    
                    for i, (label, value) in enumerate(fields):
                        field_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                        field_frame.pack(pady=10, padx=20, fill="x")
                        
                        label_widget = ctk.CTkLabel(
                            field_frame, 
                            text=label + ":",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color="#1E90FF",
                            width=150,
                            anchor="w"
                        )
                        label_widget.pack(side="left")
                        
                        value_widget = ctk.CTkLabel(
                            field_frame, 
                            text=value or "Não informado",
                            font=ctk.CTkFont(size=14),
                            text_color="#FFFFFF",
                            anchor="w"
                        )
                        value_widget.pack(side="left", padx=(10, 0))
            
            # Botão de editar perfil
            edit_button = ctk.CTkButton(
                profile_frame, 
                text="Editar Perfil",
                width=150,
                height=40,
                fg_color="#1E90FF",
                hover_color="#0078D7",
                command=self.edit_profile
            )
            edit_button.pack(pady=30)
            
        except Exception as e:
            print(f"Erro ao exibir perfil: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar o perfil.")

    def edit_profile(self):
        """Abre a tela de edição de perfil"""
        messagebox.showinfo("Info", "Funcionalidade de edição de perfil será implementada aqui!")

    def show_connections(self):
        """Exibe a tela de conexões"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Conexões", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 10))
            
            # Abas para Busca e Conexões Existentes
            tabview = ctk.CTkTabview(self.content_frame, fg_color="#2B2B2B")
            tabview.pack(pady=10, padx=20, fill="both", expand=True)
            
            tabview.add("Buscar")
            tabview.add("Suas Conexões")
            
            # ABA 1: BUSCAR
            search_frame = tabview.tab("Buscar")
            
            # Barra de pesquisa
            search_entry = ctk.CTkEntry(
                search_frame, 
                placeholder_text="Digite para buscar...",
                height=40
            )
            search_entry.pack(pady=10, padx=20, fill="x")
            
            search_button = ctk.CTkButton(
                search_frame, 
                text="Buscar",
                height=40,
                fg_color="#1E90FF",
                hover_color="#0078D7",
                command=lambda: self.perform_search(search_entry.get(), results_frame)
            )
            search_button.pack(pady=(0, 20), padx=20)
            
            # Frame para resultados
            results_frame = ctk.CTkScrollableFrame(search_frame, fg_color="#1E1E1E")
            results_frame.pack(pady=10, padx=20, fill="both", expand=True)
            
            # Texto inicial
            initial_text = ctk.CTkLabel(
                results_frame, 
                text="Use a barra de busca para encontrar conexões",
                font=ctk.CTkFont(size=14),
                text_color="#CCCCCC"
            )
            initial_text.pack(pady=20)
            
            # ABA 2: SUAS CONEXÕES
            connections_frame = tabview.tab("Suas Conexões")
            
            # Obter conexões do usuário
            if self.user_type == "user":
                self.cursor.execute('''
                    SELECT c.id, e.nome_empresa, e.email, c.status, c.data_conexao 
                    FROM conexoes c 
                    JOIN empresas e ON c.empresa_id = e.id 
                    WHERE c.user_id = ?
                ''', (self.current_user,))
            else:
                self.cursor.execute('''
                    SELECT c.id, u.nome_completo, u.email, c.status, c.data_conexao 
                    FROM conexoes c 
                    JOIN users u ON c.user_id = u.id 
                    WHERE c.empresa_id = ?
                ''', (self.current_user,))
            
            conexoes = self.cursor.fetchall()
            
            if conexoes:
                connections_scroll = ctk.CTkScrollableFrame(connections_frame, fg_color="#1E1E1E")
                connections_scroll.pack(pady=10, padx=20, fill="both", expand=True)
                
                for conn_id, nome, email, status, data in conexoes:
                    conn_frame = ctk.CTkFrame(connections_scroll, fg_color="#2B2B2B", corner_radius=10)
                    conn_frame.pack(pady=5, padx=5, fill="x")
                    
                    # Informações da conexão
                    info_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
                    info_frame.pack(pady=10, padx=10, fill="x", side="left", expand=True)
                    
                    name_label = ctk.CTkLabel(
                        info_frame, 
                        text=nome,
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color="#FFFFFF",
                        anchor="w"
                    )
                    name_label.pack(anchor="w")
                    
                    email_label = ctk.CTkLabel(
                        info_frame, 
                        text=email,
                        font=ctk.CTkFont(size=14),
                        text_color="#CCCCCC",
                        anchor="w"
                    )
                    email_label.pack(anchor="w")
                    
                    status_label = ctk.CTkLabel(
                        info_frame, 
                        text=f"Status: {status}",
                        font=ctk.CTkFont(size=14),
                        text_color="#1E90FF" if status == "aceita" else "#FFA500",
                        anchor="w"
                    )
                    status_label.pack(anchor="w")
                    
                    date_label = ctk.CTkLabel(
                        info_frame, 
                        text=f"Data: {data.split()[0]}",
                        font=ctk.CTkFont(size=12),
                        text_color="#888888",
                        anchor="w"
                    )
                    date_label.pack(anchor="w")
                    
                    # Botões de ação
                    if status == "pendente" and self.user_type == "empresa":
                        actions_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
                        actions_frame.pack(pady=10, padx=10, side="right")
                        
                        accept_button = ctk.CTkButton(
                            actions_frame, 
                            text="Aceitar",
                            width=80,
                            height=30,
                            fg_color="#00AA00",
                            hover_color="#008800",
                            command=lambda cid=conn_id: self.responder_solicitacao(cid, "aceita")
                        )
                        accept_button.pack(pady=5)
                        
                        reject_button = ctk.CTkButton(
                            actions_frame, 
                            text="Recusar",
                            width=80,
                            height=30,
                            fg_color="#AA0000",
                            hover_color="#880000",
                            command=lambda cid=conn_id: self.responder_solicitacao(cid, "recusada")
                        )
                        reject_button.pack(pady=5)
                    
                    elif status == "aceita":
                        actions_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
                        actions_frame.pack(pady=10, padx=10, side="right")
                        
                        message_button = ctk.CTkButton(
                            actions_frame, 
                            text="Mensagem",
                            width=100,
                            height=30,
                            fg_color="#1E90FF",
                            hover_color="#0078D7",
                            command=lambda n=nome, e=email: self.iniciar_conversa(n, e)
                        )
                        message_button.pack(pady=5)
            else:
                no_connections_label = ctk.CTkLabel(
                    connections_frame, 
                    text="Você ainda não possui conexões",
                    font=ctk.CTkFont(size=16),
                    text_color="#CCCCCC"
                )
                no_connections_label.pack(pady=50)
                
        except Exception as e:
            print(f"Erro ao exibir conexões: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar as conexões.")

    def perform_search(self, query, results_frame):
        """Realiza a busca por usuários ou empresas"""
        try:
            # Limpar resultados anteriores
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            if not query:
                no_results = ctk.CTkLabel(
                    results_frame, 
                    text="Digite algo para buscar",
                    font=ctk.CTkFont(size=14),
                    text_color="#CCCCCC"
                )
                no_results.pack(pady=20)
                return
            
            if self.user_type == "user":
                # Buscar empresas
                self.cursor.execute('''
                    SELECT id, nome_empresa, email, cidade, estado 
                    FROM empresas 
                    WHERE nome_empresa LIKE ? OR razao_social LIKE ? OR email LIKE ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                resultados = self.cursor.fetchall()
                
                if resultados:
                    for emp_id, nome, email, cidade, estado in resultados:
                        emp_frame = ctk.CTkFrame(results_frame, fg_color="#2B2B2B", corner_radius=10)
                        emp_frame.pack(pady=5, padx=5, fill="x")
                        
                        # Informações da empresa
                        info_frame = ctk.CTkFrame(emp_frame, fg_color="transparent")
                        info_frame.pack(pady=10, padx=10, fill="x", side="left", expand=True)
                        
                        name_label = ctk.CTkLabel(
                            info_frame, 
                            text=nome,
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color="#FFFFFF",
                            anchor="w"
                        )
                        name_label.pack(anchor="w")
                        
                        email_label = ctk.CTkLabel(
                            info_frame, 
                            text=email,
                            font=ctk.CTkFont(size=14),
                            text_color="#CCCCCC",
                            anchor="w"
                        )
                        email_label.pack(anchor="w")
                        
                        location_label = ctk.CTkLabel(
                            info_frame, 
                            text=f"{cidade}, {estado}" if cidade and estado else "Localização não informada",
                            font=ctk.CTkFont(size=14),
                            text_color="#888888",
                            anchor="w"
                        )
                        location_label.pack(anchor="w")
                        
                        # Verificar se já existe conexão
                        self.cursor.execute(
                            "SELECT status FROM conexoes WHERE user_id = ? AND empresa_id = ?",
                            (self.current_user, emp_id)
                        )
                        conexao = self.cursor.fetchone()
                        
                        actions_frame = ctk.CTkFrame(emp_frame, fg_color="transparent")
                        actions_frame.pack(pady=10, padx=10, side="right")
                        
                        if conexao:
                            status_label = ctk.CTkLabel(
                                actions_frame, 
                                text=f"Status: {conexao[0]}",
                                font=ctk.CTkFont(size=14),
                                text_color="#1E90FF" if conexao[0] == "aceita" else "#FFA500"
                            )
                            status_label.pack(pady=5)
                        else:
                            connect_button = ctk.CTkButton(
                                actions_frame, 
                                text="Conectar",
                                width=100,
                                height=30,
                                fg_color="#1E90FF",
                                hover_color="#0078D7",
                                command=lambda eid=emp_id: self.solicitar_conexao(eid, "empresa")
                            )
                            connect_button.pack(pady=5)
                else:
                    no_results = ctk.CTkLabel(
                        results_frame, 
                        text="Nenhuma empresa encontrada",
                        font=ctk.CTkFont(size=14),
                        text_color="#CCCCCC"
                    )
                    no_results.pack(pady=20)
            
            else:  # Empresa buscando usuários
                self.cursor.execute('''
                    SELECT id, nome_completo, email, genero, numero 
                    FROM users 
                    WHERE nome_completo LIKE ? OR email LIKE ?
                 ''', (f'%{query}%', f'%{query}%'))
                
                resultados = self.cursor.fetchall()
                
                if resultados:
                    for user_id, nome, email, genero, numero in resultados:
                        user_frame = ctk.CTkFrame(results_frame, fg_color="#2B2B2B", corner_radius=10)
                        user_frame.pack(pady=5, padx=5, fill="x")
                        
                        # Informações do usuário
                        info_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
                        info_frame.pack(pady=10, padx=10, fill="x", side="left", expand=True)
                        
                        name_label = ctk.CTkLabel(
                            info_frame, 
                            text=nome,
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color="#FFFFFF",
                            anchor="w"
                        )
                        name_label.pack(anchor="w")
                        
                        email_label = ctk.CTkLabel(
                            info_frame, 
                            text=email,
                            font=ctk.CTkFont(size=14),
                            text_color="#CCCCCC",
                            anchor="w"
                        )
                        email_label.pack(anchor="w")
                        
                        gender_label = ctk.CTkLabel(
                            info_frame, 
                            text=genero or "Gênero não informado",
                            font=ctk.CTkFont(size=14),
                            text_color="#888888",
                            anchor="w"
                        )
                        gender_label.pack(anchor="w")
                        
                        # Verificar se já existe conexão
                        self.cursor.execute(
                            "SELECT status FROM conexoes WHERE empresa_id = ? AND user_id = ?",
                            (self.current_user, user_id)
                        )
                        conexao = self.cursor.fetchone()
                        
                        actions_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
                        actions_frame.pack(pady=10, padx=10, side="right")
                        
                        if conexao:
                            status_label = ctk.CTkLabel(
                                actions_frame, 
                                text=f"Status: {conexao[0]}",
                                font=ctk.CTkFont(size=14),
                                text_color="#1E90FF" if conexao[0] == "aceita" else "#FFA500"
                            )
                            status_label.pack(pady=5)
                        else:
                            connect_button = ctk.CTkButton(
                                actions_frame, 
                                text="Conectar",
                                width=100,
                                height=30,
                                fg_color="#1E90FF",
                                hover_color="#0078D7",
                                command=lambda uid=user_id: self.solicitar_conexao(uid, "user")
                            )
                            connect_button.pack(pady=5)
                else:
                    no_results = ctk.CTkLabel(
                        results_frame, 
                        text="Nenhum usuário encontrado",
                        font=ctk.CTkFont(size=14),
                        text_color="#CCCCCC"
                    )
                    no_results.pack(pady=20)
                    
        except Exception as e:
            print(f"Erro ao realizar busca: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro durante a busca.")

    def solicitar_conexao(self, target_id, target_type):
        """Solicita uma conexão com usuário ou empresa"""
        try:
            if self.user_type == "user" and target_type == "empresa":
                self.cursor.execute(
                    "INSERT INTO conexoes (user_id, empresa_id) VALUES (?, ?)",
                    (self.current_user, target_id)
                )
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Solicitação de conexão enviada!")
            
            elif self.user_type == "empresa" and target_type == "user":
                self.cursor.execute(
                    "INSERT INTO conexoes (user_id, empresa_id) VALUES (?, ?)",
                    (target_id, self.current_user)
                )
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Solicitação de conexão enviada!")
            
            # Adicionar notificação
            if target_type == "user":
                self.cursor.execute(
                    "INSERT INTO notificacoes (usuario_id, tipo_usuario, titulo, mensagem) VALUES (?, ?, ?, ?)",
                    (target_id, "user", "Nova solicitação de conexão", 
                     f"Uma empresa deseja se conectar com você")
                )
            else:
                self.cursor.execute(
                    "INSERT INTO notificacoes (usuario_id, tipo_usuario, titulo, mensagem) VALUES (?, ?, ?, ?)",
                    (target_id, "empresa", "Nova solicitação de conexão", 
                     f"Um investidor deseja se conectar com sua empresa")
                )
            self.conn.commit()
                
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Solicitação de conexão já existe!")
        except Exception as e:
            print(f"Erro ao solicitar conexão: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro ao solicitar conexão: {str(e)}")

    def responder_solicitacao(self, conexao_id, resposta):
        """Responde a uma solicitação de conexão (apenas para empresas)"""
        try:
            self.cursor.execute(
                "UPDATE conexoes SET status = ? WHERE id = ?",
                (resposta, conexao_id)
            )
            self.conn.commit()
            
            # Obter informações para notificação
            self.cursor.execute(
                "SELECT user_id FROM conexoes WHERE id = ?",
                (conexao_id,)
            )
            user_id = self.cursor.fetchone()[0]
            
            # Adicionar notificação
            status_text = "aceita" if resposta == "aceita" else "recusada"
            self.cursor.execute(
                "INSERT INTO notificacoes (usuario_id, tipo_usuario, titulo, mensagem) VALUES (?, ?, ?, ?)",
                (user_id, "user", "Solicitação de conexão respondida", 
                 f"Sua solicitação de conexão foi {status_text}")
            )
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", f"Solicitação {status_text} com sucesso!")
            self.show_connections()  # Recarregar a tela
            
        except Exception as e:
            print(f"Erro ao responder solicitação: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def iniciar_conversa(self, nome, email):
        """Inicia uma conversa com um usuário ou empresa"""
        messagebox.showinfo("Info", f"Conversa com {nome} ({email}) será iniciada aqui!")
        # Esta função seria implementada para abrir a interface de chat

    def show_conversations(self):
        """Exibe a tela de conversas"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Conversas", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Obter conversas do banco de dados
            if self.user_type == "user":
                self.cursor.execute('''
                    SELECT DISTINCT e.id, e.nome_empresa, 
                    (SELECT mensagem FROM mensagens 
                     WHERE (remetente_id = ? AND tipo_remetente = 'user' AND destinatario_id = e.id AND tipo_destinatario = 'empresa')
                     OR (remetente_id = e.id AND tipo_remetente = 'empresa' AND destinatario_id = ? AND tipo_destinatario = 'user')
                     ORDER BY data_envio DESC LIMIT 1) as ultima_mensagem,
                    (SELECT data_envio FROM mensagens 
                     WHERE (remetente_id = ? AND tipo_remetente = 'user' AND destinatario_id = e.id AND tipo_destinatario = 'empresa')
                     OR (remetente_id = e.id AND tipo_remetente = 'empresa' AND destinatario_id = ? AND tipo_destinatario = 'user')
                     ORDER BY data_envio DESC LIMIT 1) as data_ultima_mensagem
                    FROM empresas e
                    JOIN conexoes c ON e.id = c.empresa_id
                    WHERE c.user_id = ? AND c.status = 'aceita'
                ''', (self.current_user, self.current_user, self.current_user, self.current_user, self.current_user))
            else:
                self.cursor.execute('''
                    SELECT DISTINCT u.id, u.nome_completo,
                    (SELECT mensagem FROM mensagens 
                     WHERE (remetente_id = ? AND tipo_remetente = 'empresa' AND destinatario_id = u.id AND tipo_destinatario = 'user')
                     OR (remetente_id = u.id AND tipo_remetente = 'user' AND destinatario_id = ? AND tipo_destinatario = 'empresa')
                     ORDER BY data_envio DESC LIMIT 1) as ultima_mensagem,
                    (SELECT data_envio FROM mensagens 
                     WHERE (remetente_id = ? AND tipo_remetente = 'empresa' AND destinatario_id = u.id AND tipo_destinatario = 'user')
                     OR (remetente_id = u.id AND tipo_remetente = 'user' AND destinatario_id = ? AND tipo_destinatario = 'empresa')
                     ORDER BY data_envio DESC LIMit 1) as data_ultima_mensagem
                    FROM users u
                    JOIN conexoes c ON u.id = c.user_id
                    WHERE c.empresa_id = ? AND c.status = 'aceita'
                ''', (self.current_user, self.current_user, self.current_user, self.current_user, self.current_user))
            
            conversas = self.cursor.fetchall()
            
            if conversas:
                # Frame para lista de conversas
                conversations_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#1E1E1E")
                conversations_frame.pack(pady=10, padx=20, fill="both", expand=True)
                
                for id, nome, ultima_msg, data_msg in conversas:
                    conversation_frame = ctk.CTkFrame(conversations_frame, fg_color="#2B2B2B", corner_radius=10)
                    conversation_frame.pack(pady=5, padx=5, fill="x")
                    
                    # Informações da conversa
                    info_frame = ctk.CTkFrame(conversation_frame, fg_color="transparent")
                    info_frame.pack(pady=10, padx=10, fill="x", side="left", expand=True)
                    
                    name_label = ctk.CTkLabel(
                        info_frame, 
                        text=nome,
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color="#FFFFFF",
                        anchor="w"
                        )
                    name_label.pack(anchor="w")
                    
                    if ultima_msg:
                        msg_label = ctk.CTkLabel(
                            info_frame, 
                            text=ultima_msg[:50] + "..." if len(ultima_msg) > 50 else ultima_msg,
                            font=ctk.CTkFont(size=14),
                            text_color="#CCCCCC",
                            anchor="w"
                        )
                        msg_label.pack(anchor="w")
                    
                    if data_msg:
                        date_label = ctk.CTkLabel(
                            info_frame, 
                            text=data_msg.split()[0],
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            anchor="w"
                        )
                        date_label.pack(anchor="w")
                    
                    # Botão para abrir conversa
                    open_button = ctk.CTkButton(
                        conversation_frame, 
                        text="Abrir",
                        width=80,
                        height=30,
                        fg_color="#1E90FF",
                        hover_color="#0078D7",
                        command=lambda cid=id, cnome=nome: self.abrir_conversa(cid, cnome)
                    )
                    open_button.pack(pady=10, padx=10, side="right")
            else:
                no_conversations_label = ctk.CTkLabel(
                    self.content_frame, 
                    text="Nenhuma conversa encontrada",
                    font=ctk.CTkFont(size=16),
                    text_color="#CCCCCC"
                )
                no_conversations_label.pack(pady=50)
                
        except Exception as e:
            print(f"Erro ao exibir conversas: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar as conversas.")

        def abrir_conversa(self, contato_id, contato_nome):
            """Abre a conversa com um contato específico"""
            messagebox.showinfo("Info", f"Conversa com {contato_nome} será aberta aqui!")
        # Esta função seria implementada para abrir a interface de chat completa

    def show_settings(self):
        """Exibe a tela de configurações"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Configurações", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Frame principal
            settings_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#2B2B2B")
            settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
            
            # Seção de preferências
            prefs_label = ctk.CTkLabel(
                settings_frame, 
                text="Preferências",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#1E90FF"
            )
            prefs_label.pack(pady=(10, 20), anchor="w")
            
            # Tema
            theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
            theme_frame.pack(pady=10, padx=20, fill="x")
            
            theme_label = ctk.CTkLabel(
                theme_frame, 
                text="Tema:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FFFFFF"
            )
            theme_label.pack(side="left")
            
            theme_var = ctk.StringVar(value="Escuro")
            theme_option = ctk.CTkOptionMenu(
                theme_frame, 
                variable=theme_var,
                values=["Escuro", "Claro"],
                width=120
            )
            theme_option.pack(side="right")
            
            # Notificações
            notif_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
            notif_frame.pack(pady=10, padx=20, fill="x")
            
            notif_label = ctk.CTkLabel(
                notif_frame, 
                text="Notificações:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FFFFFF"
            )
            notif_label.pack(side="left")
            
            notif_var = ctk.StringVar(value="Ativadas")
            notif_option = ctk.CTkOptionMenu(
                notif_frame, 
                variable=notif_var,
                values=["Ativadas", "Desativadas"],
                width=120
            )
            notif_option.pack(side="right")
            
            # Seção de conta
            account_label = ctk.CTkLabel(
                settings_frame, 
                text="Conta",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#1E90FF"
            )
            account_label.pack(pady=(30, 20), anchor="w")
            
            # Alterar senha
            change_pass_button = ctk.CTkButton(
                settings_frame, 
                text="Alterar Senha",
                width=200,
                height=40,
                fg_color="#1E1E1E",
                border_color="#1E90FF",
                border_width=1,
                text_color="#1E90FF",
                hover_color="#2B2B2B",
                command=self.show_change_password
            )
            change_pass_button.pack(pady=10)
            
            # Excluir conta
            delete_button = ctk.CTkButton(
                settings_frame, 
                text="Excluir Conta",
                width=200,
                height=40,
                fg_color="#1E1E1E",
                border_color="#FF5555",
                border_width=1,
                text_color="#FF5555",
                hover_color="#2B2B2B",
                command=self.confirmar_exclusao_conta
            )
            delete_button.pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao exibir configurações: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar as configurações.")

    def show_change_password(self):
        """Exibe a tela de alteração de senha"""
        try:
            self.clear_content()
            
            # Título
            title_label = ctk.CTkLabel(
                self.content_frame, 
                text="Alterar Senha", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1E90FF"
            )
            title_label.pack(pady=(20, 30))
            
            # Formulário
            form_frame = ctk.CTkFrame(self.content_frame, fg_color="#1E1E1E", corner_radius=10)
            form_frame.pack(pady=20, padx=100, fill="x")
            
            # Senha atual
            current_pass_label = ctk.CTkLabel(form_frame, text="Senha Atual:", text_color="#FFFFFF")
            current_pass_label.pack(anchor="w", pady=(20, 5), padx=20)
            current_pass_entry = ctk.CTkEntry(form_frame, placeholder_text="Digite sua senha atual", show="*", width=300)
            current_pass_entry.pack(pady=5, padx=20, fill="x")
            
            # Nova senha
            new_pass_label = ctk.CTkLabel(form_frame, text="Nova Senha:", text_color="#FFFFFF")
            new_pass_label.pack(anchor="w", pady=(20, 5), padx=20)
            new_pass_entry = ctk.CTkEntry(form_frame, placeholder_text="Digite sua nova senha", show="*", width=300)
            new_pass_entry.pack(pady=5, padx=20, fill="x")
            
            # Confirmar nova senha
            confirm_pass_label = ctk.CTkLabel(form_frame, text="Confirmar Nova Senha:", text_color="#FFFFFF")
            confirm_pass_label.pack(anchor="w", pady=(20, 5), padx=20)
            confirm_pass_entry = ctk.CTkEntry(form_frame, placeholder_text="Confirme sua nova senha", show="*", width=300)
            confirm_pass_entry.pack(pady=5, padx=20, fill="x")
            
            # Botões
            buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            buttons_frame.pack(pady=30)
            
            save_button = ctk.CTkButton(
                buttons_frame, 
                text="Salvar", 
                width=120,
                height=40,
                fg_color="#1E90FF",
                hover_color="#0078D7",
                command=lambda: self.change_password(
                    current_pass_entry.get(),
                    new_pass_entry.get(),
                    confirm_pass_entry.get()
                )
            )
            save_button.pack(pady=10, side="left", padx=10)
            
            cancel_button = ctk.CTkButton(
                buttons_frame, 
                text="Cancelar", 
                width=120,
                height=40,
                fg_color="#2B2B2B",
                border_color="#1E90FF",
                border_width=2,
                text_color="#1E90FF",
                hover_color="#1E1E1E",
                command=self.show_settings
            )
            cancel_button.pack(pady=10, side="left", padx=10)
            
        except Exception as e:
            print(f"Erro ao exibir alteração de senha: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", "Ocorreu um erro ao carregar a tela de alteração de senha.")

    def change_password(self, current_password, new_password, confirm_password):
        """Altera a senha do usuário"""
        try:
            # Validações
            if not current_password or not new_password or not confirm_password:
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Erro", "As novas senhas não coincidem!")
                return
            
            # Verificar senha atual
            hashed_current = self.hash_password(current_password)
            
            if self.user_type == "user":
                self.cursor.execute("SELECT senha FROM users WHERE id = ?", (self.current_user,))
            else:
                self.cursor.execute("SELECT senha FROM empresas WHERE id = ?", (self.current_user,))
            
            db_password = self.cursor.fetchone()[0]
            
            if hashed_current != db_password:
                messagebox.showerror("Erro", "Senha atual incorreta!")
                return
            
            # Atualizar senha
            hashed_new = self.hash_password(new_password)
            
            if self.user_type == "user":
                self.cursor.execute("UPDATE users SET senha = ? WHERE id = ?", (hashed_new, self.current_user))
            else:
                self.cursor.execute("UPDATE empresas SET senha = ? WHERE id = ?", (hashed_new, self.current_user))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
            self.show_settings()
            
        except Exception as e:
            print(f"Erro ao alterar senha: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro ao alterar a senha: {str(e)}")

    def confirmar_exclusao_conta(self):
        """Confirma a exclusão da conta"""
        resultado = messagebox.askyesno(
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir sua conta? Esta ação não pode ser desfeita."
        )
        
        if resultado:
            try:
                if self.user_type == "user":
                    # Excluir usuário e todos os dados relacionados
                    self.cursor.execute("DELETE FROM users WHERE id = ?", (self.current_user,))
                    self.cursor.execute("DELETE FROM conexoes WHERE user_id = ?", (self.current_user,))
                    self.cursor.execute("DELETE FROM mensagens WHERE remetente_id = ? AND tipo_remetente = 'user'", (self.current_user,))
                    self.cursor.execute("DELETE FROM mensagens WHERE destinatario_id = ? AND tipo_destinatario = 'user'", (self.current_user,))
                    self.cursor.execute("DELETE FROM notificacoes WHERE usuario_id = ? AND tipo_usuario = 'user'", (self.current_user,))
                else:
                    # Excluir empresa e todos os dados relacionados
                    self.cursor.execute("DELETE FROM empresas WHERE id = ?", (self.current_user,))
                    self.cursor.execute("DELETE FROM conexoes WHERE empresa_id = ?", (self.current_user,))
                    self.cursor.execute("DELETE FROM mensagens WHERE remetente_id = ? AND tipo_remetente = 'empresa'", (self.current_user,))
                    self.cursor.execute("DELETE FROM mensagens WHERE destinatario_id = ? AND tipo_destinatario = 'empresa'", (self.current_user,))
                    self.cursor.execute("DELETE FROM notificacoes WHERE usuario_id = ? AND tipo_usuario = 'empresa'", (self.current_user,))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
                self.logout()
                
            except Exception as e:
                print(f"Erro ao excluir conta: {str(e)}")
                print(traceback.format_exc())
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir a conta: {str(e)}")

    def clear_window(self):
        """Limpa toda a janela principal"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_content(self):
        """Limpa apenas a área de conteúdo (mantendo a sidebar)"""
        if hasattr(self, 'content_frame'):
            for widget in self.content_frame.winfo_children():
                widget.destroy()
    
    def logout(self):
        """Realiza o logout do usuário"""
        self.current_user = None
        self.user_type = None
        self.user_name = None
        self.show_login_screen()
    
    def run(self):
        """Inicia a aplicação"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Erro durante a execução: {str(e)}")
            print(traceback.format_exc())
            input("Pressione Enter para sair...")

# Função principal
if __name__ == "__main__":
    try:
        app = BossBridgeSystem()
        app.run()
    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        print(traceback.format_exc())
        input("Pressione Enter para sair...")