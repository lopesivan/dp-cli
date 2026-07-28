#include "app_Customer.h"
#include "app_Strategies.h"

int main() {
  // Criar cliente com estratégia bronze
  app_CustomerPtr customer = app_Customer_create(app_bronzeStrategy);

  // Calcular preço
  double price = app_Customer_execute(customer, 100.0, 10.0);

  // Mudar para estratégia gold
  app_Customer_changeStrategy(customer, app_goldStrategy);
  price = app_Customer_execute(customer, 100.0, 10.0);

  app_Customer_destroy(customer);
  return 0;
}
