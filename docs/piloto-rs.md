# Ficha de piloto orçada: Rio Grande do Sul

**Estimativa preliminar · CivisBR · 26 de novembro de 2026**

Esta ficha estima a ordem de grandeza do custo de um piloto do programa previsto na [minuta-modelo](minuta-modelo.md). É um cenário para apoiar a conversa com o Estado e os municípios. Não é orçamento de obra e não substitui projeto, vistoria nem cotação.

## Cenário

- Um município do RS, com 50 vistorias de diagnóstico e cerca de 30 obras.
- Casa-tipo térrea, com cerca de 50 m² de área construída, telhado de madeira em duas águas e cerca de 60 m² de cobertura, incluindo beirais.
- As 20 vistorias que não resultam em obra entram no custo. Elas correspondem a casas cujo reforço não se mostra necessário ou cabível, ou cuja eficácia fica comprometida (arts. 2º, V, e 4º, § 3º, da minuta).
- As obras foram distribuídas em três níveis de intervenção, em proporção hipotética: 15 de nível 1, 10 de nível 2 e 5 de nível 3.

## Fonte dos preços

Custos do [SINAPI](https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/Paginas/default.aspx) (Caixa e IBGE), mês de referência outubro de 2026, relatório de composições com encargos sociais sem desoneração, localidade Porto Alegre. Os preços de outros municípios podem diferir. Arquivo consultado: [SINAPI-2026-10-formato-xlsx.zip](https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-2026-10-formato-xlsx.zip), emitido em 12/11/2026 e baixado em 26/11/2026 (SHA-256 2e99cde7594353af311963d93c6defcc89bbd62de64d8282c2335c5e9a7c66d4). O extrato das composições usadas, com a aba e a linha de origem na planilha, está no repositório em `dados/sinapi-2026-10-rs.csv`.

| Código | Composição SINAPI (resumo) | Unidade | Custo RS (R$) |
|---|---|---|---|
| 90777 | Engenheiro civil de obra júnior, com encargos complementares | h | 139,01 |
| 88323 | Telhadista, com encargos complementares | h | 30,15 |
| 88316 | Servente, com encargos complementares | h | 25,81 |
| 97647 | Remoção manual de telhas, sem reaproveitamento | m² | 4,20 |
| 97650 | Remoção manual de trama de madeira, sem reaproveitamento | m² | 9,06 |
| 92543 | Trama de madeira com terças, para telha ondulada de fibrocimento, até 2 águas | m² | 27,76 |
| 94207 | Telhamento com telha ondulada de fibrocimento de 6 mm, até 2 águas | m² | 50,85 |
| 92539 | Trama de madeira com ripas, caibros e terças, para telha cerâmica, até 2 águas | m² | 91,33 |
| 94440 | Telhamento com telha cerâmica de encaixe tipo francesa, até 2 águas | m² | 80,30 |
| 94232 | Amarração de telhas cerâmicas ou de concreto | un | 3,06 |
| 94221 | Cumeeira para telha cerâmica emboçada, até 2 águas | m | 43,46 |

## Custo por etapa

As horas técnicas e as quantidades são hipóteses desta ficha, a ajustar com o protocolo de vistoria.

| Etapa | Hipótese | Custo unitário (R$) | Quantidade | Subtotal (R$) |
|---|---|---|---|---|
| Diagnóstico | 4 h de engenheiro por casa | 556,04 | 50 | 27.802,00 |
| Projeto da intervenção | 3 h de engenheiro por obra | 417,03 | 30 | 12.510,90 |
| Vistoria final independente | 2 h de engenheiro por obra | 278,02 | 30 | 8.340,60 |
| Obra de nível 1 | Reforço das ligações e fixações, sem troca de telhas: 16 h de telhadista e 16 h de servente (só mão de obra; conectores à parte) | 895,36 | 15 | 13.430,40 |
| Obra de nível 2 | Remoção das telhas e da trama existentes e execução de terças novas de madeira com telha ondulada de fibrocimento sem amianto, de 6 mm, em 60 m², mais o nível 1 | 6.407,56 | 10 | 64.075,60 |
| Obra de nível 3 | Remoção das telhas e da trama existentes e execução de trama completa de madeira com telha cerâmica francesa em 60 m², amarração de todas as telhas (16 por m², hipótese: 960 telhas), 8 m de cumeeira, mais o nível 1 | 15.274,04 | 5 | 76.370,20 |
| **Custo direto** | | | | **202.529,70** |
| **Com BDI de 22,12%** | | | | **247.329,27** |

O BDI usado é o valor médio de referência para construção de edifícios no [Acórdão nº 2.622/2013 do TCU](https://www.mpf.mp.br/o-mpf/unidades/pr-to/transparencia/licitacoes-novo/2016/12Acordao26222013BDI.pdf) (faixa de 20,34% a 25,00%). A taxa efetiva depende da forma de contratação. Aqui o BDI incide também sobre diagnóstico, projeto e vistoria, que costumam ser contratados à parte; se incidir só sobre as obras, o total fica em R$ 236.567,12. A área de 60 m² é tratada como área de telhamento, sem fator de inclinação.

Com BDI, o custo médio fica em cerca de R$ 8.244 por obra concluída (R$ 247.329,27 divididos por 30), incluídas as vistorias sem obra. Essas 20 vistorias custam cerca de R$ 13.581 (20 × R$ 556,04 × 1,2212) e não reforçam nenhuma cobertura, mas produzem o diagnóstico e o encaminhamento da família.

## O que não está incluído

- **Conectores metálicos e fixações das ligações** entre a estrutura do telhado e as paredes. Não há composição SINAPI para esse item, que depende de cotação e do projeto de cada casa.
- **Remoção e destinação de telhas de fibrocimento com amianto**, que exigem procedimento próprio. Se a cobertura removida nos níveis 2 e 3 contiver amianto, esse custo se soma.
- Equipamentos e procedimentos de trabalho em altura (NR-35), andaimes, deslocamento das equipes e taxas de ART ou RRT.
- Gestão do programa, seleção das famílias, licenciamento municipal, comunicação e avaliação do piloto.
- Reparos fora do escopo da cobertura, como a ligação entre paredes e fundação.

## Próximos passos

- Cotar os conectores e as fixações das ligações com fornecedores do RS.
- Substituir a distribuição hipotética entre os níveis pelos resultados das primeiras vistorias.
- Ajustar os preços ao município escolhido e à data de execução.
- Conferir os valores com engenheiro orçamentista antes de apresentá-los como estimativa oficial.
