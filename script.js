
const imagemMolecula = document.getElementById("imagem-molecula");
const carregandoMolecula = document.getElementById("carregando-molecula");

const campoResposta = document.getElementById("campo-resposta");
const botaoEnviar = document.getElementById("botao-enviar");
const botaoDica = document.getElementById("botao-dica");
const mensagemErro = document.getElementById("mensagem-erro");

const areaDicas = document.querySelector(".area-dicas");
const listaDicas = document.getElementById("lista-dicas");

const listaTentativas = document.getElementById("lista-tentativas");

const painelVitoria = document.getElementById("painel-vitoria");
const vitoriaNome = document.getElementById("vitoria-nome");
const vitoriaFuncao = document.getElementById("vitoria-funcao");
const vitoriaFormula = document.getElementById("vitoria-formula");
const vitoriaGrupo = document.getElementById("vitoria-grupo");
const vitoriaDescricao = document.getElementById("vitoria-descricao");
const botaoNovaRodada = document.getElementById("botao-nova-rodada");


let enviando = false;
let rodadaGanha = false;



function mostrarErro(texto) {
  mensagemErro.textContent = texto;
}

function limparErro() {
  mensagemErro.textContent = "";
}

function sacudirCampo() {
  campoResposta.classList.remove("tremer");
  requestAnimationFrame(() => {
    campoResposta.classList.add("tremer");
  });
}


function renderizarTentativa(tentativaNormalizada, diff) {
  const linha = document.createElement("div");
  linha.className = "linha-tentativa";

  for (let i = 0; i < tentativaNormalizada.length; i++) {
    const tile = document.createElement("div");
    tile.className = `tile ${diff[i]}`;
    tile.textContent = tentativaNormalizada[i];
    tile.style.animationDelay = `${i * 70}ms`;
    linha.appendChild(tile);
  }

  listaTentativas.appendChild(linha);
}

function renderizarDica(texto, numero) {
  areaDicas.classList.add("visivel");

  const item = document.createElement("div");
  item.className = "dica-item";
  item.textContent = `Dica ${numero}: ${texto}`;
  listaDicas.appendChild(item);
}

function mostrarPainelVitoria(info) {
  vitoriaNome.textContent = info.nome;
  vitoriaFuncao.textContent = info.funcao;
  vitoriaFormula.textContent = info.formula;
  vitoriaGrupo.textContent = info.grupo_funcional;
  vitoriaDescricao.textContent = info.descricao;

  painelVitoria.classList.remove("escondido");
}

function esconderPainelVitoria() {
  painelVitoria.classList.add("escondido");
}



async function carregarNovaMolecula() {

  rodadaGanha = false;
  limparErro();
  listaTentativas.innerHTML = "";
  listaDicas.innerHTML = "";
  areaDicas.classList.remove("visivel");
  campoResposta.value = "";
  campoResposta.disabled = false;
  botaoEnviar.disabled = false;
  botaoDica.disabled = false;

  imagemMolecula.classList.remove("visivel");
  carregandoMolecula.classList.remove("escondido");

  try {
    const resposta = await fetch("/api/nova_molecula");
    if (!resposta.ok) {
      throw new Error("Falha ao sortear uma nova molécula.");
    }
    const dados = await resposta.json();

    imagemMolecula.src = dados.imagem;
    imagemMolecula.onload = () => {
      carregandoMolecula.classList.add("escondido");
      imagemMolecula.classList.add("visivel");
    };
  } catch (erro) {
    carregandoMolecula.textContent = "Erro ao carregar a molécula. Recarregue a página.";
    console.error(erro);
  }

  campoResposta.focus();
}

async function enviarTentativa() {
  if (enviando || rodadaGanha) return;

  const texto = campoResposta.value.trim();
  if (texto === "") {
    mostrarErro("Digite uma resposta antes de enviar.");
    sacudirCampo();
    return;
  }

  limparErro();
  enviando = true;
  botaoEnviar.disabled = true;

  try {
    const resposta = await fetch("/api/tentativa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tentativa: texto }),
    });

    const dados = await resposta.json();

    if (!resposta.ok) {
      mostrarErro(dados.erro || "Ocorreu um erro. Tente novamente.");
      sacudirCampo();
      return;
    }

    renderizarTentativa(dados.tentativa_normalizada, dados.diff);
    campoResposta.value = "";

    if (dados.acertou) {
      rodadaGanha = true;
      campoResposta.disabled = true;
      botaoDica.disabled = true;

      setTimeout(() => mostrarPainelVitoria(dados.info), 500);
    } else {
      sacudirCampo();
    }
  } catch (erro) {
    mostrarErro("Não foi possível enviar sua resposta. Verifique a conexão.");
    console.error(erro);
  } finally {
    enviando = false;
    botaoEnviar.disabled = rodadaGanha; 
  }

  campoResposta.focus();
}

async function pedirDica() {
  if (rodadaGanha) return;

  botaoDica.classList.remove("pulsar");
  requestAnimationFrame(() => botaoDica.classList.add("pulsar"));

  try {
    const resposta = await fetch("/api/dica");
    const dados = await resposta.json();

    if (!resposta.ok) {
      mostrarErro(dados.erro || "Não foi possível obter uma dica.");
      return;
    }

    if (dados.dica) {
      renderizarDica(dados.dica, dados.dicas_usadas);
    } else {
      renderizarDica(dados.mensagem || "Não há mais dicas para essa molécula.", dados.total_dicas);
      botaoDica.disabled = true;
    }
  } catch (erro) {
    mostrarErro("Não foi possível obter a dica. Verifique a conexão.");
    console.error(erro);
  }
}



botaoEnviar.addEventListener("click", enviarTentativa);

campoResposta.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter") {
    evento.preventDefault();
    enviarTentativa();
  }
});


campoResposta.addEventListener("input", limparErro);

botaoDica.addEventListener("click", pedirDica);

botaoNovaRodada.addEventListener("click", () => {
  esconderPainelVitoria();
  carregarNovaMolecula();
});


carregarNovaMolecula();