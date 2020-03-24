## Example project

This is a simple example project that can be successfully
deployed using this lambda ci cd package.

## Project structure

The project has a specific example structure that your 
project must obey in order to successfully use ci cd pipeline.

#### Files that must be present in your project

- _install.sh_ - A script that will be called when building 
you project. The script should install your project and dependencies.

- _test.sh_ - A script that will be called after a successful
build. The script should run your project's tests.

Note: these files can be empty.
