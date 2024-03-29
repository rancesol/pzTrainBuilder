import os, sys, yaml
import tables_io
import numpy as np
from utils import get_pixels


with open(sys.argv[1]) as fstream :
    cfg = yaml.safe_load(fstream)

## all of the healpix pixels in cosmoDC2 footprint
pixels = get_pixels(cfg)

datadir = "/global/cfs/cdirs/lsst/groups/PZ/PhotoZDC2/COSMODC2v1.1.4/IMAGE/10_year_error_estimates"



outpath = os.path.join(cfg['outpath'], cfg['name'])
if not os.path.exists(outpath) :
    os.makedirs(outpath)

## training set is small enough for single file
## validation set could be much larger so we break into healpix files
if cfg['stype'] == 'training' :
        magLimit = 25.3
        outfiles = os.path.join(outpath, f"cosmodc2_i{magLimit}_training.hdf5")
elif cfg['stype'] == 'validation' :
        magLimit = 26.5
        outfiles = [os.path.join(outpath, f"cosmodc2_i{magLimit}_validation_{pix}pix.hdf5") for pix in pixels]




## read the galaxies of the selected pixels  and add colors
xsum_total = 0
bigdata = {}
bands = ['u', 'g', 'r', 'i', 'z', 'y']

for ix,pix in enumerate(pixels) :
        print(f"Pixel {pix}\t{ix+1} out of {len(pixels)}...")
        xsum_pix = 0
        bigdata_pix = {}
        for iy,zz in enumerate(['z_0_1', 'z_1_2', 'z_2_3']) :
                fname = f"{zz}.step_all.healpix_{pix}_magwerrSNtrim.hdf5"
                fpath = os.path.join(datadir, fname)
                data = tables_io.read(fpath)['photometry']

                ## look at only i<magLimit galaxies and galaxies passing mag limits
                mask = (data['mag_i_lsst'] < magLimit)
                for band in bands :
                        mask &= (data[f"mag_{band}_lsst"] < cfg['mag_limits'][f"mag_{band}_lsst"])


                xsum_zbin = len(data['redshift'][mask])
                xsum_pix += xsum_zbin
                print(f"\t{zz}: {xsum_zbin} galaxies")


                ## add colors and color_errs
                for i in range(len(bands) - 1) :
                        color = np.array(data[f"mag_{bands[i]}_lsst"] - data[f"mag_{bands[i+1]}_lsst"])
                        color_err = np.hypot(data[f"mag_err_{bands[i]}_lsst"], data[f"mag_err_{bands[i+1]}_lsst"])

                        color[color >  8] =  8
                        color[color < -8] = -8

                        data[f"{bands[i]}{bands[i+1]}"] = color
                        data[f"{bands[i]}{bands[i+1]}_err"] = color_err

                if (iy==0) :
                        for iz, thing in enumerate(data):
                                tmparr = np.array(data[thing])
                                #shortarr = tmparr[mask][::int(cfg['nFrac'])]
                                shortarr = tmparr[mask]
                                bigdata_pix[thing] = shortarr
                else:
                        for iz, thing in enumerate(data):
                                tmparr = np.array(data[thing])
                                #shortarr = tmparr[mask][::int(cfg['nFrac'])]
                                shortarr = tmparr[mask]
                                bigdata_pix[thing] = np.append(bigdata_pix[thing], shortarr)


        xsum_total += xsum_pix
        print(f"\tTotal: {xsum_pix} galaxies")

        if cfg['stype'] == 'training' :
                N = int(cfg['N'])
                N_perPix = int( N / len(pixels) )
                ind2use = np.random.choice(range(len(bigdata_pix['mag_i_lsst'])), size=N_perPix, replace=False)
                for thing in bigdata_pix :
                        if (ix!=0) :
                                bigdata[thing] = np.append(bigdata[thing], bigdata_pix[thing][ind2use])
                        else :
                                bigdata[thing] = bigdata_pix[thing][ind2use]
                print(f"\tSelected: {len(ind2use)} galaxies")

        if cfg['stype'] == 'validation' :
                outdict = dict(photometry=bigdata_pix)
                tables_io.write(outdict, outfiles[ix])
                bigdata_pix = {}

print(f"{xsum_total} total galaxies")

if cfg['stype'] == 'training' :
        print(f"{N_perPix * len(pixels)} selected galaxies")
        outdict = dict(photometry=bigdata)
        tables_io.write(outdict, outfiles)

