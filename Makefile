PYTHON   := python3
CHAINLIT := $(PYTHON) -m chainlit

.PHONY: help install run clean

help:
	@echo ""
	@echo "  make install     Install Python dependencies into current venv"
	@echo "  make run         Run the experiment (reads from config.yaml)"
	@echo "  make clean       Delete all session logs (asks for confirmation)"
	@echo ""

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(CHAINLIT) run chat_session.py

clean:
	@echo ""
	@echo "  WARNING: This will permanently delete all session logs in 'logs/'."
	@echo "  This cannot be undone. Make sure the data is backed up."
	@echo ""
	@printf "  Type 'yes' to confirm: " && read answer && [ "$$answer" = "yes" ] \
		|| (echo "Aborted." && exit 1)
	rm -rf logs
	@echo "  Logs deleted."
