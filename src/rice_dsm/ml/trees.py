"""Inspectable classification and regression trees for Lecture 14.

The implementation favors explicit mathematical structure over production
speed.  It uses greedy, axis-aligned binary splits and exposes fitted nodes so
students can connect impurity calculations to the resulting prediction rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

ClassificationCriterion = Literal["gini", "entropy"]


def gini_impurity(class_counts: ArrayLike) -> float:
    """Return Gini impurity from nonnegative class counts.

    Parameters
    ----------
    class_counts
        Number of observations belonging to each class.

    Returns
    -------
    float
        ``1 - sum(p_k**2)``. An empty node has impurity zero.
    """

    counts = np.asarray(class_counts, dtype=float)
    if counts.ndim != 1 or np.any(counts < 0):
        raise ValueError("class_counts must be a one-dimensional nonnegative array")
    total = float(counts.sum())
    if total == 0.0:
        return 0.0
    probabilities = counts / total
    return float(1.0 - probabilities @ probabilities)


def entropy_impurity(class_counts: ArrayLike) -> float:
    """Return base-two entropy from nonnegative class counts."""

    counts = np.asarray(class_counts, dtype=float)
    if counts.ndim != 1 or np.any(counts < 0):
        raise ValueError("class_counts must be a one-dimensional nonnegative array")
    total = float(counts.sum())
    if total == 0.0:
        return 0.0
    probabilities = counts[counts > 0] / total
    return float(-(probabilities * np.log2(probabilities)).sum())


def mean_squared_impurity(targets: ArrayLike) -> float:
    """Return the mean squared deviation from a node's target mean."""

    values = np.asarray(targets, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("targets must be a nonempty one-dimensional array")
    return float(np.mean((values - values.mean()) ** 2))


@dataclass(slots=True)
class TreeNode:
    """One fitted region in an inspectable binary decision tree."""

    prediction: int | float
    n_samples: int
    impurity: float
    class_counts: NDArray[np.int64] | None = None
    feature_index: int | None = None
    threshold: float | None = None
    impurity_decrease: float = 0.0
    left: TreeNode | None = None
    right: TreeNode | None = None

    @property
    def is_leaf(self) -> bool:
        """Whether this node returns a prediction rather than asking a question."""

        return self.feature_index is None


class _DecisionTreeBase:
    """Shared recursive-partitioning machinery."""

    def __init__(
        self,
        *,
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
    ) -> None:
        if max_depth is not None and max_depth < 0:
            raise ValueError("max_depth must be nonnegative or None")
        if min_samples_split < 2:
            raise ValueError("min_samples_split must be at least 2")
        if min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1")
        if min_impurity_decrease < 0 or ccp_alpha < 0:
            raise ValueError("impurity and pruning penalties must be nonnegative")
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_impurity_decrease = min_impurity_decrease
        self.ccp_alpha = ccp_alpha

    def _validate_features(self, features: ArrayLike) -> NDArray[np.float64]:
        array = np.asarray(features, dtype=float)
        if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
            raise ValueError("features must be a nonempty two-dimensional array")
        if not np.isfinite(array).all():
            raise ValueError("features must contain only finite values")
        return array

    def _validate_prediction_features(
        self, features: ArrayLike
    ) -> NDArray[np.float64]:
        self._require_fitted()
        array = self._validate_features(features)
        if array.shape[1] != self.n_features_in_:
            raise ValueError(
                f"expected {self.n_features_in_} features; received {array.shape[1]}"
            )
        return array

    def _require_fitted(self) -> None:
        if not hasattr(self, "tree_"):
            raise RuntimeError("fit must be called before prediction")

    def _route(self, row: NDArray[np.float64]) -> TreeNode:
        node = self.tree_
        while not node.is_leaf:
            assert node.feature_index is not None
            assert node.threshold is not None
            assert node.left is not None and node.right is not None
            node = (
                node.left
                if row[node.feature_index] <= node.threshold
                else node.right
            )
        return node

    def apply(self, features: ArrayLike) -> NDArray[np.int64]:
        """Return deterministic preorder leaf identifiers for each observation."""

        array = self._validate_prediction_features(features)
        leaf_ids: dict[int, int] = {}

        def register(node: TreeNode) -> None:
            if node.is_leaf:
                leaf_ids[id(node)] = len(leaf_ids)
                return
            assert node.left is not None and node.right is not None
            register(node.left)
            register(node.right)

        register(self.tree_)
        return np.asarray([leaf_ids[id(self._route(row))] for row in array])

    def get_depth(self) -> int:
        """Return the greatest number of decisions on a root-to-leaf path."""

        self._require_fitted()

        def depth(node: TreeNode) -> int:
            if node.is_leaf:
                return 0
            assert node.left is not None and node.right is not None
            return 1 + max(depth(node.left), depth(node.right))

        return depth(self.tree_)

    def get_n_leaves(self) -> int:
        """Return the number of terminal regions."""

        self._require_fitted()

        def count(node: TreeNode) -> int:
            if node.is_leaf:
                return 1
            assert node.left is not None and node.right is not None
            return count(node.left) + count(node.right)

        return count(self.tree_)

    def export_text(
        self, feature_names: list[str] | tuple[str, ...] | None = None
    ) -> str:
        """Render the fitted prediction rule as readable, testable branches."""

        self._require_fitted()
        if feature_names is None:
            feature_names = [f"x{index}" for index in range(self.n_features_in_)]
        if len(feature_names) != self.n_features_in_:
            raise ValueError("feature_names must match the fitted feature count")
        lines: list[str] = []

        def visit(node: TreeNode, indent: str) -> None:
            if node.is_leaf:
                lines.append(
                    f"{indent}predict {self._display_prediction(node.prediction)} "
                    f"(n={node.n_samples}, impurity={node.impurity:.4f})"
                )
                return
            assert node.feature_index is not None and node.threshold is not None
            assert node.left is not None and node.right is not None
            name = feature_names[node.feature_index]
            lines.append(f"{indent}if {name} <= {node.threshold:.6g}:")
            visit(node.left, indent + "  ")
            lines.append(f"{indent}else:  # {name} > {node.threshold:.6g}")
            visit(node.right, indent + "  ")

        visit(self.tree_, "")
        return "\n".join(lines)

    def _display_prediction(self, prediction: int | float) -> object:
        return prediction

    def _set_feature_importances(self) -> None:
        decreases = np.zeros(self.n_features_in_, dtype=float)

        def collect(node: TreeNode) -> None:
            if node.is_leaf:
                return
            assert node.feature_index is not None
            assert node.left is not None and node.right is not None
            decreases[node.feature_index] += node.impurity_decrease * node.n_samples
            collect(node.left)
            collect(node.right)

        collect(self.tree_)
        total = decreases.sum()
        self.feature_importances_ = decreases / total if total > 0 else decreases


def plot_tree(
    estimator: _DecisionTreeBase,
    feature_names: list[str] | tuple[str, ...] | None = None,
    *,
    ax: Any | None = None,
    precision: int = 2,
) -> Any:
    """Draw an inspectable fitted course tree with Matplotlib.

    Parameters
    ----------
    estimator
        A fitted :class:`DecisionTreeClassifier` or
        :class:`DecisionTreeRegressor`.
    feature_names
        Human-readable names in the same order as the fitted feature matrix.
    ax
        Optional Matplotlib axes. A new figure and axes are created when omitted.
    precision
        Number of decimal places shown for thresholds, impurity, and predictions.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the diagram. Returning the axes lets callers add titles,
        annotations, or save the figure without hidden global state.

    Notes
    -----
    The diagram is an explanation of one fitted artifact. It does not establish
    causal, biological, or population-stable relationships.
    """

    import matplotlib.pyplot as plt

    estimator._require_fitted()
    if feature_names is None:
        feature_names = [f"x{index}" for index in range(estimator.n_features_in_)]
    if len(feature_names) != estimator.n_features_in_:
        raise ValueError("feature_names must match the fitted feature count")
    if precision < 0:
        raise ValueError("precision must be nonnegative")
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5.5))

    # Leaves receive consecutive horizontal slots. Each internal node is centered
    # above its two children, which makes the recursive structure visible.
    positions: dict[int, tuple[float, int]] = {}
    next_leaf = 0

    def assign_positions(node: TreeNode, depth: int) -> float:
        nonlocal next_leaf
        if node.is_leaf:
            x_position = float(next_leaf)
            next_leaf += 1
        else:
            assert node.left is not None and node.right is not None
            left_x = assign_positions(node.left, depth + 1)
            right_x = assign_positions(node.right, depth + 1)
            x_position = (left_x + right_x) / 2.0
        positions[id(node)] = (x_position, depth)
        return x_position

    assign_positions(estimator.tree_, 0)
    leaf_count = max(next_leaf, 1)
    tree_depth = max(estimator.get_depth(), 1)

    def coordinates(node: TreeNode) -> tuple[float, float]:
        x_position, depth = positions[id(node)]
        return ((x_position + 0.5) / leaf_count, 1.0 - depth / (tree_depth + 0.35))

    def impurity_name() -> str:
        if isinstance(estimator, DecisionTreeClassifier):
            return "Gini" if estimator.criterion == "gini" else "entropy"
        return "MSE"

    def node_label(node: TreeNode) -> str:
        evidence = (
            f"n = {node.n_samples}\n"
            f"{impurity_name()} = {node.impurity:.{precision}f}"
        )
        if node.is_leaf:
            prediction = estimator._display_prediction(node.prediction)
            if node.class_counts is not None:
                counts = ", ".join(str(int(count)) for count in node.class_counts)
                return f"predict {prediction}\ncounts = [{counts}]\n{evidence}"
            return f"predict {float(node.prediction):.{precision}f}\n{evidence}"
        assert node.feature_index is not None and node.threshold is not None
        feature = feature_names[node.feature_index]
        return f"{feature} <= {node.threshold:.{precision}f}?\n{evidence}"

    # Draw edges first so node boxes remain visually on top of the arrows.
    def draw_edges(node: TreeNode) -> None:
        if node.is_leaf:
            return
        assert node.left is not None and node.right is not None
        parent_xy = coordinates(node)
        for child, answer in ((node.left, "yes"), (node.right, "no")):
            child_xy = coordinates(child)
            ax.annotate(
                "",
                xy=child_xy,
                xytext=parent_xy,
                arrowprops={"arrowstyle": "->", "color": "#5b6770", "lw": 1.4},
                zorder=1,
            )
            midpoint = (
                (parent_xy[0] + child_xy[0]) / 2.0,
                (parent_xy[1] + child_xy[1]) / 2.0,
            )
            ax.text(*midpoint, answer, color="#5b6770", fontsize=8, ha="center")
            draw_edges(child)

    def draw_nodes(node: TreeNode) -> None:
        x_position, y_position = coordinates(node)
        face_color = "#f7e7a9" if node.is_leaf else "#dce6f2"
        ax.text(
            x_position,
            y_position,
            node_label(node),
            ha="center",
            va="center",
            fontsize=8.5,
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": face_color,
                "edgecolor": "#00205b",
                "linewidth": 1.2,
            },
            zorder=2,
        )
        if not node.is_leaf:
            assert node.left is not None and node.right is not None
            draw_nodes(node.left)
            draw_nodes(node.right)

    draw_edges(estimator.tree_)
    draw_nodes(estimator.tree_)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-0.05, 1.08)
    ax.set_axis_off()
    return ax


class DecisionTreeClassifier(_DecisionTreeBase):
    """A small CART-style classifier supporting Gini impurity or entropy."""

    def __init__(
        self,
        *,
        criterion: ClassificationCriterion = "gini",
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
    ) -> None:
        if criterion not in {"gini", "entropy"}:
            raise ValueError("criterion must be 'gini' or 'entropy'")
        super().__init__(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_impurity_decrease=min_impurity_decrease,
            ccp_alpha=ccp_alpha,
        )
        self.criterion = criterion

    def fit(self, features: ArrayLike, targets: ArrayLike) -> DecisionTreeClassifier:
        """Grow and optionally cost-complexity-prune a classification tree."""

        x = self._validate_features(features)
        y = np.asarray(targets)
        if y.ndim != 1 or y.shape[0] != x.shape[0]:
            raise ValueError("targets must be one-dimensional and match features")
        self.classes_, encoded = np.unique(y, return_inverse=True)
        if self.classes_.size < 2:
            raise ValueError("classification requires at least two classes")
        self.n_features_in_ = x.shape[1]
        self._x = x
        self._y = encoded.astype(int)
        self.tree_, _, _ = self._grow(np.arange(x.shape[0]), depth=0)
        self._set_feature_importances()
        del self._x, self._y
        return self

    def _impurity(self, counts: NDArray[np.int64]) -> float:
        return (
            gini_impurity(counts)
            if self.criterion == "gini"
            else entropy_impurity(counts)
        )

    def _grow(
        self, indices: NDArray[np.int64], depth: int
    ) -> tuple[TreeNode, float, int]:
        counts = np.bincount(self._y[indices], minlength=self.classes_.size)
        impurity = self._impurity(counts)
        prediction = int(np.flatnonzero(counts == counts.max())[0])
        node = TreeNode(prediction, len(indices), impurity, class_counts=counts)
        raw_leaf_loss = len(indices) * impurity
        should_stop = (
            impurity <= np.finfo(float).eps
            or len(indices) < self.min_samples_split
            or len(indices) < 2 * self.min_samples_leaf
            or (self.max_depth is not None and depth >= self.max_depth)
        )
        if should_stop:
            return node, raw_leaf_loss, 1

        split = self._best_split(indices, raw_leaf_loss)
        if split is None:
            return node, raw_leaf_loss, 1
        feature, threshold, left_indices, right_indices, decrease = split
        left, left_loss, left_leaves = self._grow(left_indices, depth + 1)
        right, right_loss, right_leaves = self._grow(right_indices, depth + 1)
        subtree_loss = left_loss + right_loss
        subtree_leaves = left_leaves + right_leaves
        if raw_leaf_loss + self.ccp_alpha <= (
            subtree_loss + self.ccp_alpha * subtree_leaves
        ):
            return node, raw_leaf_loss, 1
        node.feature_index = feature
        node.threshold = threshold
        node.impurity_decrease = decrease
        node.left = left
        node.right = right
        return node, subtree_loss, subtree_leaves

    def _best_split(
        self, indices: NDArray[np.int64], parent_loss: float
    ) -> tuple[int, float, NDArray[np.int64], NDArray[np.int64], float] | None:
        best: (
            tuple[int, float, NDArray[np.int64], NDArray[np.int64], float] | None
        ) = None
        best_loss = parent_loss
        n_node = len(indices)
        for feature in range(self.n_features_in_):
            order = np.argsort(self._x[indices, feature], kind="mergesort")
            ordered_indices = indices[order]
            values = self._x[ordered_indices, feature]
            labels = self._y[ordered_indices]
            total_counts = np.bincount(labels, minlength=self.classes_.size)
            left_counts = np.zeros_like(total_counts)
            for position in range(1, n_node):
                left_counts[labels[position - 1]] += 1
                if values[position - 1] == values[position]:
                    continue
                if (
                    position < self.min_samples_leaf
                    or n_node - position < self.min_samples_leaf
                ):
                    continue
                right_counts = total_counts - left_counts
                loss = position * self._impurity(left_counts) + (
                    n_node - position
                ) * self._impurity(right_counts)
                if loss < best_loss - 1e-12:
                    threshold = float((values[position - 1] + values[position]) / 2.0)
                    decrease = (parent_loss - loss) / n_node
                    if decrease + 1e-12 < self.min_impurity_decrease:
                        continue
                    best_loss = loss
                    best = (
                        feature,
                        threshold,
                        ordered_indices[:position],
                        ordered_indices[position:],
                        decrease,
                    )
        return best

    def predict(self, features: ArrayLike) -> NDArray[np.object_]:
        """Predict original class labels."""

        array = self._validate_prediction_features(features)
        encoded = np.asarray([self._route(row).prediction for row in array], dtype=int)
        return self.classes_[encoded]

    def predict_proba(self, features: ArrayLike) -> NDArray[np.float64]:
        """Return empirical class proportions in each reached leaf."""

        array = self._validate_prediction_features(features)
        probabilities = []
        for row in array:
            counts = self._route(row).class_counts
            assert counts is not None
            probabilities.append(counts / counts.sum())
        return np.asarray(probabilities)

    def _display_prediction(self, prediction: int | float) -> object:
        label = self.classes_[int(prediction)]
        # NumPy scalar reprs such as ``np.int64(1)`` distract from the model's
        # meaning in exported rules and diagrams. Display the corresponding
        # ordinary Python value while preserving strings with quotes.
        if isinstance(label, np.generic):
            label = label.item()
        return repr(label)


class DecisionTreeRegressor(_DecisionTreeBase):
    """A small CART-style regressor minimizing within-leaf squared error."""

    def fit(self, features: ArrayLike, targets: ArrayLike) -> DecisionTreeRegressor:
        """Grow and optionally cost-complexity-prune a regression tree."""

        x = self._validate_features(features)
        y = np.asarray(targets, dtype=float)
        if y.ndim != 1 or y.shape[0] != x.shape[0]:
            raise ValueError("targets must be one-dimensional and match features")
        if not np.isfinite(y).all():
            raise ValueError("targets must contain only finite values")
        self.n_features_in_ = x.shape[1]
        self._x = x
        self._y = y
        self.tree_, _, _ = self._grow(np.arange(x.shape[0]), depth=0)
        self._set_feature_importances()
        del self._x, self._y
        return self

    def _grow(
        self, indices: NDArray[np.int64], depth: int
    ) -> tuple[TreeNode, float, int]:
        targets = self._y[indices]
        impurity = mean_squared_impurity(targets)
        node = TreeNode(float(targets.mean()), len(indices), impurity)
        raw_leaf_loss = len(indices) * impurity
        should_stop = (
            impurity <= np.finfo(float).eps
            or len(indices) < self.min_samples_split
            or len(indices) < 2 * self.min_samples_leaf
            or (self.max_depth is not None and depth >= self.max_depth)
        )
        if should_stop:
            return node, raw_leaf_loss, 1
        split = self._best_split(indices, raw_leaf_loss)
        if split is None:
            return node, raw_leaf_loss, 1
        feature, threshold, left_indices, right_indices, decrease = split
        left, left_loss, left_leaves = self._grow(left_indices, depth + 1)
        right, right_loss, right_leaves = self._grow(right_indices, depth + 1)
        subtree_loss = left_loss + right_loss
        subtree_leaves = left_leaves + right_leaves
        if raw_leaf_loss + self.ccp_alpha <= (
            subtree_loss + self.ccp_alpha * subtree_leaves
        ):
            return node, raw_leaf_loss, 1
        node.feature_index = feature
        node.threshold = threshold
        node.impurity_decrease = decrease
        node.left = left
        node.right = right
        return node, subtree_loss, subtree_leaves

    def _best_split(
        self, indices: NDArray[np.int64], parent_loss: float
    ) -> tuple[int, float, NDArray[np.int64], NDArray[np.int64], float] | None:
        best: (
            tuple[int, float, NDArray[np.int64], NDArray[np.int64], float] | None
        ) = None
        best_loss = parent_loss
        n_node = len(indices)
        for feature in range(self.n_features_in_):
            order = np.argsort(self._x[indices, feature], kind="mergesort")
            ordered_indices = indices[order]
            values = self._x[ordered_indices, feature]
            targets = self._y[ordered_indices]
            cumulative_sum = np.cumsum(targets)
            cumulative_square = np.cumsum(targets**2)
            total_sum = cumulative_sum[-1]
            total_square = cumulative_square[-1]
            last_position = n_node - self.min_samples_leaf + 1
            for position in range(self.min_samples_leaf, last_position):
                if values[position - 1] == values[position]:
                    continue
                left_sum = cumulative_sum[position - 1]
                left_square = cumulative_square[position - 1]
                right_sum = total_sum - left_sum
                right_square = total_square - left_square
                left_loss = left_square - left_sum**2 / position
                right_count = n_node - position
                right_loss = right_square - right_sum**2 / right_count
                loss = float(max(left_loss, 0.0) + max(right_loss, 0.0))
                if loss < best_loss - 1e-12:
                    threshold = float((values[position - 1] + values[position]) / 2.0)
                    decrease = (parent_loss - loss) / n_node
                    if decrease + 1e-12 < self.min_impurity_decrease:
                        continue
                    best_loss = loss
                    best = (
                        feature,
                        threshold,
                        ordered_indices[:position],
                        ordered_indices[position:],
                        decrease,
                    )
        return best

    def predict(self, features: ArrayLike) -> NDArray[np.float64]:
        """Predict the mean target of each reached leaf."""

        array = self._validate_prediction_features(features)
        return np.asarray([self._route(row).prediction for row in array], dtype=float)
