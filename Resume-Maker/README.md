# Resume Maker MCP Server

MCP Server em Python para apoiar a criação e a otimização de currículos para leitura por tech recruiters e sistemas ATS.

O servidor lê a descrição da vaga, os conhecimentos comprovados do candidato e o currículo geral. O agente de IA realiza a adaptação, mantendo a estrutura HTML e salvando o resultado em `Curriculos Finalizados`.

## Pré-requisitos

- Python 3.10 ou superior.
- VS Code com suporte a MCP.
- Um agente de IA compatível com MCP.
- Uma descrição de vaga preenchida em `Fontes de conteúdo/descricao-vaga.md`.

O projeto utiliza a API `FastMCP` da linha 1.x do SDK. A dependência está fixada em `mcp<2` porque a linha 2.x substituiu essa API.

## Instalação

Abra um terminal na raiz do repositório:

```powershell
cd "C:\Users\uliss\OneDrive\Documentos\Codigos\Repositorios\MCP-Servers\Resume-Maker"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Caso o PowerShell bloqueie a ativação do ambiente virtual, execute o servidor usando diretamente `.venv\Scripts\python.exe` ou ajuste a política de execução conforme as regras da sua máquina.

## Arquivos utilizados

O servidor usa caminhos relativos ao próprio `mcp-server.py`:

- `Fontes de conteúdo/descricao-vaga.md`: descrição da vaga. Deve ser preenchido antes da análise.
- `Fontes de conteúdo/conhecimentos.md`: única fonte autorizada para as informações do candidato.
- `Fontes de conteúdo/Currículo Geral.html`: currículo-base e referência visual.
- `Curriculos Finalizados/`: destino dos currículos otimizados.
- `PROMPT_OTIMIZACAO_CURRICULO.md`: procedimento recomendado para o agente de IA.

A descrição da vaga pode ficar vazia enquanto o servidor não estiver sendo utilizado. As ferramentas de análise e gravação interrompem a execução com uma mensagem orientando o usuário a preencher o arquivo.

## Inicialização pelo VS Code

O servidor já está registrado em `.vscode/mcp.json`:

```json
{
  "servers": {
    "resume-maker": {
      "type": "stdio",
      "command": "python",
      "args": [
        "${workspaceFolder}/Resume-Maker/mcp-server.py"
      ]
    }
  }
}
```

Para usar:

1. Abra a pasta raiz `MCP-Servers` no VS Code.
2. Selecione o interpretador Python do ambiente `.venv`.
3. Certifique-se de que as dependências foram instaladas nesse ambiente.
4. Inicie ou recarregue o MCP Server `resume-maker` na interface do VS Code.
5. Cole a descrição da vaga em `Resume-Maker/Fontes de conteúdo/descricao-vaga.md`.
6. Instrua o agente a seguir `PROMPT_OTIMIZACAO_CURRICULO.md`.

## Execução manual

Para iniciar o servidor diretamente pelo terminal:

```powershell
cd "C:\Users\uliss\OneDrive\Documentos\Codigos\Repositorios\MCP-Servers"
Resume-Maker\.venv\Scripts\python.exe Resume-Maker\mcp-server.py
```

O servidor usa transporte stdio. Isso significa que ele deve ser iniciado pelo cliente MCP e não deve ser acessado por navegador ou por uma URL HTTP.

## Ferramentas disponíveis

### `get_server_status`

Confirma a existência dos arquivos de entrada, informa se a descrição da vaga está pronta e mostra o diretório de saída.

### `get_resume_optimization_context`

Retorna para o agente a descrição da vaga, o conteúdo de `conhecimentos.md`, o HTML do currículo geral e as regras essenciais de uso das fontes.

### `analyze_vacancy_match`

Compara os termos da vaga com os termos presentes em `conhecimentos.md` e no currículo geral. Retorna termos sustentados, termos já presentes, lacunas e cobertura aproximada.

Essa análise é uma orientação lexical. A decisão final deve considerar o contexto e a evidência descrita em `conhecimentos.md`.

### `save_optimized_resume`

Recebe o HTML produzido pelo agente, verifica se é um documento HTML completo com folha de estilos e salva o arquivo em `Curriculos Finalizados`.

Exemplo de nome de saída:

```text
Curriculo - Empresa - Cargo.html
```

O nome é reduzido ao nome do arquivo para impedir gravação fora do diretório de saída.

### `evaluate_resume`

Avalia o currículo em relação à vaga atual e retorna:

- nota de 0 a 10 para perspectiva de tech recruiter humano;
- nota de 0 a 10 para compatibilidade ATS;
- termos correspondentes;
- percentual de cobertura lexical.

As notas são métricas auxiliares e devem ser acompanhadas de uma análise qualitativa do agente.

## Fluxo recomendado

1. Preencha `descricao-vaga.md`.
3. Leia `PROMPT_OTIMIZADO.md`
2. Execute `get_server_status`.
3. Execute `get_resume_optimization_context`.
4. Execute `analyze_vacancy_match`.
5. Reescreva o currículo usando somente evidências de `conhecimentos.md`.
6. Preserve o HTML, CSS, links Credly, estrutura A4 e informações verdadeiras.
7. Execute `save_optimized_resume`.
8. Execute `evaluate_resume` com o HTML final.
9. Relate adaptações, requisitos atendidos, lacunas e as duas notas.

## Regras de integridade

- Não inventar cargos, resultados, métricas, datas, responsabilidades ou tecnologias.
- Não transformar cursos em experiência profissional.
- Não transformar estudos, noções, apoio ou POC em domínio avançado.
- Não declarar certificações relacionadas que não estejam registradas como obtidas.
- Usar `conhecimentos.md` como única fonte sobre o candidato.
- Manter os hyperlinks de verificação existentes.
- Manter a formatação e estrutura do currículo-base.

## Verificação local

Validar a sintaxe do servidor:

```powershell
python -m py_compile Resume-Maker\mcp-server.py
```

Validar a configuração JSON do MCP:

```powershell
Get-Content -Raw .vscode\mcp.json | ConvertFrom-Json
```
