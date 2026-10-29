# Guia Completo de Instalação e Configuração do Repomix (pt-BR)

Este guia serve como um passo a passo para instalar, configurar e rodar o **Repomix** em qualquer projeto, garantindo que o arquivo gerado seja em Markdown e que a IA interaja sempre em Português do Brasil (pt-BR).

---

## 1. Instalação Inicial (Primeira Vez de Uso)

Se você nunca usou o Repomix na sua máquina, você pode optar por instalar o Node.js/npm e instalar o Repomix de forma global no sistema para liberar o comando direto:

```bash
# Instalação global do Repomix no sistema
npm install -g repomix
```

*Nota: Se preferir não instalar nada globalmente, você pode pular esta instalação e usar sempre o prefixo `npx` antes dos comandos.*

---

## 2. Criar o Arquivo de Instrução em Português

Para forçar a IA a responder estritamente no seu idioma, crie um arquivo de texto na raiz do seu projeto chamado **`repomix-instrucao.md`** e cole o seguinte conteúdo dentro dele:

```markdown
# Instruções para o Assistente de IA
Você é um desenvolvedor especialista trabalhando neste projeto.
Por favor, processe todas as solicitações, explicações, comentários de código e interações estritamente em Português do Brasil (pt-BR).
```

---

## 3. Como Executar (Escolha a Opção A ou B)

Você pode rodar o Repomix de duas formas diferentes nos seus projetos:

### Opção A: Comando Direto via Terminal (Sem precisar de arquivo JSON)
Se você quer apenas rodar o comando rapidamente em um projeto novo apontando para a sua instrução em português e gerando um arquivo Markdown, execute:

```bash
# Se instalou globalmente:
repomix --instruction-file-path repomix-instrucao.md --format markdown

# Ou via npx (sem instalação global):
npx repomix --instruction-file-path repomix-instrucao.md --format markdown
```

### Opção B: Automatizar com Arquivo de Configuração (Recomendado para o dia a dia)
Se você não quer digitar comandos longos toda vez, crie o arquivo de configuração do Repomix:

```bash
npx repomix --init
```

Isso gerará o arquivo `repomix.config.json` na raiz. Abra-o e substitua todo o conteúdo pelo modelo abaixo, que já deixa o formato Markdown e a instrução em português configurados por padrão:

```json
{
  "\$schema": "https://repomix.com",
  "input": {
    "maxFileSize": 52428800
  },
  "output": {
    "filePath": "repomix-output.md",
    "style": "markdown",
    "filePathStyle": "target-relative",
    "parsableStyle": false,
    "instructionFilePath": "repomix-instrucao.md",
    "fileSummary": true,
    "directoryStructure": true,
    "files": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 5,
    "showLineNumbers": false,
    "truncateBase64": false,
    "copyToClipboard": false,
    "includeFullDirectoryStructure": false,
    "tokenCountTree": false,
    "git": {
      "sortByChanges": true,
      "sortByChangesMaxCommits": 100,
      "includeDiffs": false,
      "includeLogs": false,
      "includeLogsCount": 50
    }
  },
  "include": [],
  "ignore": {
    "useGitignore": true,
    "useDotIgnore": true,
    "useDefaultPatterns": true,
    "customPatterns": []
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
```

Depois de salvar esse JSON, basta rodar o comando simplificado no terminal para gerar seu pacote pronto:

```bash
repomix
# ou
npx repomix
```

---

## 4. Resultado Final
O Repomix vai gerar o arquivo **`repomix-output.md`**. Suas diretrizes em português estarão fixadas no início do documento. Basta enviar esse arquivo para o ChatGPT, Claude, DeepSeek ou Gemini e começar a interagir em português!
