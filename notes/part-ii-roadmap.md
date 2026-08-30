# Part II roadmap: Supervised Learning Systems

Part II studies supervised learning as the design of a defensible prediction
system. The sequence retains the mathematical clarity of the affine unit,
perceptron, and gradient descent while placing them inside contemporary data,
evaluation, software, and operational contracts.

## Governing question

How does a claim about future or unobserved outcomes survive the path from a
sample of labeled observations to a versioned model that produces monitored
decisions?

The recurring architecture is:

```text
validated observations
        |
versioned split and feature definitions
        |
train -> evaluate -> promote
        |
versioned model artifact
        |
batch job or prediction API
        |
scientific or operational client
        |
outcomes, monitoring, and retraining evidence
```

Three paths must remain visible:

1. The **training path** creates a candidate artifact from versioned evidence.
2. The **prediction path** applies an approved artifact under an interface
   contract.
3. The **feedback path** joins predictions to delayed outcomes and decides
   whether intervention, rollback, or retraining is justified.

## Unit sequence

| Unit | Core question | System contribution |
| --- | --- | --- |
| 9. Supervised learning systems | What exactly is being predicted, from what information, for whom, and when? | Prediction contract, leakage-safe split, baseline, and first vertical slice |
| 10. Linear regression and regularization | What does an affine predictor estimate, and how do optimization and regularization change it? | Tested regression pipeline and diagnostics |
| 11. Classification and decisions | How do scores, probabilities, thresholds, and costs become decisions? | Calibrated classifier with explicit decision policy |
| 12. Geometric learning | When should similarity, distance, margin, or a kernel determine a prediction? | Geometry-aware preprocessing and latency contract |
| 13. Decision trees | How can recursive partitions model interactions, and where do they become unstable? | Interpretable tree baseline with pruning evidence |
| 14. Ensemble learning | How do diverse weak or unstable learners become a stronger system? | Forest, boosting, voting, and stacking comparison |
| 15. Model selection and evaluation | Which candidate should be promoted, and how strong is the evidence? | Reproducible selection protocol and promotion gate |
| 16. Neural networks and automatic differentiation | What does composition add beyond one affine unit, and what does autodiff actually compute? | Small tested neural model and versioned artifact |
| 17. Reliable supervised systems | How do training, prediction, and feedback remain coherent after release? | End-to-end capstone with monitoring and rollback |

## Pedagogical decisions

- The affine map \(w^T x+b\) is a unifying object, not a claim that all learners
  share one interchangeable update rule.
- The perceptron is taught briefly for historical and geometric clarity.
  Linear and logistic regression receive deeper treatment because their losses,
  estimates, diagnostics, and probability semantics matter widely.
- One small backpropagation calculation is implemented manually and checked
  numerically. Subsequent neural-network work uses automatic differentiation.
- Ensembles are a central unit, not an optional footnote.
- Every algorithm is paired with a baseline, a leakage analysis, an evaluation
  design, resource constraints, and an artifact contract.
- Notebooks remain experimental laboratories. Reusable transformers, metrics,
  schemas, and model interfaces graduate into `rice_dsm`; tests and CI preserve
  them.

## Running case

A battery-cell laboratory supplies the recurring case. Measurements available
at an explicitly named observation time are used either to estimate remaining
capacity (regression) or to predict whether a cell will cross a degradation
threshold within a future horizon (classification). Cell identity, experimental
batch, and time make random row splitting unsafe in many formulations. The case
therefore supports grouping, temporal evaluation, delayed outcomes, calibration,
resource-aware serving, and drift without pretending that prediction alone
establishes a causal or safety claim.

Small synthetic and repository-owned data should support deterministic offline
execution. A larger public dataset may be added only with documented provenance,
license, retrieval, schema, and a small CI-safe fixture.

## Release standard for each unit

Before a unit is classroom-ready, its detailed notebooks should include a
motivating scientific question, mathematical development, executable
experiments, failure cases, interpretation, exercises, and a professional
artifact. The repository tests should execute every notebook in a clean locked
environment and verify any new package contract.
