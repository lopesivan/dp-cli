-- patterns/lua/composite/example/main.lua
local composite = require("composite")

-- Criar folhas
local leaf1 = composite.Leaf:new("A")
local leaf2 = composite.Leaf:new("B")
local leaf3 = composite.Leaf:new("C")

-- Criar composite e adicionar folhas
local composite1 = composite.Composite:new()
composite1:add(leaf1)
composite1:add(leaf2)

-- Criar composite raiz
local root = composite.Composite:new()
root:add(composite1)
root:add(leaf3)

-- Executar operação
print(root:operation()) -- Saída: ((A+B)+C)
