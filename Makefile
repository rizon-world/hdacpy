.PHONY: setup test

setup:
	bash ./scripts/install_rizon.sh
	cd rizon && make install
