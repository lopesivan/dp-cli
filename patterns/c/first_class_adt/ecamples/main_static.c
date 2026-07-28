// Gerado com: prefix=app, adt_name=Customer, allocation_strategy=static_pool,
// max_objects=100
#include "app_Customer.h"

int main() {
  app_CustomerPtr customer = app_Customer_create(/* params */);
  // Use customer...
  // A destruição não libera memória, apenas marca como não usado (simplificado)
  app_Customer_destroy(customer);
  return 0;
}
