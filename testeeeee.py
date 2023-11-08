import tkinter as tk
from tkinter import ttk
import psycopg2

class PrincipalBD:
    def __init__(self, win):
        # Conecte-se ao banco de dados PostgreSQL
        self.conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="1234",
            host="127.0.0.1",
            port="5432"
        )
        self.cur = self.conn.cursor()

        # Componentes
        self.lbNome = tk.Label(win, text='Nome')
        self.lbEmail = tk.Label(win, text='Email')
        self.lbCurso = tk.Label(win, text='Curso')

        self.txtNome = tk.Entry()
        self.txtEmail = tk.Entry()
        self.txtCurso = tk.Entry()
        self.btnCadastrar = tk.Button(win, text='Cadastrar', command=self.fCadastrarCadastro)
        self.btnAtualizar = tk.Button(win, text='Atualizar', command=self.fAtualizarCadastro)
        self.btnExcluir = tk.Button(win, text='Excluir', command=self.fExcluirCadastro)
        self.btnLimpar = tk.Button(win, text='Limpar', command=self.fLimparTela)

        # Componente TreeView
        self.dadosColunas = ("Matrícula", "Nome", "Email", "Curso")

        self.treeCadastro = ttk.Treeview(win, columns=self.dadosColunas, selectmode='browse')

        self.verscrlbar = ttk.Scrollbar(win, orient="vertical", command=self.treeCadastro.yview)
        self.verscrlbar.pack(side='right', fill='x')

        self.treeCadastro.configure(yscrollcommand=self.verscrlbar.set)

        for coluna in self.dadosColunas:
            self.treeCadastro.heading(coluna, text=coluna)

        self.treeCadastro.column("Matrícula", minwidth=0, width=100)
        self.treeCadastro.column("Nome", minwidth=0, width=150)
        self.treeCadastro.column("Email", minwidth=0, width=200)
        self.treeCadastro.column("Curso", minwidth=0, width=100)

        self.treeCadastro.pack(padx=10, pady=10)

        self.treeCadastro.bind("<<TreeviewSelect>>", self.apresentarRegistrosSelecionados)

        # Posicionamento dos componentes na janela
        self.lbNome.place(x=350, y=50)
        self.txtNome.place(x=400, y=50)

        self.lbEmail.place(x=350, y=100)
        self.txtEmail.place(x=400, y=100)

        self.lbCurso.place(x=350, y=150)
        self.txtCurso.place(x=400, y=150)

        self.btnCadastrar.place(x=280, y=200)
        self.btnAtualizar.place(x=380, y=200)
        self.btnExcluir.place(x=480, y=200)
        self.btnLimpar.place(x=580, y=200)

        self.treeCadastro.place(x=100, y=250)
        self.verscrlbar.place(x=855, y=250, height=225)

        self.carregarDadosIniciais()

    def apresentarRegistrosSelecionados(self, event):
        self.fLimparTela()
        for selection in self.treeCadastro.selection():
            item = self.treeCadastro.item(selection)
            matricula, nome, email, curso = item["values"]
            self.txtNome.insert(0, nome)
            self.txtEmail.insert(0, email)
            self.txtCurso.insert(0, curso)

    def carregarDadosIniciais(self):
        try:
            self.id = 0
            self.iid = 0
            self.cur.execute("SELECT matricula, nome, email, curso FROM cadastro")
            registros = self.cur.fetchall()

            for item in registros:
                matricula, nome, email, curso = item

                self.treeCadastro.insert('', 'end', iid=self.iid, values=(matricula, nome, email, curso))
                self.iid = self.iid + 1
                self.id = self.id + 1
        except Exception as e:
            print(f'Erro ao carregar dados: {e}')

    def fLerCampos(self):
        try:
            nome = self.txtNome.get()
            email = self.txtEmail.get()
            curso = self.txtCurso.get()
            return nome, email, curso
        except Exception as e:
            print(f'Erro ao ler campos: {e}')
            return None

    def fCadastrarCadastro(self):
        campos = self.fLerCampos()
        if campos:
            nome, email, curso = campos
            try:
                self.cur.execute("SELECT MAX(matricula) FROM cadastro")
                max_matricula = self.cur.fetchone()[0] or 0
                matricula = max_matricula + 1
                self.cur.execute("INSERT INTO cadastro (matricula, nome, email, curso) VALUES (%s, %s, %s, %s)",
                                 (matricula, nome, email, curso))
                self.conn.commit()
                self.treeCadastro.insert('', 'end', iid=self.iid, values=(matricula, nome, email, curso))
                self.iid = self.iid + 1
                self.id = self.id + 1
                self.fLimparTela()
            except Exception as e:
                print(f'Erro ao cadastrar registro: {e}')

    def fAtualizarCadastro(self):
        campos = self.fLerCampos()
        if campos:
            nome, email, curso = campos
            try:
                matricula = self.treeCadastro.item(self.treeCadastro.selection())["values"][0]
                self.cur.execute("UPDATE cadastro SET nome = %s, email = %s, curso = %s WHERE matricula = %s",
                                 (nome, email, curso, matricula))
                self.conn.commit()
                self.treeCadastro.delete(*self.treeCadastro.get_children())
                self.carregarDadosIniciais()
                self.fLimparTela()
            except Exception as e:
                print(f'Erro ao atualizar registro: {e}')

    def fExcluirCadastro(self):
        try:
            matricula = self.treeCadastro.item(self.treeCadastro.selection())["values"][0]
            self.cur.execute("DELETE FROM cadastro WHERE matricula = %s", (matricula,))
            self.conn.commit()
            self.treeCadastro.delete(*self.treeCadastro.get_children())
            self.carregarDadosIniciais()
            self.fLimparTela()
        except Exception as e:
            print(f'Erro ao excluir registro: {e}')

    def fLimparTela(self):
        self.txtNome.delete(0, tk.END)
        self.txtEmail.delete(0, tk.END)
        self.txtCurso.delete(0, tk.END)

    def __del__(self):
        self.cur.close()
        self.conn.close()

janela = tk.Tk()
principal = PrincipalBD(janela)
janela.title('Bem Vindo à Aplicação de Banco de Dados')
janela.geometry("920x600+10+10")
janela.mainloop()
