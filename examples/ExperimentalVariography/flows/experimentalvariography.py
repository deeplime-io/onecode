
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('experimentalvariography.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, ask for help at https://github.com/deeplime-io/onecode/issues

import ast
import logging
import os

NO_GEOLIME = False
try:
    import geolime as geo
except:
    NO_GEOLIME = True

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
from pyproj import CRS

from onecode import (
    Logger,
    Project,
    csv_reader,
    dropdown,
    image_output,
    plotly_output,
    slider,
    text_input,
    text_output
)

plt.rcParams["figure.figsize"] = [12, 6]


def fit_varios(dh, vario_params, grade, orebody_name):
    varios = []
    for v in vario_params:
        lags, tol = geo.generate_lags(lag=v['lag'], plag=v['plag'], nlags=v['lag_dist']//v['lag'])

        varios.append(
            geo.variogram(
                object=dh,
                attribute=f'cut_{grade}',
                region=orebody_name,
                geographic_azimuth=v['azi'],
                dip=v['dip'],
                pitch=v['pitch'],
                lags=lags,
                tol=tol,
                atol=v['atol'],
                slice_width=None,
                slice_height=None,
                weights_attribute=None
            )
        )

    dip = vario_params[0]['dip']
    geo.vario_contour(
        dh,
        attribute=f'cut_{grade}',
        region=orebody_name,
        lags=lags,
        tol=tol,
        n_az=6,
        atol=45,
        dip=dip,
        pitch=90,
        save_file=image_output(f"variomap_{dip}", f"images/variomap_{dip}.jpg")
    )

    min_dip = dip - 20 if dip > 20 else 0
    max_dip = dip + 20 if dip < 70 else 90
    cov = geo.Nugget() + geo.Spherical()
    geo.model_fit(
        varios,
        cov,
        constraints=[
            {},
            {"angle_fixed_0": 0, "angle_fixed_2": 90, "angle_min_1": min_dip, "angle_max_1": max_dip}
        ]
    )

    fig = geo.plot_semivariogram(
        variograms=varios,
        model=cov,
        model_angles=vario_params,
        display_npairs=False
    )
    fig.write_image(image_output(f"vario_dip_{dip}", f"images/vario_dip_{dip}.jpg"))
    plotly.io.write_json(fig, plotly_output(f"vario_dip_{dip}_plot", f"plots/vario_dip_{dip}.json"))

    return cov


def run():
    if NO_GEOLIME:
        Logger.info('GeoLime is not available')
        Logger.info('Input parameters are therefore ignored and displayed results are not related to your input dataset')
        Logger.info('For GeoLime licensing information, contact us at: contact+geolime@deeplime.io')

        for dip in [40, 70, 90]:
            image_output(f"variomap_{dip}", f"images/variomap_{dip}.jpg")
            image_output(f"vario_dip_{dip}", f"images/vario_dip_{dip}.jpg")
            plotly_output(f"vario_dip_{dip}_plot", f"plots/vario_dip_{dip}.json")
            text_output('vario', f'cov_model_dip_{dip}.txt')

        grade = 'Au'
        image_output(f'histrogram_{grade}', f'images/histrogram_{grade}.jpg')
        image_output('variomap', "images/vertical_variomap.jpg")

    else:
        Logger.info('Setting project configuration...')
        geo.Project().set_crs(CRS(text_input('epsg', 'EPSG:32108')))
        os.makedirs(os.path.join(Project().data_root, 'outputs', 'images'), exist_ok=True)
        os.makedirs(os.path.join(Project().data_root, 'outputs', 'plots'), exist_ok=True)

        Logger.info('Loading collars...')
        collars = csv_reader('collars', 'collars.csv')
        x_col = dropdown('x_col', 'collarX', options="$collars$.columns")
        y_col = dropdown('y_col', 'collarY', options="$collars$.columns")
        z_col = dropdown('z_col', 'collarZ', options="$collars$.columns")
        borehole_id = dropdown('borehole_id', 'boreholeName', options="$collars$.columns")
        collar_cols_to_drop = dropdown(
            'collars_cols_to_drop',
            ['boreholeIterationId'],
            options="$collars$.columns",
            multiple=True
        )
        geo.Project().set_attribute_mapping(geo.Attribute.X_COLLAR, x_col)
        geo.Project().set_attribute_mapping(geo.Attribute.Y_COLLAR, y_col)
        geo.Project().set_attribute_mapping(geo.Attribute.Z_COLLAR, z_col)
        geo.Project().set_attribute_mapping(geo.Attribute.HOLEID, borehole_id)
        collars = collars.drop(columns=collar_cols_to_drop)

        Logger.info('Loading assays...')
        assays = csv_reader('assays', 'Au_assay.csv')
        depth_from = dropdown('depth_from', 'depthFrom', options="$assays$.columns")
        depth_to = dropdown('depth_to', 'depthTo', options="$assays$.columns")
        grade = dropdown('grade', 'Au', options="$assays$.columns")
        assay_cols_to_drop = dropdown(
            'assay_cols_to_drop',
            ['boreholeIterationId'],
            options="$assays$.columns",
            multiple=True
        )
        geo.Project().set_attribute_mapping(geo.Attribute.FROM, depth_from)
        geo.Project().set_attribute_mapping(geo.Attribute.TO, depth_to)
        assays = assays.drop(columns=assay_cols_to_drop)

        Logger.info('Loading surveys...')
        survey = csv_reader('survey', 'surveys.csv')
        depth = dropdown('depth', 'depth', options="$survey$.columns")
        azimuth = dropdown('azimuth', 'azimuth', options="$survey$.columns")
        dip = dropdown('dip', 'dip', options="$survey$.columns")
        survey_cols_to_drop = dropdown(
            'survey_cols_to_drop',
            ['boreholeIterationId'],
            options="$survey$.columns",
            multiple=True
        )
        geo.Project().set_attribute_mapping(geo.Attribute.DEPTH_SURVEY, depth)
        geo.Project().set_attribute_mapping(geo.Attribute.AZIMUTH, azimuth)
        geo.Project().set_attribute_mapping(geo.Attribute.DIP, dip)
        survey = survey.drop(columns=survey_cols_to_drop)

        orebody = csv_reader('orebody', 'categ.csv', optional=True)
        orebody_name = text_input('orebody_name', 'ORE_BODY', optional='$orebody$ is None')
        orebody_cols_to_drop = dropdown(
            'orebody_cols_to_drop',
            ['boreholeIterationId'],
            optional='$orebody$ is None',
            options="$orebody$.columns",
            multiple=True
        )
        if orebody is not None:
            Logger.info('Loading geology...')
            orebody = orebody.drop(columns=orebody_cols_to_drop)
            orebody = orebody.astype({depth_from: float, depth_to: float})

        Logger.info('Standardizing data...')
        survey = survey[[borehole_id, depth, dip, azimuth]]
        grade_list = list(assays.columns)
        grade_list.remove(borehole_id)
        grade_list.remove(depth_from)
        grade_list.remove(depth_to)
        assays = assays.replace('undefined', np.nan)
        assays = assays.dropna()

        # Fill assay with collar and geology information
        if orebody is not None:
            Logger.info(f'Calculating {orebody_name} domain...')
            assays = pd.merge(assays, collars[[borehole_id]])
            if orebody is not None:
                assays = pd.merge(assays, orebody, on=[borehole_id, depth_from, depth_to], how='outer')

            assays['below'] = assays['intersect'].fillna(method='ffill')
            assays['above'] = assays['intersect'].fillna(method='bfill')
            assays['between'] = 0
            assays.loc[(assays['above'] == orebody_name) & (assays['below'] == orebody_name), 'between'] = 1
        else:
            assays['between'] = 1

        assays = assays.dropna(subset=grade_list)

        Logger.info('Creating drillholes...')
        dh = geo.create_drillholes(
            'DH',
            collar=collars,
            assays=assays,
            survey=survey,
        )

        dh.set_property(grade, dh[grade].astype(float))
        dh.set_region_condition(orebody_name, 'between == 1', False)
        dh.set_region_condition('OUT', 'between != 1', False)

        Logger.info('Applying P99 and P1 cutoffs...')
        Ore = dh[grade]
        P99 = np.percentile(Ore, int(slider('low_cutoff', 99, min=90, max=99, step=1)))
        P01 = np.percentile(Ore, int(slider('high_cutoff', 1, min=1, max=10, step=1)))
        Ore[Ore > P99] = P99
        Ore[Ore < P01] = P01
        dh.set_property_expr(f'cut_{grade}', 0, False)
        dh.set_property_value(f'cut_{grade}', Ore)

        Logger.info('Plotting histogram...')
        plt.hist(dh.data(f'cut_{grade}', orebody_name), bins=40)
        plt.hist(dh.data(f'cut_{grade}', 'OUT'), bins=40)
        plt.legend(loc='upper right', labels=['ORE', 'OUT'])
        plt.title(f'Histogram {grade}')
        plt.savefig(image_output(f'histrogram_{grade}', f'images/histrogram_{grade}.jpg'), bbox_inches='tight')

        Logger.info(f"Calculating Experimental Variography on {grade}")

        covs = []
        dip_angles = dropdown('dip_angles', [40, 70, 90], options=[30, 40, 50, 60, 70, 80, 90, 100, 110], multiple=True)
        for dip in dip_angles:
            Logger.info(f"Calculating variograms and vario-contours for dip = {dip}")
            vario_params = [
                {"lag": 2.5, "lag_dist": 220, "plag": 50, "atol": 45, "azi": 0, "dip": dip, "pitch": 90 },
                {"lag": 4, "lag_dist": 150, "plag": 50, "atol": 90, "azi": 0, "dip": dip, "pitch": 0 },
                {"lag": 3, "lag_dist": 80, "plag": 50, "atol": 90, "azi": 180, "dip": 90 - dip, "pitch": 90 },
            ]

            c = fit_varios(dh, vario_params, grade, orebody_name)
            covs.append(c)

            with open(text_output('vario', f'cov_model_dip_{dip}.txt'), 'w') as f:
                f.write(f'Covariance Model for experimental variogram dip = {dip}\n')
                f.write('========================================================\n\n')
                f.write(str(c))

        lags, tol = geo.generate_lags(lag=1.5, plag=50, nlags=6)

        Logger.info(f"Calculating vertical variomap")
        fig = geo.vario_map(
            dh,
            attribute=f'cut_{grade}',
            region=orebody_name,
            lags=lags,
            tol=tol,
            n_az=18,
            atol=45,
            dip=90,
            pitch=0
        )

        fig.write_image(image_output('variomap', "images/vertical_variomap.jpg"))
