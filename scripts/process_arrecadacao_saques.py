"""
Gráfico 6 — Arrecadação x saques do FGTS (contexto, não manchete).

DIFERENTE dos demais scripts deste projeto: aqui não há um CSV/API oficial
— os números vêm de PDFs de Demonstrações Financeiras/Contábeis do FGTS
(Caixa/fgts.gov.br), transcritos manualmente da seção "Demonstração dos
Fluxos de Caixa" (Fluxo de Caixa das Atividades de Financiamento),
linhas "Arrecadação Recebida em depósitos vinculados do FGTS" e
"Pagamento de Saques de depósitos vinculados do FGTS" (coluna
Controladora = Consolidado para essas duas linhas, confirmado em todos
os anos lidos). Cada valor abaixo tem a fonte exata citada (arquivo +
página) para conferência.

PDFs de origem em data/raw/fgts_demonstracoes/ (cada um traz o ano
corrente + o anterior, por isso 3 arquivos cobrem 6 anos):
- Demonstracao_Financeira_FGTS_2025.pdf (fgts.gov.br) -> dá 2025 e 2024
- Demonstracao_Financeira_FGTS_2023-v6.pdf (fgts.gov.br) -> dá 2023 e 2022
- DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf (caixa.gov.br) -> dá 2021 e 2020

ATENÇÃO — 2020 não é diretamente comparável aos demais anos: a Medida
Provisória 946/2020 incorporou o patrimônio do PIS/PASEP ao FGTS,
somando R$ 22.597.458 milhares à arrecadação daquele ano (ver Nota 1(A)
do PDF de 2021). O valor de "arrecadação" usado aqui para 2020 é só a
linha recorrente de depósitos (163.878.448), SEM essa transferência
extraordinária — por isso não fecha com o "Caixa Líquido Gerado pelas
Atividades de Financiamento" total de 2020 reportado no balanço
(9.543.221), que inclui a transferência. Escolha deliberada para manter
a série comparável ano a ano.

Valores em R$ milhares (conforme unidade do documento original).
"""
import pandas as pd

# (ano, arrecadacao_milhares, saques_milhares, arquivo_fonte, pagina)
DADOS_TRANSCRITOS = [
    (2020, 163_878_448, 176_932_685, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2021, 137_053_928, 115_378_216, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2022, 156_569_578, 154_694_821, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 3),
    (2023, 176_100_550, 140_428_026, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 3),
    (2024, 192_546_632, 160_943_957, "Demonstracao_Financeira_FGTS_2025.pdf", 3),
    (2025, 212_594_313, 190_444_731, "Demonstracao_Financeira_FGTS_2025.pdf", 3),
]

# Saques por modalidade (%) — bônus disponível só para 2020-2023 nos PDFs lidos.
# (ano, modalidade, percentual)
SAQUES_POR_MODALIDADE = [
    (2020, "Demissão sem Justa Causa", 60.3),
    (2020, "Habitação", 13.9),
    (2020, "Aposentadoria", 10.2),
    (2020, "Saque-aniversário", 7.6),
    (2020, "Outras modalidades", 8.0),
    (2021, "Demissão sem Justa Causa", 48.9),
    (2021, "Habitação", 19.0),
    (2021, "Aposentadoria", 9.3),
    (2021, "Saque-aniversário", 15.1),
    (2021, "Outras modalidades", 7.7),
    (2022, "Demissão sem Justa Causa", 33.3),
    (2022, "Habitação", 12.7),
    (2022, "Aposentadoria", 8.1),
    (2022, "Saque-aniversário", 17.3),
    (2022, "Saque extraordinário", 19.5),
    (2022, "Outras modalidades", 9.1),
    (2023, "Demissão sem Justa Causa", 41.5),
    (2023, "Habitação", 16.2),
    (2023, "Aposentadoria", 9.3),
    (2023, "Saque-aniversário", 26.8),
    (2023, "Saque extraordinário", 0.0),
    (2023, "Outras modalidades", 6.2),
]


def main():
    df = pd.DataFrame(
        DADOS_TRANSCRITOS,
        columns=["ano", "arrecadacao_rs_milhares", "saques_rs_milhares", "arquivo_fonte", "pagina_fonte"],
    )
    df["arrecadacao_liquida_rs_milhares"] = df["arrecadacao_rs_milhares"] - df["saques_rs_milhares"]

    out_dir = __import__("pathlib").Path(__file__).resolve().parent.parent / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / "arrecadacao_saques_fgts.csv", index=False)
    print(df.to_string(index=False))

    df_modalidade = pd.DataFrame(SAQUES_POR_MODALIDADE, columns=["ano", "modalidade", "percentual"])
    df_modalidade.to_csv(out_dir / "saques_por_modalidade_fgts.csv", index=False)
    print("\n")
    print(df_modalidade.to_string(index=False))


if __name__ == "__main__":
    main()
