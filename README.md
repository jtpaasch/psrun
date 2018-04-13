# Psrun

Executes a command, and collects system statistics as it runs.


## Install

Run `make install`. This assumes you have pip installed,
or better: you have activated a virtual environment.


## Quality

Run `make test`.


## CLI Usage

To execute the command ``ls -la``:

    psrun 'ls -la'

This will print system statistics as ``ls -la`` runs.

To send the statistics to a different place:

    psrun 'ls -la' --ps-log /path/to/ps.log

To send the stdout of `ls -la` to, say, stdout:

    psrun 'ls -la' --stdout-log stdout

To send the stderr of `ls -la` to, say, stderr:

    psrun 'ls -la' --stdout-log stdout

To silence the runner's information:

    psrun 'ls -la' --runner-log /dev/null

To give `ls -la` a timeout:

    psrun 'ls -la' --timeout 5

See `psrun --help` for all the options.
