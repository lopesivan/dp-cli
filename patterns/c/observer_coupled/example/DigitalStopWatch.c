#include "app_TimeObserver.h"
#include "app_TimeSubject.h"
#include <stdlib.h>

struct DigitalStopWatch {
  int watchDisplay;
};

static void changedTime(void *instance, const SystemTime *newTime) {
  DigitalStopWatchPtr watch = instance;
  /* Update display... */
}

DigitalStopWatchPtr createDigitalWatch(void) {
  DigitalStopWatchPtr watch = malloc(sizeof(*watch));
  if (watch != NULL) {
    app_TimeObserver observer = {0};
    observer.instance = watch;
    observer.notification = changedTime;
    app_TimeSubject_attach(&observer);
  }
  return watch;
}
