#include "app_singleton.h"

int main() {
  app_singleton *s1 = app_singleton_instance();
  app_singleton *s2 = app_singleton_instance();
  // s1 e s2 apontam para a mesma instância

  app_singleton_destroy();
  return 0;
}
