# Gerador de Cards - Colação de Grau PROGRAD/UFSM

Aplicativo desktop desenvolvido para automatizar e padronizar a criação dos cards nominais utilizados nas cerimônias de colação de grau da Pró-Reitoria de Graduação da Universidade Federal de Santa Maria (PROGRAD/UFSM).

O software substitui o fluxo manual anterior baseado em edição de código LaTeX (TikZ), fornecendo uma interface gráfica simples e à prova de falhas para operadores administrativos, com pré-visualização em tempo real e geração instantânea do arquivo PDF pronto para impressão e recorte.

---

## Funcionalidades

- **Interface Desktop Nativa:** Desenvolvida em Python com PyQt5, focada na simplicidade operacional e prevenção de erros de entrada.
- **Pré-visualização em Tempo Real:** Renderização vetorial instantânea (QPainter) mantendo a proporção exata e o posicionamento tipográfico do layout original.
- **Tabelas Editáveis e Suporte a CSV:** Cadastro manual rápido ou importação/exportação em lote a partir de planilhas de formandos, mesa de honra e homenageados.
- **Geração de PDF Fiel ao Padrão Institucional:** Renderização de alta qualidade (ReportLab) utilizando a tipografia oficial (família Agrandir) e o emblema da instituição.
- **Otimização de Impressão:** Geração no formato A4 retrato, organizando automaticamente dois cards por página com espaçamento de corte pré-configurado.
- **Executável Único:** Distribuição simplificada através de um único arquivo `.exe` autossuficiente, sem necessidade de instalação de dependências externas por parte do usuário final.

---

## Estrutura do Projeto

```text
Cards Formatura PROGRAD/
├── assets/                  # Tipografia oficial (.otf), logotipos e ícone do executável
├── core/
│   ├── card_data.py         # Estruturas de dados (DataClasses) e parsers de importação CSV
│   └── pdf_generator.py     # Motor de renderização do arquivo PDF via ReportLab
├── ui/
│   ├── card_preview.py      # Componente visual de pré-visualização vetorial dos cards
│   ├── data_panel.py        # Painel de abas e tabelas de gerenciamento dos participantes
│   └── main_window.py       # Janela principal, barra de ação e controle da aplicação
├── main.py                  # Ponto de entrada e rotinas de inicialização/auto-desbloqueio
├── requirements.txt         # Lista de dependências Python para o ambiente de desenvolvimento
└── build.bat                # Script de automação para geração do executável PyInstaller
```

---

## Uso pelo Operador (Usuário Final)

**Não é necessário instalar Python, bibliotecas, ou qualquer programa adicional.** 

O software foi projetado para ser 100% autossuficiente para o usuário final. Todas as bibliotecas gráficas, motores de renderização e tipografias oficiais da UFSM já estão embutidas dentro do próprio executável.

Para utilizar a ferramenta:
1. Baixe o arquivo único `Gerador de Cards PROGRAD.exe`.
2. Clique duas vezes no arquivo para iniciar a interface.
3. Cadastre ou importe os dados dos formandos via CSV e clique em **Gerar PDF**.

---

## Ambiente de Desenvolvimento (Para Programadores / Manutenção)

As instruções abaixo são destinadas **exclusivamente a desenvolvedores** que desejam modificar o código-fonte ou compilar uma nova versão do binário.

### Requisitos do Sistema
- Windows 10 ou 11
- Python 3.10 ou superior

### Configuração do Ambiente
Clone o repositório e instale as dependências necessárias através do terminal:

```cmd
git clone https://github.com/SeuUsuario/Cards-Formatura-PROGRAD.git
cd Cards-Formatura-PROGRAD
pip install -r requirements.txt
```

Para executar a aplicação diretamente a partir do código-fonte:

```cmd
python main.py
```

---

## Compilação do Executável (.exe)

O executável final para distribuição aos usuários finais é construído via PyInstaller no formato `--onefile` (arquivo único), embutindo todas as dependências, fontes e imagens dentro do próprio binário.

Para compilar, execute o script de build incluso na raiz do projeto:

```cmd
build.bat
```

Ou, alternativamente, execute o comando manualmente via terminal:

```cmd
pyinstaller --onefile --windowed --icon=assets\logo.ico --name="Gerador de Cards PROGRAD" --add-data "assets;assets" main.py -y
```

Após o término da compilação, o arquivo final (`Gerador de Cards PROGRAD.exe`) estará disponível dentro do diretório `dist/`.

---

## Observações de Segurança e Distribuição no Windows

Por se tratar de uma ferramenta interna e não possuir um certificado digital comercial pago (Code Signing), o Microsoft Defender SmartScreen pode exibir um aviso de "Computador protegido" na primeira vez que o arquivo `.exe` for baixado da internet ou aberto via rede local.

Para resolver isso de forma transparente, a aplicação possui uma rotina de auto-desbloqueio (`Unblock-File`) executada em segundo plano durante a primeira inicialização. A partir da segunda execução no mesmo computador, o sistema operacional reconhecerá a liberação e o programa abrirá instantaneamente sem exibir alertas.

Caso o operador precise liberar manualmente antes de abrir a primeira vez, basta clicar com o botão direito sobre o arquivo `.exe`, acessar **Propriedades**, marcar a caixa **Desbloquear** na aba Geral e clicar em **OK**.

---

## Autoria e Créditos

Desenvolvido por Anthony Perotti para a Pró-Reitoria de Graduação da Universidade Federal de Santa Maria (PROGRAD/UFSM).
