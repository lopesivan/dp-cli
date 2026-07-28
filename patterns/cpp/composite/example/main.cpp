// main.cpp
#include "Component.hpp"
#include "Composite.hpp"
#include "Leaf.hpp"
#include <iostream>
#include <memory>

using namespace app;

int main() {
  std::cout << "=== Composite Pattern Demo ===\n\n";

  // Criar folhas (nós terminais)
  auto leaf1 = std::make_unique<Leaf>("A");
  auto leaf2 = std::make_unique<Leaf>("B");
  auto leaf3 = std::make_unique<Leaf>("C");
  auto leaf4 = std::make_unique<Leaf>("D");
  auto leaf5 = std::make_unique<Leaf>("E");

  // Criar composite1 com duas folhas: (A+B)
  auto composite1 = std::make_unique<Composite>();
  composite1->Add(std::move(leaf1));
  composite1->Add(std::move(leaf2));
  std::cout << "composite1 (A+B): " << composite1->Operation() << "\n";

  // Criar composite2 com uma folha e composite1: (C+(A+B))
  auto composite2 = std::make_unique<Composite>();
  composite2->Add(std::move(leaf3));
  composite2->Add(std::move(composite1));
  std::cout << "composite2 (C+(A+B)): " << composite2->Operation() << "\n";

  // Criar composite3 (raiz) com composite2 e duas folhas: ((C+(A+B))+D+E)
  auto root = std::make_unique<Composite>();
  root->Add(std::move(composite2));
  root->Add(std::move(leaf4));
  root->Add(std::move(leaf5));

  // Exibir resultado final
  std::cout << "\nÁrvore final (root): " << root->Operation() << "\n";

  // Exibir estrutura hierárquica
  std::cout << "\nEstrutura da árvore:\n";
  std::cout << "root\n";
  std::cout << "├── composite2\n";
  std::cout << "│   ├── C\n";
  std::cout << "│   └── composite1\n";
  std::cout << "│       ├── A\n";
  std::cout << "│       └── B\n";
  std::cout << "├── D\n";
  std::cout << "└── E\n";

  return 0;
}
