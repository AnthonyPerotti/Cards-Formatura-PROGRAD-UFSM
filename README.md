# Gerador de Cards - ColaÃ§Ã£o de Grau PROGRAD/UFSM

Aplicativo desktop desenvolvido para automatizar e padronizar a criaÃ§Ã£o dos cards nominais utilizados nas cerimÃ´nias de colaÃ§Ã£o de grau da PrÃ³-Reitoria de GraduaÃ§Ã£o da Universidade Federal de Santa Maria (PROGRAD/UFSM).

O software substitui o fluxo manual anterior baseado em ediÃ§Ã£o de cÃ³digo LaTeX (TikZ), fornecendo uma interface grÃ¡fica simples e Ã  prova de falhas para operadores administrativos, com prÃ©-visualizaÃ§Ã£o em tempo real e geraÃ§Ã£o instantÃ¢nea do arquivo PDF pronto para impressÃ£o e recorte.

---

## Funcionalidades

- **Interface Desktop Nativa:** Desenvolvida em Python com PyQt5, focada na simplicidade operacional e prevenÃ§Ã£o de erros de entrada.
- **PrÃ©-visualizaÃ§Ã£o em Tempo Real:** RenderizaÃ§Ã£o vetorial instantÃ¢nea (QPainter) mantendo a proporÃ§Ã£o exata e o posicionamento tipogrÃ¡fico do layout original.
- **Tabelas EditÃ¡veis e Suporte a CSV:** Cadastro manual rÃ¡pido ou importaÃ§Ã£o/exportaÃ§Ã£o em lote a partir de planilhas de formandos, mesa de honra e homenageados.
- **GeraÃ§Ã£o de PDF Fiel ao PadrÃ£o Institucional:** RenderizaÃ§Ã£o de alta qualidade (ReportLab) utilizando a tipografia oficial (famÃ­lia Agrandir) e o emblema da instituiÃ§Ã£o.
- **OtimizaÃ§Ã£o de ImpressÃ£o:** GeraÃ§Ã£o no formato A4 retrato, organizando automaticamente dois cards por pÃ¡gina com espaÃ§amento de corte prÃ©-configurado.
- **ExecutÃ¡vel Ãšnico:** DistribuiÃ§Ã£o simplificada atravÃ©s de um Ãºnico arquivo `.exe` autossuficiente, sem necessidade de instalaÃ§Ã£o de dependÃªncias externas por parte do usuÃ¡rio final.

---

## Estrutura do Projeto

```text
Cards Formatura PROGRAD/
â”œâ”€â”€ assets/                  # Tipografia oficial (.otf), logotipos e Ã­cone do executÃ¡vel
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ card_data.py         # Estruturas de dados (DataClasses) e parsers de importaÃ§Ã£o CSV
â”‚   â””â”€â”€ pdf_generator.py     # Motor de renderizaÃ§Ã£o do arquivo PDF via ReportLab
â”œâ”€â”€ ui/
â”‚   â”œâ”€â”€ card_preview.py      # Componente visual de prÃ©-visualizaÃ§Ã£o vetorial dos cards
â”‚   â”œâ”€â”€ data_panel.py        # Painel de abas e tabelas de gerenciamento dos participantes
â”‚   â””â”€â”€ main_window.py       # Janela principal, barra de aÃ§Ã£o e controle da aplicaÃ§Ã£o
â”œâ”€â”€ main.py                  # Ponto de entrada e rotinas de inicializaÃ§Ã£o/auto-desbloqueio
â”œâ”€â”€ requirements.txt         # Lista de dependÃªncias Python para o ambiente de desenvolvimento
â””â”€â”€ build.bat                # Script de automaÃ§Ã£o para geraÃ§Ã£o do executÃ¡vel PyInstaller
```

---

## Uso pelo Operador (UsuÃ¡rio Final)

**NÃ£o Ã© necessÃ¡rio instalar Python, bibliotecas, ou qualquer programa adicional.** 

O software foi projetado para ser 100% autossuficiente para o usuÃ¡rio final. Todas as bibliotecas grÃ¡ficas, motores de renderizaÃ§Ã£o e tipografias oficiais da UFSM jÃ¡ estÃ£o embutidas dentro do prÃ³prio executÃ¡vel.

Para utilizar a ferramenta:
1. Baixe o arquivo Ãºnico `Gerador de Cards PROGRAD.exe`.
2. Clique duas vezes no arquivo para iniciar a interface.
3. Cadastre ou importe os dados dos formandos via CSV e clique em **Gerar PDF**.

---

## Ambiente de Desenvolvimento (Para Programadores / ManutenÃ§Ã£o)

As instruÃ§Ãµes abaixo sÃ£o destinadas **exclusivamente a desenvolvedores** que desejam modificar o cÃ³digo-fonte ou compilar uma nova versÃ£o do binÃ¡rio.

### Requisitos do Sistema
- Windows 10 ou 11
- Python 3.10 ou superior

### ConfiguraÃ§Ã£o do Ambiente
Clone o repositÃ³rio e instale as dependÃªncias necessÃ¡rias atravÃ©s do terminal:

```cmd
git clone https://github.com/SeuUsuario/Cards-Formatura-PROGRAD.git
cd Cards-Formatura-PROGRAD
pip install -r requirements.txt
```

Para executar a aplicaÃ§Ã£o diretamente a partir do cÃ³digo-fonte:

```cmd
python main.py
```

---

## CompilaÃ§Ã£o do ExecutÃ¡vel (.exe)

O executÃ¡vel final para distribuiÃ§Ã£o aos usuÃ¡rios finais Ã© construÃ­do via PyInstaller no formato `--onefile` (arquivo Ãºnico), embutindo todas as dependÃªncias, fontes e imagens dentro do prÃ³prio binÃ¡rio.

Para compilar, execute o script de build incluso na raiz do projeto:

```cmd
build.bat
```

Ou, alternativamente, execute o comando manualmente via terminal:

```cmd
pyinstaller --onefile --windowed --icon=assets\logo.ico --name="Gerador de Cards PROGRAD" --add-data "assets;assets" main.py -y
```

ApÃ³s o tÃ©rmino da compilaÃ§Ã£o, o arquivo final (`Gerador de Cards PROGRAD.exe`) estarÃ¡ disponÃ­vel dentro do diretÃ³rio `dist/`.

---

## ObservaÃ§Ãµes de SeguranÃ§a e DistribuiÃ§Ã£o no Windows

Por se tratar de uma ferramenta interna e nÃ£o possuir um certificado digital comercial pago (Code Signing), o Microsoft Defender SmartScreen pode exibir um aviso de "Computador protegido" na primeira vez que o arquivo `.exe` for baixado da internet ou aberto via rede local.

Para resolver isso de forma transparente, a aplicaÃ§Ã£o possui uma rotina de auto-desbloqueio (`Unblock-File`) executada em segundo plano durante a primeira inicializaÃ§Ã£o. A partir da segunda execuÃ§Ã£o no mesmo computador, o sistema operacional reconhecerÃ¡ a liberaÃ§Ã£o e o programa abrirÃ¡ instantaneamente sem exibir alertas.

Caso o operador precise liberar manualmente antes de abrir a primeira vez, basta clicar com o botÃ£o direito sobre o arquivo `.exe`, acessar **Propriedades**, marcar a caixa **Desbloquear** na aba Geral e clicar em **OK**.

---

## Autoria e CrÃ©ditos

Desenvolvido por Anthony Perotti para a PrÃ³-Reitoria de GraduaÃ§Ã£o da Universidade Federal de Santa Maria (PROGRAD/UFSM).
