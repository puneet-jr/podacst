"""One new user-authorized experiment paragraph, preserving earlier attempts."""
import server_section_phase6 as run
run.ATTEMPT_PREFIX='experiment-section-'
run.VALIDATOR='validate_experiment'
run.PROMPT='Write exactly one 65–75-word paragraph proposing an onboarding experiment to an early-stage product manager. Suggest comparing the existing signup promise and first onboarding task with a revised version. Track the proportion of new users completing that first task. Frame any expected improvement as an explicit hypothesis to test, not a fact. Suggest keeping or revising the change after reviewing data, without promising a result or statistical certainty. Advice only; no historical case, heading, label, citations, IDs or preamble. Start directly with the proposed action.'
if __name__=='__main__':run.main()
