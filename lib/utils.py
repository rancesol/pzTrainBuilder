import os, sys, yaml, subprocess, time
import glob, struct
import numpy as np
import matplotlib.pyplot as plt


def create_slurm_script(task, config, pixel) :
    with open(config) as fstream:
        param_cfg = yaml.safe_load(fstream)
    slurm_cfg = param_cfg['admin']['slurm']

    print ('...task = ', task)

    scr = __file__.replace('utils.py', '')

    logPath = os.path.join(slurm_cfg['logPath'], param_cfg['name'])
    scriptPath = os.path.join(slurm_cfg['scriptPath'], param_cfg['name'])
    if (pixel is None) :
        logPath = os.path.join(slurm_cfg['logPath'], param_cfg['name'])
        scriptPath = os.path.join(slurm_cfg['scriptPath'], param_cfg['name'])
    else :
        logPath = os.path.join(slurm_cfg['logPath'], param_cfg['name'], pixel)
        scriptPath = os.path.join(slurm_cfg['srciptPath'], param_cfg['name'], pixel)

    logFile = os.path.join(logPath, slurm_cfg['logFile'][task])
    script = os.path.join(scriptPath, slurm_cfg['scriptFile'][task])

    if not os.path.exists(logPath) :
        os.makedirs(logPath)
    if not os.path.exists(scriptPath) :
        os.makedirs(scriptPath)

    f = open(f"{script}", "w")
    f.write("#!/bin/sh\n")
    f.write(f"#SBATCH --nodes={slurm_cfg['Nnodes']}\n")
    f.write(f"#SBATCH --job-name={task}\n")
    f.write(f"#SBATCH --time={slurm_cfg['time']}\n")
    f.write(f"#SBATCH --constraint={slurm_cfg['constraint']}\n")
    f.write(f"#SBATCH --qos={slurm_cfg['qos']}\n")
    f.write(f"#SBATCH --ntasks=1\n")
    f.write(f"#SBATCH --output={logFile}\n")
    f.write(f"#SBATCH --mem={slurm_cfg['memory'][task]}GB\n")
    f.write(f"module load conda\n")
    f.write(f"conda activate rail\n")
    if pixel is None :
        f.write(f"python -u {scr}{task}.py {config}\n")
    else :
        f.write(f"python -u {src}{task}.py {config} {pixel}\n")
    f.close()
    return script


def slurm_submit(task, config, pixel=None, dep=None, gap=True) :

    if (dep is not None) and (gap == True) :
        time.sleep(3)

    script = create_slurm_script(task, config, pixel)
    if dep is not None:
        cmd = f"sbatch --depend=afterok:{dep} {script}"
    else:
        cmd = f"sbatch {script}"

    res = subprocess.run(cmd, shell=True, capture_output=True)
    job_id = str(res.stdout).split("Submitted batch job ")[1].split("\\")[0]
    return job_id



def get_pixels(cfg) :
        if cfg['pixels'] == 'all' :
            pixels = np.load('./lib/cosmodc2_hpix.npy')
        else :
            pixels = cfg['pixels']

        return [str(pix) for pix in pixels]
