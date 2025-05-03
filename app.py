from flask import Flask, request, redirect, url_for, render_template, session
import json
import hashlib
from statistics import mean
from collections import Counter


app = Flask(__name__)
app.secret_key = 'chave_super_secreta_123'
ARQUIVO_USUARIOS = 'usuarios.json'
ARQUIVO_QUESTIONARIO = 'questionario.json'

# Função para carregar dados do JSON
def carregar_dados(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Função para salvar dados no JSON
def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# 🔁 Redireciona para a página de cadastro
@app.route('/')
def home():
    return redirect(url_for('cadastro'))

# 📋 Página de Cadastro
from datetime import datetime

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = int(request.form['idade'])
        email = request.form['email']

        if not nome.strip():
            nome = 'Visitante'

        email_cripto = hashlib.sha256(email.encode()).hexdigest()

        # ⏱️ Salvar início da sessão e dados temporários
        session['inicio_sessao'] = datetime.now().isoformat()
        session['nome'] = nome
        session['email_cripto'] = email_cripto

        dados = carregar_dados(ARQUIVO_USUARIOS)
        dados.append({
            'nome': nome,
            'idade': idade,
            'email': email_cripto,
            'tempo_acesso': 0  # será atualizado ao sair
        })
        salvar_dados(ARQUIVO_USUARIOS, dados)

        return redirect(url_for('index', nome=nome))
    
    return render_template('cadastro.html')

# 🏠 Página Inicial com mensagem personalizada e gráfico
@app.route('/index')
def index():
    nome = request.args.get('nome', '').strip()  # Se não houver nome, será uma string vazia.
    if not nome:
        nome = 'Visitante'  # Se o nome não for fornecido, usa 'Visitante'.

    dados = carregar_dados(ARQUIVO_USUARIOS)

    faixa_etaria = {
        'Menores de 18': [],
        'Entre 18 e 50': [],
        'Maiores de 50': []
    }

    for u in dados:
        try:
            idade = int(u['idade'])
            tempo = u.get('tempo_acesso', 0)
        except:
            continue

        if idade < 18:
            faixa_etaria['Menores de 18'].append(tempo)
        elif idade <= 50:
            faixa_etaria['Entre 18 e 50'].append(tempo)
        else:
            faixa_etaria['Maiores de 50'].append(tempo)

    media_faixas = {
        faixa: round(mean(tempos), 2) if tempos else 0
        for faixa, tempos in faixa_etaria.items()
    }

    return render_template('index.html', nome=nome, media_faixas=media_faixas)
@app.route('/sair')
def sair():
    if 'inicio_sessao' in session and 'nome' in session and 'email_cripto' in session:
        inicio = datetime.fromisoformat(session['inicio_sessao'])
        fim = datetime.now()
        tempo_acesso = (fim - inicio).total_seconds()

        nome_usuario = session['nome']
        email_cripto = session['email_cripto']

        dados = carregar_dados(ARQUIVO_USUARIOS)

        for usuario in reversed(dados):  # pega o último registro com o mesmo nome e email
            if usuario['nome'] == nome_usuario and usuario['email'] == email_cripto:
                usuario['tempo_acesso'] = round(tempo_acesso, 2)
                break

        salvar_dados(ARQUIVO_USUARIOS, dados)
        session.clear()

    return redirect(url_for('index'))

# ⚡ Simulação de Economia de Energia
@app.route('/simular_energia', methods=['GET', 'POST'])
def simular_energia():
    resultado = False
    valor_conta = 0
    economia = 0

    if request.method == 'POST':
        try:
            valor_conta = float(request.form['valor_conta'])
        except ValueError:
            valor_conta = 0

        habitos_selecionados = request.form.getlist('habitos')

        if valor_conta > 0 and habitos_selecionados:
            economia = valor_conta * 0.20
            resultado = True

    return render_template('simular_energia.html', resultado=resultado, valor_conta=valor_conta, economia=economia)

# 📝 Página de Questionário
@app.route('/questionario')
def questionario():
    return render_template('questionario.html')

# ✅ Processamento do Questionário
@app.route('/enviar_respostas', methods=['POST'])
def enviar_respostas():
    respostas = {
        "pergunta1": request.form.get('pergunta1'),
        "pergunta2": request.form.get('pergunta2'),
        "pergunta3": request.form.get('pergunta3'),
        "pergunta4": request.form.get('pergunta4'),
        "pergunta5": request.form.get('pergunta5')
    }

    novo_usuario_questionario = {
        "questionario": respostas
    }

    # Carregar dados do questionário existente e salvar novo
    dados_questionario = carregar_dados(ARQUIVO_QUESTIONARIO)
    dados_questionario.append(novo_usuario_questionario)
    salvar_dados(ARQUIVO_QUESTIONARIO, dados_questionario)

    return redirect('/resultados_questionario')


@app.route('/resultados_questionario')
def resultados_questionario():
    dados = carregar_dados(ARQUIVO_QUESTIONARIO)

    # Inicializar contadores
    contagens = {
        'pergunta1': Counter(),
        'pergunta2': Counter(),
        'pergunta3': Counter(),
        'pergunta4': Counter(),
        'pergunta5': Counter(),
    }

    total = len(dados)

    for entrada in dados:
        respostas = entrada['questionario']
        for pergunta, resposta in respostas.items():
            contagens[pergunta][resposta] += 1

    # Calcular porcentagens
    porcentagens = {}
    for pergunta, respostas in contagens.items():
        porcentagens[pergunta] = {
            opcao: round((qtd / total) * 100, 1) for opcao, qtd in respostas.items()
        }

    return render_template('resultados_questionario.html', porcentagens=porcentagens)

if __name__ == '__main__':
    app.run(debug=True)
    from collections import Counter
