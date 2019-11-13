## How to update the model's Dockerfile

The [recipe file](https://github.com/IBM/MAX-Skeleton/blob/master/Dockerfile) illustrates how to customize the model's `Dockerfile` to allow for consumption of pre-trained model artifacts and custom-trained model artifacts.

There are two important sections:

```
ARG use_pre_trained_model=true

WORKDIR /workspace
RUN if [ "$use_pre_trained_model" = "true" ] ; then\
# download pre-trained model artifacts from Cloud Object Storage
# wget ...
```

Summary:
- New build argument `use_pre_trained_model`. If set to `true` (default) the pre-trained model artifacts are downloaded from COS to the `assets` directory in the Docker file system.
- Users can change the default at build time, by specifying the `docker build --build-arg use_pre_trained_model=false`

```
RUN if [ "$use_pre_trained_model" = "true" ] ; then \
      # validate MD5 hash of downloaded pre-trained model assets
    else \
      # rename the directory that contains the custom-trained model artifacts
      if [ -d "./custom_assets/" ] ; then \
        ln -s ./custom_assets ./assets ; \
      fi \
    fi
```

Summary:
- If `use_pre_trained_model` is set to `false` the custom-trained model artifacts are "moved" from the `custom_assets` directory in the Docker file system to the (empty) `assets` directory.
- The custom-trained model artifacts where stored by the training framework in the `custom_assets` directory on the build machine and copied to the `custom_assets` directory in the Docker file system.

