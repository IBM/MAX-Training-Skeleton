
## Review Dockerfile

## Review config.py

 - Is the microservice enabled to serve more than one model?
   - Yes. => Requires investigation

 - Does the configuration point to one or more serialized model files ?
   - Yes.
     - Are the file names proprietary (e.g. `model-jan-27-2018.pb`) as opposed to generic (e.g. `model.pb`)?
       - Yes. => Likely requires a rename of the file(s) on COS to something generic. (a custom-trained model archive name should not imply something that it is not; for example, a model that was custom trained in March of 2019 should not be named `model-jan-27-2018-blah.pb`)

 - Does the configuration point to a single compressed archive (as opposed to a directory)?
   - Yes. => Requires changes to `training/training_code/train-max-model.sh` to create an archive. (By default model artifacts are not compressed.)
   - Is the archive name proprietary (e.g. `model-jan-27-2018-blah.tar.gz`) as opposed to generic (e.g. `model.tar.gz`)?
     - Yes. => likely requires rename of the archive on COS to something generic. (a custom-trained model archive name should not imply something that it is not; for example, a model that was custom trained in March of 2019 should not be named `model-jan-27-2018-blah.tar.gz`)
