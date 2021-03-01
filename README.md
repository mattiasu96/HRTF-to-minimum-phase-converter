# HRTF-to-minimum-phase-converter

This repository contains a simple script that converts standard HRTF into minimum-phase ones using the Hilbert transform. The formula is the following:

![Model diagram](https://chart.googleapis.com/chart?cht=tx&chl=%5CIm%20%5BHilbert(-ln(%7CH%7C))%5D)

Which is used to extract the minimum-phase from the phase of the original HRTF, then the HRTF is computed by multiplying the original magnitude of the HRTF with the new phase.

Minimum-phase decomposition of HRTF has been proved to be one of the main approach to perform HRTF interpolation, as mentioned in https://www.researchgate.net/publication/236169325_Creating_Interactive_Virtual_Acoustic_Environments .

The script reads as input a HRTF dataset in SOFA format and returns a SOFA file containing the same identical data of the original HRTF dataset, but in minimum-phase.

This is an example of the original phase vs the minimum-phase extracted via Hilbert: 

![Phase comparison](https://i.stack.imgur.com/1mVY9.png)

And this is the comparison of the original impulse response vs the minimum phase one: 
![impulse response comparison](https://i.stack.imgur.com/W6hF1.png)

## Notes

1. I am not totally sure about the results. I have been using this to interpolate HRTF and it seems to work fine. They are based on theoretical formulas and papers, which (unfortunately) do not report any code or data that allows to reproduce the results and compare the implementations. 
2. For some dataset (the KEMAR MIT for example) the logarithm inside the formula returns an error due to zero value passed. If this happens, just add a negligible value to the resulting FFT (you can find more here: https://dsp.stackexchange.com/questions/25031/encounter-0-when-calculating-log-power-spectrum) 
