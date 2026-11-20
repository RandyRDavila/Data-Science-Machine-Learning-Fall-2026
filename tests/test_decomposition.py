"""Mathematical and interface tests for dimensionality reduction."""

import numpy as np
import pytest

from rice_dsm.ml.decomposition import PrincipalComponentProjector


def correlated_observations() -> np.ndarray:
    """Return a small rank-two matrix with one dominant direction."""

    return np.array(
        [
            [-2.0, -4.1, 0.2],
            [-1.0, -1.9, -0.1],
            [0.0, 0.1, 0.0],
            [1.0, 2.2, 0.1],
            [2.0, 3.9, -0.2],
        ]
    )


def test_components_are_orthonormal_and_scores_are_centered() -> None:
    observations = correlated_observations()
    projector = PrincipalComponentProjector(2)

    scores = projector.fit_transform(observations)

    assert scores.shape == (5, 2)
    assert np.allclose(scores.mean(axis=0), 0.0)
    assert np.allclose(projector.components_ @ projector.components_.T, np.eye(2))
    assert np.all(np.diff(projector.explained_variance_) <= 0)
    assert 0.0 < projector.explained_variance_ratio_.sum() <= 1.0


def test_reconstruction_error_decreases_when_rank_increases() -> None:
    observations = correlated_observations()
    rank_one = PrincipalComponentProjector(1).fit(observations)
    rank_two = PrincipalComponentProjector(2).fit(observations)

    assert rank_two.reconstruction_error(observations) < rank_one.reconstruction_error(
        observations
    )


def test_full_rank_reconstruction_recovers_the_observations() -> None:
    observations = correlated_observations()
    projector = PrincipalComponentProjector(3).fit(observations)

    reconstructed = projector.inverse_transform(projector.transform(observations))

    assert np.allclose(reconstructed, observations)
    assert projector.reconstruction_error(observations) < 1e-28


@pytest.mark.parametrize(
    ("observations", "message"),
    [
        (np.array([1.0, 2.0]), "two-dimensional"),
        (np.array([[1.0], [np.nan]]), "finite"),
        (np.empty((1, 3)), "at least two rows"),
    ],
)
def test_invalid_observation_matrices_fail_clearly(
    observations: np.ndarray, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        PrincipalComponentProjector(1).fit(observations)


def test_transform_rejects_wrong_schema_and_use_before_fit() -> None:
    observations = correlated_observations()
    projector = PrincipalComponentProjector(2)

    with pytest.raises(RuntimeError, match="Call fit"):
        projector.transform(observations)

    projector.fit(observations)
    with pytest.raises(ValueError, match="Expected 3 features"):
        projector.transform(np.ones((3, 2)))


def test_component_signs_are_deterministic_for_teaching_displays() -> None:
    projector = PrincipalComponentProjector(2).fit(correlated_observations())

    for component in projector.components_:
        pivot = np.argmax(np.abs(component))
        assert component[pivot] > 0
