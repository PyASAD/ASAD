from asad import pyasad
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    model = pyasad.Model(
        path='data/models/bc2003_hr_m52_salp_ssp.ised_ASCII',
        format='GALAXEV'
    )

    fig = plt.figure(figsize=(10,11))

    for i, a in enumerate(model.age):
        x, y = model.flux[i][0], model.flux[i][-1]
        if a >= 6.5 and a <= 7.5 and x >= 0.015 and y <= 0.005:
            plt.plot(model.wavelength,
                model.flux[i],
                label=str(a),
                linewidth=0.3
            )

    plt.title('Flux vs Wavelength')
    plt.xlabel("Wavelength (Angstroms)")
    plt.ylabel("Flux")
    plt.legend(loc='upper right', shadow=False, prop={'size':8})
    plt.savefig(
        'test3.pdf',
        format='pdf',
        bbox_inches='tight',
        dpi=1400
    )

