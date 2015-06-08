import os.path
import time
import pandas
import numpy as np
from pandas import DataFrame

col_cluster = ['Data', 'Algoritmo', 'Base de dados', 'Distância', 'Variável',
               'Nº registros', 'Nº grupos', 't (segundos)', 'Menor grupo',
               'Maior grupo', 'Variância', 'Dunn', 'Silhueta',
               'Classificações', 'RMSE', 'Taxa de sobreposição']

index, datetime, t, qtd_itens, rmse, overlap,
                         r_max, path

col_cat = ['Índice', 'Data', 't (segundos)', 'Qtd. itens',
           'RMSE', 'Taxa de sobreposição', 'r. max']
col_localCat = ['Índice', 'Theta', 'Est. Theta', 'Id. itens', 'r. max']


def loadClusterResults(path):
    """Loads the csv file containing the clustering results in a
       :func: pandas.DataFrame. If the file does not exist, creates an empty
       file with the column headers
    """
    if not os.path.exists(path):
        df = pandas.DataFrame([col_cluster])
    else:
        df = pandas.read_csv(path, header=0, index_col=False,
                             encoding='utf-8')

    df['Data'] = pandas.to_datetime(df['Data'])

    df[['t (segundos)', 'Dunn', 'Silhueta', 'Nº registros', 'Nº grupos',
        'Menor grupo', 'Maior grupo', 'RMSE', 'Taxa de sobreposição']] = df[
        ['t (segundos)', 'Dunn', 'Silhueta', 'Nº registros', 'Nº grupos',
         'Menor grupo', 'Maior grupo', 'RMSE',
         'Taxa de sobreposição']].astype(np.float64)

    df[['Base de dados', 'Distância']] = df[
        ['Base de dados', 'Distância']].astype(str)

    df['Sem Classificação'] = df['Classificações'].apply(lambda x:
                                                         x.count('-1'))
    df['Classificações'] = df[
        'Classificações'].apply(
        lambda x: np.array(x.strip().strip('[]').split(' '), dtype=np.int64))

    df['pct. sem Classificação'] = df[['Sem Classificação', 'Classificações'
                                       ]].apply(lambda x: 100 / np.size(x[1]) *
                                                x[0], axis=1)

    df['Classificações'] = df['Classificações'].astype(np.ndarray)
    return df


def saveClusterResults(datetime, algorithm, dataset, distance, variable,
                       n_observations, n_clusters, t, smallest_cluster,
                       largest_cluster, variance, dunn, sillhouette,
                       classifications, path):
    """Appends a result to the end of the cluster results csv file:
    """
    ar = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(datetime)),
          algorithm,
          dataset,
          distance,
          variable,
          n_observations,
          n_clusters,
          t,
          smallest_cluster,
          largest_cluster,
          variance,
          dunn,
          sillhouette,
          str(classifications.tolist()).strip('[]').replace(',', ''),
          None,
          None]

    if not os.path.exists(path):
        DataFrame([ar], columns=col_cluster).to_csv(
            path, header=True, index=False)
    with open(path, 'a') as f:
        DataFrame([ar]).to_csv(f, header=False, index=False)


def process(datadir, imgdir):
    df = loadClusterResults()

    df.groupby('Algoritmo')['Menor grupo', 'Maior grupo', 't (segundos)',
                            'Variância', 'Dunn', 'Silhueta'].mean().to_csv(
                                datadir + 'alg_means.csv')
    df.groupby('Base de dados')['Menor grupo', 'Maior grupo', 't (segundos)',
                                'Variância', 'Dunn', 'Silhueta'].mean().to_csv(
        datadir + 'dataset_means.csv')
    df.groupby('Nº grupos')['Menor grupo', 'Maior grupo', 't (segundos)',
                            'Variância', 'Dunn', 'Silhueta'].mean().to_csv(
                                datadir + 'nclusters_means.csv')

    ax = df.groupby(
        'Nº grupos')['Variância', 'Dunn', 'Silhueta'].mean().plot(
            title='Índices de validação de clusters / N. grupos',
            legend='best',
            figsize=(8, 6))
    ax.set_ylabel('Índices')
    ax.get_figure().savefig(imgdir + 'validity_by_nclusters.pdf')

    df_enem = df[df['Base de dados'] == 'Enem'][
        df['Algoritmo'] !=
        'Aff. Propagation'][df['Algoritmo']
                            != 'DBSCAN']
    df_sintetico = df[df['Base de dados'] ==
                      'Sintético'][df['Algoritmo'] !=
                                   'Aff. Propagation'][df['Algoritmo'] !=
                                                       'DBSCAN']

    ax = pandas.pivot_table(
        df_enem,
        values='Dunn',
        columns='Algoritmo',
        index='Nº grupos').plot(
            figsize=(8, 6),
            grid=True,
            title='Média Dunn / Algoritmo na base \'Enem\'')
    ax.set_ylabel('Dunn')
    ax.get_figure().savefig(imgdir + 'dunn_by_algorithm_enem.pdf')

    ax = pandas.pivot_table(
        df_enem,
        values='Silhueta',
        columns='Algoritmo',
        index='Nº grupos').plot(
            figsize=(8, 6),
            grid=True,
            title='Média silhueta / Algoritmo na base \'Enem\'')
    ax.set_ylabel('Silhueta')
    ax.get_figure().savefig(
        imgdir + 'silhouette_by_algorithm_enem.pdf')

    ax = pandas.pivot_table(
        df_enem,
        values='Menor grupo',
        columns='Algoritmo',
        index='Nº grupos').plot(
            figsize=(8, 6),
            grid=True,
            title='Itens no menor cluster / Algoritmo na base \'Enem\'')
    ax.set_ylabel('Itens no menor cluster')
    ax.get_figure().savefig(
        imgdir + 'smallestcluster_by_algorithm_enem.pdf')

    ax = pandas.pivot_table(df_sintetico, values='Dunn',
                            columns='Algoritmo', index='Nº grupos').plot(
        figsize=(8, 6),
        grid=True,
        title='Média Dunn /' +
        ' Algoritmo na base \'Sintética\'')
    ax.set_ylabel('Dunn')
    ax.get_figure().savefig(imgdir +
                            'dunn_by_algorithm_sintetico.pdf')

    ax = pandas.pivot_table(df_sintetico, values='Silhueta',
                            columns='Algoritmo', index='Nº grupos').plot(
        figsize=(8, 6), grid=True, title='Média silhueta' +
        '/ Algoritmo na base \'Sintética\'')
    ax.set_ylabel('Silhueta')
    ax.get_figure().savefig(
        imgdir + 'silhouette_by_algorithm_sintetico.pdf')

    ax = pandas.pivot_table(df_sintetico, values='Menor grupo',
                            columns='Algoritmo', index='Nº grupos').plot(
        figsize=(8, 6), grid=True, title='Itens no menor' +
        'cluster / Algoritmo na base \'Sintética\'')
    ax.set_ylabel('Itens no menor cluster')
    ax.get_figure().savefig(
        imgdir + 'smallestcluster_by_algorithm_sintetico.pdf')

    dfdb = df[df['Algoritmo'] == 'DBSCAN']
    dfdb = dfdb.rename(columns={'Variável': '$\epsilon$'})

    ax = pandas.pivot_table(dfdb,
                            values='Dunn',
                            columns='Base de dados',
                            index='$\epsilon$').plot(
                                figsize=(8, 6),
                                grid=True,
                                title='Média Dunn / $\epsilon$ para DBSCAN')
    ax.set_ylabel('Dunn')
    ax.get_figure().savefig(imgdir + 'dunn_by_dbscan.pdf')

    ax = pandas.pivot_table(
        dfdb,
        values='Silhueta',
        columns='Base de dados',
        index='$\epsilon$').plot(
            figsize=(8, 6),
            grid=True,
            title='Média silhueta / $\epsilon$ para DBSCAN')
    ax.set_ylabel('Silhueta')
    ax.get_figure().savefig(imgdir + 'silhouette_by_dbscan.pdf')

    ax = pandas.pivot_table(
        dfdb,
        values='Menor grupo',
        columns='Base de dados',
        index='$\epsilon$').plot(
            figsize=(8, 6),
            grid=True,
            title='Itens no menor cluster / $\epsilon$ para DBSCAN')
    ax.set_ylabel('Itens no menor cluster')
    ax.get_figure().savefig(
        imgdir + 'smallestcluster_by_dbscan.pdf')

    ax = pandas.pivot_table(
        dfdb,
        values='pct. sem Classificação',
        columns='Base de dados',
        index='$\epsilon$').plot(
            figsize=(8, 6),
            grid=True,
            title='% de itens não classificados / $\epsilon$ para DBSCAN')
    ax.set_ylabel('% Itens')
    ax.get_figure().savefig(imgdir + 'unclassified_by_dbscan.pdf')

    ax = pandas.pivot_table(
        dfdb,
        values='Nº grupos',
        columns='Base de dados',
        index='$\epsilon$').plot(
            figsize=(8, 6),
            grid=True,
            title='Nº de clusters / $\epsilon$ para DBSCAN')
    ax.set_ylabel('Nº grupos')
    ax.get_figure().savefig(imgdir + 'nclusters_by_dbscan.pdf')


def loadGlobalCATResults(path):
    """Loads the csv file containing the computerized adaptive testing
       simulation results in a pandas.DataFrame. If the file does not exist,
       creates an empty file with the column headers.
    """
    if not os.path.exists(path):
        df = pandas.DataFrame([col_cat])
    else:
        df = pandas.read_csv(path, header=0, index_col=False,
                             encoding='utf-8')

    df[['Theta', 'Qtd. itens', 'r_max']] = df[
        ['Theta', 'Qtd. itens', 'r_max']].astype(float)

    df['Id. itens'] = df['Id. itens'].apply(lambda x:
                                            np.array(x.strip().split(' '),
                                                     dtype='int'))

    df['Est. thetas'] = df['Est. thetas'].apply(lambda x:
                                                np.array(x.strip().split(' '),
                                                         dtype='int'))

    return df


def saveGlobalCATResults(index, datetime, t, qtd_itens, rmse, overlap,
                         r_max, path):
    """Appends a result to the end of the cluster results csv file:"""
    ar = [index,
          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(datetime)),
          t,
          qtd_itens,
          rmse,
          overlap,
          r_max]

    if not os.path.exists(path):
        DataFrame([ar], columns=col_cat).to_csv(
            path, header=True, index=False)
    with open(path, 'a') as f:
        DataFrame([ar]).to_csv(f, header=False, index=False)


def saveLocalCATResults(index, theta, est_theta, id_itens, r_max, path):
    ar = [index,
          theta,
          est_theta,
          str(id_itens).strip('[]').replace(',', ''),
          r_max]

    if not os.path.exists(path):
        DataFrame([ar], columns=col_localCat).to_csv(
            path, header=True, index=False)
    with open(path, 'a') as f:
        DataFrame([ar]).to_csv(f, header=False, index=False)
