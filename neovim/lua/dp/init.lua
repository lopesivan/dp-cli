local M = {}

M.options = {
  command = ".venv/bin/dp",
  keymap = "<leader>dp",
  root_dir = nil,
}

local state = {
  language = nil,
  pattern = nil,
  root = nil, -- << NOVO: raiz fixada por sessão de geração
}

local function notify(message, level)
  vim.notify(message, level or vim.log.levels.INFO, { title = "dp" })
end

local function resolve_root()
  if type(M.options.root_dir) == "function" then
    return M.options.root_dir()
  end

  if type(M.options.root_dir) == "string" then
    return M.options.root_dir
  end

  local current_file = vim.api.nvim_buf_get_name(0)
  local start = current_file ~= "" and vim.fs.dirname(current_file)
    or vim.fn.getcwd()
  return vim.fs.root(start, { ".git", "pyproject.toml", "Makefile" })
    or vim.fn.getcwd()
end

-- project_root() agora é estável: calcula uma vez e reusa,
-- em vez de recalcular a cada chamada com base no buffer atual
-- (que muda depois que abrimos o key.yaml pra edição).
local function project_root()
  if not state.root then
    state.root = resolve_root()
  end
  return state.root
end

-- reseta a raiz cacheada; use quando quiser forçar recálculo
-- (ex: começando geração num projeto diferente)
function M.reset_root()
  state.root = nil
end

local function command()
  if type(M.options.command) == "function" then
    return M.options.command(project_root())
  end
  return M.options.command
end

local function key_path()
  return vim.fs.joinpath(project_root(), "key.yaml")
end

local function yaml_value(value)
  value = vim.trim((value:gsub("%s+#.*$", "")))
  local quote = value:sub(1, 1)

  if (quote == '"' or quote == "'") and value:sub(-1) == quote then
    return value:sub(2, -2)
  end

  return value
end

local function key_metadata()
  local path = key_path()
  if not vim.uv.fs_stat(path) then
    return nil
  end

  local values = {}
  for _, line in ipairs(vim.fn.readfile(path)) do
    local name, value = line:match("^%s*([%w_%-]+):%s*(.-)%s*$")
    if name and value then
      values[name] = yaml_value(value)
    end
  end

  local language = values.language
  local pattern = values.pattern or values.module_name
  if not language or not pattern then
    return nil
  end

  return {
    language = language,
    pattern = pattern,
  }
end

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

local function get_registry(callback)
  vim.system(
    { command(), "--list" },
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
        callback(parse_registry(result.stdout))
      end)
    end
  )
end

local function terminal_command(arguments)
  local parts = {
    vim.fn.shellescape(command()),
  }

  for _, argument in ipairs(arguments) do
    table.insert(parts, vim.fn.shellescape(argument))
  end

  return "cd "
    .. vim.fn.shellescape(project_root())
    .. " && "
    .. table.concat(parts, " ")
end

local function open_terminal(arguments, on_success)
  vim.cmd.terminal(terminal_command(arguments))

  local terminal_buffer = vim.api.nvim_get_current_buf()

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

function M.list()
  open_terminal({ "--list" })
end

function M.generate(language, pattern)
  language = language or state.language
  pattern = pattern or state.pattern
  if not language or not pattern then
    M.select_and_generate()
    return
  end

  state.language = language
  state.pattern = pattern
  local path = key_path()
  local key_exists = vim.uv.fs_stat(path) ~= nil

  open_terminal({ "-" .. language, pattern }, function()
    if not key_exists then
      edit_file(path)
    end
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

function M.select_and_generate()
  M.select_pattern(function(language, pattern)
    M.generate(language, pattern)
  end)
end

function M.repeat_last()
  local metadata = key_metadata()
  if metadata then
    M.generate(metadata.language, metadata.pattern)
    return
  end

  if not state.language or not state.pattern then
    notify("key.yaml não contém language e pattern.", vim.log.levels.WARN)
    return
  end

  M.generate(state.language, state.pattern)
end

function M.setup(options)
  M.options = vim.tbl_deep_extend("force", M.options, options or {})

  vim.api.nvim_create_user_command("DP", function(command_options)
    if command_options.bang then
      M.repeat_last()
      return
    end

    -- nova seleção de padrão = nova "sessão" -> permite trocar de projeto
    M.reset_root()
    M.select_and_generate()
  end, { bang = true })
  vim.api.nvim_create_user_command("DPList", M.list, {})
  vim.api.nvim_create_user_command("DPGenerate", function(command_options)
    M.generate(command_options.fargs[1], command_options.fargs[2])
  end, { nargs = "*" })
  vim.api.nvim_create_user_command("DPEditConfig", function()
    M.edit_config()
  end, { nargs = 0 })
  vim.api.nvim_create_user_command("DPResetRoot", function()
    M.reset_root()
    notify("Raiz do projeto resetada.")
  end, { nargs = 0 })

  if M.options.keymap then
    vim.keymap.set("n", M.options.keymap, function()
      M.reset_root()
      M.select_and_generate()
    end, {
      desc = "Generate design pattern",
    })
  end
end

return M
