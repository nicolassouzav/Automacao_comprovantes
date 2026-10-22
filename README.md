## 💼 Contexto de negócio

Este sistema foi idealizado e desenvolvido internamente a partir da vivência direta nas operações de rotina de um departamento financeiro corporativo. Em escritórios de advocacia, o processo de conciliar guias de pagamento com seus respectivos comprovantes bancários é tradicionalmente manual, lento e suscetível a erros humanos. 

O projeto nasceu para transformar horas de trabalho operacional em uma execução de poucos minutos com muitos arquivos, trazendo eficiência, padronização e segurança.

## ⚙️ Como o Sistema Funciona

A arquitetura foi desenhada para ser simples para o usuário final, executando processos complexos nos bastidores:

1. **Mapeamento e Varredura (Scanning):** Através da interface intuitiva, o usuário seleciona as pastas de origem. O script utiliza a biblioteca nativa `os` para varrer os diretórios e identificar todos os documentos em PDF (guias e comprovantes separados).
2. **Extração Inteligente (Parsing):** O "cérebro" da automação utiliza Expressões Regulares (`re` / Regex) para ler o conteúdo textual dos PDFs, buscando padrões numéricos, códigos de barras ou chaves de identificação que liguem perfeitamente uma guia ao seu comprovante exato.
3. **Processamento e Fusão (Merging):** Uma vez identificados os pares (Guia + Comprovante), o motor do `PyPDF2` entra em ação, juntando as páginas de forma imutável e gerando um documento consolidado, sem perda de qualidade visual ou metadados.
4. **Organização e Entrega:** Os novos arquivos unificados são exportados automaticamente para o diretório de saída escolhido, já renomeados de forma padronizada e prontos para o arquivamento definitivo ou envio aos clientes.
