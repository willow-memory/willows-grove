# Willow Grove — convenience targets
# b17: MKGRV  ΔΣ=42

.PHONY: grove-docs help

help:
	@echo "make grove-docs  — regenerate docs/generated from Postgres (needs WILLOW_DB_URL or peer auth)"

grove-docs:
	@chmod +x scripts/grove_docs_refresh.sh 2>/dev/null || true
	./scripts/grove_docs_refresh.sh
