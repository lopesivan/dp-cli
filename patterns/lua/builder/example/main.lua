-- patterns/lua/builder/example/main.lua
-- main.lua - Exemplo de uso do Builder Pattern

local builder = require("builder")

-- Função para exibir o produto
local function showProduct(product)
  print("=== Produto ===")
  print("PartA: " .. (product:getPartA() or "nil"))
  print("PartB: " .. (product:getPartB() or "nil"))
  print()
end

print("=== Builder Pattern Demo ===\n")

-- Exemplo 1: Usando o Builder diretamente
print("Exemplo 1: Usando o ConcreteBuilder diretamente")
local concreteBuilder = builder.ConcreteBuilder:new()

-- Construir o produto passo a passo
concreteBuilder:buildPartA()
concreteBuilder:buildPartB()

-- Obter o resultado
local product1 = concreteBuilder:getResult()
showProduct(product1)

-- Exemplo 2: Usando o Director para orquestrar a construção
print("Exemplo 2: Usando o Director")
local builder2 = builder.ConcreteBuilder:new()
local director = builder.Director:new(builder2)

-- Director constrói o produto automaticamente
director:construct()

local product2 = builder2:getResult()
showProduct(product2)

-- Exemplo 3: Personalizando o Builder (exemplo avançado)
print("Exemplo 3: Personalizando a construção")
local customBuilder = builder.ConcreteBuilder:new()

-- Construir apenas uma parte
customBuilder:buildPartA()
-- A parte B permanece nil

local product3 = customBuilder:getResult()
showProduct(product3)

-- Exemplo 4: Múltiplos builders
print("Exemplo 4: Múltiplos builders com diferentes configurações")
local builders = {
  builder.ConcreteBuilder:new(),
  builder.ConcreteBuilder:new(),
  builder.ConcreteBuilder:new(),
}

-- Construir produtos diferentes
builders[1]:buildPartA()
builders[1]:buildPartB()

builders[2]:buildPartA()
-- builders[2] não tem PartB

builders[3]:buildPartB()
-- builders[3] não tem PartA

for i, b in ipairs(builders) do
  local p = b:getResult()
  print(
    string.format(
      "Produto %d: PartA=%s, PartB=%s",
      i,
      p:getPartA() or "nil",
      p:getPartB() or "nil"
    )
  )
end
print()

-- Exemplo 5: Função helper para criar produtos completos
print("Exemplo 5: Função helper para criar produtos completos")
local function createProductWithParts(partA, partB)
  local b = builder.ConcreteBuilder:new()
  if partA then
    b:buildPartA()
  end
  if partB then
    b:buildPartB()
  end
  return b:getResult()
end

local product4 = createProductWithParts(true, true)
showProduct(product4)

local product5 = createProductWithParts(true, false)
showProduct(product5)

-- Exemplo 6: Simulando um sistema de construção de pedidos
print("Exemplo 6: Sistema de construção de pedidos")
local function createOrder(builder_type)
  local b
  if builder_type == "complete" then
    b = builder.ConcreteBuilder:new()
    local director = builder.Director:new(b)
    director:construct()
  else
    b = builder.ConcreteBuilder:new()
    b:buildPartA()
  end
  return b:getResult()
end

print("Pedido completo:")
local order1 = createOrder("complete")
showProduct(order1)

print("Pedido simples (apenas PartA):")
local order2 = createOrder("simple")
showProduct(order2)

print("=== Fim do Demo ===\n")
