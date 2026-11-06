"""Mathematical, interface, and failure contracts for Lecture 14 trees."""

import numpy as np
import pytest
from matplotlib import pyplot as plt
from sklearn.tree import DecisionTreeClassifier as SklearnTreeClassifier
from sklearn.tree import DecisionTreeRegressor as SklearnTreeRegressor

from rice_dsm.ml.trees import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
    entropy_impurity,
    gini_impurity,
    mean_squared_impurity,
    plot_tree,
)


def test_impurity_functions_match_hand_calculations() -> None:
    assert gini_impurity([2, 2]) == pytest.approx(0.5)
    assert gini_impurity([4, 0]) == pytest.approx(0.0)
    assert entropy_impurity([2, 2]) == pytest.approx(1.0)
    assert entropy_impurity([4, 0]) == pytest.approx(0.0)
    assert mean_squared_impurity([1.0, 3.0]) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "function, values",
    [
        (gini_impurity, [-1, 2]),
        (entropy_impurity, [[1, 2]]),
        (mean_squared_impurity, []),
    ],
)
def test_impurity_functions_reject_invalid_nodes(function, values) -> None:
    with pytest.raises(ValueError):
        function(values)


@pytest.mark.parametrize("criterion", ["gini", "entropy"])
def test_classifier_finds_a_hand_computable_threshold(criterion: str) -> None:
    features = np.array([[0.0], [1.0], [2.0], [3.0]])
    labels = np.array(["cold", "cold", "hot", "hot"])

    model = DecisionTreeClassifier(criterion=criterion, max_depth=1).fit(
        features, labels
    )

    assert model.tree_.feature_index == 0
    assert model.tree_.threshold == pytest.approx(1.5)
    assert model.get_depth() == 1
    assert model.get_n_leaves() == 2
    np.testing.assert_array_equal(model.predict([[0.2], [2.8]]), ["cold", "hot"])
    np.testing.assert_allclose(model.predict_proba([[0.2], [2.8]]), [[1, 0], [0, 1]])


def test_threshold_equality_routes_left_and_leaf_ids_are_stable() -> None:
    model = DecisionTreeClassifier(max_depth=1).fit(
        [[0.0], [1.0], [2.0], [3.0]], [0, 0, 1, 1]
    )
    threshold = model.tree_.threshold
    assert threshold is not None

    np.testing.assert_array_equal(
        model.predict([[np.nextafter(threshold, -np.inf)], [threshold]]), [0, 0]
    )
    np.testing.assert_array_equal(
        model.predict([[np.nextafter(threshold, np.inf)]]), [1]
    )
    np.testing.assert_array_equal(model.apply([[0.0], [3.0]]), [0, 1])


def test_classifier_tie_policy_uses_first_sorted_class() -> None:
    model = DecisionTreeClassifier(max_depth=0).fit([[0.0], [1.0]], ["z", "a"])

    assert model.predict([[0.5]]).tolist() == ["a"]
    np.testing.assert_allclose(model.predict_proba([[0.5]]), [[0.5, 0.5]])


def test_regressor_finds_piecewise_constant_means() -> None:
    features = np.array([[0.0], [1.0], [2.0], [3.0]])
    targets = np.array([1.0, 1.0, 5.0, 7.0])

    model = DecisionTreeRegressor(max_depth=1).fit(features, targets)

    assert model.tree_.threshold == pytest.approx(1.5)
    np.testing.assert_allclose(model.predict([[0.5], [2.5]]), [1.0, 6.0])
    assert model.feature_importances_.tolist() == pytest.approx([1.0])


def test_cost_complexity_penalty_can_collapse_a_subtree() -> None:
    features = np.arange(8, dtype=float).reshape(-1, 1)
    targets = np.array([0.0, 0.1, -0.1, 0.0, 10.0, 10.1, 9.9, 10.0])

    detailed = DecisionTreeRegressor(max_depth=5, ccp_alpha=0.0).fit(features, targets)
    pruned = DecisionTreeRegressor(max_depth=5, ccp_alpha=10_000.0).fit(
        features, targets
    )

    assert detailed.get_n_leaves() > 1
    assert pruned.get_n_leaves() == 1
    assert pruned.predict([[4.0]])[0] == pytest.approx(targets.mean())


def test_exported_rules_name_features_and_leaf_evidence() -> None:
    model = DecisionTreeRegressor(max_depth=1).fit(
        [[0.0], [1.0], [2.0], [3.0]], [0.0, 0.0, 1.0, 1.0]
    )

    rules = model.export_text(["temperature"])

    assert "if temperature <= 1.5" in rules
    assert "else:  # temperature > 1.5" in rules
    assert "predict 0.0" in rules
    assert "n=2" in rules


@pytest.mark.parametrize(
    "model, targets",
    [
        (DecisionTreeClassifier(max_depth=1), [0, 0, 1, 1]),
        (DecisionTreeRegressor(max_depth=1), [1.0, 1.0, 5.0, 7.0]),
    ],
)
def test_plot_tree_exposes_questions_leaf_predictions_and_evidence(
    model, targets
) -> None:
    fitted = model.fit([[0.0], [1.0], [2.0], [3.0]], targets)
    figure, axis = plt.subplots()

    returned_axis = plot_tree(fitted, ["measurement"], ax=axis)
    labels = "\n".join(text.get_text() for text in axis.texts)

    assert returned_axis is axis
    assert "measurement <= 1.50?" in labels
    assert "predict" in labels
    assert "n =" in labels
    assert ("Gini =" in labels) or ("MSE =" in labels)
    plt.close(figure)


def test_plot_tree_validates_names_and_precision() -> None:
    model = DecisionTreeRegressor(max_depth=1).fit(
        [[0.0], [1.0], [2.0]], [0.0, 1.0, 2.0]
    )

    with pytest.raises(ValueError, match="feature_names"):
        plot_tree(model, ["too", "many"])
    with pytest.raises(ValueError, match="precision"):
        plot_tree(model, ["x"], precision=-1)


@pytest.mark.parametrize(
    "estimator",
    [DecisionTreeClassifier(), DecisionTreeRegressor()],
)
def test_prediction_before_fit_has_a_clear_error(estimator) -> None:
    with pytest.raises(RuntimeError, match="fit must be called"):
        estimator.predict([[0.0]])


@pytest.mark.parametrize(
    "features, targets, message",
    [
        ([[0.0], [np.nan]], [0, 1], "finite"),
        ([[0.0], [1.0]], [0], "match"),
        ([], [], "two-dimensional"),
    ],
)
def test_classifier_rejects_invalid_training_data(features, targets, message) -> None:
    with pytest.raises(ValueError, match=message):
        DecisionTreeClassifier().fit(features, targets)


def test_custom_trees_agree_with_trusted_library_on_fixed_structures() -> None:
    # One feature and three unambiguous response plateaus avoid comparing two
    # equally optimal but structurally different trees.
    features = np.arange(6, dtype=float).reshape(-1, 1)
    classes = np.array([0, 0, 1, 1, 1, 1])
    targets = np.array([0.0, 0.0, 3.0, 3.0, 10.0, 10.0])
    queries = np.array([[0.5], [2.5], [4.5]])

    ours_classifier = DecisionTreeClassifier(max_depth=2).fit(features, classes)
    trusted_classifier = SklearnTreeClassifier(
        max_depth=2, random_state=438
    ).fit(features, classes)
    ours_regressor = DecisionTreeRegressor(max_depth=2).fit(features, targets)
    trusted_regressor = SklearnTreeRegressor(max_depth=2, random_state=438).fit(
        features, targets
    )

    np.testing.assert_array_equal(
        ours_classifier.predict(queries), trusted_classifier.predict(queries)
    )
    np.testing.assert_allclose(
        ours_regressor.predict(queries), trusted_regressor.predict(queries)
    )
