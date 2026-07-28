#include "app_EventHandler.h"
#include "app_Reactor.h"
#include <stdio.h>

/* Concrete event handler */
typedef struct {
  int socket;
  char name[64];
} MyHandler;

static app_Handle getHandler(void *instance) {
  MyHandler *h = instance;
  return h->socket;
}

static void handleEvent(void *instance) {
  MyHandler *h = instance;
  printf("Event on socket %d: %s\n", h->socket, h->name);
}

int main() {
  MyHandler handler = {.socket = 42, .name = "My Socket"};
  app_EventHandler eventHandler = {.instance = &handler,
                                   .getHandle = getHandler,
                                   .handleEvent = handleEvent};

  app_Reactor_Register(&eventHandler);

  for (;;) {
    app_Reactor_HandleEvents();
  }

  return 0;
}
