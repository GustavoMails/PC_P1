"""
Módulo de cálculo estadístico acelerado con Numba.
"""

from typing import Tuple
import numba
import numpy as np


@numba.njit
def category_stats(
    prices: np.ndarray, type_ids: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcula metricas estadisticas por categoria agrupando datos por su ID.
    """
    unique_types = np.unique(type_ids)
    n_cats = len(unique_types)

    # Arreglos para almacenar resultados finales
    counts = np.zeros(n_cats, dtype=np.int64)
    mins = np.full(n_cats, np.inf, dtype=np.float64)
    maxs = np.full(n_cats, -np.inf, dtype=np.float64)
    means = np.zeros(n_cats, dtype=np.float64)
    stds = np.zeros(n_cats, dtype=np.float64)

    # PASO 1: Agrupar datos por cada categoría
    for cat_idx in range(n_cats):
        cat_id = unique_types[cat_idx]
        
        # Filtramos manualmente los precios que pertenecen a esta categoría
        # (Esto es equivalente a un WHERE en SQL o filter en Python)
        cat_prices = prices[type_ids == cat_id]
        
        if len(cat_prices) > 0:
            counts[cat_idx] = len(cat_prices)
            mins[cat_idx] = np.min(cat_prices)
            maxs[cat_idx] = np.max(cat_prices)
            means[cat_idx] = np.mean(cat_prices)
            stds[cat_idx] = np.std(cat_prices)

    return unique_types, counts, mins, maxs, means, stds


@numba.njit
def price_zscores(prices: np.ndarray, type_ids: np.ndarray) -> np.ndarray:
    """
    Calcula el Z-score de cada producto relativo a su propia categoria.
    """
    unique_types, _, _, _, means, stds = category_stats(prices, type_ids)
    n = len(prices)
    z_scores = np.zeros(n, dtype=np.float64)

    # Calculamos el Z-score producto por producto
    for i in range(n):
        price = prices[i]
        cat_id = type_ids[i]

        # Buscamos la posición de la categoría para sacar su promedio y desviación
        for cat_idx in range(len(unique_types)):
            if unique_types[cat_idx] == cat_id:
                mean = means[cat_idx]
                std = stds[cat_idx]
                
                # Evitamos división por cero si todos los juegos de la categoría valen lo mismo
                if std > 1e-9:
                    z_scores[i] = (price - mean) / std
                else:
                    z_scores[i] = 0.0
                break

    return z_scores


def price_zscores_py(prices: np.ndarray, type_ids: np.ndarray) -> np.ndarray:
    """Versión en Python puro (sin Numba) para el benchmark comparativo."""
    unique_types = list(set(type_ids))
    means = {}
    stds = {}

    # Calcular promedio y desviación con listas nativas de Python
    for cat in unique_types:
        cat_prices = [prices[i] for i in range(len(prices)) if type_ids[i] == cat]
        if cat_prices:
            m = sum(cat_prices) / len(cat_prices)
            var = sum((x - m) ** 2 for x in cat_prices) / len(cat_prices)
            s = var ** 0.5
        else:
            m, s = 0.0, 0.0
        means[cat] = m
        stds[cat] = s

    # Calcular Z-scores en Python puro
    z_scores = np.zeros(len(prices), dtype=np.float64)
    for i in range(len(prices)):
        cat = type_ids[i]
        m, s = means[cat], stds[cat]
        z_scores[i] = (prices[i] - m) / s if s > 1e-9 else 0.0

    return z_scores