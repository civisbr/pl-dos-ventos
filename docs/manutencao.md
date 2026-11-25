# Manutenção do site e dos registros

Orientações para a equipe responsável pela atualização do projeto.

## Acompanhar as manifestações

A linha do tempo publica um resumo das movimentações confirmadas de cada sugestão. O [portal de acompanhamento do RS](https://ouvidoriageral.al.rs.gov.br/acompanhe-sua-manifestacao) exige Gov.br, e a primeira versão depende de consulta humana aos canais oficiais. O GitHub Actions valida o histórico e publica o site após cada atualização incorporada à branch `main`.

Após obter confirmação pelo canal oficial:

1. Edite [dados/acompanhamento.json](../dados/acompanhamento.json) na chave do estado. Acrescente a movimentação no final da lista, em ordem cronológica. Se o aviso não informar a data da movimentação, use a data da consulta e indique essa circunstância no resumo.
2. Registre apenas a data, a etapa e um resumo público, conforme o exemplo fictício abaixo. Guarde o número do protocolo, recibos, credenciais, anexos, dados pessoais e respostas integrais fora do repositório, inclusive de issues, PRs e logs do Actions.
3. Abra um pull request. Depois da validação e da revisão do resumo, incorpore o PR à `main`. O site mostra a movimentação mais recente primeiro.

```json
{
  "data": "2027-01-15",
  "etapa": "encaminhada",
  "resumo": "A Ouvidoria informou que a sugestão foi encaminhada ao setor legislativo."
}
```

Etapas disponíveis: `registrada`, `encaminhada`, `em_analise`, `respondida`, `encerrada`, `proposicao_publicada` e `outra`. Registre a existência de proposição formal somente após confirmação na fonte legislativa pública.

## GitHub Pages

O site é estático e usa caminhos relativos para funcionar em um repositório de projeto. Em **Settings → Pages**, selecione **GitHub Actions** como fonte de publicação. A primeira execução pode ser iniciada na aba **Actions → Validar e publicar o site → Run workflow**, na branch `main`. Em seguida, cada atualização da `main` gera uma nova publicação.

Para visualizar localmente, use Python 3.11 ou superior:

```sh
python3 scripts/gerar_site.py
python3 -m http.server 8000 --directory _dist
```

Abra `http://localhost:8000`. A página **Dados** separa vendavais e ciclones de tornados e compara danos humanos e habitacionais entre UFs. A geração local e o deploy usam somente os totais já agregados. A atualização da série do Atlas tem procedimento próprio documentado na metodologia.
