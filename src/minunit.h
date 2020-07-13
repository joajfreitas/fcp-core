/* file: minunit.h */

#ifndef __MIN_UNIT_
#define __MIN_UNIT_

#include <stdbool.h>
#include <string.h>

#define mu_assert(msg, test) do { strcpy(message, msg); if (!(test)) return true; } while (0)
#define mu_run_test(test) do { bool r = test(); tests_run++; \
                                if (r) {return message;} else {printf("TEST %d %s ✓\n", tests_run, message);} } while (0)
extern int tests_run;
extern char message[];

#endif
