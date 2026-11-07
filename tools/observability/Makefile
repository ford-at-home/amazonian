# tools/observability/Makefile — localhost dev controls.
#
# `make up`     bring up the observability server in the foreground
# `make up-bg`  bring it up in the background, logging to data/server.log
# `make down`   stop the backgrounded server (if any)
# `make logs`   tail the background log
# `make clean`  drop the venv and SQLite DB
# `make smoke`  start, hit /healthz + post a test event, stop

PY            ?= python3
VENV          ?= .venv
HOST          ?= 127.0.0.1
PORT          ?= 8765
MANIFEST_PATH ?= $(abspath ../../governance.yaml)
DB_PATH       ?= $(abspath data/observability.db)
PID_FILE      := data/server.pid
LOG_FILE      := data/server.log

ENV := AMAZONIAN_OBS_MANIFEST_PATH=$(MANIFEST_PATH) AMAZONIAN_OBS_DB_PATH=$(DB_PATH)

.PHONY: venv install up up-bg down logs clean smoke

venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)

install: venv
	@$(VENV)/bin/pip install -q --upgrade pip
	@$(VENV)/bin/pip install -q -r requirements.txt
	@echo "deps installed in $(VENV)"

up: install
	@mkdir -p data
	@echo "starting observability at http://$(HOST):$(PORT)"
	@echo "  manifest: $(MANIFEST_PATH)"
	@echo "  db:       $(DB_PATH)"
	@$(ENV) $(VENV)/bin/uvicorn server.app:app --host $(HOST) --port $(PORT)

up-bg: install
	@mkdir -p data
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "already running as pid $$(cat $(PID_FILE))"; exit 0; \
	fi
	@$(ENV) nohup $(VENV)/bin/uvicorn server.app:app \
		--host $(HOST) --port $(PORT) > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE)
	@sleep 0.5
	@echo "started; pid=$$(cat $(PID_FILE)) log=$(LOG_FILE)"
	@echo "open http://$(HOST):$(PORT)/"

down:
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		if kill -0 $$pid 2>/dev/null; then kill $$pid && echo "stopped pid=$$pid"; \
		else echo "stale pid file; cleaning up"; fi; \
		rm -f $(PID_FILE); \
	else echo "not running"; fi

logs:
	@test -f $(LOG_FILE) && tail -f $(LOG_FILE) || echo "no log yet"

clean: down
	@rm -rf $(VENV) data/observability.db $(LOG_FILE) $(PID_FILE)
	@echo "cleaned venv and data"

smoke: up-bg
	@sleep 1.0
	@echo "health:" && curl -fsS http://$(HOST):$(PORT)/healthz && echo ""
	@echo "post event:"
	@curl -fsS -X POST http://$(HOST):$(PORT)/api/events \
		-H 'Content-Type: application/json' \
		-d '{"skill_id":"smoke-test","phase":"end","payload":{"note":"hello from make smoke"}}'
	@echo ""
	@echo "state:" && curl -fsS http://$(HOST):$(PORT)/api/state | head -c 300 && echo "..."
	@$(MAKE) down
