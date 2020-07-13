CC=gcc
FLAGS=-pedantic -Wall -Wextra -Wcast-align -Wcast-qual -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-declarations -Wmissing-include-dirs  -Wredundant-decls -Wshadow -Wsign-conversion -Wstrict-overflow=5 -Wswitch-default -Wundef -Werror -Wno-unused
OUT=test

make:
	$(CC) $(FLAGS) *.c -o $(OUT)

clean:
	rm -rf $(OUT)
