async function carregarDados() {
  const resposta = await fetch("http://127.0.0.1:8000/media-por-ano");
  const dados = await resposta.json();

  const anos = dados.map(d => d.pasta_ano);
  const medias = dados.map(d => d.TRWET_medio);

  const trace = {
    x: anos,
    y: medias,
    type: "scatter",
    mode: "lines+markers",
    name: "TRWET médio",
  };

  const layout = {
    title: "Média anual de TRWET",
    xaxis: { title: "Ano (pasta_ano)" },
    yaxis: { title: "TRWET médio" },
  };

  Plotly.newPlot("grafico", [trace], layout);
}

carregarDados();
