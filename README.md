# star-ID-graph-match
Source Code of "An Accurate Star Identification Approach Based on Spectral Graph Matching for Attitude Measurement of Spacecraft"

```
@article{you2022accurate,
  title={An accurate star identification approach based on spectral graph matching for attitude measurement of spacecraft},
  author={You, Zhiyuan and Li, Junzheng and Zhang, Hongcheng and Yang, Bo and Le, Xinyi},
  journal={Complex & Intelligent Systems},
  volume={8},
  number={2},
  pages={1639--1652},
  year={2022}
}
```

## Qucik Start

- Convert SAO star catalog to txt format 

  `sh scripts/convert.sh`

- Simulate to generate star images

  `sh scripts/simulate.sh`
  
- Generate database

  `sh scripts/gen_database.sh`

- Search to identifify star with noise

  `sh scripts/search.sh #STD_POSITION_NOISE #NUM_LOST_STAR #NUM_FALSE_STAR`
  
  *i.e.*, `sh scripts/search.sh 3.0 1 0` means the std of positon noise is 3.0, lost star number is 1, and false star number is 0.
