# Integração com Neovim

O módulo exige uma versão do Neovim que disponibilize `vim.terminal.open`.
Ele executa as gerações no terminal embutido e usa `vim.ui.select` para escolher
linguagem e padrão.

Copie ou adicione `neovim/lua/dp/init.lua` ao seu `runtimepath`, depois carregue:

```lua
require("dp").setup({
    command = ".venv/bin/dp",
    keymap = "<leader>dg",
})
```

Se o seu projeto estiver em outra pasta, configure o caminho absoluto ou uma
função para `command`:

```lua
require("dp").setup({
    command = function(root)
        return root .. "/.venv/bin/dp"
    end,
})
```

Comandos disponíveis:

```vim
:DP
:DPList
:DPGenerate kotlin factory
:DPEditConfig kotlin factory
```

`DP` abre dois seletores e executa o comando no terminal. Na primeira geração,
o arquivo `.dp/<linguagem>/<padrão>.yaml` é aberto automaticamente para edição.
As gerações seguintes reutilizam essa mesma configuração.
