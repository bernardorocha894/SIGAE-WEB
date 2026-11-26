# SIGAE WEB - telas e botões (Flask)
# Rodar: python app.py   e abrir   http://127.0.0.1:5000

from flask import Flask, render_template, request, redirect, flash

from sistema import Sistema, ErroSIGAE, RISCOS

app = Flask(__name__)
app.secret_key = "sigae"
sistema = Sistema()


@app.context_processor
def dados_para_todas_as_telas():
    return {"s": sistema, "riscos": RISCOS}


def fazer(acao, *args, ok=None):
    # roda uma ação do sistema e mostra a mensagem na tela
    try:
        acao(*args)
        if ok:
            flash(ok, "ok")
    except ErroSIGAE as erro:
        flash(str(erro), "erro")
    return redirect(request.referrer or "/")


# ---------------- telas ----------------

@app.route("/")
def painel():
    return render_template("painel.html", pagina="painel")


@app.route("/pacientes")
def pacientes():
    achado = None
    busca = request.args.get("id", "")
    if busca:
        achado = sistema.pacientes.obter_item(int(busca))     # busca na Tabela Hash
        if achado is None:
            flash(f"Paciente #{busca} não encontrado.", "erro")
    return render_template("pacientes.html", pagina="pacientes", achado=achado, busca=busca)


@app.route("/triagem")
def triagem():
    return render_template("triagem.html", pagina="triagem")


@app.route("/medicos")
def medicos():
    return render_template("medicos.html", pagina="medicos")


@app.route("/atendimentos")
def atendimentos():
    return render_template("atendimentos.html", pagina="atendimentos")


@app.route("/historico")
def historico():
    return render_template("historico.html", pagina="historico")


@app.route("/arvore")
def arvore():
    selecionado = None
    caminho = []
    id_escolhido = request.args.get("p", "")
    if id_escolhido:
        selecionado = sistema.pacientes.obter_item(int(id_escolhido))
        if selecionado is not None:
            caminho = sistema.arvore.caminho(selecionado.chave())
    return render_template("arvore.html", pagina="arvore", nos=sistema.arvore.desenho(),
                           selecionado=selecionado, caminho=caminho)


# ---------------- botões ----------------

@app.post("/pacientes/novo")
def novo_paciente():
    return fazer(sistema.cadastrar_paciente, request.form.get("nome"), request.form.get("risco"),
                 ok="Paciente cadastrado.")


@app.post("/medicos/novo")
def novo_medico():
    return fazer(sistema.cadastrar_medico, request.form.get("nome"), request.form.get("crm"),
                 ok="Médico cadastrado.")


@app.post("/chamar")
def chamar():
    return fazer(sistema.chamar_proximo, ok="Próximo paciente chamado.")


@app.post("/pacientes/<int:id>/reclassificar")
def reclassificar(id):
    return fazer(sistema.reclassificar, id, request.form.get("risco"), ok="Risco atualizado.")


@app.post("/pacientes/<int:id>/concluir")
def concluir(id):
    return fazer(sistema.concluir, id, ok="Atendimento concluído.")


@app.post("/pacientes/<int:id>/cancelar")
def cancelar(id):
    return fazer(sistema.cancelar, id, ok="Paciente cancelado.")


@app.post("/reiniciar")
def reiniciar():
    global sistema
    sistema = Sistema()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
