from fdk_verification.verifiers._generated_artifacts import is_rc_generated_artifact


def test_matches_verification_report_filename():
    assert is_rc_generated_artifact("forge-docs/history/2026-08-04-phase-07-verification-report.md")


def test_matches_verification_escalation_filename():
    assert is_rc_generated_artifact("forge-docs/history/2026-08-04-phase-07-verification-escalation.md")


def test_matches_multi_word_phase_names():
    assert is_rc_generated_artifact(
        "forge-docs/history/2026-08-04-phase-07-knowledge-hub-verification-report.md"
    )


def test_does_not_match_hand_written_checkpoint_log():
    assert not is_rc_generated_artifact("forge-docs/history/2026-08-04-phase-07-checkpoint-log.md")


def test_does_not_match_files_outside_history():
    assert not is_rc_generated_artifact("forge-docs/implementation/2026-08-04-phase-07-verification-report.md")


def test_does_not_match_non_markdown_files():
    assert not is_rc_generated_artifact("forge-docs/history/2026-08-04-phase-07-verification-report.txt")
