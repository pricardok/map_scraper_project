# memory/ — Memória do Projeto para IAs

Esta pasta contém documentação **resumida e densa** sobre o projeto Map Scraper,
escrita para ser lida por modelos de IA antes de alterar código.

## Por que existe

Ler esses arquivos curtos daqui custa muito menos tokens do que reler todo o código.
Use esta pasta como **primeira fonte de contexto**.

## Ordem de leitura recomendada

| # | Arquivo | Conteúdo |
|---|---|---|
| 1 | [00-resumo-projeto.md](./00-resumo-projeto.md) | O que o projeto faz, stack, estrutura |
| 2 | [01-arquitetura-e-modulos.md](./01-arquitetura-e-modulos.md) | Cada módulo, funções principais, fluxos |
| 3 | [02-decisoes-e-armadilhas.md](./02-decisoes-e-armadilhas.md) | Decisões técnicas, bugs conhecidos, cuidados |
| 4 | [03-historico-de-mudancas.md](./03-historico-de-mudancas.md) | O que mudou recentemente e por quê |
| 5 | [04-como-contribuir.md](./04-como-contribuir.md) | Padrões de código, logs, config, testes e documentação |
| 6 | [05-plano-coleta-nacional-docker.md](./05-plano-coleta-nacional-docker.md) | **Plano aprovado (não implementado):** banco plugável, fila de jobs, circuit breaker WAHA, Docker |

## Regras de manutenção

- **Atualize ao mudar comportamento**, não a cada commit.
- Mantenha cada arquivo curto (ideal: < 200 linhas). Detalhe fica no código.
- Registre o **porquê** das decisões, não só o quê.
- Nunca coloque segredos aqui (API keys, tokens). Use `.env`.
- Datas no formato `AAAA-MM-DD`.

## Arquivos que NÃO devem ser duplicados aqui

- `README.md` (raiz) — manual do usuário, instalação, uso.
- `.env.example` — valores e comentários de cada variável.

## Git force
- Enviar
git add -A; git commit -m "Atualização"; git push --force origin main


## git forçado
- Envia
git add -A; git commit -m "Melhorias no processo de coletas v3 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; git push --force-with-lease origin main
- Recebe
git fetch --all; git reset --hard origin/main