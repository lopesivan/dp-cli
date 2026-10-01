-- Integração Neovim para o CLI `dp` (scaffolding de design patterns).
--
-- Comandos:
--   :DP [--force]            se existe key.yaml, gera direto com ele; senão
--                            escolhe linguagem/pattern (recalcula a raiz)
--   :DP! [--force]           ignora o key.yaml e sempre mostra a seleção
--   :DPList                  roda `dp --list` no terminal
--   :DPGenerate ...          gera direto, com completion (veja abaixo)
--   :DPEditConfig            abre o key.yaml
--   :DPResetRoot             esquece raiz, pattern e cache
--
-- :DPGenerate aceita posicional ou nomeado, em qualquer ordem:
--   :DPGenerate cpp singleton
--   :DPGenerate -lang:cpp -pattern:singleton --force
--
-- Requer Neovim >= 0.10 (vim.fs.root, vim.fs.joinpath, vim.uv).

local M = {}

M.options = {
  command = ".venv/bin/dp", -- string ou function(root) -> string
  keymap = "<leader>dp",
  root_dir = nil, -- string ou function() -> string
}

local REGISTRY_TTL_MS = 30000
local OPTIONS = { "-lang:", "-pattern:", "--force" }

local state = {
  language = nil,
  pattern = nil,
  root = nil, -- raiz fixada por sessão de geração
  registry = nil, -- cache de `dp --list`
  registry_at = 0,
}

local function notify(message, level)
  vim.notify(message, level or vim.log.levels.INFO, { title = "dp" })
end

local function starts_with(s, prefix)
  return s:sub(1, #prefix) == prefix
end

---------------------------------------------------------------------------
-- raiz do projeto
---------------------------------------------------------------------------

local function resolve_root()
  if type(M.options.root_dir) == "function" then
    return M.options.root_dir()
  end

  if type(M.options.root_dir) == "string" then
    return M.options.root_dir
  end

  -- só confia no nome do buffer se for arquivo normal (não term://, help...)
  local start = vim.fn.getcwd()
  if vim.bo.buftype == "" then
    local current_file = vim.api.nvim_buf_get_name(0)
    if current_file ~= "" then
      start = vim.fs.dirname(current_file)
    end
  end

  return vim.fs.root(start, { ".git", "pyproject.toml", "Makefile" })
    or vim.fn.getcwd()
end

-- estável: calcula uma vez e reusa (o buffer atual muda quando abrimos
-- o terminal ou o key.yaml)
local function project_root()
  if not state.root then
    state.root = resolve_root()
  end
  return state.root
end

-- força recálculo e esquece a sessão anterior
function M.reset_root()
  state.root = nil
  state.language = nil
  state.pattern = nil
  state.registry = nil
  state.registry_at = 0
end

---------------------------------------------------------------------------
-- executável
---------------------------------------------------------------------------

-- Resolve o executável: absoluto, relativo à raiz, ou no PATH.
-- Retorna nil (e avisa, a menos que silent) se não achar.
local function command(silent)
  local cmd = M.options.command
  if type(cmd) == "function" then
    cmd = cmd(project_root())
  end

  local candidates = {}
  if type(cmd) == "string" and cmd ~= "" then
    if starts_with(cmd, "/") or starts_with(cmd, "~") then
      table.insert(candidates, vim.fn.expand(cmd))
    else
      table.insert(candidates, vim.fs.joinpath(project_root(), cmd))
      table.insert(candidates, cmd)
    end
  end
  table.insert(candidates, "dp") -- último recurso: PATH

  for _, candidate in ipairs(candidates) do
    if vim.fn.executable(candidate) == 1 then
      local full = vim.fn.exepath(candidate)
      return full ~= "" and full or candidate
    end
  end

  if not silent then
    notify(
      "Executável do dp não encontrado (procurei: "
        .. table.concat(candidates, ", ")
        .. ").",
      vim.log.levels.ERROR
    )
  end
  return nil
end

local function key_path()
  return vim.fs.joinpath(project_root(), "key.yaml")
end

---------------------------------------------------------------------------
-- key.yaml
---------------------------------------------------------------------------

local function yaml_value(value)
  value = vim.trim(value)

  -- aspas primeiro: um "#" dentro delas não é comentário
  local quote = value:sub(1, 1)
  if quote == '"' or quote == "'" then
    local close = value:find(quote, 2, true)
    if close then
      return value:sub(2, close - 1)
    end
  end

  return vim.trim((value:gsub("%s+#.*$", "")))
end

local function key_metadata()
  local path = key_path()
  if not vim.uv.fs_stat(path) then
    return nil
  end

  local values = {}
  for _, line in ipairs(vim.fn.readfile(path)) do
    -- só chaves de topo (sem indentação)
    local name, value = line:match("^([%w_%-]+):%s*(.-)%s*$")
    if name and value then
      values[name] = yaml_value(value)
    end
  end

  local language = values.language
  local pattern = values.pattern or values.module_name
  if not language or not pattern then
    return nil
  end

  return { language = language, pattern = pattern }
end

---------------------------------------------------------------------------
-- registry (`dp --list`) com cache
---------------------------------------------------------------------------

local function parse_registry(output)
  local registry = {}
  for line in output:gmatch("[^\r\n]+") do
    local language, items = line:match("^([%w_-]+):%s*(.*)$")
    if language then
      registry[language] =
        vim.split(items, ",", { plain = true, trimempty = true })
      for index, pattern in ipairs(registry[language]) do
        registry[language][index] = vim.trim(pattern)
      end
    end
  end
  return registry
end

local function registry_fresh()
  return state.registry ~= nil
    and (vim.uv.now() - state.registry_at) < REGISTRY_TTL_MS
end

local function store_registry(output)
  state.registry = parse_registry(output)
  state.registry_at = vim.uv.now()
  return state.registry
end

local function get_registry(callback)
  if registry_fresh() then
    callback(state.registry)
    return
  end

  local cmd = command()
  if not cmd then
    return
  end

  vim.system(
    { cmd, "--list" },
    { cwd = project_root(), text = true },
    function(result)
      vim.schedule(function()
        if result.code ~= 0 then
          notify(
            result.stderr ~= "" and result.stderr
              or "Não foi possível listar os patterns.",
            vim.log.levels.ERROR
          )
          return
        end
        callback(store_registry(result.stdout))
      end)
    end
  )
end

-- versão síncrona, usada pelo completion (cmdline não espera callback)
local function registry_sync()
  if registry_fresh() then
    return state.registry
  end

  local cmd = command(true)
  if not cmd then
    return nil
  end

  local ok, result = pcall(function()
    return vim
      .system({ cmd, "--list" }, { cwd = project_root(), text = true })
      :wait(3000)
  end)
  if not ok or not result or result.code ~= 0 then
    return nil
  end
  return store_registry(result.stdout)
end

---------------------------------------------------------------------------
-- terminal
---------------------------------------------------------------------------

local function terminal_command(cmd, arguments)
  local parts = { vim.fn.shellescape(cmd) }
  for _, argument in ipairs(arguments) do
    table.insert(parts, vim.fn.shellescape(argument))
  end
  return "cd "
    .. vim.fn.shellescape(project_root())
    .. " && "
    .. table.concat(parts, " ")
end

-- abre num split (a saída do dp continua visível) e chama on_success se exit 0
local function open_terminal(arguments, on_success)
  local cmd = command()
  if not cmd then
    return
  end

  vim.cmd("botright 15split")
  vim.cmd.terminal(terminal_command(cmd, arguments))

  local terminal_buffer = vim.api.nvim_get_current_buf()
  vim.bo[terminal_buffer].buflisted = false
  vim.bo[terminal_buffer].bufhidden = "wipe"

  vim.api.nvim_create_autocmd("TermClose", {
    buffer = terminal_buffer,
    once = true,
    callback = function()
      local exit_code = tonumber(vim.v.event.status) or 1

      vim.schedule(function()
        if exit_code == 0 then
          if on_success then
            on_success()
          end
          return
        end

        notify(
          "dp terminou com código " .. exit_code .. ".",
          vim.log.levels.ERROR
        )
      end)
    end,
  })
end

local function edit_file(path)
  vim.cmd("edit " .. vim.fn.fnameescape(path))
end

---------------------------------------------------------------------------
-- argumentos de :DPGenerate (compartilhado entre comando e completion)
---------------------------------------------------------------------------

-- Aceita nomeado (-lang:x, -pattern:y) e posicional, em qualquer ordem.
-- Nomeados são lidos primeiro; posicionais preenchem os slots que sobrarem.
local function parse_args(args)
  local parsed = { used = {} }
  local positional = {}

  for _, arg in ipairs(args) do
    if arg == "--force" then
      parsed.force = true
      parsed.used["--force"] = true
    elseif starts_with(arg, "-lang:") then
      parsed.language = arg:sub(7)
      parsed.used["-lang:"] = true
    elseif starts_with(arg, "-pattern:") then
      parsed.pattern = arg:sub(10)
      parsed.used["-pattern:"] = true
    else
      table.insert(positional, arg)
    end
  end

  for _, arg in ipairs(positional) do
    if not parsed.language then
      parsed.language = (arg:gsub("^%-+", "")) -- tolera "-cpp"
    elseif not parsed.pattern then
      parsed.pattern = arg
    end
  end

  return parsed
end

---------------------------------------------------------------------------
-- ações
---------------------------------------------------------------------------

function M.list()
  open_terminal({ "--list" })
end

-- opts: { force = bool, validated = bool }
function M.generate(language, pattern, opts)
  opts = opts or {}
  language = language or state.language
  pattern = pattern or state.pattern
  if not language or not pattern then
    M.select_and_generate(opts)
    return
  end
  language = (language:gsub("^%-+", ""))

  local function run()
    state.language = language
    state.pattern = pattern
    local path = key_path()
    local key_exists = vim.uv.fs_stat(path) ~= nil

    local arguments = { "-" .. language, pattern }
    if opts.force then
      table.insert(arguments, "--force")
    end

    open_terminal(arguments, function()
      if not key_exists and vim.uv.fs_stat(path) then
        -- key.yaml acima, saída do dp continua visível embaixo
        vim.cmd("leftabove split " .. vim.fn.fnameescape(path))
        notify("key.yaml criado. Edite e rode :DP! para gerar.")
      else
        vim.cmd.checktime() -- recarrega buffers alterados no disco
        notify("Geração concluída.")
      end
    end)
  end

  if opts.validated then
    run()
    return
  end

  -- dp cria o key.yaml mesmo com pattern inexistente: valida antes
  get_registry(function(registry)
    local patterns = registry[language]
    if not patterns then
      local languages = vim.tbl_keys(registry)
      table.sort(languages)
      notify(
        "Linguagem desconhecida: "
          .. language
          .. " (disponíveis: "
          .. table.concat(languages, ", ")
          .. ").",
        vim.log.levels.ERROR
      )
      return
    end
    if not vim.tbl_contains(patterns, pattern) then
      notify(
        string.format("Pattern '%s' não existe em %s.", pattern, language),
        vim.log.levels.ERROR
      )
      return
    end
    run()
  end)
end

function M.edit_config()
  local path = key_path()
  if vim.uv.fs_stat(path) then
    edit_file(path)
    return
  end

  notify(
    "key.yaml ainda não existe. Execute :DP primeiro.",
    vim.log.levels.WARN
  )
end

function M.select_pattern(callback)
  get_registry(function(registry)
    local languages = vim.tbl_keys(registry)
    table.sort(languages)
    if #languages == 0 then
      notify("dp --list não retornou nada.", vim.log.levels.WARN)
      return
    end

    vim.ui.select(languages, {
      prompt = "Linguagem do pattern:",
    }, function(language)
      if not language then
        return
      end
      vim.ui.select(registry[language], {
        prompt = "Pattern para " .. language .. ":",
      }, function(pattern)
        if pattern then
          callback(language, pattern)
        end
      end)
    end)
  end)
end

function M.select_and_generate(opts)
  opts = opts or {}
  M.select_pattern(function(language, pattern)
    -- veio do registry: já é válido
    M.generate(language, pattern, { force = opts.force, validated = true })
  end)
end

function M.repeat_last(opts)
  opts = opts or {}
  local metadata = key_metadata()
  if metadata then
    M.generate(metadata.language, metadata.pattern, { force = opts.force })
    return
  end

  if not state.language or not state.pattern then
    notify("key.yaml não contém language e pattern.", vim.log.levels.WARN)
    return
  end

  M.generate(state.language, state.pattern, { force = opts.force })
end

-- nova seleção = nova sessão (permite trocar de projeto)
local function start_selection(opts)
  M.reset_root()
  M.select_and_generate(opts)
end

-- Se já existe key.yaml (com language e pattern), gera direto, sem picker.
-- Sem key.yaml, cai na seleção normal.
local function smart_generate(opts)
  opts = opts or {}
  M.reset_root()

  local metadata = key_metadata()
  if metadata then
    M.generate(metadata.language, metadata.pattern, { force = opts.force })
    return
  end

  M.select_and_generate(opts)
end

---------------------------------------------------------------------------
-- completion
---------------------------------------------------------------------------

-- candidatos de `list` que começam com `typed`, devolvidos como key..item
local function filter(list, typed, key)
  local out = {}
  for _, item in ipairs(list) do
    if starts_with(item, typed) then
      table.insert(out, (key or "") .. item)
    end
  end
  return out
end

-- argumentos já completos (sem o nome do comando e sem o que está em edição)
local function completed_args(cmdline, cursorpos)
  local line = cmdline:sub(1, cursorpos)
  local tokens = vim.split(vim.trim(line), "%s+", { trimempty = true })
  table.remove(tokens, 1)
  if not line:match("%s$") then
    table.remove(tokens)
  end
  return tokens
end

local function sorted_languages(registry)
  local languages = vim.tbl_keys(registry)
  table.sort(languages)
  return languages
end

-- patterns da linguagem; sem linguagem definida, a união de todas
local function patterns_for(registry, language)
  if language and registry[language] then
    return registry[language]
  end

  local seen, out = {}, {}
  for _, items in pairs(registry) do
    for _, pattern in ipairs(items) do
      if not seen[pattern] then
        seen[pattern] = true
        table.insert(out, pattern)
      end
    end
  end
  table.sort(out)
  return out
end

local function complete_generate(arglead, cmdline, cursorpos)
  local registry = registry_sync() or {}
  local parsed = parse_args(completed_args(cmdline, cursorpos))

  -- valores: -lang:<Tab> / -pattern:<Tab>
  if starts_with(arglead, "-lang:") then
    return filter(sorted_languages(registry), arglead:sub(7), "-lang:")
  end
  if starts_with(arglead, "-pattern:") then
    return filter(
      patterns_for(registry, parsed.language),
      arglead:sub(10),
      "-pattern:"
    )
  end

  -- opções ainda não usadas
  local available = {}
  for _, option in ipairs(OPTIONS) do
    if not parsed.used[option] then
      table.insert(available, option)
    end
  end

  if starts_with(arglead, "-") then
    return filter(available, arglead)
  end

  -- posicionais: primeiro linguagem, depois pattern
  local out = {}
  if not parsed.language then
    vim.list_extend(out, filter(sorted_languages(registry), arglead))
  elseif not parsed.pattern then
    vim.list_extend(
      out,
      filter(patterns_for(registry, parsed.language), arglead)
    )
  end

  if arglead == "" then
    vim.list_extend(out, available)
  end
  return out
end

local function complete_flags(arglead)
  return filter({ "--force" }, arglead)
end

---------------------------------------------------------------------------
-- setup
---------------------------------------------------------------------------

function M.setup(options)
  M.options = vim.tbl_deep_extend("force", M.options, options or {})

  vim.api.nvim_create_user_command("DP", function(command_options)
    local parsed = parse_args(command_options.fargs)
    if command_options.bang then
      start_selection({ force = parsed.force })
      return
    end
    smart_generate({ force = parsed.force })
  end, {
    bang = true,
    nargs = "*",
    complete = complete_flags,
  })

  vim.api.nvim_create_user_command("DPList", function()
    M.list()
  end, {})

  vim.api.nvim_create_user_command("DPGenerate", function(command_options)
    local parsed = parse_args(command_options.fargs)
    M.generate(parsed.language, parsed.pattern, { force = parsed.force })
  end, {
    nargs = "*",
    complete = complete_generate,
  })

  vim.api.nvim_create_user_command("DPEditConfig", function()
    M.edit_config()
  end, { nargs = 0 })

  vim.api.nvim_create_user_command("DPResetRoot", function()
    M.reset_root()
    notify("Raiz do projeto resetada.")
  end, { nargs = 0 })

  if M.options.keymap then
    vim.keymap.set("n", M.options.keymap, function()
      smart_generate()
    end, { desc = "Generate design pattern" })
  end
end

return M
