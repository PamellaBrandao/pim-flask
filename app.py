from flask import Flask, redirect, render_template, request, url_for
import json
import hashlib
from statistics import mean

app = Flask(__name__)
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
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = int(request.form['idade'])
        email = request.form['email']

        # Se o nome não for fornecido, utiliza 'Visitante'
        if not nome.strip():
            nome = 'Visitante'

        email_cripto = hashlib.sha256(email.encode()).hexdigest()

        dados = carregar_dados(ARQUIVO_USUARIOS)

        dados.append({
            'nome': nome,
            'idade': idade,
            'email': email_cripto,
            'tempo_acesso': 30  # valor fictício
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

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

