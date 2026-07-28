-- patterns/lua/builder/example/pizza_builder.lua

-- pizza_builder.lua
-- Builder Pattern para criar pizzas personalizadas

-- ============================================
-- 1. Produto: Pizza
-- ============================================
local Pizza = {}
Pizza.__index = Pizza

function Pizza:new()
  local obj = {
    tamanho = nil, -- "pequena", "media", "grande"
    massa = nil, -- "fina", "tradicional", "pan"
    queijo = nil, -- "mussarela", "cheddar", "provolone"
    ingredientes = {}, -- lista de ingredientes extras
    borda_recheada = false,
  }
  setmetatable(obj, Pizza)
  return obj
end

function Pizza:setTamanho(tamanho)
  self.tamanho = tamanho
end

function Pizza:setMassa(massa)
  self.massa = massa
end

function Pizza:setQueijo(queijo)
  self.queijo = queijo
end

function Pizza:addIngrediente(ingrediente)
  table.insert(self.ingredientes, ingrediente)
end

function Pizza:setBordaRecheada(borda)
  self.borda_recheada = borda
end

function Pizza:getDescricao()
  local descricao = string.format(
    "Pizza %s, massa %s, queijo %s",
    self.tamanho,
    self.massa,
    self.queijo
  )

  if #self.ingredientes > 0 then
    descricao = descricao
      .. ", ingredientes: "
      .. table.concat(self.ingredientes, ", ")
  end

  if self.borda_recheada then
    descricao = descricao .. ", borda recheada"
  end

  return descricao
end

function Pizza:getPreco()
  local preco = 0

  -- Preço base por tamanho
  local precos = {
    pequena = 25.00,
    media = 35.00,
    grande = 45.00,
  }
  preco = preco + (precos[self.tamanho] or 0)

  -- Adicionais
  preco = preco + (#self.ingredientes * 3.50)

  if self.borda_recheada then
    preco = preco + 5.00
  end

  return preco
end

-- ============================================
-- 2. Builder
-- ============================================
local PizzaBuilder = {}
PizzaBuilder.__index = PizzaBuilder

function PizzaBuilder:new()
  local obj = {}
  obj._pizza = Pizza:new()
  setmetatable(obj, PizzaBuilder)
  return obj
end

-- Métodos do builder
function PizzaBuilder:setTamanho(tamanho)
  self._pizza:setTamanho(tamanho)
  return self -- Retorna self para encadeamento
end

function PizzaBuilder:setMassa(massa)
  self._pizza:setMassa(massa)
  return self
end

function PizzaBuilder:setQueijo(queijo)
  self._pizza:setQueijo(queijo)
  return self
end

function PizzaBuilder:addIngrediente(ingrediente)
  self._pizza:addIngrediente(ingrediente)
  return self
end

function PizzaBuilder:comBordaRecheada()
  self._pizza:setBordaRecheada(true)
  return self
end

function PizzaBuilder:build()
  return self._pizza
end

-- ============================================
-- 3. Director (Opcional - para receitas prontas)
-- ============================================
local PizzaDirector = {}
PizzaDirector.__index = PizzaDirector

function PizzaDirector:new(builder)
  local obj = {
    _builder = builder,
  }
  setmetatable(obj, PizzaDirector)
  return obj
end

-- Receitas prontas
function PizzaDirector:makeMargherita()
  self._builder
    :setTamanho("media")
    :setMassa("tradicional")
    :setQueijo("mussarela")
    :addIngrediente("manjericão")
    :addIngrediente("tomate")
  return self._builder:build()
end

function PizzaDirector:makePepperoni()
  self._builder
    :setTamanho("grande")
    :setMassa("fina")
    :setQueijo("mussarela")
    :addIngrediente("pepperoni")
    :addIngrediente("oregano")
    :comBordaRecheada()
  return self._builder:build()
end

function PizzaDirector:makeVeggie()
  self._builder
    :setTamanho("media")
    :setMassa("pan")
    :setQueijo("provolone")
    :addIngrediente("pimentão")
    :addIngrediente("cebola")
    :addIngrediente("cogumelos")
    :addIngrediente("azeitona")
  return self._builder:build()
end

-- ============================================
-- 4. Exemplo de uso
-- ============================================

print("=== SISTEMA DE PEDIDOS DE PIZZA ===\n")

-- Exemplo 1: Construindo pizza passo a passo
print("Exemplo 1: Pizza personalizada passo a passo")
local builder = PizzaBuilder:new()
local pizza1 = builder
  :setTamanho("grande")
  :setMassa("fina")
  :setQueijo("cheddar")
  :addIngrediente("bacon")
  :addIngrediente("frango")
  :addIngrediente("catupiry")
  :comBordaRecheada()
  :build()

print("Descrição: " .. pizza1:getDescricao())
print(string.format("Preço: R$ %.2f\n", pizza1:getPreco()))

-- Exemplo 2: Usando o Director (receitas prontas)
print("Exemplo 2: Receitas prontas com Director")
local director = PizzaDirector:new(PizzaBuilder:new())

-- Pizza Margherita
local pizza2 = director:makeMargherita()
print("Margherita:")
print("  " .. pizza2:getDescricao())
print(string.format("  Preço: R$ %.2f\n", pizza2:getPreco()))

-- Pizza Pepperoni
local pizza3 = director:makePepperoni()
print("Pepperoni:")
print("  " .. pizza3:getDescricao())
print(string.format("  Preço: R$ %.2f\n", pizza3:getPreco()))

-- Pizza Veggie
local pizza4 = director:makeVeggie()
print("Veggie:")
print("  " .. pizza4:getDescricao())
print(string.format("  Preço: R$ %.2f\n", pizza4:getPreco()))

-- Exemplo 3: Sistema de pedidos interativo
print("Exemplo 3: Criando sua pizza personalizada")
local function criarPizzaPersonalizada()
  local b = PizzaBuilder:new()

  -- Tamanho
  print("Escolha o tamanho (pequena/media/grande):")
  local tamanho = io.read()
  b:setTamanho(tamanho)

  -- Massa
  print("Escolha a massa (fina/tradicional/pan):")
  local massa = io.read()
  b:setMassa(massa)

  -- Queijo
  print("Escolha o queijo (mussarela/cheddar/provolone):")
  local queijo = io.read()
  b:setQueijo(queijo)

  -- Ingredientes extras (até 3)
  local ingredientes = {
    "bacon",
    "frango",
    "catupiry",
    "manjericão",
    "tomate",
    "pepperoni",
    "pimentão",
  }
  print("Ingredientes disponíveis: " .. table.concat(ingredientes, ", "))
  print("Digite até 3 ingredientes (ou 'fim' para terminar):")

  local contador = 0
  while contador < 3 do
    print("Ingrediente " .. (contador + 1) .. ":")
    local ing = io.read()
    if ing == "fim" then
      break
    end
    b:addIngrediente(ing)
    contador = contador + 1
  end

  -- Borda recheada?
  print("Deseja borda recheada? (s/n):")
  local borda = io.read()
  if borda:lower() == "s" then
    b:comBordaRecheada()
  end

  return b:build()
end

-- Descomente para usar o modo interativo
-- local pizzaPersonalizada = criarPizzaPersonalizada()
-- print("\nSua pizza personalizada:")
-- print("  " .. pizzaPersonalizada:getDescricao())
-- print(string.format("  Preço: R$ %.2f", pizzaPersonalizada:getPreco()))

-- Exemplo 4: Lista de pedidos
print("Exemplo 4: Lista de pedidos")
local pedidos = {}

-- Adicionar pizzas ao pedido
local function adicionarPedido(builder_func)
  local builder = PizzaBuilder:new()
  local pizza = builder_func(builder)
  table.insert(pedidos, pizza)
end

-- Funções para criar pizzas
local function pizzaCalabresa(builder)
  return builder
    :setTamanho("media")
    :setMassa("tradicional")
    :setQueijo("mussarela")
    :addIngrediente("calabresa")
    :addIngrediente("cebola")
    :build()
end

local function pizzaPortuguesa(builder)
  return builder
    :setTamanho("grande")
    :setMassa("pan")
    :setQueijo("mussarela")
    :addIngrediente("ovo")
    :addIngrediente("ervilha")
    :addIngrediente("presunto")
    :addIngrediente("cebola")
    :comBordaRecheada()
    :build()
end

-- Adicionar ao pedido
adicionarPedido(pizzaCalabresa)
adicionarPedido(pizzaPortuguesa)
adicionarPedido(function(builder)
  return builder
    :setTamanho("pequena")
    :setMassa("fina")
    :setQueijo("provolone")
    :addIngrediente("rúcula")
    :addIngrediente("tomate seco")
    :build()
end)

-- Exibir todos os pedidos
print("\nResumo do pedido:")
local total = 0
for i, pizza in ipairs(pedidos) do
  print(string.format("%d. %s", i, pizza:getDescricao()))
  print(string.format("   Preço: R$ %.2f", pizza:getPreco()))
  total = total + pizza:getPreco()
end
print(string.format("\nTotal do pedido: R$ %.2f", total))

print("\n=== FIM ===")
