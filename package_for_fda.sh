rm termset_generator.zip
zip -u termset_generator.zip bin/*.py
zip -u termset_generator.zip bin/*.txt
zip -u termset_generator.zip lib/*.py
zip -u termset_generator.zip samples/sample*
zip -u termset_generator.zip static/logo.png
zip -u termset_generator.zip static/ibm_fda_logos.png
zip -u termset_generator.zip Dockerfile
zip -u termset_generator.zip LICENSE.txt
zip -u termset_generator.zip README.md
zip -u termset_generator.zip build_docker.*
zip -u termset_generator.zip requirements.txt
zip -u termset_generator.zip run_docker.*
mv termset_generator.zip delivery
echo Wrote delivery/termset_generator.zip
shasum -a 256 delivery/termset_generator.zip
