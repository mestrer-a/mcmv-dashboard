"""
Gráfico 2 — Composição das despesas do FGTS por rubrica, 2020-2025.

ATENÇÃO — isto é a composição REALIZADA (executada), não o orçamento
APROVADO pelo CCFGTS para o exercício seguinte. São documentos diferentes:
o orçamento aprovado é uma peça orçamentária publicada separadamente pelo
CCFGTS (não localizada ainda); o que está aqui é a Demonstração do
Resultado do Exercício das Demonstrações Financeiras/Contábeis do FGTS —
ou seja, o que efetivamente aconteceu, não o que foi planejado. Optou-se
por essa composição por já estar em mãos (mesmos PDFs do Gráfico 6, sem
pesquisa nova) e por ser mais direta para o argumento de sustentabilidade
(mostra o custo real, não a previsão).

Mesma limitação de transcrição manual do Gráfico 6 — sem CSV/API oficial,
números tirados linha a linha da seção "Demonstração do Resultado do
Exercício" (coluna Controladora) de cada PDF, com arquivo+página citados.

PDFs em data/raw/fgts_demonstracoes/ (cada um traz o ano corrente + o
anterior):
- Demonstracao_Financeira_FGTS_2025.pdf -> 2025 e 2024
- Demonstracao_Financeira_FGTS_2023-v6.pdf -> 2023 e 2022
- DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf -> 2021 e 2020

Valores em R$ milhares (unidade do documento original), despesas como
valores positivos (o sinal negativo do balanço foi removido para facilitar
o gráfico de composição).
"""
import pandas as pd

# (ano, rubrica, valor_rs_milhares, arquivo_fonte, pagina)
DADOS_TRANSCRITOS = [
    # 2025 / 2024 — Demonstracao_Financeira_FGTS_2025.pdf, página 2
    (2025, "Descontos concedidos", 11_538_915, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2025, "Despesas de depósitos vinculados", 32_159_888, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2025, "Taxa de administração", 3_400_736, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2025, "Despesas administrativas", 97_666, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2025, "Outras despesas operacionais e administrativas", 2_630_839, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2024, "Descontos concedidos", 11_388_468, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2024, "Despesas de depósitos vinculados", 22_382_635, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2024, "Taxa de administração", 3_105_759, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2024, "Despesas administrativas", 82_790, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    (2024, "Outras despesas operacionais e administrativas", 1_976_051, "Demonstracao_Financeira_FGTS_2025.pdf", 2),
    # 2023 / 2022 — Demonstracao_Financeira_FGTS_2023-v6.pdf, página 2
    (2023, "Descontos concedidos", 8_782_467, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2023, "Despesas de depósitos vinculados", 26_068_869, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2023, "Taxa de administração", 2_883_513, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2023, "Despesas administrativas", 89_386, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2023, "Outras despesas operacionais e administrativas", 262_423, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2022, "Descontos concedidos", 6_319_165, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2022, "Despesas de depósitos vinculados", 22_926_672, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2022, "Taxa de administração", 2_697_253, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2022, "Despesas administrativas", 79_541, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    (2022, "Outras despesas operacionais e administrativas", 4_912_100, "Demonstracao_Financeira_FGTS_2023-v6.pdf", 2),
    # 2021 / 2020 — DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf, página 1-2
    (2021, "Descontos concedidos", 7_315_745, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2021, "Despesas de depósitos vinculados", 14_041_567, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2021, "Taxa de administração", 2_643_000, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2021, "Despesas administrativas", 74_703, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2021, "Outras despesas operacionais e administrativas", 1_918_624, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2020, "Descontos concedidos", 8_209_966, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2020, "Despesas de depósitos vinculados", 12_973_603, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2020, "Taxa de administração", 2_640_801, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2020, "Despesas administrativas", 72_766, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
    (2020, "Outras despesas operacionais e administrativas", 1_683_794, "DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf", 2),
]


def main():
    df = pd.DataFrame(
        DADOS_TRANSCRITOS,
        columns=["ano", "rubrica", "valor_rs_milhares", "arquivo_fonte", "pagina_fonte"],
    )
    out_dir = __import__("pathlib").Path(__file__).resolve().parent.parent / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "orcamento_fgts_rubrica.csv", index=False)
    print(df.to_string(index=False))

    total_por_ano = df.groupby("ano")["valor_rs_milhares"].sum()
    print("\nTotal de despesas operacionais por ano (R$ milhares):")
    print(total_por_ano.to_string())


if __name__ == "__main__":
    main()
