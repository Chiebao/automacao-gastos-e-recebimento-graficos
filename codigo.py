import customtkinter as ctk
import tkinter.messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



#?===== Cores mantendo dois tons iguais =====
cores = {
    "dark":  {"bg": "#DCC2A0", "text": "#FFFFFF", "frame": "#E6D4B8", "entry": "#9F8467", "btn": "#A67C52", "btn_hover": "#B88C5F"},
    "light": {"bg": "#DCC2A0", "text": "#FFFFFF", "frame": "#E6D4B8", "entry": "#9F8467", "btn": "#A67C52", "btn_hover": "#B88C5F"},
}



def inicializar_banco():
    con = sqlite3.connect("financeiro.db")
    cur = con.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servico TEXT NOT NULL,
        valor REAL NOT NULL,
        tipo TEXT NOT NULL);
    """)
    con.commit()
    con.close()

def get_cor(tipo):
    tema = ctk.get_appearance_mode().lower()  # 'light' ou 'dark'
    return cores['dark' if tema == 'dark' else 'light'][tipo]

#*SQLite
def conectar_db():
    conn = sqlite3.connect('financeiro.db')
    return conn.cursor(), conn

def criar_tabela():
    cursor, conn = conectar_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'receita'  -- receita ou gasto
        )
    ''')
    conn.commit()

def adicionar_dado_db(servico, valor, tipo="receita", id=None):
    cursor, conn = conectar_db()
    if id is None:
        cursor.execute('INSERT INTO servicos (servico, valor, tipo) VALUES (?, ?, ?)', (servico, valor, tipo))
    else:
        cursor.execute('UPDATE servicos SET servico=?, valor=?, tipo=? WHERE id=?', (servico, valor, tipo, id))
    conn.commit()

def deleta_dados_db(id):
    cursor, conn = conectar_db()
    cursor.execute('DELETE FROM servicos WHERE id=?', (id,))
    conn.commit()

def carregar_dados_db(tipo="receita"):
    cursor, _ = conectar_db()
    cursor.execute('SELECT id, servico, valor FROM servicos WHERE tipo=?', (tipo,))
    return cursor.fetchall()

janela = ctk.CTk()
janela.title('📈 Dashboard Financeiro 💰')
janela.geometry('950x750')
janela.minsize(850, 550)
janela.configure(fg_color=get_cor('bg'))
title_label = ctk.CTkLabel(
    janela,
    text='📈 Dashboard Financeiro 💰',
    text_color=get_cor('text'),
    font=('Roboto', 30, 'bold')
)
title_label.pack(pady=20)


cima_frame = ctk.CTkFrame(janela, fg_color=get_cor('frame'))
cima_frame.pack(pady=20, padx=30, fill='x')

entrada_frame = ctk.CTkFrame(janela, fg_color=get_cor('frame'))
entrada_frame.pack(pady=10, padx=30, fill='x')

#! Entradas
service_entry = ctk.CTkEntry(
    entrada_frame, placeholder_text='Serviço',
    fg_color=get_cor('entry'), text_color="#FFFFFF",
    width=300, height=40
)
service_entry.grid(row=0, column=0, padx=10, pady=10)

valor_entry = ctk.CTkEntry(
    entrada_frame, placeholder_text='Valor',
    fg_color=get_cor('entry'), text_color="#FFFFFF",
    width=150, height=40
)
valor_entry.grid(row=0, column=1, padx=10, pady=10)

tipo_var = ctk.StringVar(value="receita")
receita_btn = ctk.CTkRadioButton(entrada_frame, text="Receita", variable=tipo_var, value="receita",
                                 fg_color=get_cor('btn'), text_color="#fff")
receita_btn.grid(row=0, column=2, padx=5)

gasto_btn = ctk.CTkRadioButton(entrada_frame, text="Gasto", variable=tipo_var, value="gasto",
                               fg_color="red", text_color="#fff")
gasto_btn.grid(row=0, column=3, padx=5)

adicionar_button = ctk.CTkButton(
    entrada_frame, text='Adicionar',
    fg_color=get_cor('btn'), hover_color=get_cor('btn_hover'),
    text_color="#FFFFFF",
    font=('Helvetica', 18, 'bold')
)
adicionar_button.grid(row=0, column=4, padx=10, pady=10, ipadx=10)

#! Área rolável
scrollable_frame = ctk.CTkScrollableFrame(janela, fg_color=get_cor('frame'), width=650, height=250)
scrollable_frame.pack(pady=20, padx=30, fill='both', expand=True)

#* ===== Lógica 
total_label = None
grafico_canvas = None
valores = []
tipo_atual = "receita"

def atualizar_dados():
    """Atualiza lista, total e gráfico."""
    global valores, total_label, grafico_canvas

    # Limpa UI antiga
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    if total_label:
        total_label.destroy()
    if grafico_canvas:
        grafico_canvas.get_tk_widget().destroy()

    #! Recarrega dados
    valores = carregar_dados_db(tipo_atual)
    if not valores:
        total_label = ctk.CTkLabel(
            cima_frame, text="Nenhum dado cadastrado",
            font=('Roboto', 18, 'bold'), text_color=get_cor('text')
        )
        total_label.pack(pady=10, padx=20, side='right')
        return

    total_valor = sum([v[2] for v in valores])
    nome = "Renda" if tipo_atual == "receita" else "Gastos"

    total_label = ctk.CTkLabel(
        cima_frame, text=f"Total {nome}: R$ {total_valor:.2f}",
        font=('Roboto', 18, 'bold'), text_color=get_cor('text')
    )
    total_label.pack(pady=10, padx=20, side='right')

    # Linhas da lista
    for id_, servico, valor in valores:
        frame_ = ctk.CTkFrame(scrollable_frame, fg_color=get_cor('frame'))
        frame_.pack(pady=10, padx=15, fill='x')

        percentagem = (valor / total_valor) * 100 if total_valor > 0 else 0

        ctk.CTkLabel(frame_, text=servico, width=150,
                     fg_color=get_cor('entry'), text_color="#FFFFFF").pack(side='left', padx=5)
        ctk.CTkLabel(frame_, text=f'R$ {valor:.2f}', width=100,
                     fg_color=get_cor('entry'), text_color="#FFFFFF").pack(side='left', padx=5)
        ctk.CTkLabel(frame_, text=f'{percentagem:.2f}%', width=100,
                     fg_color=get_cor('entry'), text_color="#FFFFFF").pack(side='left', padx=5)

        ctk.CTkButton(frame_, text='Excluir',
                      fg_color=get_cor('btn'), hover_color=get_cor('btn_hover'),
                      text_color="#FFFFFF", font=('Helvetica', 12, 'bold'),
                      command=lambda i=id_: deleta_e_atualiza(i)
                      ).pack(side='right', padx=5)

    atualizar_grafico()

def deleta_e_atualiza(id):
    deleta_dados_db(id)
    atualizar_dados()

def atualizar_grafico():
    """Desenha o gráfico horizontal com estilo."""
    global grafico_canvas
    if not valores:
        return

    categorias = [x[1] for x in valores]
    valores_servico = [x[2] for x in valores]
    cor = '#4B4B4B' if tipo_atual == "receita" else '#CC3333' 

    fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
    bars = ax.barh(categorias, valores_servico, color=cor, edgecolor='#ffffff', height=0.7)

    desloc = max(valores_servico) * 0.01 if max(valores_servico) > 0 else 1
    for bar in bars:
        width = bar.get_width()
        ax.text(width + desloc, bar.get_y() + bar.get_height()/2,
                f'R$ {width:,.2f}', va='center', ha='left', fontsize=10, fontweight='bold', color='black')

    titulo = "Distribuição das Receitas" if tipo_atual == "receita" else "Distribuição dos Gastos"
    ax.set_xlabel('Valor em R$', fontsize=12, fontweight='bold', color='#333333')
    ax.set_ylabel('Serviços', fontsize=12, fontweight='bold', color='#333333')
    ax.set_title(titulo, fontsize=16, fontweight='bold', color='#333333')
    ax.tick_params(axis='both', labelsize=10, colors='#555555')
    ax.set_facecolor('#f4f4f4')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5, color='#bbbbbb')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('none')
    

    if grafico_canvas:
        grafico_canvas.get_tk_widget().destroy()
    grafico_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
    grafico_canvas.draw()
    grafico_canvas.get_tk_widget().pack(pady=20)

def adicionar_servico():
    servico = service_entry.get().strip()
    valor = valor_entry.get().replace(',', '.').strip()
    tipo = tipo_var.get()
    if not servico or not valor:
        tkinter.messagebox.showerror("Erro", "Preencha Serviço e Valor.")
        return
    try:
        valor_float = float(valor)
    except ValueError:
        tkinter.messagebox.showerror("Erro", "Valor inválido! Use apenas números (ex: 1234.56).")
        return

    adicionar_dado_db(servico, valor_float, tipo)
    service_entry.delete(0, 'end')
    valor_entry.delete(0, 'end')
    atualizar_dados()

adicionar_button.configure(command=adicionar_servico)

# Botões para alternar
def mostrar_receitas():
    global tipo_atual
    tipo_atual = "receita"
    atualizar_dados()

def mostrar_gastos():
    global tipo_atual
    tipo_atual = "gasto"
    atualizar_dados()

btn_frame = ctk.CTkFrame(janela, fg_color=get_cor('frame'))
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="Ver Receitas", command=mostrar_receitas,
              fg_color=get_cor('btn'), hover_color=get_cor('btn_hover'),
              text_color="#fff").pack(side='left', padx=10)

ctk.CTkButton(btn_frame, text="Ver Gastos", command=mostrar_gastos,
              fg_color="#CC3333", hover_color="#AA2222",
              text_color="#fff").pack(side='left', padx=10)

#!Para criação de rodapé
rodape = ctk.CTkLabel(
    janela,
    text="Feito por Luana Godoy",
    font=("Arial", 10),
    text_color="#4B3621"
)
rodape.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5) 

#!para cortar loops
def on_closing():
    global grafico_canvas
    try:
        if grafico_canvas:
            grafico_canvas.get_tk_widget().destroy()
            grafico_canvas = None
    except:
        pass
    try:
        for after_id in janela.tk.eval('after info').split():
            try:
                janela.after_cancel(after_id)
            except:
                pass
    except:
        pass
    janela.quit()
    janela.destroy()

janela.protocol("WM_DELETE_WINDOW", on_closing)

# ===== Inicialização =====
criar_tabela()
valores = carregar_dados_db(tipo_atual)
atualizar_dados()
janela.mainloop()
