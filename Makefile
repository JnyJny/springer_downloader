
TARGET=springer

VERSION_FILE= $(TARGET)/__version__.py

.PHONY: $(VERSION_FILE) tag bump push update_pyproject README.md

all:
	@echo $(TARGET) release automation
	@echo
	@echo "patch_release - updates version and publishes"
	@echo "major_release - updates version and publishes"
	@echo "minor_release - updates version and publishes"
	@echo
	@echo "release       - performs a patch_release"
	@echo
	@echo "MAJOR  - updates version major number"
	@echo "MINOR  - updates version minor number"
	@echo "PATCH  - updates version patch number"
	@echo "major  - commits version update to git and tags"
	@echo "minor  - commits version update to git and tags"
	@echo "patch  - commits version update to git and tags"
	@echo "update - updates __version__.py, commits and tags"
	@echo "push   - pushes commits and tags to origin/master"
	@echo
	@echo "clean  - cleans up report files and/or directories"

README.md:
	typer $(TARGET).__main__ utils docs --name $(TARGET) --output $@

MAJOR:
	@poetry version major

MINOR:
	@poetry version minor

PATCH:
	@poetry version patch

major: MAJOR update

minor: MINOR update

patch: PATCH update


version_file: $(VERSION_FILE)
$(VERSION_FILE):
	@awk '/^version/ {print $$0}' pyproject.toml | sed "s/version/__version__/" > $@

update: $(VERSION_FILE)
	@git add pyproject.toml $(VERSION_FILE)
	@awk '{print $$3}' $(VERSION_FILE) | xargs git commit -m
	@awk '{print $$3}' $(VERSION_FILE) | xargs git tag


push:
	@git push --tags origin master

publish:
	@poetry build
	@poetry publish


patch_release: patch push publish

major_release: major push publish

minor_release: minor push publish

release: patch_release

demo:
	@make -C demo


clean:
	@/bin/rm -rf *.pdf *.epub DOWNLOAD_ERRORS.txt *.cast
	@make -C demo clean
