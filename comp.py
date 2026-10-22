import os
import re
from PyPDF2 import PdfMerger
import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="Comprovantes - Drive", page_icon="💼", layout="centered"
)
st.title("Automação de comprovantes")
st.write("Insira o caminho das pastas para juntar guias e comprovantes.")


# 2. FUNÇÕES DE SUPORTE E LÓGICA DE NEGÓCIO
def extrair_valor_e_base(filename):
  """Extrai o valor monetário exato e isola o nome base."""
  nome_limpo = filename.lower().replace(".pdf", "").replace("_", " ")

  match_valor = re.search(r"(\d{1,3}(\.\d{3})*|\d+),\d{2}", nome_limpo)

  if match_valor:
    valor_encontrado = match_valor.group(0)
    base = re.sub(
        r"\b(guia|comprovante|comp)\b(\s*\d+)?",
        "",
        nome_limpo,
        flags=re.IGNORECASE,
    )
    base = re.sub(r"[\s-]+(\d{1,3}(\.\d{3})*|\d+),\d{2}", "", base)
    base = (re.sub(r"[-_.\s]+$", "", base).strip().replace(" ", "_").upper())
    return f"{base}_{valor_encontrado}"

  base_fallback = re.sub(r"\b(guia|comprovante|comp)\b(\s*\d+)?", "", nome_limpo, flags=re.IGNORECASE)
  return (re.sub(r"[-_.\s]+$", "", base_fallback).strip().replace(" ", "_").upper())


def ordem(caminho_arquivo):
  """Define a ordem exata: Guia sem comp = 0, comp = 1, comp 2 = 2..."""
  nome = os.path.basename(caminho_arquivo).lower()
  if "comp" not in nome and "comprovante" not in nome:
    return 0
  match = re.search(r"comp\s*(\d+)", nome)
  if match:
    return int(match.group(1))
  return 1


def junta_pdfs(caminhos_locais, local_output_path):
  """Junta os PDFs respeitando rigorosamente a ordem matemática."""
  merger = PdfMerger()
  for caminho in caminhos_locais:
    merger.append(caminho)
  merger.write(local_output_path)
  merger.close()


# 3. INTERFACE VISUAL DO STREAMLIT
st.divider()

pasta_origem = st.text_input("Caminho da Pasta:", value="")
pasta_destino = st.text_input("Caminho da Pasta de Destino:", value="")

if st.button("🚀 Executar Automação", use_container_width=True):
  if not pasta_origem or not pasta_destino:
    st.warning("⚠️ Por favor, informe os caminhos das pastas.")
  elif pasta_origem.strip() == pasta_destino.strip():
    st.error("❌ A Pasta de Origem e a Pasta de Destino não podem ser iguais!")
  elif not os.path.exists(pasta_origem):
    st.error(f"❌ A pasta de origem não foi encontrada: {pasta_origem}") 
  else:
    try:
      os.makedirs(pasta_destino, exist_ok=True)

      grupos = {}
      total_encontrados = 0

      # VARREDURA PRESERVANDO O CAMINHO DAS SUBPASTAS
      for raiz, diretorios, arquivos in os.walk(pasta_origem):
        caminho_relativo = os.path.relpath(raiz, pasta_origem)

        for arquivo in arquivos:
          if arquivo.lower().endswith(".pdf"):
            if "_FINALIZADO" in arquivo.upper():
              continue

            total_encontrados += 1
            caminho_completo = os.path.join(raiz, arquivo)
            base_identificador = extrair_valor_e_base(arquivo)

            chave_unica = f"{caminho_relativo}_{base_identificador}"

            if chave_unica not in grupos:
              grupos[chave_unica] = {
                  "caminho_relativo": caminho_relativo,
                  "base_name": base_identificador,
                  "arquivos": [],
              }
            grupos[chave_unica]["arquivos"].append(caminho_completo)

      if total_encontrados == 0:
        st.info("ℹ️ Nenhum arquivo PDF encontrado na pasta ou subpastas.")
      else:
        sucessos = 0
        ja_processados = 0
        arquivos_com_falha = []

        # Preparação para a barra de progresso
        lista_grupos = list(grupos.items())
        total_lotes = len(lista_grupos)

        # Elementos visuais da barra de progresso no Streamlit
        texto_status = st.empty()
        barra_progresso = st.progress(0)

        # 4. PROCESSAMENTO E RECONSTRUÇÃO DA ÁRVORE NO DESTINO COM BARRA DE PROGRESSO
        for index, (chave_unica, dados) in enumerate(lista_grupos):
          caminho_relativo = dados["caminho_relativo"]
          caminhos_locais = dados["arquivos"]
          base_name = dados["base_name"]

          # Atualiza a mensagem da barra de progresso em tempo real
          porcentagem = (index + 1) / total_lotes
          barra_progresso.progress(porcentagem)
          texto_status.text(f"Processando lote {index + 1} de {total_lotes}: {base_name}...")

          # Define exatamente a pasta de destino espelhando a origem
          if caminho_relativo == ".":
            destino_lote = pasta_destino
          else:
            destino_lote = os.path.join(pasta_destino, caminho_relativo)

          os.makedirs(destino_lote, exist_ok=True)

          output_pdf_name = f"{base_name}_FINALIZADO.pdf"
          caminho_output = os.path.join(destino_lote, output_pdf_name)

          # Se já existe no destino exato, pula
          if os.path.exists(caminho_output):
            ja_processados += 1
            continue

          # CONDIÇÃO DE ALERTA: Ficheiro órfão (sem par)
          if len(caminhos_locais) < 2:
            for caminho_isolado in caminhos_locais:
              local_origem_txt = (
                  f"[{caminho_relativo}]"
                  if caminho_relativo != "."
                  else "[Raiz]"
              )
              arquivos_com_falha.append(f"{local_origem_txt} {os.path.basename(caminho_isolado)}")
            continue

          caminhos_locais.sort(key=ordem)
          junta_pdfs(caminhos_locais, caminho_output)
          sucessos += 1

        # Limpa os elementos visuais de carregamento da tela
        texto_status.empty()
        barra_progresso.empty()

        # 5. RELATÓRIO VISUAL NA INTERFACE
        if sucessos > 0:
          st.success(f"✅ Processo concluído! {sucessos} arquivo(s) processado(s) mantendo a estrutura exata de subpastas.")

        if ja_processados > 0:
          st.info(f"ℹ️ {ja_processados} lote(s) já haviam sido processados e foram ignorados.")

        if arquivos_com_falha:
          st.warning ("⚠️ **Atenção: Os seguintes arquivos continuam sem par (Guia + Comprovante):**")
          for arquivo_errado in arquivos_com_falha:
            st.markdown(f"- ❌ `{arquivo_errado}`")

        if sucessos == 0 and ja_processados > 0 and not arquivos_com_falha:
          st.success("✨ Todos os documentos já foram devidamente processados e espelhados!")

    except Exception as e:
      st.error(f"❌ Ocorreu um erro durante o processamento: {e}")