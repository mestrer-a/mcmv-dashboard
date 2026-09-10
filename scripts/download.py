"""
Baixa as bases oficiais do PMCMV (Ministério das Cidades) para data/raw/, intocadas.

Fontes e datas de acesso: ver SOURCES.md.
Uso: python scripts/download.py [--skip-analitico]
"""
import argparse
import sys
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

FILES = {
    "mcmv_subsidiado_202606302.zip": (
        "https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/"
        "habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_subsidiado_202606302.zip"
    ),
    "mcmv_financ_sintetico_20260724_v2.zip": (
        "https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/"
        "habitacao/programa-minha-casa-minha-vida/arquivos/"
        "mcmv_financ_sintetico_20260724_v2.zip"
    ),
    "Dicionarios_SNH_2025_10_09.pdf": (
        "https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/"
        "habitacao/arquivos-1/Dicionarios_SNH_2025_10_09.pdf"
    ),
    # ~191 MB comprimido — nível de contrato individual, único nível que separa
    # subsídio por fonte (FGTS/OGU) e por programa (inclui "Fundo Social").
    "mcmv_financ_analitico_20260724.zip": (
        "https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/"
        "mcmv_financ_analitico_20260724.zip"
    ),
}


def download(filename: str, url: str) -> None:
    dest = RAW_DIR / filename
    if dest.exists():
        print(f"[skip] {filename} já existe ({dest.stat().st_size:,} bytes)")
        return
    print(f"[baixando] {filename} <- {url}")
    with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        written = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                written += len(chunk)
                if total:
                    pct = 100 * written / total
                    print(f"\r  {written:,}/{total:,} bytes ({pct:.1f}%)", end="", flush=True)
    print(f"\n[ok] {filename} salvo em {dest}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-analitico",
        action="store_true",
        help="pula o download da base analítica de contratos (~191 MB)",
    )
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in FILES.items():
        if args.skip_analitico and filename.startswith("mcmv_financ_analitico"):
            print(f"[skip] {filename} (--skip-analitico)")
            continue
        download(filename, url)


if __name__ == "__main__":
    sys.exit(main())
