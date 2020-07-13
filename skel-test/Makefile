CC=gcc
FLAGS=-pedantic -Wall -Wextra -Wcast-align -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-include-dirs  -Wstrict-overflow=5 -Wundef -Wno-unused -Wall -W -Wcast-align -Wcast-qual -Winline -Wpointer-arith -Wredundant-decls -Wshadow
OUT=test

make:
	$(CC) $(FLAGS) *.c -o $(OUT)

test: make
	./$(OUT)

clean:
	rm -rf $(OUT)

