# particle_overlap
Command-line script for removing duplicate particles when merging two RELION particle sets from the same cryo-EM dataset.

It was developed in the laboratory of Ana Casanal at Human Technopole (Milan, Italy) for the analysis in:

> Lassandro, M. *et al.* RNA recognition and modification by the eukaryotic m6A writer complex. *Nature Structural & Molecular Biology* (2026).

## Description

`particle_overlap` takes two RELION particle `.star` files from the same dataset and compares the picked
coordinates (`_rlnCoordinateX`, `_rlnCoordinateY`) micrograph by micrograph. Two picks that lie within a
user-defined radius (in pixels) of each other are considered to be the same particle. The script then
sorts the particles into those found only in the first file, only in the second file, and in both, and
writes a merged, non-redundant set in which each duplicated particle is kept once (with the coordinates
of the first file).

Input: two RELION (3.1 or later) particle `.star` files that refer to the same micrographs.

## Requirements

- Python 3.8 or later
- pandas

```bash
pip install pandas
```

## Usage

```bash
python particle_overlap.py --star1 picks_A.star --star2 picks_B.star --radius 20
```

| Argument   | Description |
|------------|-------------|
| `--star1`  | First RELION particle `.star` file |
| `--star2`  | Second RELION particle `.star` file |
| `--radius` | Distance threshold in pixels (same units as `_rlnCoordinateX/Y`) used to decide whether two picks are the same particle |

## Output

Four `.star` files are written to the current working directory (existing files with the same names
are overwritten): `star1.star`, `star2.star`, `combined.star` and `unique.star`.

## Repository

Source code: https://github.com/miclassandro/particle_overlap

Each release of this repository is archived on Zenodo, which provides a citable DOI.

## Citation

If you use this script, please cite the archived version:

> [Lassandro, M.] (2026). *particle_overlap* (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23456823

and the associated paper (see above).

## License

Released under the GNU Affero General Public License v3.0 (see `LICENSE`).

## Contact

Please open an issue on the GitHub repository, or contact [michelangelo.lassandro@gmail.com, [ORCID: 0009-0006-7265-0602](https://orcid.org/0009-0006-7265-0602)].
