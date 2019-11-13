## How to prepare your data for training

Follow the instructions in this document to prepare your data for model training.
- [Prerequisites](#prerequisites)
- [Preparing your data](#preparing-your-data)
- [Organize data directory](#organize-data-directory)

## Prerequisites
TODO: List prerequisite steps the user needs to complete before data preparation can be started.

## Preparing your data
TODO: List steps the user needs to complete to prepare data for model training.

## Organize data directory

A trainable model should adhere to the standard directory structure below:

```
|-- data_directory
    |-- assets
    |-- data
    |-- initial_model
```

1. `assets` holds ancillary files required for training (typically these are generated during the data preparation phase).
2. `data` holds the data required for training.
3. `initial_model` holds the initial checkpoint files to initiate training.

If a particular directory is not required, it can be omitted.
