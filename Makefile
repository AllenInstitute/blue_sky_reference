PROJECTNAME = blue_sky_reference
DISTDIR = dist
BUILDDIR = build
RELEASEDIR = $(PROJECTNAME)-$(VERSION)$(RELEASE)
EGGINFODIR = $(PROJECTNAME).egg-info
DOCDIR = doc
COVDIR = htmlcov
BSWE_DIR = ../blue_sky_workflow_engine

DOC_URL=http://alleninstitute.github.io/blue_sky_reference

build:
	mkdir -p $(DISTDIR)/$(PROJECTNAME) 
	cp -r workflow_engine setup.py README.md $(DISTDIR)/$(PROJECTNAME)/
	cd $(DISTDIR); tar czvf $(PROJECTNAME).tgz --exclude .git $(PROJECTNAME)
	

distutils_build:
	python setup.py build

sdist: distutils_build
	python setup.py sdist

pypi_deploy:
	python setup.py sdist upload --repository local

pytest_lax:
	pytest -s --cov=workflow_engine,workflow_client --cov-report html --cov-append --junitxml=test-reports/test.xml

pytest: pytest_lax

test: pytest

pytest_pep8:
	find -L . -name "test_*.py" -exec py.test --cov-config coveragerc --cov=workflow_client --cov=workflow_engine --cov-report html --junitxml=test-reports/test.xml {} \+

pytest_lite:
	find -L . -name "test_*.py" -exec py.test --assert=reinterp --junitxml=test-reports/test.xml {} \+

prospector:
	prospector > htmlcov/pylint.txt || exit 0
	grep import htmlcov/pylint.txt > htmlcov/pylint_imports.txt

pylint:
	pylint --disable=C workflow_engine | tee htmlcov/pylint.txt || exit 0
	grep import-error htmlcov/pylint.txt | tee htmlcov/pylint_imports.txt

flake8:
	flake8 --ignore=E201,E202,E226 --max-line-length=200 --filename 'workflow_engine/**/*.py' workflow_engine | grep -v "local variable '_' is assigned to but never used" > htmlcov/flake8.txt
	grep -i "import" htmlcov/flake8.txt > htmlcov/imports.txt || exit 0

EXAMPLES=$(DOCDIR)/_static/examples

fsm_figures:
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/task_states.png workflow_engine.Task
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/job_states.png workflow_engine.Job
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/job_states.png workflow_engine.Job
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/calibration_states.png blue_sky.Calibration
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/observation_states.png blue_sky.Observation
	python -m manage graph_transitions -o doc_template/aibs_sphinx/static/observation_group_states.png blue_sky.ObservationGroup

doc: FORCE
	sphinx-apidoc -d 4 -H "Blue Sky Workflow Engine" -A "Allen Institute for Brain Science" -V $(VERSION) -R $(VERSION)$(RELEASE) --full -o $(DOCDIR) $(BSWE_DIR)/workflow_client
	sphinx-apidoc -d 4 -H "Blue Sky Workflow Engine" -A "Allen Institute for Brain Science" -V $(VERSION) -R $(VERSION)$(RELEASE) --full -o $(DOCDIR) $(BSWE_DIR)/workflow_engine
	sphinx-apidoc -d 4 -H "Blue Sky Workflow Engine" -A "Allen Institute for Brain Science" -V $(VERSION) -R $(VERSION)$(RELEASE) --full -o $(DOCDIR) blue_sky
	cp doc_template/*.rst doc_template/conf.py $(DOCDIR)
	sed -i --expression "s/|version|/${VERSION}/g" $(DOCDIR)/conf.py
	cp -R doc_template/aibs_sphinx/static/* $(DOCDIR)/_static
	cp -R htmlcov $(DOCDIR)/_static
	cp -R doc_template/aibs_sphinx/templates/* $(DOCDIR)/_templates
ifdef STATIC
	sed -i --expression "s/\/_static\/external_assets/${STATIC}\/external_assets/g" $(DOCDIR)/_templates/layout.html
	sed -i --expression "s/\/_static\/external_assets/${STATIC}\/external_assets/g" $(DOCDIR)/_templates/portalHeader.html
	sed -i --expression "s/\/_static\/external_assets/${STATIC}\/external_assets/g" $(DOCDIR)/_templates/portalFooter.html
endif
	cd $(DOCDIR) && make html || true

FORCE:

clean:
	rm -rf $(DISTDIR)
	rm -rf $(BUILDDIR)
	rm -rf $(RELEASEDIR)
	rm -rf $(EGGINFODIR)
	rm -rf $(DOCDIR)
