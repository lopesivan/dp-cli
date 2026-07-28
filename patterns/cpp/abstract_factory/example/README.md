Aqui está o `main.cpp` completo para testar o Abstract
Factory pattern que você gerou:

```cpp
// main.cpp
#include <iostream>
#include <memory>
#include "AbstractFactory.hpp"
#include "ConcreteFactory1.hpp"
#include "ConcreteFactory2.hpp"
#include "ProductA.hpp"
#include "ProductB.hpp"

using namespace app;

// Função para usar a fábrica e exibir os produtos
void clientCode(AbstractFactory& factory, const std::string& factoryName) {
    std::cout << "\n=== " << factoryName << " ===\n";

    // Criar produtos usando a fábrica
    auto productA = factory.CreateProductA();
    auto productB = factory.CreateProductB();

    // Exibir os produtos criados
    std::cout << "Criou: " << productA->Name() << "\n";
    std::cout << "Criou: " << productB->Name() << "\n";
}

int main() {
    std::cout << "=== Abstract Factory Pattern Demo ===\n";
    std::cout << "Criando famílias de produtos relacionados\n\n";

    // Criar fábricas concretas
    auto factory1 = std::make_unique<ConcreteFactory1>();
    auto factory2 = std::make_unique<ConcreteFactory2>();

    // Usar a primeira fábrica
    clientCode(*factory1, "ConcreteFactory1");

    // Usar a segunda fábrica
    clientCode(*factory2, "ConcreteFactory2");

    // Exemplo: criar produtos de ambas as fábricas lado a lado
    std::cout << "\n=== Comparação lado a lado ===\n";
    std::cout << "ConcreteFactory1 produz:\n";
    std::cout << "  ProductA: " << factory1->CreateProductA()->Name() << "\n";
    std::cout << "  ProductB: " << factory1->CreateProductB()->Name() << "\n";

    std::cout << "\nConcreteFactory2 produz:\n";
    std::cout << "  ProductA: " << factory2->CreateProductA()->Name() << "\n";
    std::cout << "  ProductB: " << factory2->CreateProductB()->Name() << "\n";

    // Exemplo: escolha da fábrica em tempo de execução
    std::cout << "\n=== Escolha de fábrica em tempo de execução ===\n";
    int choice = 1;
    std::cout << "Escolha uma fábrica (1 = ConcreteFactory1, 2 = ConcreteFactory2): ";
    std::cin >> choice;

    AbstractFactory* selectedFactory = nullptr;
    std::string selectedName;

    if (choice == 1) {
        selectedFactory = factory1.get();
        selectedName = "ConcreteFactory1";
    } else if (choice == 2) {
        selectedFactory = factory2.get();
        selectedName = "ConcreteFactory2";
    } else {
        std::cout << "Opção inválida! Usando ConcreteFactory1 por padrão.\n";
        selectedFactory = factory1.get();
        selectedName = "ConcreteFactory1 (padrão)";
    }

    // Usar a fábrica selecionada
    auto productA = selectedFactory->CreateProductA();
    auto productB = selectedFactory->CreateProductB();
    std::cout << "\nFábrica selecionada: " << selectedName << "\n";
    std::cout << "Produtos criados: " << productA->Name() << " e " << productB->Name() << "\n";

    return 0;
}
```

## CMakeLists.txt (para compilar com CMake)

```cmake
cmake_minimum_required(VERSION 3.10)
project(AbstractFactoryDemo)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(abstract_factory_demo
    main.cpp
    src/ConcreteFactory1.cpp
    src/ConcreteFactory2.cpp
)

target_compile_features(abstract_factory_demo PRIVATE cxx_std_14)
```

## Como compilar e executar:

### Opção 1: Compilação direta com g++
```bash
g++ -std=c++14 -Iinclude -o abstract_factory_demo \
    main.cpp \
    src/ConcreteFactory1.cpp \
    src/ConcreteFactory2.cpp

./abstract_factory_demo
```

### Opção 2: Compilação separada (para projetos maiores)
```bash
# Compilar os objetos
g++ -std=c++14 -Iinclude -c src/ConcreteFactory1.cpp -o ConcreteFactory1.o
g++ -std=c++14 -Iinclude -c src/ConcreteFactory2.cpp -o ConcreteFactory2.o
g++ -std=c++14 -Iinclude -c main.cpp -o main.o

# Linkar
g++ -o abstract_factory_demo ConcreteFactory1.o ConcreteFactory2.o main.o

./abstract_factory_demo
```

### Opção 3: Com Makefile simples
```makefile
# Makefile
CXX = g++
CXXFLAGS = -std=c++14 -Iinclude
TARGET = abstract_factory_demo
SOURCES = main.cpp src/ConcreteFactory1.cpp src/ConcreteFactory2.cpp
OBJECTS = $(SOURCES:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

run: $(TARGET)
	./$(TARGET)
```

## Saída esperada:

```
=== Abstract Factory Pattern Demo ===
Criando famílias de produtos relacionados


=== ConcreteFactory1 ===
Criou: ConcreteProductA1
Criou: ConcreteProductB1

=== ConcreteFactory2 ===
Criou: ConcreteProductA2
Criou: ConcreteProductB2

=== Comparação lado a lado ===
ConcreteFactory1 produz:
  ProductA: ConcreteProductA1
  ProductB: ConcreteProductB1

ConcreteFactory2 produz:
  ProductA: ConcreteProductA2
  ProductB: ConcreteProductB2

=== Escolha de fábrica em tempo de execução ===
Escolha uma fábrica (1 = ConcreteFactory1, 2 = ConcreteFactory2): 2

Fábrica selecionada: ConcreteFactory2
Produtos criados: ConcreteProductA2 e ConcreteProductB2
```

## Exemplo adicional: Cliente que aceita qualquer fábrica

Se você quiser testar com uma função que aceita qualquer fábrica:

```cpp
// Função que aceita qualquer AbstractFactory
void testFactory(AbstractFactory& factory) {
    auto pa = factory.CreateProductA();
    auto pb = factory.CreateProductB();

    std::cout << "Testando fábrica:\n";
    std::cout << "  ProductA: " << pa->Name() << "\n";
    std::cout << "  ProductB: " << pb->Name() << "\n";
}

// Uso no main
int main() {
    ConcreteFactory1 factory1;
    ConcreteFactory2 factory2;

    // As duas chamadas funcionam porque ambas implementam AbstractFactory
    testFactory(factory1);
    testFactory(factory2);

    return 0;
}
```
