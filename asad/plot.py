import os.path, re, sys
from itertools import cycle

import numpy              as np
import matplotlib         as mpl
mpl.use('Agg')

import matplotlib.cm      as cm
import matplotlib.pyplot  as plt
import matplotlib.markers as markers

import random

def random_number():
    random_number = random.randint(1,99999)
    sid = str(random_number)
    return sid

options = {
    'xtick.labelsize'         : 28,
    'ytick.labelsize'         : 28,
    'xtick.major.size'        : 20,
    'xtick.major.width'       : 1,
    'xtick.minor.size'        : 10,
    'xtick.minor.width'       : 0.5,
    'ytick.major.size'        : 20,
    'ytick.major.width'       : 1,
    'ytick.minor.size'        : 10,
    'ytick.minor.width'       : 0.5,
    'figure.max_open_warning' : 100
}

font = {
    'fontname' : 'Sans',
    'fontsize' : 36
}

small_font = {
    'fontname' : 'Sans',
    'fontsize' : 28
}


def model_name_format(model_name):
    m = re.search('\.z(\d{3})', model_name)
    if not m:
        return model_name
    else:
        return 'z=0.%s' % m.group(1)

def observation_name_format(observation_name):
    return os.path.splitext(observation_name)[0]

def title_format(obj1, obj2=None):
    model_name = model_name_format(obj1.model.original_name)
    observation_name = observation_name_format(obj1.observation.original_name)
    if obj2:
        model_name1 = model_name_format(obj2.model.original_name)
        return '[ {} with {} & {}]'.format(observation_name, model_name,model_name1)
    else:
        return '[ {} with {}]'.format(observation_name, model_name)

def surface(obj, levels=15, outdir="",
            fname='',
            format='eps',
            labels=False,
            save=False,
            show=False,
            title=None,
            *args, **kwargs):


    mpl.rcParams = dict(mpl.rcParams, **options)
    NL = levels
    x  = obj.model.age
    y  = obj.observation.reddening
    z  = 1.0 / np.array(obj.stat)

    fig = plt.figure(figsize=(16,10))
    border_width = 0.10
    border_height = 0.09
    ax_size = [0.10, 0.15, 0.90, 0.75]
    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y, z, NL, colors=['k'], linewidths=0.10, zorder=2)
    if labels: plt.clabel(C, inline=1, linewidths=0.10, **small_font)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet, zorder=1)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
    cb = fig.colorbar(CF)
    cb.ax.tick_params(labelsize=26)
    cb.set_label("Test Statistic", size=32)
    plt.scatter([obj.min_age], [obj.min_reddening], c='w', s=350, marker="*", zorder=3)

    plt.xlim(xmin=obj.model.age[0], xmax=obj.model.age[-1])
    plt.ylim([obj.observation.reddening[0], obj.observation.reddening[-1]])

    if title:
      plt.title(title, **font)
    else:
      plt.title(title_format(obj), **font)

    plt.xlabel("log(Age/Year)", **font)
    plt.ylabel("E (B-V)", **font)

    plt.tick_params(labelsize=26)
    plt.minorticks_on()
    plt.grid(which='both')

    file_name = fname or ("surface_" + obj.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format,
            bbox_inches=0
        )

    if show:
        plt.show()
    plt.close()

def surface_subplot(obj, levels=15,
            labels=False,
            title=None,
            *args, **kwargs):
#    mpl.rcParams = dict(mpl.rcParams, **options)
    NL = levels
    x  = obj.model.age
    y  = obj.observation.reddening
    z  = 1.0 / np.array(obj.stat)

#    fig = plt.figure()
#    border_width = 0.10
#    border_height = 0.07
#    ax_size = [0+border_width, 0+border_height,
#               1-0.5*border_width, 1-2*border_height]
#    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y, z, NL, colors=['k'], linewidths=0.10)
    if labels: plt.clabel(C, inline=1, linewidths=0.10, **small_font)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
#    cb = fig.colorbar(CF)
#    cb.set_label("Test Statistic")
    plt.scatter([obj.min_age], [obj.min_reddening], c='w', s=350, marker="*")
    plt.xlim([obj.model.age[0], obj.model.age[-1]])
    plt.ylim([obj.observation.reddening[0], obj.observation.reddening[-1]])

    if title:
        plt.title(title, **small_font)
    else:
        plt.title(title_format(obj), **small_font)

    plt.xlabel("log(Age/Year)", **small_font)
    plt.ylabel("E (B-V)", **small_font)
    plt.minorticks_on()
    plt.grid(which='both')

def scatter(obj, ages=[], reddenings=[], outdir='',
            fname='',
            format='eps',
            title=None,
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            close=True,
            *args, **kwargs):
    model_linestyles = cycle(['--', ':', '-.', '-'])
    obsv_linestyles = cycle(['-',':','-.',':'])
    model = obj.model
    obsv = obj.observation

    def find_indices(values, target):
        return np.searchsorted(values, target)

    model_index = find_indices(model.age, ages)
    if len(model_index) == 0: model_index = [obj.min_model]
    obsv_index = find_indices(obsv.reddening, reddenings)
    if len(obsv_index) == 0: obsv_index = [obj.min_observation]

    for mi in model_index:
        model_label = 'Model: age=%s' % (model.age[mi])
        plt.plot(model.wavelength, model.flux[mi],
                 label=model_label, linewidth=1.0,
                 linestyle=next(model_linestyles))

    for oi in obsv_index:
        obsv_label = 'Observation: reddening=%s' % (obsv.reddening[oi])
        plt.plot(obsv.wavelength, obsv.flux[oi],
                 label=obsv_label, linewidth=0.5,
                 linestyle=next(obsv_linestyles))

    plt.tick_params(axis='both', which='major', labelsize=16)

    if title:
        plt.title(title, size=20)
    else:
        plt.title('Flux vs Wavelength\n' + title_format(obj), size=20)

    plt.xlabel("Wavelength (Angstroms)", fontsize=18)
    plt.ylabel("Normalized Flux", fontsize=18)
    plt.legend(loc='upper right', shadow=False, prop={'size':14})

    file_name = fname or ("best_spectra_match_" + obj.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    if close:
        plt.close()

def scatter_subplot(obj, ages=[], reddenings=[],
            original_ages={},
            outdir='',
            fname='',
            format='eps',
            title=None,
            xlabel='',
            ylabel='',
            *args, **kwargs):
    model = obj.model
    obsv = obj.observation
    obsv_name = obj.observation.original_name

    def find_indices(values, target):
        return np.searchsorted(values, target)

    model_index = find_indices(model.age, ages) - 1
    if len(model_index) == 0: model_index = [obj.min_model]
    obsv_index = find_indices(obsv.reddening, reddenings)
    if len(obsv_index) == 0: obsv_index = [obj.min_observation]

    for mi in model_index:
        model_label = 'Model: age=%s' % (model.age[mi])
        plt.plot(model.wavelength, model.flux[mi],
                 label=model_label, linewidth=0.13,
                 linestyle='solid', color='b')

    for oi in obsv_index:
        if obsv_name in original_ages:
            obsv_label = 'Observation: age=%s' % original_ages[obsv_name]
        else:
            obsv_label = 'Observation'
        plt.plot(obsv.wavelength, obsv.flux[oi],
                 label=obsv_label, linewidth=0.8, linestyle='solid', color='g')

    plt.tick_params(axis='both', which='major', labelsize=20)

    if title:
        plt.title(title)
    else:
        plt.title('[{}]'.format(obsv_name))

    plt.xlabel(u"Wavelength (Angstroms)")
    plt.ylabel("Normalized Flux")
    plt.legend(loc='upper right', shadow=False, prop={'size':7})


def residual_match(obj1,obj2, outdir='',          #Edit this function for Plotting
            fname='',
            observationKey='Default',
            modelKey1='Default',
            modelKey2='Default',
            format='eps',
            title=None,
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    mpl.rcParams = dict(mpl.rcParams, **options)
    model1 = obj1.model
    model2 = obj2.model
    obsv1 = obj1.observation
    obsv2 = obj2.observation
    flux1 = model1.flux[obj1.min_model] - obsv1.flux[obj1.min_observation]
    flux2 = model2.flux[obj2.min_model] - obsv2.flux[obj2.min_observation]

    ##Labelling
    if observationKey != 'Default':
        observation_title = observationKey
    else:
        observation_title = observation_name_format(obsv1.original_name)

    if modelKey1 != 'Default':
        model1_title = modelKey1
    else:
        model1_title = model_name_format(model1.original_name)
    if modelKey2 != 'Default':
        model2_title = modelKey2
    else:
        model2_title = model_name_format(model2.original_name)

    residual1_title = "Residual Flux for " + model1_title
    residual2_title = "Residual Flux for " + model2_title
    ##

    fig = plt.figure(figsize=(8, 6))
    gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharex=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.minorticks_on()

    if title:
        ax1.set_title(title)
    else:
        ax1.set_title('Normalized Flux vs Wavelength\n' + title_format(obj1,obj2))

    ax1.plot(model1.wavelength, model1.flux[obj1.min_model],color='r', label=model1_title, linewidth=0.6)
    ax1.plot(model2.wavelength, model2.flux[obj2.min_model],color='b', label=model2_title, linewidth=0.6)
    ax1.plot(obsv1.wavelength, obsv1.flux[obj1.min_observation],color='k', label=observation_title, linewidth=0.9)
    ax1.set_ylabel('Normalized Flux', fontsize=18)
    ax1.legend(loc='best', shadow=False, prop={'size':10})

    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xlim(obsv1.wavelength[0], obsv1.wavelength[-1])
    ax2.plot(obsv1.wavelength, flux1, color='r', label=residual1_title, linewidth=0.7)
    ax2.plot(obsv1.wavelength, flux2, color='b', label=residual2_title, linewidth=0.7)
    ax2.set_ylabel('Residual', fontsize=18)
    ax2.set_xlabel("Wavelength (Angstroms)", fontsize=18)
    ax2.legend(loc='best', shadow=False, prop={'size':10})

    plt.tight_layout()
    file_name = fname or ("residual_match_" + obj1.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    plt.close()


def residual_match_one_model(obj, outdir='',          #Edit this function for Plotting
            fname='',
            observationKey='Default',
            modelKey='Default',
            format='eps',
            title=None,
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    mpl.rcParams = dict(mpl.rcParams, **options)
    model = obj.model
    obsv = obj.observation
    flux = model.flux[obj.min_model] - obsv.flux[obj.min_observation]

    ##Labelling

    if observationKey != 'Default':
        observation_title = observationKey
    else:
        observation_title = observation_name_format(obsv.original_name)

    if modelKey != 'Default':
        model_title = modelKey
    else:
        model_title = model_name_format(model.original_name)

    residual_title = "Residual Flux for " + model_title

    ##

    fig = plt.figure(figsize=(8, 6))
    gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharex=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.minorticks_on()

    if title:
        ax1.set_title(title)
    else:
        ax1.set_title('Normalized Flux vs Wavelength\n' + title_format(obj))

    ax1.plot(model.wavelength, model.flux[obj.min_model], label=model_title, linewidth=0.6)
    ax1.plot(obsv.wavelength, obsv.flux[obj.min_observation], label=observation_title, linewidth=0.9)
    ax1.set_ylabel('Normalized Flux', fontsize=18)
    ax1.legend(loc='best', shadow=False, prop={'size':10})

    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xlim(obsv.wavelength[0], obsv.wavelength[-1])
    ax2.plot(obsv.wavelength, flux, color='r', label=residual_title, linewidth=0.7)
    ax2.set_ylabel('Residual', fontsize=18)
    ax2.set_xlabel("Wavelength (Angstroms)", fontsize=18)
    ax2.legend(loc='best', shadow=False, prop={'size':10})

    plt.tight_layout()
    file_name = fname or ("residual_match_" + obj.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    plt.close()

def residual(obj, outdir='',
            fname='',
            format='eps',
            title=None,
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    model = obj.model
    obsv = obj.observation
    flux = model.flux[obj.min_model] - obsv.flux[obj.min_observation]
    f, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True, sharey=True)

    ax1.plot(model.wavelength, model.flux[obj.min_model],
             label="Model Flux", linewidth=0.5)

    if title:
        ax1.set_title(title)
    else:
        ax1.set_title('Normalized Flux vs Wavelength\n' + title_format(obj))
    ax1.tick_params(which='major', labelsize=8)
    ax1.legend(loc='upper right', shadow=False, prop={'size':7})

    ax2.plot(obsv.wavelength, obsv.flux[obj.min_observation],
             label="Observation Flux", linewidth=0.5)
    ax2.set_ylabel("Normalized Flux")
    ax2.legend(loc='upper right', shadow=False, prop={'size':7})
    ax2.tick_params(which='major', labelsize=8)

    ax3.plot(model.wavelength, model.flux[obj.min_model], linewidth=0.5)
    ax3.plot(obsv.wavelength, obsv.flux[obj.min_observation], linewidth=0.5)
    ax3.tick_params(which='major', labelsize=8)

    ax4.axhline(0, color='black', linewidth=1)
    ax4.set_xlim(obsv.wavelength[0], obsv.wavelength[-1])
    ax4.plot(obsv.wavelength, flux, label="Residual Flux", linewidth=0.5)
    ax4.set_xlabel("Wavelength (Angstroms)")

    ax4.legend(loc='upper right', shadow=False, prop={'size':7})
    ax4.tick_params(axis='y', which='major', labelsize=8)

    file_name = fname or ("residual_" + obj.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format
        )

    if show:
        plt.show()
    plt.close()

def surface_error(obj, levels=15, outdir='',
            fname='',
            format='eps',
            labels=False,
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    mpl.rcParams = dict(mpl.rcParams, **options)
    NL = levels
    x  = obj.model.age
    y  = obj.observation.reddening
    z  = 1.0 / np.array(obj.stat)

    fig = plt.figure(figsize=(16,10))
    border_width = 0.10
    border_height = 0.07
    ax_size = [0+border_width, 0+border_height,
               1-0.5*border_width, 1-2*border_height]
    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y, z, NL, colors=['k'], linewidths=0.10)
    if labels: plt.clabel(C, inline=1, linewidths=0.10, **small_font)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
    cb = fig.colorbar(CF)
    cb.set_label("Inverse Chi-Squared Statistic")
    plt.scatter([obj.min_age], [obj.min_reddening], c='w', s=350, marker="*")
    for error_age, error_reddening, error_stat in zip(obj.error_age, obj.error_reddening, obj.error_stat):
        plt.plot([error_age], [error_reddening], 'ro')

    plt.xlim([obj.model.age[0], obj.model.age[-1]])
    plt.ylim([obj.observation.reddening[0], obj.observation.reddening[-1]])

    plt.title(title_format(obj), **font)
    plt.xlabel("log(Age/Year)", **font)
    plt.ylabel("E (B-V)", **font)

    plt.minorticks_on()
    plt.grid(which='both')

    file_name = fname or ("surface_error_" + obj.name)
    file_name = file_name + '_' + random_number()
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            bbox_inches=0
        )

    if show:
        plt.show()
    plt.close()

def tile_plot(tile_subplot, objs, nrows, ncols, outdir='',
            fname='',
            format='eps',
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    fig, axes = plt.subplots(nrows, ncols, figsize=(11.312,16))
    fig.tight_layout()
    obj_index = 1
    for i in range(1, nrows+1):
        for j in range(1, ncols+1):
            plt.subplot(nrows, ncols, obj_index)
            if obj_index <= len(objs):
                tile_subplot(objs[obj_index-1])
            else:
                plt.plot()
                plt.axis("off")
            obj_index += 1

    plt.subplots_adjust(hspace = 0.32, wspace=0.3)
    file_name = fname or 'surface_tile'
    file_name = file_name + '_' + random_number()

    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format,
            bbox_inches='tight',
            orientation='portrait',
            papertype='a4',
            dpi=800
        )
    plt.close()

def surface_tile(*args, **kwargs):
    tile_plot(surface_subplot, *args, **kwargs)

"""
def scatter_tile(objs, nrows, ncols, original_ages=None, outdir='',
            fname='',
            format='eps',
            title='',
            xlabel='',
            ylabel='',
            save=False,
            show=False,
            *args, **kwargs):
    fig, axes = plt.subplots(nrows, ncols, figsize=(11.312,16))
    fig.tight_layout()
    obj_index = 1
    for i in range(1, nrows+1):
        for j in range(1, ncols+1):
            if obj_index > len(objs):
                return
            plt.subplot(nrows, ncols, obj_index)
            scatter_subplot(objs[obj_index-1], original_ages=original_ages,
                            close=False)
            obj_index += 1

    plt.subplots_adjust(hspace = 0.32, wspace=0.3)
    file_name = fname or 'scatter_tile'
    if save:
        plt.savefig(
            os.path.abspath(os.path.join(outdir, file_name)) + "." + format,
            format=format,
            bbox_inches='tight',
            orientation='portrait',
            papertype='a4',
            dpi=800
        )
"""
