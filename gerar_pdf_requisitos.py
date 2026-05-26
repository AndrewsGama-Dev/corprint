#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera PDF a partir de REQUISITOS_CLIENTE_INTEGRACAO.md (uso pontual)."""
import sys
from pathlib import Path

import markdown
from xhtml2pdf import pisa


def gerar_pdf(caminho_md: Path, caminho_pdf: Path | None = None) -> Path:
    if caminho_pdf is None:
        caminho_pdf = caminho_md.with_suffix(".pdf")
    texto = caminho_md.read_text(encoding="utf-8")
    corpo = markdown.markdown(
        texto,
        extensions=["tables", "fenced_code"],
    )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<style>
body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; margin: 1.8cm;
  line-height: 1.35; color: #111; }}
h1 {{ font-size: 17pt; border-bottom: 1px solid #333; padding-bottom: 6px; }}
h2 {{ font-size: 13pt; margin-top: 18px; }}
h3 {{ font-size: 11.5pt; margin-top: 12px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 8.5pt; }}
th, td {{ border: 1px solid #444; padding: 5px; vertical-align: top; }}
th {{ background: #e8e8e8; font-weight: bold; }}
code {{ font-family: Consolas, monospace; font-size: 8.8pt; background: #f4f4f4;
  padding: 1px 3px; }}
pre code {{ background: transparent; }}
ul {{ padding-left: 20px; }}
hr {{ margin: 16px 0; border: none; border-top: 1px solid #999; }}
@page {{
  margin: 1.5cm;
}}
</style>
</head><body>{corpo}</body></html>
"""
    with open(caminho_pdf, "wb") as fh:
        status = pisa.CreatePDF(html.encode("utf-8"), dest=fh)
    if getattr(status, "err", False):
        raise RuntimeError(f"Erro ao gerar PDF: {status}")
    return caminho_pdf


def main():
    root = Path(__file__).resolve().parent
    md = root / "REQUISITOS_CLIENTE_INTEGRACAO.md"
    if not md.exists():
        print(f"Arquivo não encontrado: {md}")
        sys.exit(1)
    pdf = gerar_pdf(md)
    print(f"PDF gerado: {pdf}")
    sys.exit(0)


if __name__ == "__main__":
    main()
