import sys
from lib.utils import slurm_submit

cfgFile = sys.argv[1]

job_id = slurm_submit('prep', cfgFile)

