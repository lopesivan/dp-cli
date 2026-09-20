# dp.nvim

Integração do [`dp`](.) (gerador de padrões de projeto) com o Neovim. Executa
as gerações no terminal embutido e usa `vim.ui.select` para escolher
linguagem e padrão, evitando sair do editor.

## Requisitos

- Neovim 0.10+ (usa `vim.uv`, `vim.fs.root`, `vim.fs.joinpath`).
- O comando `dp` instalado (via `pipx` ou em um `.venv`), acessível pelo
  caminho configurado em `command`.

## Instalação

### lazy.nvim

```lua
{
  dir = "/caminho/para/neovim/lua/dp", -- ou url do repositório, se publicado
  config = function()
    require("dp").setup({
      command = ".venv/bin/dp",
      keymap = "<leader>dp",
    })
  end,
}
```

### Manual

Copie `neovim/lua/dp/init.lua` para algum diretório do seu `runtimepath`
(por exemplo `~/.config/nvim/lua/dp/init.lua`) e carregue no seu `init.lua`:

```lua
require("dp").setup({
  command = ".venv/bin/dp",
  keymap = "<leader>dp",
})
```

## Configuração

```lua
require("dp").setup({
  -- Caminho do executável dp, relativo à raiz do projeto, ou função
  -- que recebe a raiz e retorna o caminho.
  command = ".venv/bin/dp",

  -- Atalho para abrir o seletor de linguagem/padrão. nil desativa.
  keymap = "<leader>dp",

  -- Raiz do projeto. Por padrão é detectada automaticamente a partir do
  -- buffer atual, procurando por .git, pyproject.toml ou Makefile.
  -- Pode ser uma string fixa ou uma função:
  root_dir = function(root)
    return root .. "/.venv/bin/dp" -- exemplo: usado junto com command
  end,
})
```

A raiz do projeto é calculada uma vez por "sessão de geração" e reutilizada,
mesmo que você abra outros buffers no meio do processo (como o `key.yaml`
gerado). Use `:DPResetRoot` para forçar um novo cálculo.

## Comandos

| Comando | Descrição |
|---|---|
| `:DP` | Abre os seletores de linguagem e padrão (`vim.ui.select`) e executa a geração no terminal. Se já existir um `key.yaml` válido na raiz do projeto, gera direto a partir dele, sem perguntar. |
| `:DP!` | Repete a última geração usando `key.yaml` (ou a última linguagem/padrão usados na sessão), sem abrir seletores. |
| `:DPList` | Lista, no terminal, as linguagens e padrões disponíveis (`dp --list`). |
| `:DPGenerate {linguagem} {padrao}` | Gera diretamente, sem seletor. Ex.: `:DPGenerate kotlin factory`. |
| `:DPEditConfig` | Abre o `key.yaml` da raiz atual para edição. Avisa se o arquivo ainda não existe. |
| `:DPResetRoot` | Limpa a raiz de projeto cacheada, forçando recálculo na próxima geração. |

O mapeamento configurado em `keymap` (padrão `<leader>dp`) reseta a raiz e
abre os seletores, equivalente a `:DPResetRoot` seguido de `:DP`.

## Fluxo de uso

O `dp` funciona em duas etapas: a primeira execução cria um `key.yaml`
editável; a segunda lê esse arquivo e gera o código.

1. Rode `:DP` (ou o keymap). Escolha a linguagem e o padrão nos seletores.
2. O plugin executa `dp --<linguagem> <padrao>` no terminal embutido.
3. Na primeira geração, apenas o `key.yaml` é criado — o plugin abre esse
   arquivo automaticamente para você editar os campos.
4. Edite o `key.yaml` e salve.
5. Rode `:DP` novamente (ou `:DP!`): como o `key.yaml` já existe e é válido,
   o plugin lê `language`/`pattern` direto dele e gera o código, sem
   perguntar de novo.

### Exemplo

```vim
:DP
" -> seleciona: java, singleton
" -> cria key.yaml e abre para edição
```

Edite `key.yaml`:

```yaml
pattern: singleton
language: java
package: br.eng.ivanlopes.patterns
class_name: AppSingleton
instance_method: getInstance
output_dir: src/main/java/br/eng/ivanlopes/patterns
thread_safe: true
```

```vim
:DP
" -> detecta key.yaml existente, gera direto:
" Gerado: src/main/java/br/eng/ivanlopes/patterns/AppSingleton.java
```

Para gerar sem passar pelos seletores desde o início:

```vim
:DPGenerate java singleton
```

## Detecção de erros

Se o comando `dp` terminar com código de saída diferente de zero, o plugin
mostra uma notificação de erro (`vim.notify`) com o código retornado. A
saída completa continua visível no terminal embutido.
