"""The 8 concrete verifiers (Milestone 2) satisfying the Verifier protocol.

None of these modules import each other — each depends only on
`..contract`, `..report`, and this package's shared, verifier-agnostic
utilities (`_shell`, `_git`, `_commands`, `_paths`). That's what makes
every verifier independently constructible, runnable, and testable
without the Orchestrator or any other verifier.
"""

from .architecture import ArchitectureVerifier
from .build import BuildVerifier
from .code_quality import CodeQualityVerifier
from .documentation import DocumentationVerifier
from .regression import RegressionVerifier
from .specification import SpecificationVerifier
from .tests import TestVerifier
from .ux import UXVerifier

__all__ = [
    "ArchitectureVerifier",
    "BuildVerifier",
    "CodeQualityVerifier",
    "DocumentationVerifier",
    "RegressionVerifier",
    "SpecificationVerifier",
    "TestVerifier",
    "UXVerifier",
    "default_registry",
]


def default_registry() -> dict[str, object]:
    """One instance of each of the 8 verifiers, keyed by canonical name.

    A convenience for wiring an Orchestrator — not required, since every
    verifier above is independently constructible and runnable without it.
    """
    return {
        "Specification": SpecificationVerifier(),
        "Architecture": ArchitectureVerifier(),
        "Build": BuildVerifier(),
        "Test": TestVerifier(),
        "Regression": RegressionVerifier(),
        "Code Quality": CodeQualityVerifier(),
        "Documentation": DocumentationVerifier(),
        "UX": UXVerifier(),
    }
