CC = clang

LIBDIR = generated_code
SRCDIR = .

SRCS = $(wildcard $(SRCDIR)/*.c) $(wildcard $(LIBDIR)/*.c)
OBJS = $(SRCS:.c=.o)

OBJECTS = $(OBJS)
OUTPUT = test

CFLAGS = -I$(LIBDIR) -Wall 

all: $(OUTPUT)

$(OUTPUT): $(OBJS)
	$(CC) $(OBJS) -o $(OUTPUT)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

run_tests: all
	./$(OUTPUT)
	make clean

clean:
	rm -f $(OBJS) $(OUTPUT)

clean-all: clean
	rm -f $(LIBDIR)/*.c $(LIBDIR)/*.h
