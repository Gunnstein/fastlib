# -*- coding: utf-8 -*-
import logging
from multiprocessing.dummy import Pool, Lock
import subprocess
import time
import sys


logger = logging.getLogger("fastlib.multiprocessing")

class MultiProcessHandler:
    """MultiProcessHandler distributes input files to a cpu pool.

    MultiProcessHandler takes in a input_files, sets up a processing
    pool, distributes the input files to the processes which runs 
    the command 
    
        binary_name input_file 
    
    in the shell.

    Arguments
    ---------
    input_files : list[str]
        A list of strings to the input files.
    ncpus : Optional[int]
        Number of cpus to use in the simulations.
    binary_name : Optional[str]   
        Name of binary/executable to send the input files to. 
    stream : Optional[fileobj]
        File object to report the results from the processes.
    """
    def __init__(self, input_files, ncpus=2, binary_name='fast', stream=sys.stdout):
        self.input_files = input_files
        self.ncpus = ncpus
        self.binary_name = binary_name
        self.stream = stream
        self.lock = Lock()

    def start(self):
        """Start processing input file with the cpu pool."""
        t0 = time.time()
        with self.lock:
            logger.info(f"Start processing files with {self.ncpus} cpus")
        with Pool(processes=self.ncpus) as pool:
            args = [(self.binary_name, input_file, self.lock) 
                    for input_file in self.input_files]

            args = self.input_files
            pool.map(self._run, args)
        dt = time.time() - t0
        with self.lock:
            logger.info(f"Finished files in {dt:.1f} seconds")

    def _run(self, input_file):
        """This method is sent to the processing pool by the `start` method."""
        t0 = time.time()
        with self.lock:
            logger.info(f"Start {self.binary_name} with input file {input_file}")

        # # Submit input file to the binary
        result = subprocess.run([self.binary_name, input_file], 
                                  shell=True, capture_output=True,)

        dt = time.time() - t0
        with self.lock:
            try:
                result.check_returncode()
                logger.info(f"Finished {self.binary_name} with input file {input_file} in {dt:.1f} seconds.")
                if self.stream is not None:
                    self.stream.write(result.stdout.decode("utf8"))
            except subprocess.CalledProcessError:
                stdout = result.stdout.decode("utf8").replace('\r\n', " ").replace('\n', " ")
                stderr = result.stderr.decode("utf8").replace('\r\n', " ").replace('\n', " ")
                logger.error(f"[STDOUT]: {stdout}, [STDERR]: {stderr}")

