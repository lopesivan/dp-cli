// main.cpp
#include "AbstractFactory.hpp"
#include "ConcreteFactory1.hpp"
#include "ConcreteFactory2.hpp"
#include "ProductA.hpp"
#include "ProductB.hpp"
#include <iostream>
#include <memory>

using namespace app;

// Função para usar a fábrica e exibir os produtos
void clientCode(AbstractFactory &factory, const std::string &factoryName) {
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
  std::cout
      << "Escolha uma fábrica (1 = ConcreteFactory1, 2 = ConcreteFactory2): ";
  std::cin >> choice;

  AbstractFactory *selectedFactory = nullptr;
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
  std::cout << "Produtos criados: " << productA->Name() << " e "
            << productB->Name() << "\n";

  return 0;
}
