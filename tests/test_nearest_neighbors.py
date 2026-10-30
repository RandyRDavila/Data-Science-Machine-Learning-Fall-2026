"""Mathematical and software contracts for the nearest-neighbor lesson."""

import csv
import hashlib
from pathlib import Path

import numpy as np
import pytest

from rice_dsm.ml.neighbors import (
    ItemKNNRecommender,
    KNearestNeighborsClassifier,
    KNearestNeighborsRegressor,
    euclidean_distances,
)
from rice_dsm.paths import movielens_teaching_directory

PROJECT_ROOT = Path(__file__).parents[1]
MOVIES_SHA256 = "3cc819c9d68059d980caad9e41a34bab90ff5309d42d258b87dddfff425e5c29"
RATINGS_SHA256 = "6f5bf8d4ef0e604197cdbd3771369fa7e0a32b140a7b272e7aa6aed92e3aa75c"


def test_movielens_digests_have_a_cross_platform_line_ending_contract() -> None:
    attributes = (PROJECT_ROOT / ".gitattributes").read_text(encoding="utf-8")

    assert "data/lecture_13_movielens/*.csv text eol=lf" in attributes


def test_versioned_movielens_subset_is_authentic_and_structurally_sound() -> None:
    data_directory = movielens_teaching_directory(PROJECT_ROOT)
    movies_path = data_directory / "movies.csv"
    ratings_path = data_directory / "ratings.csv"

    assert hashlib.sha256(movies_path.read_bytes()).hexdigest() == MOVIES_SHA256
    assert hashlib.sha256(ratings_path.read_bytes()).hexdigest() == RATINGS_SHA256

    with movies_path.open(encoding="utf-8", newline="") as stream:
        movies = list(csv.DictReader(stream))
    with ratings_path.open(encoding="utf-8", newline="") as stream:
        ratings = list(csv.DictReader(stream))

    assert len(movies) == 80
    assert len(ratings) == 13_817
    assert len({(row["userId"], row["movieId"]) for row in ratings}) == len(ratings)
    assert {row["movieId"] for row in ratings} == {row["movieId"] for row in movies}


def test_euclidean_distances_matches_hand_computable_geometry() -> None:
    queries = np.array([[0.0, 0.0], [3.0, 4.0]])
    references = np.array([[3.0, 4.0], [0.0, 4.0]])

    distances = euclidean_distances(queries, references)

    np.testing.assert_allclose(distances, [[5.0, 4.0], [0.0, 3.0]])


def test_classifier_returns_sorted_neighbors_and_reproducible_tie_break() -> None:
    features = np.array([[0.0], [2.0], [4.0], [6.0]])
    labels = np.array(["b", "a", "b", "a"])
    model = KNearestNeighborsClassifier(n_neighbors=2).fit(features, labels)

    distances, indices = model.kneighbors([[3.0]])

    np.testing.assert_allclose(distances, [[1.0, 1.0]])
    np.testing.assert_array_equal(indices, [[1, 2]])
    assert model.predict([[3.0]]).tolist() == ["a"]
    np.testing.assert_allclose(model.predict_proba([[3.0]]), [[0.5, 0.5]])


def test_distance_weighting_gives_exact_matches_all_vote_mass() -> None:
    model = KNearestNeighborsClassifier(n_neighbors=3, weights="distance").fit(
        [[0.0], [0.0], [1.0]], ["cat", "cat", "dog"]
    )

    probabilities = model.predict_proba([[0.0]])

    np.testing.assert_allclose(probabilities, [[1.0, 0.0]])


def test_regressor_matches_uniform_and_weighted_hand_calculations() -> None:
    features = np.array([[0.0], [2.0], [5.0]])
    targets = np.array([0.0, 4.0, 10.0])

    uniform = KNearestNeighborsRegressor(n_neighbors=2).fit(features, targets)
    weighted = KNearestNeighborsRegressor(
        n_neighbors=2, weights="distance"
    ).fit(features, targets)

    assert uniform.predict([[1.5]])[0] == pytest.approx(2.0)
    assert weighted.predict([[1.5]])[0] == pytest.approx(3.0)


@pytest.mark.parametrize(
    ("estimator", "features", "targets", "message"),
    [
        (KNearestNeighborsClassifier(2), [[0.0]], [0], "cannot exceed"),
        (KNearestNeighborsRegressor(1), [[0.0], [1.0]], [1.0], "align"),
        (KNearestNeighborsRegressor(1), [[0.0]], [np.nan], "finite"),
    ],
)
def test_supervised_estimators_reject_invalid_training_contracts(
    estimator: object, features: list[list[float]], targets: list[object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        estimator.fit(features, targets)  # type: ignore[attr-defined]


def test_predict_before_fit_and_wrong_feature_width_fail_helpfully() -> None:
    model = KNearestNeighborsClassifier(n_neighbors=1)
    with pytest.raises(RuntimeError, match="fit"):
        model.predict([[0.0]])

    model.fit([[0.0, 1.0], [1.0, 0.0]], [0, 1])
    with pytest.raises(ValueError, match="2 columns"):
        model.predict([[0.0]])


def _ratings() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Users 1 and 2 rate A and B above their own baselines; user 3 has not seen B.
    return (
        np.array([1, 1, 1, 2, 2, 2, 3, 3, 3]),
        np.array(["A", "B", "D", "A", "B", "D", "A", "C", "D"]),
        np.array([5.0, 4.0, 1.0, 4.0, 3.0, 1.0, 5.0, 2.0, 1.0]),
    )


def test_recommender_finds_similar_items_and_excludes_seen_items() -> None:
    users, items, ratings = _ratings()
    model = ItemKNNRecommender(n_neighbors=2, min_common_users=2).fit(
        users, items, ratings
    )

    similar_ids, similarities = model.similar_items("A", n=2)
    recommendation_ids, predicted_ratings = model.recommend(3, n=2)

    assert similar_ids.tolist() == ["B"]
    assert similarities[0] > 0.9
    assert recommendation_ids.tolist() == ["B"]
    assert np.isfinite(predicted_ratings).all()
    assert not {"A", "C", "D"} & set(recommendation_ids)


def test_recommender_rejects_duplicate_events_and_unknown_ids() -> None:
    model = ItemKNNRecommender(min_common_users=1)
    with pytest.raises(ValueError, match="only once"):
        model.fit([1, 1], ["A", "A"], [4.0, 5.0])

    users, items, ratings = _ratings()
    model.fit(users, items, ratings)
    with pytest.raises(KeyError, match="unknown user_id"):
        model.recommend(999)
