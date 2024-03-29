To run this you just need to use
`python run_prep.py configFile`
where the `configFile` is one of the files contained in `config`. There is a config file for building the training set and another for building the validation set.
This will submit a slurm job that builds the sets remotely with the use of the `configFile` for all of the necessary information.

The output files are by default sent to the top directory. You can change this in the config files. Also, the validation set is only setup to build for a few randomly chosen pixels.
If you instead want a validation set produced for the whole cosmoDC2 catalog then set pixels to `'all'` in the config file like what is done in the one for training -- just keep in mind that this will take up a lot of space.
