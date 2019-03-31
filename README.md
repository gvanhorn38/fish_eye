# fish_eye
Analyzing ARIS data to detect, track, and count fish.


# Compile C Functions

You can run the makefile, created for Mac:
```
$ make
```

Or you can modify the below line to create the `.so` file for your own platform:
```
$ gcc -DNDEBUG -shared -Wl,-install_name,arisparse -o arisparse.so -fPIC -O1 -Wall parse.c
```

# Example

Run the code found in `example.py` in an ipython console, in the project directory. This should show the individual frames from the sample video.  


# Generating GIFs

To generate GIFs for observations, run the code found in `gen_gif.py` in an ipython console, in the project directory. Note that this code requires ARIS files containing the data we want to be stored in the `aris_samples` directory.