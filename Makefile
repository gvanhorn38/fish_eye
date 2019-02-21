CC=gcc
CFLAGS=-Wall
main: arisparse.so
	$(CC) -DNDEBUG -shared -Wl,-install_name,arisparse -o arisparse.so -fPIC -O1 -Wall parse.c
clean:
	rm -f arisparse.so